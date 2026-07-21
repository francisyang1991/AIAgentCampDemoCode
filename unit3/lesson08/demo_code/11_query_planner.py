"""用透明规则演示四种查询动作。完全离线。"""

import re


def plan(query: str) -> tuple[str, list[str]]:
    if query in {"你好", "谢谢", "继续"}:
        return "不检索", []
    if re.search(r"[A-Z]{2,}|\w+-\d+", query):
        return "原样搜", [query]
    if "以及" in query or "同时" in query:
        parts = [part.strip("？?，, ") for part in re.split(r"以及|同时", query)]
        return "拆成两问", [part for part in parts if part]
    if "它" in query or "那个" in query:
        return "改写后搜", ["补全指代后再检索：" + query]
    return "原样搜", [query]


def main() -> None:
    examples = [
        "你好",
        "JD-104 要求 AWS 吗？",
        "找远程岗位以及签证政策",
        "它那个签证要求是什么？",
    ]
    for query in examples:
        action, searches = plan(query)
        print(f"{query} -> {action}: {searches}")

    assert plan("你好")[0] == "不检索"
    assert plan("JD-104 要求 AWS 吗？")[0] == "原样搜"
    assert plan("找远程岗位以及签证政策")[0] == "拆成两问"
    print("结论：查询规划先保住精确词，再决定改写、拆分还是不查。")


if __name__ == "__main__":
    main()
