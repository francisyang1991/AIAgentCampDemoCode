"""
01 · Hello Agent —— the simplest Agent: create + run
------------------------------------------------
Run:      python 01_hello_agent.py
Setup:    pip install -r requirements.txt; set OPENAI_API_KEY, or just run with Ollama installed (zero cost, see README)

★ The thread running through this whole lesson: starting today, we'll build a [job-hunt assistant ResuMatch]
  together, step by step —— it tailors your resume highlights + cover letter to different JDs (job descriptions).
  This lesson first brings it "to life": remember two of the three core pieces —— Agent (the entity) + Runner (the run engine).
"""

import _local  # noqa: F401 —— no key? auto-falls back to local Ollama; no Ollama? prints a hint (see _local.py in this dir)
from agents import Agent, Runner

# 1) Create an Agent —— all you need is name + instructions
agent = Agent(
    name="ResuMatch",
    instructions="你是 ResuMatch 求职助手，简洁地回答求职与简历相关的问题。",
)

# 2) Run it with Runner (single-turn conversation, run_sync = synchronous blocking version)
result = Runner.run_sync(agent, "用一句话介绍你能帮我做什么")

# 3) Get the final answer
print(result.final_output)

# Demo done —— stay in interactive mode to keep asking
_local.chat_loop(agent, hint="问问它能怎么帮你找工作 / 改简历，体验最简单的 Agent")
