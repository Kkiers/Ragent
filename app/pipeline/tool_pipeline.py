"""
app.pipeline.tool_pipeline

这个文件实现“工具调用分支（TOOL intent）”的主流水线：
1) 给 LLM 一份工具列表 + schema
2) 让 LLM 输出一个严格 JSON（工具指令）
3) 解析/校验这个工具指令
4) 执行工具（本地工具或 MCP 工具）
5) 可选：把工具返回交给 LLM，生成最终回答

本文件也是“审计证据链”最关键的位置之一，因为它能在同一处同时拿到：
- 模型产出的工具指令（tool_plan_llm_output）
- 工具真实返回（tool_execute_end）
- 最终回填给用户的回答（final_answer_llm_end）
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from app.domain.enums import IntentType
from app.domain.schemas import ChatMessage, ChatRequest, ChatResponse
from app.framework.context import RequestContext
from app.infra.llm.client import LLMClient
from app.infra.llm.prompts import TOOL_CALLING_SYSTEM_PROMPT_TEMPLATE, TOOL_RESULT_TO_ANSWER_SYSTEM_PROMPT
from app.infra.mcp.invoke import invoke_mcp_tool
from app.infra.tools.combined_catalog import build_combined_tool_catalog, tools_json_for_prompt
from app.infra.tools.executor import create_default_executor
from app.infra.tools.register import create_default_registry
from app.infra.tools.tool_base import ToolContext, ToolResult
from app.infra.tools.tool_calling_schema import ToolCall, parse_tool_call, validate_tool_call
from app.infra.observability.audit_sqlite import emit_event

_log = logging.getLogger(__name__)


def _needs_clarify(tool_call: ToolCall) -> bool:
    # 第一版：只要 arguments 中出现 None，就认为缺关键信息需要澄清
    for v in tool_call.arguments.values():
        if v is None:
            return True
    return False


async def _ask_llm_for_tool_call(
    llm_client: LLMClient,
    user_query: str,
    effective_query: str,
    *,
    tools_json: str,
) -> tuple[str, str]:
    system = ChatMessage(
        role="system",
        content=TOOL_CALLING_SYSTEM_PROMPT_TEMPLATE.format(tools_json=tools_json),
    )
    user = ChatMessage(
        role="user",
        content=f"用户问题：{user_query}\n\n规整后的问题（可选参考）：{effective_query}",
    )
    text = await llm_client.chat([system, user], stage="agent")
    return system.content, text


async def _ask_llm_to_answer(llm_client: LLMClient, user_query: str, tool_call: ToolCall, tool_content: str) -> str:
    system = ChatMessage(role="system", content=TOOL_RESULT_TO_ANSWER_SYSTEM_PROMPT)
    user = ChatMessage(
        role="user",
        content=(
            f"用户问题：{user_query}\n\n"
            f"调用的工具：{tool_call.tool_name}\n"
            f"工具参数：{json.dumps(tool_call.arguments, ensure_ascii=False)}\n\n"
            f"工具结果：\n{tool_content}"
        ),
    )
    return await llm_client.chat([system, user], stage="agent")


async def run_tool_pipeline(
    *,
    req: ChatRequest,
    ctx: RequestContext,
    llm_client: LLMClient,
    tool_name: str,
    effective_query: str,
) -> ChatResponse:
    """
    通用 Tool Pipeline（第一版）：
    1) 给 LLM 工具列表 + schema
    2) 强约束 LLM 输出 JSON: {tool_name, arguments, reason}
    3) 解析 + 校验
    4) 执行工具
    5) 可选：把工具结果交给 LLM 生成最终回答
    """
    # 目前 intent_service 会把天气路由到 weather，但这里仍保留 tool_name 入参，便于以后扩展
    registry = create_default_registry()
    catalog = await build_combined_tool_catalog(registry=registry)
    specs = catalog.specs
    tools_json = tools_json_for_prompt(specs)

    await emit_event(
        "tool_planning_start",
        tool_name=tool_name,
        fields={"effective_query": effective_query, "available_tools": [s.name for s in specs]},
    )
    system_prompt, llm_text = await _ask_llm_for_tool_call(
        llm_client=llm_client,
        user_query=req.query,
        effective_query=effective_query,
        tools_json=tools_json,
    )
    await emit_event(
        "tool_plan_llm_output",
        tool_name=tool_name,
        payload=llm_text,
        fields={"system_prompt_sha256": None if not system_prompt else "sha256_hidden"},
    )
    tool_call = parse_tool_call(llm_text)
    if not tool_call:
        await emit_event(
            "tool_plan_parse_failed",
            status="error",
            tool_name=tool_name,
            payload=llm_text,
        )
        return ChatResponse(
            intent=IntentType.AGENT,
            answer=None,
            clarify_question="我没能解析出可执行的工具调用。请你换一种说法，或直接提供工具所需参数（例如经纬度 lat, lon）。",
            sources=[],
            trace_id=ctx.trace_id,
            meta={
                "tool_name": tool_name,
                "tool_calling_error": "parse_failed",
                "llm_output": llm_text[:800],
            },
        )

    ok, reason = validate_tool_call(tool_call, specs)
    if not ok:
        await emit_event(
            "tool_plan_validation_failed",
            status="error",
            tool_name=tool_call.tool_name,
            payload=llm_text,
            fields={"reason": reason, "parsed": {"tool_name": tool_call.tool_name, "arguments": tool_call.arguments}},
        )
        return ChatResponse(
            intent=IntentType.AGENT,
            answer=None,
            clarify_question=f"我需要补充信息才能调用工具：{reason}。你能补充一下吗？",
            sources=[],
            trace_id=ctx.trace_id,
            meta={
                "tool_name": tool_name,
                "tool_calling_error": "validation_failed",
                "validation_reason": reason,
                "tool_call": {"tool_name": tool_call.tool_name, "arguments": tool_call.arguments, "reason": tool_call.reason},
                "llm_output": llm_text[:800],
            },
        )

    if _needs_clarify(tool_call):
        await emit_event(
            "tool_plan_needs_clarify",
            status="error",
            tool_name=tool_call.tool_name,
            fields={"parsed": {"tool_name": tool_call.tool_name, "arguments": tool_call.arguments}},
        )
        return ChatResponse(
            intent=IntentType.AGENT,
            answer=None,
            clarify_question="我还缺少调用工具所需的关键信息。你可以给我更具体的地点，或直接提供经纬度（lat, lon）。",
            sources=[],
            trace_id=ctx.trace_id,
            meta={
                "tool_name": tool_name,
                "tool_call": {"tool_name": tool_call.tool_name, "arguments": tool_call.arguments, "reason": tool_call.reason},
            },
        )

    tool_ctx = ToolContext(trace_id=ctx.trace_id, timeout_seconds=10.0)
    mcp_route = catalog.mcp_routes.get(tool_call.tool_name)
    tool_result: ToolResult
    await emit_event(
        "tool_execute_start",
        tool_name=tool_call.tool_name,
        fields={"arguments": tool_call.arguments, "via": "mcp" if mcp_route is not None else "local"},
    )
    if mcp_route is not None and catalog.mcp_config_path:
        alias, mcp_name = mcp_route
        tool_result = await invoke_mcp_tool(
            Path(catalog.mcp_config_path),
            alias,
            mcp_name,
            tool_call.arguments,
            combined_display_name=tool_call.tool_name,
        )
    else:
        executor = create_default_executor()
        tool_result = await executor.execute(
            tool_name=tool_call.tool_name, arguments=tool_call.arguments, ctx=tool_ctx
        )
    _log.info("tool executed: %s ok=%s", tool_call.tool_name, tool_result.ok)
    await emit_event(
        "tool_execute_end",
        status="ok" if tool_result.ok else "error",
        tool_name=tool_call.tool_name,
        payload=tool_result.content,
        fields={"error": tool_result.error},
    )

    meta: dict[str, Any] = {
        "tool_name": tool_call.tool_name,
        "tool_call": {"tool_name": tool_call.tool_name, "arguments": tool_call.arguments, "reason": tool_call.reason},
    }
    if req.debug:
        meta["tool_system_prompt"] = system_prompt
        meta["tool_llm_output"] = llm_text[:1200]
        meta["tool_catalog"] = {
            "mcp_config": catalog.mcp_config_path,
            "tool_names": [s.name for s in specs],
            "mcp_errors": catalog.mcp_errors,
        }

    if not tool_result.ok:
        meta["tool_error"] = tool_result.error
        return ChatResponse(
            intent=IntentType.AGENT,
            answer=tool_result.content,
            clarify_question=None,
            sources=[],
            trace_id=ctx.trace_id,
            meta=meta,
        )

    # 可选回填：让 LLM 把工具输出整理成最终回答
    await emit_event(
        "final_answer_llm_start",
        tool_name=tool_call.tool_name,
        fields={"tool_ok": True},
    )
    final_answer = await _ask_llm_to_answer(
        llm_client=llm_client,
        user_query=req.query,
        tool_call=tool_call,
        tool_content=tool_result.content,
    )
    await emit_event(
        "final_answer_llm_end",
        tool_name=tool_call.tool_name,
        payload=final_answer,
        status="ok",
    )

    return ChatResponse(
        intent=IntentType.AGENT,
        answer=final_answer,
        clarify_question=None,
        sources=[],
        trace_id=ctx.trace_id,
        meta=meta,
    )
