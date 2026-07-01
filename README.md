# AI Agent Camp Demo Code

这个仓库用于给学生分发 AI Agent 课程的课件 PDF 和课堂 demo code。

## 目录

- `unit1/lesson01/slides.pdf`：Unit 1 第 1 节课件，什么是 AI Agent
- `unit1/lesson02/slides.pdf`：Unit 1 第 2 节课件，OpenAI Agents SDK 入门
- `unit1/lesson02/demo_code/`：Unit 1 第 2 节课堂演示代码
- `unit1/lesson03/slides.pdf`：Unit 1 第 3 节课件，系统提示词与角色设计
- `unit1/lesson03/demo_code/`：Unit 1 第 3 节课堂演示代码与 P1 骨架

## 运行课堂 demo

推荐学生直接用 Cursor 打开对应 demo 目录。下面以第 3 节为例：

```bash
cd unit1/lesson03/demo_code
cursor .
```

然后在 Cursor 终端里一键安装依赖：

```bash
bash setup.sh
```

安装完成后运行：

```bash
source .venv/bin/activate
python 01_same_model_diff_prompt.py
```

模型后端三选一：

- OpenAI：设置 `OPENAI_API_KEY`，也可以复制 `.env.example` 为 `.env` 后填写
- 本地 Ollama：不设 `OPENAI_API_KEY`，安装 Ollama 后运行 `ollama pull qwen2.5:7b`
- 其他 OpenAI-compatible 模型：设置 `OPENAI_BASE_URL`、`OPENAI_API_KEY`、`OPENAI_MODEL`，并设置 `OPENAI_API_MODE=chat_completions`

更详细的课堂运行说明在对应的 `unit1/lessonXX/demo_code/README.md`。
