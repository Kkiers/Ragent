from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.infra.mcp.config_file import McpServerEntry, coerce_env_values


def stdio_server_parameters(entry: McpServerEntry) -> StdioServerParameters:
    return StdioServerParameters(
        command=entry.command,
        args=list(entry.args or []),
        env=coerce_env_values(entry.env),
        cwd=entry.cwd,
    )


@asynccontextmanager
async def open_stdio_session(entry: McpServerEntry) -> AsyncIterator[ClientSession]:
    """
    打开一个 stdio MCP 会话（with 块结束时子进程会退出）。

    用法::
        async with open_stdio_session(entry) as session:
            await session.initialize()
            tools = await session.list_tools()
    """
    params = stdio_server_parameters(entry)
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            yield session
