"""
意图识别（语义理解）
同一句话不一定都走 RAG。
有些问题是闲聊，有些要澄清，有些要调工具。
所以先分流，再执行。
"""
import json
import os
import time
from typing import Protocol, Optional
from app.domain.enums import IntentType
from app.domain.schemas import ChatMessage, IntentResult
from app.framework.context import RequestContext
from app.framework.exceptions import AppError
from app.infra.llm.client import LLMClient
from app.infra.observability.audit_sqlite import emit_event
from app.infra.llm.prompts import INTENT_SYSTEM_PROMPT

class IntentServiceProtocol(Protocol):
    """意图识别服务必须要有以下方法"""

    # 输入当前问题、对话历史、上下文信息，输出Result规定的标准格式
    async def identify_intent(self, query: str, history: list[ChatMessage], ctx: RequestContext) -> IntentResult: 
        ...

class IntentService:
    async def identify_intent(self, query: str, history: list[ChatMessage], ctx: RequestContext) -> IntentResult:
        # 兜底策略（按你的要求）：
        # - 不做关键词规则
        # - 当 LLM 意图识别失败/低分时，统一走 AGENT（即 Tool 分支）
        return IntentResult(
            intent=IntentType.AGENT,
            score=0.0,
            reason="LLM 意图识别不可用/不可信时的兜底：统一走 AGENT（Tool）分支",
        )


def _extract_json_object(text: str) -> Optional[str]:
    """
    尝试从模型输出里截取第一个 JSON 对象片段。
    兼容模型偶尔带解释文字或代码块围栏的情况。
    """
    s = (text or "").strip()
    if not s:
        return None
    # 去掉 ```json / ``` 围栏
    if s.startswith("```"):
        lines = [ln for ln in s.splitlines() if not ln.strip().startswith("```")]
        s = "\n".join(lines).strip()
    start = s.find("{")
    end = s.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    return s[start : end + 1]


class LLMIntentService:
    """
    用大模型做“语义意图识别”：
    - 输出严格 JSON（IntentResult 的字段子集）
    - 解析失败/低置信度时回退到规则版
    """

    def __init__(
        self,
        llm_client: LLMClient,
        *,
        fallback: Optional[IntentServiceProtocol] = None,
        min_score: float = 0.55,
        max_history_turns: int = 8,
    ) -> None:
        self.llm_client = llm_client
        self.fallback = fallback or IntentService()
        self.min_score = float(min_score)
        self.max_history_turns = int(max_history_turns)

    async def identify_intent(self, query: str, history: list[ChatMessage], ctx: RequestContext) -> IntentResult:
        hist = list(history or [])[-max(0, self.max_history_turns) :]
        history_text = "\n".join([f"{m.role}: {m.content}" for m in hist]).strip()

        system = INTENT_SYSTEM_PROMPT.strip()

        user = (
            f"当前用户问题：{(query or '').strip()}\n"
            f"对话历史（可能为空）：\n{history_text if history_text else '(empty)'}\n"
        )

        provider_name, model_name = self.llm_client.model_info_for_stage("intent")
        t0 = time.perf_counter()
    
        try:
            await emit_event(
                "intent_llm_started",
                status="ok",
                intent=None,
                model_provider=provider_name,
                model_name=model_name,
                fields={
                    "history_turns": len(hist),
                    "query_len": len((query or "").strip()),
                    "max_history_turns": self.max_history_turns,
                    "min_score": self.min_score,
                },
            )
            # 调用 LLM 模型，获取意图识别结果
            out = await self.llm_client.chat(
                [
                    ChatMessage(role="system", content=system),
                    ChatMessage(role="user", content=user),
                ],
                stage="intent",
            )
            # 尝试从模型输出里截取第一个 JSON 对象片段。 
            # 兼容模型偶尔带解释文字或代码块围栏的情况。
            blob = _extract_json_object(out)
            # 如果LLM输出没有JSON，则抛出异常
            if not blob:
                raise ValueError(f"LLM 输出无 JSON: {out!r}")
            data = json.loads(blob)
            # 解析 JSON 对象，获取意图、置信度和原因
            intent_raw = str(data.get("intent", "")).strip().upper()
            if intent_raw not in {t.value for t in IntentType}:
                raise ValueError(f"未知 intent={intent_raw!r}")
            score = float(data.get("score", 0.0) or 0.0)
            reason = str(data.get("reason", "") or "").strip()

            result = IntentResult(
                intent=IntentType(intent_raw),
                score=max(0.0, min(1.0, score)),
                reason=reason,
            )

            fallback_used = False
            if result.score < self.min_score:
                fallback_used = True
                fb = await self.fallback.identify_intent(query, history, ctx)
                dt_ms = int((time.perf_counter() - t0) * 1000)
                await emit_event(
                    "intent_llm_finished",
                    status="fallback",
                    intent=fb.intent.value,
                    model_provider=provider_name,
                    model_name=model_name,
                    payload=out,
                    fields={
                        "duration_ms": dt_ms,
                        "parsed_intent": result.intent.value,
                        "parsed_score": result.score,
                        "parsed_reason": result.reason,
                        "min_score": self.min_score,
                        "fallback_used": fallback_used,
                        "fallback_intent": fb.intent.value,
                        "fallback_score": fb.score,
                        "fallback_reason": fb.reason,
                    },
                )
                return fb

            dt_ms = int((time.perf_counter() - t0) * 1000)
            await emit_event(
                "intent_llm_finished",
                status="ok",
                intent=result.intent.value,
                model_provider=provider_name,
                model_name=model_name,
                payload=out,
                fields={
                    "duration_ms": dt_ms,
                    "score": result.score,
                    "reason": result.reason,
                    "fallback_used": fallback_used,
                },
            )
            return result
        except Exception:
            # 任何异常都回退到规则，确保不影响主链路可用性
            fb = await self.fallback.identify_intent(query, history, ctx)
            dt_ms = int((time.perf_counter() - t0) * 1000)
            await emit_event(
                "intent_llm_finished",
                status="error",
                intent=fb.intent.value,
                model_provider=provider_name,
                model_name=model_name,
                fields={
                    "duration_ms": dt_ms,
                    "fallback_used": True,
                    "fallback_intent": fb.intent.value,
                    "fallback_score": fb.score,
                    "fallback_reason": fb.reason,
                },
            )
            return fb


# 统一创建入口
def create_intent_service(llm_client: Optional[LLMClient] = None) -> IntentServiceProtocol:
    mode_raw = os.getenv("RAGENT_INTENT_MODE")
    if mode_raw is None or not str(mode_raw).strip():
        raise AppError(
            code="INTENT_MODE_NOT_CONFIGURED",
            message="未配置 RAGENT_INTENT_MODE：本项目要求显式开启大模型意图识别（例如 RAGENT_INTENT_MODE=llm）。",
            status_code=503,
            details={"hint": "在项目根 .env 或环境变量中设置 RAGENT_INTENT_MODE=llm，并确保 LLM Key 已配置。"},
        )

    mode = str(mode_raw).strip().lower()
    if mode not in {"llm", "model"}:
        raise AppError(
            code="INTENT_MODE_UNSUPPORTED",
            message=f"不支持的 RAGENT_INTENT_MODE={mode_raw!r}：仅支持 'llm'。",
            status_code=503,
        )
    if llm_client is None:
        raise AppError(
            code="INTENT_LLM_CLIENT_MISSING",
            message="意图识别已配置为 llm，但未传入 llm_client。",
            status_code=503,
        )

    min_score = float(os.getenv("RAGENT_INTENT_MIN_SCORE", "0.55") or 0.55)
    max_turns = int(os.getenv("RAGENT_INTENT_MAX_HISTORY_TURNS", "8") or 8)
    return LLMIntentService(
        llm_client=llm_client,
        fallback=IntentService(),  # 兜底：统一 AGENT（Tool）
        min_score=min_score,
        max_history_turns=max_turns,
    )

"""
后续意图识别迭代可以用llm

def create_intent_service():
    return LLMIntentService()

"""
