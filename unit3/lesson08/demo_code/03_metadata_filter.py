"""
03 · metadata 过滤 —— 用 where= 先筛一刀，再按意思排
=====================================================
运行：  python 03_metadata_filter.py（建议先跑过 02，让库里有 50 条 JD）
前置：  pip install -r requirements.txt

光靠"意思"还不够准：查"初级数据分析"，也可能召回资深岗。
先用 metadata（每条 JD 挂的 role / seniority 标签）把范围缩小，
再在这个范围里按意思排序——又快又准。
关键概念：metadata 过滤（ChromaDB 的 where= 等值筛选）。
"""

from data.jobs import ids, texts, metas
from memory_kit import get_collection, banner

col = get_collection(name="jobs", persist_dir="./chroma_db")
banner()

# 兜底：如果还没跑过 02，这里补灌一次，保证本文件单独也能演示
if col.count() == 0:
    col.add(ids=ids(), documents=texts(), metadatas=metas())
    print(f"（库是空的，已灌入 {col.count()} 条 JD）\n")

question = "data analyst"

# A) 不过滤：直接按意思召回，资深 / 初级都可能进来
plain = col.query(query_texts=[question], n_results=3)
print(f"查询：{question}")
print("\n【不过滤】召回 top-3（seniority 混着来）：")
for doc, meta in zip(plain["documents"][0], plain["metadatas"][0]):
    print(f"  [{meta.get('seniority','?'):<6}] {doc}")

# B) 过滤：先用 where= 只保留"初级"岗，再在里面按意思排
filtered = col.query(
    query_texts=[question],
    n_results=5,
    where={"seniority": "junior"},   # 关键：等值筛选，资深岗根本不进候选
)
print("\n【where=junior】只在初级岗里召回 top-3：")
for doc, meta in zip(filtered["documents"][0], filtered["metadatas"][0]):
    print(f"  [{meta.get('seniority','?'):<6}] {doc}")

print("\n对比两块：加了 where= 之后，资深岗被挡在候选之外——")
print("先按标签把范围缩小，再按意思排序，召回就既准又省算力。")
