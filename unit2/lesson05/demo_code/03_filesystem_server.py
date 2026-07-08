"""
03 · Connect a ready-made official Server (filesystem) — read-only + sandboxed
==============================================================================
Run:     python 03_filesystem_server.py
Needs:
  - Node.js / npx on your machine (this Server is written in Node, run via npx).
    Check with `npx --version`; if missing, install from nodejs.org.
  - The first npx run downloads the package (cached after, works offline later).
  - No model needed for the default smoke test.

Key point (the "CONNECT 接现成" half of L5): read_file / list_directory are NOT
written by us. They come from the officially maintained
@modelcontextprotocol/server-filesystem. "Install it and use it — don't write
your own 80-line file reader" is the value of the MCP ecosystem (the L5 hook).

Two safety moves straight from the slides:
  1) SANDBOX — the last npx arg is the only reachable directory. The Server
     refuses anything outside it. We point it at sample_docs/.
  2) READ-ONLY — the filesystem Server can also write_file / delete_file. We
     clamp it with create_static_tool_filter(allowed_tool_names=[...]) so the
     Agent only ever sees read_file + list_directory. This is exactly the
     homework's "限制为只读" requirement, and the least-privilege habit.

ResuMatch theme: the real use case — read your ACTUAL resume / JD files over
MCP. The sample files live in sample_docs/ (resume.md + jd.txt); this script
lists the dir, reads both files, and reports matched skills vs. gaps. Swap in
your own resume folder path to use it for real.

Optional: set RUN_AGENT_DEMO=1 to also try the Agent version after the stable
MCP smoke test. Local models may not reliably call tools, so this is not the
default classroom path.
"""

import asyncio
import os
from pathlib import Path

from agents.mcp import MCPServerStdio, create_static_tool_filter

# Only this dir is reachable = sandbox. Points at sample_docs/ (resume.md + jd.txt).
# Absolute path so it works no matter where the Server subprocess is spawned.
# To read YOUR resume, replace this with your own resume folder path.
RESUME_DIR = Path(__file__).parent / "sample_docs"

SKILL_BANK = [
    "python", "sql", "aws", "gcp", "docker", "kubernetes", "pytorch",
    "tensorflow", "rag", "llm", "agent", "fastapi", "pandas", "spark",
    "mlops",
]


async def main():
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
        # Read-only clamp: the Agent will only ever see these two tools, even
        # though the Server also exposes write_file / delete_file. Least privilege.
        tool_filter=create_static_tool_filter(
            allowed_tool_names=["read_file", "list_directory"],
            # or, to block instead of allow-list:
            # blocked_tool_names=["write_file", "edit_file", "move_file"],
        ),
        # First npx run downloads the package; allow a generous timeout.
        client_session_timeout_seconds=30,
    ) as server:
        # After the filter, only read_file + list_directory remain visible.
        tools = await server.list_tools()
        print(f"过滤后 Agent 可见的工具（只读白名单）：{[t.name for t in tools]}")

        listing = await server.call_tool("list_directory", {"path": str(RESUME_DIR)})
        resume = await server.call_tool("read_file", {"path": str(RESUME_DIR / "resume.md")})
        jd = await server.call_tool("read_file", {"path": str(RESUME_DIR / "jd.txt")})

        resume_text = _content_text(resume)
        jd_text = _content_text(jd)
        jd_skills = [s for s in SKILL_BANK if s in jd_text.lower()]
        matched = [s for s in jd_skills if s in resume_text.lower()]
        missing = [s for s in jd_skills if s not in resume_text.lower()]

        print("\n稳定链路：list_directory -> read_file(resume.md/jd.txt)")
        print("  目录内容 ->", _content_text(listing).replace("\n", " | "))
        print("  resume.md 字数 ->", len(resume_text))
        print("  jd.txt 字数     ->", len(jd_text))
        print("  JD 技能        ->", jd_skills)
        print("  已匹配         ->", matched)
        print("  还缺           ->", missing)

        if os.getenv("RUN_AGENT_DEMO") == "1":
            await _try_agent_demo(server)


def _content_text(call_result):
    try:
        return call_result.content[0].text
    except Exception:
        return ""


async def _try_agent_demo(server):
    import _local  # noqa: F401 — auto local Ollama when no key (see _local.py)
    from agents import Agent, Runner

    agent = Agent(
        name="ResuMatch Assistant",
        instructions=(
            "你是求职助手。用户的简历和 JD 都以文件形式放在沙箱目录里。"
            "先用 list_directory 看目录，再用 read_file 读 resume.md 和 jd.txt 的真实内容，"
            "然后对照指出'已匹配的硬技能'和'还差的缺口'。"
            "红线：只依据文件里真实写到的内容，绝不编造用户没有的经历或技能。"
        ),
        mcp_servers=[server],
    )
    print("\n[可选 Agent 模式] 让模型自己决定调用 filesystem MCP：")
    result = await Runner.run(
        agent,
        "目录里有我的简历 resume.md 和目标岗位 jd.txt，"
        "帮我读一下，对照说说我匹配上了什么、还差什么。",
        max_turns=8,
    )
    print(result.final_output)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except FileNotFoundError:
        # npx / Node not installed -> the subprocess can't start.
        print(
            "\n⚠️  没找到 npx（Node.js）。本 demo 用的是 Node 写的官方 filesystem Server。\n"
            "   装 Node.js（nodejs.org）后 `npx --version` 验证，再重跑本文件。\n"
            "   （其余 demo 先跑 `python3 run_l5_demo.py --demo 01` 也可以。）"
        )
        raise SystemExit(1)
    except Exception as e:
        print(f"\n[失败] filesystem demo 没跑通（{type(e).__name__}：{e}）。"
              "检查 Node/npx、网络和 sample_docs 文件。")
        raise SystemExit(1)
