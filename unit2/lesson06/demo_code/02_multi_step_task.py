"""
02 · Multi-step task — one question, several tools chained (watch the ReAct loop)
================================================================================
Run:  python 02_multi_step_task.py

Demo 01 was "one sentence -> one tool". This is "one sentence -> parse -> score ->
suggest": the model decides the order itself and loops several times before it
answers. That loop is ReAct — think, call a tool, read the result, think again.

The star of this file: use ``result.new_items`` to print exactly which steps it
took, so you can *see* the loop turn. Offline / no key → prints the steps it would
have taken, never crashes.
"""

import _local  # noqa: F401 — no key auto-falls-back to local Ollama; see _local.py
from agents import Agent, Runner, function_tool

# ── Shared, model-independent scoring logic (also reused by demo 03) ──
_SKILL_KEYWORDS = [
    "Python", "SQL", "Java", "Go", "React", "TypeScript", "Docker",
    "Kubernetes", "AWS", "机器学习", "深度学习", "NLP", "数据分析",
    "PyTorch", "TensorFlow", "LLM", "RAG", "Agent", "Spark", "Kafka",
]


@function_tool
def parse_jd(jd_text: str) -> dict:
    """Read a raw JD and extract the employer's hard requirements (structured).

    First link of the chain. Returns a dict whose ``must_have`` field feeds
    straight into score_resume — the value being passed along the chain.

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
    """Score a resume against a JD's must-have list — by code, not model guessing.

    Consumes ``must_have`` produced by parse_jd (the core value-passing link) and
    returns a numeric match score plus the concrete gap (missing keywords).

    Args:
        resume_text: The candidate's resume text.
        must_have: Hard-requirement keywords, typically parse_jd()["must_have"].

    Returns:
        dict: {status, score:int, matched: list[str], missing: list[str]}
    """
    if not must_have:
        return {"status": "error", "score": 0, "matched": [], "missing": [],
                "message": "错误：must_have 为空，请先用 parse_jd 解析 JD。"}
    lower = (resume_text or "").lower()
    matched = [kw for kw in must_have if kw.lower() in lower]
    missing = [kw for kw in must_have if kw.lower() not in lower]
    score = round(100 * len(matched) / len(must_have))
    return {"status": "ok", "score": score, "matched": matched, "missing": missing}


@function_tool
def suggest_rewrite(missing: list[str], resume_text: str) -> dict:
    """Given the gap (missing keywords), suggest resume bullets to close it.

    Last link of the chain — turns the earlier results into something the user can
    actually paste into their resume. Consumes score_resume()["missing"].

    Args:
        missing: Keywords the resume is missing, from score_resume()["missing"].
        resume_text: The current resume text (for light context).

    Returns:
        dict: {status, bullets: list[str]}
    """
    if not missing:
        return {"status": "ok", "bullets": ["简历已覆盖所有硬性要求，无需补充。"]}
    bullets = [
        f"补一条体现『{kw}』的项目经历：用 {kw} 做了什么、量化产出（如提速 X%/服务 Y 用户）。"
        for kw in missing
    ]
    return {"status": "ok", "bullets": bullets}


agent = Agent(
    name="ResuMatch",
    instructions=(
        "你是 ResuMatch 求职助手。可用工具：parse_jd 解析 JD、"
        "score_resume 对照简历打分、suggest_rewrite 给改写建议。"
        "一步步来：先 parse_jd 拿 must_have，再 score_resume 打分并拿 missing，"
        "最后用 suggest_rewrite 给建议，用中文汇报分数、缺口和改写要点。"
    ),
    tools=[parse_jd, score_resume, suggest_rewrite],
)

JD = "后端工程师，要求 Python、SQL、Docker、Kubernetes、AWS。"
RESUME = "三年后端经验，熟悉 Python 和 SQL，用过 Docker 部署服务。"
QUESTION = f"这是 JD：{JD}\n这是我的简历：{RESUME}\n帮我打个匹配分，缺什么，怎么补？"


def main():
    try:
        # Give max_turns room so it can loop several times.
        result = Runner.run_sync(agent, QUESTION, max_turns=10)
        print(f"你:   {QUESTION}")
        print(f"助手: {result.final_output}\n")

        # ↓↓↓ the star: print every step of this run ↓↓↓
        _local.show_steps(result.new_items)
    except Exception as e:
        print(f"你:   {QUESTION}")
        print(f"[离线] 无法连模型（{type(e).__name__}）。")
        print("     正常情况下它会连调多步：")
        print("       parse_jd(JD) → must_have=[Python,SQL,Docker,Kubernetes,AWS]")
        print("       score_resume(简历, must_have) → score=60, missing=[Kubernetes,AWS]")
        print("       suggest_rewrite(missing, 简历) → 两条补 K8s / AWS 的 bullet")
        print("       → 回答『匹配 60 分，缺 Kubernetes/AWS，建议补两条经历』")


if __name__ == "__main__":
    main()
    _local.chat_loop(agent, hint="换个 JD + 简历，看它怎么一步步解析、打分、给改写建议")
