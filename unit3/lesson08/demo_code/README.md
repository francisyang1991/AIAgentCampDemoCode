# 第 8 节 Demo｜检索工程与向量数据库

学生不需要一开始背 BM25、RRF 或 cross-encoder。先把检索链讲清：

> 建库 → 找候选 → 过滤明确条件 → 拒绝低相关结果 → 两路合并 → 再排一次。

## 运行顺序

```bash
pip install -r requirements.txt

python 01_embedding_basics.py
python 02_chroma_quickstart.py
python 03_metadata_filter.py
python 04_distance_threshold.py
python 05_rag_agent.py
python 06_hybrid_search.py
python 07_business_rerank.py
python 08_chunking_intuition.py   # 课后加分
python 09_parent_child_retrieval.py
python 10_index_lifecycle.py
python 11_query_planner.py
```

`05_rag_agent.py` 默认只打印“检索到了什么、怎样交给模型”；真正聊天使用：

```bash
python 05_rag_agent.py --chat
```

## 掌握层级

| Demo | 学习目标 | 层级 |
|---|---|---|
| 01 | 理解“文字可以按意思排序” | 必会 |
| 02 | 会写 `add` 和 `query` | 必会 |
| 03 | 地点、级别、权限先做结构化过滤 | 必会 |
| 04 | top-k 不代表相关，需要拒绝门槛 | 必会 |
| 05 | 回答必须带资料 id | 必会 |
| 06 | 语义和关键词两路一起找 | 看懂并集 |
| 07 | 候选找全后，用硬条件重新排序 | 必会规则版 |
| 08 | 分块方式会影响检索到的上下文 | 课后加分 |
| 09 | 小块命中后，取回完整父块 | 工程补充 |
| 10 | upsert 新版并删除过期旧块 | 工程补充 |
| 11 | 原样搜、改写、拆问或不检索 | 工程补充 |

## 作业最小要求

- 至少 30 条真实资料。
- 5 个固定问题，并事先写出应该命中的文档 id。
- 最终回答列出用过的文档 id。
- 没有可靠候选时明确说“资料不足”。

距离阈值、top-k 和重排分数都是本项目要校准的参数，不是全行业通用答案。
