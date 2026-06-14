"""
app.framework.exceptions

这个文件集中注册 FastAPI 的异常处理器（exception handlers）。

它的目的有两个：
- 把业务异常（AppError）统一转换成前端可读的 ApiResponse JSON
- 兜底捕获“未预料的异常”，打日志并返回 JSON（可选暴露 traceback）

在审计链路里，它还会写一条 unhandled_exception 事件，
避免“程序挂了但你不知道是在哪一步挂的”。
"""

import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.framework.response import API_JSON_MEDIA_TYPE
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.framework.response import ApiResponse

_log = logging.getLogger(__name__)
from app.infra.observability.audit_sqlite import emit_event


# 自定义应用异常类
@dataclass
class AppError(Exception):
    code: str  # 错误码
    message: str  # 错误信息
    status_code: int = 400  # HTTP 状态码，默认 400
    details: Optional[Dict[str, Any]] = None  # 额外信息，可选


# 注册异常处理函数
def register_exception_handlers(app: FastAPI) -> None:

    # 定义处理 AppError 异常的函数
    async def handle_app_error(request, exc: AppError):
        # 准备返回的 JSON 数据
        content = ApiResponse.fail(code=exc.code, message=exc.message, data=exc.details)
        # 把 ApiResponse 转换成 dict，JSONResponse 才能序列化
        json_content = content.model_dump()
        # 返回 JSONResponse，status_code 从异常里拿
        response = JSONResponse(
            status_code=exc.status_code, content=json_content, media_type=API_JSON_MEDIA_TYPE
        )
        return response  # 返回给客户端

    # 注册到 FastAPI
    app.add_exception_handler(AppError, handle_app_error)

    async def handle_unexpected(request: Request, exc: Exception):
        """未显式包装的异常：打日志并返回 JSON，便于脚本看到原因。"""
        if isinstance(exc, RequestValidationError):
            return await request_validation_exception_handler(request, exc)
        if isinstance(exc, StarletteHTTPException):
            return await http_exception_handler(request, exc)
        if isinstance(exc, AppError):
            return await handle_app_error(request, exc)
        try:
            await emit_event(
                "unhandled_exception",
                status="error",
                route=f"{request.method} {request.url.path}",
                fields={"type": type(exc).__name__, "message": (str(exc).strip() or type(exc).__name__)[:500]},
            )
        except Exception:
            # 观测不能影响主流程
            pass
        _log.exception("未处理异常")
        msg = (str(exc).strip() or type(exc).__name__)[:500]
        payload = ApiResponse.fail(
            code="INTERNAL_ERROR",
            message=msg,
            data={"type": type(exc).__name__},
        ).model_dump()
        if os.getenv("RAGENT_EXPOSE_ERRORS", "").strip().lower() in ("1", "true", "yes"):
            import traceback

            d = dict(payload.get("data") or {})
            d["traceback"] = traceback.format_exc()[-8000:]
            payload["data"] = d
        return JSONResponse(status_code=500, content=payload, media_type=API_JSON_MEDIA_TYPE)

    app.add_exception_handler(Exception, handle_unexpected)
