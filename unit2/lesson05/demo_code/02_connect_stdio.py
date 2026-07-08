"""
02 · Connect the ResuMatch Server into an Agent — stdio transport
==============================================================================
Run:     python 02_connect_stdio.py
Needs:   01_minimal_mcp_server.py in this folder (launched here as a subprocess)
         No model needed for the default smoke test.

This script does three things (mirrors the P4 "接入" slides):
  1) start 01's server as a subprocess via MCPServerStdio (command + args)
  2) list which tools that server exposes (list_tools)
  3) call parse_jd -> score_resume directly through MCP, so the demo is stable

The MCP client is ASYNC, so the whole flow lives in async def main(), launched
with asyncio.run(main()). This is the easiest trap of the lesson — remember
await and asyncio.run.

ResuMatch theme: 01 exposes parse_jd + score_resume over MCP. Here we first
call parse_jd on a JD, then feed required_skills into score_resume to get a
reproducible match_score — the exact tool chain from the slides, except the
tools live in another process reachable by any MCP client.

Optional: set RUN_AGENT_DEMO=1 to also try the Agent version after the stable
MCP smoke test. Local models may not reliably call tools, so this is not the
default classroom path.
"""

import asyncio
import os
import sys
from pathlib import Path

from agents.mcp import MCPServerStdio

# The JD + resume we ask about. The resume states only what it HAS; gaps (RAG,
# AWS) simply do not appear, so they surface honestly as "missing".
JD_TEXT = (
    "Senior ML Engineer. 5+ years experience. Strong Python, PyTorch, "
    "RAG and Docker; AWS and Kubernetes a plus; SQL for data work."
)
RESUME_TEXT = (
    "3 years Python backend with FastAPI; trained a recommender in PyTorch; "
    "ships to production with Docker; comfortable with SQL."
)

SERVER_PATH = Path(__file__).with_name("01_minimal_mcp_server.py")


async def main():
    # command + args == typing `python 01_minimal_mcp_server.py`.
    # The SDK launches it as a subprocess and talks over stdio.
    async with MCPServerStdio(
        name="ResuMatch Server",
        params={"command": sys.executable, "args": [str(SERVER_PATH)]},
    ) as server:
        # 1) Inspect the tools this Server gives us (proves MCP is wired up).
        tools = await server.list_tools()
        print("这个 MCP Server 暴露的工具：")
        for t in tools:
            print(f"  - {t.name}: {t.description}")

        # 2) Stable smoke test: call the MCP tools directly. This proves the
        #    server, schemas, transport, and structured returns all work without
        #    relying on a model's tool-calling behavior.
        parsed = await server.call_tool("parse_jd", {"jd_text": JD_TEXT})
        skills = _tool_json(parsed).get("required_skills", [])
        report = await server.call_tool(
            "score_resume",
            {"resume_text": RESUME_TEXT, "required_skills": skills},
        )

        print("\n稳定链路：parse_jd -> score_resume")
        print("  parse_jd     ->", _tool_json(parsed))
        print("  score_resume ->", _tool_json(report))

        if os.getenv("RUN_AGENT_DEMO") == "1":
            await _try_agent_demo(server)


def _tool_json(call_result):
    """Pull the JSON dict out of an MCP call_tool result (content[0].text)."""
    import json
    try:
        return json.loads(call_result.content[0].text)
    except Exception:
        return {}


async def _try_agent_demo(server):
    import _local  # noqa: F401 — auto local Ollama when no key (see _local.py)
    from agents import Agent, Runner

    agent = Agent(
        name="ResuMatch",
        instructions=(
            "你是求职助手 ResuMatch。先用 parse_jd 解析 JD 拿到 required_skills，"
            "再把它喂给 score_resume 算匹配分。"
            "匹配分与缺口一律以 score_resume 返回的 match_score / missing 为准，"
            "绝不自己重算。红线：绝不编造用户没有的经历或技能。"
        ),
        mcp_servers=[server],
    )
    question = (
        f"这是目标岗位 JD：\n{JD_TEXT}\n\n"
        f"这是我的简历：\n{RESUME_TEXT}\n\n"
        "帮我算一下匹配分，并列出我还差哪些硬技能。"
    )
    print("\n[可选 Agent 模式] 让模型自己决定调用 MCP 工具：")
    result = await Runner.run(agent, question, max_turns=8)
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
