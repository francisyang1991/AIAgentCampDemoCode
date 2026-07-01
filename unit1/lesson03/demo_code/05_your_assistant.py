"""
05 · Your assistant skeleton (the P1 starting point) — multi-turn chat + memory (flagship theme: ResuMatch).
===========================================================================================================
Run:    python 05_your_assistant.py   (type exit to quit)

This is the prototype of your P1 skeleton — the [job-hunt assistant ResuMatch] that runs through this lesson:
  1) INSTRUCTIONS is already written as a job-hunt assistant using the "5-block structure" (copy and adapt it to your own topic)
  2) run it and chat a few rounds: first tell it your target role, then ask "what am I still missing", and see if it remembers
SQLiteSession makes it remember context automatically (we go deeper into memory in Unit 3).

★ Want a different topic (stock / travel / scheduling…)? Sure — just swap INSTRUCTIONS for your role, the skeleton stays the same.
"""

import _local  # noqa: F401 — no key? auto-fallback to local Ollama; no Ollama? prints a hint (see _local.py)
from agents import Agent, Runner, SQLiteSession

# ╔══════════════════════════════════════════════════════════╗
# ║  EDIT HERE: write your own assistant (follow the 5 blocks:      ║
# ║  role / capabilities / boundaries / style / format).           ║
# ║  Below is this lesson's theme "ResuMatch"; swap it for yours.   ║
# ╚══════════════════════════════════════════════════════════╝
INSTRUCTIONS = """【角色】你是"ResuMatch 求职教练"，帮求职者针对某个目标岗位定制简历要点与 cover letter。

【能力】你可以：
- 记住用户说过的目标岗位和已有经历
- 把已有经历按目标岗位重排、用岗位的语言改写
- 指出"匹配上了什么"和"还差什么"（缺口清单）

【边界】你不做：
- **绝不编造**用户没有的经历 / 学历 / 数字；信息不足先反问，不硬猜
- 与求职定制无关的请求（写代码、闲聊），礼貌拒绝

【风格】简洁、面试官视角；改动经历前先用一句话确认理解。

【格式】给简历要点时用清单，每行：动词开头 + 量化结果 + 岗位关键词。
"""
# ╔══════════════════════════════════════════════════════════╗
# ║  END OF EDIT REGION                                            ║
# ╚══════════════════════════════════════════════════════════╝

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
        # Pass in session, and the Agent remembers what was discussed earlier
        result = Runner.run_sync(agent, user, session=session)
        print("助手:", result.final_output)


if __name__ == "__main__":
    main()
