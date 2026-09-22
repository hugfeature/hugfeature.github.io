---
layout: post
title: "Agent 为什么需要 Harness：模型负责决策，系统负责约束"
date: 2026-09-22 16:25:00 +0800
categories: [Agent-Harness, Agent-Reliability]
permalink: /harness/why-agent-needs-harness/
description: "为什么 Prompt 不能替代执行约束？从 Permission、Budget、Timeout、Side Effect、Evidence 到 Recovery，解释 Harness 如何成为 Agent Reliability 的边界。"
tags: ["agent-harness", "agent-reliability", "runtime", "quality-gate"]
series: agent-harness
series_order: 8
---

> **Agent Harness 系列 #08**  
> 建议先读：[不用 Agent Framework，自己写一个最小 Harness](/harness/build-minimal-agent-harness/)

做 Agent 很容易形成一种错觉：

**只要 Prompt 写得足够好，Agent 就会越来越可靠。**

于是我们不断追加规则：

- 修改文件前先读取；
- 删除前必须确认；
- 失败后最多重试三次；
- 完成任务以后必须执行测试；
- 不允许访问某些目录；
- 不要重复调用同一个工具。

这些规则并不是没用。

问题是：

**Prompt 只能影响模型的决策，不能成为系统的最终执行边界。**

这就是 Agent 为什么需要 Harness。

## 一、先把模型和系统的职责分开

我现在更倾向于用一句话划分：

> **Model proposes. Harness enforces.**

模型负责：

- 理解目标；
- 规划；
- 选择 Tool；
- 根据 Observation 调整下一步。

Harness 负责：

- Tool 能不能执行；
- 参数是否合法；
- 是否需要 Approval；
- 最多执行多少步；
- 最长运行多久；
- 失败是否允许 Retry；
- Side Effect 是否可接受；
- Trace 是否完整；
- 最终结果是否有 Evidence。

可以画成：

```text
Goal
 ↓
Model
 ↓
Proposed Action
 ↓
Harness
 ├── Policy
 ├── Permission
 ├── Budget
 ├── Timeout
 ├── State
 └── Trace
 ↓
Execution
```

Agent Reliability 真正开始的地方，不是模型输出。

而是：

**Proposed Action → Actual Execution**

之间这层控制。

## 二、为什么 Prompt 不能当权限系统

假设 Prompt 写：

> 永远不要删除 production 数据。

听起来没问题。

但从系统安全角度，这句话本质上只是：

**给模型的一条自然语言建议。**

如果 Tool 列表中仍然暴露：

```text
delete_database("prod")
```

而 Runtime 没有任何 Policy，那么最终权限实际上仍然掌握在模型手里。

更合理的设计是：

```text
Model
  ↓
delete_database("prod")
  ↓
Harness Policy
  ↓
DENY
```

或者：

```text
REQUIRE_APPROVAL
  ↓
Human
  ↓
ALLOW / DENY
```

这样即使模型判断错误，危险动作仍然不会自动落地。

所以：

**重要规则应该从 Prompt 下沉到 Runtime。**

## 三、Retry 也不能只告诉模型“再试一次”

Agent Tool Call 失败以后，最常见做法是：

> 告诉模型错误信息，让它再试。

但 Retry 其实是一个系统问题。

考虑：

```text
send_payment()
```

第一次调用超时。

模型看到：

```text
timeout
```

然后决定再试一次。

问题是：

第一次支付到底有没有成功？

如果成功了，但响应包丢了，第二次 Retry 就可能重复付款。

所以 Harness 必须考虑：

- Error 类型；
- Retry 次数；
- Backoff；
- Idempotency Key；
- Side Effect；
- Tool 是否允许自动重试。

这已经完全超出 Prompt Engineering。

一个合理策略可能是：

```text
read-only tool
→ retry automatically

idempotent write
→ retry with same idempotency key

non-idempotent side effect
→ stop / verify / require approval
```

Reliability 的核心不是：

**发生错误以后继续跑。**

而是：

**知道什么错误可以继续跑。**

## 四、Budget 是系统约束，不是行为建议

长任务 Agent 很容易出现：

- Reasoning Loop；
- Rabbit Hole；
- 重复搜索；
- 重复 Tool Call；
- 无意义文件遍历。

如果只在 Prompt 写：

> 尽量少调用工具。

约束非常弱。

Harness 可以真正维护：

```text
max_turns = 30
max_tool_calls = 50
max_wall_time = 20min
max_cost = $X
max_same_tool_retry = 3
```

然后：

```text
Budget Exceeded
      ↓
   Stop / Escalate
```

Budget 不只是省钱。

它还是防止 Agent 长时间失控的重要 Safety Boundary。

## 五、Timeout 的意义不是“别等太久”

Tool Timeout 经常被当成普通工程参数。

对于 Agent，它还有第二层意义：

**阻断错误轨迹继续占用执行资源。**

例如 Agent 调一个外部系统：

```text
deploy()
```

如果 15 分钟都没有明确返回，模型继续假设：

> 部署应该成功了。

然后执行下一步：

```text
run_post_deploy_test()
```

这时真正的问题不是慢。

而是：

**Agent 的内部状态和真实环境状态可能已经分叉。**

因此 Timeout 后不能简单变成：

```text
error → retry
```

可能应该变成：

```text
timeout
 ↓
verify external state
 ↓
known?
 ├─ yes → continue
 └─ no  → stop / human
```

这就是 State Verification。

## 六、Harness 还必须控制 Side Effect

Agent Tool 可以粗略分成两类：

### Read

```text
search
read_file
query_db
get_status
```

### Write / Side Effect

```text
edit_file
send_message
create_ticket
deploy
delete
payment
```

它们不应该共享同样的运行策略。

Harness 应该知道：

- Tool 风险级别；
- 是否可逆；
- 是否幂等；
- 是否需要 Approval；
- 是否需要执行后 Verification；
- 是否需要记录 Artifact。

例如：

```text
edit_file
  ↓
execute
  ↓
git diff
  ↓
test
  ↓
evidence
```

而不是：

```text
edit_file
  ↓
Agent says done
```

这也是 Harness 从“执行引擎”进入“Reliability Engine”的关键一步。

## 七、Agent 说完成，不等于系统应该相信它

很多 Agent 的最终状态是：

```text
Final Answer:
Task completed successfully.
```

但真正的生产系统应该问：

**证据呢？**

以 Coding Agent 为例：

模型说：

> 已经修复 bug。

Harness 可以要求：

```text
Evidence Contract

required:
- changed_files
- git_diff
- test_command
- test_exit_code
- test_output
```

如果缺其中任何一个：

```text
Status != VERIFIED
```

这会把：

```text
Agent self-report
```

变成：

```text
Independent Verification
```

我认为这是 Agent Reliability 最重要的一次升级。

## 八、Trace 的价值不是“方便查日志”

传统日志通常回答：

> 系统发生了什么？

Agent Trace 还要回答：

> **Agent 为什么走到这里？**

一条真正有用的 Trace 至少应该能关联：

```text
Goal
 ↓
Context Version
 ↓
Model Decision
 ↓
Tool Call
 ↓
Tool Result
 ↓
State Change
 ↓
Retry / Recovery
 ↓
Final Evidence
```

这样出现问题以后，才能判断：

- 第一次错误发生在哪；
- 错误有没有被发现；
- 后面是不是基于错误状态继续执行；
- 最终 Pass 是否只是偶然回来。

这和我们前面讨论的“隐藏失败”是同一个问题：

[Agent 最危险的不是失败，而是最终通过但过程已经失控](/agent-reliability/ai-testing/2026/09/21/agent-hidden-failures.html)


## 九、Recovery 不是让模型“自己想办法”

很多 Agent 宣传里会强调：

> 自主恢复。

但真正可靠的恢复至少需要：

```text
Failure Detection
       ↓
Failure Classification
       ↓
Known Recovery Policy?
    ├─ yes → execute
    └─ no  → stop / human
       ↓
State Verification
       ↓
Resume
```

而不是：

```text
失败
 ↓
把错误丢给模型
 ↓
再试试
```

Harness 应该知道：

- 当前 Checkpoint；
- 哪一步已经产生副作用；
- 哪些动作可以重复；
- 哪些 Artifact 已经生成；
- Resume 应该从哪里开始。

这也是为什么长任务 Agent 最终一定会碰到：

**Checkpoint + Resume + Idempotency。**

## 十、把 Reliability 能力放回 Harness

到这里，一个真正面向生产的 Harness 已经不只是：

```text
Model + Tool Loop
```

它更像：

```text
              ┌───────────────┐
Goal ────────→│    Harness    │
              │               │
Model ───────→│ Policy        │
              │ Permission    │
Tools ───────→│ Budget        │
              │ Timeout       │
State ───────→│ Retry         │
              │ Trace         │
              │ Evidence      │
              │ Recovery      │
              └───────┬───────┘
                      ↓
                 Verified Result
```

这里最重要的变化是：

**Harness 不再只保证 Agent 能运行。**

而是开始保证：

**Agent 在明确边界内运行。**

## 十一、最终会自然走到 Quality Gate

如果 Harness 已经能产出：

- Trace；
- Evidence；
- Failure Type；
- Risk Signal；
- Regression Result；

那么下一步非常自然：

```text
Can this result move forward?
```

例如：

```text
PASS
├── tests passed
├── evidence complete
├── no forbidden tool
├── no unresolved failure
└── regression passed
```

才允许：

```text
Merge / Release
```

否则：

```text
BLOCK
```

这时 Harness 就从：

**Agent Execution Layer**

逐渐变成：

**AI Delivery Reliability Layer。**

## 十二、我现在更愿意怎么定义 Harness

如果只谈功能：

> Harness 是驱动 Agent Loop 的运行时脚手架。

但如果讨论真实工程：

> **Harness 是把模型的不确定决策，转换成受控、可观察、可验证执行的系统边界。**

前一个定义解释：

**它是什么。**

后一个定义解释：

**为什么它值得做。**

## 结语

模型能力一定还会继续增强。

模型越强，能执行的动作越多，任务越长。

但这不会让 Harness 变得不重要。

恰恰相反。

因为当模型从：

```text
生成文本
```

进入：

```text
修改代码
操作系统
调用 API
创建数据
执行发布
```

我们真正需要解决的问题就不再只是：

> 它聪不聪明？

而是：

> **我们是否有能力控制它做什么、证明它做对了，以及在它做错时及时阻断。**

这才是 Harness 和 Agent Reliability 真正连接起来的地方。

下一篇将继续拆具体职责：

**Harness 到底应该管什么？**

---

## 延伸阅读

- [Agent Harness 是什么？](/harness/what-is-agent-harness/)
- [不用 Agent Framework，自己写一个最小 Harness](/harness/build-minimal-agent-harness/)
- [2026 年 Agent Harness / Runtime 工具盘点](/harness/agent-harness-runtime-tools-2026/)
