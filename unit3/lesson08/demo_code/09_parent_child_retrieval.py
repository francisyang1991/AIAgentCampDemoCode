"""小块负责命中，父块负责提供完整上下文。完全离线。"""

PARENTS = {
    "jd_007:requirements": "必须条件：熟悉 SQL 和 Python。签证：公司目前不提供工作签证。工作方式：可远程。",
    "jd_012:requirements": "必须条件：熟悉 Excel 和 Tableau。签证：可协助办理。工作方式：每周到岗三天。",
}

CHILDREN = [
    ("jd_007:requirements", "签证：公司目前不提供工作签证"),
    ("jd_007:requirements", "工作方式：可远程"),
    ("jd_012:requirements", "签证：可协助办理"),
]


def main() -> None:
    query = "哪个远程岗位不提供签证？"
    words = {"远程", "不提供", "签证"}
    parent_id, child = max(
        CHILDREN,
        key=lambda item: sum(word in item[1] for word in words),
    )

    print("问题：", query)
    print("小块命中：", child)
    print("返回父块：", PARENTS[parent_id])

    assert "可远程" in PARENTS[parent_id]
    assert "不提供工作签证" in PARENTS[parent_id]
    print("结论：小块让命中更准，父块把回答需要的上下文补完整。")


if __name__ == "__main__":
    main()
