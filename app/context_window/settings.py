from __future__ import annotations

from app.domain.context import ContextWindowSettings


def default_context_window_settings() -> ContextWindowSettings:
    """默认窗口参数；后续可从 LLMSettings 或环境变量注入。"""
    return ContextWindowSettings()
