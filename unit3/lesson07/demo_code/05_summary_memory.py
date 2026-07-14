"""05｜历史太长时，把旧内容压成一份简版状态。

基础：python 05_summary_memory.py       # 看懂数据流
进阶：python 05_summary_memory.py --live # 调用 Responses compaction
"""

import argparse
import asyncio

from agents import Agent, Runner, SQLiteSession
from agents.memory import OpenAIResponsesCompactionSession


def show_concept() -> None:
    print("压缩前：很多轮旧对话 + 最近对话")
    print("压缩后：一份简版任务状态 + 最近对话")
    print("\n代码接入位置：")
    print('underlying = SQLiteSession("tenant:user:thread", "sessions.db")')
    print("session = OpenAIResponsesCompactionSession(session_id=..., underlying_session=underlying)")
    print("await session.run_compaction({'force': True})")
    print("\n[观察] 压缩是有损的，不能把地点、签证、薪资底线只扔进自由文本摘要。")
    print("[结论] 基础课理解数据流即可；自动/手动触发是进阶。")
    print("[下一步] 运行 06_state_slots.py。")


async def run_live() -> None:
    underlying = SQLiteSession("resumatch:alice:thread-01", "sessions.db")
    await underlying.clear_session()
    session = OpenAIResponsesCompactionSession(
        session_id="resumatch:alice:thread-01",
        underlying_session=underlying,
        should_trigger_compaction=lambda _: False,
    )
    agent = Agent(
        name="ResuMatch",
        instructions="你是求职助手。地点、签证和薪资底线不得自行改写。",
    )
    await Runner.run(agent, "我只看马德里或远程岗位。", session=session)
    await Runner.run(agent, "我需要公司支持工作签证。", session=session)
    before = len(await underlying.get_items())
    await session.run_compaction({"force": True})
    after = len(await underlying.get_items())
    result = await Runner.run(agent, "复述我的两个硬约束。", session=session)
    print(f"压缩前 items：{before}\n压缩后 items：{after}\n验证：{result.final_output}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    asyncio.run(run_live()) if args.live else show_concept()


if __name__ == "__main__":
    main()
