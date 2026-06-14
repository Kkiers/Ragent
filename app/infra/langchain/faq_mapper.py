from __future__ import annotations

import json
from typing import Any, Dict

from app.core.faq_chunk_text import build_faq_chunk_text, build_faq_embedding_text, estimate_token_count
from app.domain.chunks import FaqChunk


def to_langchain_metadata(chunk: FaqChunk) -> Dict[str, Any]:
    md = dict(chunk.metadata or {})
    urls = md.pop("urls", None)
    if urls is not None:
        md["urls_json"] = json.dumps(urls, ensure_ascii=False)
    md.update(
        {
            "id": chunk.id,
            "section_id": chunk.section_id,
            "section_title": chunk.section_title,
            "question": chunk.question,
            "answer": chunk.answer,
        }
    )
    return md


def to_langchain_document(chunk: FaqChunk):
    from langchain_core.documents import Document  # type: ignore

    page_content = build_faq_embedding_text(
        section_title=chunk.section_title,
        question=chunk.question,
        answer=chunk.answer,
    )
    return Document(
        page_content=page_content,
        metadata=to_langchain_metadata(chunk),
        id=chunk.id,
    )


def langchain_document_to_faq_chunk(doc) -> FaqChunk:
    page_content = str(getattr(doc, "page_content", "") or "")
    md = dict(doc.metadata or {})
    urls_raw = md.pop("urls_json", None)
    urls: list = []
    if isinstance(urls_raw, str) and urls_raw.strip():
        try:
            urls = json.loads(urls_raw)
        except json.JSONDecodeError:
            urls = []

    section_title = str(md.get("section_title", "") or "")
    question = str(md.get("question", "") or "")
    answer = str(md.get("answer", "") or "")

    meta = {
        "doc_type": md.get("doc_type", "faq"),
        "category": md.get("category", section_title),
        "section_title": section_title,
        "page_start": md.get("page_start"),
        "page_end": md.get("page_end"),
        "urls": urls,
        "question_length": md.get("question_length"),
        "answer_length": md.get("answer_length"),
    }

    chunk_text = build_faq_chunk_text(
        section_title=section_title,
        section_id=str(md.get("section_id", "") or ""),
        question=question,
        answer=answer,
    )
    if not answer.strip() and page_content.strip():
        chunk_text = page_content.strip()

    return FaqChunk(
        id=str(md.get("id", "") or ""),
        section_id=str(md.get("section_id", "") or ""),
        section_title=section_title,
        question=question,
        answer=answer,
        metadata=meta,
        source={},
        chunk_text=chunk_text,
        token_count=estimate_token_count(chunk_text),
    )
