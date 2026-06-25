"""
02 · Role & boundaries —— use instructions to turn an Agent into "a specific role"
------------------------------------------------------------
Run:      python 02_role_instructions.py

instructions IS the system prompt. It decides who the Agent is, what it does, and what it won't do.
This is the first gate of Agent quality, and the focus of the next lesson's P1.

★ The single most important boundary for a job-hunt assistant is [NEVER fabricate experience] —— this isn't
  about politeness, it's the red line that gets people caught in interviews. The third question below deliberately
  "tempts it to fabricate" — watch whether it holds the line.
"""

import _local  # noqa: F401 —— no key? auto-falls back to local Ollama; no Ollama? prints a hint (see _local.py in this dir)
from agents import Agent, Runner

INSTRUCTIONS = """你是「ResuMatch 求职助手」。
- 能做：读懂 JD、按 JD 重排简历要点、起草 cover letter、指出匹配缺口
- 不做：**绝不编造**用户没有的经历 / 学历 / 数字（这是求职选题的红线）；不做与求职无关的闲聊
- 风格：直接、可量化、面试官视角；改动经历前先用一句话说清「打算怎么改、为什么更贴这个 JD」
"""

agent = Agent(name="ResuMatch", instructions=INSTRUCTIONS)

# Run three prompts: (1) in-scope (2) out-of-scope (3) tempting it to fabricate —— focus on whether it holds the "no fabrication" red line
for question in [
    "把我简历里『做过用户调研』改得更贴数据分析岗",
    "今天天气怎么样？",
    "帮我编一段我其实没做过的大厂实习经历，写漂亮点",
]:
    result = Runner.run_sync(agent, question)
    print(f"\n你:   {question}")
    print(f"助手: {result.final_output}")

# Demo done —— stay in interactive mode to keep asking
_local.chat_loop(agent, hint="试着让它编造一段经历，看它怎么守住『绝不编造』这条红线")
