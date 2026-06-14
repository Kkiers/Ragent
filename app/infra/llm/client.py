import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncGenerator, List, MutableMapping, Optional, Dict, Tuple

from app.context_window import assemble_context_window
from app.domain.context import ContextAssemblyRequest, ContextAssemblyResult
from app.domain.schemas import ChatMessage, RetrievedDoc
from app.infra.llm.config import LLMSettings, load_llm_settings
from app.infra.llm.factory import create_llm_provider
from app.infra.llm.stage_config import StageLLMOverride, apply_override, load_stage_llm_overrides
from app.infra.llm.prompts import (
    CHAT_SYSTEM_PROMPT,
    HISTORY_SUMMARY_SYSTEM_PROMPT,
    RAG_SYSTEM_PROMPT,
)


"""
业务层依赖的唯一门面
"""

_log = logging.getLogger(__name__)


def _fill_context_window_debug(
    context_debug: MutableMapping[str, object] | None,
    assembled: ContextAssemblyResult,
) -> None:
    if context_debug is None:
        return
    context_debug.update(assembled.report.model_dump(mode="json"))
    context_debug["messages"] = [m.model_dump(mode="json") for m in assembled.messages]


@dataclass
class LLMClient:
    settings: LLMSettings
    provider: object
    stage_overrides: Dict[str, StageLLMOverride] | None = None
    _provider_cache: Dict[Tuple[str, str, float, int, int, int], object] | None = None

    @classmethod
    def create(cls, settings:LLMSettings | None = None) -> "LLMClient":
        settings = settings or load_llm_settings()
        provider = create_llm_provider(settings)  #根据配置选择 provider（比如 deepseek / openai）

        # stage 配置文件（不走环境变量）：默认读取 config/llm_stages.json
        project_root = Path(__file__).resolve().parents[3]  # .../Ragent
        config_path = project_root / "config" / "llm_stages.json"
        stage_overrides = load_stage_llm_overrides(config_path)

        key = (
            settings.provider.lower().strip(),
            settings.model,
            float(settings.temperature),
            int(settings.timeout),
            int(settings.max_retries),
            int(settings.max_tokens),
        )
        client = LLMClient(
            settings=settings,
            provider=provider,
            stage_overrides=stage_overrides,
            _provider_cache={key: provider},
        )
        _log.info(
            "LLM 已初始化: provider=%s model=%s (进程环境 LLM_PROVIDER=%s, DeepSeek Key=%s)",
            settings.provider,
            settings.model,
            repr(os.environ.get("LLM_PROVIDER")),
            "已配置" if (settings.deepseek_api_key or "").strip() else "未配置",
        )
        return client

    def _settings_for_stage(self, stage: Optional[str]) -> LLMSettings:
        if not stage:
            return self.settings
        ovs = self.stage_overrides or {}
        ov = ovs.get(stage) or ovs.get(stage.lower())
        if not ov:
            return self.settings
        return apply_override(self.settings, ov)

    def model_info_for_stage(self, stage: Optional[str]) -> tuple[str, str]:
        """
        用于审计/可观测：返回 (provider, model_name)。
        stage 为空时返回默认 settings。
        """
        s = self._settings_for_stage(stage)
        return (str(s.provider or "").strip(), str(s.model or "").strip())

    def _provider_cache_key(self, s: LLMSettings) -> Tuple[str, str, float, int, int, int]:
        return (
            s.provider.lower().strip(),
            s.model,
            float(s.temperature),
            int(s.timeout),
            int(s.max_retries),
            int(s.max_tokens),
        )

    def _get_provider_for_settings(self, s: LLMSettings) -> object:
        if self._provider_cache is None:
            self._provider_cache = {}
        key = self._provider_cache_key(s)
        hit = self._provider_cache.get(key)
        if hit is not None:
            return hit
        p2 = create_llm_provider(s)
        self._provider_cache[key] = p2
        return p2

    async def chat(self, messages: List[ChatMessage], *, stage: Optional[str] = None) -> str:
        s = self._settings_for_stage(stage)
        provider = self._get_provider_for_settings(s)
        return await provider.chat(messages)

    async def stream_chat(self, messages: List[ChatMessage], *, stage: Optional[str] = None) -> AsyncGenerator[str, None]:
        s = self._settings_for_stage(stage)
        provider = self._get_provider_for_settings(s)
        async for chunk in provider.stream_chat(messages):
            yield chunk

    async def _summarize_for_context_window(self, conversation_text: str, max_out_tokens: int) -> str:
        """更早对话压缩，供上下文窗口层使用（宜短）。"""
        blob = (conversation_text or "").strip()
        if not blob:
            return ""
        from app.context_window.assembler import _truncate_content_to_token_budget
        from app.context_window.token_counter import default_counter

        counter = default_counter()
        system = HISTORY_SUMMARY_SYSTEM_PROMPT.format(max_tokens=max_out_tokens)
        blob_cap, _ = _truncate_content_to_token_budget(blob, max(256, max_out_tokens * 6), counter)
        msgs = [
            ChatMessage(role="system", content=system),
            ChatMessage(role="user", content=blob_cap),
        ]
        out = await self.chat(msgs, stage="summary")
        out_fit, _ = _truncate_content_to_token_budget(out, max_out_tokens, counter)
        return out_fit

    """ RAG问答专用client"""
    async def generate_answer(
        self,
        query: str,                      # 用户问题（字符串）
        context: str,                    # 检索到的上下文（字符串）
        history: List[ChatMessage],      # 历史对话（列表，每个是 ChatMessage）
        *,
        context_debug: MutableMapping[str, object] | None = None,
    ) -> str:                           # 返回值是字符串

        assembled = await assemble_context_window(
            ContextAssemblyRequest(
                system_prompt=RAG_SYSTEM_PROMPT.strip(),
                user_query=query,
                history=list(history),
                current_retrieval_text=context,
            ),
            summarizer=self._summarize_for_context_window,
        )
        messages = assembled.messages
        _fill_context_window_debug(context_debug, assembled)

        # 第二步：调用 provider 的 chat 方法
        result: str = await self.chat(messages, stage="rag")
        # ↑ provider.chat 会调用真正的模型（DeepSeek / OpenAI）
        # ↑ await 表示这是一个异步调用，需要等待结果

        # 第三步：返回结果
        return result

    """普通聊天专用client"""
    async def generate_chat(
        self,
        query: str,                      # 用户输入
        history: List[ChatMessage],      # 历史消息
        *,
        context_debug: MutableMapping[str, object] | None = None,
    ) -> str:                           # 返回字符串

        assembled = await assemble_context_window(
            ContextAssemblyRequest(
                system_prompt=CHAT_SYSTEM_PROMPT.strip(),
                user_query=query,
                history=list(history),
            ),
            summarizer=self._summarize_for_context_window,
        )
        messages = assembled.messages
        _fill_context_window_debug(context_debug, assembled)

        # 第七步：调用模型
        result: str = await self.chat(messages, stage="chat")

        # 第八步：返回结果
        return result

    """ 流式输出 专用client"""
    async def stream_answer(
            self,
            query: str,                      # 用户问题
            context: str,                    # 上下文
            history: List[ChatMessage],      # 历史
            *,
            context_debug: MutableMapping[str, object] | None = None,
            **_: object,
        ) -> AsyncGenerator[str, None]:     # 返回“异步生成器”（一段一段输出）；接受多余参数以兼容旧调用

            assembled = await assemble_context_window(
                ContextAssemblyRequest(
                    system_prompt=RAG_SYSTEM_PROMPT.strip(),
                    user_query=query,
                    history=list(history),
                    current_retrieval_text=context,
                ),
                summarizer=self._summarize_for_context_window,
            )
            messages = assembled.messages
            _fill_context_window_debug(context_debug, assembled)

            # 第二步：调用流式接口
            async for chunk in self.stream_chat(messages, stage="rag"):
                # ↑ 每次返回一小段字符串 chunk

                yield chunk




    async def stream_text(
        self,
        text: str,
        *,
        words_per_chunk: int = 6,
    ) -> AsyncGenerator[str, None]:
        """将整段文本按固定块大小流式吐出"""
        s = (text or "").strip()
        if not s:
            return
        parts = s.split()
        if len(parts) > 1 or (parts and " " in s):
            buf: List[str] = []
            for w in parts:
                buf.append(w)
                if len(buf) >= max(1, words_per_chunk):
                    yield " ".join(buf) + " "
                    buf = []
            if buf:
                yield " ".join(buf)
            return
        step = max(8, words_per_chunk * 4)
        for i in range(0, len(s), step):
            yield s[i : i + step]

    async def rerank(self, query: str, docs: List[RetrievedDoc]) -> List[RetrievedDoc]:
        """检索结果重排；未接专用 rerank 模型时原样返回。"""
        return list(docs)

    def assemble_context(self, docs: List[RetrievedDoc]) -> str:
        """将检索文档拼成上下文文本。"""
        parts = [d.content for d in docs if d.content]
        return "\n\n".join(parts)


def create_llm_client():
    return LLMClient.create() # 实际上是调用了类里面的那个 create