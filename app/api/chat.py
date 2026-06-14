import logging

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from app.framework.response import Utf8JSONResponse

from app.domain.schemas import ChatRequest
from app.framework.context import get_request_context
from app.framework.response import ApiResponse
from app.framework.sse import sse_event_stream
from app.infra.observability.audit_sqlite import emit_event
from app.infra.observability.trace_ctx import reset_trace, set_trace
from app.services.rag_service import StreamPersistContext

router = APIRouter(prefix="/api", tags=["chat"])
_log = logging.getLogger(__name__)

SESSION_COOKIE_NAME = "rag_session_id"

@router.get("/chat/history")
async def chat_history(request: Request):
    """页面刷新后用于恢复历史：从 Cookie 取 session_id，返回该会话历史。"""
    rag_service = request.app.state.rag_service
    sid, hist = await rag_service.get_history(request.cookies.get(SESSION_COOKIE_NAME))
    payload = ApiResponse.ok(
        data={"session_id": sid, "history": [m.model_dump(mode="json") for m in hist]},
    ).model_dump(mode="json")
    resp = Utf8JSONResponse(content=payload)
    if sid:
        resp.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=sid,
            httponly=True,
            samesite="lax",
        )
    return resp


@router.post("/chat")
async def chat_json(req: ChatRequest, request: Request):
    ctx = get_request_context(request)
    _log.info("Chat 请求体验证与上下文准备已经完成。")
    rag_service = request.app.state.rag_service
    if not req.session_id:
        req = req.model_copy(update={"session_id": request.cookies.get(SESSION_COOKIE_NAME)})
    resp = await rag_service.handle_chat(req, ctx)
    _log.info("Chat 业务处理与响应数据组装已经完成。")
    payload = ApiResponse.ok(data=resp.model_dump(mode="json")).model_dump(mode="json")
    response = Utf8JSONResponse(content=payload)
    if resp.session_id:
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=resp.session_id,
            httponly=True,
            samesite="lax",
        )
    return response

@router.post("/chat/stream")
async def chat_stream(req: ChatRequest, request: Request):
    ctx = get_request_context(request)
    _log.info("Chat 流式请求体验证与上下文准备已经完成。")
    rag_service = request.app.state.rag_service
    if not req.session_id:
        req = req.model_copy(update={"session_id": request.cookies.get(SESSION_COOKIE_NAME)})
    req, sid = await rag_service.attach_memory_to_request(req)
    stream_persist = StreamPersistContext() if sid is not None else None
    token_stream = rag_service.handle_chat_stream(req, ctx, stream_persist)

    async def event_generator():
        # StreamingResponse 会在“开始推流后”才执行这个生成器。
        # 但中间件的 finally（emit response_sent + reset_trace）会在返回 StreamingResponse 后立刻执行，
        # 导致 contextvars 中的 trace_id 被提前清理。
        # 因此这里需要把 trace_id 重新安装到当前生成器任务上下文里，保证审计事件能落库。
        tokens = set_trace(ctx.trace_id)
        try:
            await emit_event(
                "stream_start",
                route="POST /api/chat/stream",
                session_id=sid,
                fields={"stream": True},
            )
            if sid is not None:
                yield sse_event_stream({"type": "meta", "session_id": sid})
            parts: list[str] = []
            async for chunk in token_stream:
                parts.append(chunk)
                yield sse_event_stream({"type": "delta", "content": chunk})
            await rag_service.persist_stream_turn(
                req,
                ctx.trace_id,
                "".join(parts),
                intent=stream_persist.intent if stream_persist else None,
                context=stream_persist.context if stream_persist else None,
            )
            yield sse_event_stream({"type": "done"})
            _log.info("Chat 流式 SSE 推送已经完成。")
            await emit_event(
                "stream_end",
                status="ok",
                route="POST /api/chat/stream",
                session_id=sid,
                fields={"assistant_chars": len("".join(parts))},
            )
        except Exception as e:
            # 典型场景：客户端中途断开、上游超时、生成器异常。
            # 这里不向客户端再写 SSE（连接可能已断），只保证审计留痕。
            await emit_event(
                "stream_end",
                status="error",
                route="POST /api/chat/stream",
                session_id=sid,
                fields={"error": repr(e)},
            )
            raise
        finally:
            reset_trace(tokens)

    response = StreamingResponse(event_generator(), media_type="text/event-stream")
    if sid is not None:
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=sid,
            httponly=True,
            samesite="lax",
        )
    return response