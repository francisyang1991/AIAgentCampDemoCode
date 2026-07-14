"""06｜混合检索：语义候选 + 关键词候选取并集。

运行：python 06_hybrid_search.py

这里的关键词分数是教学简化版，便于学生逐行看懂。
真实项目可换成 BM25，外层的“两路召回→合并”不变。
"""

import re

from data.jobs import ids, texts
from memory_kit import banner, cosine, embed


def words(text: str) -> set[str]:
    """英文按词、中文按单字切分；只用来演示精确词命中。"""
    text = text.lower()
    return set(re.findall(r"[a-z0-9]+", text) + re.findall(r"[一-鿿]", text))


def keyword_score(query: str, document: str) -> int:
    """教学简化版：问题中有多少个词/字在文档中出现。"""
    return len(words(query) & words(document))


def top_indices(scores: list[float], k: int, positive_only: bool = False) -> list[int]:
    order = sorted(range(len(scores)), key=lambda index: scores[index], reverse=True)
    if positive_only:
        order = [index for index in order if scores[index] > 0]
    return order[:k]


def main() -> None:
    banner()
    job_ids, documents = ids(), texts()
    query = "data analyst dashboard SQL"
    k = 5

    document_vectors = embed(documents)
    query_vector = embed([query])[0]
    semantic_scores = [cosine(query_vector, vector) for vector in document_vectors]
    lexical_scores = [keyword_score(query, document) for document in documents]

    semantic_top = top_indices(semantic_scores, k)
    keyword_top = top_indices(lexical_scores, k, positive_only=True)
    merged = semantic_top + [index for index in keyword_top if index not in semantic_top]

    def show(title: str, indices: list[int]) -> None:
        print(f"\n{title}")
        for rank, index in enumerate(indices, 1):
            print(f"  {rank}. {job_ids[index]}  {documents[index][:58]}")

    print(f"问题：{query}")
    show("语义支路：擅长找换一种说法的内容", semantic_top)
    show("关键词支路：擅长找精确词、缩写和编号", keyword_top)
    show("合并后的候选池（去重）", merged)

    rescued = [job_ids[index] for index in keyword_top if index not in semantic_top]
    print(f"\n只由关键词支路补回的候选：{rescued or '无'}")
    assert len(merged) == len(set(merged))
    print("\n[观察] 两路的前几名不完全相同。")
    print("[结论] Hybrid 先减少漏掉正确资料的风险，它不负责最终排序。")
    print("[下一步] 运行 07_business_rerank.py。")


if __name__ == "__main__":
    main()
