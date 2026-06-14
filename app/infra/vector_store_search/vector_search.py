"""
向量检索入口。

默认（RAG_HYBRID 未关闭）：BM25（jieba 分词）与 Chroma 向量经 EnsembleRetriever 融合，见 faq_hybrid_vector_store。
关闭混合：环境变量 RAG_HYBRID=0/false，则仅为 Chroma（Ollama 自算 query 向量）。

CHROMA_PERSIST_DIR 若为相对路径，则相对于仓库根目录（含 app/ 的那一层），不随进程 cwd 变化。
"""
from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Protocol, runtime_checkable

from app.domain.schemas import RetrievedDoc


def _env(name: str, default: str) -> str:
    v = os.getenv(name)
    return (v or default).strip()


def _truthy(v: str) -> bool:
    s = (v or "").strip().lower()
    return s in ("1", "true", "yes", "y", "on")


def resolve_chroma_persist_directory() -> str:
    """解析 CHROMA_PERSIST_DIR：绝对路径原样；相对路径相对本仓库根（app/ 的上一级）。"""
    raw = _env("CHROMA_PERSIST_DIR", "knowledge/chroma")
    p = Path(raw)
    if p.is_absolute():
        return str(p.resolve())
    # vector_search.py -> app/infra/vector_store_search/ → 上三级到仓库根
    repo_root = Path(__file__).resolve().parents[3]
    return str((repo_root / p).resolve())


@runtime_checkable
class VectorStore(Protocol):
    async def search(self, query: str, top_k: int = 5) -> list[RetrievedDoc]: ...


class ChromaVectorStore:
    """Ollama 向量化 query → Chroma similarity_search_by_vector_with_relevance_scores → RetrievedDoc。"""

    def __init__(self) -> None:
        from app.infra.embedding.ollama_embedder import OllamaEmbedder, OllamaEmbeddingSettings
        from app.infra.langchain.faq_mapper import langchain_document_to_faq_chunk
        from app.infra.vector_store_search.chroma_store import ChromaSettings, create_chroma_vectorstore

        self._langchain_document_to_faq_chunk = langchain_document_to_faq_chunk
        persist = resolve_chroma_persist_directory()
        collection = _env("CHROMA_COLLECTION", "huawei_voicecall_faq")
        ollama_url = _env("OLLAMA_BASE_URL", "http://localhost:11434")
        embed_model = _env("OLLAMA_EMBED_MODEL", "nomic-embed-text:latest")

        self._embedder = OllamaEmbedder(
            OllamaEmbeddingSettings(base_url=ollama_url, model=embed_model)
        )
        self._chroma = create_chroma_vectorstore(
            settings=ChromaSettings(persist_directory=persist, collection_name=collection),
            ollama_base_url=ollama_url,
            ollama_embedding_model=embed_model,
        )

    @property
    def chroma(self):
        """LangChain Chroma 实例，供混合检索与 as_retriever 等扩展使用。"""
        return self._chroma

    def _search_sync(self, query: str, top_k: int) -> list[RetrievedDoc]:
        text = (query or "").strip()
        if not text:
            return []
        qvec = self._embedder.embed_texts([text])[0]

        # TOP_K: Chroma 向量检索直接取回多少条
        pairs = self._chroma.similarity_search_by_vector_with_relevance_scores(qvec, k=top_k)
        out: list[RetrievedDoc] = []
        for doc, rel in pairs:
            chunk = self._langchain_document_to_faq_chunk(doc)
            out.append(
                RetrievedDoc(doc_id=chunk.id, content=chunk.chunk_text, score=float(rel))
            )
        return out

    # TOP_K:对外统一接口里的 “最终要返回LLM多少条 RetrievedDoc”
    async def search(self, query: str, top_k: int = 5) -> list[RetrievedDoc]:
        return await asyncio.to_thread(self._search_sync, query, top_k)


class DisabledVectorStore(VectorStore):
    """用于本地开发/自检：禁用向量检索，避免启动期重依赖初始化。"""

    async def search(self, query: str, top_k: int = 5) -> list[RetrievedDoc]:
        return []


def create_vector_store() -> VectorStore:
    from app.infra.vector_store_search.faq_hybrid_vector_store import create_hybrid_vector_store_or_fallback, hybrid_enabled
    from app.infra.vector_store_search.rerank import CrossEncoderRerankVectorStore, load_rerank_settings

    if _truthy(_env("RAG_VECTOR_DISABLED", "")) or _truthy(_env("VECTOR_STORE_DISABLED", "")):
        return DisabledVectorStore()

    base: VectorStore
    if hybrid_enabled():
        base = create_hybrid_vector_store_or_fallback()
    else:
        base = ChromaVectorStore()

    s = load_rerank_settings()
    if not s.enabled:
        return base
    return CrossEncoderRerankVectorStore(base, s)
