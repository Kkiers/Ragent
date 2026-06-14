from __future__ import annotations

from mcp.types import CallToolResult, ContentBlock, TextContent


def tool_result_to_text(result: CallToolResult) -> str:
    """
    将 MCP call_tool 返回拼成单一字符串（优先文本块；其它块做 str 回退）。
    """
    if result.isError:
        parts: list[str] = []
        for block in result.content or []:
            parts.append(_block_to_text(block))
        blob = "\n".join(p for p in parts if p).strip()
        return blob or "工具返回错误（isError=true）且无文本内容。"

    parts = []
    for block in result.content or []:
        t = _block_to_text(block)
        if t:
            parts.append(t)
    if parts:
        return "\n".join(parts).strip()
    sc = result.structuredContent
    if sc is not None:
        return str(sc).strip()
    return ""


def _block_to_text(block: ContentBlock) -> str:
    if isinstance(block, TextContent):
        return (block.text or "").strip()
    return str(block).strip()
