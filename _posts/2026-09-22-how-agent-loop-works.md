---
layout: post
title: "一个 Agent Loop 到底是怎么跑起来的？"
date: 2026-09-22 17:35:00 +0800
categories: [Agent-Harness, Agent-Runtime]
permalink: /harness/how-agent-loop-works/
description: "从 Context Build、Model Decision、Action Validation、Tool Execution、Observation、State Update 到 Termination，拆开一个完整 Agent Loop。"
tags: ["agent-harness", "agent-loop", "agent-runtime", "trace-evidence"]
series: agent-harness
series_order: 7
---

> **Agent Harness 系列 #07**  
> 上一篇：[不用 Agent Framework，自己写一个最小 Harness](/harness/build-minimal-agent-harness/)

很多 Agent 架构图都会画成：

```text
LLM
 ↓
Tool
 ↓
LLM
```

看起来非常简单。

但真正的 Agent Loop 至少包含七个阶段：

```text
Context Build
      ↓
Model Decision
      ↓
Action Parse
      ↓
Policy / Validation
      ↓
Execution
      ↓
Observation
      ↓
State Update
      ↓
Continue or Stop
```

Harness 的大部分工程复杂度，就藏在这些箭头里。

这一篇我们不讨论具体框架，而把一个 Agent Loop 从头拆到底。

## 一、Loop 的本质：模型每次只决定“下一步”

先明确一件事：

**Agent 通常不是模型一次性生成完整执行计划，然后系统照着执行。**

更常见的是：

```text
看当前状态
   ↓
决定下一步
   ↓
执行
   ↓
看到结果
   ↓
重新决定下一步
```

这就是 Agent 和传统 Workflow 的关键区别之一。

Workflow 更像：

```text
A → B → C → D
```

Agent Loop 更像：

```text
State 0
  ↓
Action 1
  ↓
State 1
  ↓
Action 2
  ↓
State 2
  ↓
???
```

下一步是什么，运行时才知道。

## 二、第一阶段：Context Build

每一轮模型调用之前，Harness 首先要决定：

**模型这一轮能看到什么。**

Context 可能包含：

- System Instruction；
- User Goal；
- Conversation History；
- Current Plan；
- Tool Definitions；
- Previous Observation；
- Files；
- Memory；
- Environment State；
- Budget；
- Runtime Policy。

可以理解成：

```text
Raw State
   ↓
Context Builder
   ↓
Model Input
```

这一步非常关键。

因为模型的决策质量，不只取决于模型本身，还取决于：

**Harness 给它看了什么。**

例如上一步 Tool 已经失败，但 Context Builder 没把 Error 放进去。

模型可能继续假设：

> Tool 已经成功。

于是错误就会开始传播。

## 三、第二阶段：Model Decision

模型收到 Context 后，通常会产生几种结果：

```text
Final Answer
Tool Call
Handoff
Clarification
Plan Update
```

最简系统通常只处理两种：

```text
tool
or
final
```

例如：

```json
{
  "type": "tool",
  "name": "read_file",
  "arguments": {
    "path": "src/app.py"
  }
}
```

注意：

**这时候什么都还没真正发生。**

模型只是提出一个 Proposed Action。

## 四、第三阶段：Action Parse

模型输出必须先被系统解析。

如果用结构化 Tool Calling，这一步相对简单：

```text
Tool Name
Arguments
```

如果使用文本协议，则可能需要额外解析。

例如模型返回：

```text
Action: read_file
Path: src/app.py
```

Harness 必须把它转成：

```json
{
  "tool": "read_file",
  "args": {
    "path": "src/app.py"
  }
}
```

这一步看起来不起眼，但会产生很多典型失败：

- Tool 名不存在；
- 参数缺失；
- 类型错误；
- JSON 不合法；
- 模型输出了多个冲突动作。

因此成熟系统通常尽量把模型输出限制在结构化协议里。

## 五、第四阶段：Policy / Validation

这是 Harness 最重要的控制点之一。

模型提出：

```text
delete_file("/data/prod.db")
```

系统不能直接执行。

至少应该经过：

```text
Schema Validation
        ↓
Tool Exists?
        ↓
Permission
        ↓
Risk Policy
        ↓
Budget
        ↓
Approval?
```

一个动作可能得到三种结果：

```text
ALLOW
DENY
REQUIRE_APPROVAL
```

这里是真正把：

**模型意图**

和：

**系统行为**

分开的地方。

如果没有这一层，Agent 的权限边界实际上就是模型本身。

## 六、第五阶段：Execution

Action 通过检查以后，才进入真实执行。

例如：

```text
read_file()
run_test()
query_database()
edit_code()
send_message()
deploy()
```

执行层至少要处理：

- Timeout；
- Exception；
- Exit Code；
- Retry；
- Sandbox；
- Idempotency；
- Resource Limit；
- Side Effect。

真正工程化后，Tool Execution 不是简单：

```python
tool(**args)
```

更接近：

```text
Tool Request
   ↓
Execution Policy
   ↓
Sandbox / Service
   ↓
Timeout
   ↓
Result / Error
```

## 七、第六阶段：Observation

Execution 完成后，要把结果变成模型能理解的 Observation。

例如测试命令返回：

```text
exit_code = 1
stdout = ...
stderr = AssertionError
```

Harness 不一定应该把所有原始输出原封不动塞回 Context。

它可能需要：

- 截断；
- 结构化；
- 去敏；
- 摘要；
- 标记错误级别；
- 附加 Artifact Link。

于是：

```text
Raw Tool Result
      ↓
Observation Builder
      ↓
Model-readable Observation
```

这一步同样会影响下一轮决策。

## 八、第七阶段：State Update

Tool Result 不只是给模型看。

系统自己也应该更新状态。

例如：

```text
completed_steps += 1
last_tool = run_test
test_status = failed
changed_files = [...]
budget_remaining -= 3
```

这就是为什么：

**Conversation History 不等于 Runtime State。**

History 是模型看到的消息。

State 是系统真正维护的执行事实。

两者可以重叠，但不应该完全等价。

## 九、最后：Continue or Stop

每轮结束后 Harness 要判断：

```text
继续吗？
```

停止条件可能包括：

### 正常完成

```text
Final Answer
+
Verification Passed
```

### Budget 用完

```text
max_steps
max_time
max_cost
```

### Policy 阻断

```text
forbidden action
```

### 无法恢复错误

```text
permanent failure
```

### 需要人工

```text
approval
clarification
high-risk decision
```

所以一个完整 Loop 其实应该是：

```text
while runtime_allows_continue():

    context = build_context(state)

    decision = model(context)

    action = parse(decision)

    validation = policy.check(action)

    if validation == REQUIRE_APPROVAL:
        pause()

    result = execute(action)

    observation = normalize(result)

    state.update(
        action,
        observation,
    )

    trace.record(...)

    if should_finish(state):
        verify()
        break
```

这已经不是“LLM 调 Tool”。

这是一个 Runtime。

## 十、Trace 应该在哪记录

如果只在最后写一条日志：

```text
task success
```

几乎没有价值。

更有用的是给 Loop 中每个关键阶段留 Span / Event：

```text
run.start

context.build

model.call
model.decision

action.parse
policy.check

tool.start
tool.result

state.update

verification

run.finish
```

这样出问题以后才能回答：

- 第一次错误发生在哪；
- 模型是否看到了正确 Context；
- Action 是否被错误解析；
- Policy 为什么放行；
- Tool 到底返回什么；
- State 有没有同步；
- 后续步骤是不是基于错误信息继续运行。

**Trace 最好的形态，是 Loop 的结构化投影。**

## 十一、Agent Loop 最常见的五类失败

把 Loop 拆开后，失败也会变清楚。

### 1. Context Failure

模型看到的是过期或缺失状态。

例如：

```text
真实环境：deploy failed
模型 Context：deploy succeeded
```

### 2. Decision Failure

Context 没问题，但模型选错 Action。

### 3. Execution Failure

Action 正确，但 Tool 超时、报错或产生异常副作用。

### 4. State Failure

Tool 已经执行，但 Runtime 没有正确更新状态。

### 5. Termination Failure

任务其实已经失败或偏离，但 Loop 仍然继续。

这些都可能最终表现成同一个结果：

> Agent 失败了。

但修复方式完全不同。

所以 Reliability 不能只看 Final Output。

## 十二、为什么 Retry Density 是个危险信号

假设 Loop 是：

```text
tool A
↓ fail

tool A
↓ fail

tool A
↓ fail

tool A
↓ success
```

最终结果可能是：

```text
PASS
```

但这个过程已经暴露出：

- Tool 不稳定；
- 策略可能错误；
- Agent 不理解失败；
- Runtime 可能缺少退避或替代路径。

所以真实 Reliability 指标会开始关注：

```text
retry_count
retry_density
trajectory_length
repeated_action
recovery_success
```

这也是为什么 Agent 的“成功率”远远不够。

## 十三、一个健康的 Loop 应该有什么特征

我会至少看六件事：

### 1. 每一轮有明确输入

Context Version 可追踪。

### 2. 每一个 Action 可解释

知道模型为什么选择这个 Tool。

### 3. Tool Execution 有边界

Timeout、Permission、Budget 明确。

### 4. Observation 和 State 不混乱

真实环境状态和模型认知尽量保持同步。

### 5. Stop Condition 在模型之外

不能只靠 Agent 自己决定：

> 我完成了。

### 6. 全过程可重建

一次 Run 出问题以后能重新还原：

```text
Goal
→ Context
→ Decision
→ Action
→ Result
→ State
→ Next Decision
```

这才是一个真正可调试的 Agent Loop。

## 十四、Harness 的职责，其实就是管理这条 Loop

现在可以回到整个系列最核心的一句话：

```text
Model proposes.
Harness controls execution.
```

Harness 不是替模型思考。

它负责：

- 准备 Context；
- 驱动 Model；
- 解析 Action；
- 应用 Policy；
- 执行 Tool；
- 管理 State；
- 记录 Trace；
- 决定是否继续。

也就是说：

**Agent Loop 是 Harness 最核心的运行对象。**

当 Loop 被控制住以后，才有资格继续谈：

- Evidence；
- Recovery；
- Failure Regression；
- Quality Gate。

下一篇：[Agent 为什么需要 Harness：模型负责决策，系统负责约束](/harness/why-agent-needs-harness/)

---

## 延伸阅读

- [不用 Agent Framework，自己写一个最小 Harness](/harness/build-minimal-agent-harness/)
- [smolagents 入门：几十行代码跑一个 Agent Loop](/harness/smolagents-agent-loop-quickstart/)
- [Agent Harness 是什么？](/harness/what-is-agent-harness/)
