"""
tests/manual/chat_multi_tool_smoke.py

手工烟测脚本：向本地 FastAPI 的 /api/chat 发一个“理论上需要多次工具调用”的问题，
用来观察当前系统真实行为（目前是否仍只执行一次工具调用）。

用法：
  1) 先启动服务：python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
  2) 再运行：python tests/manual/chat_multi_tool_smoke.py
"""

import json

import requests


def main() -> None:
    """
    手工烟测：向本地 /api/chat 发一个“理应需要多次工具调用”的问题，
    用来观察当前系统的真实行为（是否只做一次 tool call）。

    用法：
      python tests/manual/chat_multi_tool_smoke.py
    """
    payload = {
        "query": "请分别查询北京今天和上海明天的天气（温度/降雨/风），并对比后给出穿衣建议。",
        "history": [],
        "enable_heavy_rewrite": True,
        "top_k": 5,
        "debug": True,
    }
    r = requests.post("http://127.0.0.1:8000/api/chat", json=payload, timeout=30)
    print("status:", r.status_code)
    try:
        print(json.dumps(r.json(), ensure_ascii=False, indent=2))
    except Exception:
        print(r.text)


if __name__ == "__main__":
    main()

