"""
Ragent 侧 MCP 集成（仅用官方 mcp SDK，不经过 langchain-mcp-adapters）。

典型用法：
1) 读 JSON（与 Cursor 的 mcpServers 结构兼容）
2) stdio_client + ClientSession 建连并 initialize
3) list_tools → 转成项目内的 ToolSpec（供 prompt / 校验）
4) call_tool → 转成可读字符串（供二次总结或返回用户）
"""

from app.infra.mcp.config_file import McpFileConfig, McpServerEntry, load_mcp_file_config
from app.infra.mcp.results import tool_result_to_text
from app.infra.mcp.spec_bridge import mcp_tool_to_tool_spec
from app.infra.mcp.stdio_connect import open_stdio_session, stdio_server_parameters

__all__ = [
    "McpFileConfig",
    "McpServerEntry",
    "load_mcp_file_config",
    "mcp_tool_to_tool_spec",
    "open_stdio_session",
    "stdio_server_parameters",
    "tool_result_to_text",
]
