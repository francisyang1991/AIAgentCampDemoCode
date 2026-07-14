"""
05 · 带检索的 Agent（学生填空 · RAG 起点）
==============================================
运行：  python 05_rag_agent.py        （默认只展示检索→证据拼装）
        python 05_rag_agent.py --chat （设置 Key 后进入交互对话）
前置：  pip install -r requirements.txt

把前四幕拼成一个"先检索、再作答"的 Agent（RAG）：
  ① 用一把 search_jobs 工具去向量库检索（top-k + distance 阈值）；
  ② 把召回到的 JD 当"可用资料"拼进 instructions；
  ③ Agent 只根据这些资料回答，召回为空就如实说没有。
这就是课程 RAG 的地基："答案以检索到的材料为准，材料外不编。"

★ 学生填空：把语料换成你选题的资料（课程材料 / 你的日程），检索线照搬即可。
基础路径不调模型，学生先检查候选和证据块是否正确。
"""

import os
import sys

from agents import Agent, Runner, SQLiteSession, function_tool

from data.jobs import ids, texts, metas
from memory_kit import get_collection, banner

# 岗位语料向量库（持久化到本地，跨会话 / 重启都在）
JOBS = get_collection(name="jobs", persist_dir="./chroma_db")

THRESHOLD = 0.3  # distance 阈值：超过就当不够相关，丢掉（见 demo 04；按 embedding 校准）

# ↓↓↓ 学生填空：把它改成你选题的助手（课程问答 / 日程 / 你的项目）↓↓↓
PROFILE = """你是一个"岗位检索助手"。
- 能做：只根据【可用资料】里检索到的岗位描述回答用户问题
- 不做：编造资料里没有的岗位；资料为空时必须直说"没有找到相关岗位"
- 风格：简洁、用中文；答完点出用到了哪几条（jd_编号）
"""
# ↑↑↑ 学生填空 ↑↑↑


def _seed():
    """首次运行时把 50 条 JD 灌进去（已存在则跳过）。"""
    if JOBS.count() == 0:
        JOBS.add(ids=ids(), documents=texts(), metadatas=metas())


def retrieve(question: str, k: int = 3):
    """检索半步：召回 top-k，再用 distance 阈值筛掉不够像的。返回 [(id, doc)]。"""
    if JOBS.count() == 0:
        return []
    hits = JOBS.query(query_texts=[question], n_results=k)
    got_ids = hits["ids"][0]
    docs = hits["documents"][0]
    dists = hits["distances"][0]
    return [(i, d) for i, d, dist in zip(got_ids, docs, dists) if dist < THRESHOLD]


@function_tool
def search_jobs(question: str) -> str:
    """按用户问题在岗位库里检索最相关的几条 JD（已卡 distance 阈值）。

    Args:
        question: 用户的检索问题，例如"有适合我的数据分析岗吗"。
    Returns:
        召回到的 JD 文本（带 id），或"没有找到相关岗位"。
    """
    kept = retrieve(question)
    if not kept:
        return "没有找到相关岗位。"
    return "\n".join(f"- {jid} {doc}" for jid, doc in kept)


def build_instructions(question: str) -> str:
    """把召回的资料拼进 instructions——这就是"检索增强"落到 Agent 上。"""
    kept = retrieve(question)
    if not kept:
        return PROFILE + "\n【可用资料】\n（本次没有检索到相关岗位，请直说没有）\n"
    block = "\n".join(f"- {jid} {doc}" for jid, doc in kept)
    return PROFILE + "\n【可用资料，只能据此回答】\n" + block + "\n"


def chat_loop():
    """交互模式：每轮先检索、把资料拼进 instructions，再让 Agent 作答。"""
    session = SQLiteSession("rag_agent")  # 短期记忆（会话内多轮），Unit3 第7节内容
    print("开始对话（输入 exit / 退出 结束）。试试问'有适合我的数据分析岗吗'。")
    while True:
        try:
            user = input("\n你:   ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            return
        if user in {"exit", "quit", "退出"}:
            print("再见！")
            return
        if not user:
            continue
        # 每轮动态构造 instructions：把和这句话相关的资料检索进来
        agent = Agent(name="RagAgent", instructions=build_instructions(user),
                      tools=[search_jobs])
        try:
            result = Runner.run_sync(agent, user, session=session)
            print("助手:", result.final_output)
        except Exception as e:
            print(f"[出错] {type(e).__name__}：{e}（换句话再试，或输入 exit 退出）")


def demo_run():
    """离线演示：不调真实模型，把"检索→拼进 prompt"的闭环打印出来。"""
    print("\n=== 基础模式：展示检索→证据拼装（不调用对话模型）===")

    # 场景 A：库里有相关岗位
    q1 = "有适合我的数据分析岗吗？"
    print(f"\n  用户问：{q1}")
    instr1 = build_instructions(q1)
    print("  本轮拼好的 instructions（含检索到的资料）：")
    print("  " + instr1.replace("\n", "\n  "))

    # 场景 B：库里没有的东西 → 召回为空，如实说没有
    q2 = "有没有米其林三星大厨的岗位？"
    print(f"\n  用户问：{q2}")
    kept = retrieve(q2)
    print(f"  检索结果：{'（空）——诚实回答：没有找到相关岗位' if not kept else kept}")
    print("\n  → 先检查候选和证据块。它们正确后，再用 --chat 调用模型作答。")


if __name__ == "__main__":
    _seed()
    banner()
    if "--chat" in sys.argv:
        if not os.environ.get("OPENAI_API_KEY"):
            raise SystemExit("--chat 需要先设置 OPENAI_API_KEY。基础演示直接运行本文件即可。")
        chat_loop()
    else:
        demo_run()
