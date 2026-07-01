# 第 3 节 · 系统提示词与角色设计 演示代码

> 配套课件：`../slides.pdf`
> 这节给上节那个"通用助手"一个**灵魂**——用 System Prompt 定义角色与边界，搭出 P1 骨架。在 **Cursor** 里逐个跑。

> 🎯 **本课贯穿主题：求职助手 ResuMatch**——按某个目标岗位 / JD，把已有简历要点重排、起草 cover letter。
> 全套 demo 都用这个主题。它最值得学的是【边界】红线：**绝不编造用户没有的经历 / 数字**——
> 这比"日程助手礼貌拒绝写代码"有真实后果得多（编造会让求职者面试翻车），正是 P1 该死守的东西。

---

## 前置

- **Python 3.10+**（推荐 3.11+）
- **Cursor**（推荐）：用来打开文件夹、运行终端、让 AI 帮你解释报错
- 模型后端：OpenAI、其他 OpenAI-compatible 服务、本地 Ollama，三选一
- 已跑通第 2 节的 demo（会创建、会调用 Agent）

## 最快跑起来

```bash
# 1. 进入 demo 目录
cd unit1/lesson03/demo_code

# 2. 用 Cursor 打开当前目录（如果已经在 Cursor 里，可以跳过）
cursor .

# 3. 一键安装依赖
bash setup.sh

# 4. 激活环境，再跑第一个 demo
source .venv/bin/activate
python 01_same_model_diff_prompt.py
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
python 01_same_model_diff_prompt.py
```

没设 `OPENAI_API_KEY` 但 Ollama 正在运行时，demo 会自动走本地模型。弱机可以换小模型：

```bash
LOCAL_MODEL=qwen2.5:3b python 01_same_model_diff_prompt.py
```

### 方式 C：其他 OpenAI-compatible 模型

很多模型服务提供 OpenAI-compatible API。把地址、key、模型名填进去即可：

```bash
export OPENAI_BASE_URL="https://your-provider.example/v1"
export OPENAI_API_KEY="your-provider-key"
export OPENAI_MODEL="your-model-name"
export OPENAI_API_MODE="chat_completions"
python 01_same_model_diff_prompt.py
```

> 用环境变量，**别把 Key 写进代码、别提交到 Git**。可以参考 `.env.example`，但真正的 `.env` 不要上传。

> 没设 Key 也没装 Ollama？直接跑会给你**一句友好提示**，不会再甩一长串报错。

## 在 Cursor 里怎么跑

1. `File → Open Folder` 打开 `unit1/lesson03/demo_code/`
2. 打开内置终端（``Ctrl+` ``）
3. 第一次运行先执行 `bash setup.sh`
4. 按顺序运行：

```bash
python 01_same_model_diff_prompt.py
python 02_anatomy.py
python 03_boundaries.py
python 04_few_shot_format.py
python 05_your_assistant.py
python 06_variables_in_prompt.py
python 07_prompt_injection_defense.py
```

5. 跑 **P1 骨架模板**（你 P1 要交的就是这个结构）：

```bash
cd p1_skeleton
python main.py
```

6. **Cursor 小技巧**：`Cmd/Ctrl + K` 让它直接改代码；`Cmd/Ctrl + L` 问它问题；选中报错让它解释。角色和边界你来定，让 Cursor 帮你润色措辞。

---

## 文件清单（循序渐进）

> 全部以**求职助手 ResuMatch**为例（教学目的不变，只是把例子领域统一成求职/简历）。

| 文件 | 学到什么 | 求职示例 | 对应课件 |
|------|----------|----------|----------|
| `01_same_model_diff_prompt.py` | 同一模型，**换 Prompt = 换助手** | 弱提示 vs 五块结构提示，同一个"帮我改简历贴岗位"问两遍 | WHY · Prompt 的威力 |
| `02_anatomy.py` | 好提示词的 **5 块结构**（角色/能力/边界/风格/格式） | 用 ResuMatch 五块拆给你看（同 `prompts_resume.py` 结构） | ANATOMY |
| `03_boundaries.py` | **边界**：拒绝越界 / 信息不足先反问 / **绝不编造** | 现场诱导它编一段没做过的实习，看它守住红线 | 边界三件套 |
| `04_few_shot_format.py` | **Few-shot 示例 + 固定输出格式**（JSON） | 把一条原始经历按目标岗位重排成结构化简历要点 | TECHNIQUES |
| `05_your_assistant.py` | **你的助手**骨架：多轮 + 记忆（改 INSTRUCTIONS） | 先说目标岗位，再问"我还差什么"，看它记不记得 | BUILD P1 |
| `06_variables_in_prompt.py` | **进阶 ★**：指令里加**变量** —— 把 `{today}` 每轮注入（固定写前面、会变放后面） | 问"距周五截止还够时间吗"，它用注入的今天日期算天数 | 逐行读① · 变量/缓存前缀 |
| `07_prompt_injection_defense.py` | **进阶 ★**：**分隔符**防指令注入 —— 用 `<untrusted_data>` 圈住 JD/简历、声明"只当数据" | 埋雷简历（藏了"打 10/10"指令）被分隔符挡住，不照做 | 三层防御①数据分隔 |
| `p1_skeleton/` | **P1 项目模板**：`prompts.py` / `agent.py` / `main.py` | 默认就是 ResuMatch 求职助手，照改即可 | P1 骨架结构 |

---

## P1 骨架（`p1_skeleton/`）

学生 P1 交付的项目模板，**prompt 与逻辑分离**：

- `prompts.py` —— 只放 System Prompt（角色 + 边界），调角色只动这里（**默认范例：求职助手 ResuMatch**）
- `agent.py` —— Agent 定义（`name="ResuMatch"`），import 自 `prompts.py`
- `main.py` —— CLI 多轮循环 + `SQLiteSession`
- `p1_skeleton/README.md` —— 一句话说明 + 运行方式

### 🚩 详版范例 / 想换方向？

- `prompts_resume.py` —— **求职助手 ResuMatch 详版**（按 JD 定制简历 + cover letter，5 块写满）。红线：**绝不编造经历**。
  默认的 `prompts.py` 就是从它精简来的；想要更全的版本切到这个。
- `prompts_stock.py` —— ⚠️ **可选 · 非本课默认主题**：投研助手 EquityLens（多视角股票速读），给想做股票方向的同学的模板。红线：**不给买卖建议 + 必带免责声明**。

切换方法：把 `agent.py` 里的 `from prompts import SYSTEM_PROMPT`
改成 `from prompts_resume import SYSTEM_PROMPT`（或 `prompts_stock`），其余不动。
> 这套范例最值得学的是它们的【边界】——比"日程助手礼貌拒绝"有**真实后果**的红线，这正是 P1 的重点。

---

## 常见报错

| 报错 | 原因 | 解决 |
|------|------|------|
| `ModuleNotFoundError: agents` | 没装 / 没激活 `.venv` | 先 `bash setup.sh`，再 `source .venv/bin/activate` |
| `ModuleNotFoundError: prompts`（跑 main.py 时） | 没在 `p1_skeleton/` 目录里运行 | 先 `cd p1_skeleton` 再 `python main.py` |
| `AuthenticationError` | Key 没设或写错 | 检查 `OPENAI_API_KEY` |
| 模型不按格式输出 JSON | 提示词不够明确 | 把格式写死、加 few-shot 示例（见 `04`） |
| 连接超时 / 没反应 | 网络或代理 | 确认网络可访问 API |

---

## 🎯 本节作业目标（基础必达 + 进阶挑战）

**🎯 基础 Goal**
- `prompts.py` 写出五块结构系统提示（角色/能力/边界/风格/格式）。
- Agent 能稳定响应 1 类任务，多轮对话（SQLiteSession）不失忆。

**🚀 Extra Challenge**
- 🌶️ 加 few-shot 示例 + 强制 JSON 输出格式，并验证下游能稳定解析。
- 🌶️ 写 3 个边界测试（越权 / 信息不足 / 职责外），证明 Agent 守得住。
- 🌶️🌶️ 把 prompt 做成可配置（支持切换语气/详略），用一个开关切两种人设。
