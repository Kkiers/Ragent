from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import aiosqlite

from app.domain.schemas import ChatMessage


# 数据库表结构
_SCHEMA = """
PRAGMA journal_mode=WAL; -- 读写并发更好

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY, -- 会话ID
    created_at TEXT NOT NULL, -- 创建时间
    updated_at TEXT NOT NULL -- 更新时间
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- 表示消息先后顺序
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE, -- 会话ID
    trace_id TEXT, -- 请求唯一ID
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    intent TEXT,
    context_json TEXT, -- 送给下游模型的完整上下文（messages + report），通常仅 assistant 行有
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_messages_session_created
ON messages (session_id, id);
"""


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class ChatSqliteMemory:
    """SQLite 对话记忆：
    服务端生成/校验 session_id，
    按条存 user/assistant。"""

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    # 启动时建目录 + 建表
    async def init_schema(self) -> None:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("PRAGMA foreign_keys = ON")
            await db.executescript(_SCHEMA)
            # 向后兼容：旧库可能缺 context_json 列
            try:
                cur = await db.execute("PRAGMA table_info(messages)")
                cols = [r[1] for r in await cur.fetchall()]  # (cid, name, type, notnull, dflt, pk)
                if "context_json" not in cols:
                    await db.execute("ALTER TABLE messages ADD COLUMN context_json TEXT")
            except Exception:
                # schema 迁移失败不应影响主链路（最多就是没有上下文字段）
                pass
            await db.commit()

    # 新建或查询：要么复用会话，要么新建 UUID
    # 空 id / 无效 id → 新会话；合法且存在的 id → 原样返回。
    async def ensure_session(self, session_id: Optional[str]) -> str:
        """无 id 或 id 在库中不存在时生成新会话；存在则复用。"""
        sid = (session_id or "").strip()
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("PRAGMA foreign_keys = ON")
            if sid:
                cur = await db.execute("SELECT 1 FROM sessions WHERE id = ?", (sid,))
                row = await cur.fetchone()
                if row:
                    return sid
            new_id = str(uuid.uuid4())
            now = _utc_now_iso()
            await db.execute(
                "INSERT INTO sessions (id, created_at, updated_at) VALUES (?, ?, ?)",
                (new_id, now, now),
            )
            await db.commit()
            return new_id

    # 查询：拉最近若干条，转成 ChatMessage 列表
    async def fetch_history(self, session_id: str, *, max_messages: int = 40) -> list[ChatMessage]:
        """取该会话最近 max_messages 条（按时间正序），供模型使用。"""
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("PRAGMA foreign_keys = ON")
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                """
                SELECT role, content FROM messages
                WHERE session_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (session_id, max_messages),
            )
            rows = await cur.fetchall()
        rows = list(reversed(rows))
        out: list[ChatMessage] = []
        for r in rows:
            role = r["role"]
            if role not in ("user", "assistant", "system"):
                continue
            out.append(ChatMessage.model_validate({"role": role, "content": r["content"]}))
        return out

    # 写入：一轮对话写两行 + 更新会话时间
    async def record_exchange(
        self,
        *,
        session_id: str,
        trace_id: str,
        user_content: str,
        assistant_content: str,
        intent: Optional[str] = None,
        context: object | None = None,
    ) -> None:
        """写入一轮：一条 user + 一条 assistant，
        并更新 sessions.updated_at。"""
        now = _utc_now_iso()
        context_json = None
        if context is not None:
            try:
                context_json = json.dumps(context, ensure_ascii=False)
            except Exception:
                context_json = None
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("PRAGMA foreign_keys = ON")
            await db.execute(
                """
                INSERT INTO messages (session_id, trace_id, role, content, intent, context_json, created_at)
                VALUES (?, ?, 'user', ?, ?, NULL, ?)
                """,
                (session_id, trace_id, user_content, intent, now),
            )
            await db.execute(
                """
                INSERT INTO messages (session_id, trace_id, role, content, intent, context_json, created_at)
                VALUES (?, ?, 'assistant', ?, ?, ?, ?)
                """,
                (session_id, trace_id, assistant_content, intent, context_json, now),
            )
            await db.execute(
                "UPDATE sessions SET updated_at = ? WHERE id = ?",
                (now, session_id),
            )
            await db.commit()


def default_chat_db_path(project_root: Optional[Path] = None) -> Path:
    """默认 data/chat_memory.db；sqlite_memory.py 在 app/infra/chat_memory/，parents[3] 为项目根。"""
    root = project_root or Path(__file__).resolve().parents[3]
    return root / "data" / "chat_memory.db"
