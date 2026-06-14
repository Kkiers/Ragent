from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from app.infra.llm.config import LLMSettings


@dataclass(frozen=True)
class StageLLMOverride:
    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    timeout: Optional[int] = None
    max_retries: Optional[int] = None
    max_tokens: Optional[int] = None


def _as_override(obj: object) -> StageLLMOverride:
    if not isinstance(obj, dict):
        return StageLLMOverride()
    d: Dict[str, Any] = obj
    return StageLLMOverride(
        provider=(str(d.get("provider")).strip() if d.get("provider") is not None else None) or None,
        model=(str(d.get("model")).strip() if d.get("model") is not None else None) or None,
        temperature=(float(d["temperature"]) if "temperature" in d and d["temperature"] is not None else None),
        timeout=(int(d["timeout"]) if "timeout" in d and d["timeout"] is not None else None),
        max_retries=(int(d["max_retries"]) if "max_retries" in d and d["max_retries"] is not None else None),
        max_tokens=(int(d["max_tokens"]) if "max_tokens" in d and d["max_tokens"] is not None else None),
    )


def load_stage_llm_overrides(path: Path) -> dict[str, StageLLMOverride]:
    """
    读取一个 JSON 配置文件，返回 {stage -> override}。

    文件不存在时返回空 dict（不报错）。
    """
    if not path.is_file():
        return {}
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return {}
    data = json.loads(raw)
    stages = data.get("stages", {}) if isinstance(data, dict) else {}
    if not isinstance(stages, dict):
        return {}
    return {str(k): _as_override(v) for k, v in stages.items()}


def apply_override(base: LLMSettings, ov: StageLLMOverride) -> LLMSettings:
    update: Dict[str, Any] = {}
    if ov.provider is not None:
        update["provider"] = ov.provider
    if ov.model is not None:
        update["model"] = ov.model
    if ov.temperature is not None:
        update["temperature"] = ov.temperature
    if ov.timeout is not None:
        update["timeout"] = ov.timeout
    if ov.max_retries is not None:
        update["max_retries"] = ov.max_retries
    if ov.max_tokens is not None:
        update["max_tokens"] = ov.max_tokens
    return base.model_copy(update=update) if update else base

