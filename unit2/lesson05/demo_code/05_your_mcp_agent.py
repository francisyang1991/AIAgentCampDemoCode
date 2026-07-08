"""
05 · Your MCP assistant (P-stage starting point) — TWO servers on one Agent
==============================================================================
Run:     python 05_your_mcp_agent.py
Needs:   01_minimal_mcp_server.py in this folder (your own ResuMatch Server);
         Node.js / npx for the official filesystem Server;
         no model needed for the default smoke test.

This is the seed of your P-stage skeleton and the high point of L5: "自建" and
"接入" converge on ONE Agent (the P4 slide "把自建 Server 当子进程接进 Agent" +
the P6 "ResuMatch 落地" split):

  · CONNECT — official filesystem Server (read-only, sandboxed): reading files
    is generic I/O someone already maintains. We do NOT write a file reader.
  · BUILD   — your own ResuMatch Server from 01 (parse_jd + score_resume): the
    scoring is proprietary business logic you make into a Server so a chat
    client / plugin / batch CLI can all reuse the SAME scoring.

Both servers are attached to one script. The stable classroom path calls MCP
tools directly:
  read_file (fs)  ->  parse_jd (yours)  ->  score_resume (yours)  ->  gaps.

Optional: set RUN_AGENT_DEMO=1 to also try a SINGLE Agent with
mcp_servers=[fs, resumatch]. Local models may not reliably call tools, so this
is not the default classroom path.

That "~70% your own tools + ~30% ready-made third-party Server" split is the
production ratio the slides quote — this file is a minimal instance of it.

Your turn (adapt to your own topic):
  1) point RESUME_DIR at your real resume folder (reads YOUR resume/JD);
  2) change INSTRUCTIONS to your project's role (job-hunt sample given here);
  3) swap 01's tools for your project's proprietary logic (keep the shape);
  4) keep the filesystem (or any official) Server for generic I/O.

Offline behavior (course bar): if Node/npx is missing we transparently run with
only the ResuMatch Server and read sample files directly from disk, so the demo
still produces the same deterministic result.
"""

import asyncio
import os
import sys
from pathlib import Path

from agents.mcp import MCPServerStdio, create_static_tool_filter

# Point this at YOUR resume folder to run it for real. Defaults to sample_docs/.
RESUME_DIR = Path(__file__).parent / "sample_docs"
SERVER_PATH = Path(__file__).with_name("01_minimal_mcp_server.py")

INSTRUCTIONS = """你是求职助手 ResuMatch，手上有两个 MCP Server：
- 文件系统 Server（只读）：用 list_directory / read_file 读沙箱里的 resume.md、jd.txt。
- ResuMatch Server（你自建）：用 parse_jd 解析 JD 拿 required_skills，再喂给 score_resume 算匹配分。
流程：先读文件 → parse_jd → score_resume → 给出匹配分与缺口清单。
匹配分与缺口一律以 score_resume 返回的 match_score / missing 为准，绝不自己重算。
红线：只依据文件真实写到的内容，绝不编造用户没有的经历或技能。"""


def _tool_json(call_result):
    """Pull the JSON dict out of an MCP call_tool result (content[0].text)."""
    import json
    try:
        return json.loads(call_result.content[0].text)
    except Exception:
        return {}


async def _run_with_both(fs_server, resumatch_server):
    """Stable path: filesystem MCP + ResuMatch MCP in one deterministic chain."""
    if fs_server is not None:
        print("\n稳定链路：filesystem.read_file -> parse_jd -> score_resume")
        listing = await fs_server.call_tool("list_directory", {"path": str(RESUME_DIR)})
        resume_call = await fs_server.call_tool("read_file", {"path": str(RESUME_DIR / "resume.md")})
        jd_call = await fs_server.call_tool("read_file", {"path": str(RESUME_DIR / "jd.txt")})
        print("  filesystem.list_directory ->", _content_text(listing).replace("\n", " | "))
        resume = _content_text(resume_call)
        jd = _content_text(jd_call)
    else:
        print("\n稳定链路：direct file read -> parse_jd -> score_resume")
        resume = (RESUME_DIR / "resume.md").read_text(encoding="utf-8")
        jd = (RESUME_DIR / "jd.txt").read_text(encoding="utf-8")

    parsed = await resumatch_server.call_tool("parse_jd", {"jd_text": jd})
    skills = _tool_json(parsed).get("required_skills", [])
    report = await resumatch_server.call_tool(
        "score_resume", {"resume_text": resume, "required_skills": skills}
    )
    print("  parse_jd     ->", _tool_json(parsed))
    print("  score_resume ->", _tool_json(report))

    if os.getenv("RUN_AGENT_DEMO") == "1":
        await _try_agent_demo(fs_server, resumatch_server)


async def main():
    # BUILD side: your own ResuMatch Server (01), as a subprocess.
    async with MCPServerStdio(
        name="ResuMatch Server",
        params={"command": sys.executable, "args": [str(SERVER_PATH)]},
    ) as resumatch_server:
        # CONNECT side: official filesystem Server, read-only + sandboxed.
        try:
            async with MCPServerStdio(
                name="Filesystem Server",
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
            ) as fs_server:
                print("已接入两个 Server：Filesystem（只读）+ ResuMatch（自建）。")
                await _run_with_both(fs_server, resumatch_server)
        except FileNotFoundError:
            # No Node/npx: degrade gracefully to ResuMatch-only (still full MCP).
            print("⚠️  没找到 npx（Node.js），跳过文件系统 Server，"
                  "仅用自建 ResuMatch Server 跑（读文件改由脚本直接完成）。")
            await _run_with_both(None, resumatch_server)


def _content_text(call_result):
    try:
        return call_result.content[0].text
    except Exception:
        return ""


async def _try_agent_demo(fs_server, resumatch_server):
    import _local  # noqa: F401 — auto local Ollama when no key (see _local.py)
    from agents import Agent, Runner

    servers = [s for s in (fs_server, resumatch_server) if s is not None]
    agent = Agent(
        name="MyMCPAssistant",
        instructions=INSTRUCTIONS,
        mcp_servers=servers,
    )
    print("\n[可选 Agent 模式] 让模型自己跨两个 MCP Server 编排：")
    result = await Runner.run(
        agent,
        "沙箱目录里有我的简历 resume.md 和目标岗位 jd.txt。"
        "帮我读出来，解析 JD、算匹配分，并列出我还差哪些硬技能。",
        max_turns=12,
    )
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
