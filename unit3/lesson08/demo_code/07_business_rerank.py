"""07｜业务重排：语义相关之外，还要满足硬条件。

运行：python 07_business_rerank.py（完全离线）
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Candidate:
    job_id: str
    title: str
    remote: bool
    visa: bool
    semantic_score: float


CANDIDATES = [
    Candidate("jd_007", "Data Analyst · SQL / Python", True, True, 0.83),
    Candidate("jd_012", "Senior Data Engineer · Spark", True, False, 0.91),
    Candidate("jd_019", "BI Analyst · Dashboards", False, True, 0.79),
    Candidate("jd_026", "Junior Product Analyst", True, True, 0.76),
]


def business_score(candidate: Candidate) -> tuple[float, list[str]]:
    """先使用语义分，再用远程/签证条件做可解释调整。"""
    score = candidate.semantic_score * 100
    reasons = [f"语义 {candidate.semantic_score:.2f}"]
    score += 15 if candidate.remote else -60
    reasons.append("支持远程 +15" if candidate.remote else "不支持远程 -60")
    score += 20 if candidate.visa else -80
    reasons.append("支持签证 +20" if candidate.visa else "不支持签证 -80")
    return score, reasons


def main() -> None:
    semantic_order = sorted(CANDIDATES, key=lambda item: item.semantic_score, reverse=True)
    print("用户条件：数据分析相关；必须远程；必须支持签证。")
    print("\n第一步：只看语义相似度")
    for rank, candidate in enumerate(semantic_order, 1):
        print(f"  {rank}. {candidate.job_id}  {candidate.title:<34} {candidate.semantic_score:.2f}")

    ranked = sorted(
        [(business_score(candidate)[0], candidate, business_score(candidate)[1]) for candidate in CANDIDATES],
        key=lambda row: row[0],
        reverse=True,
    )
    print("\n第二步：加入远程和签证条件")
    for rank, (score, candidate, reasons) in enumerate(ranked, 1):
        print(f"  {rank}. {candidate.job_id}  总分={score:6.1f}  {'；'.join(reasons)}")

    assert semantic_order[0].job_id == "jd_012"
    assert ranked[0][1].job_id == "jd_007"
    print("\n[观察] 语义第一的 jd_012 因为不支持签证，不再排第一。")
    print("[结论] 最终排序 = 语义相关性 + 可测试的业务约束。")
    print("[进阶] 候选很复杂时，可以用重排模型替换语义打分，硬约束仍保留。")


if __name__ == "__main__":
    main()
