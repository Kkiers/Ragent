"""
读取 tests/test_chroma_retrieval_debug.py 生成的候选结果rerank_candidates（JSONL .txt），
做 Cross-Encoder 重排并写回 txt。

用法：
    python tests/test_rerank.py

环境变量（可选）：
    RAG_DEBUG_CANDIDATES_OUT   候选文件路径（默认 tests/rerank_candidates.txt）
    RAG_DEBUG_RERANK_OUT       重排结果路径（默认 tests/rerank_results.txt）
    RAG_RERANK_MODEL           Cross-Encoder 模型名（默认 BAAI/bge-reranker-base）
    RAG_DEBUG_RERANK_TOP_K     输出 top_k（默认 20）
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

from tests._config import TestSettings


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_S = TestSettings.load()


@dataclass(frozen=True)
class Candidate:
    section_id: str
    doc_id: str
    content: str
    score: float = 0.0


def _cfg_int(*keys: str, default: int) -> int:
    v = _S.get(*keys, default=default)
    try:
        return int(v)
    except Exception:
        return default


def _read_candidates(path: Path) -> tuple[str, list[Candidate]]:
    if not path.is_file():
        raise FileNotFoundError(f"候选文件不存在: {path}")
    query = ""
    docs: list[Candidate] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            if not s.startswith("{"):
                continue
            row = json.loads(s)
            if "query" in row and isinstance(row["query"], str):
                query = row["query"].strip()
                continue
            doc_id = str(row.get("doc_id") or "")
            section_id = str(row.get("section_id") or doc_id)
            content = str(row.get("content") or "")
            score = float(row.get("score") or 0.0)
            if not (section_id and content):
                continue
            docs.append(Candidate(section_id=section_id, doc_id=doc_id or section_id, content=content, score=score))
    if not query:
        raise ValueError("候选文件中缺少 query 行（第一行应为 {'query': ...}）")
    return query, docs


def _write_reranked(path: Path, *, model: str, query: str, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(json.dumps({"model": model, "query": query}, ensure_ascii=False) + "\n")
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main() -> None:
    candidates_path = (ROOT / str(_S.get("retrieval_debug", "candidates_out", default="tests/rerank_candidates.txt"))).resolve()
    out_path = (ROOT / str(_S.get("rerank_debug", "rerank_out", default="tests/rerank_results.txt"))).resolve()
    model_name = str(_S.get("rerank_debug", "model", default="BAAI/bge-reranker-base")).strip()
    top_k = _cfg_int("rerank_debug", "top_k", default=20)

    query, docs = _read_candidates(candidates_path)
    if not docs:
        _write_reranked(out_path, model=model_name, query=query, rows=[])
        print(f"无候选文档，已写空结果: {out_path}")
        return

    try:
        from sentence_transformers import CrossEncoder  # type: ignore
    except ModuleNotFoundError:
        # 依赖未安装时降级：直接按原顺序输出（仍保留 score / section_id 字段）
        rows: list[dict] = []
        for rank, d in enumerate(docs[: max(1, top_k)], 1):
            rows.append(
                {
                    "rank": rank,
                    "section_id": d.section_id,
                    "doc_id": d.doc_id,
                    "score": float(d.score),
                    "content": d.content,
                }
            )
        _write_reranked(out_path, model=model_name, query=query, rows=rows)
        print(
            "未检测到 sentence-transformers，已降级为不重排输出。"
            f" 结果: {out_path}  (top_k={top_k}, candidates={len(docs)})"
        )
        return

    ce = CrossEncoder(model_name)
    pairs = [[query, d.content] for d in docs]
    scores = ce.predict(pairs)

    scored = []
    for d, s in zip(docs, scores, strict=False):
        scored.append((float(s), d))
    scored.sort(key=lambda x: x[0], reverse=True)

    rows: list[dict] = []
    for rank, (s, d) in enumerate(scored[: max(1, top_k)], 1):
        rows.append(
            {
                "rank": rank,
                "section_id": d.section_id,
                "doc_id": d.doc_id,
                "score": float(s),
                "content": d.content,
            }
        )

    _write_reranked(out_path, model=model_name, query=query, rows=rows)
    print(f"已写入重排结果到: {out_path}  (top_k={top_k}, candidates={len(docs)}, model={model_name!r})")


if __name__ == "__main__":
    main()

