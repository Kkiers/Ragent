# query 规整
# 统一规则：只保留一次 rewriting（仅在 RAG 分支触发）

from typing import Protocol
from app.domain.schemas import ChatMessage
from app.core.cleaner import light_clean
from app.framework.context import RequestContext #还没写，留个坑，要装用户id，请求id，一些上下文信息 
from app.infra.llm.client import LLMClient
from app.infra.llm.prompts import REWRITE_SYSTEM_PROMPT

class QueryServiceProtocol(Protocol):
    """任何 QueryService 都必须有这些方法"""
    async def rewrite(self, query: str, history: list[ChatMessage], ctx: RequestContext) -> str:
        """一次 query rewriting：标准化/补全/拆分（输出适合检索的 query）"""
        ...

class QueryService:
    """真正实现"""
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def rewrite(self, query: str, history: list[ChatMessage], ctx: RequestContext) -> str:
        base = light_clean(query)
        hist = list(history or [])[-8:]
        history_text = "\n".join([f"{m.role}: {m.content}" for m in hist]).strip()
        system = ChatMessage(role="system", content=REWRITE_SYSTEM_PROMPT.strip())
        user = ChatMessage(
            role="user",
            content=(
                "请把用户问题改写成更适合检索知识库的一句话查询（必要时消解指代、补全省略）。\n"
                "要求：只输出改写后的 query 文本，不要输出解释，不要 Markdown。\n\n"
                f"用户当前问题：{(base or '').strip()}\n\n"
                f"对话历史（可能为空，仅供消解指代）：\n{history_text if history_text else '(empty)'}\n"
            ),
        )
        out = await self.llm_client.chat([system, user], stage="rewrite")
        rewritten = light_clean(out)
        return rewritten or base

# 工厂函数

def create_query_service(llm_client: LLMClient):
    return QueryService(llm_client=llm_client)

# test
# def test_query_service():
#     service = create_query_service()
#     raw_query = "  你好，世界！  "
#     normalized = service.light_normalize(raw_query)
#     assert normalized == "你好,世界!"
#     print("light_normalize passed.")

#     # heavy_rewrite 默认直接返回原query
#     class DummyRequestContext:
#         pass

#     ctx = DummyRequestContext()
#     history = []
#     rewritten = service.heavy_rewrite(raw_query, history, ctx)
#     assert rewritten == raw_query
#     print("heavy_rewrite passed.")

# if __name__ == "__main__":
#     test_query_service()