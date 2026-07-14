"""
01 · Embedding 基础 —— 文字变向量，意思近的距离也近
=====================================================
运行：  python 01_embedding_basics.py
前置：  pip install -r requirements.txt
       真 embedding：设了 OPENAI_API_KEY 用 OpenAI；否则用本机 Ollama nomic-embed-text（零成本、可断网）。

这一幕只做一件事：把几句话变成真向量，再两两算相似度，亲眼确认
"意思接近的文字，向量也接近"——哪怕中英不同字、换个说法。
这是后面"按意思检索 JD"的全部底气。
关键概念：embedding（文字→向量）+ cosine 相似度（越大越像）。
"""

from memory_kit import embed, cosine, banner

# 一句英文"查询"，四句中文"候选"。直觉上：前两句和查询意思很近，后两句不相关。
query = "data analyst"
candidates = [
    "数据分析师岗位，负责 SQL 取数与报表",   # 同义（中文），应该最像
    "负责用 Python 做业务指标分析",           # 高度相关
    "资深后端 Go 工程师，做微服务",           # 不相关（另一个工种）
    "这台笔记本电脑续航很长",                 # 完全不相关
]

banner()  # 打印这次用的真 embedding 后端（OpenAI 或本机 Ollama）

# 一次把 5 句话都编码成真向量（查询放在第 0 个）
vectors = embed([query] + candidates)
q_vec, cand_vecs = vectors[0], vectors[1:]

print(f"\n查询（英文）：{query}")
print(f"向量维度：{len(q_vec)}（每句话都被压成这么长的一串数）\n")
print("按相似度从高到低排序（cosine 越接近 1 越像）：")

# 算查询与每个候选的相似度，排序后打印
ranked = sorted(
    zip(candidates, cand_vecs),
    key=lambda pair: cosine(q_vec, pair[1]),
    reverse=True,
)
for text, vec in ranked:
    score = cosine(q_vec, vec)
    bar = "█" * max(0, int(score * 20))  # 用小条形直观看差距
    print(f"  {score:+.3f}  {bar:<20}  {text}")

print("\n看排序：查询是英文，命中的却是中文 JD——字不一样，意思一样，分照样高。")
print("无关的两句沉到最后。这就是语义检索的地基：不靠字面匹配，靠'意思'的远近。")
