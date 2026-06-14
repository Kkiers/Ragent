from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

"""
定义“工具长什么样、返回什么、怎么执行”
"""


# 工具执行时带的上下文
@dataclass
class ToolContext:
    trace_id: str | None = None
    timeout_seconds: float = 10.0

# 工具说明书：名字、描述、输入参数
@dataclass
class ToolSpec:
    name: str
    description: str
    input_schema: dict[str, Any] = field(default_factory=dict)

# 工具执行结果：成功/失败、返回值、错误信息
@dataclass
class ToolResult:
    tool_name: str
    ok: bool
    content: str
    raw: dict[str, Any] | None = None
    error: str | None = None

# 抽象基类：所有工具都要遵守的接口
class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def description(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def input_schema(self) -> dict[str, Any]:
        raise NotImplementedError

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name=self.name,
            description=self.description,
            input_schema=self.input_schema,
        )

    @abstractmethod
    async def run(
        self,
        arguments: dict[str, Any],
        ctx: ToolContext,
    ) -> ToolResult:
        raise NotImplementedError