"""
agent.py — the Agent definition.
The prompt is imported from prompts.py; this file only "assembles the Agent".
"""

from agents import Agent

from prompts import SYSTEM_PROMPT  # defaults to this lesson's theme: the ResuMatch job-hunt assistant
# Want a different topic? Change only this import line (leave the rest untouched):
#   from prompts_resume import SYSTEM_PROMPT   # ResuMatch, detailed version (JD-tailored resume)
#   from prompts_stock import SYSTEM_PROMPT    # EquityLens research assistant (optional · stock track)
#   or just edit SYSTEM_PROMPT in prompts.py to your own topic's role

# The Agent itself: name is the identity label, instructions is the system prompt
agent = Agent(
    name="ResuMatch",
    instructions=SYSTEM_PROMPT,
    # no tools yet; next lesson (lesson 4) we add tools=[...]
)
