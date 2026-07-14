"""01｜没有 Session：两次调用互相不知道。

基础：python 01_no_memory.py       # 离线、结果固定
进阶：python 01_no_memory.py --live # 真正调用模型
"""

import argparse

from agents import Agent, Runner


TURNS = ["你好，我叫小明。", "我刚才说我叫什么？"]


def show_offline() -> None:
    replies = [
        "你好，小明。",
        "我没有上一次调用的对话记录，不知道你的名字。",
    ]
    print("【离线对照】每一轮都是全新调用")
    for index, (question, answer) in enumerate(zip(TURNS, replies), 1):
        print(f"\n第 {index} 轮\n  用户：{question}\n  助手：{answer}")


def run_live() -> None:
    agent = Agent(name="ResuMatch", instructions="你是求职助手，用中文简短回答。")
    for index, question in enumerate(TURNS, 1):
        # 故意不传 session：两次 run 彼此独立。
        result = Runner.run_sync(agent, question)
        print(f"\n第 {index} 轮\n  用户：{question}\n  助手：{result.final_output}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="真正调用模型")
    args = parser.parse_args()
    run_live() if args.live else show_offline()
    print("\n[观察] 第 2 轮没有收到第 1 轮的内容。")
    print("[结论] 连续对话来自应用传回历史，不是模型自己记住了。")
    print("[下一步] 运行 02_sqlite_session.py。")


if __name__ == "__main__":
    main()
