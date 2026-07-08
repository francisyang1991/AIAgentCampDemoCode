# L5 Demo Code 运行指南

本文档提供第 5 节 MCP demo code 的标准运行流程。建议先按照本文命令完成环境检查与一键运行，再根据需要单独运行某个 demo 文件。

## 0. 进入项目目录

```bash
cd unit2/lesson05/demo_code
```

确认当前目录：

```bash
pwd
ls
```

目录中应包含以下文件：

```text
01_minimal_mcp_server.py
02_connect_stdio.py
03_filesystem_server.py
04_resources_demo.py
05_your_mcp_agent.py
06_apify_linkedin_jobs_mcp.py
07_agent_autonomous_mcp.py
run_l5_demo.py
sample_docs/
```

## 1. 初始化运行环境

```bash
python3 run_l5_demo.py --setup-only
```

看到 `Setup complete.` 表示环境初始化完成，可以继续执行下一步。

如果出现 `python: command not found`，请使用 `python3` 执行命令。

## 2. 运行 L5 主线 Demo

```bash
python3 run_l5_demo.py
```

该命令会依次运行：

```text
01 自建 ResuMatch MCP Server 自检
02 用 MCPServerStdio 接入自建 Server
04 读取 MCP Resource：rubric://{role}
03 接官方 filesystem MCP，只读读取 resume.md / jd.txt
05 同时接 filesystem MCP + ResuMatch MCP
07 Agent 自主调用 MCP 彩排
```

成功标准：终端最后显示：

```text
All selected L5 demos finished.
```

## 3. 运行真实 Agent 自主调用 MCP Demo

如需运行真实 Agent 模式，请先配置 OpenAI API Key：

```bash
export OPENAI_API_KEY="sk-..."
```

然后运行：

```bash
python3 run_l5_demo.py --demo 07 --agent
```

成功时应看到类似输出：

```text
[真实 Agent 自主调用模式]
--- Agent Loop Trace ---
ToolCall -> ...
ToolOut  -> ...
最终回答
```

未配置 OpenAI API Key 时，可以运行离线彩排模式：

```bash
python3 run_l5_demo.py --demo 07
```

该模式会运行“离线 Agent Loop 彩排”。彩排中的每一步都是真实 MCP 工具调用，但工具选择过程由脚本显式打印；如需展示模型自主选择工具，请使用上方 `OPENAI_API_KEY + --agent` 的真实 Agent 模式。

## 4. 运行 LinkedIn 岗位搜索 MCP Demo

如需运行 LinkedIn 岗位搜索 demo，请先配置 Apify token：

```bash
export APIFY_API_TOKEN="apify_api_..."
python3 run_l5_demo.py --demo 06
```

成功时应看到类似输出：

```text
已连接 Apify MCP
调用 Apify Actor
读取 MCP dataset items
真实岗位结果
```

不要将 token 写入 `.py` 文件，也不要提交到 Git 仓库。

## 5. 单独运行指定 Demo

```bash
python3 run_l5_demo.py --demo 01
python3 run_l5_demo.py --demo 02
python3 run_l5_demo.py --demo 03
python3 run_l5_demo.py --demo 04
python3 run_l5_demo.py --demo 05
python3 run_l5_demo.py --demo 07
```

也可以逐个运行 demo 文件。请先确保已完成第 1 步环境初始化：

```bash
.venv/bin/python 01_minimal_mcp_server.py --selftest
.venv/bin/python 02_connect_stdio.py
.venv/bin/python 04_resources_demo.py
.venv/bin/python 03_filesystem_server.py
.venv/bin/python 05_your_mcp_agent.py
.venv/bin/python 07_agent_autonomous_mcp.py
```

## 6. Demo 对照表

| Demo | 重点 | 成功标志 |
|---|---|---|
| 01 | 自建 MCP Server | `parse_jd` / `score_resume` 自检通过 |
| 02 | `MCPServerStdio` 接自建 Server | 打印 `parse_jd -> score_resume` |
| 03 | 接官方 filesystem MCP | 读到 `resume.md` / `jd.txt`，列出缺口 |
| 04 | MCP Resource | 读到 `rubric://senior-ml-engineer` |
| 05 | 同时接入两个 MCP Server | `filesystem.read_file -> parse_jd -> score_resume` |
| 06 | 第三方 Apify MCP | 输出真实 LinkedIn 岗位链接 |
| 07 | Agent 自主调用 MCP | 无 key 查看彩排；有 key 查看真实 ToolCall trace |

## 7. 常见问题处理

### `ModuleNotFoundError: agents` 或 `ModuleNotFoundError: mcp`

请先运行：

```bash
python3 run_l5_demo.py --setup-only
```

### `npx: command not found`

03/05/06/07 需要 Node.js。请先尝试：

```bash
python3 run_l5_demo.py --demo 03
```

如果仍然失败，请安装 Node.js，并检查：

```bash
npx --version
```

### `缺少 APIFY_API_TOKEN`

仅 06 需要设置该 token：

```bash
export APIFY_API_TOKEN="apify_api_..."
python3 run_l5_demo.py --demo 06
```

### `AuthenticationError`

仅真实 Agent 模式需要 OpenAI API Key：

```bash
export OPENAI_API_KEY="sk-..."
python3 run_l5_demo.py --demo 07 --agent
```

### 直接运行 `python 01_minimal_mcp_server.py` 后终端停住

这是正常现象。`01_minimal_mcp_server.py` 是 MCP Server，直接运行时会等待 MCP client 连接。

如需自检，请运行：

```bash
python3 run_l5_demo.py --demo 01
```

或运行：

```bash
.venv/bin/python 01_minimal_mcp_server.py --selftest
```
