"""
tests/manual/startup_smoke.py

手工烟测脚本：不启动 FastAPI，只验证“依赖 wiring 能跑通”：
- SQLite 记忆库能建表
- LLM client 能初始化（不一定发请求）
- vector store 能初始化
- RagService 能构造成功

用法：
  python tests/manual/startup_smoke.py
"""

import asyncio
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


async def main() -> None:
    """
    手工烟测：验证依赖初始化能跑通（DB/LLM/Vector/Service wiring）。
    用法：
      python tests/manual/startup_smoke.py
    """
    from app.infra.chat_memory.sqlite_memory import ChatSqliteMemory, default_chat_db_path
    from app.infra.llm.client import create_llm_client
    from app.infra.vector_store_search.vector_search import create_vector_store
    from app.services.intent_service import create_intent_service
    from app.services.query_service import create_query_service
    from app.services.rag_service import create_rag_service

    print("init db...")
    memory = ChatSqliteMemory(default_chat_db_path())
    await memory.init_schema()
    print("init llm...")
    llm_client = create_llm_client()
    print("init vector...")
    vector_store = create_vector_store()
    print("init query...")
    query_service = create_query_service(llm_client)
    print("init intent...")
    intent_service = create_intent_service(llm_client)
    print("init rag...")
    rag_service = create_rag_service(
        llm_client=llm_client,
        vector_store=vector_store,
        query_service=query_service,
        intent_service=intent_service,
        chat_memory=memory,
    )
    print("done", type(rag_service))


if __name__ == "__main__":
    asyncio.run(main())

