---
layout: post
title: "手写 Agent Harness：用 Python 实现 Loop、Tool、Policy 与 Trace"
date: 2026-09-22 16:20:00 +0800
categories: [Agent-Harness, Tutorial]
permalink: /harness/build-minimal-agent-harness/
description: "不用 Agent Framework，用 Python 从零实现一个最小 Agent Harness：包含 Model Adapter、Tool Registry、Policy、Trace、max_steps 与执行循环。"
tags: ["agent-harness", "agent-loop", "python", "tutorial"]
series: agent-harness
series_order: 6
---

> **Agent Harness 系列 #06**  
> 建议先读：[OpenAI Agents SDK 入门](/harness/openai-agents-sdk-quickstart/)

上一篇我们用了 OpenAI Agents SDK。

这一篇反过来：

**不用 Agent Framework，自己写一个最小 Harness。**

目标不是造一个新的生产级框架，而是把 Harness 最核心的东西拆开：

```text
Context
Model
Loop
Tool
Policy
Trace
Stop Condition
```

只要这几个东西真正写过一次，以后再看任何 Agent Framework，都会清楚很多。

## 一、先确定最小架构

我们先不做 Memory、Multi-Agent、Workflow。

最小 Harness 只保留五块：

```text
User Goal
   ↓
Context / History
   ↓
Model
   ↓
Decision
   ↓
Harness
 ├── final → return
 └── tool
      ↓
   Policy Check
      ↓
   Tool Execute
      ↓
   Trace
      ↓
   Observation
      ↓
     Loop
```

对应成代码：

```text
Harness
├── model
├── tools
├── policy
├── trace
└── run()
```

## 二、先定义 Tool

为了让 Harness 不绑定具体业务，Tool 最少需要：

- name；
- description；
- handler。

```python
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Tool:
    name: str
    description: str
    handler: Callable[..., Any]
```

再做两个工具：

```python
def add(a: int, b: int) -> int:
    return a + b


def read_build(build_id: str) -> str:
    data = {
        "build-101": "passed",
        "build-102": "failed",
    }
    return data.get(build_id, "not found")


TOOLS = {
    "add": Tool(
        name="add",
        description="Add two integers.",
        handler=add,
    ),
    "read_build": Tool(
        name="read_build",
        description="Read build status.",
        handler=read_build,
    ),
}
```

到这里还没有 Agent。

只是一个 Tool Registry。

## 三、统一模型输出协议

Harness 不应该依赖“模型输出一段自然语言以后再猜它想干什么”。

所以我们约定模型每一轮只能返回两种 Decision：

### Tool Decision

```json
{
  "type": "tool",
  "name": "read_build",
  "arguments": {
    "build_id": "build-102"
  }
}
```

### Final Decision

```json
{
  "type": "final",
  "output": "build-102 failed"
}
```

这个协议非常重要。

因为 Harness 只处理结构化状态：

```text
tool
or
final
```

而不是去理解任意自然语言。

## 四、先做一个假的 Model Adapter

为了让整套 Harness 不依赖任何云 API，我们先写一个 Fake Model。

```python
class DemoModel:
    def __init__(self):
        self.called = False

    def decide(self, history, tools):
        if not self.called:
            self.called = True
            return {
                "type": "tool",
                "name": "read_build",
                "arguments": {
                    "build_id": "build-102",
                },
            }

        last = history[-1]

        return {
            "type": "final",
            "output": (
                "The build status is: "
                + str(last["tool_result"])
            ),
        }
```

以后接 OpenAI、Gemini、Claude 或本地模型，只需要替换：

```python
model.decide(...)
```

Harness 本身不用跟着重写。

这就是 Model Adapter 的价值。

## 五、增加 Policy

现在最危险的事情来了：

模型说：

> 调用 read_build。

Harness 要不要直接执行？

对于读操作，也许可以。

但如果以后有：

```text
delete_file
send_email
deploy_prod
drop_table
```

显然不能全部直接执行。

所以我们做一个最简单 Policy：

```python
class Policy:
    def __init__(self, allowed_tools):
        self.allowed_tools = set(allowed_tools)

    def check(self, tool_name: str):
        if tool_name not in self.allowed_tools:
            raise PermissionError(
                f"Tool not allowed: {tool_name}"
            )
```

注意这里最关键的一点：

**Policy 在模型之外。**

Prompt 可以建议模型不要调用危险工具。

Policy 可以真正阻止危险工具执行。

这是 Harness 的核心价值之一。

## 六、增加 Trace

先不用任何 Observability 平台。

一个 list 就够。

```python
class Trace:
    def __init__(self):
        self.events = []

    def record(self, event_type: str, **data):
        self.events.append({
            "type": event_type,
            **data,
        })
```

我们至少记录：

```text
model_decision
tool_start
tool_result
error
final
```

这已经足够重建一条最小执行轨迹。

## 七、真正的 Harness.run()

现在把它们串起来：

```python
class Harness:
    def __init__(
        self,
        model,
        tools,
        policy,
        max_steps=8,
    ):
        self.model = model
        self.tools = tools
        self.policy = policy
        self.max_steps = max_steps
        self.trace = Trace()

    def run(self, goal: str):
        history = [{
            "role": "user",
            "content": goal,
        }]

        for step in range(1, self.max_steps + 1):
            decision = self.model.decide(
                history=history,
                tools=self.tools,
            )

            self.trace.record(
                "model_decision",
                step=step,
                decision=decision,
            )

            if decision["type"] == "final":
                self.trace.record(
                    "final",
                    step=step,
                    output=decision["output"],
                )
                return decision["output"]

            if decision["type"] != "tool":
                raise ValueError(
                    "Unknown decision type"
                )

            tool_name = decision["name"]
            arguments = decision["arguments"]

            self.policy.check(tool_name)

            tool = self.tools.get(tool_name)

            if tool is None:
                raise KeyError(
                    f"Unknown tool: {tool_name}"
                )

            self.trace.record(
                "tool_start",
                step=step,
                tool=tool_name,
                arguments=arguments,
            )

            try:
                result = tool.handler(**arguments)

            except Exception as exc:
                self.trace.record(
                    "error",
                    step=step,
                    tool=tool_name,
                    error=repr(exc),
                )
                raise

            self.trace.record(
                "tool_result",
                step=step,
                tool=tool_name,
                result=result,
            )

            history.append({
                "role": "tool",
                "tool": tool_name,
                "tool_result": result,
            })

        raise RuntimeError(
            f"max_steps exceeded: {self.max_steps}"
        )
```

这已经是一个最小 Agent Harness。

## 八、把它跑起来

```python
harness = Harness(
    model=DemoModel(),
    tools=TOOLS,
    policy=Policy(
        allowed_tools={"read_build", "add"}
    ),
    max_steps=5,
)

result = harness.run(
    "Check build-102."
)

print("RESULT:")
print(result)

print("\nTRACE:")
for event in harness.trace.events:
    print(event)
```

你会得到类似：

```text
RESULT:
The build status is: failed

TRACE:
model_decision ...
tool_start ...
tool_result ...
model_decision ...
final ...
```

我们没有任何 Agent Framework。

但已经有了：

- Loop；
- Tool Registry；
- Tool Execution；
- Permission；
- max_steps；
- Trace；
- Final Result。

这就是 Harness 的骨架。

## 九、如果接真实 LLM，哪里需要替换？

只换这一块：

```python
DemoModel.decide()
```

真实 Model Adapter 要做：

1. 把 history 转成模型输入；
2. 把 tools 转成 Tool Schema；
3. 调用模型；
4. 解析 function call；
5. 返回统一 Decision。

例如：

```python
{
    "type": "tool",
    "name": "...",
    "arguments": {...}
}
```

或者：

```python
{
    "type": "final",
    "output": "..."
}
```

模型厂商可以变。

Harness 的控制逻辑不用变。

所以一个比较健康的架构是：

```text
Harness
  ↓
Model Adapter
  ├── OpenAI
  ├── Gemini
  ├── Claude
  └── Local Model
```

这也是为什么我不建议把 Harness 设计成某个模型 API 的薄封装。

## 十、这个最小 Harness 还缺什么

非常多。

### 1. Retry

现在 Tool 一失败就退出。

生产环境至少需要区分：

```text
Transient Error
→ Retry

Permanent Error
→ Stop
```

### 2. Timeout

Tool 必须有明确执行时间边界。

### 3. Idempotency

如果 Tool 有副作用：

```text
create_order()
```

Retry 可能创建两次订单。

### 4. Approval

Policy 现在只有 allow / deny。

真实系统通常至少需要：

```text
ALLOW
DENY
REQUIRE_APPROVAL
```

### 5. Persistent State

现在 history 在内存里。

进程一挂，任务就没了。

需要：

- Session；
- Checkpoint；
- Resume。

### 6. Context Management

长任务不可能无限追加 history。

需要 Compaction。

### 7. Evidence

Tool Result 不代表最终结论一定可信。

需要独立 Evidence。

### 8. Regression

Trace 只记录失败还不够。

失败要变成可重复执行的 Regression Case。

---

## 十一、从 50 行 Harness 到生产系统

真正的演化路线大概是：

```text
v0
Loop + Tool

↓
v1
Policy + Trace + max_steps

↓
v2
Retry + Timeout + Budget

↓
v3
Session + Checkpoint + Resume

↓
v4
Evidence + Verification

↓
v5
Failure Corpus + Regression

↓
v6
Quality Gate
```

这也是我认为 Harness 最有价值的地方。

它不是一个“Agent 框架名词”。

它是你逐步把 Agent 从：

**会做事**

升级成：

**可控地做事**

的工程边界。

## 十二、最后重新看这段代码

整个 Harness 最重要的其实只有一句思想：

```text
Model proposes.
Harness decides what actually happens.
```

模型负责提出下一步。

Harness 决定：

- 能不能执行；
- 怎么执行；
- 执行多久；
- 失败怎么办；
- 留下什么证据；
- 什么时候必须停止。

这就是 Agent Engineering 和普通 LLM 调用之间真正的分界线。

后面我们会继续进入更深的一层：

[一个 Agent Loop 到底是怎么跑起来的？](/harness/how-agent-loop-works/)

---

## 延伸阅读

- [OpenAI Function Calling](https://developers.openai.com/api/docs/guides/function-calling)
- [Agent Harness 是什么？](/harness/what-is-agent-harness/)
