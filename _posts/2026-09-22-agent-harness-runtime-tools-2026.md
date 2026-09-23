---
layout: post
title: "2026 Agent Harness / Runtime 工具盘点：主流方案怎么选"
date: 2026-09-22 16:10:00 +0800
categories: [Agent-Harness, Agent-Runtime]
permalink: /harness/agent-harness-runtime-tools-2026/
description: "2026 Agent Harness / Runtime 工具盘点：对比 OpenAI、Microsoft、Cloudflare、LangGraph、Google ADK 与 smolagents 的 Loop、State、Trace、Permission 和 Recovery 能力，帮助选择合适的 Agent 技术栈。"
tags: ["agent-harness", "agent-runtime", "agent-framework", "tools"]
series: agent-harness
series_order: 3
---

> **Agent Harness 系列 #03**  
> 上一篇：[Agent、Framework、Workflow、Runtime、Harness 到底有什么区别？](/harness/agent-framework-workflow-runtime-harness/)

如果你搜索“Agent Harness”，会遇到一个很现实的问题：

**真正把自己叫 Harness 的产品并不多。**

更多工具会把自己称为：

- Agent SDK
- Agent Framework
- Runtime
- Orchestration Framework
- Workflow Engine

但从工程职责看，它们都可能覆盖 Harness 的一部分甚至大部分能力。

所以这篇不按产品自称分类，而统一看七个问题：

1. 谁驱动 Agent Loop？
2. Tool 谁执行？
3. State / Session 怎么保存？
4. Permission / Guardrail 怎么做？
5. Trace 怎么记录？
6. 任务中断以后怎么恢复？
7. 它更适合哪类场景？

> 信息截至 **2026-09-22**。Agent 工具变化很快，具体 API 以官方文档为准。

## 先看结论表

| 工具 | Loop | State / Session | Permission / Guardrail | Trace / Observability | Durable / Recovery | 更像什么 |
| --- | --- | --- | --- | --- | --- | --- |
| OpenAI Agents SDK | 内置 Runner | 内置 Session | Guardrail / HITL | 内置 Tracing | 支持会话与中断恢复，复杂持久执行需进一步组合 | 轻量 Agent Runtime / SDK |
| OpenAI Agents API | 托管 | 托管环境与中间结果 | 托管 Harness 能力 | 平台级 | 面向长时间运行任务 | 托管 Harness + Infrastructure |
| Microsoft Agent Framework Harness | 内置 | Session / Context / Memory | Tool Approval | Observability / Middleware | 长任务、Todo、Compaction、Background 能力 | 明确自称 Harness |
| Cloudflare Agents | 可自建或用 Harness | Durable State / Session | 由 Harness / App 控制 | Runtime Observability | Workflow 提供重试、等待、恢复 | Runtime + Harness 分层 |
| LangGraph | Graph / Runtime 驱动 | Checkpointer / Store | Interrupt / HITL 可组合 | 常与 LangSmith 配合 | Durable Execution / Resume | Stateful Agent Orchestration |
| Google ADK + Agent Runtime | Runner / Agent 编排 | Session Service | Callback / Tool 层可控 | Trace / Eval 生态 | Agent Runtime / Sandbox / Deployment | Agent Framework + Cloud Runtime |
| Hugging Face smolagents | MultiStepAgent | 以内存和步骤为主 | final checks / 自定义 | Logger / callbacks | 不以 durable runtime 为核心 | 轻量 Agent Loop |

这张表不是排名。

它真正说明的是：

**今天所谓“Agent Harness”，不是一个单独产品品类，而是一组运行时能力。**

---

## 1. OpenAI Agents SDK：最容易理解 Agent Loop 的生产级入口

OpenAI Agents SDK 的核心抽象很少：

- Agent
- Runner
- Tools
- Handoffs
- Guardrails
- Sessions
- Tracing

关键是 **Runner**。

官方文档明确说明：当你使用 Agent + Runner 时，SDK 会替你管理 Turns、Tools、Guardrails、Handoffs 和 Sessions；如果你希望自己掌控 Loop、Tool Dispatch 和 State，则可以直接使用 Responses API。

这恰好体现了 Harness 的边界：

```text
Responses API
    ↑
你自己写 Loop / Tool Dispatch / State
    ↑
更低层控制

Agents SDK
    ↑
Runner 帮你管理 Agent Loop
    ↑
更高层 Runtime
```

### 它的优势

对于刚开始做 Agent 工程的人，它很适合用来理解：

- Agent Loop 怎么跑；
- Tool Call 怎么接回来；
- Session 怎么保持状态；
- Guardrail 在哪里执行；
- Trace 如何串联一次完整运行。

SDK 自带 Tracing，会记录模型生成、Tool Call、Handoff、Guardrail 和自定义事件。

### 需要注意

Agents SDK 并不意味着“所有可靠性问题自动解决”。

例如：

- Tool 的副作用控制；
- 企业级审批；
- 跨服务恢复；
- Failure Regression；
- Release Gate；

仍然需要你的应用层继续建设。

官方文档：

- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [Running agents](https://openai.github.io/openai-agents-python/running_agents/)
- [Tracing](https://openai.github.io/openai-agents-python/tracing/)

---

## 2. OpenAI Agents API：把 Harness 和基础设施一起托管

2026 年 9 月，OpenAI 发布了 Agents API public beta。

它和 Agents SDK 不完全是同一层东西。

官方的描述很明确：Agents API 把支撑 Codex 的 **harness + infrastructure** 提供给开发者。

其中 Harness 负责：

- Context
- Tools
- Subagents
- Agent behavior

Infrastructure 则负责：

- 长时间持续运行；
- 工作环境；
- 文件；
- 代码执行；
- 中间结果保存。

也就是说：

```text
Agents SDK
→ 你在自己的应用里运行 Agent Runtime

Agents API
→ 直接使用托管的 Harness + Infrastructure
```

这代表一个很重要的趋势：

**Harness 正从一个代码库里的 Loop，变成云端运行基础设施。**

如果未来 Coding Agent、Research Agent 要连续执行数小时甚至数天，仅仅有一个 while loop 显然不够。

官方资料：

- [Introducing the Agents API](https://openai.com/index/introducing-the-agents-api/)

---

## 3. Microsoft Agent Framework Harness：目前“Harness”定义最明确的一套

如果你想找一个真正把 Harness 当一级概念设计的框架，Microsoft Agent Framework 很值得看。

微软把 Harness 定义成：

**把语言模型变成能够执行工作的 Agent 的 runtime scaffolding。**

它组合已有的 Agent Framework 能力，包括：

- Chat Client
- Chat Pipeline
- Session
- Context Provider
- Memory
- Todo
- Operating Mode
- Tool Approval
- Middleware
- Observability
- Bounded Loop
- Context Compaction

它的设计思路不是重新造一个独立 Runtime，而是把这些组件组装成一个 opinionated Harness。

这点很有参考价值：

> **Harness 未必是一个单独服务，它也可以是一组 Runtime 能力的组合层。**

如果你在企业内部自己建设 Harness，这种“组合现有组件，而不是把所有东西重写”的思路很实用。

官方资料：

- [Microsoft Agent Framework — Agent Harness](https://learn.microsoft.com/agent-framework/agents/harness)
- [Agent Framework Concepts](https://learn.microsoft.com/agent-framework/concepts/)

---

## 4. Cloudflare Agents：Runtime 和 Harness 分层最清楚

Cloudflare 的文档很适合拿来建立架构心智模型。

它明确把两层拆开：

### Runtime

负责 durable infrastructure：

- Agent State
- Sessions
- Routing
- WebSocket
- Scheduling
- Communication
- Observability

### Harness

负责 Agent Behavior：

- Model Call
- Prompt Construction
- Tool Selection
- Tool Result
- Streaming
- Memory Strategy
- Lifecycle Hook
- Continue / Stop

可以画成：

```text
Application
    ↓
Harness
    ↓
Agents Runtime
    ↓
Durable Infrastructure
```

Cloudflare 还把 Workflow 作为另一层 durable execution 能力，用于：

- 长任务；
- 自动重试；
- 失败恢复；
- 等待外部事件；
- 审批。

这个分层非常适合企业架构：

**Agent 决策交给 Harness，确定性的长流程交给 Workflow。**

官方资料：

- [Cloudflare Harnesses](https://developers.cloudflare.com/agents/harnesses/)
- [Cloudflare Runtime](https://developers.cloudflare.com/agents/runtime/)
- [Agents with Workflows](https://developers.cloudflare.com/agents/concepts/workflows/)

---

## 5. LangGraph：更像“可持久执行的 Agent 状态机”

LangGraph 不强调 Harness 这个词。

但如果从能力看，它覆盖了大量 Runtime / Harness 邻接问题。

官方把 LangGraph 定义为一个用于构建 **long-running、stateful agents** 的低层 orchestration framework，重点能力包括：

- Durable Execution
- Streaming
- Human-in-the-loop
- Persistence
- Memory

LangGraph 最有特点的不是“帮你写 Prompt”，而是：

**把 Agent 执行过程建模成一个可保存、恢复、分支和检查的 Graph State。**

它的 Persistence 又拆成：

- Checkpointer：保存 thread 内 graph state；
- Store：保存跨 thread 的长期数据。

因此它很适合：

- 状态复杂；
- 流程存在确定性节点；
- 需要人工介入；
- 任务需要中断恢复；
- 想精确控制 Agent / Workflow 混合执行。

官方资料：

- [LangGraph Reference](https://langchain-ai.github.io/langgraph/reference/)
- [LangGraph Persistence](https://langchain-ai.github.io/langgraphjs/how-tos/cross-thread-persistence-functional/)

---

## 6. Google ADK + Agent Runtime：Framework 与云 Runtime 的组合路线

Google ADK 更像完整的 Agent Development Kit。

它负责构建和编排 Agent，并提供：

- Agent
- Tool
- Session
- Runner
- Multi-agent
- Callback
- Evaluation
- Deployment 集成

Google Cloud Agent Runtime 则继续往执行环境走。

例如 Agent Runtime Code Execution 提供：

- Sandbox；
- 跨 Tool Call 持久化的执行状态；
- 隔离环境；
- 多步骤代码执行。

这和“Framework + Runtime”的组合路线很接近。

它值得关注的原因不是它有没有叫 Harness，而是：

**Agent 的开发层和生产运行层开始明显分离。**

官方资料：

- [Google Agent Development Kit](https://google.github.io/adk-docs/)
- [Agent Runtime Code Execution](https://google.github.io/adk-docs/tools/google-cloud/code-exec-agent-engine/)

---

## 7. smolagents：最适合把 Agent Loop 看清楚的轻量实现之一

Hugging Face 的 smolagents 走的是另一条路线：

**尽可能少的抽象。**

它的 MultiStepAgent 很直观：

```text
Thought
  ↓
Tool Call
  ↓
Execution
  ↓
Next Step
```

目前主要有两类 Agent：

- CodeAgent：通过 Python 代码表达 Tool Call；
- ToolCallingAgent：通过结构化 Tool Call 执行。

MultiStepAgent 还直接暴露：

- max_steps
- planning_interval
- step_callbacks
- final_answer_checks

这对理解 Harness 很有价值，因为你能很容易看到：

**Agent Loop 到底在哪里。**

但它本身并不把企业级 Durable Runtime 当作核心目标。

所以我更愿意把它定位成：

> **轻量 Agent Framework + 清晰 Agent Loop。**

官方资料：

- [smolagents Agents](https://huggingface.co/docs/smolagents/reference/agents)

---

## 到底应该怎么选？

如果只是想学习 Harness，我建议按目标选，而不是问“哪个最好”。

### 想最快理解 Agent Loop

看：

**OpenAI Agents SDK + smolagents**

它们的抽象比较直接。

### 想研究完整 Harness 设计

看：

**Microsoft Agent Framework Harness**

Todo、Compaction、Approval、Memory、Loop、Observability 被放在同一个 Harness 心智模型里。

### 想研究 Runtime / Harness 分层

看：

**Cloudflare Agents**

它把 Runtime、Harness、Workflow 的职责拆得非常清楚。

### 想做复杂状态和 Durable Execution

看：

**LangGraph**

尤其适合 Graph、Checkpoint、Human-in-the-loop 和恢复。

### 想看云托管长任务的发展方向

看：

**OpenAI Agents API + Google Agent Runtime**

这里已经不只是 SDK，而是在解决长期运行环境问题。

---

## 我会怎么评估一个新的 Harness 工具

以后再出现新的 Agent Framework，我不会先看它支持多少模型。

我会先做这张检查表：

```text
□ Loop 谁驱动？
□ Context 谁组装？
□ Tool 谁执行？
□ State 是否持久化？
□ Permission 能否模型外强制控制？
□ 是否有 Trace？
□ 是否支持 Checkpoint / Resume？
□ Tool Side Effect 怎么处理？
□ Failure 能否沉淀成 Regression？
□ 是否能接 Quality Gate？
```

前六项决定它是不是一个成熟的 Agent Runtime。

后四项决定它离 **Agent Reliability** 还有多远。

## 结语

2026 年再讨论 Agent 工具，已经不能只比较：

> 支持 GPT 还是 Gemini？

更应该比较：

> **谁在控制执行，执行留下了什么证据，失败以后系统怎么办。**

这也是 Harness 真正开始变得重要的原因。

下一篇：[OpenAI Agents SDK 入门：从安装到第一个 Agent](/harness/openai-agents-sdk-quickstart/)

---

## 参考资料

本文只采用各项目官方文档作为主要依据，链接已放在对应章节。能力状态截至 2026-09-22。
