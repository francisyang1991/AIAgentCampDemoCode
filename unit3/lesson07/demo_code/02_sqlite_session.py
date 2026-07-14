"""02｜同一个 Session：下一轮可以取回上一轮。

基础：python 02_sqlite_session.py
联网：python 02_sqlite_session.py --live
聊天：python 02_sqlite_session.py --chat
"""

import argparse
import asyncio

from agents import Agent, Runner, SQLiteSession


SESSION_ID = "student:xiaoming:thread-01"
TURNS = ["你好，我叫小明。", "我刚才说我叫什么？"]


async def show_storage() -> None:
    session = SQLiteSession(SESSION_ID)
    await session.clear_session()
    await session.add_items(
        [
            {"role": "user", "content": TURNS[0]},
            {"role": "assistant", "content": "你好，小明。"},
        ]
    )
    items = await session.get_items()
    print("【离线演示】Session 取回了上一轮：")
    for item in items:
        print(f"  {item['role']:<9} | {item['content']}")
    print(f"\n新问题：{TURNS[1]}")
    print("模型本轮会收到：上面的历史 + 新问题。")


def run_live(chat: bool = False) -> None:
    session = SQLiteSession(SESSION_ID)
    agent = Agent(name="ResuMatch", instructions="你是求职助手，用中文简短回答。")
    if chat:
        print("进入聊天模式（输入 exit 退出）。")
        while True:
            question = input("\n你：").strip()
            if question in {"exit", "quit", "退出"}:
                return
            if question:
                print("助手：", Runner.run_sync(agent, question, session=session).final_output)
        return
    for index, question in enumerate(TURNS, 1):
        result = Runner.run_sync(agent, question, session=session)
        print(f"\n第 {index} 轮\n  用户：{question}\n  助手：{result.final_output}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--chat", action="store_true")
    args = parser.parse_args()
    if args.live or args.chat:
        run_live(chat=args.chat)
    else:
        asyncio.run(show_storage())
    print("\n[观察] Session 里有上一轮的 user/assistant items。")
    print("[结论] 同一个 thread 复用同一 session_id；不同 thread 不要混用。")
    print("[下一步] 运行 03_inspect_history.py。")


if __name__ == "__main__":
    main()
