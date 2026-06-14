from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from app.infra.tools.tool_base import ToolSpec

"""
要求模型输出的 JSON 的“目标形状”。
把模型输出解析成 ToolCall，并做校验
"""

@dataclass
class ToolCall:
    tool_name: str
    arguments: dict[str, Any]
    reason: str | None = None


def extract_first_json_object(text: str) -> str | None:
    """
    从模型输出中提取第一个 JSON 对象（最小实现：取最外层 { ... }）。
    """
    s = (text or "").strip()
    if not s:
        return None
    start = s.find("{")
    end = s.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    return s[start : end + 1]

# 模型输出的校验：提取 JSON 对象、转换为 ToolCall 对象
def parse_tool_call(text: str) -> ToolCall | None:
    json_text = extract_first_json_object(text)
    if not json_text:
        return None
    try:
        payload = json.loads(json_text)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None

    tool_name = payload.get("tool_name")
    arguments = payload.get("arguments")
    reason = payload.get("reason")

    if not isinstance(tool_name, str) or not tool_name.strip():
        return None
    if not isinstance(arguments, dict):
        return None

    return ToolCall(tool_name=tool_name.strip(), arguments=arguments, reason=reason if isinstance(reason, str) else None)


def _is_number(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _matches_schema(value: Any, schema: dict[str, Any]) -> bool:
    """
    极简 schema 校验（第一版够用）：
    - type: object/string/number/integer/boolean/array
    - properties: 对 object 子字段做类型检查
    """
    t = (schema or {}).get("type")
    if not t:
        return True

    if t == "object":
        if not isinstance(value, dict):
            return False
        props = (schema or {}).get("properties") or {}
        if isinstance(props, dict):
            for k, sub_schema in props.items():
                if k in value and value[k] is not None and isinstance(sub_schema, dict):
                    if not _matches_schema(value[k], sub_schema):
                        return False
        return True

    if t == "string":
        return isinstance(value, str)
    if t == "number":
        return _is_number(value)
    if t == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if t == "boolean":
        return isinstance(value, bool)
    if t == "array":
        return isinstance(value, list)

    return True


def validate_tool_call(tool_call: ToolCall, tool_specs: list[ToolSpec]) -> tuple[bool, str]:
    """
    校验：
    1) tool_name 必须存在于工具列表
    2) arguments 必填字段存在（允许为 null，用于触发澄清）
    3) 类型做粗校验
    """
    specs_by_name = {s.name: s for s in tool_specs}
    spec = specs_by_name.get(tool_call.tool_name)
    if not spec:
        return False, f"unknown tool_name: {tool_call.tool_name}"

    schema = spec.input_schema or {}
    required = schema.get("required") or []
    if isinstance(required, list):
        for k in required:
            if isinstance(k, str) and k not in tool_call.arguments:
                return False, f"missing required argument: {k}"

    if not _matches_schema(tool_call.arguments, schema):
        return False, "arguments do not match input_schema"

    return True, "ok"
