"""
03 · 掀开盖子看记忆 —— 打印 session 里到底存了哪些消息
------------------------------------------------------------------
运行：  python 03_inspect_history.py   （完全离线，不需要 API Key）

短期记忆不是魔法，它就是一串消息列表。这一幕直接把它打印出来：
  · 用 session.add_items(...) 手动塞几条（平时是 Runner 自动塞的）
  · 用 session.get_items() 取回来，逐条看 role / content
看完你就明白：所谓"记得住"，就是把这串历史每轮重新喂给模型。
"""

import asyncio
from agents import SQLiteSession


async def main():
    # 这些 session 方法是异步的，所以用 async；逻辑纯本地，无需联网
    session = SQLiteSession("inspect_demo")  # :memory:，跑完即弃

    # 手动写入几条对话历史（模拟 Agent 跑了两轮后留下的记录）
    await session.add_items([
        {"role": "user", "content": "我叫小明，体重 70 公斤。"},
        {"role": "assistant", "content": "好的小明，已经记下你的体重。"},
        {"role": "user", "content": "帮我制定一个减脂计划。"},
        {"role": "assistant", "content": "建议每周 3 次有氧 + 2 次力量训练……"},
    ])

    # 取回全部历史，这就是模型每轮真正"看到"的上下文
    items = await session.get_items()

    print(f"=== session 里现在有 {len(items)} 条消息 ===\n")
    for i, msg in enumerate(items, 1):
        role = msg.get("role", "?")
        content = msg.get("content", "")
        # 对齐打印：role 占一列，内容跟在后面
        print(f"[{i}] {role:<9} | {content}")

    print("\n[观察] 所谓会话记忆，就是一个按顺序保存的 items 列表。")
    print("[结论] 列表会越聊越长，所以保存全部历史不等于每轮都要全发。")
    print("[下一步] 运行 04_sliding_window.py。")


if __name__ == "__main__":
    asyncio.run(main())
