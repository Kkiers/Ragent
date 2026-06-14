"""
统一消息格式
转成 LangChain 的消息类型
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, List

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from app.domain.schemas import ChatMessage

def to_langchain_messages(messages: List[ChatMessage]) -> list[BaseMessage]:
    """
    把自己定义的 ChatMessage 转成 LangChain 的消息对象。
    这是“数据格式适配”层，不属于业务逻辑。
    """
    result: list[BaseMessage] = []

    for msg in messages:
        if msg.role == "system":
            result.append(SystemMessage(content=msg.content))
        elif msg.role == "user":
            result.append(HumanMessage(content=msg.content))
        else:
            result.append(AIMessage(content=msg.content))

    return result


class BaseLLMProvider(ABC):
    """
    所有模型供应商都要遵守的统一接口。
    业务层只认这两个方法：
    - chat：返回完整字符串
    - stream_chat：流式返回增量文本
    """

    @abstractmethod
    async def chat(self, messages: List[ChatMessage]) -> str:
        raise NotImplementedError

    @abstractmethod
    async def stream_chat(self, messages: List[ChatMessage]) -> AsyncGenerator[str, None]:
        raise NotImplementedError