"""
04 · Structured returns — make the return value reliable "raw material" for the model
--------------------------------------------------------
Run:  python 04_structured_return.py

A tool's return value is the input to the model's next step. So:
  · return a dict, not a free-text sentence
  · include a status field (ok / error) so the model sees success/failure at a glance
  · give the model only the fields it needs; don't dump the whole raw API response back

Two tools here show how structured returns chain together:
  score_resume   -> compute match score + gaps (structured)
  suggest_focus  -> take the previous tool's "gaps" and advise what to shore up first

★ Single course theme: the ResuMatch job-hunt assistant. It returns match score /
  matched / gaps, which a downstream tool can consume directly — that is exactly the
  value of structured returns.
"""

import _local  # noqa: F401 —— no key: auto local Ollama; no Ollama: prints a hint (see _local.py)
from agents import Agent, Runner, function_tool


@function_tool
def score_resume(resume_text: str, jd_skills: str) -> dict:
    """Score a resume by keyword-coverage against a role's hard skills and list the gaps.

    Args:
        resume_text: the raw resume text.
        jd_skills: comma-separated hard skills the role requires, e.g. "python,sql,docker".
    """
    need = [s.strip().lower() for s in jd_skills.split(",") if s.strip()]
    if not need:
        return {"status": "error", "message": "no JD skills given, cannot score"}
    have = [s for s in need if s in resume_text.lower()]
    missing = [s for s in need if s not in resume_text.lower()]
    score = round(100 * len(have) / len(need))
    # Return only the fields the model needs; keep the shape clean.
    return {"status": "ok", "score": score, "matched": have, "missing": missing}


@function_tool
def suggest_focus(missing_skills: list[str]) -> dict:
    """Given the list of resume gaps, advise which skill to shore up first.

    Args:
        missing_skills: hard skills not yet covered (from score_resume's missing).
    """
    if not missing_skills:
        return {"status": "ok", "advice": "all hard skills covered; focus on quantified impact"}
    first = missing_skills[0]
    return {"status": "ok", "advice": f"shore up '{first}' first: ship a small project using it"}


agent = Agent(
    name="ResuMatch",
    instructions=(
        "你是求职教练。先用 score_resume 算匹配分和缺口，"
        "再把 missing 传给 suggest_focus 拿补强建议，最后用中文综合成一句话回答。"
        "红线：绝不编造用户简历里没有的经历或技能。"
    ),
    tools=[score_resume, suggest_focus],
)

result = Runner.run_sync(
    agent,
    "我的简历写了 python 和 sql。岗位要求 python,sql,docker,aws。匹配度多少、我先补哪个？",
)
print("最终回答：")
print(result.final_output)

print("\n--- 多个工具按结构化结果串起来 ---")
_local.show_steps(result.new_items)

# After the demo, stay in interactive mode to keep chatting.
_local.chat_loop(agent, hint="换组简历/技能，看两个工具如何按结构化的缺口列表接力")
