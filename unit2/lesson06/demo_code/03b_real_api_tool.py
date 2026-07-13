"""
03b · A real external-API tool — what an industrial-grade tool looks like
=========================================================================
Run:  python 03b_real_api_tool.py
Prereq:  pip install -r requirements.txt (includes httpx, tenacity)

Demos 01-03 return hand-written dicts, which is great for teaching the mechanics.
But a real ResuMatch tool looks like this ``search_jobs``:
  · it calls a real HTTP endpoint — Hacker News' public Algolia jobs API,
    **no API key required**;
  · that endpoint *will* fail: timeout, rate-limit (429), network down — the tool
    has to survive it, mid-chain, without crashing the whole run;
  · it uses tenacity for **exponential-backoff retry** (only on transient errors,
    never on a 4xx that won't get better);
  · it returns **structured data** (a Pydantic model -> dict) with a ``source``
    field, not a blob of free text, so downstream code (and the model) can trust it.

★ This is the "real tool" template for the flagship topic ResuMatch. Swap the HN
  call for any real endpoint in your own project (a jobs board / a company careers API);
  the retry + timeout + structured-error skeleton carries over unchanged.

Offline-safe: if HN can't be reached after retries, the tool falls back to a small
built-in sample and marks source="offline-sample" — so the whole chain still runs
on a plane / behind a firewall, and it honestly tells the model the data is a
sample. This is exactly the chain-error-recovery the lesson is about.
"""
from __future__ import annotations

import httpx
from pydantic import BaseModel
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

import _local  # noqa: F401 — no key auto-falls-back to local Ollama; see _local.py
from agents import Agent, Runner, function_tool

# Public HN jobs search (Algolia). tags=job restricts results to job posts.
_HN_API = "https://hn.algolia.com/api/v1/search"

# Offline fallback sample (used ONLY when the live call truly fails; clearly labelled).
_OFFLINE = {
    "python": [
        "Senior Python Engineer @ Acme (Remote)",
        "Backend Engineer (Python/Django) @ Globex",
        "ML Platform Engineer — Python @ Initech",
    ],
    "react": [
        "Frontend Engineer (React/TS) @ Hooli (Remote)",
        "Senior React Developer @ Umbrella",
    ],
}
_OFFLINE_DEFAULT = [
    "Software Engineer @ Sample Corp (Remote)",
    "Full-Stack Developer @ Demo Inc",
]


class JobSearch(BaseModel):
    """One structured job-search result. Downstream (scorer / UI / another Agent)
    can read fields directly instead of parsing prose."""
    keyword: str
    jobs: list[str] = []
    count: int = 0
    source: str = ""        # "hn" / "offline-sample" — tells the caller how trustworthy
    status: str = "ok"      # "ok" / "error"
    message: str = ""       # human-readable note when status=error or source=offline-sample


# Retry ONLY transient network errors (timeout / connection). A 4xx like a bad
# request is permanent and must not be retried.
@retry(
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.TransportError)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.4, max=3),
    reraise=True,
)
def _fetch_from_hn(keyword: str) -> JobSearch:
    """Actually hit HN's jobs API. Timeouts / network blips get backed-off up to 3x."""
    r = httpx.get(
        _HN_API,
        params={"query": keyword, "tags": "job", "hitsPerPage": 5},
        headers={"User-Agent": "ResuMatch-demo/1.0"},
        timeout=4.0,
    )
    if r.status_code == 429:
        # Rate-limited: raise a transient error so tenacity backs off and retries.
        raise httpx.TransportError("rate limited (429)")
    r.raise_for_status()  # other 5xx also raise -> caught by fallback below
    hits = r.json().get("hits", [])
    jobs = [h.get("title") or h.get("story_title") or "(untitled)" for h in hits]
    jobs = [j for j in jobs if j][:5]
    return JobSearch(keyword=keyword, jobs=jobs, count=len(jobs), source="hn")


def job_search(keyword: str) -> JobSearch:
    """Pure-function version (no @function_tool): live fetch + offline fallback.
    Extracted so it can be unit-tested / called offline without going through an Agent."""
    kw = (keyword or "").strip()
    if not kw:
        return JobSearch(keyword=kw, status="error", message="错误：搜索关键词为空。")
    try:
        result = _fetch_from_hn(kw)
        if not result.jobs:
            return JobSearch(keyword=kw, status="ok", source="hn", count=0,
                             message=f"没有搜到与『{kw}』相关的在招岗位，换个关键词试试。")
        return result
    except Exception as e:
        # Retries exhausted (usually offline / rate-limited) -> fall back to sample.
        sample = _OFFLINE.get(kw.lower(), _OFFLINE_DEFAULT)
        return JobSearch(
            keyword=kw, jobs=sample, count=len(sample), source="offline-sample",
            message=f"实时接口连不上（{type(e).__name__}），这是内置样例，仅供演示。",
        )


@function_tool
def search_jobs(keyword: str) -> dict:
    """Search real open job posts by keyword (role or skill).

    Calls Hacker News' public jobs API (no key). On timeout/429/network failure it
    retries with backoff, then falls back to a built-in sample marked
    source="offline-sample" so the chain never crashes.

    Args:
        keyword: A role/skill keyword, e.g. "python", "react", "ml engineer".
    """
    return job_search(keyword).model_dump()


agent = Agent(
    name="ResuMatch",
    instructions=(
        "你是 ResuMatch 求职助手。需要在招岗位时调用 search_jobs。"
        "规则：①岗位只能来自工具返回值，绝不自己编；"
        "②若返回 source 为 'offline-sample'，要向用户说明这是样例数据；"
        "③用中文简洁列出岗位。"
    ),
    tools=[search_jobs],
)


def main():
    # First verify the *tool itself* (no model) — this is a real endpoint, so we
    # can see the structured data directly.
    demo = job_search("python")
    print(f"[自检] 工具直跑 search_jobs('python') => 命中 {demo.count} 条，"
          f"数据源={demo.source}")
    for j in demo.jobs[:3]:
        print(f"        · {j}")

    for q in ["帮我搜 Python 相关的在招岗位", "有没有 React 前端的岗位？"]:
        print(f"\n你:   {q}")
        try:
            print("助手:", Runner.run_sync(agent, q, max_turns=4).final_output)
        except Exception as e:
            print(f"[离线] 连不上模型（{type(e).__name__}）。"
                  "但上面[自检]已证明工具能独立取到真实/样例数据。")


if __name__ == "__main__":
    main()
    _local.chat_loop(agent, hint="搜搜 python / react / go 的岗位；断网时它会自动回退样例并诚实标注")
