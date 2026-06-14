"""
tests/manual/audit_write_smoke.py

手工烟测脚本：不走 HTTP，直接调用 audit_sqlite.emit_event 写一条事件，
用来验证：
- audit_events.db 能创建/写入
- contextvars 的 trace_id/seq 生效

用法：
  python tests/manual/audit_write_smoke.py
"""

import asyncio
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


async def main() -> None:
    """
    手工烟测：验证 audit_events.db 可写入（不走 HTTP）。
    用法：
      python tests/manual/audit_write_smoke.py
    """
    from app.infra.observability.audit_sqlite import init_audit_schema, emit_event
    from app.infra.observability.trace_ctx import reset_trace, set_trace

    await init_audit_schema()
    tokens = set_trace("trace_test_001")
    await emit_event("hello", payload="payload-123", fields={"a": 1})
    reset_trace(tokens)

    db = REPO_ROOT / "data" / "audit_events.db"
    con = sqlite3.connect(db)
    cur = con.cursor()
    cur.execute("select count(*) from audit_events")
    print("count:", cur.fetchone()[0])
    cur.execute("select trace_id, seq, event_type, payload_len from audit_events order by id desc limit 3")
    print(cur.fetchall())


if __name__ == "__main__":
    asyncio.run(main())

