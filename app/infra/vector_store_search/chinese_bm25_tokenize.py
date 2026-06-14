"""BM25 用中文分词：jieba 切词 + 字母数字 token，过滤空白。"""
from __future__ import annotations

import re
from typing import List

_ALNUM = re.compile(r"[A-Za-z0-9]+")


def tokenize_for_bm25(text: str) -> List[str]:
    s = (text or "").strip()
    if not s:
        return []
    import jieba

    out: List[str] = []
    for tok in jieba.lcut(s):
        t = tok.strip()
        if not t:
            continue
        if t.isascii() and not _ALNUM.fullmatch(t):
            continue
        out.append(t)
    return out
