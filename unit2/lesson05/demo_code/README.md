# 第 5 节 · MCP 协议与 Server 调用 演示代码

> 配套课件：`../slides.pdf`
> 上节你会写本地工具了；这节用 **MCP 标准协议**接入整个工具生态——"工具界的 USB-C"。
> 从最小 MCP Server，到接入官方现成 Server，再到本地工具 + MCP 工具并存（P2 起点）。在 **Cursor** 里逐个跑。
>
> 🧩 **全课统一主题：求职助手 ResuMatch**（按 JD 定制简历要点 + cover letter）。
> 本节 MCP 的教学骨架不变，只把"演示用的数据/场景"贴到求职上：最小 server 用 `FastMCP` 暴露两个
> 自建工具 `parse_jd`（JD→结构化字段）、`score_resume`（简历对着技能打 0-100 分），只读资源
> `rubric://{role}`（按岗位返回评分细则），外加一个可复用 prompt `improve_resume`；
> `03` 用官方 filesystem 读 `sample_docs/` 里真实的简历/JD 文件——这正是 ResuMatch 的真实用法。
> 打分是**程序算出的确定值**（命中/总数），不靠模型估计。红线（全课一致）：**绝不编造**用户没有的经历/学历/数字。

## 最快跑起来

```bash
cd unit2/lesson05/demo_code
cursor .
python3 run_l5_demo.py --setup-only
python3 run_l5_demo.py
```

这会自动创建/使用 `.venv`、安装依赖，并按顺序跑通 `01 -> 02 -> 04 -> 03 -> 05 -> 07`。

只跑某一个 demo：

```bash
python3 run_l5_demo.py --demo 03
```

跑 Apify LinkedIn Jobs 真实岗位搜索：

```bash
export APIFY_API_TOKEN="apify_api_..."
python3 run_l5_demo.py --demo 06
```

展示**真实 Agent 自主调用 MCP**：

```bash
export OPENAI_API_KEY="sk-..."
python3 run_l5_demo.py --demo 07 --agent
```

> 没有 OpenAI Key 时，`07` 会自动跑“离线 Agent Loop 彩排”：每一步都是真 MCP 工具调用，但决策轨迹由脚本打印，适合先排查环境。真实模型自主调用请用上面的 `--agent` 命令。

更完整的运行步骤见：[L5_DEMO_RUNBOOK.md](./L5_DEMO_RUNBOOK.md)。

---

## 前置

- **Python 3.10+**（推荐 3.11+）
- **Cursor**（推荐）：用来打开文件夹、运行终端、让 AI 帮你解释报错
- 默认 smoke test 不需要 OpenAI Key；只有 `python3 run_l5_demo.py --demo 07 --agent` 的真实 Agent 模式需要 OpenAI Key。
- **`03` / `05` / `06` 需要 Node.js / npx**（官方 filesystem server、`mcp-remote` 都通过 npx 跑）；其余文件**纯 Python**。
  - 检查 npx：终端敲 `npx --version`，有版本号即可；没有去 [nodejs.org](https://nodejs.org) 装。

## 安装

推荐直接让 runner 安装：

```bash
python3 run_l5_demo.py --setup-only
```

手动安装才用下面这段：

```bash
pip install -r requirements.txt
```

等价于：

```bash
pip install openai-agents mcp python-dotenv
```

- `openai-agents` —— Agents SDK，提供 `Agent` / `Runner` 和 `agents.mcp`（客户端）。
- `mcp` —— 官方 MCP SDK，提供 `FastMCP`（写 server 用）。

## 设置 Key（只在可选真实 Agent / Apify 模式需要）

最省心的方式：复制 `.env.example` 成 `.env`，然后在 `.env` 里填需要的变量。

真实 Agent 模式：

```bash
export OPENAI_API_KEY="sk-..."
python3 run_l5_demo.py --demo 07 --agent
```

Apify LinkedIn Jobs MCP：

```bash
export APIFY_API_TOKEN="apify_api_..."
python3 run_l5_demo.py --demo 06
```

> 用环境变量，**别把 Key 写进代码、别提交到 Git**。

## 在 Cursor 里怎么跑

1. `File → Open Folder` 打开 `unit2/lesson05/demo_code/`
2. 打开内置终端（``Ctrl+` ``），优先运行：

```bash
python3 run_l5_demo.py
```

如果你想逐个文件讲，再按顺序运行：

```bash
# 01 是 server，不用直接对话——它由 02 / 04 / 05 自动当子进程启动
.venv/bin/python 01_minimal_mcp_server.py --selftest  # 离线自检两个工具（不连模型/不走协议）
.venv/bin/python 02_connect_stdio.py      # 连上 01，列出工具并走 parse_jd→score_resume
.venv/bin/python 04_resources_demo.py     # 演示 Resources 模板 rubric://{role}
.venv/bin/python 03_filesystem_server.py  # 接官方 filesystem server + 只读过滤（需要 npx）
.venv/bin/python 05_your_mcp_agent.py     # 自建 Server + 官方 Server 同挂（P 起点，需 npx）
.venv/bin/python 06_apify_linkedin_jobs_mcp.py  # Extra：接 Apify LinkedIn Jobs MCP 搜真实岗位（需 APIFY_API_TOKEN）
.venv/bin/python 07_agent_autonomous_mcp.py     # Agent 自主调用 MCP：无 key 跑彩排，有 key 跑真实 Agent 模式
```

3. **Cursor 小技巧**：`Cmd/Ctrl + K` 让它直接改代码；`Cmd/Ctrl + L` 问它问题；选中报错让它解释。

> **关键概念**：MCP 客户端是**异步**的，所以所有连接代码都包在 `async def main()` 里，
> 最后用 `asyncio.run(main())` 启动。这是本节最容易踩的坑——别忘了 `await` 和 `asyncio.run`。

---

## 文件清单（循序渐进）

| 文件 | 学到什么 | 求职示例 | 对应课件 | 需要 npx？ |
|------|----------|----------|----------|:---:|
| `run_l5_demo.py` | **一键入口**：建 `.venv`、装依赖、按顺序跑 demo | 推荐作为首次运行入口 | 课堂/作业入口 | 视 demo 而定 |
| `01_minimal_mcp_server.py` | 用 `FastMCP` 写最小 **Server**：`@mcp.tool()` / `@mcp.resource()` / `@mcp.prompt()` | 工具 `parse_jd` + `score_resume`、资源 `rubric://{role}`、prompt `improve_resume`（`--selftest` 可离线自检） | P5 自建 Server | 否 |
| `02_connect_stdio.py` | 用 `MCPServerStdio` **接入** 01，列工具 + 直接调用 MCP 工具链 | 通过 MCP 串 `parse_jd`→`score_resume` 算匹配分、列缺口 | P4 接入 Server | 否 |
| `03_filesystem_server.py` | 接**官方现成 Server**（filesystem），并用 `create_static_tool_filter` **限制只读** | 只保留 `read_file`/`list_directory` 读 `sample_docs/` 里真实 `resume.md` + `jd.txt`；默认不依赖模型 | P4 生态 · 只读沙箱 | **是** |
| `04_resources_demo.py` | **Resources**：列出并读取只读资源模板（无需 Key/模型） | 读评分细则资源 `rubric://{role}`（任意岗位同一份标准） | P3 三元抽象 | 否 |
| `05_your_mcp_agent.py` | **自建 Server + 官方 Server 同挂**（P 起点） | filesystem 读文件 + 自建 `parse_jd`/`score_resume` 打分；默认确定性链路，可选 Agent 模式 | P4/P6 合流 | 是（无则自动降级为仅自建） |
| `06_apify_linkedin_jobs_mcp.py` | **第三方真实 MCP**：通过 `mcp-remote` 接 Apify LinkedIn Jobs Scraper | 直接调用 MCP 工具搜真实 LinkedIn 岗位，返回岗位名/公司/地点/链接；不依赖模型，适合课堂 smoke test | Extra · 搜索 MCP | **是** |
| `07_agent_autonomous_mcp.py` | **Agent 自主调用 MCP**：一个 Agent 挂两个 MCP Server | 无 key 时跑离线 Agent Loop 彩排；有 OpenAI Key + `--agent` 时跑真实模型自主调用 | Agent Loop · MCP 编排 | **是** |

> `sample_docs/` —— 给 `03` 用的示例文档：`resume.md`（示例简历）+ `jd.txt`（示例 JD）。
> 把它换成你自己的简历文件夹，Agent 就能通过 MCP 读你真实的简历/JD（ResuMatch 的真实用法）。

---

## 常见报错

| 报错 | 原因 | 解决 |
|------|------|------|
| `python: command not found` | macOS / 新环境只有 `python3` | 把命令里的 `python` 换成 `python3` |
| `.venv/bin/python: No such file` | 还没建虚拟环境 | 先跑 `python3 run_l5_demo.py --setup-only` |
| `ModuleNotFoundError: mcp` | 没装 MCP SDK | `pip install mcp` |
| `ModuleNotFoundError: agents` | 没装 Agents SDK / 装错环境 | `pip install openai-agents` |
| `AuthenticationError` | 真实 Agent 模式下 Key 未设置或配置错误 | 默认 smoke test 不需要 OpenAI Key；如果运行 `python3 run_l5_demo.py --demo 07 --agent`，请检查 `OPENAI_API_KEY` |
| `npx: command not found`（03/05/06） | 没装 Node.js，或 shell PATH 没带 Node | 优先用 `python3 run_l5_demo.py`；它会自动补常见 Node 路径。仍失败就装 [Node.js](https://nodejs.org)，再 `npx --version` 验证 |
| `缺少 APIFY_API_TOKEN`（仅 06） | 未设置 Apify token | `export APIFY_API_TOKEN="apify_api_..."` 后重跑；不要写进代码 |
| 06 返回空结果或失败 | token 无效、Apify 额度不足、Actor 限流、LinkedIn 搜索条件太窄 | 换关键词/地点，检查 Apify 控制台额度与运行日志 |
| 03 第一次卡很久 | npx **首次联网**下载 server 包 | 等一会儿；已把超时调到 30s，网络差可再调大。装好后有缓存，断网也能再跑 |
| 03 说"目录不允许访问" | 沙箱目录写错，或文件不在 `sample_docs/` 里 | server 只能读授权目录；确认 `sample_docs/resume.md`、`jd.txt` 在位 |
| `RuntimeError: ... no running event loop` | 忘了用 `asyncio.run()` | MCP 客户端是异步的，入口要 `asyncio.run(main())` |
| `FileNotFoundError: 01_minimal_mcp_server.py` | 不在 demo_code 目录里跑 | **必须 `cd` 进 `demo_code/` 再运行**（02/04/05 把 01 当子进程，路径是相对的） |

---

## 🎯 本节作业目标（基础必达 + 进阶挑战）

**🎯 基础 Goal**
- 用 `MCPServerStdio` 接通一个 MCP Server（filesystem 或自写最小 server），Agent 能调到 MCP 工具。
- 求职向：把 `03` 的沙箱指向你自己的简历目录，让 Agent 通过 MCP 读你真实的简历/JD 文件。

**🚀 Extra Challenge**
- 🌶️🌶️ 给你选题写一个最小 MCP Server（2 个 tool + 1 个 resource）。求职向已在 `01` 给出样板：`parse_jd` / `score_resume` + 资源模板 `rubric://{role}`（再加分：`@mcp.prompt` `improve_resume`）。
- 🌶️🌶️ 用 `create_static_tool_filter` 的 `blocked_tool_names` 做一组「写工具被拦截」对照实验，或接一个第三方真实 MCP（sqlite / git / 搜索）。求职向可以跑 `06_apify_linkedin_jobs_mcp.py` 接 Apify LinkedIn Jobs MCP，再写 3 条「本地 function_tool vs MCP 工具」的取舍（例如：`search_jobs` 适合第三方 MCP，`score_resume` 适合自建 MCP）。
