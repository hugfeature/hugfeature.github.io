---
title: "2026 Agent Harness 工具全景：OpenAI、微软、Cloudflare、LangGraph 到底怎么选？"
channel: wechat
status: ready
source: /harness/agent-harness-runtime-tools-2026/
---

# 2026 Agent Harness 工具全景：OpenAI、微软、Cloudflare、LangGraph 到底怎么选？

最近 Agent 圈里一个词出现得越来越频繁：

**Harness。**

但真正开始查资料，会发现一个很尴尬的问题：有的产品叫 Agent SDK，有的叫 Runtime，有的叫 Framework，有的叫 Workflow，真正把自己叫 Harness 的反而不多。

那到底什么才算 Harness？

我现在更愿意换一种问法：

> 不看它叫什么，直接看它有没有能力控制 Agent 的真实执行。

具体看六件事：

**Loop 谁驱动？Tool 谁执行？State 谁保存？权限谁控制？Trace 谁记录？失败以后谁负责恢复？**

按这个标准再看主流工具，会清晰很多。

## OpenAI Agents SDK：最适合快速理解 Harness

OpenAI Agents SDK 的抽象很少：

Agent、Runner、Tool、Session、Guardrail、Trace。

最关键的是 Runner。

模型负责决定下一步做什么，Runner 负责把 Tool Call 真正执行、把结果送回模型，再继续下一轮。

也就是说：

**模型负责决策，Runtime 负责执行。**

如果你刚开始理解 Agent Loop，我最推荐从这里入手。

它的优势不是功能最多，而是边界比较清楚：Tool、Session、Tracing 都能直接看到。

但它也不是完整的企业 Reliability 平台。

Tool Side Effect、跨服务恢复、Failure Regression、Release Gate，这些仍然需要继续往上构建。

## Microsoft Agent Framework：目前最“像 Harness”的一个

微软现在已经直接把 Harness 当成一级概念。

它把这些能力组合到一起：

Context、Memory、Todo、Tool Approval、Middleware、Observability、Bounded Loop、Context Compaction……

这件事对企业团队很有启发。

Harness 未必一定要重新造一个大平台。

它也可以是：

**把已有的 Runtime 能力按照 Agent 生命周期重新组合。**

如果公司内部已经有审批、日志、任务系统、权限体系，可能真正应该做的是把这些能力接到 Agent 执行边界，而不是再造一遍。

## Cloudflare：Runtime 和 Harness 分得最清楚

Cloudflare 的设计非常适合建立架构心智模型。

它把 Runtime 和 Harness 分成两层。

Runtime 管：

State、Session、Routing、Scheduling、Durable Infrastructure。

Harness 管：

Model Call、Prompt、Tool Loop、Memory Strategy、Lifecycle。

再往外，还有 Workflow 去负责更确定性的长流程和恢复。

我很喜欢这个结构：

**Agent 的动态决策交给 Harness，确定性的业务流程交给 Workflow。**

这比“所有流程都让 Agent 自己决定”更适合企业系统。

## LangGraph：状态复杂时很有优势

LangGraph 不强调 Harness 这个名字。

但它真正擅长的是：

**把 Agent 执行建模成一个可持久化、可恢复的状态图。**

Checkpoint、Store、Human-in-the-loop、Durable Execution，都是长任务真正会碰到的问题。

如果任务中间需要停几个小时、等待审批、恢复后继续，或者 Agent 和确定性节点混合执行，LangGraph 会更有吸引力。

## smolagents：最适合看清 Agent Loop

smolagents 很轻。

也正因为轻，它非常适合学习。

你可以直接看到：

Thought → Action → Execution → Observation → Next Step。

CodeAgent 甚至让模型用 Python 代码表达 Tool Call。

它很适合研究 Agent Loop，但 CodeAgent 本地执行模型生成代码时一定要注意安全边界。真正不可信的执行环境，应该使用隔离 Sandbox，而不是默认本地执行。

## 我现在会怎么选

如果目标是**学习 Agent Loop**：

OpenAI Agents SDK + smolagents。

如果目标是**研究完整 Harness 架构**：

Microsoft Agent Framework。

如果目标是**研究 Runtime / Harness / Workflow 怎么分层**：

Cloudflare Agents。

如果任务是**复杂状态 + 长时间恢复**：

LangGraph。

但真正做企业 Harness，我不会先问：

> 哪个框架最好？

我会先画一张表：

- Loop 谁驱动？
- Context 谁管理？
- Tool 谁执行？
- State 是否持久化？
- Permission 能否在模型之外阻断？
- Trace 能不能重建执行过程？
- Checkpoint / Resume 有没有？
- Tool Side Effect 怎么处理？
- Failure 能不能进入 Regression？
- 最终能不能接 Quality Gate？

因为 Harness 最终不是选一个框架。

而是在回答：

> **Agent 做出一个决定以后，谁来保证这个决定能安全、可控、可验证地执行？**

这也是我接下来会持续写 Agent Harness 的原因。

我的网站「runtime质量论」已经整理了一套完整 Harness 系列，从 Agent Harness 是什么、工具实操，到 Trace、Evidence、Regression 和 Quality Gate。

如果你也在做 Agent / AI 测试 / Harness，这套问题可能比“选哪个模型”更值得提前想清楚。
