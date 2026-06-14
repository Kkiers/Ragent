from __future__ import annotations

from collections.abc import Awaitable, Callable

from app.domain.context import (
    ContextAssemblyRequest,
    ContextAssemblyResult,
    ContextWindowSettings,
    TruncationReport,
)
from app.domain.schemas import ChatMessage
from app.context_window.settings import default_context_window_settings
from app.context_window.token_counter import ApproxTokenCounter, default_counter

_TRUNC_MARKER = "\n...[已截断]..."

HistorySummarizer = Callable[[str, int], Awaitable[str]]


def _truncate_content_to_token_budget(
    text: str,
    max_tokens: int,
    counter: ApproxTokenCounter,
) -> tuple[str, bool]:
    s = text or ""
    if not s:
        return "", False
    if counter.content_tokens(s) <= max_tokens:
        return s, False

    lo, hi = 0, len(s)
    best = ""
    while lo <= hi:
        mid = (lo + hi) // 2
        candidate = s[:mid]
        if mid < len(s):
            candidate = candidate + _TRUNC_MARKER
        if counter.content_tokens(candidate) <= max_tokens:
            best = candidate
            lo = mid + 1
        else:
            hi = mid - 1
    if not best:
        return _TRUNC_MARKER.strip(), True
    return best, True


def _message_overhead(counter: ApproxTokenCounter, role: str) -> int:
    return counter.message_tokens(ChatMessage(role=role, content="x")) - counter.content_tokens("x")


def _split_old_and_recent(
    history: list[ChatMessage],
    recent_exchange_rounds: int,
) -> tuple[list[ChatMessage], list[ChatMessage]]:
    k = max(0, recent_exchange_rounds * 2)
    if not history or k == 0:
        return list(history), []
    if len(history) <= k:
        return [], list(history)
    return list(history[:-k]), list(history[-k:])


def _history_to_text(msgs: list[ChatMessage]) -> str:
    lines: list[str] = []
    for m in msgs:
        label = {"user": "用户", "assistant": "助手", "system": "系统"}.get(m.role, m.role)
        lines.append(f"{label}：{m.content}")
    return "\n".join(lines)


def _build_system_body(
    base: str,
    *,
    earlier_summary: str,
    current_retrieval: str,
    current_tool: str,
) -> str:
    parts: list[str] = [(base or "").strip()]
    es = (earlier_summary or "").strip()
    if es:
        parts.append("\n\n【更早对话摘要】\n" + es)
    cr = (current_retrieval or "").strip()
    if cr:
        parts.append("\n\n【本轮检索】\n" + cr)
    ct = (current_tool or "").strip()
    if ct:
        parts.append("\n\n【本轮工具输出】\n" + ct)
    return "".join(parts)


def _messages_tokens(
    system_body: str,
    old_msgs: list[ChatMessage],
    recent_msgs: list[ChatMessage],
    user_msg: ChatMessage,
    counter: ApproxTokenCounter,
) -> int:
    msgs = [
        ChatMessage(role="system", content=system_body),
        *old_msgs,
        *recent_msgs,
        user_msg,
    ]
    return counter.messages_tokens(msgs)


async def assemble_context_window(
    req: ContextAssemblyRequest,
    *,
    counter: ApproxTokenCounter | None = None,
    summarizer: HistorySummarizer | None = None,
) -> ContextAssemblyResult:
    """
    单一总预算 + 按优先级注水：
    P1 system prompt + 当前 user
    P2 本轮检索、本轮工具输出（动态占满剩余中的优先段）
    P3 最近若干轮原始 history
    P4 更早 history：优先摘要；无 summarizer 则逐条丢弃最旧
    超窗时：先处理 P4 → 再缩 P2（先压工具输出再压本轮检索）→ 再动 P3 → 最后才动 P1
    """
    c = counter or default_counter()
    settings = req.settings or default_context_window_settings()
    report = TruncationReport()
    T = settings.max_total_tokens

    base = (req.system_prompt or "").strip()
    user_text = (req.user_query or "").strip()
    user_msg = ChatMessage(role="user", content=user_text)

    # P1：保证「仅底座 system + user」能塞进总预算（绝境才截 user）
    sys_probe = ChatMessage(role="system", content=base)
    user_probe = ChatMessage(role="user", content=user_text)
    if c.message_tokens(sys_probe) + c.message_tokens(user_probe) > T:
        user_cap = max(
            32,
            T - c.message_tokens(sys_probe) - _message_overhead(c, "user"),
        )
        user_text, u_trunc = _truncate_content_to_token_budget(user_text, user_cap, c)
        if u_trunc:
            report.user_truncated = True
        user_msg = ChatMessage(role="user", content=user_text)

    old_msgs, recent_msgs = _split_old_and_recent(list(req.history), settings.recent_exchange_rounds)
    retrieval = (req.current_retrieval_text or "").strip()
    tool_out = (req.current_tool_output_text or "").strip()
    summary_block = ""

    tried_summary = False
    guard = 0

    while guard < 512:
        guard += 1
        system_body = _build_system_body(
            base,
            earlier_summary=summary_block,
            current_retrieval=retrieval,
            current_tool=tool_out,
        )
        tok = _messages_tokens(system_body, old_msgs, recent_msgs, user_msg, c)
        if tok <= T:
            break

        if old_msgs and settings.enable_history_summary and summarizer is not None and not tried_summary:
            blob = _history_to_text(old_msgs)
            summary_block = await summarizer(blob, settings.summary_output_max_tokens)
            old_msgs = []
            tried_summary = True
            report.history_summary_used = True
            continue

        if old_msgs:
            old_msgs = old_msgs[1:]
            report.old_messages_removed += 1
            continue

        if summary_block.strip():
            cap = max(64, int(settings.summary_output_max_tokens * (0.85 ** min(10, guard // 3))))
            new_s, _ = _truncate_content_to_token_budget(summary_block, cap, c)
            if new_s == summary_block:
                summary_block = ""
            else:
                summary_block = new_s
            continue

        if tool_out:
            new_t, _ = _truncate_content_to_token_budget(
                tool_out,
                max(32, int(c.content_tokens(tool_out) * 0.82)),
                c,
            )
            if new_t == tool_out or not new_t:
                tool_out = ""
            else:
                tool_out = new_t
            report.current_tool_output_truncated = True
            continue

        if retrieval:
            new_r, _ = _truncate_content_to_token_budget(
                retrieval,
                max(64, int(c.content_tokens(retrieval) * 0.82)),
                c,
            )
            if new_r == retrieval or not new_r:
                retrieval = ""
            else:
                retrieval = new_r
            report.current_retrieval_truncated = True
            continue

        if recent_msgs:
            recent_msgs = recent_msgs[1:]
            report.recent_messages_removed += 1
            continue

        prev_u = user_msg.content
        ut, u_trunc = _truncate_content_to_token_budget(
            user_msg.content,
            max(1, int(c.content_tokens(user_msg.content) * 0.82)),
            c,
        )
        if ut == prev_u:
            prev_b = base
            nb, s_trunc = _truncate_content_to_token_budget(
                base,
                max(1, int(c.content_tokens(base) * 0.82)),
                c,
            )
            if nb == prev_b or not nb.strip():
                break
            base = nb
            report.system_truncated = True
            continue

        user_msg = ChatMessage(role="user", content=ut)
        if u_trunc or ut != user_text:
            report.user_truncated = True
        if not ut.strip():
            break
        continue

    system_body = _build_system_body(
        base,
        earlier_summary=summary_block,
        current_retrieval=retrieval,
        current_tool=tool_out,
    )
    messages = [
        ChatMessage(role="system", content=system_body),
        *old_msgs,
        *recent_msgs,
        user_msg,
    ]
    report.approx_input_tokens = c.messages_tokens(messages)
    return ContextAssemblyResult(messages=messages, report=report)
