from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import AsyncGenerator

# 职责：RAG 主链路编排服务
# 作用：
# 1. 接收用户请求
# 2. 先做 query 规整
# 3. 再做意图识别
# 4. 根据意图分流到 RAG / CHAT / CLARIFY / TOOL / WORKFLOW
# 5. 最终返回统一的 ChatResponse
#
# 这个文件只负责“编排流程”，不负责具体技术细节。
# 例如：
# - query 怎么清洗：交给 query_service
# - 意图怎么判断：交给 intent_service
# - 检索怎么做：交给 vector_store_search
# - 模型怎么回答：交给 llm_client

from app.domain.enums import IntentType
from app.domain.schemas import ChatRequest, ChatResponse
from app.framework.context import RequestContext
from app.pipeline.all_branch_pipeline import run_chat_pipeline
from app.pipeline.query_pipeline import run_query_pipeline
from app.services.intent_service import IntentServiceProtocol
from app.services.query_service import QueryServiceProtocol
from app.infra.chat_memory.sqlite_memory import ChatSqliteMemory
from app.infra.llm.client import LLMClient
from app.infra.vector_store_search.vector_search import VectorStore

_log = logging.getLogger(__name__)
from app.infra.observability.audit_sqlite import emit_event
import time


@dataclass
class StreamPersistContext:
    """流式路径在意图识别完成后写入 intent，供落库使用（不重复调用意图服务）。"""

    intent: str | None = None
    context: object | None = None


def create_rag_service(
    llm_client: LLMClient,
    vector_store: VectorStore,
    query_service: QueryServiceProtocol,
    intent_service: IntentServiceProtocol,
    chat_memory: ChatSqliteMemory | None = None,
):
    # 工厂函数
    # 作用是：把 rag_service 需要的依赖都传进来，然后创建一个 RagService 对象
    return RagService(
        llm_client=llm_client,
        vector_store=vector_store,
        query_service=query_service,
        intent_service=intent_service,
        chat_memory=chat_memory,
    )


class RagService:
    # 这个类是“总编排器”
    # 它不直接写复杂算法，只负责把各个阶段按顺序串起来

    def __init__(
        self,
        llm_client: LLMClient,
        vector_store: VectorStore,
        query_service: QueryServiceProtocol,
        intent_service: IntentServiceProtocol,
        chat_memory: ChatSqliteMemory | None = None,
    ):
        # 保存大模型客户端
        self.llm_client = llm_client

        # 保存向量库
        self.vector_store = vector_store

        # 保存 query 处理服务
        self.query_service = query_service

        # 保存意图识别服务
        self.intent_service = intent_service

        self._chat_memory = chat_memory

    async def attach_memory_to_request(self, req: ChatRequest) -> tuple[ChatRequest, str | None]:
        """启用 SQLite 记忆时：
        确保 session、用库里的历史替换请求里的 history。"""
        if self._chat_memory is None:
            return req, None
        # 要么新建sessionid 要么复用sessionid
        sid = await self._chat_memory.ensure_session(req.session_id)
        hist = await self._chat_memory.fetch_history(sid)
        return req.model_copy(update={"session_id": sid, "history": hist}), sid

    async def get_history(self, session_id: str | None) -> tuple[str | None, list]:
        """给 UI 使用：返回（可复用/新建的）session_id + 历史消息。"""
        if self._chat_memory is None:
            return None, []
        sid = await self._chat_memory.ensure_session(session_id)
        hist = await self._chat_memory.fetch_history(sid)
        return sid, hist

    async def persist_stream_turn(
        self,
        req: ChatRequest,
        trace_id: str,
        assistant_text: str,
        *,
        intent: str | None = None,
        context: object | None = None,
    ) -> None:
        """流式结束后写入 user/assistant；intent 由 StreamPersistContext 传入。"""
        if self._chat_memory is None or not req.session_id:
            return
        await self._chat_memory.record_exchange(
            session_id=req.session_id,
            trace_id=trace_id,
            user_content=req.query,
            assistant_content=assistant_text or "",
            intent=intent,
            context=context,
        )

    async def handle_chat(self, req: ChatRequest, ctx: RequestContext) -> ChatResponse:
        req, sid = await self.attach_memory_to_request(req)
        # 直接进入主问答链路（内部会先意图识别，且仅 RAG 才 rewriting）
        response = await run_chat_pipeline(
            req=req,
            ctx=ctx,
            query_service=self.query_service,
            intent_service=self.intent_service,
            llm_client=self.llm_client,
            vector_store=self.vector_store,
        )
        _log.info("RagService：主问答流水线已经完成。")

        if sid is not None:
            assert self._chat_memory is not None
            response = response.model_copy(update={"session_id": sid})
            assistant = response.answer or response.clarify_question or ""
            context = (response.meta or {}).get("_context_window")
            await self._chat_memory.record_exchange(
                session_id=sid,
                trace_id=ctx.trace_id,
                user_content=req.query,
                assistant_content=assistant,
                intent=response.intent.value,
                context=context,
            )
            # 内部字段不下发给前端
            if isinstance(response.meta, dict) and "_context_window" in response.meta:
                meta2 = dict(response.meta)
                meta2.pop("_context_window", None)
                response = response.model_copy(update={"meta": meta2})

        return response

    def handle_chat_stream(
        self,
        req: ChatRequest,
        ctx: RequestContext,
        stream_persist: StreamPersistContext | None = None,
    ) -> AsyncGenerator[str, None]:
        # 这个方法负责“流式返回”
        # 它返回的是一个异步生成器，也就是一个一个吐文本片段
        return self._stream_impl(req=req, ctx=ctx, stream_persist=stream_persist)

    async def _stream_impl(
        self,
        req: ChatRequest,
        ctx: RequestContext,
        stream_persist: StreamPersistContext | None = None,
    ) -> AsyncGenerator[str, None]:
        # 第 1 步：意图识别（不 rewriting）
        intent = await self.intent_service.identify_intent(
            query=req.query,
            history=req.history,
            ctx=ctx,
        )
        _log.info("RagService（流式）：意图识别已经完成。")

        # 仅 RAG 才 rewriting（用于检索）
        effective_query = (req.query or "").strip()
        query_result = None
        if intent.intent == IntentType.RAG:
            query_result = await run_query_pipeline(req=req, ctx=ctx, query_service=self.query_service)
            effective_query = (query_result.query or "").strip() or effective_query
            _log.info("RagService（流式）：RAG rewriting 已完成。")

        await emit_event(
            "intent_identified",
            route="POST /api/chat/stream",
            session_id=req.session_id,
            intent=intent.intent.value,
            fields={
                "score": getattr(intent, "score", None),
                "effective_query": effective_query,
                "did_rewrite": None if query_result is None else query_result.did_rewrite,
            },
        )
        if stream_persist is not None:
            stream_persist.intent = intent.intent.value

        # 第 3 步：分支处理
        if intent.intent == IntentType.CHAT:
            # 聊天分支：直接走普通模型回复
            await emit_event(
                "branch_selected",
                route="POST /api/chat/stream",
                session_id=req.session_id,
                intent=IntentType.CHAT.value,
            )
            provider_name, model_name = self.llm_client.model_info_for_stage("chat")
            t0 = time.perf_counter()
            await emit_event(
                "chat_llm_started",
                status="ok",
                route="POST /api/chat/stream",
                session_id=req.session_id,
                intent=IntentType.CHAT.value,
                model_provider=provider_name,
                model_name=model_name,
                fields={"query_len": len((req.query or "").strip()), "history_turns": len(list(req.history or []))},
            )
            try:
                cw_capture: dict[str, object] = {}
                answer = await self.llm_client.generate_chat(
                    query=req.query,
                    history=req.history,
                    context_debug=cw_capture,
                )
                dt_ms = int((time.perf_counter() - t0) * 1000)
                await emit_event(
                    "chat_llm_finished",
                    status="ok",
                    route="POST /api/chat/stream",
                    session_id=req.session_id,
                    intent=IntentType.CHAT.value,
                    model_provider=provider_name,
                    model_name=model_name,
                    fields={"duration_ms": dt_ms, "answer_len": len((answer or "").strip())},
                )
                if stream_persist is not None:
                    # 保存完整上下文（送给模型的 messages + report）
                    stream_persist.context = cw_capture
                _log.info("RagService（流式）：大模型闲聊生成已经完成。")
                async for chunk in self.llm_client.stream_text(answer, words_per_chunk=6):
                    yield chunk
                _log.info("RagService（流式）：闲聊分支流式推送已经完成。")
                return
            except Exception as e:
                dt_ms = int((time.perf_counter() - t0) * 1000)
                await emit_event(
                    "chat_llm_finished",
                    status="error",
                    route="POST /api/chat/stream",
                    session_id=req.session_id,
                    intent=IntentType.CHAT.value,
                    model_provider=provider_name,
                    model_name=model_name,
                    fields={"duration_ms": dt_ms, "error": (repr(e) or "")[:500]},
                )
                raise

        if intent.intent == IntentType.AGENT:
            await emit_event(
                "branch_selected",
                route="POST /api/chat/stream",
                session_id=req.session_id,
                intent=IntentType.AGENT.value,
            )
            # 复用非流式工具链路，然后把结果“流式吐出”
            response = await run_chat_pipeline(
                req=req,
                ctx=ctx,
                query_service=self.query_service,
                intent_service=self.intent_service,
                llm_client=self.llm_client,
                vector_store=self.vector_store,
            )
            if stream_persist is not None:
                stream_persist.context = (response.meta or {}).get("_context_window")
            text = response.answer or response.clarify_question or ""
            async for chunk in self.llm_client.stream_text(text, words_per_chunk=6):
                yield chunk
            return

        # RAG 分支
        await emit_event(
            "branch_selected",
            route="POST /api/chat/stream",
            session_id=req.session_id,
            intent=IntentType.RAG.value,
        )
        # 第 4 步：先检索
        docs = await self.vector_store.search(
            query=effective_query,
            top_k=req.top_k,
        )
        _log.info("RagService（流式）：向量检索已经完成。")

        # 第 5 步：重排
        reranked_docs = await self.llm_client.rerank(
            query=req.query,
            docs=docs,
        )
        _log.info("RagService（流式）：检索结果重排已经完成。")

        # 第 6 步：组装上下文
        context_text = self.llm_client.assemble_context(reranked_docs)
        _log.info("RagService（流式）：RAG 上下文组装已经完成。")

        # 第 7 步：流式生成答案
        cw_capture: dict[str, object] = {}
        async for chunk in self.llm_client.stream_answer(
            query=req.query,
            context=context_text,
            history=req.history,
            words_per_chunk=6,
            context_debug=cw_capture,
        ):
            yield chunk
        if stream_persist is not None:
            stream_persist.context = cw_capture
        _log.info("RagService（流式）：大模型 RAG 流式答案推送已经完成。")


