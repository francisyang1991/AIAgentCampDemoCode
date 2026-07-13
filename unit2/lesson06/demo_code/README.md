# 第 6 节 · 多工具协同与错误恢复 演示代码

> 配套课件：`../slides.pdf`
> 本节交付 **P2**：你的 Agent 接上 **≥1 个本地工具 + 1 个 MCP 工具**，能多工具协同、能优雅处理失败。
> 循序渐进，在 **Cursor** 里逐个跑。

## 最快跑起来

用 Cursor 打开本目录，在内置终端运行：

```bash
cd unit2/lesson06/demo_code
cursor .
bash setup.sh
source .venv/bin/activate
python3 01_two_local_tools.py
```

`setup.sh` 会自动选择合适的 Python、创建 `.venv` 并安装依赖。首次完成后，后续只需激活环境并运行想看的 demo。

---

## 前置

- **Python 3.10+**（推荐 3.11+）。MCP 部分需要 3.10+；低于 3.10 时 demo 05 会自动降级为"仅本地工具"。
- 模型后端三选一：OpenAI、本地 Ollama，或其他 OpenAI-compatible 服务。没有 Key 时也会给出友好提示，不会抛出长 traceback。
- **Node.js ≥ 18**（含 `npx`）—— 仅 demo 05 的 MCP 文件系统 Server 需要；没装也能跑（自动降级）。

## 安装

推荐一键安装：

```bash
bash setup.sh
```

手动安装时才使用 `python3 -m pip install -r requirements.txt`。

## 设置 Key

最省心的方式是复制配置模板，再填写其中一种后端：

```bash
cp .env.example .env
```

- OpenAI：填写 `OPENAI_API_KEY`，可选填 `OPENAI_MODEL`
- 本地 Ollama：保持 `OPENAI_API_KEY` 为空，启动 Ollama；默认使用 `qwen2.5:7b`
- 其他兼容服务：填写 `OPENAI_BASE_URL`、`OPENAI_API_KEY`、`OPENAI_MODEL`，并使用 `OPENAI_API_MODE=chat_completions`

> 用环境变量，**别把 Key 写进代码、别提交到 Git**。
> 没设 Key 也不会崩——每个 demo 都有离线提示，告诉你"本该发生什么"。

## 在 Cursor 里怎么跑

1. `File → Open Folder` 打开本文件夹 `demo_code/`
2. 打开内置终端（`` Ctrl+` ``），按顺序运行：

```bash
python3 01_two_local_tools.py
python3 02_multi_step_task.py
python3 03_tool_chaining.py
python3 03b_real_api_tool.py
python3 04_error_recovery.py
python3 05_p2_assistant.py
```

3. **Cursor 小技巧**：`Cmd + K` 让它直接改代码；`Cmd + L` 问它问题；选中报错让它解释。

---

## 文件清单（循序渐进 · 每个只加一个新概念）

> 主线：**ResuMatch 求职助手**。四把本地工具串成一条链——读 JD、搜岗位、对照简历打分、给改写建议——外加一把 MCP 工具把报告落盘。

| 文件 | 学到什么 | 对应课件 |
|------|----------|----------|
| `01_two_local_tools.py` | 一个 Agent 挂 **2 把本地工具**（`parse_jd` / `search_jobs`），靠 name/description **按需选用** | 多工具并存·选工具 |
| `02_multi_step_task.py` | 一句话触发 **多步链**（`parse_jd`→`score_resume`→`suggest_rewrite`），用 `result.new_items` 看 **ReAct 循环** | ReAct 多步 trace |
| `03_tool_chaining.py` | **工具间传值**：`parse_jd` 返回的 `must_have` 字段喂给 `score_resume` 当输入 | 工具数据传递 |
| `04_error_recovery.py` | 工具内 `try/except` → **友好错误**，模型据此恢复；真实 `search_jobs` 中途超时也不崩；`max_turns` **兜底** | 失败恢复 + 防死循环 |
| `05_p2_assistant.py` | **P2 模板**：本地工具链 + **MCP 工具**（把匹配报告写进沙箱文件）协同（多轮 + 记忆），缺环境自动降级 | 交付 P2 |
| `03b_real_api_tool.py` 🚩 | **旗舰·ResuMatch**：`search_jobs` 调**真实** HN Algolia 招聘搜索接口（无需 Key），`tenacity` **指数退避重试** + 超时 + 结构化返回 `JobSearch`；断网回退内置样例 | 真·外部 API + 限流/超时（兑现 P2 🌶️🌶️🌶️）|

> 🚩 这是"工业界工具长什么样"的模板：真 HTTP、会失败、有重试、返回结构化数据。把 `search_jobs` 换成你选题里任何真实接口，这套骨架照搬。`python3 03b_real_api_tool.py` 断网也能跑（自动回退样例并诚实标注为 `offline-sample`）。

---

## demo 05 说明（P2 模板）

- 启用 MCP 的条件：装了 **Node（npx 可用）** 且 `import agents.mcp` 正常（Python 3.10+）。
  满足时 → 自动用 `npx -y @modelcontextprotocol/server-filesystem` 起一个文件系统 Server，
  Agent 就能 **读 / 写 / 列** 一个沙箱目录 `demo_code/p2_workspace/`（最后一步把匹配报告写进 `report.md`）。
- 不满足时 → 打印一行 `[降级] …`，退回"仅本地工具"模式，照常多轮对话，**不崩**。
- 改造成你的 P2：把顶部 `INSTRUCTIONS` 换成你的选题角色；把本地工具链 `parse_jd`/`score_resume`/`suggest_rewrite` 换成你自己的工具；
  MCP 想换别的 Server（如 git / sqlite / 你自己的 Server）也行——课件最后一页有指引。

> **沙箱安全**：文件系统 Server 只被授权操作 `p2_workspace/` 这一个目录，碰不到你电脑别处，放心试。

---

## 常见报错

| 报错 | 原因 | 解决 |
|------|------|------|
| `ModuleNotFoundError: agents` | 没装 / 装错环境 | `pip install -r requirements.txt` |
| `.venv/bin/python: No such file` | 还没完成安装 | 先运行 `bash setup.sh` |
| `python: command not found` | macOS 默认只有 `python3` | 使用 `python3`，或先激活 `.venv` |
| `AuthenticationError` / `OpenAIError: OPENAI_API_KEY is not set` | Key 没设或写错 | 检查 `OPENAI_API_KEY`（没 Key 时 demo 仍有离线提示） |
| `ImportError: ... agents.mcp` 或 demo 05 显示 `[降级]` | Python < 3.10 或缺 `mcp` 包 | 升到 **3.10+** 并 `pip install mcp`；不升也能跑（仅本地工具） |
| demo 05 卡在启动 / `npx` 报错 | 没装 Node，或首次下包慢/被墙 | 装 **Node ≥ 18**；首次会下载 Server 包，多等几秒；实在不行就用降级模式 |
| `MaxTurnsExceeded` | 任务步数超过 `max_turns` | 这是**兜底正常行为**（demo 04 故意演示）；正式用调大 `max_turns` 或缩小任务 |
| `Unable to evaluate type annotation 'X \| None'` | Python 版本太老 | 用 **3.10+** |
| 连接超时 / 没反应 | 网络或代理 | 确认网络可访问 API |

---

## 🎯 本节作业目标（基础必达 + 进阶挑战）

**🎯 基础 Goal**
- ≥1 本地 + 1 MCP 工具并存；一段多轮对话里两类工具都被调用到；工具失败有兜底（不崩）。

**🚀 Extra Challenge**
- 🌶️🌶️ 实现真正的多步任务（工具链：A 的输出喂给 B），打印 ReAct 轨迹。
- 🌶️ 加 `max_turns` 防死循环，并演示一次触发。
- 🌶️🌶️🌶️ 给一个工具接**真实外部 API**（天气/汇率/搜索）替换假数据，处理超时与限流。
