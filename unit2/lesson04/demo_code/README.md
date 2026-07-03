# 第 4 节 · Function Calling 与工具设计 演示代码

> 配套课件：`../slides.pdf`
> 主题：上节 Agent 有了角色（灵魂），这节给它一双**手**——会调用工具。
> **全课唯一主题：求职助手 ResuMatch**（按不同 JD 定制简历要点 + cover letter）。本节所有 demo 都围绕它的"手"——
> 岗位技能查询（`get_role_keywords`）、简历匹配评分（`score_resume`）、在招岗位搜索（`search_jobs`）。
> 循序渐进，从"看模型怎么请求调用工具"到"工具失败怎么优雅处理"。在 **Cursor** 里逐个跑。

---

## 前置

- **Python 3.10+**（推荐 3.11+）
- **Cursor**（推荐）：用来打开文件夹、运行终端、让 AI 帮你解释报错
- 模型后端：OpenAI、其他 OpenAI-compatible 服务、本地 Ollama，三选一
- 已学完第 2、3 节（认识 SDK、会用 instructions 定义角色）

## 最快跑起来

```bash
# 1. 进入 demo 目录
cd unit2/lesson04/demo_code

# 2. 用 Cursor 打开当前目录（如果已经在 Cursor 里，可以跳过）
cursor .

# 3. 一键安装依赖
bash setup.sh

# 4. 激活环境，再跑第一个 demo
source .venv/bin/activate
python 01_function_calling_basics.py
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
python 01_function_calling_basics.py
```

没设 `OPENAI_API_KEY` 但 Ollama 正在运行时，demo 会自动走本地模型。弱机可以换小模型：

```bash
LOCAL_MODEL=qwen2.5:3b python 01_function_calling_basics.py
```

### 方式 C：其他 OpenAI-compatible 模型

很多模型服务提供 OpenAI-compatible API。把地址、key、模型名填进去即可：

```bash
export OPENAI_BASE_URL="https://your-provider.example/v1"
export OPENAI_API_KEY="your-provider-key"
export OPENAI_MODEL="your-model-name"
export OPENAI_API_MODE="chat_completions"
python 01_function_calling_basics.py
```

> 用环境变量，**别把 Key 写进代码、别提交到 Git**。可以参考 `.env.example`，但真正的 `.env` 不要上传。

> 没设 Key 也没装 Ollama？直接跑会给你**一句友好提示**，不会再甩一长串报错。

## 在 Cursor 里怎么跑

1. `File → Open Folder` 打开 `unit2/lesson04/demo_code/`
2. 打开内置终端（``Ctrl+` ``）
3. 第一次运行先执行 `bash setup.sh`
4. 按顺序运行：

```bash
python 01_function_calling_basics.py
python 02_inspect_schema.py
python 03_good_vs_bad_tool.py
python 04_structured_return.py
python 04b_structured_resume_match.py
python 05_error_handling.py
```

5. **Cursor 小技巧**：`Cmd/Ctrl + K` 让它直接改代码；`Cmd/Ctrl + L` 问它问题；选中报错让它解释。

---

## 文件清单（循序渐进）

| 文件 | 学到什么 | 对应课件 |
|------|----------|----------|
| `01_function_calling_basics.py` | 用求职工具 `get_role_keywords`（岗位→技能）跑一遍，打印 `result.new_items`，**亲眼看模型怎么"请求"调用** | Function Calling 原理 |
| `02_inspect_schema.py` | 拿求职工具 `get_role_keywords` 打印 `@function_tool` **自动生成的 Schema**（name / description / 参数，含 `Literal` 枚举） | Tool Schema |
| `03_good_vs_bad_tool.py` | 同一功能两种写法：模糊的 `f1(a,b)` vs 清晰的 `score_resume(resume_text, jd_skills)`——**无描述/返回字符串** vs **清晰 docstring/结构化返回** | 设计原则·描述 |
| `04_structured_return.py` | **结构化返回**（`score_resume` 返回匹配分/缺口），缺口列表接力给 `suggest_focus`，两个工具串起来 | 设计原则·返回值 |
| `05_error_handling.py` | 岗位库没数据时 `return {"status":"error",...}`，Agent **优雅处理/反问**（重点）；**进阶**：`search_jobs` 真去 HTTP 搜在招岗位，`try/except` + 超时 + 离线兜底 | 失败处理 |
| `04b_structured_resume_match.py` 🚩 | **旗舰·求职助手**：`parse_jd`/`score_resume` 返回 **Pydantic 结构化**；匹配分**用程序算**（不靠模型猜）——结构化输出 + 可信评估的种子 | 设计原则·返回值（真实选题版）|

> 🚩 = 真实选题旗舰范例（对应第 1 节问卷最热的求职/简历方向）。运行同样 `python 04b_structured_resume_match.py`，断网也能跑（工具是确定性的，只有最后串联作答用模型）。
> 全节统一主题：求职助手 ResuMatch。**红线 = 绝不编造用户没有的经历/学历/数字**；缺口就如实标"待补强"。

---

## 工具设计表（动手填这张，再写代码）

下笔实现前，先把每个工具想清楚。复制下面这张表，给你选题的 Agent 设计 2 个工具：

| 工具名 (name) | 描述 (description) | 参数 | 返回 | 失败时 |
|---------------|--------------------|------|------|--------|
| `score_resume` | 对照岗位技能给简历算匹配分，需要评估匹配度时调用 | `resume_text: str`、`jd_skills: str`（逗号分隔技能） | `{status, score, matched, missing}` | 返回 `{status:"error", message}` |
| `（你的工具1）` | | | | |
| `（你的工具2）` | | | | |

**自检 checklist**（5 条都"是"才算立得住）：
- [ ] 单一职责：这工具只做一件事？
- [ ] 描述清楚：说清了"做什么 + 何时用 + 参数含义"？
- [ ] 参数有类型有描述：类型标注 + 枚举限定 + 逐个说明？
- [ ] 返回结构化带 status：dict + 状态字段，不是一句自由文本？
- [ ] 失败返回错误不崩：出错 `return` 结构化错误，而不是 `raise`？

---

## 常见报错

| 报错 | 原因 | 解决 |
|------|------|------|
| `ModuleNotFoundError: agents` | 没装 / 没激活 `.venv` | 先 `bash setup.sh`，再 `source .venv/bin/activate` |
| `AuthenticationError` | Key 没设或写错 | 检查 `OPENAI_API_KEY` |
| `Unable to evaluate type annotation 'float \| None'` | Python 版本太老 | 用 **3.10+** |
| `02` 里某个属性打印不出来 | SDK 版本属性名略有差异 | 脚本已 `try` 多个名字；以打印出来的为准 |
| 连接超时 / 没反应 | 网络或代理 | 确认网络可访问 API |

---

## 🎯 本节作业目标（基础必达 + 进阶挑战）

**🎯 基础 Goal**
- 为项目设计 2 个 `@function_tool`：清晰 docstring + 类型标注 + 结构化（dict + `status`）返回。

**🚀 Extra Challenge**
- 🌶️ 做「坏工具 vs 好工具」对比（模糊命名/无 docstring 那版），实测模型选错工具的概率。
- 🌶️🌶️ 给工具加输入校验 + 友好 error 返回，故意喂坏输入，看 Agent 能否优雅恢复并反问。
