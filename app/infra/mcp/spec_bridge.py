from __future__ import annotations

from typing import Any

from mcp.types import Tool as McpTool

from app.infra.tools.tool_base import ToolSpec


def _input_schema_dict(tool: McpTool) -> dict[str, Any]:
    s = tool.inputSchema
    if s is None:
        return {"type": "object", "properties": {}}
    if isinstance(s, dict):
        return s
    if hasattr(s, "model_dump"):
        return s.model_dump(mode="json", exclude_none=True)  # type: ignore[no-any-return]
    return {"type": "object", "properties": {}}


def mcp_tool_to_tool_spec(tool: McpTool, *, name_prefix: str = "") -> ToolSpec:
    """
    把 MCP 的 Tool 定义映射为 Ragent 的 ToolSpec（给现有 JSON tool-calling 用）。

    name_prefix：多服务器并存时建议 ``f\"{server_alias}__\"`` 避免重名。
    """
    base = (tool.name or "").strip()
    name = f"{name_prefix}{base}" if name_prefix else base
    desc = (tool.description or "").strip()
    return ToolSpec(name=name, description=desc, input_schema=_input_schema_dict(tool))
