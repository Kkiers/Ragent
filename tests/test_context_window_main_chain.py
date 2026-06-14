"""
走主问答链路（RagService.handle_chat），每轮把「实际送进模型的上下文窗口」追加到 TXT。

要点
----
- 客户端每次请求带上**上一轮响应里的 session_id**，SQLite 会续同一会话；不带或无效 id 时
  ensure_session 会分配**新的 UUID**（不会把你随便写的字符串当新 id 用）。
- 换 session：本脚本在 queries 文件里用单独一行的 `---` 分隔；之后会用新 session，
  并改用**新 session_id** 作为文件名再写一个 TXT，避免和旧 session 混在一起。
- 仅在意图为 **RAG / CHAT** 且 `debug=true` 时，响应 `meta.context_window` 里会有
  `messages`（完整装配列表）与裁剪统计；**工具/澄清/工作流**等分支可能无该字段。

用法（项目根目录）::

  python scripts/test_context_window_main_chain.py
  python scripts/test_context_window_main_chain.py --queries-file scripts/test_memory_fixtures/context_window_chain_sample.txt
  python scripts/test_context_window_main_chain.py --queries-file my.txt --out-dir ./dumps

依赖：.env 里 LLM 等配置与线上一致；会真实调用模型与向量库（若走 RAG）。
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def _safe_filename(session_id: str) -> str:
    return "".join(c if c not in '<>:"/\\|?*' else "_" for c in session_id)


def _load_query_lines(path: Path) -> list[str | None]:
    """
    返回若干条 query；None 表示「此处新开 session」（对应文件中的 --- 行）。
    """
    raw = path.read_text(encoding="utf-8").splitlines()
    out: list[str | None] = []
    for line in raw:
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s in ("---", "==="):
            out.append(None)
            continue
        out.append(s)
    return out


def _append_round_dump(
    *,
    path: Path,
    round_no: int,
    session_id: str,
    trace_id: str,
    intent: str,
    query: str,
    answer: str | None,
    clarify: str | None,
    context_window: dict | None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    sep = "=" * 76
    with path.open("a", encoding="utf-8") as f:
        f.write(f"\n{sep}\n")
        f.write(f"UTC 时间: {now}\n")
        f.write(f"Session ID（本文件仅含此会话）: {session_id}\n")
        f.write(f"Trace ID: {trace_id}\n")
        f.write(f"轮次: 第 {round_no} 轮\n")
        f.write(f"意图: {intent}\n")
        f.write(f"用户输入（本轮 query）:\n{query}\n")
        if clarify:
            f.write(f"澄清问题:\n{clarify}\n")
        if answer:
            prev = (answer[:500] + "…") if len(answer) > 500 else answer
            f.write(f"助手回复（节选）:\n{prev}\n")
        f.write(f"{sep}\n")
        f.write("【上下文窗口 — 与本轮 LLM 调用 assemble 结果一致】\n")

        if not context_window:
            f.write(
                "（本轮 meta 无 context_window：可能走了工具/澄清/工作流等未装配窗口的分支。）\n"
            )
            f.write("\n")
            return

        msgs = context_window.get("messages")
        if isinstance(msgs, list) and msgs:
            for i, m in enumerate(msgs):
                role = m.get("role", "?") if isinstance(m, dict) else getattr(m, "role", "?")
                content = m.get("content", "") if isinstance(m, dict) else getattr(m, "content", "")
                f.write(f"\n--- 消息 [{i}] role={role} ---\n")
                f.write(str(content))
                f.write("\n")
        else:
            f.write("（无 messages 字段）\n")

        f.write(f"\n--- context_window 其余字段（JSON）---\n")
        rest = {k: v for k, v in context_window.items() if k != "messages"}
        f.write(json.dumps(rest, ensure_ascii=False, indent=2))
        f.write("\n")


async def _bootstrap_rag_service():
    from dotenv import load_dotenv

    load_dotenv(_ROOT / ".env")

    from app.infra.chat_memory.sqlite_memory import ChatSqliteMemory, default_chat_db_path
    from app.infra.llm.client import create_llm_client
    from app.infra.vector_store_search.vector_search import create_vector_store
    from app.services.intent_service import create_intent_service
    from app.services.query_service import create_query_service
    from app.services.rag_service import create_rag_service

    memory = ChatSqliteMemory(default_chat_db_path(_ROOT))
    await memory.init_schema()
    llm_client = create_llm_client()
    vector_store = create_vector_store()
    query_service = create_query_service(llm_client)
    intent_service = create_intent_service(llm_client)
    return create_rag_service(
        llm_client=llm_client,
        vector_store=vector_store,
        query_service=query_service,
        intent_service=intent_service,
        chat_memory=memory,
    )


async def _run(
    *,
    queries: list[str | None],
    out_dir: Path,
    truncate_session_files: bool,
) -> None:
    from app.domain.schemas import ChatRequest
    from app.framework.context import RequestContext

    rag = await _bootstrap_rag_service()
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    session_id: str | None = None
    out_path: Path | None = None
    round_no = 0

    for item in queries:
        if item is None:
            session_id = None
            out_path = None
            round_no = 0
            print("--- 分隔：下一轮将使用新 session（新 TXT 文件名）---")
            continue

        round_no += 1
        trace_id = str(uuid.uuid4())
        ctx = RequestContext(trace_id=trace_id)

        req = ChatRequest(
            query=item,
            session_id=session_id,
            history=[],
            debug=True,
        )
        resp = await rag.handle_chat(req, ctx)
        sid = resp.session_id or session_id
        if sid is None:
            print("警告：响应未带 session_id，无法写 TXT。")
            continue

        if out_path is None or sid != session_id:
            session_id = sid
            out_path = out_dir / f"{_safe_filename(session_id)}.txt"
            if truncate_session_files and out_path.exists():
                out_path.unlink()
            with out_path.open("a", encoding="utf-8") as f:
                f.write(
                    f"主链路上下文窗口导出\n"
                    f"说明: 本文件仅记录 session_id = {session_id} 的对话；\n"
                    f"其它 session 会写入其它文件名，不会混在本文件。\n"
                )
            print(f"写入文件: {out_path}")

        cw = resp.meta.get("context_window") if isinstance(resp.meta, dict) else None
        if not isinstance(cw, dict):
            cw = None

        assert out_path is not None
        _append_round_dump(
            path=out_path,
            round_no=round_no,
            session_id=session_id,
            trace_id=trace_id,
            intent=resp.intent.value,
            query=item,
            answer=resp.answer,
            clarify=resp.clarify_question,
            context_window=cw,
        )
        print(f"  第 {round_no} 轮已记录 intent={resp.intent.value} trace={trace_id[:8]}…")


def main() -> None:
    p = argparse.ArgumentParser(description="主链路上下文窗口导出到 TXT")
    p.add_argument(
        "--queries-file",
        type=Path,
        default=_ROOT / "tests" / "test_memory_fixtures" / "context_window_chain_sample.txt",
        help="每行一条用户话；# 开头为注释；单独一行 --- 表示新开 session",
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=_ROOT / "tests" / "tests_context_window_chain_output",
        help="TXT 输出目录（每个 session 一个 <session_id>.txt）",
    )
    p.add_argument(
        "--truncate",
        action="store_true",
        help="若目标 TXT 已存在则在本 session 第一次写入前删除（仅该文件）",
    )
    args = p.parse_args()

    if not args.queries_file.is_file():
        print("找不到 queries 文件:", args.queries_file)
        sys.exit(1)

    queries = _load_query_lines(args.queries_file)
    if not queries:
        print("没有可执行的 query 行。")
        sys.exit(1)

    asyncio.run(
        _run(
            queries=queries,
            out_dir=args.out_dir,
            truncate_session_files=bool(args.truncate),
        )
    )


if __name__ == "__main__":
    main()
