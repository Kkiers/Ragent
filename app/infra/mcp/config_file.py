from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

class McpServerEntry(BaseModel):
    """与 Cursor / Claude Desktop 中单个 mcpServers 条目对齐（stdio）。"""

    command: str
    args: list[str] = Field(default_factory=list)
    # 市场 JSON 里常见为字符串；偶发为数字，在 stdio_server_parameters 里统一转成 str
    env: dict[str, object] | None = None
    cwd: str | None = None


class McpFileConfig(BaseModel):
    """顶层 JSON：{ \"mcpServers\": { \"别名\": { command, args, env?, cwd? } } }"""

    mcpServers: dict[str, McpServerEntry]


def load_mcp_file_config(path: str | Path) -> McpFileConfig:
    raw = Path(path).read_text(encoding="utf-8")
    data: Any = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("MCP 配置文件顶层必须是 JSON 对象")
    return McpFileConfig.model_validate(data)


def coerce_env_values(env: dict[str, object] | None) -> dict[str, str] | None:
    """部分市场 JSON 里 env 值可能是数字；StdioServerParameters 需要 str。"""
    if env is None:
        return None
    out: dict[str, str] = {}
    for k, v in env.items():
        out[str(k)] = v if isinstance(v, str) else str(v)
    return out
