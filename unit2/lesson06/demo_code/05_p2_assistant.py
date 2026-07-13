"""
05 · P2 assistant template — local tools + one MCP tool working together
========================================================================
Run:  python 05_p2_assistant.py        (type exit to quit)
This is your P2 starting point: >=1 local tool + 1 MCP tool, cooperating in one
multi-turn conversation, with memory.

P2 acceptance = local function tools + an MCP tool, both wired up, cooperating in
a single conversation. This ResuMatch template ships:
  · local tools  parse_jd / score_resume / suggest_rewrite — your @function_tool chain
  · MCP tool     — the public filesystem Server (@modelcontextprotocol/server-filesystem)
                   giving write_file / read_file / list within a sandbox directory.
                   The last step (fs_write_report) writes the match report to disk.
  · SQLiteSession — multi-turn memory; conversation context is kept automatically.

Offline-friendly (important): missing node/npx, missing mcp package, or missing key
all degrade to "local tools only" — still runs, never crashes. So a classroom with
no network, or a machine without Node, still works.
  ↓↓↓ Student edit points: swap INSTRUCTIONS for your topic, swap the local tools ↓↓↓
"""

import _local  # noqa: F401 — no key auto-falls-back to local Ollama; see _local.py
import asyncio
import os
import shutil

from agents import Agent, Runner, SQLiteSession, function_tool

# ── A sandbox dir for the MCP filesystem Server (it can only touch here — safe) ──
SANDBOX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "p2_workspace")
os.makedirs(SANDBOX, exist_ok=True)
# Seed a sample JD file so the very first turn can "read a file".
with open(os.path.join(SANDBOX, "sample_jd.txt"), "w", encoding="utf-8") as f:
    f.write("后端工程师\n要求：Python、SQL、Docker、Kubernetes、AWS。\n加分：Go、Kafka。\n")


_SKILL_KEYWORDS = [
    "Python", "SQL", "Java", "Go", "React", "TypeScript", "Docker",
    "Kubernetes", "AWS", "机器学习", "深度学习", "NLP", "数据分析",
    "PyTorch", "TensorFlow", "LLM", "RAG", "Agent", "Spark", "Kafka",
]


# ── Local tools: plain Python functions; @function_tool auto-builds the schema ──
@function_tool
def parse_jd(jd_text: str) -> dict:
    """Parse a JD into structured hard requirements (must_have).

    Args:
        jd_text: The raw JD text.

    Returns:
        dict: {status, role, must_have: list[str], nice_to_have: list[str]}
    """
    text = (jd_text or "").strip()
    if not text:
        return {"status": "error", "role": "", "must_have": [], "nice_to_have": [],
                "message": "错误：JD 文本为空。"}
    lower = text.lower()
    hits = [kw for kw in _SKILL_KEYWORDS if kw.lower() in lower]
    role = text.splitlines()[0][:40] if text.splitlines() else "未知职位"
    return {"status": "ok", "role": role, "must_have": hits, "nice_to_have": []}


@function_tool
def score_resume(resume_text: str, must_have: list[str]) -> dict:
    """Score a resume against a JD's must_have list (from parse_jd).

    Args:
        resume_text: The candidate's resume text.
        must_have: Hard-requirement keywords, i.e. parse_jd()["must_have"].

    Returns:
        dict: {status, score:int, matched: list[str], missing: list[str]}
    """
    if not must_have:
        return {"status": "error", "score": 0, "matched": [], "missing": [],
                "message": "错误：must_have 为空，请先用 parse_jd 解析 JD。"}
    lower = (resume_text or "").lower()
    matched = [kw for kw in must_have if kw.lower() in lower]
    missing = [kw for kw in must_have if kw.lower() not in lower]
    return {"status": "ok", "score": round(100 * len(matched) / len(must_have)),
            "matched": matched, "missing": missing}


@function_tool
def suggest_rewrite(missing: list[str], resume_text: str) -> dict:
    """Suggest resume bullets to close the gap (missing, from score_resume).

    Args:
        missing: Keywords the resume is missing, i.e. score_resume()["missing"].
        resume_text: The current resume text (for light context).

    Returns:
        dict: {status, bullets: list[str]}
    """
    if not missing:
        return {"status": "ok", "bullets": ["简历已覆盖所有硬性要求，无需补充。"]}
    return {"status": "ok", "bullets": [
        f"补一条体现『{kw}』的经历：做了什么、量化产出。" for kw in missing]}


# ↓↓↓ Edit here: replace with your own topic's role ↓↓↓
INSTRUCTIONS = """你是 ResuMatch 求职助手。
- 能做：用 parse_jd 解析 JD、score_resume 对照简历打分、suggest_rewrite 给改写建议；
        用文件系统工具把最终匹配报告写进沙箱（如 write_file 到 report.md），也能读/列文件。
- 不做：访问沙箱以外的路径（越权请求礼貌拒绝）；数字不能自己编，必须来自工具返回。
- 流程：先 parse_jd 拿 must_have → score_resume 打分拿 missing → suggest_rewrite 给建议
        → 用户要求时用 write_file 把报告落盘到沙箱。
- 风格：简洁；工具报错（status=error）时换路或如实告知用户。
"""
# ↑↑↑ Edit here ↑↑↑

LOCAL_TOOLS = [parse_jd, score_resume, suggest_rewrite]


def _mcp_available() -> bool:
    """Can we enable MCP? Need npx on PATH and agents.mcp importable (Py3.10+ & mcp)."""
    if shutil.which("npx") is None:
        return False
    try:
        from agents.mcp import MCPServerStdio  # noqa: F401  probe importability only
        return True
    except Exception:
        return False


async def run_with_mcp():
    """Full version: local tools + MCP filesystem tool cooperating."""
    from agents.mcp import MCPServerStdio  # confirmed importable in _mcp_available

    # Launch the public filesystem Server over stdio, locked to SANDBOX only.
    async with MCPServerStdio(
        name="filesystem",
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", SANDBOX],
        },
        # First run downloads the package, so widen the startup timeout.
        client_session_timeout_seconds=30,
    ) as fs_server:
        agent = Agent(
            name="ResuMatch-P2",
            instructions=INSTRUCTIONS,
            tools=LOCAL_TOOLS,          # local tools
            mcp_servers=[fs_server],    # MCP tool (read/write/list files)
        )
        session = SQLiteSession("p2_resumatch")  # multi-turn memory
        print("已启用：本地工具(parse_jd/score_resume/suggest_rewrite) + MCP 文件系统工具。")
        print(f"沙箱目录：{SANDBOX}")
        await chat_loop(agent, session)


def run_local_only(reason: str):
    """Degraded version: local tools only, so offline / no-node still runs."""
    agent = Agent(
        name="ResuMatch-P2(local-only)",
        instructions=INSTRUCTIONS,
        tools=LOCAL_TOOLS,
    )
    session = SQLiteSession("p2_resumatch")
    print(f"[降级] {reason} → 仅本地工具模式（MCP 部分跳过）。")
    asyncio.run(chat_loop(agent, session))


async def chat_loop(agent, session):
    """Shared multi-turn loop; both modes use it."""
    print("开始对话（输入 exit / 退出 结束）")
    print("试试：① 读 sample_jd.txt 并解析  ② 对照我的简历打分：我会 Python、SQL、Docker")
    print("      ③ 把匹配报告写进 report.md")
    while True:
        try:
            user = input("\n你:   ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if user in {"exit", "quit", "退出"}:
            break
        if not user:
            continue
        try:
            result = await Runner.run(agent, user, session=session, max_turns=10)
            print("助手:", result.final_output)
        except Exception as e:
            # Model / tool trouble is caught here — a friendly line, never a crash.
            print(f"助手: [这次没成功：{type(e).__name__}]，换个说法或稍后再试。")


def main():
    if _mcp_available():
        try:
            asyncio.run(run_with_mcp())
        except Exception as e:
            # MCP failing to start (download / port / perms) must not crash either.
            run_local_only(f"MCP 启动失败（{type(e).__name__}）")
    else:
        run_local_only("未检测到 npx 或 MCP 依赖（需 Node + Python 3.10+ + mcp 包）")


if __name__ == "__main__":
    main()
