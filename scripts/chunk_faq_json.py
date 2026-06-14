from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any, Dict, List

"""
一次性任务
将faq json 变成切片 jsonl
"""

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.pipeline.faq_chunk_pipeline import faq_records_to_chunks  # noqa: E402


def main() -> None:
    import argparse

    p = argparse.ArgumentParser(description="FAQ JSON list -> chunks JSONL")
    p.add_argument("faq_json")
    p.add_argument("--out", default=None)
    p.add_argument("--source-id", default=None)
    args = p.parse_args()
    in_path = Path(args.faq_json)
    data = json.loads(in_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("FAQ JSON 须为 list")
    out_path = Path(args.out) if args.out else in_path.with_suffix(".chunks.jsonl")
    chunks = faq_records_to_chunks(
        data,
        source={"path": str(in_path)},
        source_id=args.source_id or in_path.name,
    )
    with out_path.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(c.model_dump_json(ensure_ascii=False) + "\n")
    print(f"chunks={len(chunks)} -> {out_path}")


if __name__ == "__main__":
    main()
