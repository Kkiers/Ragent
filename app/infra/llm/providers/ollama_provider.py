import logging
from typing import AsyncGenerator, List

from langchain_ollama import ChatOllama

from app.domain.schemas import ChatMessage
from app.framework.exceptions import AppError
from app.infra.llm.config import LLMSettings
from app.infra.llm.providers.base import BaseLLMProvider, to_langchain_messages

logger = logging.getLogger(__name__)


class OllamaProvider(BaseLLMProvider):
    def __init__(self, settings: LLMSettings):
        self.settings = settings
        self.client = ChatOllama(
            model=settings.model,
            base_url=settings.ollama_base_url,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            timeout=settings.timeout,
            max_retries=settings.max_retries,
            streaming=True,
        ) 

    async def chat(self, messages: List[ChatMessage]) -> str:
        lc_messages = to_langchain_messages(messages)
        try:
            resp = await self.client.ainvoke(lc_messages)
            return resp.content
        except AppError:
            raise
        except Exception as e:
            logger.exception("Ollama ainvoke 失败")
            msg = str(e).strip() or type(e).__name__
            raise AppError(
                code="OLLAMA_CHAT_FAILED",
                message=f"Ollama 调用失败: {msg[:400]}",
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
            logger.exception("Ollama astream 失败")
            msg = str(e).strip() or type(e).__name__
            raise AppError(
                code="OLLAMA_STREAM_FAILED",
                message=f"Ollama 流式调用失败: {msg[:400]}",
                status_code=502,
                details={"type": type(e).__name__},
            ) from e