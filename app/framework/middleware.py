"""
app.framework.middleware

这个文件放的是 FastAPI/Starlette 的中间件（所有请求都会经过）。

在本项目里它承担两件事：
- 为每个 HTTP 请求生成 trace_id，并写入 request.state.trace_id（便于 API 层取用）
- 同时把 trace_id 安装到 contextvars（“背景音乐”），并在请求入口/出口各写一条审计事件：
  - request_received
  - response_sent（带总耗时、HTTP 状态码）

这样你就能用 trace_id 把一次请求的所有中间产物串成时间线。
"""

import time
import uuid
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

# 观测：背景音乐 + 事件落库（基础设施层）
from app.infra.observability.trace_ctx import reset_trace, set_trace
from app.infra.observability.audit_sqlite import emit_event

# 定义中间件类，每个请求都会经过这个中间件
class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 给请求增加 trace_id
        new_trace_id = str(uuid.uuid4())  # 生成新的 UUID
        request.state.trace_id = new_trace_id  # 放到 request.state.trace_id
        tokens = set_trace(new_trace_id)
        t0 = time.perf_counter()
        await emit_event(
            "request_received",
            route=f"{request.method} {request.url.path}",
            fields={
                "client": getattr(request.client, "host", None),
                "user_agent": request.headers.get("user-agent"),
            },
        )
        # 继续调用下一个中间件或最终路由处理
        try:
            response = await call_next(request)
            return response  # 返回响应给客户端
        finally:
            dt_ms = int((time.perf_counter() - t0) * 1000)
            status_code = getattr(locals().get("response", None), "status_code", None)
            await emit_event(
                "response_sent",
                status="ok" if (status_code and int(status_code) < 500) else "error",
                route=f"{request.method} {request.url.path}",
                fields={"status_code": status_code, "duration_ms": dt_ms},
            )
            reset_trace(tokens)

# 注册中间件的函数
def add_request_context_middleware(app: FastAPI) -> None:
    app.add_middleware(RequestContextMiddleware)  # FastAPI 里增加这个中间件