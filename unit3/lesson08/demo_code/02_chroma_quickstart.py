"""
02 · ChromaDB 最小例 —— 建库、灌 50 条 JD，再 query 查回来
============================================================
运行：  python 02_chroma_quickstart.py（再跑一次会发现数据还在 → 持久化生效）
前置：  pip install -r requirements.txt（没装 chromadb 也能跑，自动用本地 JSON 兜底）

向量库帮你把"算相似度 + 取 top-k"打包好：你只管 add（灌）和 query（查）。
这一幕把 50 条真实 JD 灌进库，再用一句话 query，看它按意思召回最像的几条。
关键概念：collection（一张表）/ add（写入）/ query（按意思检索 top-k）。
本地持久化目录 = ./chroma_db，重启不丢——这点很重要（本节易错点）。
"""

from data.jobs import ids, texts, metas
from memory_kit import get_collection, banner

# 1) 拿到一个 collection（向量库里的"一张表"），数据落在本地 ./chroma_db
col = get_collection(name="jobs", persist_dir="./chroma_db")
banner()

# 2) add：把 50 条 JD 一次灌进去。每条一个唯一 id；文档内容会被自动编码成真向量
col.add(ids=ids(), documents=texts(), metadatas=metas())
print(f"库内现有 {col.count()} 条 JD\n")

# 3) query：给一句话，让库返回"意思最接近"的 top-k（这里要 3 条）
question = "software engineer相关的岗位"
result = col.query(query_texts=[question], n_results=3)

print(f"查询：{question}")
print("召回 top-3（distance 越小越相关）：")
docs = result["documents"][0]
dists = result["distances"][0]
metadatas = result["metadatas"][0]
for doc, dist, meta in zip(docs, dists, metadatas):
    print(f"  distance={dist:.4f}  [{meta.get('role','?')}]  {doc}")

print("\n注意：我们问的词和命中 JD 的字面并不完全一样，")
print("但它照样按'意思'把数据分析类岗位找了回来——这就是 query 的价值。")
print("再运行一次这个文件：count 不翻倍（相同 id 自动去重），数据也还在（落盘了）。")
