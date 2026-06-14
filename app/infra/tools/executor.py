from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from app.infra.tools.register import ToolRegistry, create_default_registry
from app.infra.tools.tool_base import ToolContext, ToolResult

logger = logging.getLogger(__name__)
"""
统一工具执行入口，负责按名字取工具、执行工具、返回结果。`
"""

@dataclass
class ToolExecutor:
    registry: ToolRegistry

    async def execute(self, tool_name: str, arguments: dict[str, Any], ctx: ToolContext) -> ToolResult:
        try:
            tool = self.registry.get(tool_name)
        except Exception as exc:
            msg = str(exc).strip() or type(exc).__name__
            return ToolResult(
                tool_name=(tool_name or "").strip() or "<unknown>",
                ok=False,
                content="工具不存在或不可用。",
                raw=None,
                error=msg[:400],
            )

        try:
            return await tool.run(arguments=arguments or {}, ctx=ctx)
        except Exception as exc:
            logger.exception("Tool 执行失败: %s", tool_name)
            msg = str(exc).strip() or type(exc).__name__
            return ToolResult(
                tool_name=tool.name,
                ok=False,
                content="工具执行失败。",
                raw=None,
                error=msg[:400],
            )

# 内部调用 create_default_registry()，把 WeatherTool 注册好
def create_default_executor() -> ToolExecutor:
    return ToolExecutor(registry=create_default_registry())

# test
# import asyncio
# if __name__ == "__main__":
#     async def main():
#         executor = create_default_executor()
#         result = await executor.execute(
#             tool_name="weather",
#             arguments={"latitude": 38.8977, "longitude": -77.0365},
#             ctx=ToolContext(trace_id="t1"),
#         )
#         print(result.ok)
#         print(result.content)
#         print(result.error)
#
#     asyncio.run(main())