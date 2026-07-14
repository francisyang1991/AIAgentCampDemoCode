"""同一个请求重试两次，只写入一次。完全离线。"""

import sqlite3


def main() -> None:
    db = sqlite3.connect(":memory:")
    db.execute(
        """
        CREATE TABLE turns (
            session_id TEXT NOT NULL,
            request_id TEXT NOT NULL,
            user_text TEXT NOT NULL,
            UNIQUE(session_id, request_id)
        )
        """
    )

    def save_once(session_id: str, request_id: str, text: str) -> str:
        try:
            db.execute(
                "INSERT INTO turns VALUES (?, ?, ?)",
                (session_id, request_id, text),
            )
            db.commit()
            return "首次写入"
        except sqlite3.IntegrityError:
            return "重复请求：直接复用第一次结果"

    print("第一次：", save_once("alice:thread-1", "req-001", "帮我找远程岗位"))
    print("网络重试：", save_once("alice:thread-1", "req-001", "帮我找远程岗位"))

    count = db.execute("SELECT COUNT(*) FROM turns").fetchone()[0]
    print("\n观察：数据库记录数 =", count)
    assert count == 1
    print("结论：request_id + UNIQUE 约束，让重复提交不会重复落库。")


if __name__ == "__main__":
    main()
