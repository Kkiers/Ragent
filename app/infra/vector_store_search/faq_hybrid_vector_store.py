"""
FAQ 混合检索：BM25（jieba 分词）+ Chroma 向量，
经 LangChain EnsembleRetriever（加权 RRF）融合。

环境变量（可选）：
- FAQ_CHUNKS_JSONL：相对仓库根的路径，默认 knowledge/HUAWEI-Voicecall-faq.chunks.jsonl
- ENSEMBLE_BM25_WEIGHT / ENSEMBLE_VECTOR_WEIGHT：融合权重，默认各 0.5
- ENSEMBLE_RRF_C：RRF 常数 c，默认 60，默认 60 就像是“平均分”。
- RAG_HYBRID：设为 0/false 可关闭混合（仅用 Chroma），默认 true
"""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import List

from app.domain.chunks import FaqChunk
from app.domain.schemas import RetrievedDoc
from app.infra.langchain.faq_mapper import langchain_document_to_faq_chunk, to_langchain_document
from app.infra.vector_store_search.chinese_bm25_tokenize import tokenize_for_bm25
from app.infra.vector_store_search.vector_search import ChromaVectorStore, VectorStore, _env, resolve_chroma_persist_directory

_log = logging.getLogger(__name__)


def _repo_root() -> Path:
    # faq_hybrid_vector_store.py -> app/infra/vector_store_search/ → 上三级到仓库根
    return Path(__file__).resolve().parents[3]


def resolve_faq_chunks_jsonl() -> Path:
    raw = _env("FAQ_CHUNKS_JSONL", "knowledge/HUAWEI-Voicecall-faq.chunks.jsonl")
    p = Path(raw)
    if p.is_absolute():
        return p.resolve()
    return (_repo_root() / p).resolve()


def _parse_weights() -> tuple[float, float]:
    w_bm = _env("ENSEMBLE_BM25_WEIGHT", "0.5")
    w_vec = _env("ENSEMBLE_VECTOR_WEIGHT", "0.5")
    try:
        a, b = float(w_bm), float(w_vec)
    except ValueError:
        return 0.5, 0.5
    if a <= 0 and b <= 0:
        return 0.5, 0.5
    return a, b

# 把JSONL 文件（那些 FAQ）全部读进内存。
def _load_faq_chunks(path: Path) -> List[FaqChunk]:
    rows: List[FaqChunk] = []
    with path.open(encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            s = line.strip()
            if not s:
                continue
            try:
                rows.append(FaqChunk.model_validate_json(s))
            except Exception as e:
                raise ValueError(f"FAQ chunks JSONL 解析失败 line {i}: {path}") from e
    return rows


class FaqHybridVectorStore(VectorStore):
    """BM25 + Chroma 向量，EnsembleRetriever 融合后映射为 RetrievedDoc。"""

    def __init__(self, chunks_path: Path) -> None:
        from langchain_classic.retrievers import EnsembleRetriever
        from langchain_community.retrievers import BM25Retriever

        self._mapper = langchain_document_to_faq_chunk
        self._base = ChromaVectorStore()
        self._chroma = self._base.chroma

        chunks = _load_faq_chunks(chunks_path)
        lc_docs = [to_langchain_document(c) for c in chunks]
        # BM25Retriever 拿着 jieba 分好的词，建立了索引。
        # BM25Retriever 关键词检索 TOPK 默认取回40条
        self._bm25 = BM25Retriever.from_documents(
            lc_docs,
            preprocess_func=tokenize_for_bm25,
            k=40,
        )
        self._vector_retriever = self._chroma.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 40}, # Chroma 向量检索 TOPK 默认取回40条
        )
        w_bm, w_vec = _parse_weights()
        c_raw = _env("ENSEMBLE_RRF_C", "60")
        try:
            c_rrf = int(c_raw)
        except ValueError:
            c_rrf = 60
        # 融合检索：BM25Retriever 和 Chroma 向量检索的结果，按照权重融合在一起。
        self._ensemble = EnsembleRetriever(
            retrievers=[self._bm25, self._vector_retriever],
            weights=[w_bm, w_vec],
            c=c_rrf,
            id_key="id", # 向量检索和关键词检索可能会搜到同一个 FAQ, 所以需要id_key来区分
        )
        _log.info(
            "混合检索已启用：BM25 文档数=%s，Chroma=%s，权重 BM25=%s vector=%s",
            len(lc_docs),
            resolve_chroma_persist_directory(),
            w_bm,
            w_vec,
        )
    # TOP_K: 每次检索时，检索结果的数量需要乘以5，保底24
    def _fetch_k(self, top_k: int) -> int:
        return max(top_k * 5, 24)

    def _search_sync(self, query: str, top_k: int) -> list[RetrievedDoc]:
        text = (query or "").strip()
        if not text:
            return []
        fk = self._fetch_k(top_k) # 检索设置的TOP_K乘5，保底24

        # 本次 BM25 实际取回的 候选数 = fk
        self._bm25.k = fk

        # 本次 Chroma 向量检索实际取回的 候选数 = fk
        self._vector_retriever.search_kwargs["k"] = fk

        fused = self._ensemble.invoke(text)

        # 最终返回给LLM的 候选数 = top_k
        fused = fused[:top_k]

        out: list[RetrievedDoc] = []
        for rank, doc in enumerate(fused):
            chunk = self._mapper(doc)
            rrf_proxy = 1.0 / (1.0 + rank)
            out.append(RetrievedDoc(doc_id=chunk.id, content=chunk.chunk_text, score=float(rrf_proxy)))
        return out

    async def search(self, query: str, top_k: int = 5) -> list[RetrievedDoc]:
        return await asyncio.to_thread(self._search_sync, query, top_k)


def hybrid_enabled() -> bool:
    v = (_env("RAG_HYBRID", "true") or "true").lower()
    return v in ("1", "true", "yes", "on")


def create_hybrid_vector_store_or_fallback() -> VectorStore:
    path = resolve_faq_chunks_jsonl()
    if not path.is_file():
        _log.warning("未找到 FAQ chunks 文件 %s，回退为纯 Chroma 检索。", path)
        return ChromaVectorStore()
    try:
        return FaqHybridVectorStore(path)
    except Exception:
        _log.exception("混合检索初始化失败，回退为纯 Chroma。")
        return ChromaVectorStore()
