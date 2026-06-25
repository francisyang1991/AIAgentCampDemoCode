"""
03b · Real API tool —— the tool is no longer hard-coded; it really searches "live job openings"
----------------------------------------------------------------
Run:      python 03b_real_api_tool.py

The only difference from 03: 03's tool returns a hard-coded skill table; here it **really sends an HTTP request**,
searching the Hacker News "Who is hiring" threads for real openings related to a keyword
(Algolia's public search API — free, no key, stable). This is what a tool really looks like:

  · really calls an external API   → httpx.get(...)
  · the returned data is "dirty"   → has HTML tags / escape chars, must be cleaned into text the model can read
  · it can time out, it can fail   → timeout + try/except
  · degrade honestly when no data  → fall back to an offline sample and label it; never pretend it found something

★ This is one of the prototype tools of the ResuMatch job-hunt assistant. Lessons 4 and 6 cover "tool robustness"
  (retries, rate limiting, structured returns) in depth; here we just show "what one real tool looks like".
"""

import html
import re

import _local  # noqa: F401 —— no key? auto-falls back to local Ollama and prints a hint
import httpx
from agents import Agent, Runner, function_tool

# Fallback for when the network / API is down (clearly labeled "offline reference" — no lying to the user)
_OFFLINE = (
    "· PYTHON DEVS - REMOTE OK | a startup is hiring 5-10 Python engineers\n"
    "· Senior Data Analyst | Oakland, CA | a healthcare org is hiring\n"
    "(the above is an offline sample, shown when the live API can't be reached)"
)


@function_tool
def search_jobs(keyword: str) -> str:
    """Search the Hacker News hiring threads for real openings related to a keyword (no API key needed).

    Args:
        keyword: a role / skill keyword, e.g. "python remote", "data analyst".
    """
    try:
        resp = httpx.get(
            "https://hn.algolia.com/api/v1/search",
            params={"query": f"{keyword} hiring", "tags": "comment", "hitsPerPage": 4},
            timeout=6,
        )
        resp.raise_for_status()
        hits = resp.json().get("hits", [])
        lines = []
        for h in hits[:4]:
            # The real API returns "dirty" text with HTML tags and escape chars — it must be cleaned
            text = re.sub(r"<[^>]+>", " ", h.get("comment_text") or "")
            text = html.unescape(text).strip().replace("\n", " ")
            if text:
                lines.append("· " + text[:120])
        return "\n".join(lines) if lines else f"Found no hiring posts related to '{keyword}', try another keyword."
    except (httpx.HTTPError, KeyError) as e:
        # A real tool must handle failure: degrade to the offline sample and label it honestly, instead of crashing or making things up
        return f"(live search failed {type(e).__name__}, here's an offline reference)\n{_OFFLINE}"


agent = Agent(
    name="ResuMatch",
    instructions="你是求职助手。用户想看某方向在招岗位时调用 search_jobs，再用中文简要点评这些岗位适合什么背景的人投、看重哪些技能。",
    tools=[search_jobs],
)

result = Runner.run_sync(agent, "帮我看看现在有哪些招 python 远程开发的岗位？")
print(result.final_output)

# Want to see which tool it called and what it returned? Uncomment the next line:
# _local.show_steps(result.new_items)

_local.chat_loop(agent, hint="搜搜 『data analyst / react / machine learning』 的岗位——这次是真的去查的")
