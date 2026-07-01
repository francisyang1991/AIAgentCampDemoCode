"""
04 · Few-shot examples + an explicit output format (flagship theme: ResuMatch).
------------------------------------------------------------------------------
Run:    python 04_few_shot_format.py

Two techniques that make the output "obedient":
  · Few-shot: drop one or two "input -> output" examples into the instructions and the model copies the pattern.
  · Output format: pin the exact shape you want (here, JSON with fixed fields) so downstream code can parse it directly.

Same teaching goal, job-hunt flavor: take one raw resume experience and "re-order it into a structured bullet" for a target role.
"""

import _local  # noqa: F401 — no key? auto-fallback to local Ollama (see _local.py)
from agents import Agent, Runner

# Drop one example (few-shot) straight into the instructions, and require JSON output
INSTRUCTIONS = """你是"简历要点重排器"。把用户的一条原始经历，按目标岗位改写成一条结构化简历要点。

只输出 JSON，字段固定为：bullet（动词开头的简历要点）、metric（量化结果，没有就填 ""）、
keywords（命中目标岗位的关键词列表）、gap（这条还差什么，没有就填 ""）。
不要输出 JSON 以外的任何文字。
红线：只重排和改写用户**已有**的经历，**绝不**替他添加没说过的数字或技能。

示例：
输入：目标岗位=数据分析师；经历=帮运营团队整理过用户问卷，做了张报表
输出：{"bullet": "整理并分析用户问卷数据，输出可视化报表支持运营决策", "metric": "", "keywords": ["数据分析", "问卷", "报表"], "gap": "缺具体样本量与业务影响数字，建议补强"}
"""

agent = Agent(name="ResumeBulletFormatter", instructions=INSTRUCTIONS)

result = Runner.run_sync(
    agent,
    "目标岗位=后端开发工程师；经历=用 Python 写过一个小接口，给同学的项目用",
)
print(result.final_output)

# After the one-shot demo, stay in interactive mode to keep re-ordering
# (each item is independent, so turning off session memory keeps it cleaner)
_local.chat_loop(agent, hint="再给一条『目标岗位+经历』，看它转成结构化要点 JSON", use_session=False)

# Going further: to have the SDK validate/parse the result into an object, use output_type
# (with a pydantic model); lesson 4 and beyond dig into that. Here we focus on few-shot + the format contract itself.
