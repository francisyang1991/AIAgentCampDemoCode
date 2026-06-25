"""
06 · Structured output —— make the Agent return "fields" instead of a wall of prose
----------------------------------------------------------------
Run:      python 06_structured_output.py

In the earlier demos the Agent returned a block of text — nice for humans, but **a program can't use it directly**.
In real projects, an Agent's output often feeds the next step (store in a database / score it / trigger another tool),
and that's where you need **structured output**: give the Agent an `output_type=Pydantic model`,
and `result.final_output` is directly an object whose fields you can read with `.field`.

★ Job-hunt theme: parse a JD into a structured JDProfile (title / hard skills / minimum years / nice-to-haves).
  This is exactly the first step of ResuMatch's later "resume match score" —— lesson 4 turns it into a real tool.
"""

import _local  # noqa: F401 —— no key? auto-falls back to local Ollama
from pydantic import BaseModel
from agents import Agent, Runner


# (1) Define what you want the "output to look like" —— just a plain Pydantic model
class JDProfile(BaseModel):
    title: str                 # job title
    must_have: list[str]       # required hard skills (a list the program can iterate over)
    min_years: int | None      # minimum years (a number, None if unspecified)
    nice_to_have: list[str]    # nice-to-haves


# (2) Attach the model to output_type, and the Agent is "constrained" to output by field
agent = Agent(
    name="JDParser",
    instructions="你是 JD 解析器。从用户给的 JD 文本里抽取：职位名、硬性要求技能、最低年限、加分项，按字段输出。",
    output_type=JDProfile,
)

SAMPLE_JD = "Hiring a Data Analyst: requires 3+ years of experience, strong SQL and Python, familiar with A/B testing and data visualization; experience with Tableau or Looker is a plus."

result = Runner.run_sync(agent, f"解析这段 JD：\n{SAMPLE_JD}")

profile = result.final_output            # ← this is a JDProfile object, not a string!
print("拿到的是对象：", type(profile).__name__)
print(profile)
print("\n程序可以直接取字段用：")
print("  职位       :", profile.title)
print("  硬技能(列表) :", profile.must_have)
print("  最低年限   :", profile.min_years)
