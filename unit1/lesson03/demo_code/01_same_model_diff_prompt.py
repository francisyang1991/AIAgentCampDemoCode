"""
01 · Same model, different prompt = different assistant (flagship theme: ResuMatch).
------------------------------------------------------------------------------------
Run:    python 01_same_model_diff_prompt.py
Setup:  pip install -r requirements.txt; set OPENAI_API_KEY, or run with Ollama
        installed (zero-cost, offline — see README and _local.py).

Ask the SAME question to two agents whose only difference is `instructions`,
and watch how far the answers diverge. The model is identical; the gap is
entirely in the prompt you give it (the System Prompt).
Course-wide theme: ResuMatch — re-order resume bullets for a JD, draft a cover letter.
"""

import _local  # noqa: F401 — no key? auto-fallback to local Ollama (see _local.py)
from agents import Agent, Runner

QUESTION = "我想投一个数据分析师的岗位，我做过用户调研和 Excel 报表，帮我把简历改得更贴这个岗位。"

# A: weak one-line prompt — no role, no boundaries
agent_a = Agent(
    name="GenericBot",
    instructions="你是一个求职助手。",
)

# B: structured strong prompt — role + boundaries + style
agent_b = Agent(
    name="ResuMatch",
    instructions="""你是"ResuMatch 求职教练"，帮求职者针对某个具体岗位重排简历要点。
- 能做：读懂目标岗位要什么、把用户已有经历按岗位重排改写、指出匹配点与缺口
- 风格：先用一句话点明"我打算怎么改、为什么更贴这个岗位"，再给带量化的要点
- 红线：**绝不编造**用户没有的经历 / 数字；信息不足时先反问，不硬猜""",
)

for label, agent in [("A · 弱提示词", agent_a), ("B · 强提示词", agent_b)]:
    result = Runner.run_sync(agent, QUESTION)
    print(f"\n===== {label} =====")
    print(result.final_output)

print("\n----------------------------------------")
print("同一个模型、同一个问题，换一段 instructions，助手就换了一个。")

# After the demo, stay interactive with the strong-prompt assistant to compare live
_local.chat_loop(agent_b, hint="拿强提示词的求职助手再问几句，对比上面弱版的差别")
