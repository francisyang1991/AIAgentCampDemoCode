"""_local.py —— 让本目录 demo 直接 `python xxx.py` 就能跑，外加两个教学小工具。

【后端自动选择】import 本模块即生效，按顺序挑：
  ① 设了 OPENAI_API_KEY（真 key）→ 原样用 OpenAI，生产级效果；
  ② 没 key 但本机 Ollama 在跑（:11434）→ 自动用本地模型 qwen2.5:7b，零成本、可断网；
  ③ 两者都没有 → 打印一句怎么办，干净退出（不再甩一长串 traceback）。

【两个 demo 通用工具】
  · _local.chat_loop(agent, hint="…")    演示跑完后留在交互模式，让你接着问；
  · _local.show_steps(result.new_items)  把 Agent Loop 每步用一行讲清，不 dump 整个对象。

想显式指定模型 / 批量跑，也可用根目录 run_with_ollama.py。
弱机想更快：  LOCAL_MODEL=qwen2.5:3b python xxx.py
"""
from __future__ import annotations

import os
import urllib.request

_BASE = os.environ.get("LOCAL_BASE_URL", "http://localhost:11434/v1")
_MODEL = os.environ.get("LOCAL_MODEL", "qwen2.5:7b")
_KEY = os.environ.get("OPENAI_API_KEY", "")


def _ollama_alive() -> bool:
    """探一下本机 Ollama 在不在（0.6s 超时，不卡课堂）。"""
    try:
        urllib.request.urlopen(_BASE.replace("/v1", "") + "/api/version", timeout=0.6)
        return True
    except Exception:
        return False


def chat_loop(agent, hint="继续追问", use_session=True):
    """演示跑完后留在交互模式，让你接着问；输入 exit / 退出 / Ctrl-D 结束。

    - use_session=True：用一个内存会话，让你的追问能连贯上下文（默认）。
    - 单次调用出错（本地模型偶尔抽风）不会让整个程序崩，打印后继续等你输入。
    """
    from agents import Runner

    session = None
    if use_session:
        try:
            from agents import SQLiteSession
            session = SQLiteSession("demo_chat")  # 内存会话，退出即清空
        except Exception:
            session = None

    print(f"\n—— 轮到你：{hint}（输入 exit 退出）——")
    while True:
        try:
            q = input("\n你:   ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            return
        if q in {"exit", "quit", "退出"}:
            print("再见！")
            return
        if not q:
            continue
        try:
            print("助手:", Runner.run_sync(agent, q, session=session).final_output)
        except Exception as e:
            print(f"[出错] {type(e).__name__}：{e}（换句话再试，或输入 exit 退出）")


def show_steps(items):
    """把 result.new_items 每一步用一行讲清楚：调了什么工具、返回什么、最后说了什么。

    比直接 print(item) 干净得多——只挑关键字段，不再 dump 整个 Agent 对象。
    """
    print("\n--- Agent Loop 内部（它走了哪几步）---")
    for i, item in enumerate(items, 1):
        kind = type(item).__name__
        raw = getattr(item, "raw_item", None)
        if kind == "ToolCallItem":
            name = getattr(raw, "name", "?")
            args = getattr(raw, "arguments", "")
            print(f"  {i}. 🔧 请求工具  {name}({args})")
        elif kind == "ToolCallOutputItem":
            print(f"  {i}. ↩️  工具返回  {getattr(item, 'output', '')}")
        elif kind == "MessageOutputItem":
            try:
                from agents import ItemHelpers
                text = ItemHelpers.text_message_output(item)
            except Exception:
                text = str(getattr(item, "raw_item", item))
            text = text.replace("\n", " ")
            if len(text) > 60:
                text = text[:60] + "…"
            print(f"  {i}. 💬 模型消息  {text}")
        else:
            print(f"  {i}. ·  {kind}")


# ① 有真 key：什么都不做，demo 原样走 OpenAI
if _KEY and _KEY != "ollama":
    pass

# ② 没真 key 但 Ollama 活着：把 SDK 指向本地，给没写 model= 的 Agent 注入本地模型
elif _ollama_alive():
    from openai import AsyncOpenAI

    import agents
    from agents import (
        set_default_openai_api,
        set_default_openai_client,
        set_tracing_disabled,
    )

    os.environ.setdefault("OPENAI_API_KEY", "ollama")  # 占位，绕过 SDK 的“缺 key”检查
    set_default_openai_client(AsyncOpenAI(base_url=_BASE, api_key="ollama"))
    set_default_openai_api("chat_completions")  # 本地服务只认 chat completions（不是 Responses）
    set_tracing_disabled(True)                  # 别往 OpenAI 发 trace（没真 key 会报错）

    _orig_init = agents.Agent.__init__

    def _init_with_local_model(self, *args, **kwargs):
        if not kwargs.get("model"):
            kwargs["model"] = _MODEL
        _orig_init(self, *args, **kwargs)

    agents.Agent.__init__ = _init_with_local_model
    print(f"[本地] 没设 OPENAI_API_KEY，自动用 Ollama {_MODEL} 跑（零成本）。\n")

# ③ 两者都没有：友好提示，干净退出（不抛 traceback）
else:
    print(
        "\n⚠️  没检测到 OPENAI_API_KEY，也没检测到本机 Ollama（http://localhost:11434）。\n"
        "   二选一，再重跑本文件：\n"
        "   ① 本地零成本（推荐）：装 Ollama → `ollama pull qwen2.5:7b`，\n"
        "      详见根目录《本地模型零成本跑法.md》；启动后直接重跑即可。\n"
        "   ② 用 OpenAI：`export OPENAI_API_KEY=sk-...` 后重跑。\n"
    )
    raise SystemExit(0)
