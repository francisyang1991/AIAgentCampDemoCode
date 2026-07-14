"""06｜重要事实单独放在结构化 state。

基础：python 06_state_slots.py
联网：python 06_state_slots.py --live
聊天：python 06_state_slots.py --chat
"""

import argparse
from dataclasses import dataclass

from agents import Agent, RunContextWrapper, Runner, SQLiteSession, function_tool


@dataclass
class Profile:
    name: str = ""
    target_role: str = ""
    work_location: str = ""
    visa: str = ""


def profile_card(profile: Profile) -> str:
    return (
        f"姓名={profile.name or '未知'}；"
        f"目标岗位={profile.target_role or '未知'}；"
        f"地点={profile.work_location or '未知'}；"
        f"签证={profile.visa or '未知'}"
    )


@function_tool
def save_profile(wrapper: RunContextWrapper[Profile], field: str, value: str) -> str:
    """把一个硬事实写入结构化档案。

    Args:
        field: name / target_role / work_location / visa 之一。
        value: 要保存的当前值。
    """
    if field not in vars(wrapper.context):
        return f"未知字段：{field}"
    setattr(wrapper.context, field, value)
    return f"已更新档案：{field}={value}"


def instructions(ctx: RunContextWrapper[Profile], _agent: Agent[Profile]) -> str:
    return "你是求职助手。\n[代码每轮注入的档案]\n" + profile_card(ctx.context)


AGENT = Agent[Profile](
    name="ResuMatch",
    instructions=instructions,
    tools=[save_profile],
)


def show_offline() -> None:
    profile = Profile(
        name="小明",
        target_role="后端工程师",
        work_location="只看远程或马德里",
        visa="需要工签支持",
    )
    history_before = ["我叫小明", "我只看远程岗位"]
    history_after: list[str] = []  # 模拟换了一个全新 Session
    print("旧会话历史：", history_before)
    print("新会话历史：", history_after)
    print("新会话仍会注入的档案：", profile_card(profile))
    assert not history_after and profile.work_location
    print("\n[观察] 历史已清空，地点和签证仍在 state。")
    print("[结论] 流水对话可以裁，当前硬事实要单独保存和更新。")


def run_live(chat: bool = False) -> None:
    profile = Profile()
    session = SQLiteSession("student:state:thread-01")
    if chat:
        print("进入聊天模式（输入 exit 退出）。")
        while True:
            question = input("\n你：").strip()
            if question in {"exit", "quit", "退出"}:
                return
            if question:
                result = Runner.run_sync(AGENT, question, session=session, context=profile)
                print("助手：", result.final_output)
                print("档案：", profile_card(profile))
        return
    questions = ["我叫小明，想找后端岗。", "我只看远程，而且需要工签支持。"]
    for question in questions:
        result = Runner.run_sync(AGENT, question, session=session, context=profile)
        print(f"用户：{question}\n助手：{result.final_output}\n档案：{profile_card(profile)}\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--chat", action="store_true")
    args = parser.parse_args()
    run_live(chat=args.chat) if (args.live or args.chat) else show_offline()


if __name__ == "__main__":
    main()
