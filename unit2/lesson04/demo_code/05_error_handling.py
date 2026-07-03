"""
05 · Failure handling — when a tool fails, don't let the whole run crash
------------------------------------------------------
Run:  python 05_error_handling.py

Tools will hit failures: the role isn't in the library, the JD can't be parsed,
the network times out... The wrong move is to raise an exception, which kills the
whole run. The right move:

  return {"status": "error", "message": "no data for this role, please confirm the role name"}

Return a structured error + actionable info, and the model can respond gracefully:
switch strategy, or ask the user — instead of crashing.

★ Single course theme: the ResuMatch job-hunt assistant.
  · get_role_keywords — returns a structured error when the role is missing
    (no crash, no made-up data).
  · search_jobs (advanced) — actually makes one HTTP call to a public API to find
    live postings; shows try/except + timeout + offline fallback: when it can't
    connect, it falls back to a built-in sample and labels it honestly.
"""

import html
import re

import _local  # noqa: F401 —— no key: auto local Ollama; no Ollama: prints a hint (see _local.py)
import httpx
from agents import Agent, Runner, function_tool


@function_tool
def get_role_keywords(role: str) -> dict:
    """Look up the common hard-skill keywords for a target role; call when you need a role's skill requirements.

    Args:
        role: target job title, e.g. "Data Analyst", "Backend Engineer".
    """
    table = {
        "Data Analyst": ["SQL", "Python", "statistics", "data visualization"],
        "Backend Engineer": ["Java or Go", "databases", "microservices", "caching"],
    }
    if role not in table:
        # Don't raise! Return a structured error + tell the model what it can do.
        return {
            "status": "error",
            "message": (
                f"No keywords for '{role}'. Supported roles: Data Analyst, "
                "Backend Engineer. Please ask the user to confirm the role title."
            ),
        }
    return {"status": "ok", "role": role, "skills": table[role]}


# ---------- Advanced: a tool that really calls an external API (no key needed, offline fallback) ----------
# Offline sample shown when the live API is unreachable (clearly labelled, never faked).
_OFFLINE = (
    "· PYTHON DEVS - REMOTE OK | a startup is hiring 5-10 Python engineers\n"
    "· Senior Data Analyst | Oakland, CA | a healthcare org is hiring\n"
    "(offline sample, shown when the live API can't be reached)"
)


@function_tool
def search_jobs(keyword: str) -> str:
    """Search Hacker News "who is hiring" comments for real, live postings matching a keyword (no API key needed).

    Args:
        keyword: a role / skill keyword, e.g. "python remote", "data analyst".
    """
    try:
        resp = httpx.get(
            "https://hn.algolia.com/api/v1/search",
            params={"query": f"{keyword} hiring", "tags": "comment", "hitsPerPage": 4},
            timeout=6,  # Timeout: a real tool must set one — never wait forever.
        )
        resp.raise_for_status()
        hits = resp.json().get("hits", [])
        lines = []
        for h in hits[:4]:
            # The live API returns "dirty" text with HTML tags and escapes; clean it for the model.
            text = re.sub(r"<[^>]+>", " ", h.get("comment_text") or "")
            text = html.unescape(text).strip().replace("\n", " ")
            if text:
                lines.append("· " + text[:120])
        return "\n".join(lines) if lines else f"没找到和『{keyword}』相关的招聘帖，换个关键词试试。"
    except (httpx.HTTPError, KeyError) as e:
        # Degrade honestly: fall back to the offline sample and label it, instead of crashing or faking a hit.
        return f"（实时搜索失败 {type(e).__name__}，给离线参考）\n{_OFFLINE}"


agent = Agent(
    name="ResuMatch",
    instructions=(
        "你是求职助手。需要岗位技能时调用 get_role_keywords，想看在招岗位时调用 search_jobs。"
        "如果工具返回 status 为 error，不要编造数据——"
        "把原因友好地告诉用户，并请他确认或换一个岗位。"
    ),
    tools=[get_role_keywords, search_jobs],
)

# Deliberately ask for a role the library doesn't support, to trigger the structured error branch.
result = Runner.run_sync(agent, "产品经理这个岗位一般要求哪些硬技能？")
print("最终回答（注意它没有胡编，而是优雅地说明并反问）：")
print(result.final_output)

print("\n--- 工具返回了 error，模型据此换了策略 ---")
_local.show_steps(result.new_items)

# After the demo, stay in interactive mode to keep chatting.
_local.chat_loop(
    agent,
    hint="故意问个不支持的岗位看它怎么优雅处理 error；或搜 'python remote' 看真去查的在招岗位（断网会自动回退离线样例）",
)
