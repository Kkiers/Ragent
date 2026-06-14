"""
在项目根目录执行（需已 pip install -r requirements.txt）::

    python scripts/mcp_probe.py --config config/mcp_servers.example.json --server filesystem

步骤含义：
1) 读 JSON（mcpServers 与 Cursor 类似）
2) 启动 stdio 子进程并 MCP initialize
3) 打印 list_tools（名称 + 描述 + inputSchema 摘要）
4) 若传入 --call-name / --call-json，则再执行一次 call_tool（用于冒烟）
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcp.types import TextContent

from app.infra.mcp import load_mcp_file_config, open_stdio_session, tool_result_to_text
from app.infra.mcp.spec_bridge import mcp_tool_to_tool_spec


def _short_schema(schema: object, limit: int = 400) -> str:
    try:
        if hasattr(schema, "model_dump"):
            blob = json.dumps(schema.model_dump(mode="json", exclude_none=True), ensure_ascii=False)  # type: ignore[union-attr]
        else:
            blob = json.dumps(schema, ensure_ascii=False)
    except TypeError:
        blob = str(schema)
    blob = blob.replace("\n", " ")
    return blob if len(blob) <= limit else blob[: limit - 3] + "..."


async def _run(args: argparse.Namespace) -> int:
    cfg_path = Path(args.config)
    if not cfg_path.is_file():
        print(f"找不到配置文件: {cfg_path.resolve()}", file=sys.stderr)
        return 2

    file_cfg = load_mcp_file_config(cfg_path)
    if args.server not in file_cfg.mcpServers:
        names = ", ".join(sorted(file_cfg.mcpServers))
        print(f"未知 server 别名 {args.server!r}。可用: {names}", file=sys.stderr)
        return 2

    entry = file_cfg.mcpServers[args.server]
    print(f"启动 MCP stdio: command={entry.command!r} args={entry.args!r}")

    async with open_stdio_session(entry) as session:
        await session.initialize()
        listed = await session.list_tools()
        prefix = f"{args.server}__" if args.name_prefix else ""
        print(f"\n共 {len(listed.tools)} 个工具:\n")
        for t in listed.tools:
            spec = mcp_tool_to_tool_spec(t, name_prefix=prefix)
            print(f"- {spec.name}")
            if spec.description:
                print(f"  说明: {spec.description[:200]}{'…' if len(spec.description) > 200 else ''}")
            print(f"  schema: {_short_schema(spec.input_schema)}")

        if args.call_name:
            raw = args.call_json or "{}"
            try:
                arguments = json.loads(raw)
            except json.JSONDecodeError as e:
                print(f"--call-json 不是合法 JSON: {e}", file=sys.stderr)
                return 2
            if not isinstance(arguments, dict):
                print("--call-json 必须解析为 JSON 对象", file=sys.stderr)
                return 2
            # 模型侧可能带前缀；MCP 进程只认原始 name
            mcp_name = args.call_name[len(prefix) :] if prefix and args.call_name.startswith(prefix) else args.call_name
            print(f"\n调用 call_tool({mcp_name!r}, ...) ...")
            result = await session.call_tool(mcp_name, arguments)
            text = tool_result_to_text(result)
            print("\n--- 文本结果 ---\n")
            print(text or "(空)")
            if args.verbose:
                print("\n--- 原始 content 块 ---\n")
                for i, block in enumerate(result.content or []):
                    if isinstance(block, TextContent):
                        print(f"[{i}] text: {block.text!r}")
                    else:
                        print(f"[{i}] {type(block).__name__}: {block!r}")
            if result.isError:
                return 1
    return 0


def main() -> None:
    p = argparse.ArgumentParser(description="列出 MCP 工具并可选用 call_tool 冒烟")
    p.add_argument("--config", required=True, help="JSON 路径（含 mcpServers）")
    p.add_argument("--server", required=True, help="mcpServers 里的别名，例如 filesystem")
    p.add_argument(
        "--name-prefix",
        action="store_true",
        help="打印时给工具名加 server__ 前缀（与多服合并到 Ragent 注册表时一致）",
    )
    p.add_argument("--call-name", default="", help="试用 call_tool 时使用的工具名（可带或不带前缀）")
    p.add_argument("--call-json", default="", help="传给 call_tool 的参数 JSON 对象字符串，默认 {}")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args()
    raise SystemExit(asyncio.run(_run(args)))


if __name__ == "__main__":
    main()
