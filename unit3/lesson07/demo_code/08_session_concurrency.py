"""用版本号演示乐观并发控制。完全离线。"""

from dataclasses import dataclass


@dataclass
class SessionState:
    version: int = 7
    last_message: str = "初始状态"


def write_if_current(state: SessionState, expected: int, text: str) -> bool:
    if state.version != expected:
        return False
    state.last_message = text
    state.version += 1
    return True


def main() -> None:
    state = SessionState()
    version_seen_by_a = state.version
    version_seen_by_b = state.version

    ok_b = write_if_current(state, version_seen_by_b, "B 标签页先完成")
    ok_a = write_if_current(state, version_seen_by_a, "A 标签页晚完成")

    print("B 写入：", "成功" if ok_b else "冲突")
    print("A 写入：", "成功" if ok_a else "冲突，需要重新读取")
    print("最终状态：", state)

    assert ok_b is True
    assert ok_a is False
    assert state.last_message == "B 标签页先完成"
    print("结论：冲突要被明确发现，不能让晚到的旧写入静默覆盖。")


if __name__ == "__main__":
    main()
