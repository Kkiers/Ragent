from __future__ import annotations

from pathlib import Path
import sys


"""
一次性任务
从pdf抽取faq json
"""
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.infra.data_clean.pdf_faq import extract_faq_records  # noqa: E402


def main():
    pdf_path = Path("knowledge") / "HUAWEI-Voicecall-faq.pdf"
    out_path = Path("knowledge") / "HUAWEI-Voicecall-faq.json"

    stats, records = extract_faq_records(str(pdf_path))
    print(stats)
    out_path.write_text(
        __import__("json").dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"wrote: {out_path}")


if __name__ == "__main__":
    main()

