from __future__ import annotations

from app.domain.schemas import ChatMessage


class ApproxTokenCounter:
    """
    近似 token：中英混排保守估计（偏大一点，留出模型侧余量）。
    每条消息额外加少量 overhead，模拟 chat template 开销。
    """

    def __init__(self, *, chars_per_token: float = 1.8, per_message_overhead: int = 4) -> None:
        self._chars_per_token = max(0.5, float(chars_per_token))
        self._per_message_overhead = max(0, int(per_message_overhead))

    def content_tokens(self, text: str) -> int:
        s = text or ""
        if not s:
            return 0
        return max(1, int(len(s) / self._chars_per_token))

    def message_tokens(self, msg: ChatMessage) -> int:
        return self.content_tokens(msg.content) + self._per_message_overhead

    def messages_tokens(self, messages: list[ChatMessage]) -> int:
        return sum(self.message_tokens(m) for m in messages)


def default_counter() -> ApproxTokenCounter:
    return ApproxTokenCounter()
