"""稳定 chunk_id、upsert 与删除旧块。完全离线。"""

import hashlib


def chunk_id(source: str, section: str) -> str:
    raw = f"{source}:{section}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:12]


def sync(index: dict[str, str], source: str, chunks: dict[str, str]) -> None:
    new_ids = {chunk_id(source, section) for section in chunks}
    stale_ids = {key for key in index if key.startswith(source + "|")} - {
        f"{source}|{cid}" for cid in new_ids
    }
    for key in stale_ids:
        del index[key]
    for section, text in chunks.items():
        index[f"{source}|{chunk_id(source, section)}"] = text


def main() -> None:
    index: dict[str, str] = {}
    sync(index, "jd_007", {"summary": "数据分析师", "visa": "不提供签证"})
    print("v1：", index)

    sync(index, "jd_007", {"summary": "高级数据分析师", "remote": "可远程"})
    print("v2：", index)

    assert len(index) == 2
    assert all("不提供签证" not in value for value in index.values())
    assert any(value == "高级数据分析师" for value in index.values())
    print("结论：新版覆盖同一 section，旧版已不存在的块会被删除。")


if __name__ == "__main__":
    main()
