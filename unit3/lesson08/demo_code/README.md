# 第 8 节 Demo｜检索工程与向量数据库

学生不需要一开始背 BM25、RRF 或 cross-encoder。先把检索链讲清：

> 建库 → 找候选 → 过滤明确条件 → 拒绝低相关结果 → 两路合并 → 再排一次。

## 首次安装

在仓库根目录执行：

```bash
cd unit3/lesson08/demo_code
bash setup.sh
source .venv/bin/activate
```

`setup.sh` 会创建独立的 Python 环境并安装 ChromaDB 等依赖。

## Key 只填一次

打开当前 `demo_code` 目录中由 `setup.sh` 生成的
`VOYAGE_API_KEY.txt`，把 Voyage API Key 粘贴到注释下面，不要加引号：

```text
# 把 Key 粘贴到下一行（不要加引号）
你的Voyage_API_Key
```

然后直接运行下方任意 Demo。01–06 中所有需要向量的代码都会通过本目录的
`course_demo_config.py` 自动使用 Voyage `voyage-4-lite`（默认 1024 维），不需要逐个
文件配置。这个 Key 文件已被 Git 忽略，不会随代码提交；也可以改用环境变量
`VOYAGE_API_KEY`。

不同模型的向量不能混用。公共工具会按“模型 + 维度”自动使用不同的本地向量库目录，
所以从 Ollama/OpenAI/GLM 切到 Voyage 时会自动建立一份干净索引。

## 每位学生如何建立自己的 Chroma DB

ChromaDB 在本节使用本地 `PersistentClient`，不需要注册账号、连接公共数据库或启动独立服务。
每位学生在自己的电脑上执行：

```bash
cd unit3/lesson08/demo_code
source .venv/bin/activate
python 02_chroma_quickstart.py
```

第一次运行会自动：

1. 在 `./chroma_db/` 下按 embedding 模型创建专属子目录。
2. 创建名为 `jobs` 的 collection。
3. 把课程示例数据编码成向量并持久化到本机。

再运行一次会复用同一个本地库；相同 id 会 upsert，不会重复累加。
`chroma_db/` 已被 Git 忽略，不会上传学生的本地数据。

需要从空库重新开始时：

```bash
rm -rf chroma_db
python 02_chroma_quickstart.py
```

不要把不同 embedding 模型产生的向量手动混到同一个 collection 中。本 demo 会按模型自动分目录，
例如 `chroma_db/voyage-voyage-4-lite-1024d/`。

## 运行顺序

```bash
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

Voyage 负责 embedding。对话模型会自动选择：设置了
`OPENAI_API_KEY` 就用 OpenAI；否则使用本机 Ollama `qwen2.5:7b`。
因此已安装并启动 Ollama 时，`--chat` 不需要 OpenAI Key。

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
