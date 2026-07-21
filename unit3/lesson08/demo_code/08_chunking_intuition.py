"""08｜分块直觉：不要把一个完整含义从中间切断。

运行：python 08_chunking_intuition.py（完全离线，课后加分）
"""


JD = """## 岗位职责
用 SQL 和 Python 分析用户行为，建设数据看板。
## 必须条件
支持远程工作，可为合适候选人提供签证支持。
## 加分项
了解 A/B 测试和产品分析。"""


def fixed_chunks(text: str, size: int = 36) -> list[str]:
    return [text[index:index + size] for index in range(0, len(text), size)]


def section_chunks(text: str) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []
    for line in text.splitlines():
        if line.startswith("## ") and current:
            chunks.append("\n".join(current))
            current = []
        current.append(line)
    if current:
        chunks.append("\n".join(current))
    return chunks


def show(title: str, chunks: list[str]) -> None:
    print(f"\n{title}")
    for index, chunk in enumerate(chunks, 1):
        print(f"  [{index}] {chunk.replace(chr(10), ' / ')}")


def main() -> None:
    fixed = fixed_chunks(JD)
    by_section = section_chunks(JD)
    show("固定字符数分块：可能在句子中间断开", fixed)
    show("按标题分块：职责、必须条件、加分项各自完整", by_section)
    assert any("必须条件" in chunk and "签证支持" in chunk for chunk in by_section)
    print("\n[观察] 按标题分块时，‘必须条件’和具体内容保持在一起。")
    print("[结论] 分块的目标是保留完整含义，不是追求某个固定长度。")


if __name__ == "__main__":
    main()
