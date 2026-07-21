"""
04 · distance 阈值 —— 不够像的就丢掉，宁缺毋滥
==================================================
运行：  python 04_distance_threshold.py（建议先跑过 02，让库里有 50 条 JD）
前置：  pip install -r requirements.txt

top-k 有个陷阱：它一定会给你 k 条，哪怕全不相关。
所以在 top-k 之后再卡一道 distance 阈值：离太远的直接丢掉。
全被丢光，就老实说"资料里没有"——这就是"不编造"落到检索上。
关键概念：distance 阈值过滤（检索到的才可信）。
"""

from data.jobs import ids, texts, metas
from memory_kit import get_collection, banner

col = get_collection(name="jobs", persist_dir="./chroma_db")
banner()

if col.count() == 0:
    col.add(ids=ids(), documents=texts(), metadatas=metas())
    print(f"（库是空的，已灌入 {col.count()} 条 JD）\n")

THRESHOLD = 0.5  # distance 超过它就当"不够像"，丢掉。
#                  这个值已按 voyage-4-lite 校准：相关岗位约 0.33–0.42，
#                  明显不相关的“大厨岗位”约 0.77，取 0.5 能把两组切开。


def retrieve(question: str, k: int = 3):
    """召回 top-k，再用阈值把"离太远"的丢掉，只留可信的几条。"""
    hits = col.query(query_texts=[question], n_results=k)
    docs = hits["documents"][0]
    dists = hits["distances"][0]
    kept = [(d, dist) for d, dist in zip(docs, dists) if dist < THRESHOLD]
    return kept, list(zip(docs, dists))


# 场景 A：库里有相关岗位——阈值内留下几条
q1 = "数据分析师"
kept1, raw1 = retrieve(q1)
print(f"查询：{q1}（阈值 {THRESHOLD}）")
for doc, dist in raw1:
    mark = "保留" if dist < THRESHOLD else "丢弃"
    print(f"  [{mark}] distance={dist:.4f}  {doc}")

# 场景 B：库里根本没有的东西——应当全被丢光，如实报"没有"
q2 = "米其林三星大厨招聘"
kept2, raw2 = retrieve(q2)
print(f"\n查询：{q2}（库里没有这类岗位）")
for doc, dist in raw2:
    mark = "保留" if dist < THRESHOLD else "丢弃"
    print(f"  [{mark}] distance={dist:.4f}  {doc}")

if not kept2:
    print("  → 全部超阈值，一条都不留。诚实回答：资料里没有相关岗位。")

print("\n结论：top-k 会硬塞满 k 条，阈值负责把'凑数的'踢掉——")
print("留得下就据它作答，留不下就说没有，绝不硬编。")
