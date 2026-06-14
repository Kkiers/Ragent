from pydantic import BaseModel, Field
from app.domain.enums import IntentType
from typing import Any, Literal, Optional

# 聊天消息规范 角色、内容
class ChatMessage(BaseModel): 
    role: Literal["user", "assistant", "system"]
    content: str

# 聊天请求规范 意图类型、消息列表、上下文
class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None # 会话ID可以没有
    history: list[ChatMessage] = Field(default_factory=list) # 历史消息 默认空列表 每次创建新列表 
    top_k: int = 5
    stream: bool = False
    debug: bool = False  # True 时在 meta 中返回检索、上下文等（仅调试用）

# 意图识别结果
class IntentResult(BaseModel):
    intent: IntentType  # 仅三类：RAG / CHAT / AGENT
    score: float = 0.5  # 置信度 0-1
    reason: str = ""  # 为什么判定为该意图（用于调试/可解释性）

# 检索出来的文档
class RetrievedDoc(BaseModel):
    doc_id: str # 文档ID
    content: str # 文档内容
    score: float = 0.0 # 相似度得分 0-1 默认0.0

#query处理结果
class QueryNormalizationResult(BaseModel):
    query: str
    did_rewrite: bool = False  # 是否进行了 rewriting

# 聊天响应 最终返回给用户的数据
class ChatResponse(BaseModel):
    intent: IntentType # 意图类型
    answer: Optional[str] = None # 回答 可选
    clarify_question: Optional[str] = None # 澄清问题 可选
    sources: list[str] = Field(default_factory=list) # 来源 默认空列表
    trace_id: str # 追踪ID 请求唯一 ID（调试用，非常重要）
    session_id: Optional[str] = None  # 服务端会话；未启用记忆时为 None
    meta: dict[str, Any] = Field(default_factory=dict) # 元数据 Token，日志等 可选
