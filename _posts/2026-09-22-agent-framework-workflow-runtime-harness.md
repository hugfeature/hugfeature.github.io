---
layout: post
title: "Agent、Framework、Workflow、Runtime、Harness 到底有什么区别？"
date: 2026-09-22 16:30:00 +0800
categories: [Agent-Harness, Agent-Reliability]
permalink: /harness/agent-framework-workflow-runtime-harness/
description: "用五个工程问题讲清 Agent、Agent Framework、Workflow、Runtime 和 Harness 的边界，以及为什么这些概念经常重叠。"
tags: ["agent-harness", "agent-framework", "agent-runtime", "workflow"]
series: agent-harness
series_order: 2
---

> **Agent Harness 系列 #02**  
> 上一篇：[Agent Harness 是什么？为什么它正在成为 Agent 工程的关键一层](/harness/what-is-agent-harness/)

做 Agent 一段时间以后，几乎一定会遇到一组越来越混乱的词：

**Agent、Agent Framework、Workflow、Runtime、Harness。**

更麻烦的是，同一个产品可能同时被叫做 Framework、Runtime，甚至承担 Harness 的职责。

这不是谁用错了词。

真正的问题是：**这些概念本来就不是同一个维度。**

与其问“这个产品到底属于哪一类”，不如先问五个工程问题：

| 概念 | 它主要回答的问题 |
| --- | --- |
| **Agent** | 谁在做决策和执行任务？ |
| **Framework / SDK** | 我用什么组件把 Agent 构建出来？ |
| **Workflow** | 任务步骤和控制流怎么组织？ |
| **Runtime** | 任务在哪里、以什么状态持续运行？ |
| **Harness** | 谁驱动 Agent Loop，并控制 Context、Tool、State 和 Policy？ |

只要把这五个问题分开，很多架构图就会突然清楚。

## 一、Agent：真正“做事”的那个执行主体

先从最小单位开始。

一个 Agent 通常可以抽象成：

```text
Agent
├── Goal / Instructions
├── Model
├── Tools
└── Runtime Behavior
```

OpenAI Agents SDK 对 Agent 的定义就很接近这个思路：一个配置了 Instructions、Tools，以及 Handoff、Guardrail 等运行时行为的 LLM。

所以 Agent 更像一个**执行角色**。

例如：

- Coding Agent
- Test Agent
- Research Agent
- Review Agent

这些名字描述的是：

**谁负责完成这类任务，以及它具备什么能力。**

但 Agent 自己并不等于整个执行系统。

一个“测试 Agent”可以知道如何生成测试、调用浏览器、判断结果，但它不一定自己负责：

- Session 怎么保存；
- Tool 怎么真正执行；
- 失败是否 Retry；
- 权限是否允许；
- Trace 怎么记录。

这些通常属于外层系统。

所以第一个边界是：

> **Agent 描述的是执行主体，不是完整运行基础设施。**

## 二、Agent Framework / SDK：帮助你把系统搭起来的开发工具箱

Framework 或 SDK 回答的是另一个问题：

> **我用什么开发抽象来构建 Agent？**

一个 Agent Framework 通常会提供一些现成组件：

- Agent 定义
- Tool
- Session
- Memory
- Handoff
- Guardrail
- Workflow
- Middleware
- Tracing
- Hosting Integration

例如 Microsoft Agent Framework 本身同时提供 Agent、Workflow、Memory、Harness 等多个概念。

OpenAI Agents SDK 则提供 Agent、Tool、Handoff、Guardrail、Session、Tracing，并通过 Runner 管理 Agent Loop。

所以 Framework / SDK 更像：

```text
开发者
  ↓
Framework / SDK
  ├── Agent API
  ├── Tool API
  ├── Session API
  ├── Workflow API
  └── Runtime / Runner
```

它是**构建系统的工具集合**。

关键点在这里：

**Framework 不是一个与 Harness 平行、互斥的类别。**

Framework 完全可以内部自带 Harness。

也可以只给你一些组件，让你自己写 Harness。

OpenAI 官方文档甚至明确区分：

- 如果你直接用 Responses API，你自己拥有 Loop、Tool Dispatch 和 State；
- 如果你用 Agents SDK，SDK 的 higher-level runtime 会替你管理 Turns、Tools、Guardrails、Handoffs 和 Sessions。

这说明“SDK”和“Runtime”本来就可能叠在一起。

## 三、Workflow：规定“任务怎么走”

Workflow 最容易理解，因为它关注的是：

**控制流。**

例如一个测试流程：

```text
读取 PRD
   ↓
生成测试点
   ↓
人工确认
   ↓
生成用例
   ↓
执行测试
   ↓
生成报告
```

这里每一步是谁完成的不重要。

可能全部由 Agent 做，也可能有程序、人工、服务混合执行。

Workflow 关心的是：

- 顺序；
- 分支；
- 并行；
- 等待；
- 审批；
- Retry；
- Checkpoint；
- 状态转移。

因此 Workflow 更接近：

**Process / Graph / State Machine。**

Cloudflare 在自己的文档里有一个很好的区分：当一个 durable job 的“步骤本身很重要”，例如需要长时间等待、审批门、可重试的确定性副作用时，应让 Workflow 拥有整个 Process，而其中某一步再调用模型完成推理。

这和完全由 Agent 自主决定下一步，是两种不同思路。

### Workflow 更强调“预先定义”

典型 Workflow 是：

```text
A → B → C
    ↓
    D
```

流程边界在设计时就已经比较明确。

Agent Loop 则更像：

```text
Observe
  ↓
Reason
  ↓
Action
  ↓
Observe
  ↓
???
```

下一步可能由模型动态决定。

所以可以粗略理解成：

> **Workflow 是系统提前决定任务怎么走；Agent 是运行过程中动态决定下一步怎么走。**

但两者也可以组合。

例如：

```text
Workflow
├── Step 1: deterministic parser
├── Step 2: Agent research
├── Step 3: human approval
└── Step 4: deterministic deploy
```

这往往比“所有东西都做成 Agent”更可靠。

## 四、Runtime：让任务真正持续运行的基础设施

Runtime 是这几个词里最容易被无限扩大的一个。

广义 Runtime 可以包含所有运行时能力。

但如果为了架构分析，我更愿意把它收窄成：

> **让 Agent 或 Workflow 能够持续存在、调度和恢复的执行基础设施。**

例如：

- Session
- Persistent State
- Scheduling
- Queue
- Background Execution
- Checkpoint
- Resume
- Networking
- Isolation
- Storage
- Observability

Cloudflare 对 Runtime 和 Harness 的拆分非常清楚。

它把 Runtime 定义为底层持久基础设施，负责：

- Agent class
- State
- Session
- Routing
- WebSocket
- Scheduling
- Observability

然后 Harness 建在 Runtime 上面，负责模型调用、Prompt、Tool Loop、Memory Strategy 和 Lifecycle。

可以画成：

```text
Application
     ↓
Harness
     ↓
Runtime
     ↓
Execution Environment / Infrastructure
```

但注意，这只是 Cloudflare 的一种架构划分。

微软则直接把 Harness 称为 **runtime scaffolding**。

所以现实中 Runtime 和 Harness 的边界并没有统一标准。

## 五、Harness：把模型决策变成受控执行

如果说 Workflow 决定流程结构，Runtime 提供执行基础设施，那么 Harness 更靠近 Agent 本身：

> **它负责把模型的一轮轮判断驱动成真正的 Agent Loop。**

VS Code 对 Harness 的解释很具体：

一次请求进来后，Harness 会：

1. 获取请求和当前 Session State；
2. 准备 Instructions、Context 和 Tool Definitions；
3. 调用模型；
4. 如果模型请求 Tool Call，就应用 Permission / Approval；
5. 把 Tool Call 路由到执行环境；
6. 获取 Tool Result；
7. 再交给模型；
8. 持续保存消息、Tool Call、结果和代码修改。

所以 Harness 的核心不是简单的“调用 LLM”。

它控制的是：

```text
Context
   ↓
Model
   ↓
Decision
   ↓
Policy / Permission
   ↓
Tool Execution
   ↓
Observation
   ↓
State Update
   ↓
Next Turn
```

因此 Harness 回答的是：

**Agent 这一轮到底怎么运行。**

## 六、一个最重要的区别：Workflow 控制流程，Harness 控制 Agent Loop

这两个最容易混。

假设我们要实现一个代码修复任务。

### Workflow 方式

```text
读取 Issue
   ↓
定位代码
   ↓
生成 Patch
   ↓
执行测试
   ↓
测试失败？
 ┌─Yes──→ 修复
 │
 No
 ↓
创建 PR
```

流程由系统提前定义。

### Harness 方式

Harness 可能只给 Agent 一个目标：

> 修复 Issue #123，并证明修复有效。

然后：

```text
Model → grep
Model → open file
Model → edit
Model → run test
Model → inspect failure
Model → edit again
Model → run test
...
```

具体路径是运行时动态产生的。

所以一个很实用的判断方法是：

- **路径主要由代码预定义：更像 Workflow**
- **路径主要由模型运行时决定：更依赖 Harness**

真实系统通常两者一起用：

```text
Workflow
   ↓
"修复代码" Step
   ↓
Agent + Harness
   ↓
Result
   ↓
Workflow
   ↓
Quality Gate
```

我认为这会是企业 Agent 系统里越来越常见的结构。

## 七、Runtime 和 Harness 为什么总是分不清

因为它们天然贴得很近。

Session 是 Runtime 还是 Harness？

Trace 是 Runtime 还是 Harness？

Retry 是谁负责？

答案往往取决于具体产品架构。

例如：

### Cloudflare

明确分层：

```text
Harness
  ↓
Agents SDK Runtime
```

Runtime 提供 durable infrastructure，Harness 提供 Agent behavior。

### Microsoft Agent Framework

Harness 被称为 runtime scaffolding，而且它本身由 Agent Framework 里的多个现有组件组合而成，并不是一个完全独立的新 Runtime。

### OpenAI Agents SDK

官方主要称它为 SDK + higher-level runtime。

但它实际负责：

- Agent Loop
- Tool Execution
- Guardrail
- Handoff
- Session
- Tracing

从职责上看，它已经覆盖了大量 Harness 能力。

所以看到一个新产品时，最没有意义的问题是：

> 它到底算 Runtime 还是 Harness？

更有意义的是：

> **它实际负责了哪些生命周期职责？**

## 八、以后看任何 Agent 架构，我建议问这六个问题

与其记名词，我更推荐记一组检查问题。

### 1. 谁决定下一步动作？

- 固定代码？
- Workflow Graph？
- LLM？

这决定系统有多大的动态性。

### 2. 谁驱动 Agent Loop？

- 自己写 while loop？
- SDK Runner？
- Provider Harness？

这基本可以定位 Harness 在哪。

### 3. Tool 是谁执行的？

模型只会“请求调用”。

真正执行、校验、超时、审批的是谁？

### 4. State 存在哪里？

- Prompt History？
- Memory Store？
- Session？
- Durable Runtime？

这决定任务能否长期运行和恢复。

### 5. Process 是谁控制的？

- Agent 自己规划？
- Workflow Engine？
- 两者混合？

这决定确定性和自治性的边界。

### 6. 出问题以后，谁负责处理？

- Retry
- Timeout
- Rollback
- Resume
- Trace
- Verification

如果这些全靠 Prompt，那么这套系统通常还处在比较早期的阶段。

## 九、把五个概念放到一张图里

如果必须画一张简化图，我会这样画：

```text
┌─────────────────────────────────────┐
│              Application            │
│                                     │
│  Workflow                           │
│  ├── deterministic step             │
│  ├── approval                       │
│  ├── Agent step ───────────────┐    │
│  └── release step              │    │
│                                │    │
│                    ┌───────────▼──┐ │
│                    │    Agent     │ │
│                    │ Goal / Model │ │
│                    │ Tools        │ │
│                    └──────┬───────┘ │
│                           │         │
│                    ┌──────▼───────┐ │
│                    │   Harness    │ │
│                    │ Loop/Context │ │
│                    │ Tool/Policy  │ │
│                    └──────┬───────┘ │
│                           │         │
│                    ┌──────▼───────┐ │
│                    │   Runtime    │ │
│                    │ State/Session│ │
│                    │ Schedule     │ │
│                    └──────────────┘ │
└─────────────────────────────────────┘

Framework / SDK：
提供构建上面这些组件的 API 和抽象。
```

这张图不是行业标准。

但它足够帮助我们做工程讨论。

## 十、为什么我要把这些边界分清楚

因为如果边界不清楚，很多工程问题最后都会错误地归因给“模型不够聪明”。

Agent 经常重复调用工具：

> 是模型问题，还是 Harness 没有限制 Retry？

长任务中途丢失状态：

> 是模型问题，还是 Runtime 没有 Persistence？

流程必须严格经过审批：

> 应该继续靠 Agent 自觉，还是交给 Workflow？

删除文件需要授权：

> 写进 Prompt，还是让 Harness 强制拦截？

任务执行完却不知道中间发生过什么：

> 是回答质量问题，还是 Trace 能力缺失？

当这些问题被拆开以后，Agent Engineering 才真正从：

**调 Prompt**

进入：

**设计执行系统。**

## 结语

如果只记住一句话，可以记这一组：

**Agent 决策。**

**Framework 提供开发组件。**

**Workflow 组织流程。**

**Runtime 维持运行。**

**Harness 驱动并控制 Agent Loop。**

现实产品会相互重叠，所以不要执着于标签。

真正应该关注的是：

**谁在控制执行。**

下一篇我会进入更偏流量和工具的一篇：

**《2026 年 Agent Harness / Runtime 工具有哪些？》**

我们会把主流方案按“谁负责 Loop、Tool、State、Trace、Permission”真正拆开，而不是只列一个工具清单。

---

## 参考资料

- Microsoft Learn — [Agent Harness](https://learn.microsoft.com/agent-framework/agents/harness)
- Microsoft Learn — [Agent Framework Concepts](https://learn.microsoft.com/agent-framework/concepts/)
- Visual Studio Code — [Understand agent harnesses](https://code.visualstudio.com/docs/agents/concepts/agent-harnesses)
- Cloudflare Agents — [Harnesses](https://developers.cloudflare.com/agents/harnesses/)
- Cloudflare Agents — [Workflows](https://developers.cloudflare.com/agents/harnesses/think/workflows/)
- OpenAI Agents SDK — [Documentation](https://openai.github.io/openai-agents-python/)
- OpenAI Agents SDK — [Agents](https://openai.github.io/openai-agents-python/agents/)
