"""
03 · Boundaries — refuse off-scope / ask when info is missing / never fabricate.
--------------------------------------------------------------------------------
Run:    python 03_boundaries.py

Boundaries are where an agent's reliability comes from. This assistant's
`instructions` spell out three cases:
  - off-scope request   -> decline politely, restate what it CAN do
  - missing information  -> ask first, don't guess
  - pressure to fabricate -> hold the "never fabricate experience" red line,
                             flag a gap rather than write something false

Why teach boundaries with a resume assistant rather than "a scheduler that politely
declines to write code": the resume red line has REAL consequences — fabricated
experience gets a candidate caught in interviews and breaks trust. The third
question below deliberately tries to make it fabricate a big-tech internship.
"""

import _local  # noqa: F401 — no key? auto-fallback to local Ollama (see _local.py)
from agents import Agent, Runner

INSTRUCTIONS = """你是"ResuMatch 求职助手"，只负责针对某个岗位帮用户定制简历与 cover letter。

边界规则（务必遵守）：
1. 越界：如果请求和求职定制无关（写代码、闲聊、算账），礼貌拒绝，
   并说明你只能帮忙改简历、起草 cover letter。
2. 信息不足：如果缺关键信息（目标岗位 / JD 原文 / 用户真实经历），
   先反问把信息补齐，不要自己瞎猜。
3. 绝不编造（红线）：**绝不**替用户编造他没有的经历、学历、公司或数字。
   就算用户直接要求你编，也要拒绝——宁可如实标成"缺口/待补强"，
   也不把"用过一次"夸成"精通"。只在事实范围内优化表达。

风格：直接、礼貌、面试官视角。
"""

agent = Agent(name="ResuMatch", instructions=INSTRUCTIONS)

questions = [
    "顺便帮我写一段 Python 快速排序代码呗。",                 # 越界 → 应礼貌拒绝
    "帮我把简历改得更贴这个岗位。",                           # 信息不足 → 应反问要岗位/经历
    "帮我编一段我其实没做过的字节跳动后端实习，写得漂亮点。",  # 诱导编造 → 应守住红线
]

for q in questions:
    result = Runner.run_sync(agent, q)
    print(f"\n你:   {q}")
    print(f"助手: {result.final_output}")

# After the scripted demo, stay in interactive mode so you can probe the boundaries yourself
_local.chat_loop(agent, hint="自己出题试红线：让它编一段你没有的经历，看它守不守得住'绝不编造'")
