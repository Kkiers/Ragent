from __future__ import annotations

import hashlib
from typing import Any, Dict, Iterable, List, Optional

from app.core.faq_chunk_text import build_faq_chunk_text, estimate_token_count
from app.domain.chunks import FaqChunk


def _stable_chunk_id(*, source_id: str, section_id: str, question: str) -> str:
    base = f"{source_id}::{section_id}::{question}".strip()
    h = hashlib.sha1(base.encode("utf-8")).hexdigest()[:16]
    return f"faq_{h}"


def faq_records_to_chunks(
    records: Iterable[Dict[str, Any]],
    *,
    source: Optional[Dict[str, Any]] = None,
    source_id: str = "knowledge",
) -> List[FaqChunk]:
    src = dict(source or {})
    out: List[FaqChunk] = []
    for r in records:
        section_id = str(r.get("section_id", "")).strip()
        section_title = str(r.get("section_title", "")).strip()
        question = str(r.get("question", "")).strip()
        answer = str(r.get("answer", "")).strip()
        chunk_text = build_faq_chunk_text(
            section_title=section_title,
            section_id=section_id,
            question=question,
            answer=answer,
        )
        metadata = {
            "doc_type": "faq",
            "category": section_title,
            "section_title": section_title,
            "page_start": r.get("page_start"),
            "page_end": r.get("page_end"),
            "urls": r.get("urls") or [],
            "question_length": len(question),
            "answer_length": len(answer),
        }
        cid = _stable_chunk_id(source_id=source_id, section_id=section_id, question=question)
        out.append(
            FaqChunk(
                id=cid,
                section_id=section_id,
                section_title=section_title,
                question=question,
                answer=answer,
                metadata=metadata,
                source=src,
                chunk_text=chunk_text,
                token_count=estimate_token_count(chunk_text),
            )
        )
    return out
