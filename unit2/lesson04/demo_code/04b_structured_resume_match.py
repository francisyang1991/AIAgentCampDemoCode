"""
04b · Structured output in practice — a tool returns Pydantic, not free text (flagship: ResuMatch)
==============================================================================
Run:  python 04b_structured_resume_match.py

Lesson 4 says "tools should return structured data". Here we drive it home with the
**ResuMatch job-hunt assistant** — the biggest demand cluster from the lesson-1 survey
(job-seeking / resume). Two tools:
  · parse_jd(jd_text)        ->  JDProfile (extract hard skills / years from a JD, structured)
  · score_resume(resume,jd)  ->  MatchReport (score / matched / gaps — computed in CODE, not guessed)

★ Two idiomatic takeaways:
  1) A tool returns a **Pydantic model** (-> dict): clean fields a downstream consumer can use
     programmatically (front-end display, hand-off to another Agent, evaluation in Lesson 12).
  2) "Keyword coverage" is a **deterministic number computed in code**, not estimated by the LLM —
     this is the trust foundation of the job-seeking project, and the seed of Lesson 12's
     "no-fabrication evaluation": if a program can compute it, don't let the LLM guess.

The tools are deterministic and run offline; only the final "agent ties it together" step
needs the model (Ollama fallback).
"""
from __future__ import annotations

from pydantic import BaseModel, Field

import _local  # noqa: F401 —— no key: auto local Ollama; no Ollama: prints a hint (see _local.py)
from agents import Agent, Runner, function_tool

# A minimal "skill lexicon". A real project would use a larger / configurable one; this is enough to demo programmatic extraction.
_SKILL_LEXICON = [
    "python", "java", "c++", "go", "sql", "react", "typescript", "pytorch",
    "tensorflow", "docker", "kubernetes", "aws", "gcp", "llm", "rag", "agent",
    "fastapi", "pandas", "spark", "airflow", "mlops", "nlp", "ci/cd",
]


class JDProfile(BaseModel):
    """What the employer actually wants, structured out of a JD."""
    title: str = ""
    must_have: list[str] = Field(default_factory=list)  # hard skills that hit the lexicon
    min_years: int | None = None                        # minimum years, if parseable


class MatchReport(BaseModel):
    """Resume vs JD match report. The score is **computed in code**, not estimated by the model."""
    score: int                       # 0-100, = matched hard skills / JD hard skills
    matched: list[str]               # hard skills the resume hits
    missing: list[str]               # required by the JD but missing from the resume (= gaps, the valuable part)
    note: str = ""


def _skills_in(text: str) -> list[str]:
    """Find lexicon skills that appear in the text (deterministic, no model call).

    Note: this is the most naive "substring hit". Its known limitation is itself a good
    teaching point — it can't tell "used Docker" from "never touched Docker" (negations hit too).
    🚀 Extra Challenge: improve it with word boundaries / negation detection / semantic matching,
    and write one eval proving you fixed it.
    """
    low = text.lower()
    return [s for s in _SKILL_LEXICON if s in low]


@function_tool
def parse_jd(jd_text: str) -> dict:
    """Extract the job title, hard skills and minimum years from JD text; returns a structured JDProfile.

    Args:
        jd_text: the raw job description (JD).
    """
    import re
    skills = _skills_in(jd_text)
    title = jd_text.strip().splitlines()[0][:40] if jd_text.strip() else ""
    m = re.search(r"(\d+)\s*\+?\s*(?:年|years?)", jd_text.lower())
    years = int(m.group(1)) if m else None
    return JDProfile(title=title, must_have=skills, min_years=years).model_dump()


@function_tool
def score_resume(resume_text: str, jd_must_have: list[str]) -> dict:
    """Score a resume by keyword-coverage against the JD's hard-skill list and list the gaps.

    Args:
        resume_text: the raw resume text.
        jd_must_have: the JD's required hard skills (from parse_jd's must_have).
    """
    have = set(_skills_in(resume_text))
    need = [s.lower() for s in jd_must_have]
    matched = [s for s in need if s in have]
    missing = [s for s in need if s not in have]
    score = round(100 * len(matched) / len(need)) if need else 0
    note = "覆盖率 = 命中硬技能 / JD 硬技能（程序计算，可复现，不依赖模型估计）"
    return MatchReport(score=score, matched=matched, missing=missing, note=note).model_dump()


agent = Agent(
    name="ResuMatch",
    instructions=(
        "你是求职教练。先用 parse_jd 解析 JD，再用 score_resume 算匹配分。"
        "**匹配分与缺口一律以 score_resume 返回的 score / missing 为准，绝不自己重新计算**"
        "（程序算过的数字比你估的可信）。然后基于结构化结果给建议。"
        "红线：绝不编造用户没有的经历或技能；缺口就如实标为'待补强'，不要替他写假的。"
    ),
    tools=[parse_jd, score_resume],
)

SAMPLE_JD = "Senior ML Engineer\nWe need 5+ years of experience, strong Python, PyTorch, RAG and Docker, and familiarity with AWS."
# Note: the resume only lists what it HAS, never what it lacks (RAG / AWS simply don't appear -> correctly shown as gaps).
SAMPLE_RESUME = "3 years of experience, mainly Python backend development; trained models with PyTorch; shipped to production with Docker."


def main():
    # Tool self-check (deterministic, always runs, no model needed).
    print("[自检] JD 硬技能:", _skills_in(SAMPLE_JD))
    print("[自检] 简历技能:", _skills_in(SAMPLE_RESUME))
    need = _skills_in(SAMPLE_JD)
    have = set(_skills_in(SAMPLE_RESUME))
    print(f"[自检] 程序算的覆盖率 = {round(100*len([s for s in need if s in have])/len(need))}% "
          f"缺口 = {[s for s in need if s not in have]}")

    q = f"这是 JD：\n{SAMPLE_JD}\n\n这是我的简历：\n{SAMPLE_RESUME}\n\n帮我看看匹配度和缺口。"
    print(f"\n你:   （贴了一段 JD 和简历，问匹配度）")
    try:
        print("助手:", Runner.run_sync(agent, q, max_turns=6).final_output)
    except Exception as e:
        print(f"[离线] 连不上模型（{type(e).__name__}）。但上面[自检]已证明：覆盖率是程序算出来的确定值，不靠模型。")


if __name__ == "__main__":
    main()
    _local.chat_loop(agent, hint="贴一段真实 JD + 你的经历，让它算匹配分、列缺口（它不会替你编没有的经历）")
