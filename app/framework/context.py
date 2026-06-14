from fastapi import Request
from dataclasses import dataclass
import uuid


@dataclass
class RequestContext:
    trace_id: str

def get_request_context(request: Request) -> RequestContext:
    # 尝试从request.state 中获取trace_id
    trace_id = None
    if hasattr(request.state, "trace_id"):
        trace_id = request.state.trace_id
    # 如果没有 trace_id，就生成一个新的 UUID
    if trace_id is None:
        trace_id = str(uuid.uuid4())  # uuid.uuid4() 生成唯一字符串
    # 返回 RequestContext 对象
    ctx = RequestContext(trace_id=trace_id)
    return ctx