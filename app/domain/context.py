from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.schemas import ChatMessage


class ContextWindowSettings(BaseModel):
    """单一硬约束 + 可调参数"""

    max_total_tokens: int = 12_000
    recent_exchange_rounds: int = Field(
        default=3,
        ge=1,
        description="保留最近若干「轮」的原始对话；一轮按 user+assistant 两条计，即最多保留 2*rounds 条消息。",
    )
    summary_output_max_tokens: int = Field(default=800, ge=64, description="更早历史摘要的最大 token（估算）。")
    enable_history_summary: bool = Field(default=True, description="更早历史超窗时是否调用摘要；关闭则直接丢弃最旧消息。")


class TruncationReport(BaseModel):
    approx_input_tokens: int = 0
    user_truncated: bool = False
    current_retrieval_truncated: bool = False
    current_tool_output_truncated: bool = False
    system_truncated: bool = False
    history_summary_used: bool = False
    old_messages_removed: int = 0
    recent_messages_removed: int = 0


class ContextAssemblyRequest(BaseModel):
    """按信息类型注水；与当前走 RAG/闲聊/工具无关，由调用方填入本轮有哪些材料。"""

    system_prompt: str = Field(..., description="底座 system，不可挪到 user 之后。")
    user_query: str = ""
    history: list[ChatMessage] = Field(default_factory=list)
    current_retrieval_text: str | None = Field(default=None, description="本轮检索正文，P2，权重高。")
    current_tool_output_text: str | None = Field(default=None, description="本轮工具输出，P2；往轮工具未结构化进库时可留空。")
    settings: ContextWindowSettings | None = None


class ContextAssemblyResult(BaseModel):
    messages: list[ChatMessage]
    report: TruncationReport
