---
layout: post
title: "Agent Harness 是什么？为什么它正在成为 Agent 工程的关键一层"
date: 2026-09-22 07:50:00 +0800
categories: [Agent-Harness, Agent-Reliability]
permalink: /harness/what-is-agent-harness/
description: "从模型调用、Agent Loop、Tool、Context、State 到 Trace，解释 Agent Harness 在 Agent 系统里到底负责什么。"
tags: ["agent-harness", "agent-reliability", "trace-evidence"]
updated: 2026-09-22 08:27:38 +0800
last_modified_at: 2026-09-22 08:27:38 +0800
series: agent-harness
series_order: 1
---

> **Agent Harness 系列 #01**  
> 从入门、工具、实操一路写到 Trace、Failure Regression 和 Quality Gate。

如果把大模型看成 Agent 的“大脑”，那么 **Harness 更像它外面的运行时和控制层**。

模型负责判断“下一步想做什么”；Harness 负责把这个判断变成一次真正的执行：准备上下文、暴露工具、执行 Tool Call、维护状态、处理权限、记录 Trace，再把结果送回模型，直到任务结束。

这也是为什么一个能聊天的 LLM，和一个能够连续工作几十分钟甚至几小时的 Agent，中间还差了很大一层工程系统。

这层东西，现在越来越常被叫做：

**Agent Harness。**

## 一、先给一个工程化定义

微软目前对 Agent Harness 的定义很直接：

> 它是把语言模型变成能够执行工作的 Agent 的运行时脚手架。

它负责驱动模型调用和工具调用、管理上下文和会话状态、应用审批策略，并让 Agent 能持续推进多步骤任务。

VS Code 对 Harness 的解释也很接近：模型负责推理和选择动作，Harness 负责协调这些动作真正执行，包括准备请求、调用工具、处理审批、保存结果和维护 Session。

因此，如果让我用一句更工程化的话定义：

**Agent Harness = 驱动 Agent Loop，并控制 Agent 如何获取上下文、调用工具、维护状态和完成执行的运行时控制层。**

这里需要先提醒一点：**Harness 还不是一个边界完全统一的行业术语。**

不同产品对 Harness、Runtime、Framework 的划分不完全一样。比如 Cloudflare 会把 Runtime 和 Harness 分开：Runtime 提供持久状态、Session、调度等基础设施，Harness 更偏向模型调用、Prompt 构造、Tool Loop 和生命周期行为；微软则直接把 Harness 称为 runtime scaffolding。

所以讨论 Harness 时，与其纠结名词边界，不如看它到底承担了哪些执行职责。

## 二、为什么最近突然开始频繁看到 Harness

因为 Agent 正在从“一次模型调用”变成长时间运行的执行系统。

2026 年，Harness 这个词已经明显从少数工程团队的内部说法进入主流 Agent 产品。

微软在 Agent Framework 中正式提供了 Harness，把 Loop、Planning、Memory、Context Management、Approval 和 Telemetry 组合成一套可直接使用的执行层。

VS Code 的 Agent 文档也专门增加了 Agent Harness 概念，用它解释 Model、Tool、Session、Execution Environment 是如何被连接起来的。

OpenAI 在 2026 年 9 月发布 Agents API 时，也明确提到把支撑 Codex 的 **harness + infrastructure** 提供给开发者：Harness 负责 Context、Tool 和 Subagent 等 Agent 行为，而底层基础设施保证长时间任务可以持续运行。

这背后其实是同一个变化：

**Agent 的主要工程问题，正在从“模型能不能回答”，转向“任务能不能持续、受控地执行”。**

## 三、没有 Harness 时，你得到的只是一次模型调用

最简单的 LLM 应用大概是：

```text
User
  ↓
Model
  ↓
Answer
```

但一个 Agent 至少要变成：

```text
Goal
  ↓
Build Context
  ↓
Model
  ↓
Tool Call?
  ├─ No  → Final Result
  │
  └─ Yes
       ↓
   Permission / Validation
       ↓
   Execute Tool
       ↓
   Observation
       ↓
   Update State
       ↓
      Model
       ↓
      ...
```

模型只负责其中一部分。

真正让这条循环跑起来的是模型外面的系统。

伪代码大致是：

```python
while not done:
    context = build_context(state)

    decision = model(context, tools)

    if decision.tool_call:
        check_permission(decision.tool_call)
        result = execute_tool(decision.tool_call)

        trace.record(decision, result)
        state.update(result)
    else:
        done = True
        final_result = decision.output
```

真正进入工程环境后，还会继续加入：

- Timeout
- Retry
- Tool Approval
- Token / Cost Budget
- Context Compaction
- Session Persistence
- Human in the Loop
- Error Recovery
- Trace
- Verification

这些东西加起来，才逐渐形成一个真正可用的 Harness。

## 四、Harness 到底管什么

我现在更倾向于把 Harness 的职责拆成七类。

### 1. Context：模型这一次到底能看到什么

Agent 每一次调用模型之前，都要重新构造 Context。

其中可能包括：

- System Instruction
- 用户目标
- 历史消息
- 文件内容
- Memory
- 当前任务状态
- Tool Schema
- 上一步 Observation

长任务跑到后面，Context 不可能无限增长。

所以 Harness 还要决定：

**保留什么、丢掉什么、什么时候做摘要或 Compaction。**

这已经不是 Prompt Engineering，而是 Runtime Engineering。

### 2. Tool：模型想调用工具，谁真正执行

模型通常只会返回：

> 我要调用 tool_x，参数是 xxx。

真正执行工具的是 Harness。

因此 Harness 至少要处理：

- Tool Registry
- 参数校验
- 调用路由
- 执行结果回传
- Tool Error
- 并发
- Timeout

一旦工具存在副作用，还要继续处理权限和审批。

### 3. Loop：什么时候继续，什么时候结束

Agent 最基本的结构就是循环：

**Model → Action → Observation → Model**

但这个 Loop 不能无限运行。

Harness 要知道：

- 最大迭代次数是多少；
- 连续失败多少次终止；
- 是否允许 Retry；
- 是否需要用户补充信息；
- 哪些状态算完成；
- 哪些状态必须中断。

这其实已经很接近一个状态机。

### 4. State：任务执行到哪了

对于几分钟的简单任务，消息历史可能就够。

但长任务通常还需要保存：

- Current Goal
- Plan
- Completed Steps
- Pending Tasks
- Tool Results
- Artifacts
- Checkpoint
- Resume State

否则 Agent 一旦中断，就可能不知道自己之前做到了哪里。

### 5. Permission：模型“想做”不代表系统“允许做”

这是 Harness 和 Prompt 最关键的区别之一。

Prompt 可以告诉模型：

> 删除文件前必须确认。

但 Prompt 本质上只是指导。

Harness 可以真正做到：

```text
delete_file()
     ↓
Need Approval?
     ↓
 YES ──→ Pause
          ↓
       Human Approve
          ↓
        Execute
```

**可靠性不能只建立在模型“记得遵守规则”上。**

真正重要的边界，需要由模型之外的执行层控制。

### 6. Trace：任务完成以后，能不能知道刚才发生了什么

Agent 一旦进入多步骤执行，只保留最终结果是不够的。

Harness 最好能够记录：

- Model Turn
- Tool Call
- Tool Result
- Handoff
- Guardrail
- State Change
- Error
- Retry

OpenAI Agents SDK 的 Tracing 就会记录模型生成、Tool Call、Handoff、Guardrail 等事件。

这里开始出现 Harness 和 Agent Reliability 的连接点：

**没有 Trace，就很难证明一个 Agent 为什么成功，也很难定位它为什么失败。**

### 7. Recovery：失败以后怎么办

真实 Agent 一定会失败。

网络超时、Tool Error、Context 丢失、模型选错工具、环境状态变化，都可能发生。

所以 Harness 不应该只负责：

> 把 Agent 跑起来。

还应该逐步具备：

> Agent 出错以后怎么继续。

包括 Retry、Fallback、Checkpoint、Resume、Rollback，以及后面我们会专门讨论的 Failure Regression。

## 五、Harness、Framework、Workflow、Runtime 到底什么关系

这是最容易混在一起的几个词。

| 概念 | 更关注什么 |
| --- | --- |
| **Model** | 推理、生成、选择下一步动作 |
| **Agent** | 一个有目标、指令和能力的执行主体 |
| **Agent Framework / SDK** | 构建 Agent 的开发组件和抽象 |
| **Workflow** | 任务应该按照什么流程或图执行 |
| **Runtime** | 状态、Session、调度、环境等执行基础设施 |
| **Harness** | 驱动 Agent Loop，并把 Model、Context、Tool、State、Policy 组合起来运行 |

它们并不是互斥的产品类别。

一个 Agent Framework 完全可以内置 Harness。

一个 Harness 也可能建立在一个 Runtime 上。

一个 Workflow Engine 同样可能承担部分 Harness 能力。

例如 OpenAI Agents SDK 提供 Agent Loop、Tool、Guardrail、Session 和 Trace。官方更常把它描述为 SDK 和 higher-level runtime，但从职责上看，它已经覆盖了 Harness 的大量核心能力。

所以以后看到某个产品时，不要先问：

> 它到底算 Framework 还是 Harness？

更有效的问题是：

> **Agent Loop 是谁驱动的？Context 谁管理？Tool 谁执行？State 存在哪里？Permission 谁控制？Trace 谁记录？**

把这几个问题回答清楚，架构基本就看明白了。

## 六、为什么 Prompt 解决不了 Harness 的问题

这是我认为最值得区分的一点。

很多 Agent 系统早期都会不断往 System Prompt 里加规则：

- 不要重复调用工具；
- 出错之后重试；
- 修改文件之前先检查；
- 完成之后执行测试；
- 不允许删除重要文件。

Prompt 确实能够改善行为。

但 Prompt 解决的是：

**模型应该怎么做。**

Harness 解决的是：

**系统允许它怎么做，以及做了以后系统怎么处理。**

例如“最多调用工具 20 次”，如果只写在 Prompt 里，最终还是模型自己遵守。

如果 Harness 维护一个计数器：

```text
tool_calls >= 20
       ↓
 terminate_run()
```

这才是真正的执行约束。

所以对于 Agent Reliability 来说，有一个非常重要的边界：

**能用 Runtime 约束的东西，不应该只依赖 Prompt。**

## 七、一个最小 Harness 至少需要什么

如果我们完全不用 Agent Framework，自己从零写一个最小 Harness，我认为至少需要五个模块：

```text
┌──────────────────────────────┐
│          Agent Harness       │
│                              │
│  Context Builder             │
│        ↓                     │
│  Model Adapter               │
│        ↓                     │
│  Loop / State Machine        │
│        ↓                     │
│  Tool Dispatcher + Policy    │
│        ↓                     │
│  Trace / Result              │
└──────────────────────────────┘
```

有了这五块，一个最基础的 Agent 才算真正跑起来。

再继续往生产环境走，会逐步增加：

```text
Session
Checkpoint
Approval
Budget
Sandbox
Recovery
Evidence
Evaluation
Regression
Quality Gate
```

而这正是 Harness 系列后面会继续拆的内容。

## 八、怎么判断一个系统有没有真正的 Harness

以后看到一个所谓 Agent 平台，可以直接问这几个问题：

1. **Agent Loop 在哪里？**
2. **Context 是谁构造和裁剪的？**
3. **Tool Call 是谁执行和校验的？**
4. **Session / State 怎么保存？**
5. **危险动作能不能在模型之外被阻断？**
6. **一次运行结束后能不能完整重建执行轨迹？**

如果这些问题没有明确答案，那么它可能只是：

**LLM + Tools + 一些 Prompt。**

它当然也能工作，但离真正可控的 Agent Runtime 还有距离。

## 九、Harness 真正有意思的地方，是它开始连接 Reliability

如果目标只是做一个 Demo，Harness 只需要把 Loop 跑通。

但一旦 Agent 开始修改代码、操作 ERP、调用外部 API，甚至进入真实生产流程，问题就会变成：

- Agent 做的事情是否受控？
- 最终结果有没有独立证据？
- 中间有没有产生危险副作用？
- 出错以后能不能定位？
- 同样的失败以后会不会再次发生？

于是 Harness 的边界会自然向外扩展：

```text
Agent
  ↓
Harness
  ↓
Trace
  ↓
Verification
  ↓
Failure
  ↓
Regression
  ↓
Quality Gate
```

这也是我想写这个系列的原因。

**Agent Harness 不只是让 Agent“能跑起来”的东西。**

当 Agent 开始进入真实工程系统后，它还会逐渐承担另外一个角色：

**成为 Agent Reliability 真正落地的执行边界。**

下一篇：[Agent、Framework、Workflow、Runtime、Harness 到底有什么区别？](/harness/agent-framework-workflow-runtime-harness/)

---

## 参考资料

- Microsoft Learn — [Agent Harness](https://learn.microsoft.com/agent-framework/agents/harness)
- Visual Studio Code — [Understand agent harnesses](https://code.visualstudio.com/docs/agents/concepts/agent-harnesses)
- Microsoft Agent Framework — [The Microsoft Agent Framework Harness is now released](https://devblogs.microsoft.com/agent-framework/the-microsoft-agent-framework-harness-is-now-released/)
- Cloudflare Agents — [Harnesses](https://developers.cloudflare.com/agents/harnesses/)
- OpenAI — [Introducing the Agents API](https://openai.com/index/introducing-the-agents-api/)
- OpenAI Agents SDK — [Documentation](https://openai.github.io/openai-agents-python/)
