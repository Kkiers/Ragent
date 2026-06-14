from typing import Any, Optional

from fastapi.responses import JSONResponse
from pydantic import BaseModel

# 显式 charset，避免部分客户端（如 Windows PowerShell 5.x IWR）按系统编码误解析 UTF-8
API_JSON_MEDIA_TYPE = "application/json; charset=utf-8"


class Utf8JSONResponse(JSONResponse):
    media_type = API_JSON_MEDIA_TYPE


"""统一返回结构"""
# 定义返回给客户端的统一数据结构
class ApiResponse(BaseModel):
    code: str  # 状态码，"OK" 或者自定义错误码
    message: str  # 提示信息，比如 "success" 或者错误信息
    data: Optional[Any] = None  # 可选的业务数据，可能是 dict / list / str

    @staticmethod
    def ok(data: Any = None, message: str = "success") -> "ApiResponse":
        """与常见命名一致；等价于 api_ok。"""
        return ApiResponse.api_ok(data=data, message=message)

    # 返回成功结果的函数
    @staticmethod
    def api_ok(data: Any = None, message: str = "success") -> "ApiResponse":
        return ApiResponse(code="OK", message=message, data=data)

    # 返回失败结果的函数
    @staticmethod
    def fail(code: str, message: str, data: Any = None) -> "ApiResponse":
        return ApiResponse(code=code, message=message, data=data)