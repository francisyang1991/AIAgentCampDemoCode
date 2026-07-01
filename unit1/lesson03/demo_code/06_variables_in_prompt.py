"""
06 · A variable inside the instructions — inject {today} every run (flagship theme: ResuMatch).
================================================================================================
Run:    python 06_variables_in_prompt.py

The simplest hardening move the slides teach: don't hard-code things that change — put a VARIABLE in
the instructions and fill it in at run time.

  · Slide「逐行读①」: the real Claude prompt writes the date as {{currentDateTime}}, injected each turn.
  · Slide「固定的写前面，会变的放后面」: keep the fixed rules as a STABLE PREFIX (cache-friendly),
    put the {today} variable at the END (dynamic suffix). Mixing {today} into the prefix busts the
    prompt cache every turn (~10x cost), so the variable goes last.

This demo builds the system prompt from a template with build_instructions(today): fixed rules first,
then `今天的日期：{today}`. We inject the real date, print the assembled prompt so you can SEE the
variable filled in, and ask a date-aware question so you can watch the injected value actually get used.
(Demo 07 adds the OTHER hardening move — <untrusted_data> delimiters against prompt injection.)
"""

import _local  # noqa: F401 — no key? auto-fallback to local Ollama (see _local.py)
from datetime import date

from agents import Agent, Runner

# ── Stable prefix: the fixed rules. Identical on every request → the prompt cache can reuse it. ──
BASE_RULES = """你是"ResuMatch 求职教练"，针对某一个岗位帮用户定制简历要点。
- 只基于用户**真实**经历重排 / 改写，绝不编造没有的经历或数字。
- 涉及"还剩几天 / 来不来得及"时，用下面注入的今天日期来判断，别自己瞎猜今天几号。"""


def build_instructions(today: str) -> str:
    """Assemble the system prompt from a template: fixed rules first, then the {today} variable last.

    `today` is the VARIABLE — it changes every day, so it must be injected at run time, not hard-coded.
    Putting it at the end keeps the long rules block as a stable, cacheable prefix.
    """
    return f"{BASE_RULES}\n\n今天的日期：{today}"  # ← the variable, injected as the dynamic suffix


today = date.today().isoformat()  # ← run-time value; hard-coding a date would go stale tomorrow
agent = Agent(name="ResuMatch", instructions=build_instructions(today))

# See the variable actually filled into the instructions
print("--- 拼好的 instructions（注意最后一行的日期是运行时填进去的变量）---")
print(build_instructions(today))

# Ask something that depends on "today" — the agent can only answer because we injected the date
print("\n===== 用到了注入的日期 =====")
result = Runner.run_sync(agent, "这个岗位这周五（7/4）截止，我从今天开始准备，时间还够吗？")
print(result.final_output)

print("\n----------------------------------------")
print(f"instructions 里没写死日期，而是每轮把 {{today}} 换成真实的今天（{today}）再交给模型。")
print("规则在前（可缓存）、变量在后（每轮只变尾巴）——这就是『固定写前面、会变放后面』。")

_local.chat_loop(agent, hint="再问点和『今天/还剩几天』有关的，看它用不用注入进去的日期")
