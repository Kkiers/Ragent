from __future__ import annotations

import asyncio
import sys
import uuid
from pathlib import Path

from dotenv import load_dotenv


"""
测试tool_pipeline，不考虑意图识别
"""
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Windows 终端常见乱码：强制 stdout 使用 UTF-8
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from app.domain.schemas import ChatRequest
from app.framework.context import RequestContext
from app.infra.llm.client import create_llm_client
from app.pipeline.tool_pipeline import run_tool_pipeline


def _load_env() -> None:
    # 跟 app/main.py 保持一致：加载项目根目录的 .env
    load_dotenv(dotenv_path=PROJECT_ROOT / ".env")


async def main() -> None:
    _load_env()

    query = " ".join(sys.argv[1:]).strip() or "西雅图今天的天气怎么样？"

    llm_client = create_llm_client()

    req = ChatRequest(
        query=query,
        history=[],
        debug=True,
        stream=False,
    )
    ctx = RequestContext(trace_id=str(uuid.uuid4()))

    resp = await run_tool_pipeline(
        req=req,
        ctx=ctx,
        llm_client=llm_client,
        tool_name="weather",
        effective_query=query,
    )

    print("=== trace_id ===")
    print(resp.trace_id)
    print()

    print("=== intent ===")
    print(resp.intent)
    print()

    print("=== answer ===")
    print(resp.answer)
    print()

    print("=== clarify_question ===")
    print(resp.clarify_question)
    print()

    print("=== meta keys ===")
    print(sorted(list(resp.meta.keys())))
    print()

    if "tool_llm_output" in resp.meta:
        print("=== tool_llm_output (truncated) ===")
        print(resp.meta["tool_llm_output"])
        print()

    if "tool_call" in resp.meta:
        print("=== tool_call ===")
        print(resp.meta["tool_call"])
        print()

    if "tool_error" in resp.meta:
        print("=== tool_error ===")
        print(resp.meta["tool_error"])
        print()


if __name__ == "__main__":
    asyncio.run(main())

