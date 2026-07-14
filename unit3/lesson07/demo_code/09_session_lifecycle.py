"""Session 生命周期：活跃、归档、删除。完全离线。"""

from dataclasses import dataclass, field


@dataclass
class Session:
    status: str = "active"
    items: list[str] = field(default_factory=list)

    def add(self, text: str) -> None:
        if self.status != "active":
            raise RuntimeError("只有 active 会话允许继续写入")
        self.items.append(text)

    def archive(self) -> None:
        self.status = "archived"

    def delete(self) -> None:
        self.items.clear()
        self.status = "deleted"


def main() -> None:
    session = Session()
    session.add("我只看远程岗位")
    print("活跃：", session)

    session.archive()
    print("归档：", session, "（保留记录，但不再写入）")

    session.delete()
    print("删除：", session)

    assert session.status == "deleted"
    assert session.items == []
    print("结论：归档和删除不是一回事；删除后还要验证内容确实为空。")


if __name__ == "__main__":
    main()
