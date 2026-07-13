"""
01 · Two local tools — one Agent holds several tools, watch it pick on demand
=============================================================================
Run:  python 01_two_local_tools.py
Prereq:  pip install -r requirements.txt, plus OPENAI_API_KEY (or a local Ollama).

In Lesson 4 you wrote a single tool. In a real project (ResuMatch, our job-hunt
assistant) an Agent carries several tools at once. The key question: with many
tools available, how does the model pick the right one? The answer is each tool's
name + description — the model never sees your function body, only the schema.

Here we hang TWO local tools on one Agent:
  · parse_jd     — read a JD, extract the hard requirements (structured)
  · search_jobs  — search real open roles by keyword
Then we ask two different questions and watch it pick the right tool each time.
Offline / no key → prints "which tool this should have hit", never crashes.
"""

import _local  # noqa: F401 — no key auto-falls-back to local Ollama; see _local.py
from agents import Agent, Runner, function_tool

# A tiny keyword dictionary standing in for a real skills taxonomy. In production
# parse_jd would call an LLM or an NLP service; here we keep it deterministic so
# the demo is reproducible offline and never fabricates requirements.
_SKILL_KEYWORDS = [
    "Python", "SQL", "Java", "Go", "React", "TypeScript", "Docker",
    "Kubernetes", "AWS", "机器学习", "深度学习", "NLP", "数据分析",
    "PyTorch", "TensorFlow", "LLM", "RAG", "Agent", "Spark", "Kafka",
]


@function_tool
def parse_jd(jd_text: str) -> dict:
    """Read a raw job description (JD) and extract the employer's hard requirements.

    This is the first link of the ResuMatch chain: it turns free-form JD prose into
    a structured dict whose ``must_have`` field downstream tools (score_resume) can
    consume directly — never guessing from text.

    Args:
        jd_text: The raw JD text pasted by the user.

    Returns:
        dict with stable fields:
          status: "ok" | "error"
          role: best-guess role title (str)
          must_have: list[str]  — hard-requirement keywords found in the JD
          nice_to_have: list[str] — softer / bonus keywords
    """
    text = (jd_text or "").strip()
    if not text:
        # Friendly, model-readable error — never raise a bare exception.
        return {"status": "error", "role": "", "must_have": [], "nice_to_have": [],
                "message": "错误：JD 文本为空，请粘贴职位描述再试。"}

    lower = text.lower()
    hits = [kw for kw in _SKILL_KEYWORDS if kw.lower() in lower]
    # Split by a crude "必须/要求" vs "加分/优先" heuristic: keywords appearing after
    # a "加分"/"优先"/"nice" marker are treated as nice_to_have.
    nice_markers = ("加分", "优先", "bonus", "nice", "plus")
    cut = min([text.find(m) for m in nice_markers if text.find(m) != -1] or [len(text)])
    must_have, nice_to_have = [], []
    for kw in hits:
        pos = lower.find(kw.lower())
        (nice_to_have if pos >= cut else must_have).append(kw)

    # Guess a role title from the first line, else fall back.
    role = text.splitlines()[0][:40] if text.splitlines() else "未知职位"
    return {"status": "ok", "role": role,
            "must_have": must_have or hits, "nice_to_have": nice_to_have}


@function_tool
def search_jobs(keyword: str) -> dict:
    """Search real open job posts by keyword (e.g. 'python', 'ml engineer').

    In this file it returns a small offline sample so the demo is self-contained;
    demo 03b upgrades this exact tool to hit the real Hacker News jobs API with
    retry + timeout + offline fallback. Kept here so the model has a *second*,
    clearly-different tool to choose between.

    Args:
        keyword: A role/skill keyword to search open positions for.

    Returns:
        dict with fields: status, source ('offline-sample'), jobs (list[str]).
    """
    kw = (keyword or "").strip()
    if not kw:
        return {"status": "error", "source": "offline-sample", "jobs": [],
                "message": "错误：搜索关键词为空。"}
    sample = [
        f"[{kw}] Senior {kw} Engineer @ Acme (Remote)",
        f"[{kw}] {kw} Developer @ Globex (Beijing)",
        f"[{kw}] Backend Engineer ({kw}) @ Initech (Shanghai)",
    ]
    return {"status": "ok", "source": "offline-sample", "jobs": sample}


# One Agent, two tools. instructions only say "pick the right one" — we do not
# decide for it. Descriptions above are what actually drive the choice.
agent = Agent(
    name="ResuMatch",
    instructions=(
        "你是 ResuMatch 求职助手。解析 JD 硬性要求用 parse_jd，"
        "搜在招岗位用 search_jobs。选对工具后用中文简洁回答。"
    ),
    tools=[parse_jd, search_jobs],
)


def main():
    # Two questions that should hit two different tools.
    questions = [
        "帮我解析这份 JD：后端工程师，要求 Python、SQL、Docker，熟悉 AWS 加分。",
        "帮我搜一下 Python 相关的在招岗位。",
    ]
    for q in questions:
        try:
            result = Runner.run_sync(agent, q, max_turns=4)
            print(f"\n你:   {q}")
            print(f"助手: {result.final_output}")
        except Exception as e:
            # No key / offline → graceful degrade, explain what should happen.
            print(f"\n你:   {q}")
            print(f"[离线] 无法连模型（{type(e).__name__}）。")
            print("     正常情况下：第 1 句命中 parse_jd，第 2 句命中 search_jobs。")


if __name__ == "__main__":
    main()
    _local.chat_loop(agent, hint="贴段 JD 让它解析，或让它搜某个技能的岗位，看它在两把工具间挑对哪一把")
