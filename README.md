# AI Agent Camp Demo Code

这个仓库用于给学生分发 AI Agent 课程的课件 PDF 和课堂 demo code。

## 目录

- `unit1/lesson01/slides.pdf`：Unit 1 第 1 节课件，什么是 AI Agent
- `unit1/lesson02/slides.pdf`：Unit 1 第 2 节课件，OpenAI Agents SDK 入门
- `unit1/lesson02/demo_code/`：Unit 1 第 2 节课堂演示代码

## 运行第 2 节 demo

```bash
cd unit1/lesson02/demo_code
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python 01_hello_agent.py
```

没有配置 `OPENAI_API_KEY` 时，demo 会尝试使用本机 Ollama 的 `qwen2.5:7b` 模型。
