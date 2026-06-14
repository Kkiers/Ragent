"""Server-Sent Events 辅助：流式接口用。"""
from __future__ import annotations

import json
from typing import Any, Dict


def sse_event_stream(payload: Dict[str, Any]) -> str:
    """将一条业务事件格式化为 SSE 文本帧。"""
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
