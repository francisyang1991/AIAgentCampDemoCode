"""
07 · Agent autonomous MCP calls — real model mode + offline rehearsal
==============================================================================
Run offline rehearsal:
    python 07_agent_autonomous_mcp.py

Run REAL autonomous Agent mode:
    export OPENAI_API_KEY="sk-..."
    python3 run_l5_demo.py --demo 07 --agent

What this demonstrates:
  - One Agent is given two MCP servers:
      1) Filesystem MCP: list_directory / read_file
      2) ResuMatch MCP: parse_jd / score_resume
  - In real Agent mode, the model chooses the MCP tools itself.
  - Without an OpenAI key, the script still runs an offline rehearsal that
    prints the same Agent loop and executes the same real MCP tools directly.

Why two modes:
  Local small models are often unreliable at function/tool calling. For a live
  class, the offline rehearsal proves the MCP plumbing; the real Agent mode is
  the one to use when you have a proper tool-calling model key.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

from agents.mcp import MCPServerStdio, create_static_tool_filter

ROOT = Path(__file__).resolve().parent
RESUME_DIR = ROOT / "sample_docs"
RESUMATCH_SERVER = ROOT / "01_minimal_mcp_server.py"

REAL_AGENT_INSTRUCTIONS = """你是求职助手 ResuMatch。你有两个 MCP Server：
- Filesystem MCP：只能 list_directory / read_file，用来读 sample_docs 里的 resume.md 和 jd.txt。
- ResuMatch MCP：parse_jd 解析 JD，score_resume 算匹配分。

必须按顺序自主调用工具：
1. list_directory 确认文件存在；
2. read_file 读取 resume.md 和 jd.txt；
3. parse_jd 从 JD 提取 required_skills；
4. score_resume 对照简历计算 match_score/matched/missing；
5. 最终回答必须引用 score_resume 的结果，不能自己重算或编造。
"""


def _has_real_openai_key() -> bool:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    return bool(key and key != "ollama")


def _tool_json(call_result) -> dict:
    try:
        return json.loads(call_result.content[0].text)
    except Exception:
        return {}


def _content_text(call_result) -> str:
    try:
        return call_result.content[0].text
    except Exception:
        return ""


async def _connect_servers():
    resumatch = MCPServerStdio(
        name="ResuMatch MCP",
        params={"command": sys.executable, "args": [str(RESUMATCH_SERVER)]},
    )
    filesystem = MCPServerStdio(
        name="Filesystem MCP",
        params={
            "command": "npx",
            "args": [
                "-y",
                "@modelcontextprotocol/server-filesystem",
                str(RESUME_DIR),
            ],
        },
        tool_filter=create_static_tool_filter(
            allowed_tool_names=["read_file", "list_directory"],
        ),
        client_session_timeout_seconds=30,
    )
    return filesystem, resumatch


async def _offline_rehearsal(fs_server, resumatch_server) -> None:
    print("\n[离线 Agent Loop 彩排] 没有使用模型，但每一步都是真 MCP 工具调用。")
    print("课堂讲法：这些就是 Agent 在真实模式下应该自主选择的工具步骤。")

    print("\nStep 1 · Agent 观察任务：用户要读取 resume.md / jd.txt 并计算匹配分")

    print("\nStep 2 · Agent 选择工具: filesystem.list_directory")
    listing = await fs_server.call_tool("list_directory", {"path": str(RESUME_DIR)})
    print("  output ->", _content_text(listing).replace("\n", " | "))

    print("\nStep 3 · Agent 选择工具: filesystem.read_file(resume.md)")
    resume_call = await fs_server.call_tool("read_file", {"path": str(RESUME_DIR / "resume.md")})
    resume = _content_text(resume_call)
    print(f"  output -> {len(resume)} chars")

    print("\nStep 4 · Agent 选择工具: filesystem.read_file(jd.txt)")
    jd_call = await fs_server.call_tool("read_file", {"path": str(RESUME_DIR / "jd.txt")})
    jd = _content_text(jd_call)
    print(f"  output -> {len(jd)} chars")

    print("\nStep 5 · Agent 选择工具: resumatch.parse_jd")
    parsed = await resumatch_server.call_tool("parse_jd", {"jd_text": jd})
    parsed_json = _tool_json(parsed)
    print("  output ->", parsed_json)

    print("\nStep 6 · Agent 选择工具: resumatch.score_resume")
    report = await resumatch_server.call_tool(
        "score_resume",
        {
            "resume_text": resume,
            "required_skills": parsed_json.get("required_skills", []),
        },
    )
    report_json = _tool_json(report)
    print("  output ->", report_json)

    print("\nStep 7 · Agent 最终回答（基于工具结果，不自己编）")
    print(
        "  匹配分：{score}；已匹配：{matched}；缺口：{missing}".format(
            score=report_json.get("match_score"),
            matched=", ".join(report_json.get("matched", [])),
            missing=", ".join(report_json.get("missing", [])),
        )
    )

    print(
        "\n要跑真实模型自主调用："
        "\n  export OPENAI_API_KEY='sk-...'"
        "\n  python3 run_l5_demo.py --demo 07 --agent"
    )


async def _real_agent_mode(fs_server, resumatch_server) -> None:
    from agents import Agent, Runner

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    agent = Agent(
        name="ResuMatch Autonomous MCP Agent",
        model=model,
        instructions=REAL_AGENT_INSTRUCTIONS,
        mcp_servers=[fs_server, resumatch_server],
    )

    question = (
        "sample_docs 目录里有 resume.md 和 jd.txt。"
        "请你自主调用 MCP 工具读取文件、解析 JD、计算匹配分，并列出缺口。"
    )
    print(f"\n[真实 Agent 自主调用模式] model={model}")
    result = await Runner.run(agent, question, max_turns=12)
    _print_agent_steps(result)
    print("\n最终回答：\n", result.final_output)


def _print_agent_steps(result) -> None:
    print("\n--- Agent Loop Trace ---")
    for index, item in enumerate(getattr(result, "new_items", []), 1):
        kind = type(item).__name__
        raw = getattr(item, "raw_item", None)
        if kind == "ToolCallItem":
            print(f"{index}. ToolCall  -> {getattr(raw, 'name', '?')} {getattr(raw, 'arguments', '')}")
        elif kind == "ToolCallOutputItem":
            output = str(getattr(item, "output", ""))
            if len(output) > 300:
                output = output[:300] + "..."
            print(f"{index}. ToolOut   -> {output}")
        elif kind == "MessageOutputItem":
            print(f"{index}. Message   -> model response")
        else:
            print(f"{index}. {kind}")


async def main() -> None:
    fs_server_cm, resumatch_server_cm = await _connect_servers()
    async with fs_server_cm as fs_server, resumatch_server_cm as resumatch_server:
        fs_tools = await fs_server.list_tools()
        res_tools = await resumatch_server.list_tools()
        print("已连接 Filesystem MCP 工具：", [t.name for t in fs_tools])
        print("已连接 ResuMatch MCP 工具：", [t.name for t in res_tools])

        wants_real_agent = os.getenv("RUN_AGENT_DEMO") == "1"
        if wants_real_agent and _has_real_openai_key():
            await _real_agent_mode(fs_server, resumatch_server)
        elif wants_real_agent:
            print("\n⚠️  真实 Agent 模式已开启，但没有检测到 OPENAI_API_KEY。")
            await _offline_rehearsal(fs_server, resumatch_server)
        else:
            await _offline_rehearsal(fs_server, resumatch_server)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except FileNotFoundError:
        print(
            "\n⚠️  没找到 npx（Node.js）。07 需要 filesystem MCP，所以需要 Node.js。\n"
            "   优先用 `python3 run_l5_demo.py --demo 07`；仍失败就安装 Node.js。"
        )
        raise SystemExit(1)
    except Exception as e:
        print(f"\n[失败] Agent autonomous MCP demo 没跑通（{type(e).__name__}：{e}）。")
        raise SystemExit(1)
