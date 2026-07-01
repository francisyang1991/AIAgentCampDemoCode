"""
02 · Anatomy of a good System Prompt — the five blocks (flagship theme: ResuMatch).
-----------------------------------------------------------------------------------
Run:    python 02_anatomy.py

A good `instructions` usually has five blocks:
  (1) Role  (2) Capabilities  (3) Boundaries  (4) Style  (5) Format
Follow this skeleton and the prompt stays clean. The ResuMatch prompt below is
assembled from those five blocks — same structure as p1_skeleton/prompts_resume.py
(trimmed here for the classroom demo).
"""

import _local  # noqa: F401 — no key? auto-fallback to local Ollama (see _local.py)
from agents import Agent, Runner

# Five blocks, one paragraph each — copy this skeleton when you write your own
INSTRUCTIONS = """【角色】你是"ResuMatch 求职教练"，帮求职者针对某个具体岗位定制简历要点。

【能力】你可以：
- 读懂目标岗位 / JD 想要的硬技能与关键词
- 拿用户**已有**的经历，按这个岗位重新排序、用岗位的语言改写措辞
- 指出"匹配上了什么"和"还差什么"（缺口清单）

【边界】你不做：
- **绝不编造**用户没有的经历 / 学历 / 数字（这是求职选题的红线，宁可标缺口）
- 在信息不足时硬猜，缺目标岗位或真实经历先反问清楚

【风格】像改过几百份简历的资深教练：直接、可量化、面试官视角；改动经历前先用一句话说清打算怎么改、为什么。

【格式】先给「匹配概览」(3 条最强匹配 + 3 条主要缺口)，再给「按此岗位重排的简历要点」(动词开头 + 量化结果 + 岗位关键词)。
"""

agent = Agent(name="ResuMatch", instructions=INSTRUCTIONS)

result = Runner.run_sync(
    agent,
    "我想投数据分析师。我做过用户调研、写过 Excel 月报、还帮团队整理过问卷数据，帮我重排简历要点。",
)
print(result.final_output)

# After the demo, stay interactive so you can keep asking
_local.chat_loop(agent, hint="把你的目标岗位和已有经历告诉它，试试这套 5 块结构的求职助手")
