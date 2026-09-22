---
layout: post
title: "smolagents 教程：用 CodeAgent 跑通一个 Agent Loop"
date: 2026-09-22 17:30:00 +0800
categories: [Agent-Harness, Tutorial]
permalink: /harness/smolagents-agent-loop-quickstart/
description: "Hugging Face smolagents 入门教程：用 CodeAgent / ToolCallingAgent 跑通 Agent Loop，理解 max_steps、planning_interval、step_callbacks 与代码执行安全边界。"
tags: ["agent-harness", "smolagents", "agent-loop", "tutorial"]
series: agent-harness
series_order: 5
---

> **Agent Harness 系列 #05**  
> 上一篇：[OpenAI Agents SDK 入门：从安装到第一个可调用工具的 Agent](/harness/openai-agents-sdk-quickstart/)

如果 OpenAI Agents SDK 更像一个已经整理好的轻量 Runtime，那么 **smolagents 更适合把 Agent Loop 本身看清楚**。

它的核心非常直接：

```text
Thought
  ↓
Action / Tool Call
  ↓
Execution
  ↓
Observation
  ↓
Next Step
```

Hugging Face 当前把大部分 Agent 都建立在 `MultiStepAgent` 上：每一步包含一次模型思考、一次工具调用和一次执行，然后继续下一步，直到得到最终答案或达到最大步数。

这一篇的目标不是研究全部 API，而是用最少代码回答三个问题：

1. Agent Loop 到底在哪里？
2. Tool 是怎么进入 Loop 的？
3. Harness 能在哪些位置加控制？

> 本文按 2026-09-22 的 smolagents 官方文档编写。官方仍把该 API 标为 experimental，接口可能继续变化。

## 一、安装

官方当前推荐：

```bash
pip install 'smolagents[toolkit]'
```

如果使用 Hugging Face Inference Providers，需要准备：

```bash
export HF_TOKEN="你的 Hugging Face Token"
```

Windows PowerShell：

```powershell
$env:HF_TOKEN="你的 Hugging Face Token"
```

官方文档：

[smolagents](https://huggingface.co/docs/smolagents/main/index)

---

## 二、先跑一个最小 Agent

最简单的版本：

```python
from smolagents import CodeAgent, InferenceClientModel

model = InferenceClientModel()

agent = CodeAgent(
    tools=[],
    model=model,
    max_steps=5,
)

result = agent.run(
    "计算 1 到 20 的整数之和。"
)

print(result)
```

这里只做了三件事：

```text
Model
  ↓
CodeAgent
  ↓
agent.run()
```

真正重要的是：

```python
agent.run(...)
```

一旦 Run 开始，`MultiStepAgent` 会持续执行一个多步循环。

官方把这类 Agent 描述为基于 ReAct 风格的循环：

```text
Action
  ↓
Observation
  ↓
Action
  ↓
Observation
  ↓
...
```

直到目标完成。

## 三、CodeAgent 和 ToolCallingAgent 有什么区别

smolagents 当前最常见的两种 Agent：

### CodeAgent

模型通过 **Python 代码**表达动作。

例如模型可能生成类似：

```python
status = get_build_status("build-102")
print(status)
```

然后 Runtime 执行代码。

### ToolCallingAgent

模型通过结构化 Tool Call 表达动作，更接近常见的 JSON Function Calling：

```json
{
  "name": "get_build_status",
  "arguments": {
    "build_id": "build-102"
  }
}
```

两者的本质差别不是“有没有 Agent Loop”。

两者都有 Loop。

区别在于：

**Action 用什么表示。**

可以粗略画成：

```text
CodeAgent
Model
 ↓
Python Code
 ↓
Python Executor

ToolCallingAgent
Model
 ↓
Structured Tool Call
 ↓
Tool Executor
```

如果你的任务天然需要组合计算、处理对象、连续操作数据，CodeAgent 很有表达力。

如果你更强调 Tool Schema、权限和可控调用，ToolCallingAgent 的边界通常更清晰。

## 四、给 Agent 一个真正的 Tool

下面做一个最小构建状态查询工具。

```python
from smolagents import (
    CodeAgent,
    InferenceClientModel,
    tool,
)


@tool
def get_build_status(build_id: str) -> str:
    """
    Return the status of a demo build.

    Args:
        build_id: Build identifier.
    """
    fake_data = {
        "build-101": "passed",
        "build-102": "failed: test_login_timeout",
    }

    return fake_data.get(
        build_id,
        "build not found",
    )


model = InferenceClientModel()

agent = CodeAgent(
    tools=[get_build_status],
    model=model,
    max_steps=6,
)

result = agent.run(
    "检查 build-102，并告诉我失败信息。"
)

print(result)
```

这里的 `@tool` 会把普通 Python 函数转换成 Agent 可以使用的 Tool。

官方要求 Tool 函数至少要有：

- 参数类型；
- 返回类型；
- Docstring；
- Args 描述。

原因很简单：

**Harness 必须把 Tool 的能力描述给模型。**

如果 Tool Schema 本身不清楚，模型就更容易传错参数或者误解 Tool。

## 五、max_steps 是第一个真正的 Runtime Boundary

`MultiStepAgent` 默认提供 `max_steps`。

例如：

```python
agent = CodeAgent(
    tools=[get_build_status],
    model=model,
    max_steps=6,
)
```

这不是 Prompt：

> 请尽量在 6 步以内完成。

而是 Runtime 真正维护的上限。

可以理解成：

```text
step < max_steps
      ↓
continue

step >= max_steps
      ↓
stop
```

这就是 Harness 非常典型的职责：

**限制模型能够消耗的执行空间。**

后面同样的思想还会扩展成：

- max_tool_calls；
- max_wall_time；
- max_cost；
- max_retry；
- max_side_effect。

## 六、step_callbacks：Trace 最自然的插入点

smolagents 允许给 Agent 配置 `step_callbacks`。

这意味着每一步完成以后，你可以插入自己的逻辑：

```text
Step
 ↓
Callback
 ├── Trace
 ├── Metrics
 ├── Evidence
 ├── Drift Detection
 └── Policy Check
```

概念上可以写成：

```python
def on_step(step):
    print("step:", step)

agent = CodeAgent(
    tools=[get_build_status],
    model=model,
    max_steps=6,
    step_callbacks=[on_step],
)
```

真正工程化时，这里很适合记录：

- Step Number；
- Model Output；
- Tool Call；
- Observation；
- Duration；
- Error；
- Token / Cost；
- State Change。

也就是说：

**Loop 暴露得越清楚，Reliability 能力越容易插进去。**

## 七、planning_interval：不是每一步都重新做完整规划

`MultiStepAgent` 还提供 `planning_interval`。

例如：

```python
agent = CodeAgent(
    tools=[get_build_status],
    model=model,
    max_steps=9,
    planning_interval=3,
)
```

可以理解成：

```text
Step 1
Step 2
Step 3
  ↓
Planning

Step 4
Step 5
Step 6
  ↓
Planning
```

规划步骤会重新整理：

- 已知事实；
- 当前状态；
- 接下来应该做什么。

它解决的是长任务中的另一个问题：

**Agent 不能只在最开始想一次，然后一路机械执行。**

但这里也要看到另一面：

Planning 仍然是模型行为。

真正的系统约束，例如 Permission、Timeout、Budget，依然应该由 Harness 提供。

## 八、final_answer_checks：Agent 说完成以后还能再检查一次

smolagents 当前提供 `final_answer_checks`。

它允许在接受最终答案之前执行验证函数。

这很有意思，因为它开始出现一个简单的 Verification Gate：

```text
Agent Final Answer
       ↓
Final Answer Check
   ├── pass → accept
   └── fail → reject / continue
```

这仍然不是完整的 Evidence Contract。

但它已经表达了一个重要思想：

**Final Answer 不是天然可信的。**

Agent 输出“完成”以后，还可以再做一次独立判断。

## 九、CodeAgent 最大的价值，也是最大的风险：执行代码

CodeAgent 的特点是让模型生成 Python 代码作为 Action。

这带来很强的表达能力：

```text
多个 Tool 调用
+
数据处理中间变量
+
循环
+
条件逻辑
```

都可以直接用代码表示。

但这里必须特别注意安全边界。

Hugging Face 官方文档明确提醒：

**默认情况下 CodeAgent 会在你的环境里执行 LLM 生成的代码。**

smolagents 的 LocalPythonExecutor 会限制 import 和一些操作，但官方同时强调：

> 本地执行器并不是一个安全沙箱。

对于不可信代码或高风险场景，应考虑远程隔离执行，例如：

- E2B；
- Docker；
- Modal；
- Blaxel。

例如使用 E2B：

```python
from smolagents import (
    CodeAgent,
    InferenceClientModel,
)

with CodeAgent(
    model=InferenceClientModel(),
    tools=[],
    executor_type="e2b",
) as agent:
    result = agent.run(
        "计算第 100 个 Fibonacci 数。"
    )

    print(result)
```

这件事和 Harness 的关系非常直接：

**Tool / Code 能不能执行，必须是 Runtime Policy，而不是只靠模型自觉。**

## 十、把 smolagents 拆成 Harness 视角

现在重新看刚才的代码：

| Harness 能力 | smolagents 对应位置 |
| --- | --- |
| Agent Loop | MultiStepAgent |
| Model Adapter | InferenceClientModel / 其他 Model |
| Action | Python Code / Tool Call |
| Tool Registry | tools |
| Step Limit | max_steps |
| Planning | planning_interval |
| Step Hook | step_callbacks |
| Final Verification | final_answer_checks |
| Execution Environment | Local / E2B / Docker / Modal / Blaxel |

它为什么适合学习 Harness？

因为这些概念几乎都直接暴露在构造参数里。

你很容易看到：

**一个 Agent 真正跑起来，到底需要哪些 Runtime 组件。**

## 十一、OpenAI Agents SDK 和 smolagents 怎么选

如果只是学习，我会这样看：

### OpenAI Agents SDK

更适合看：

- Runner；
- Session；
- Guardrail；
- Handoff；
- Trace；
- 生产级 Runtime 抽象。

### smolagents

更适合看：

- Multi-Step Loop；
- Code Action；
- Planning；
- Step Callback；
- Execution Environment。

所以这两个工具并不是谁替代谁。

它们恰好从两个方向帮助理解 Harness。

## 十二、最值得自己动手改的三个地方

如果已经把 Demo 跑起来，我建议继续改三件事。

### 练习 1：记录每一步 Trace

用 `step_callbacks` 保存：

```text
step
action
observation
duration
error
```

### 练习 2：把 max_steps 改成动态 Budget

例如：

```text
read-only action
cost = 1

write action
cost = 3

total budget = 20
```

你会开始真正进入 Harness Design。

### 练习 3：给最终答案加 Evidence

不要只检查字符串。

要求 Agent 最后给出：

```text
result
evidence
source
tool_trace
```

然后再决定是否接受。

## 结语

smolagents 最值得看的，不是它“很轻量”。

而是它把 Agent 还原成了一件非常具体的事情：

```text
Thought
→ Action
→ Execution
→ Observation
→ Next Step
```

一旦 Loop 被看清楚，Harness 的职责也就开始清楚：

**控制每一轮发生什么，以及哪些事情不能发生。**

下一篇：[不用 Agent Framework，自己写一个最小 Harness](/harness/build-minimal-agent-harness/)

---

## 参考资料

- [smolagents Documentation](https://huggingface.co/docs/smolagents/main/index)
- [Agents Reference](https://huggingface.co/docs/smolagents/reference/agents)
- [Tools Reference](https://huggingface.co/docs/smolagents/reference/tools)
- [Secure Code Execution](https://huggingface.co/docs/smolagents/tutorials/secure_code_execution)
