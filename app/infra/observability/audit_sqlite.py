"""
app.infra.observability.audit_sqlite

这个文件负责把“审计事件（audit events）”落到 SQLite：
- 表：data/audit_events.db 里的 audit_events
- 一条请求（trace_id）对应多条事件（多行），用 seq 自增保证可排序回放
- 每条事件可带 payload，但只存“头4KB + 尾4KB”（总8KB）+ sha256 + 原始长度
- 额外信息用 fields_json（结构化 JSON）保存，便于未来扩展但不破坏表结构

排障复盘时，你会用它回答：
- 这次请求里模型产生了什么工具指令？
- 工具真实返回了什么/报了什么错？
- 这些步骤按顺序到底发生了几次？
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import aiosqlite

from app.infra.observability.trace_ctx import get_trace_id, next_seq


_SCHEMA = """
CREATE TABLE IF NOT EXISTS audit_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trace_id TEXT NOT NULL,
    seq INTEGER NOT NULL,
    ts_ms INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    status TEXT,

    -- 常用结构化字段（便于过滤/聚合）
    route TEXT,
    session_id TEXT,
    intent TEXT,
    tool_name TEXT,
    model_provider TEXT,
    model_name TEXT,

    -- payload（头/尾截断 + hash；原文不直接落库）
    payload_head TEXT,
    payload_tail TEXT,
    payload_sha256 TEXT,
    payload_len INTEGER,

    -- 额外信息（结构化 JSON，小而稳定）
    fields_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_audit_trace_seq ON audit_events(trace_id, seq);
CREATE INDEX IF NOT EXISTS idx_audit_type_ts ON audit_events(event_type, ts_ms);
"""


@dataclass(frozen=True)
class AuditSettings:
    db_path: Path
    payload_bytes: int = 8192
    head_bytes: int = 4096
    tail_bytes: int = 4096


_settings: AuditSettings | None = None


def _now_ms() -> int:
    return int(time.time() * 1000)


def _sha256(text: str) -> str:
    h = hashlib.sha256()
    h.update((text or "").encode("utf-8", errors="ignore"))
    return h.hexdigest()


def _truncate_head_tail(text: str, *, head_bytes: int, tail_bytes: int) -> tuple[str, str, int]:
    raw = (text or "").encode("utf-8", errors="ignore")
    n = len(raw)
    head = raw[:head_bytes]
    tail = raw[-tail_bytes:] if n > head_bytes else b""
    return head.decode("utf-8", errors="ignore"), tail.decode("utf-8", errors="ignore"), n


def configure_audit(db_path: str | Path) -> None:
    global _settings
    p = Path(db_path)
    if not p.is_absolute():
        # 相对路径按仓库根（含 app/ 的上一层）解析
        repo_root = Path(__file__).resolve().parents[3]
        p = (repo_root / p).resolve()
    _settings = AuditSettings(db_path=p)


async def init_audit_schema() -> None:
    """在 FastAPI lifespan 里调用一次。"""
    global _settings
    if _settings is None:
        # 默认写到 data/audit_events.db
        repo_root = Path(__file__).resolve().parents[3]
        configure_audit(repo_root / "data" / "audit_events.db")
    assert _settings is not None
    _settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(_settings.db_path) as db:
        await db.executescript(_SCHEMA)
        await db.commit()


def audit_enabled() -> bool:
    v = (os.getenv("RAGENT_AUDIT_ENABLED") or "true").strip().lower()
    return v in ("1", "true", "yes", "on")


async def emit_event(
    event_type: str,
    *,
    status: str | None = None,
    payload: str | None = None,
    route: str | None = None,
    session_id: str | None = None,
    intent: str | None = None,
    tool_name: str | None = None,
    model_provider: str | None = None,
    model_name: str | None = None,
    fields: Optional[dict[str, Any]] = None,
) -> None:
    """
    事件落库（append-only，多行/trace）。
    - trace_id/seq 来自 contextvars（背景音乐）
    - payload：只存 头4KB + 尾4KB + sha256 + 长度
    - fields：稳定的小 JSON，便于以后扩展
    """
    if not audit_enabled():
        return
    if _settings is None:
        repo_root = Path(__file__).resolve().parents[3]
        configure_audit(repo_root / "data" / "audit_events.db")

    trace_id = get_trace_id() or ""
    if not trace_id:
        return
    seq = next_seq()
    ts_ms = _now_ms()

    payload_text = payload or ""
    head, tail, nbytes = _truncate_head_tail(
        payload_text,
        head_bytes=_settings.head_bytes,  # type: ignore[union-attr]
        tail_bytes=_settings.tail_bytes,  # type: ignore[union-attr]
    )
    payload_hash = _sha256(payload_text) if payload_text else None
    fields_json = json.dumps(fields or {}, ensure_ascii=False) if (fields is not None) else "{}"

    assert _settings is not None
    async with aiosqlite.connect(_settings.db_path) as db:
        await db.execute(
            """
            INSERT INTO audit_events(
                trace_id, seq, ts_ms, event_type, status,
                route, session_id, intent, tool_name, model_provider, model_name,
                payload_head, payload_tail, payload_sha256, payload_len,
                fields_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                trace_id,
                seq,
                ts_ms,
                event_type,
                status,
                route,
                session_id,
                intent,
                tool_name,
                model_provider,
                model_name,
                head,
                tail,
                payload_hash,
                nbytes,
                fields_json,
            ),
        )
        await db.commit()

