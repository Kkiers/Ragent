import logging
from typing import Any, Dict

from app.domain.enums import IntentType  # 导入意图类型枚举，用来判断分支
from app.domain.schemas import ChatRequest  # 导入请求结构
from app.domain.schemas import ChatResponse  # 导入响应结构
from app.framework.context import RequestContext  # 导入请求上下文
from app.infra.llm.client import LLMClient  # 导入模型调用客户端
from app.infra.vector_store_search.vector_search import VectorStore  # 导入向量检索客户端
from app.services.intent_service import IntentServiceProtocol  # 导入意图识别服务接口
from app.services.query_service import QueryServiceProtocol  # 导入 query 服务接口
from app.pipeline.tool_pipeline import run_tool_pipeline
from app.infra.observability.audit_sqlite import emit_event
from app.pipeline.query_pipeline import run_query_pipeline
import time

_log = logging.getLogger(__name__)


def _debug_common(req: ChatRequest, effective_query: str, intent) -> Dict[str, Any]:
    if not req.debug:
        return {}
    return {
        "effective_query": effective_query,
        "intent_score": intent.score,
    }


async def run_chat_pipeline(  # 定义问答主流水线
    req: ChatRequest,  # 用户请求对象
    ctx: RequestContext,  # 请求上下文对象
    query_service: QueryServiceProtocol,  # query 服务
    intent_service: IntentServiceProtocol,  # 意图识别服务
    llm_client: LLMClient,  # 模型调用客户端
    vector_store: VectorStore,  # 向量检索客户端
) -> ChatResponse:  # 这个函数最后返回 ChatResponse
    # 1) 先意图识别（
    intent = await intent_service.identify_intent(
        req.query,
        req.history,  # 输入历史消息
        ctx,  # 输入上下文
    )
    _log.info("意图识别已经完成。")

    # 2) 只有 RAG 才做 query rewriting，作为“检索用 query”
    query_norm = None
    effective_query = (req.query or "").strip()
    if intent.intent == IntentType.RAG:
        query_norm = await run_query_pipeline(req=req, ctx=ctx, query_service=query_service)
        effective_query = (query_norm.query or "").strip() or effective_query
        _log.info("RAG 分支 query rewriting 已完成。")

    await emit_event(
        "intent_identified",
        route="POST /api/chat",
        session_id=req.session_id,
        intent=intent.intent.value,
        fields={
            "score": getattr(intent, "score", None),
            "reason": getattr(intent, "reason", None),
            "effective_query": effective_query,
            "did_rewrite": None if query_norm is None else query_norm.did_rewrite,
        },
    )

    if intent.intent == IntentType.RAG:  # 如果意图是 RAG
        await emit_event(
            "branch_selected",
            route="POST /api/chat",
            session_id=req.session_id,
            intent=IntentType.RAG.value,
            fields={"top_k": req.top_k},
        )
        docs = await vector_store.search(effective_query, req.top_k)  # 去向量库检索文档
        _log.info("向量检索已经完成。")
        reranked_docs = await llm_client.rerank(req.query, docs)  # 对文档重排
        _log.info("检索结果重排已经完成。")
        context_text = llm_client.assemble_context(reranked_docs)  # 把文档拼成上下文
        _log.info("RAG 上下文组装已经完成。")
        cw_capture: Dict[str, Any] = {}
        cw_debug: Dict[str, Any] | None = cw_capture if req.debug else None
        answer = await llm_client.generate_answer(
            req.query,
            context_text,
            req.history,
            context_debug=cw_capture,
        )  # 调模型生成答案
        _log.info("大模型 RAG 答案生成已经完成。")

        source_ids = []  # 准备一个空列表，存放来源文档 id
        for d in reranked_docs:  # 遍历重排后的文档
            source_ids.append(d.doc_id)  # 把每个文档 id 放进去

        meta: Dict[str, Any] = {
            "did_rewrite": None if query_norm is None else query_norm.did_rewrite,
            **_debug_common(req, effective_query, intent),
            "_context_window": cw_capture,
        }
        if req.debug:
            meta.update(
                {
                    "retrieved_before_rerank": [
                        {"doc_id": d.doc_id, "score": d.score, "content": d.content} for d in docs
                    ],
                    "retrieved_after_rerank": [
                        {"doc_id": d.doc_id, "score": d.score, "content": d.content} for d in reranked_docs
                    ],
                    "context_text": context_text,
                    "llm_user_query": req.query,
                }
            )
            if cw_debug is not None:
                meta["context_window"] = cw_debug

        response = ChatResponse(  # 创建最终响应对象
            intent=IntentType.RAG,  # 记录这次走的是 RAG
            answer=answer,  # 保存模型生成的答案
            clarify_question=None,  # 这里不需要澄清问题
            sources=source_ids,  # 保存来源文档
            trace_id=ctx.trace_id,  # 保存 trace_id
            meta=meta,
        )  # 结束响应对象创建

        _log.info("RAG 分支响应封装已经完成。")
        return response  # 返回 RAG 响应

    elif intent.intent == IntentType.CHAT:  # 如果意图是闲聊
        await emit_event(
            "branch_selected",
            route="POST /api/chat",
            session_id=req.session_id,
            intent=IntentType.CHAT.value,
        )
        cw_capture: Dict[str, Any] = {}
        cw_debug: Dict[str, Any] | None = cw_capture if req.debug else None
        provider_name, model_name = llm_client.model_info_for_stage("chat")
        t0 = time.perf_counter()
        await emit_event(
            "chat_llm_started",
            status="ok",
            route="POST /api/chat",
            session_id=req.session_id,
            intent=IntentType.CHAT.value,
            model_provider=provider_name,
            model_name=model_name,
            fields={"query_len": len((req.query or "").strip()), "history_turns": len(list(req.history or []))},
        )
        try:
            answer = await llm_client.generate_chat(req.query, req.history, context_debug=cw_capture)  # 直接让模型聊天
            dt_ms = int((time.perf_counter() - t0) * 1000)
            await emit_event(
                "chat_llm_finished",
                status="ok",
                route="POST /api/chat",
                session_id=req.session_id,
                intent=IntentType.CHAT.value,
                model_provider=provider_name,
                model_name=model_name,
                fields={"duration_ms": dt_ms, "answer_len": len((answer or "").strip())},
            )
            _log.info("大模型闲聊回复已经完成。")
        except Exception as e:
            dt_ms = int((time.perf_counter() - t0) * 1000)
            await emit_event(
                "chat_llm_finished",
                status="error",
                route="POST /api/chat",
                session_id=req.session_id,
                intent=IntentType.CHAT.value,
                model_provider=provider_name,
                model_name=model_name,
                fields={"duration_ms": dt_ms, "error": (repr(e) or "")[:500]},
            )
            raise
        chat_meta = _debug_common(req, effective_query, intent)
        if req.debug and cw_debug is not None:
            chat_meta = {**chat_meta, "context_window": cw_debug}
        # 供服务端 Chat Memory 落库使用，不下发给前端（由 RagService.handle_chat 移除）
        chat_meta["_context_window"] = cw_capture
        response = ChatResponse(  # 创建聊天响应
            intent=IntentType.CHAT,  # 保存意图
            answer=answer,  # 保存聊天答案
            clarify_question=None,  # 不需要澄清
            sources=[],  # 没有来源文档
            trace_id=ctx.trace_id,  # 保存 trace_id
            meta=chat_meta,
        )  # 结束对象创建

        _log.info("闲聊分支响应封装已经完成。")
        return response  # 返回聊天响应

    elif intent.intent == IntentType.AGENT:
        await emit_event(
            "branch_selected",
            route="POST /api/chat",
            session_id=req.session_id,
            intent=IntentType.AGENT.value,
        )
        response = await run_tool_pipeline(
            req=req,
            ctx=ctx,
            llm_client=llm_client,
            tool_name="auto",
            effective_query=effective_query,
        )
        if req.debug:
            response.meta.update(_debug_common(req, effective_query, intent))
        _log.info("AGENT 分支响应封装已经完成。")
        return response
    else:  # 如果以上都不是
        raise RuntimeError("Unhandled intent")  # 抛出错误，说明出现了没覆盖的情况
