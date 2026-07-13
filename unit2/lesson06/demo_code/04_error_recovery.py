"""
04 · Failure & recovery — try/except inside tools -> "friendly error" returns
=============================================================================
Run:  python 04_error_recovery.py

Tools WILL fail: bad arguments, nothing found, an external API times out or gets
rate-limited (429). Two iron rules of the course bar:
  ① Inside the tool, try/except and RETURN a friendly error string the model can
     read — so it can re-route / ask again / tell the user, instead of the whole
     run crashing on a bare exception.
  ② Set max_turns on the Runner as a backstop, so it can't retry forever against
     an error it can't fix (burning tokens, spinning in place).

Three scenarios below:
  · Scenario 1: parse_jd gets empty/garbage input -> friendly error -> model recovers.
  · Scenario 2: search_jobs (the REAL HN API tool) hits a forced timeout mid-chain
     -> tenacity retries, then offline fallback -> the chain does NOT crash.
  · Scenario 3: a deliberately tiny max_turns triggers the MaxTurnsExceeded backstop.
Offline / no key → each scenario explains what should happen, never crashes.
"""

import _local  # noqa: F401 — no key auto-falls-back to local Ollama; see _local.py
import httpx
from agents import Agent, Runner, function_tool

# Reuse the real search_jobs tool + its pure helper from demo 03b.
from importlib import import_module

_m = import_module("03b_real_api_tool")
search_jobs = _m.search_jobs          # the @function_tool
job_search = _m.job_search            # pure-function version (for the offline self-check)

_SKILL_KEYWORDS = ["Python", "SQL", "Docker", "Kubernetes", "AWS", "React", "Go", "NLP"]


@function_tool
def parse_jd(jd_text: str) -> dict:
    """Parse a JD into hard requirements; returns a FRIENDLY error, never raises.

    Shows rule ①: every failure path is caught inside the tool and turned into a
    message the model can act on (retry / ask the user), prefixed with '错误：'.

    Args:
        jd_text: The raw JD text (may be empty or junk).

    Returns:
        dict: {status, role, must_have: list[str], nice_to_have: list[str]}
    """
    try:
        text = (jd_text or "").strip()
        if not text:
            return {"status": "error", "role": "", "must_have": [], "nice_to_have": [],
                    "message": "错误：JD 文本为空，请把职位描述粘贴进来再试。"}
        lower = text.lower()
        hits = [kw for kw in _SKILL_KEYWORDS if kw.lower() in lower]
        if not hits:
            # Nothing recognisable found — tell the model so it can ask for a real JD.
            return {"status": "error", "role": text[:30], "must_have": [], "nice_to_have": [],
                    "message": "错误：没在这段文本里识别到技能要求，可能不是有效 JD。"
                               "请确认粘贴的是职位描述。"}
        return {"status": "ok", "role": text.splitlines()[0][:40],
                "must_have": hits, "nice_to_have": []}
    except Exception as e:  # backstop: any surprise becomes a friendly note too
        return {"status": "error", "role": "", "must_have": [], "nice_to_have": [],
                "message": f"错误：解析失败（{type(e).__name__}），请稍后重试。"}


agent = Agent(
    name="ResuMatch",
    instructions=(
        "你是 ResuMatch 求职助手。解析 JD 用 parse_jd，搜岗位用 search_jobs。"
        "若工具返回以『错误：』开头或 status 为 error，别硬扛——读懂原因后向用户"
        "说明并给出下一步（如让用户补一段有效 JD）。用中文简洁回答。"
    ),
    tools=[parse_jd, search_jobs],
)


def demo_recovery():
    """Scenario 1: a junk JD -> tool returns friendly error -> model recovers."""
    q = "帮我解析这份 JD：随便一句话，不是真的招聘描述。没有的话告诉我该怎么办。"
    print("【场景 1 · 失败后恢复】")
    try:
        result = Runner.run_sync(agent, q, max_turns=6)
        print(f"你:   {q}")
        print(f"助手: {result.final_output}")
    except Exception as e:
        print(f"你:   {q}")
        print(f"[离线] 无法连模型（{type(e).__name__}）。")
        print("     正常情况下：parse_jd 返回『错误：不是有效 JD』→ 模型据此提醒用户补真实 JD。")


def demo_chain_survives_timeout():
    """Scenario 2: force search_jobs to time out mid-chain -> it must NOT crash.

    We patch httpx.get to always raise a timeout, proving the retry + offline
    fallback keeps the chain alive. This does not need a model — it exercises the
    tool's own resilience directly.
    """
    print("\n【场景 2 · 链条中途超时不崩（真实工具的降级）】")
    orig_get = httpx.get

    def _always_timeout(*a, **k):
        raise httpx.TimeoutException("forced timeout for demo")

    httpx.get = _always_timeout  # simulate the network being down / 429 storm
    try:
        res = job_search("python")   # pure helper: same code path as the tool
        print(f"search_jobs('python') 在超时下没崩：source={res.source}，"
              f"命中 {res.count} 条")
        print(f"  说明：{res.message}")
    finally:
        httpx.get = orig_get         # always restore, even if something went wrong


def demo_max_turns():
    """Scenario 3: tiny max_turns -> MaxTurnsExceeded backstop, caught here."""
    q = "帮我依次搜 python、react、go、java、rust 五类岗位，并逐条汇报。"
    print("\n【场景 3 · max_turns 兜底（防死循环）】")
    try:
        # max_turns=1 is deliberately too small: turn 1 makes the tool call(s), but
        # reading the results + answering needs another turn -> backstop must fire.
        result = Runner.run_sync(agent, q, max_turns=1)
        print(f"助手: {result.final_output}")
    except Exception as e:
        name = type(e).__name__
        if "MaxTurns" in name:
            print(f"已触发 max_turns 兜底（{name}）：步数到上限就停，绝不无限重试。")
            print("生产里可在此返回一句『这次没查完，请缩小范围再试』，而不是让它一直转。")
        else:
            print(f"[离线] 无法连模型（{name}）。max_turns=1 时超步会抛 MaxTurnsExceeded，被这里接住。")


if __name__ == "__main__":
    demo_recovery()
    demo_chain_survives_timeout()
    demo_max_turns()
    _local.chat_loop(agent, hint="贴段无效 JD 看它怎么恢复；或让它搜岗位，观察工具超时也不崩")
