from __future__ import annotations

import re
from typing import Optional

_WS_RE = re.compile(r"[ \t]+")
_NL3_RE = re.compile(r"\n{3,}")


def _normalize_text_block(text: str) -> str:
    if text is None:
        return ""
    s = str(text).replace("\r\n", "\n").replace("\r", "\n")
    s = "\n".join(ln.rstrip() for ln in s.split("\n"))
    s = _WS_RE.sub(" ", s)
    s = _NL3_RE.sub("\n\n", s)
    return s.strip()


def build_faq_chunk_text(
    *,
    section_title: str,
    question: str,
    answer: str,
    section_id: Optional[str] = None,
) -> str:
    sec = _normalize_text_block(section_title)
    q = _normalize_text_block(question)
    a = _normalize_text_block(answer)
    header = f"分类：{sec}" if sec else ""
    if section_id:
        sid = _normalize_text_block(section_id)
        if sid:
            header = f"{header}\n编号：{sid}".strip() if header else f"编号：{sid}"
    body = "\n".join(
        part for part in [header, f"问：{q}" if q else "", f"答：{a}" if a else ""] if part
    )
    return _normalize_text_block(body)


def build_faq_embedding_text(
    *,
    section_title: str,
    question: str,
    answer: str,
) -> str:
    sec = _normalize_text_block(section_title)
    q = _normalize_text_block(question)
    a = _normalize_text_block(answer)
    parts = []
    if sec:
        parts.append(f"[分类] {sec}")
    if q:
        parts.append(f"[问题] {q}")
    if a:
        parts.append(f"[答案] {a}")
    return _normalize_text_block("\n".join(parts))


def estimate_token_count(text: str) -> int:
    s = _normalize_text_block(text)
    if not s:
        return 0
    pieces = re.findall(r"[\u4e00-\u9fff]|[A-Za-z0-9]+", s)
    return len(pieces)
