"""
01 · Function Calling basics — watch the model "request" a tool call
------------------------------------------------------------
Run:  python 01_function_calling_basics.py

The one thing to see here:
  the model never executes a function itself. It only "requests" a call to
  get_role_keywords(role=...); the SDK runs your function for real, feeds the
  result back, and the model answers from it.

We run once, then print result.new_items — inside you can see the
tool_call the model raised and the tool_output it got back.
That is one turn of the Agent Loop.

★ Single course theme: the ResuMatch job-hunt assistant. Here a tiny job tool
  get_role_keywords (role -> that role's hard skills) makes "how the model
  requests a tool call" concrete.
"""

import _local  # noqa: F401 —— no key: auto local Ollama; no Ollama: prints a hint (see _local.py)
from agents import Agent, Runner, function_tool


@function_tool
def get_role_keywords(role: str) -> str:
    """Look up the hard skills a target role values, to compare against a resume and find gaps.

    Args:
        role: target job title, e.g. "Data Analyst".
    """
    # A real project would hit a role library / hiring API; demo uses a hard-coded table.
    table = {
        "Data Analyst": "SQL, Python, statistics, data visualization, A/B testing",
        "Backend Engineer": "Java or Go, databases, microservices, caching, concurrency",
    }
    return table.get(role, f"{role}: no built-in keywords yet")


agent = Agent(
    name="ResuMatch",
    instructions="你是求职助手。需要某岗位的技能要求时调用 get_role_keywords，再用中文给求职者建议。",
    tools=[get_role_keywords],
)

result = Runner.run_sync(agent, "数据分析师（Data Analyst）一般要求哪些硬技能？我该往哪些方向准备？")

print("最终回答：")
print(result.final_output)

# Key part: see which steps the model took internally (print only the essentials per step, not the whole object).
_local.show_steps(result.new_items)

# After the demo, stay in interactive mode to keep chatting.
_local.chat_loop(agent, hint="再问几个岗位要什么技能，体会模型怎么发起工具调用")
