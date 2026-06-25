"""
05 · Your assistant (the P1 starting point) —— multi-turn conversation + memory
------------------------------------------------
Run:      python 05_your_assistant.py   (type exit to quit)

This is the prototype of your P1 skeleton —— the [job-hunt assistant ResuMatch] that runs through this lesson:
  1) instructions are already written as the "job-hunt assistant" role (you can copy and change it to your own topic)
  2) run it and chat a few rounds: first tell it your target role, then ask "what am I still missing", and see if it remembers
SQLiteSession makes it remember context automatically (we go deeper into memory in Unit 3).

★ Want a different topic (travel / scheduling / customer support…)? Sure: just swap INSTRUCTIONS for your role, the skeleton stays the same.
"""

import _local  # noqa: F401 —— no key? auto-falls back to local Ollama; no Ollama? prints a hint (see _local.py in this dir)
from agents import Agent, Runner, SQLiteSession

# ↓↓↓ this is the "job-hunt assistant" role of this lesson; to switch topics, just change this ↓↓↓
INSTRUCTIONS = """你是 ResuMatch 求职助手。
- 能做：针对用户的目标岗位 / JD，重排简历要点、起草 cover letter、指出匹配缺口
- 不做：绝不编造用户没有的经历 / 数字；信息不足先反问，不硬猜
- 风格：简洁、面试官视角、先确认再改
"""
# ↑↑↑ change here ↑↑↑

agent = Agent(name="ResuMatch", instructions=INSTRUCTIONS)
session = SQLiteSession("p1_demo")  # remembers conversation history automatically; memory covered in depth in Unit 3


def main():
    print("开始对话（输入 exit / 退出 结束）")
    print("试试：先说『我想投数据分析师』，再问『那我简历还差什么？』看它记不记得。")
    while True:
        user = input("\n你:   ").strip()
        if user in {"exit", "quit", "退出"}:
            break
        if not user:
            continue
        # Pass in session, and the Agent can remember what was discussed earlier
        result = Runner.run_sync(agent, user, session=session)
        print("助手:", result.final_output)


if __name__ == "__main__":
    main()
