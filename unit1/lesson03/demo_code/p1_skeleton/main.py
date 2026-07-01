"""
main.py — the command-line entry point: multi-turn chat loop + session memory.
Run:    python main.py   (type exit to quit)

All the logic lives here; to change the role edit prompts.py, to change Agent assembly edit agent.py.
This is the P1 deliverable skeleton: prompt separated from logic, runs, and holds a conversation.
"""

import _local  # noqa: F401 — no key? auto-fallback to local Ollama (see _local.py)
from agents import Runner, SQLiteSession

from agent import agent


def main():
    # SQLiteSession remembers the multi-turn conversation history automatically (memory covered in depth in Unit 3)
    session = SQLiteSession("p1_session")
    print("=== 你的 Agent 已启动（默认：求职助手 ResuMatch；输入 exit / 退出 结束）===")
    print("试试：先说『我想投数据分析师』，再问『那我简历还差什么？』看它记不记得。")

    while True:
        user = input("\n你:   ").strip()
        if user in {"exit", "quit", "退出"}:
            print("再见！")
            break
        if not user:
            continue
        # Pass the session along, and the Agent remembers what was discussed earlier
        result = Runner.run_sync(agent, user, session=session)
        print("助手:", result.final_output)


if __name__ == "__main__":
    main()
