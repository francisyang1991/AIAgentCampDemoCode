# P1 骨架 · 你的 Agent 项目模板

一句话：用 System Prompt 给 Agent 定好角色和边界，跑通一个能多轮对话的骨架。

> 默认就是本课主题 **求职助手 ResuMatch**（按目标岗位定制简历，红线=绝不编造经历）；想换选题改 `prompts.py` 即可。

## 文件

| 文件 | 作用 |
|------|------|
| `prompts.py` | 只放 **System Prompt**（角色 / 能力 / 边界 / 风格 / 格式）。**默认范例：求职助手 ResuMatch**，要调角色只动这里。 |
| `agent.py` | **Agent 定义**（`name="ResuMatch"`），从 `prompts.py` 引入提示词。 |
| `main.py` | **命令行入口**：多轮对话循环 + `SQLiteSession` 记忆。 |
| `prompts_resume.py` | 求职助手 ResuMatch **详版**（5 块写满），默认 `prompts.py` 由它精简而来。 |
| `prompts_stock.py` | ⚠️ 可选·非本课默认：投研助手 EquityLens 模板，给想做股票方向的同学。 |

> 设计原则：**prompt 与逻辑分离**。以后打磨角色不动逻辑，加工具不动提示词。

## 运行

```bash
cd unit1/lesson03/demo_code
bash setup.sh
source .venv/bin/activate
cd p1_skeleton
python main.py
```

## 改成你的选题

1. 打开 `prompts.py`，把 `SYSTEM_PROMPT` 换成你选题的角色（照 5 块结构写）。
2. `python main.py` 跑起来，多聊几句，边聊边改 `prompts.py`。
3. 满意了 → 这就是你的 **P1 交付**。
