import logging
from typing import AsyncGenerator, List

from langchain_openai import ChatOpenAI

from app.domain.schemas import ChatMessage
from app.framework.exceptions import AppError
from app.infra.llm.config import LLMSettings
from app.infra.llm.providers.base import BaseLLMProvider, to_langchain_messages

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """
    如果调用openai_provider：
    1. 把 业务用的 ChatMessage 转成 LangChain 消息。
    2. 通过langchain封装的接口调用模型

    3. 重写业务上层定义好的接口，把 LangChain 返回的结果，再统一成 str 或流式文本。
    - chat：返回完整字符串
    - stream_chat：流式返回增量文本
    """

    def __init__(self, settings: LLMSettings):
        self.settings = settings
        self.client = ChatOpenAI(
            model=settings.model,
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            temperature=settings.temperature,
            timeout=settings.timeout,
            max_retries=settings.max_retries,
        )

    async def chat(self, messages: List[ChatMessage]) -> str:
        lc_messages = to_langchain_messages(messages)
        try:
            resp = await self.client.ainvoke(lc_messages)
            return resp.content
        except AppError:
            raise
        except Exception as e:
            logger.exception("OpenAI ainvoke 失败")
            msg = str(e).strip() or type(e).__name__
            raise AppError(
                code="OPENAI_CHAT_FAILED",
                message=f"OpenAI 调用失败: {msg[:400]}",
                status_code=502,
                details={"type": type(e).__name__},
            ) from e

    async def stream_chat(self, messages: List[ChatMessage]) -> AsyncGenerator[str, None]:
        lc_messages = to_langchain_messages(messages)
        try:
            async for chunk in self.client.astream(lc_messages):
                if getattr(chunk, "content", None):
                    yield chunk.content
        except AppError:
            raise
        except Exception as e:
            logger.exception("OpenAI astream 失败")
            msg = str(e).strip() or type(e).__name__
            raise AppError(
                code="OPENAI_STREAM_FAILED",
                message=f"OpenAI 流式调用失败: {msg[:400]}",
                status_code=502,
                details={"type": type(e).__name__},
            ) from e