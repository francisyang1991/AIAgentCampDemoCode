# 第 2 节 · OpenAI Agents SDK 演示代码

> 配套课件：`../slides.pdf`
> 循序渐进，从最简 Agent 到你自己的助手（P1 起点）。在 **Cursor** 里逐个跑。
>
> ★ **本课贯穿主题：求职助手 ResuMatch**——所有 demo 都围绕"帮你针对 JD 定制简历 + cover letter"
> 这一个场景，和大家一步步把它做起来。想做别的选题也行，把 `instructions` 换成你的角色即可。

---

## 前置

- **Python 3.10+**（推荐 3.11+）
- **Cursor**（推荐）：用来打开文件夹、运行终端、让 AI 帮你解释报错
- 模型后端：OpenAI、其他 OpenAI-compatible 服务、本地 Ollama，三选一

## 最快跑起来

```bash
# 1. 进入 demo 目录
cd unit1/lesson02/demo_code

# 2. 用 Cursor 打开当前目录（如果已经在 Cursor 里，可以跳过）
cursor .

# 3. 一键安装依赖
bash setup.sh

# 4. 激活环境，再跑第一个 demo
source .venv/bin/activate
python 01_hello_agent.py
```

安装脚本会自动创建 `.venv` 虚拟环境并安装 `requirements.txt`，不用手动找 package。

## 模型怎么选

### 方式 A：OpenAI

最省心的方式：复制 `.env.example` 成 `.env`，然后在 `.env` 里填：

```bash
OPENAI_API_KEY=sk-...
```

也可以直接在终端里设置：

```bash
export OPENAI_API_KEY="sk-..."
```

如果想指定模型，可以再加：

```bash
export OPENAI_MODEL="gpt-your-model-name"
```

### 方式 B：本地 Ollama（零成本，适合课堂试验）

安装 [Ollama](https://ollama.com)，然后：

```bash
ollama pull qwen2.5:7b
python 01_hello_agent.py
```

没设 `OPENAI_API_KEY` 但 Ollama 正在运行时，demo 会自动走本地模型。弱机可以换小模型：

```bash
LOCAL_MODEL=qwen2.5:3b python 01_hello_agent.py
```

### 方式 C：其他 OpenAI-compatible 模型

很多模型服务提供 OpenAI-compatible API。把地址、key、模型名填进去即可：

```bash
export OPENAI_BASE_URL="https://your-provider.example/v1"
export OPENAI_API_KEY="your-provider-key"
export OPENAI_MODEL="your-model-name"
export OPENAI_API_MODE="chat_completions"
python 01_hello_agent.py
```

> 用环境变量，**别把 Key 写进代码、别提交到 Git**。可以参考 `.env.example`，但真正的 `.env` 不要上传。

> 没设 Key 也没装 Ollama？直接跑会给你**一句友好提示**，不会再甩一长串报错。

## 在 Cursor 里怎么跑

1. `File → Open Folder` 打开 `unit1/lesson02/demo_code/`
2. 打开内置终端（``Ctrl+` ``）
3. 第一次运行先执行 `bash setup.sh`
4. 按顺序运行：

```bash
python 01_hello_agent.py
python 02_role_instructions.py
python 03_first_tool.py
python 03b_real_api_tool.py
python 04_streaming.py
python 05_your_assistant.py
python 06_structured_output.py
```

5. **Cursor 小技巧**：`Cmd/Ctrl + K` 让它直接改代码；`Cmd/Ctrl + L` 问它问题；选中报错让它解释。

---

## 文件清单（循序渐进）

| 文件 | 学到什么 | 对应课件 |
|------|----------|----------|
| `01_hello_agent.py` | 最简 Agent：**创建 + 调用**（ResuMatch 打招呼） | 上手·三要素 |
| `02_role_instructions.py` | 用 `instructions` 定义**角色与边界**（求职助手红线=不编造经历） | 上手 |
| `03_first_tool.py` | 加第一个**工具**（查岗位技能，写死版），亲眼看 **Agent Loop** | 原理 |
| `03b_real_api_tool.py` | 同样的工具改成**真 API**：真去搜在招岗位（httpx + 失败兜底） | 原理·进阶 |
| `04_streaming.py` | **流式输出**：边生成边显示一封 cover letter | 最新特性 |
| `05_your_assistant.py` | **你的 ResuMatch**：多轮 + 记忆，**这就是 P1 的起点** | 你的任务 |
| `06_structured_output.py` | **结构化输出**：把 JD 解析成 `JDProfile` 对象（给程序用） | 进阶·结构化 |

---

## 常见报错

| 报错 | 原因 | 解决 |
|------|------|------|
| `ModuleNotFoundError: agents` | 没装 / 没激活 `.venv` | 先 `bash setup.sh`，再 `source .venv/bin/activate` |
| `AuthenticationError` | Key 没设或写错 | 检查 `OPENAI_API_KEY` |
| `Unable to evaluate type annotation 'float \| None'` | Python 版本太老 | 用 **3.10+** |
| 连接超时 / 没反应 | 网络或代理 | 确认网络可访问 API |

---

## 🧪 没有简历可测试？用这套样例

跟 ResuMatch 聊天（`01` / `05`）时，它会让你"发简历/JD 过来"。没有的话，用 demo_code 里的样例：
- **`sample_resume.md`** — 一份英文样例简历（虚构 Data Analyst 候选人，故意留了缺口）
- **`sample_jd.md`** — 一份英文样例 JD

> 简历/JD 内容是**英文**（求职面向北美），对话你照常用中文问。

**最快测法**：把这两个文件**末尾的"One-line version"**各复制一行，粘进对话即可（聊天框是单行输入，多行简历贴不进去，用一行版最稳）。
试试：先粘**简历一行版**，再粘 **JD 一行版**，然后问「我这份简历投这个岗位，匹配上什么？还差什么？」——看它点出"缺 A/B testing、Tableau、年限"。

---

## 🎯 本节作业目标（基础必达 + 进阶挑战）

**🎯 基础 Goal**
- 跑通 `01–04` 四个 demo；把 `instructions` 改成自己选题的角色，单轮能答。

**🚀 Extra Challenge**
- 🌶️ 在你的选题上对比「弱提示词 vs 五块结构提示词」，记录 3 个具体输出差别。
- 🌶️🌶️ 用两个后端（本地 qwen vs 云端 glm-4-flash）各跑一遍，记下风格/质量/速度差异，写出你课程默认想用哪个及理由。
