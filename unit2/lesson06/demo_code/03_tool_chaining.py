"""
03 · Tool chaining — one tool's structured output feeds the next tool's input
=============================================================================
Run:  python 03_tool_chaining.py

In a multi-step task, tools often need to pass values to each other. The trick:
have a tool return a structured dict with a *stable field*, and let the next tool
take that field as input. Returning a dict beats returning a sentence — the model
can pull out the exact field instead of "guessing" it from prose.

Here the stable field is ``must_have``:
    parse_jd(jd) -> {must_have: [...]}  ──►  score_resume(resume, must_have)
Offline / no key → prints the values it would have passed, never crashes.
"""

import _local  # noqa: F401 — no key auto-falls-back to local Ollama; see _local.py
from agents import Agent, Runner, function_tool

_SKILL_KEYWORDS = [
    "Python", "SQL", "Java", "Go", "React", "TypeScript", "Docker",
    "Kubernetes", "AWS", "机器学习", "深度学习", "NLP", "数据分析",
    "PyTorch", "TensorFlow", "LLM", "RAG", "Agent", "Spark", "Kafka",
]


@function_tool
def parse_jd(jd_text: str) -> dict:
    """Parse a JD and return the employer's hard requirements as a stable field.

    The returned ``must_have`` list is the value that gets handed to score_resume.
    We return a dict (not a sentence) precisely so the next tool can take the field
    verbatim rather than re-extracting it from text.

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
    """Score a resume against must_have — must_have comes straight from parse_jd.

    This is the core value-passing link: the ``must_have`` field returned by
    parse_jd is taken here as the second argument. Scoring is done in code, so the
    number and the gap are real, not model-invented.

    Args:
        resume_text: The candidate's resume text.
        must_have: Hard-requirement keywords, i.e. parse_jd()["must_have"].

    Returns:
        dict: {status, score:int, matched: list[str], missing: list[str]}
    """
    if not must_have:
        return {"status": "error", "score": 0, "matched": [], "missing": [],
                "message": "错误：must_have 为空，请先调用 parse_jd 拿到硬性要求。"}
    lower = (resume_text or "").lower()
    matched = [kw for kw in must_have if kw.lower() in lower]
    missing = [kw for kw in must_have if kw.lower() not in lower]
    score = round(100 * len(matched) / len(must_have))
    return {"status": "ok", "score": score, "matched": matched, "missing": missing}


agent = Agent(
    name="ResuMatch",
    instructions=(
        "你是 ResuMatch 求职助手。先用 parse_jd 拿到 must_have，"
        "再把这个 must_have 连同简历传给 score_resume 打分，"
        "最后用中文报出匹配分和缺口 missing。"
    ),
    tools=[parse_jd, score_resume],
)

JD = "算法工程师\n要求：Python、PyTorch、NLP、SQL。"
RESUME = "两年算法经验，精通 Python 与 PyTorch，做过文本分类。"
QUESTION = f"JD：{JD}\n我的简历：{RESUME}\n对照打个匹配分，告诉我缺什么。"


def main():
    try:
        result = Runner.run_sync(agent, QUESTION, max_turns=8)
        print(f"你:   {QUESTION}")
        print(f"助手: {result.final_output}")
    except Exception as e:
        print(f"你:   {QUESTION}")
        print(f"[离线] 无法连模型（{type(e).__name__}）。")
        print("     正常情况下：parse_jd(JD) → must_have=[Python,PyTorch,NLP,SQL]")
        print("                 → score_resume(简历, must_have)")
        print("                 → {score:50, missing:[NLP,SQL]}")
        print("                 → 回答『匹配 50 分，缺 NLP、SQL』")


if __name__ == "__main__":
    main()
    _local.chat_loop(agent, hint="换个 JD + 简历，看它先 parse_jd 拿 must_have，再传给 score_resume 打分")
