from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class FaqChunk(BaseModel):
    """FAQ 检索单元（与入库 metadata 可互转）。"""

    id: str
    section_id: str
    section_title: str
    question: str
    answer: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    source: Dict[str, Any] = Field(default_factory=dict)
    chunk_text: str
    token_count: Optional[int] = None
