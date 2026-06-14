from __future__ import annotations

import asyncio
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.infra.mcp.config_file import load_mcp_file_config
from app.infra.mcp.spec_bridge import mcp_tool_to_tool_spec
from app.infra.mcp.stdio_connect import open_stdio_session
from app.infra.tools.register import ToolRegistry, create_default_registry
from app.infra.tools.tool_base import ToolSpec

_log = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_MCP_REL = Path("config") / "mcp_servers.json"

# 同一进程内缓存合并结果，避免每次 TOOL 请求都重新拉起所有 MCP 子进程
_CATALOG_TTL_SEC = 30.0
_catalog_lock = asyncio.Lock()
_catalog_cache_mono: float | None = None
_catalog_cache_value: CombinedToolCatalog | None = None


@dataclass
class CombinedToolCatalog:
    """给模型用的总工具列表 + MCP 路由表（用于执行 call_tool）。"""

    specs: list[ToolSpec]
    # combined_tool_name -> (mcp_server别名, MCP 原始工具名)
    mcp_routes: dict[str, tuple[str, str]] = field(default_factory=dict)
    mcp_errors: list[dict[str, str]] = field(default_factory=list)
    mcp_config_path: str | None = None


def resolve_mcp_config_path() -> Path | None:
    """
    MCP JSON 路径：
    1) 环境变量 RAGENT_MCP_CONFIG（绝对路径或相对当前工作目录）
    2) 否则若存在 <项目根>/config/mcp_servers.json 则用之
    3) 否则 None（仅本地注册表工具）
    """
    raw = (os.environ.get("RAGENT_MCP_CONFIG") or "").strip()
    if raw:
        p = Path(raw)
        if not p.is_file():
            _log.warning("RAGENT_MCP_CONFIG 指向的文件不存在: %s", p.resolve())
            return None
        return p.resolve()

    candidate = (_PROJECT_ROOT / _DEFAULT_MCP_REL).resolve()
    if candidate.is_file():
        return candidate
    return None


def _specs_tools_json_payload(specs: list[ToolSpec]) -> list[dict[str, Any]]:
    return [{"name": s.name, "description": s.description, "input_schema": s.input_schema} for s in specs]


async def _build_combined_tool_catalog_uncached(
    *,
    registry: ToolRegistry | None = None,
    mcp_config_path: Path | None = None,
) -> CombinedToolCatalog:
    reg = registry or create_default_registry()
    local_specs = reg.list_specs()
    mcp_specs: list[ToolSpec] = []
    mcp_routes: dict[str, tuple[str, str]] = {}
    mcp_errors: list[dict[str, str]] = []

    cfg_path = mcp_config_path if mcp_config_path is not None else resolve_mcp_config_path()
    if cfg_path is None:
        return CombinedToolCatalog(
            specs=list(local_specs),
            mcp_routes={},
            mcp_errors=[],
            mcp_config_path=None,
        )

    try:
        file_cfg = load_mcp_file_config(cfg_path)
    except Exception as exc:
        _log.exception("读取 MCP 配置失败: %s", cfg_path)
        mcp_errors.append({"server": "<config>", "error": str(exc)[:500]})
        return CombinedToolCatalog(
            specs=list(local_specs),
            mcp_routes={},
            mcp_errors=mcp_errors,
            mcp_config_path=str(cfg_path),
        )

    for alias, entry in file_cfg.mcpServers.items():
        try:
            async with open_stdio_session(entry) as session:
                await session.initialize()
                listed = await session.list_tools()
                for t in listed.tools:
                    spec = mcp_tool_to_tool_spec(t, name_prefix=f"{alias}__")
                    mcp_specs.append(spec)
                    mcp_routes[spec.name] = (alias, t.name)
        except Exception as exc:
            _log.warning("MCP 服务器 %s 列举工具失败: %s", alias, exc, exc_info=False)
            mcp_errors.append({"server": alias, "error": str(exc)[:500]})

    return CombinedToolCatalog(
        specs=[*local_specs, *mcp_specs],
        mcp_routes=mcp_routes,
        mcp_errors=mcp_errors,
        mcp_config_path=str(cfg_path),
    )


async def build_combined_tool_catalog(
    *,
    registry: ToolRegistry | None = None,
    mcp_config_path: Path | None = None,
    force_refresh: bool = False,
) -> CombinedToolCatalog:
    """
    合并「本地 ToolRegistry」与「MCP list_tools」得到的 ToolSpec 列表。

    默认带 30s 内存缓存；调试接口可传 force_refresh=True。
    """
    global _catalog_cache_mono, _catalog_cache_value
    async with _catalog_lock:
        now = time.monotonic()
        if (
            not force_refresh
            and _catalog_cache_value is not None
            and _catalog_cache_mono is not None
            and (now - _catalog_cache_mono) < _CATALOG_TTL_SEC
        ):
            return _catalog_cache_value

        cat = await _build_combined_tool_catalog_uncached(
            registry=registry,
            mcp_config_path=mcp_config_path,
        )
        _catalog_cache_mono = now
        _catalog_cache_value = cat
        return cat


def tools_json_for_prompt(specs: list[ToolSpec]) -> str:
    """与 tool_pipeline 原先 _tools_json 相同结构，入参改为显式 specs。"""
    import json

    return json.dumps(_specs_tools_json_payload(specs), ensure_ascii=False)
