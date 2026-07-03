"""
03 · Same feature, two ways to write it — bad tool vs good tool
------------------------------------------------------
Run:  python 03_good_vs_bad_tool.py

The feature is identical (score a resume against a role's skills), but how you
write it decides how well the model can use it:

  Bad:  vague name (f1), no description, unclear params (a, b), returns free text
        -> the model doesn't know when to call it, and has to guess how to parse the result

  Good: clear docstring, type hints, returns a structured dict with a status field
        -> the model calls it in the right situations and reads the values directly

Give both tools to the agent and watch which one it prefers — and uses correctly.

★ Single course theme: the ResuMatch job-hunt assistant. A job-scenario contrast:
  score_resume(resume_text, jd_skills) is clear  vs  f1(a, b) is vague.
"""

import _local  # noqa: F401 —— no key: auto local Ollama; no Ollama: prints a hint (see _local.py)
from agents import Agent, Runner, function_tool


# ---------- BAD tool ----------
@function_tool
def f1(a: str, b: str) -> str:
    # No docstring (model can't see the purpose), params named a/b (which is resume? which is skills?),
    # returns a bare string the model has to parse by guessing.
    have = [s for s in b.lower().split(",") if s.strip() and s.strip() in a.lower()]
    return f"{len(have)}/{len(b.split(','))}"


# ---------- GOOD tool ----------
@function_tool
def score_resume(resume_text: str, jd_skills: str) -> dict:
    """Score a resume by keyword-coverage against a role's hard skills. Call when assessing resume fit.

    Args:
        resume_text: the raw resume text.
        jd_skills: comma-separated hard skills the role requires, e.g. "python,sql,docker".
    """
    need = [s.strip().lower() for s in jd_skills.split(",") if s.strip()]
    have = [s for s in need if s in resume_text.lower()]
    missing = [s for s in need if s not in resume_text.lower()]
    score = round(100 * len(have) / len(need)) if need else 0
    return {"status": "ok", "score": score, "matched": have, "missing": missing}


agent = Agent(
    name="ResuMatch",
    instructions="你是求职助手，需要评估简历与岗位的匹配度时调用合适的工具，再用中文简洁作答。",
    tools=[f1, score_resume],
)

result = Runner.run_sync(
    agent,
    "我的简历写了 python 和 sql。这个岗位要求 python,sql,docker。匹配度多少、还差什么？",
)
print("最终回答：")
print(result.final_output)

print("\n--- 模型实际调了哪个工具 ---")
_local.show_steps(result.new_items)

# After the demo, stay in interactive mode to keep chatting.
_local.chat_loop(agent, hint="多换几组简历/技能，观察模型更愿意用哪个工具、用得对不对")
