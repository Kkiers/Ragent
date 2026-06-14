from enum import Enum


# 意图类型：只保留三类分支（RAG / CHAT / AGENT）
class IntentType(str, Enum):
    RAG = "RAG"
    CHAT = "CHAT"
    AGENT = "AGENT"

# 使用
# IntentType.RAG
