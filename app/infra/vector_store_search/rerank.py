from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Iterable

from app.domain.schemas import RetrievedDoc
from app.infra.vector_store_search.vector_search import VectorStore, _env


@dataclass(frozen=True)
class RerankSettings:
    model_name: str = "BAAI/bge-reranker-base"
    enabled: bool = True
    candidates: int = 40 # 重排前召回多少条候选


def _env_bool(name: str, default: bool) -> bool:
    raw = (_env(name, "true" if default else "false") or "").strip().lower()
    return raw in ("1", "true", "yes", "on")


def load_rerank_settings() -> RerankSettings:
    enabled = _env_bool("RAG_RERANK", True)
    model_name = _env("RAG_RERANK_MODEL", "BAAI/bge-reranker-base")
    raw_k = _env("RAG_RERANK_CANDIDATES", "40")
    try:
        k = int(raw_k)
    except ValueError:
        k = 40
    if k <= 0:
        k = 40
    return RerankSettings(model_name=model_name, enabled=enabled, candidates=k)


class CrossEncoderRerankVectorStore(VectorStore):
    """
    包装一个 VectorStore：先召回候选（通常 40+），再用 Cross-Encoder（bge-reranker-base）重排取 top_k。

    说明：
    - score 会被重排分数覆盖（越大越相关）。
    - 默认用线程池跑同步推理，避免阻塞事件循环。
    """

    def __init__(self, base: VectorStore, settings: RerankSettings) -> None:
        self._base = base
        self._s = settings
        self._model = None

    def _get_model(self):
        if self._model is None:
            # sentence-transformers: CrossEncoder supports "BAAI/bge-reranker-base"
            from sentence_transformers import CrossEncoder  # type: ignore

            self._model = CrossEncoder(self._s.model_name)
        return self._model

    def _pairs(self, query: str, docs: Iterable[RetrievedDoc]) -> list[list[str]]:
        q = (query or "").strip()
        out: list[list[str]] = []
        for d in docs:
            out.append([q, (d.content or "").strip()])
        return out

    def _rerank_sync(self, query: str, docs: list[RetrievedDoc], top_k: int) -> list[RetrievedDoc]:
        if not docs:
            return []
        model = self._get_model()
        pairs = self._pairs(query, docs)
        scores = model.predict(pairs)

        scored: list[tuple[float, RetrievedDoc]] = []
        for s, d in zip(scores, docs, strict=False):
            try:
                fs = float(s)
            except Exception:
                fs = 0.0
            scored.append((fs, d))
        scored.sort(key=lambda x: x[0], reverse=True)

        out: list[RetrievedDoc] = []
        for s, d in scored[:top_k]:
            out.append(RetrievedDoc(doc_id=d.doc_id, content=d.content, score=float(s)))
        return out

    
    async def search(self, query: str, top_k: int = 5) -> list[RetrievedDoc]:
        text = (query or "").strip()
        if not text:
            return []
        if not self._s.enabled:
            return await self._base.search(text, top_k=top_k)
        
        # TOP_K: 混合检索输出给 rerank 的候选池，候选数至少要 ≥ 最终 top_k（避免候选不够）
        cand_k = max(int(top_k), int(self._s.candidates))

        # TOP_K: 先取 候选数 = cand_k，再重排
        docs = await self._base.search(text, top_k=cand_k)
        # sentence-transformers / torch 等依赖缺失时，自动降级为不 rerank，避免流程中断
        try:
            return await asyncio.to_thread(self._rerank_sync, text, docs, top_k)
        except ModuleNotFoundError:
            return docs[:top_k]
        except ImportError:
            return docs[:top_k]

