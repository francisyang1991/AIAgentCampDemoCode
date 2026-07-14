"""04｜保存全部历史，但本轮只发最近内容。

运行：python 04_sliding_window.py（完全离线）
"""

from __future__ import annotations

import asyncio
from typing import Any

from agents import RunConfig, SessionSettings, SQLiteSession


KEEP_ITEMS = 6  # 这个 demo 中大约是 3 轮 user/assistant


def keep_recent_history(history: list[Any], new_input: list[Any]) -> list[Any]:
    """这是“过滤器”：只决定本轮送给模型的 items。"""
    return history[-KEEP_ITEMS:] + new_input


async def main() -> None:
    session = SQLiteSession("student:window:thread-01")
    await session.clear_session()
    for turn in range(1, 7):
        await session.add_items(
            [
                {"role": "user", "content": f"第 {turn} 轮：我的岗位要求是什么？"},
                {"role": "assistant", "content": f"第 {turn} 轮：已记录。"},
            ]
        )

    stored = await session.get_items()
    new_input = [{"role": "user", "content": "请按最近的要求继续推荐。"}]
    model_input = keep_recent_history(stored, new_input)

    print(f"完整保存：{len(stored)} 条")
    print(f"本轮发送：{len(model_input)} 条（最近 {KEEP_ITEMS} 条 + 新问题）")
    assert len(stored) == 12
    assert len(model_input) == 7

    print("\n本轮发送的内容：")
    for item in model_input:
        print(f"  {item['role']:<9} | {item['content']}")

    print("\n接入 Runner 时用这个配置：")
    print("RunConfig(session_input_callback=keep_recent_history, session_settings=SessionSettings(limit=50))")
    _ = RunConfig(
        session_input_callback=keep_recent_history,
        session_settings=SessionSettings(limit=50),
    )
    print("\n[观察] Session 里的 12 条都还在，模型本轮只看 7 条。")
    print("[结论] 存多少和发多少是两个控制点。")
    print("[下一步] 运行 05_summary_memory.py。")


if __name__ == "__main__":
    asyncio.run(main())
