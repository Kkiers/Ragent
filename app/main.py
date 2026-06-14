"""
app.main

FastAPI 应用入口（uvicorn 启动的 app.main:app）。

这里主要做三件事：
- 读取项目根 .env（用于模型/向量库/MCP/审计等配置）
- 在 lifespan 启动阶段初始化依赖（SQLite 记忆库 + 审计库、LLM client、vector store、services）
- 注册中间件、异常处理器、路由（/api/chat、/api/tools/catalog）
"""

from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")

from app.api.chat import router as chat_router
from app.api.tools_catalog import router as tools_catalog_router
from app.framework.exceptions import register_exception_handlers
from app.framework.response import Utf8JSONResponse
from app.framework.middleware import add_request_context_middleware
from app.infra.chat_memory.sqlite_memory import ChatSqliteMemory, default_chat_db_path
from app.infra.llm.client import create_llm_client
from app.infra.vector_store_search.vector_search import create_vector_store
from app.services.intent_service import create_intent_service
from app.services.query_service import create_query_service
from app.services.rag_service import create_rag_service
from app.infra.observability.audit_sqlite import init_audit_schema


@asynccontextmanager
async def lifespan(app: FastAPI):
    memory = ChatSqliteMemory(default_chat_db_path())
    await memory.init_schema()
    await init_audit_schema()

    llm_client = create_llm_client()
    vector_store = create_vector_store()
    query_service = create_query_service(llm_client)
    intent_service = create_intent_service(llm_client)

    rag_service = create_rag_service(
        llm_client=llm_client,
        vector_store=vector_store,
        query_service=query_service,
        intent_service=intent_service,
        chat_memory=memory,
    )

    app.state.rag_service = rag_service
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="ragent_py",
        default_response_class=Utf8JSONResponse,
        lifespan=lifespan,
    )

    # CORS 配置
    # 注意：浏览器在 allow_credentials=True 时，禁止 Access-Control-Allow-Origin 为 "*"
    # 否则 Cookie（session）无法写入/携带，刷新后自然拿不到历史。
    origins_env = os.getenv("RAGENT_CORS_ORIGINS", "").strip()
    allow_origins = [o.strip() for o in origins_env.split(",") if o.strip()] if origins_env else []
    allow_origin_regex = os.getenv(
        "RAGENT_CORS_ORIGIN_REGEX",
        r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_origin_regex=allow_origin_regex if not allow_origins else None,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    add_request_context_middleware(app)
    register_exception_handlers(app)

    app.include_router(chat_router)
    app.include_router(tools_catalog_router)

    # 挂载静态文件
    static_dir = Path(__file__).resolve().parents[1] / "static"
    if static_dir.exists():
        app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

    return app


app = create_app()
