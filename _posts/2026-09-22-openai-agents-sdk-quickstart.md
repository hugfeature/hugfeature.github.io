---
layout: post
title: "OpenAI Agents SDK 入门：从安装到第一个可调用工具的 Agent"
date: 2026-09-22 16:15:00 +0800
categories: [Agent-Harness, Tutorial]
permalink: /harness/openai-agents-sdk-quickstart/
description: "用一个最小可运行示例理解 OpenAI Agents SDK 的 Agent、Runner、Tool、Session 与 Trace，以及这些组件和 Harness 的关系。"
tags: ["agent-harness", "openai-agents-sdk", "tutorial", "agent-runtime"]
series: agent-harness
series_order: 4
---

> **Agent Harness 系列 #04**  
> 上一篇：[2026 年 Agent Harness / Runtime 工具有哪些？](/harness/agent-harness-runtime-tools-2026/)

这一篇不讲复杂架构。

目标只有一个：

**从零跑起一个真正会调用 Tool 的 Agent，然后看清 Harness 到底藏在哪里。**

我们用 OpenAI Agents SDK，因为它的抽象非常少：

```text
Agent
Runner
Tool
Session
Trace
```

跑完这个 Demo，你应该能够回答：

- Agent 是什么；
- Agent Loop 在哪里；
- Tool 谁执行；
- State 怎么保存；
- Trace 怎么产生。

> 本文按 2026-09-22 的官方 Python SDK 文档编写。

## 一、环境准备

官方当前安装方式：

```bash
pip install openai-agents
```

建议单独建虚拟环境。

### macOS / Linux

```bash
mkdir agents-demo
cd agents-demo

python -m venv .venv
source .venv/bin/activate

pip install openai-agents
export OPENAI_API_KEY="你的 API Key"
```

### Windows PowerShell

```powershell
mkdir agents-demo
cd agents-demo

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install openai-agents
$env:OPENAI_API_KEY="你的 API Key"
```

官方 Quickstart：

[OpenAI Agents SDK Quickstart](https://openai.github.io/openai-agents-python/quickstart/)

---

## 二、先跑最小 Agent

创建：

```text
main.py
```

写入：

```python
from agents import Agent, Runner

agent = Agent(
    name="Test Assistant",
    instructions=(
        "You are a concise software testing assistant. "
        "Answer the user's testing question directly."
    ),
)

result = Runner.run_sync(
    agent,
    "API 返回 500 时，最少应该检查哪些内容？",
)

print(result.final_output)
```

执行：

```bash
python main.py
```

如果能输出回答，第一个 Agent 就跑起来了。

但这里最值得看的不是答案。

而是这一行：

```python
Runner.run_sync(...)
```

## 三、Runner 就是理解 Harness 的入口

Agent 对象主要描述：

- 名字；
- Instructions；
- Tools；
- Handoffs；
- Guardrails；
- 输出行为。

真正驱动执行的是 Runner。

官方文档明确说明，Runner 会管理 Agent Loop。

最简化以后就是：

```text
Input
  ↓
Runner
  ↓
Model
  ↓
Tool Call?
  ├─ No → Final Output
  │
  └─ Yes
       ↓
   Execute Tool
       ↓
   Tool Result
       ↓
      Model
       ↓
      ...
```

这就是一个最小 Harness 的核心。

如果你不用 Agents SDK，直接使用更低层的 Responses API，那么：

**这个 Loop 就需要你自己写。**

---

## 四、给 Agent 加一个 Tool

下面做一个假的构建状态查询工具。

为了让示例可直接运行，我们不连真实 CI。

```python
from agents import Agent, Runner
from agents.decorators import tool


@tool
def get_build_status(build_id: str) -> str:
    """Get the status of a build by build ID."""
    fake_data = {
        "build-101": "passed",
        "build-102": "failed: unit test test_login_timeout failed",
    }
    return fake_data.get(build_id, "build not found")


agent = Agent(
    name="Build Assistant",
    instructions=(
        "You help engineers inspect build results. "
        "Use get_build_status when the user asks about a build. "
        "Do not invent build status."
    ),
    tools=[get_build_status],
)

result = Runner.run_sync(
    agent,
    "帮我检查 build-102，并告诉我下一步应该先看什么。",
)

print(result.final_output)
```

执行时，模型并不会直接运行 Python 函数。

它做的是：

```text
Model:
我要调用 get_build_status
build_id = build-102
```

然后 SDK 的 Runtime：

1. 解析 Tool Call；
2. 校验参数；
3. 执行 Python 函数；
4. 得到 Tool Result；
5. 把结果交回模型；
6. 模型继续生成最终回答。

所以真正的执行链是：

```text
Model Decision
      ↓
Runner
      ↓
Tool Runtime
      ↓
Python Function
      ↓
Tool Result
      ↓
Runner
      ↓
Model
```

这就是为什么：

**Tool Calling ≠ 模型自己执行工具。**

执行权仍然在 Harness / Runtime 手里。

---

## 五、加一个最基本的执行边界：max_turns

Agent Loop 不能无限跑。

Runner 支持限制最大 Turn 数：

```python
result = Runner.run_sync(
    agent,
    "检查 build-102。",
    max_turns=8,
)
```

这看起来只是一个参数，但背后的思想非常重要。

如果你只在 Prompt 里写：

> 最多执行 8 步。

模型可能遵守，也可能在复杂任务中偏离。

当 Runtime 自己维护：

```text
turn >= 8
    ↓
STOP
```

它才是真正的系统约束。

这就是 Harness 和 Prompt 的区别之一。

---

## 六、加入 Session：让状态跨多轮保留

默认情况下，我们还需要考虑多轮上下文。

Agents SDK 自带 Session 抽象。

一个最简单的本地持久化方式是 SQLiteSession：

```python
from agents import Agent, Runner, SQLiteSession

agent = Agent(
    name="Test Assistant",
    instructions="You are a concise software testing assistant.",
)

session = SQLiteSession(
    "demo-session",
    "agent_history.db",
)

Runner.run_sync(
    agent,
    "记住：我们正在排查 build-102。",
    session=session,
)

result = Runner.run_sync(
    agent,
    "我们刚才在排查哪个构建？",
    session=session,
)

print(result.final_output)
```

现在历史信息会保存在 SQLite 中。

Session 做的事情可以简化成：

```text
Before Run
   ↓
Load History
   ↓
Model / Tool Loop
   ↓
Save New Items
   ↓
After Run
```

这已经开始接近真正 Runtime 的 State 管理。

官方文档：

[Sessions](https://openai.github.io/openai-agents-python/sessions/)

---

## 七、Trace：不要只看最终答案

Agents SDK 内置 Tracing。

默认情况下，一次 Agent Run 可以记录：

- LLM generation；
- Tool Call；
- Handoff；
- Guardrail；
- 自定义事件。

这意味着你调试 Agent 时，不应该只看：

```text
Final Output
```

而应该看：

```text
Input
↓
Model Turn
↓
Tool Call
↓
Tool Result
↓
Model Turn
↓
Final Output
```

这是从“聊天机器人调试”走向“Agent Runtime 调试”的关键变化。

官方文档：

[Tracing](https://openai.github.io/openai-agents-python/tracing/)

> 如果组织使用 Zero Data Retention 策略，官方文档说明 Tracing 不可用；生产环境还需要根据自己的数据与合规要求决定是否启用。

---

## 八、现在回头看：我们已经有了哪些 Harness 能力

刚才不到几十行代码，实际已经使用了：

| Harness 能力 | 对应组件 |
| --- | --- |
| Agent Definition | Agent |
| Agent Loop | Runner |
| Tool Registry | agent.tools |
| Tool Schema | @tool 自动生成 |
| Tool Execution | SDK Runtime |
| Turn Limit | max_turns |
| Session | SQLiteSession |
| Trace | Built-in Tracing |

这也是为什么 Agents SDK 很适合拿来学习 Harness。

它把很多基础能力封装好了，但仍然足够轻量，让你能看见每一层。

---

## 九、但它还不是“企业可靠性交付闭环”

到这里，我们只是跑通了 Agent。

真实系统还要继续问：

### Tool 有没有副作用？

```text
read_file
```

和：

```text
delete_database
```

显然不能使用同一套权限策略。

### Tool 执行失败怎么办？

- Retry 几次？
- 什么错误能重试？
- 什么错误必须停止？
- Retry 是否会产生重复副作用？

### Agent 说“完成”就真的完成了吗？

例如 Coding Agent 回答：

> 已经修复并通过测试。

Harness 是否有独立 Evidence：

- Git diff；
- Test result；
- Exit code；
- Artifact；
- Environment state？

### 同样的失败下次会不会回来？

这就进入：

```text
Trace
→ Failure
→ Regression
→ Quality Gate
```

所以 Agents SDK 帮我们解决的是：

**让 Agent 有一个成熟的运行起点。**

真正的 Reliability 仍然需要继续往上建设。

---

## 十、下一步怎么练

如果你刚跑完这个 Demo，我建议不要马上做 Multi-Agent。

先做三个小改造：

### 练习 1：增加危险工具

增加：

```python
delete_file(path)
```

但不要真的删除文件。

要求系统在执行前进入审批。

你会马上遇到 Permission 问题。

### 练习 2：制造 Tool Failure

让 Tool 第一次调用必然 Timeout，第二次成功。

你会开始思考：

- Retry 放哪；
- Retry 次数怎么限制；
- Trace 怎么记录。

### 练习 3：给最终结果增加 Evidence

Agent 不能只回答：

> build passed

必须返回：

```text
build_id
status
evidence
source
```

这会把你自然带到 Verification。

## 结语

学习 Agents SDK，真正有价值的不是学会：

```python
Agent(...)
```

而是看懂：

**Agent Loop 到底是谁在驱动。**

一旦这件事看清楚，你就可以开始把 SDK 拆开，自己实现一个最小 Harness。

下一篇：[smolagents 入门：几十行代码跑一个 Agent Loop](/harness/smolagents-agent-loop-quickstart/)

---

## 参考资料

- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [Quickstart](https://openai.github.io/openai-agents-python/quickstart/)
- [Running agents](https://openai.github.io/openai-agents-python/running_agents/)
- [Tools](https://openai.github.io/openai-agents-python/tools/)
- [Sessions](https://openai.github.io/openai-agents-python/sessions/)
- [Tracing](https://openai.github.io/openai-agents-python/tracing/)
