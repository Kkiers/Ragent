"""
混合检索调试（默认经 create_vector_store）：
跳过 query 规整、意图识别与 LLM。
参数：
默认 RAG_HYBRID=true 时为 BM25+Chroma 融合；
设 RAG_HYBRID=0 则仅 ChromaVectorStore。

依赖：Ollama 可嵌入、Chroma 已 ingest；混合模式还需 FAQ_CHUNKS_JSONL 指向的 jsonl。

用法（已激活 .venv；CHROMA_PERSIST_DIR 相对路径相对仓库根，与从哪一级目录运行无关）::

    python tests/test_chroma_retrieval_debug.py

自定义问题与 top_k（可选）::

    set RAG_DEBUG_QUERY=问题
    set RAG_DEBUG_TOP_K=8
    python tests/test_chroma_retrieval_debug.py

纯向量（关闭 BM25 融合），PowerShell::

    $env:RAG_HYBRID="0"; python tests/test_chroma_retrieval_debug.py

分词走的路径：
app/infra/vector_store_search/chinese_bm25_tokenize.py
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import chromadb

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.infra.vector_store_search.faq_hybrid_vector_store import hybrid_enabled, resolve_faq_chunks_jsonl
from app.infra.vector_store_search.vector_search import create_vector_store, resolve_chroma_persist_directory
from tests._config import TestSettings

_S = TestSettings.load()
DEFAULT_QUERY = str(_S.get("retrieval_debug", "default_query", default="为什么我的号码被拦截了？"))
TOP_K = int(_S.get("retrieval_debug", "top_k", default=10))
_CANDIDATES_OUT = str(_S.get("retrieval_debug", "candidates_out", default="tests/rerank_candidates.txt"))
CANDIDATES_OUT = (ROOT / _CANDIDATES_OUT).resolve()

def _cfg_bool(*keys: str, default: bool) -> bool:
    v = _S.get(*keys, default=default)
    if isinstance(v, bool):
        return v
    if v is None:
        return default
    s = str(v).strip().lower()
    return s in ("1", "true", "yes", "on")


def _dump_candidates_txt(*, query: str, docs, path: Path) -> None:
    """
    把混合检索/向量检索的候选结果落盘，供 tests/test_rerank.py 读取做重排。

    格式：JSONL（.txt 但每行一个 JSON），字段包含 section_id（与 doc_id 同值）。
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(json.dumps({"query": query}, ensure_ascii=False) + "\n")
        for d in docs:
            row = {
                "section_id": d.doc_id,
                "doc_id": d.doc_id,
                "score": float(d.score),
                "content": d.content,
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _collection_name() -> str:
    return str(_S.get("chroma", "collection", default="huawei_voicecall_faq")).strip()


def print_collections_inventory() -> None:
    """列出本机该 persist 目录下实际有哪些 collection、各有多少条，便于核对是否写错名字。"""
    persist = Path(resolve_chroma_persist_directory())
    target = _collection_name()
    print(f"Chroma 持久化路径（已解析）: {persist}")
    if not persist.exists():
        print("  警告: 该目录不存在，检索一定为空；请检查 CHROMA_PERSIST_DIR（相对路径相对仓库根）。")
        return
    try:
        client = chromadb.PersistentClient(path=str(persist))
    except Exception as e:
        print(f"  无法打开 Chroma: {e}")
        return
    names = client.list_collections()
    if not names:
        print("  该目录下没有任何 collection（尚未 ingest 或路径不对）。")
        return
    print("  本目录下的 collection（与入库时 --collection 一致才对得上）:")
    known = {c.name for c in names}
    for c in sorted(names, key=lambda x: x.name):
        try:
            n = c.count()
        except Exception:
            n = "?"
        mark = "  <-- 当前环境 CHROMA_COLLECTION" if c.name == target else ""
        print(f"    - {c.name!r}  documents={n}{mark}")
    if target not in known:
        print(f"  警告: 当前要查的 collection {target!r} 不在上列表中，LangChain 可能自动建了空表，检索为 0。")
    print()


async def run_retrieval(query: str, top_k: int) -> None:
    print("=" * 72)
    print("检索调试（无规整 / 无意图 / 无 LLM）")
    print("=" * 72)
    print(f"cwd                = {Path.cwd()}  （仅作参考；Chroma 路径已相对仓库根解析）")
    print(f"混合开关（hybrid_enabled）= {hybrid_enabled()}")
    print(f"FAQ_CHUNKS_JSONL（来自 .env / 代码解析）= {str(_S.get('chroma', 'faq_chunks_jsonl', default='knowledge/HUAWEI-Voicecall-faq.chunks.jsonl'))!r}")
    chunks_path = resolve_faq_chunks_jsonl()
    print(f"解析后 chunks 路径 = {chunks_path!s}  (exists={chunks_path.is_file()})")
    print(f"CHROMA_PERSIST_DIR（来自 config/test_settings.json）= {str(_S.get('chroma','persist_dir', default='knowledge/chroma'))!r}")
    print(f"解析后 persist     = {resolve_chroma_persist_directory()!r}")
    print(f"CHROMA_COLLECTION（来自 config/test_settings.json）= {str(_S.get('chroma','collection', default='huawei_voicecall_faq'))!r}")
    print("-" * 72)
    print_collections_inventory()
    print("-" * 72)
    print(f"query  = {query!r}")
    print(f"top_k  = {top_k}")
    print("-" * 72)

    store = create_vector_store()
    print(f"实际 VectorStore 类型 = {type(store).__name__}")
    print("-" * 72)
    docs = await store.search(query, top_k)

    dump_enabled = _cfg_bool("retrieval_debug", "dump_candidates", default=True)
    out_path = CANDIDATES_OUT
    if dump_enabled:
        _dump_candidates_txt(query=query, docs=docs, path=out_path)
        print(f"已写入候选结果到: {out_path}")

    print("-" * 72)
    print(f"命中条数: {len(docs)}")
    for i, d in enumerate(docs, 1):
        print()
        print(f"--- #{i}  section_id={d.doc_id!r}  score={d.score!r} ---")
        print(d.content)

    print()
    print("=" * 72)


def main() -> None:
    query = (DEFAULT_QUERY or "").strip()
    top_k = TOP_K
    asyncio.run(run_retrieval(query, top_k))


if __name__ == "__main__":
    main()
