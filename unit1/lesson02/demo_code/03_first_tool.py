"""
03 · Your first tool —— let the Agent actually "do things" (function tool)
----------------------------------------------------------
Run:      python 03_first_tool.py

This is the core scene of the Agent Loop:
  your question → model decides "I need to look up what skills this role requires" → calls the get_role_keywords tool
              → SDK runs the tool, feeds the result back to the model → model uses the result to compare against your resume
@function_tool auto-generates the tool's schema from the type annotations + docstring.

★ Job-hunt theme: the tool first demonstrates the principle with a "hard-coded role-skills table"; the next demo (03b)
  swaps it for a real API that queries live job openings. First, see clearly "how a tool gets called".
"""

import _local  # noqa: F401 —— no key? auto-falls back to local Ollama; no Ollama? prints a hint
from agents import Agent, Runner, function_tool


@function_tool
def get_role_keywords(role: str) -> str:
    """Look up the common hard-skill keywords for a role, to compare against a resume and find gaps.

    Args:
        role: the target role, e.g. "数据分析师".
    """
    # In a real project this would query a role database / recruiting API; for the demo it's hard-coded
    table = {
        "数据分析师": "SQL、Python、统计、数据可视化、A/B 测试",
        "后端工程师": "Java 或 Go、数据库、微服务、缓存、高并发",
        "前端工程师": "JavaScript、React、TypeScript、CSS、前端工程化",
    }
    return table.get(role, f"{role}：暂无内置关键词，请补充岗位信息")


agent = Agent(
    name="ResuMatch",
    instructions="你是求职助手。需要某岗位的技能要求时调用 get_role_keywords，再对照用户简历指出『匹配上的』和『还差的』。",
    tools=[get_role_keywords],
)

result = Runner.run_sync(agent, "数据分析师一般要求哪些硬技能？我简历里只写了 Excel、SQL，差什么？")
print(result.final_output)

# Want to see which tools the Agent actually called, and how many steps it took? Uncomment the line below:
# _local.show_steps(result.new_items)

# Demo done —— stay in interactive mode to keep asking
_local.chat_loop(agent, hint="问问『后端工程师 / 前端工程师』要什么技能，看它怎么调用工具再对照简历")
