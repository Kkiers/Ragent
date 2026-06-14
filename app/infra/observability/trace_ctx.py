"""
app.infra.observability.trace_ctx

这个文件负责“背景音乐式”的请求上下文传递：
- 在每次 HTTP 请求进入时安装 trace_id（快递单号）
- 在同一个异步任务/协程内，任何深层函数都可以随时 get 到 trace_id
- 同时维护一个自增 seq，用来给审计事件排序，确保你能按 seq 还原真实时间线

它的作用是：让审计/日志不需要层层把 trace_id 当参数传下去（避免污染业务函数签名）。
"""

from __future__ import annotations

import contextvars
from dataclasses import dataclass


# “背景音乐”：只在当前请求/协程上下文内可见（并发安全）
_trace_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("trace_id", default=None)
_seq_var: contextvars.ContextVar[int] = contextvars.ContextVar("audit_seq", default=0)


@dataclass(frozen=True)
class TraceTokens:
    trace_id_token: contextvars.Token[str | None]
    seq_token: contextvars.Token[int]


def set_trace(trace_id: str) -> TraceTokens:
    """在入口处安装 trace_id，并把事件序号清零。"""
    t1 = _trace_id_var.set(trace_id)
    t2 = _seq_var.set(0)
    return TraceTokens(trace_id_token=t1, seq_token=t2)


def reset_trace(tokens: TraceTokens) -> None:
    _trace_id_var.reset(tokens.trace_id_token)
    _seq_var.reset(tokens.seq_token)


def get_trace_id() -> str | None:
    return _trace_id_var.get()


def next_seq() -> int:
    """每写一条事件 +1，保证同一 trace 下可按 seq 排序。"""
    cur = _seq_var.get()
    cur += 1
    _seq_var.set(cur)
    return cur

