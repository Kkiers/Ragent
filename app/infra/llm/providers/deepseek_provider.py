import logging
import os
from typing import AsyncGenerator, List, Optional

from langchain_deepseek import ChatDeepSeek

from app.domain.schemas import ChatMessage
from app.framework.exceptions import AppError
from app.infra.llm.config import LLMSettings
from app.infra.llm.providers.base import BaseLLMProvider, to_langchain_messages

logger = logging.getLogger(__name__)


class DeepSeekProvider(BaseLLMProvider):
    """
    如果调用deepseek_provider：
    1. 把 业务用的 ChatMessage 转成 LangChain 消息。
    2. 通过langchain封装的接口调用模型

    3. 重写业务上层定义好的接口，把 LangChain 返回的结果，再统一成 str 或流式文本。
    - chat：返回完整字符串
    - stream_chat：流式返回增量文本
    """
    def __init__(self, settings: LLMSettings):
        self.settings = settings
        # 懒创建：避免未配置 DEEPSEEK_API_KEY 时连 FastAPI 进程都起不来
        self._client: Optional[ChatDeepSeek] = None

    def _get_client(self) -> ChatDeepSeek:
        if self._client is None:
            api_key = (self.settings.deepseek_api_key or os.getenv("DEEPSEEK_API_KEY") or "").strip()
            if not api_key:
                raise AppError(
                    code="DEEPSEEK_API_KEY_MISSING",
                    message="未配置 DEEPSEEK_API_KEY：请在环境变量或项目根 .env 中设置后再调用模型。",
                    status_code=503,
                    details={
                        "hint": "变量名须为 DEEPSEEK_API_KEY；建议放在项目根 .env（本项目只保留一个 .env）。修改后需重启 uvicorn。"
                    },
                )
            self._client = ChatDeepSeek(
                model=self.settings.model,
                api_key=api_key,
                base_url=self.settings.deepseek_base_url,
                temperature=self.settings.temperature,
                max_tokens=self.settings.max_tokens,
                timeout=self.settings.timeout,
                max_retries=self.settings.max_retries,
                streaming=False,
            )
        return self._client

    async def chat(self, messages: List[ChatMessage]) -> str:
        lc_messages = to_langchain_messages(messages)
        try:
            resp = await self._get_client().ainvoke(lc_messages)
            return resp.content
        except AppError:
            raise
        except Exception as e:
            logger.exception("DeepSeek ainvoke 失败")
            msg = str(e).strip() or type(e).__name__
            raise AppError(
                code="DEEPSEEK_CHAT_FAILED",
                message=f"DeepSeek 调用失败: {msg[:400]}",
                status_code=502,
                details={"type": type(e).__name__},
            ) from e

    async def stream_chat(self, messages: List[ChatMessage]) -> AsyncGenerator[str, None]:
        lc_messages = to_langchain_messages(messages)
        try:
            async for chunk in self._get_client().astream(lc_messages):
                if getattr(chunk, "content", None):
                    yield chunk.content
        except AppError:
            raise
        except Exception as e:
            logger.exception("DeepSeek astream 失败")
            msg = str(e).strip() or type(e).__name__
            raise AppError(
                code="DEEPSEEK_STREAM_FAILED",
                message=f"DeepSeek 流式调用失败: {msg[:400]}",
                status_code=502,
                details={"type": type(e).__name__},
            ) from e
