from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from app.infra.mcp.config_file import load_mcp_file_config
from app.infra.mcp.results import tool_result_to_text
from app.infra.mcp.stdio_connect import open_stdio_session
from app.infra.tools.tool_base import ToolResult

_log = logging.getLogger(__name__)


async def invoke_mcp_tool(
    config_path: Path,
    server_alias: str,
    mcp_tool_name: str,
    arguments: dict[str, Any],
    *,
    combined_display_name: str,
) -> ToolResult:
    """
    为单次工具调用临时建立 stdio MCP 会话并 call_tool（与 catalog 缓存策略独立）。
    """
    try:
        cfg = load_mcp_file_config(config_path)
    except Exception as exc:
        _log.exception("invoke_mcp_tool: 读取配置失败")
        return ToolResult(
            tool_name=combined_display_name,
            ok=False,
            content="无法读取 MCP 配置文件。",
            raw=None,
            error=str(exc)[:400],
        )

    entry = cfg.mcpServers.get(server_alias)
    if entry is None:
        return ToolResult(
            tool_name=combined_display_name,
            ok=False,
            content="MCP 配置中找不到对应服务器别名。",
            raw=None,
            error=f"unknown mcp server: {server_alias}",
        )

    try:
        async with open_stdio_session(entry) as session:
            await session.initialize()
            result = await session.call_tool(mcp_tool_name, arguments=arguments or {})
            text = tool_result_to_text(result)
            ok = not bool(result.isError)
            return ToolResult(
                tool_name=combined_display_name,
                ok=ok,
                content=text or ("(空结果)" if ok else "工具返回错误。"),
                raw=None,
                error=None if ok else (text[:400] if text else "isError"),
            )
    except Exception as exc:
        _log.exception("invoke_mcp_tool: 执行失败 server=%s tool=%s", server_alias, mcp_tool_name)
        msg = str(exc).strip() or type(exc).__name__
        return ToolResult(
            tool_name=combined_display_name,
            ok=False,
            content="MCP 工具执行失败。",
            raw=None,
            error=msg[:400],
        )
