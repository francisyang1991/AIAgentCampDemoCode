# 第 7 节 Demo｜Session 与工作记忆

这组代码回答六个问题：

1. 对话历史存在哪里？
2. 这一轮究竟发多少内容给模型？
3. 地点、签证等重要事实怎样避免被裁掉？
4. 网络重试怎样避免重复写入？
5. 两个标签页同时写，怎样发现冲突？
6. 会话归档和删除有什么区别？

## 先跑基础路线

```bash
pip install -r requirements.txt

python 01_no_memory.py
python 02_sqlite_session.py
python 03_inspect_history.py
python 04_sliding_window.py
python 05_summary_memory.py
python 06_state_slots.py
python 07_session_idempotency.py
python 08_session_concurrency.py
python 09_session_lifecycle.py
```

默认命令优先跑离线、可重复的演示，不会突然进入聊天循环。

## 九个 Demo 怎样连起来

| Demo | 先看什么 | 掌握要求 |
|---|---|---|
| `01_no_memory.py` | 两次独立调用为什么接不上 | 必会 |
| `02_sqlite_session.py` | 同一 Session 怎样接上上一轮 | 必会 |
| `03_inspect_history.py` | Session 里存的就是消息列表 | 必会 |
| `04_sliding_window.py` | 完整保存和本轮发送是两件事 | 必会 |
| `05_summary_memory.py` | 历史太长时可以压成简版 | 看懂即可 |
| `06_state_slots.py` | 硬事实放结构化 state，不跟历史一起裁 | 进阶 |
| `07_session_idempotency.py` | 同一个请求重试两次，只写一次 | 工程补充 |
| `08_session_concurrency.py` | 版本号怎样阻止静默覆盖 | 工程补充 |
| `09_session_lifecycle.py` | active、archived、deleted 的区别 | 工程补充 |

## 联网和交互模式

```bash
# 真正调用模型，需要 OPENAI_API_KEY
python 01_no_memory.py --live
python 02_sqlite_session.py --live
python 05_summary_memory.py --live
python 06_state_slots.py --live

# 聊天模式只在明确需要时开启
python 02_sqlite_session.py --chat
python 06_state_slots.py --chat
```

Key 只放环境变量，不写进代码，也不提交到 Git。

## 作业最小要求

- 一个稳定的 `session_id`。
- 连续至少 10 轮的固定测试。
- 证明 Session 保存的条数大于本轮送给模型的条数。
- 裁剪后仍能通过地点、签证等硬约束断言。

不要求背 `OpenAIResponsesCompactionSession` 的完整配置。先把“保存全部”和“本轮只发需要的”讲清楚。
