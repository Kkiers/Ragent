from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, Query

from app.framework.response import ApiResponse
from app.infra.tools.combined_catalog import build_combined_tool_catalog

router = APIRouter(prefix="/api", tags=["tools"])


@router.get("/tools/catalog")
async def get_tools_catalog(
    refresh: bool = Query(False, description="为 true 时跳过 30s 缓存，重新连接 MCP 列举工具"),
):
    """
    返回「本地注册表 + MCP list_tools」合并后的总工具列表，便于自检与对接前端。
    """
    cat = await build_combined_tool_catalog(force_refresh=refresh)
    data = {
        "mcp_config": cat.mcp_config_path,
        "local_tool_count": max(0, len(cat.specs) - len(cat.mcp_routes)),
        "mcp_tool_count": len(cat.mcp_routes),
        "total": len(cat.specs),
        "tools": [asdict(s) for s in cat.specs],
        "mcp_errors": cat.mcp_errors,
        "mcp_disabled_or_empty": len(cat.mcp_routes) == 0,
        "note": "MCP 工具名带「服务器别名__」前缀；存在 config/mcp_servers.json 或环境变量 RAGENT_MCP_CONFIG 指向有效文件时加载 MCP。",
    }
    return ApiResponse.ok(data=data)
