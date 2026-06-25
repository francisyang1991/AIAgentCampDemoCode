"""
04 · Streaming output —— display as it generates (one of the newest features)
------------------------------------------------
Run:      python 04_streaming.py

run_streamed doesn't wait for the whole thing to finish; it hands you tokens as they come.
Essential for chat UIs and typewriter effects —— especially for long outputs like "generate a cover letter",
streaming lets the user see progress immediately, which feels much better.

★ Job-hunt theme: have ResuMatch stream the opening of a cover letter.
"""

import _local  # noqa: F401 —— no key? auto-falls back to local Ollama; no Ollama? prints a hint
import asyncio

from agents import Agent, Runner
from openai.types.responses import ResponseTextDeltaEvent


async def main():
    agent = Agent(
        name="ResuMatch",
        instructions="你是求职助手，用英文写简短、得体、不浮夸的 cover letter。",
    )

    result = Runner.run_streamed(
        agent, "帮我给『数据分析师』岗位写一段 4 句话的英文 cover letter 开头。"
    )

    # Read events one by one; only print "text delta" events — that's the typewriter effect
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)
    print()


if __name__ == "__main__":
    asyncio.run(main())
