from __future__ import annotations

from dataclasses import dataclass, field

from app.infra.tools.tool_base import BaseTool, ToolSpec
from app.infra.tools.weather import WeatherTool

"""
注册工具、按名字取工具、列出工具说明（spec），
并提供一个“默认注册表”（把 WeatherTool 注册进去）。
"""

# 工具注册表本体
@dataclass
class ToolRegistry:
    tools: dict[str, BaseTool] = field(default_factory=dict)

    def register(self, tool: BaseTool) -> None:
        name = tool.name.strip()
        if not name:
            raise ValueError("tool.name 不能为空")
        if name in self.tools:
            raise ValueError(f"tool 已存在: {name}")
        self.tools[name] = tool

    def get(self, name: str) -> BaseTool:
        key = (name or "").strip()
        if not key:
            raise ValueError("tool name 不能为空")
        tool = self.tools.get(key)
        if not tool:
            raise KeyError(f"未注册的 tool: {key}")
        return tool

    def list_specs(self) -> list[ToolSpec]:
        return [tool.spec() for tool in self.tools.values()]


def create_default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(WeatherTool())
    return registry

