"""
scripts/dump_audit_trace.py

一次性排障脚本：按 trace_id 回放审计时间线（从 SQLite 的 audit_events 表读取）。

用途：
- 你拿到某次请求的 trace_id 后，用这个脚本把该请求发生过的事件按 seq 排序打印出来
- 重点查看：工具指令（tool_plan_llm_output）、工具返回（tool_execute_end）、以及入口/出口耗时

用法：
  python scripts/dump_audit_trace.py <trace_id>
"""

import json
import sqlite3
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: python scripts/dump_audit_trace.py <trace_id>")
        raise SystemExit(2)
    trace_id = sys.argv[1].strip()
    db = Path(__file__).resolve().parents[1] / "data" / "audit_events.db"
    con = sqlite3.connect(db)
    cur = con.cursor()
    cur.execute(
        """
        SELECT seq, ts_ms, event_type, status, route, session_id, intent, tool_name,
               payload_len, payload_sha256, payload_head, payload_tail, fields_json
        FROM audit_events
        WHERE trace_id = ?
        ORDER BY seq
        """,
        (trace_id,),
    )
    rows = cur.fetchall()
    print("rows:", len(rows))
    for r in rows:
        seq, ts_ms, et, st, route, sid, intent, tool, plen, ph, head, tail, fj = r
        print(f"\n[{seq}] {et} status={st} ts_ms={ts_ms}")
        if route:
            print("  route:", route)
        if sid:
            print("  session_id:", sid)
        if intent:
            print("  intent:", intent)
        if tool:
            print("  tool:", tool)
        print("  payload_len:", plen, "sha256:", ph)
        if head:
            print("  head:", head[:200])
        if tail:
            print("  tail:", tail[:200])
        try:
            extra = json.loads(fj or "{}")
        except Exception:
            extra = {"fields_json": fj}
        if extra:
            print("  fields:", json.dumps(extra, ensure_ascii=False)[:800])
    cur.execute("select count(*) from audit_events")
    total = cur.fetchone()[0]
    print("\n(total audit_events rows):", total)


if __name__ == "__main__":
    main()

