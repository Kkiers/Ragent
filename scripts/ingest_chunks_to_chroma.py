from __future__ import annotations

from pathlib import Path
import sys
from typing import List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.domain.chunks import FaqChunk  # noqa: E402
from app.infra.langchain.faq_mapper import to_langchain_document  # noqa: E402
from app.infra.vector_store_search.chroma_store import (  # noqa: E402
    ChromaSettings,
    create_chroma_vectorstore,
)
"""
一次性任务
「把 chunk（FAQ 条）向量化并写入向量库」，为以后检索做准备。
"""

def load_jsonl(path: Path) -> List[FaqChunk]:
    rows: List[FaqChunk] = []
    with path.open(encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            s = line.strip()
            if not s:
                continue
            try:
                rows.append(FaqChunk.model_validate_json(s))
            except Exception as e:
                raise ValueError(f"line {i}") from e
    return rows


def main() -> None:
    import argparse

    p = argparse.ArgumentParser(description="Chunks JSONL -> Chroma")
    p.add_argument("chunks_jsonl")
    p.add_argument("--persist-dir", default="knowledge/chroma")
    p.add_argument("--collection", default="huawei_voicecall_faq")
    p.add_argument("--ollama-url", default="http://localhost:11434")
    p.add_argument("--ollama-embed-model", default="nomic-embed-text:latest")
    args = p.parse_args()
    persist_dir = Path(args.persist_dir)
    if not persist_dir.is_absolute():
        persist_dir = (ROOT / persist_dir).resolve()
    persist_s = str(persist_dir)
    in_path = Path(args.chunks_jsonl)
    chunks = load_jsonl(in_path)
    docs = [to_langchain_document(c) for c in chunks]
    ids = [c.id for c in chunks]
    vs = create_chroma_vectorstore(
        settings=ChromaSettings(
            persist_directory=persist_s,
            collection_name=args.collection,
        ),
        ollama_base_url=args.ollama_url,
        ollama_embedding_model=args.ollama_embed_model,
    )
    vs.add_documents(docs, ids=ids)
    try:
        vs.persist()
    except Exception:
        pass
    print(f"ingested={len(docs)} -> {persist_s} ({args.collection})")


if __name__ == "__main__":
    main()
