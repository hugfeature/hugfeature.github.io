---
layout: page
title: Agent Harness 教程：从入门、工具到 Reliability
description: 2026 Agent Harness 系统教程：从 Agent Harness 是什么、Framework/Runtime/Workflow 区别、主流工具与 OpenAI Agents SDK、smolagents 实操，一路到 Trace、Evidence、Regression 和 Quality Gate。
eyebrow: SERIES / 01
permalink: /harness/
---

{% assign entries = site.posts | where: 'series', 'agent-harness' | sort: 'series_order' %}
{% assign latest = entries | sort: 'date' | last %}

这是一个围绕 **Agent Harness / Agent Runtime / Agent Reliability** 的完整系列。

如果你第一次接触 Harness，可以把它先理解成：**模型负责决定下一步想做什么，Harness 负责把这些决策变成受控的真实执行。**

这里既有适合搜索和入门的概念文章，也有 OpenAI Agents SDK、smolagents 和手写 Harness 的实践内容，最后会进入 Trace、Evidence、Failure Regression、Eval 和 Quality Gate。

当前 **{{ entries.size }} 篇** · 最近更新 {{ latest.date | date: '%Y.%m.%d' }}

## 快速入口：你可能正在找这些

- **[Agent Harness 是什么？](/harness/what-is-agent-harness/)** — 从 Agent Loop、Context、Tool、State 和 Trace 建立最基本的 Harness 心智模型。
- **[2026 年 Agent Harness / Runtime 工具有哪些？](/harness/agent-harness-runtime-tools-2026/)** — 对比 OpenAI、Microsoft、Cloudflare、LangGraph、Google ADK 和 smolagents。
- **[OpenAI Agents SDK 入门教程](/harness/openai-agents-sdk-quickstart/)** — 从安装开始，跑通 Tool、Session、Runner 和 Trace。
- **[不用框架，自己写一个最小 Agent Harness](/harness/build-minimal-agent-harness/)** — 用最少代码理解 Loop、Tool Registry、Policy 和 Trace。
- **[Agent Harness 和 Agent Framework / Runtime / Workflow 有什么区别？](/harness/agent-framework-workflow-runtime-harness/)** — 一次解决最容易混淆的几个概念。

## 第一部分：先把 Harness 搞明白

### #01 [Agent Harness 是什么？为什么它正在成为 Agent 工程的关键一层](/harness/what-is-agent-harness/)

适合第一次接触 Harness。重点解释 Context、Tool、State、Permission、Trace 和 Recovery 为什么需要模型之外的运行时控制层。

### #02 [Agent、Framework、Workflow、Runtime、Harness 到底有什么区别？](/harness/agent-framework-workflow-runtime-harness/)

不把这些词硬分成互斥类别，而是用“谁决策、谁组织流程、谁维持运行、谁控制执行”拆边界。

### #03 [2026 年 Agent Harness / Runtime 工具有哪些？一张表看懂主流方案](/harness/agent-harness-runtime-tools-2026/)

按 Loop、State、Permission、Trace 和 Recovery 比较主流方案，而不是只列工具名单。

## 第二部分：把 Agent Loop 真正跑起来

### #04 [OpenAI Agents SDK 入门：从安装到第一个可调用工具的 Agent](/harness/openai-agents-sdk-quickstart/)

从 `pip install openai-agents` 开始，理解 Agent、Runner、Tool、Session 和 Tracing。

### #05 [smolagents 入门：几十行代码跑一个 Agent Loop](/harness/smolagents-agent-loop-quickstart/)

用 CodeAgent / ToolCallingAgent 看清 Multi-Step Agent Loop，并讨论代码执行的安全边界。

### #06 [不用 Agent Framework，自己写一个最小 Harness](/harness/build-minimal-agent-harness/)

自己实现 Model Adapter、Tool Registry、Policy、Trace 和 `max_steps`，理解框架替你做了什么。

### #07 [一个 Agent Loop 到底是怎么跑起来的？](/harness/how-agent-loop-works/)

把一次执行拆成 Context Build → Model Decision → Action Parse → Policy → Execution → Observation → State Update → Stop。

## 第三部分：从“能跑”进入 Reliability

### #08 [Agent 为什么需要 Harness：模型负责决策，系统负责约束](/harness/why-agent-needs-harness/)

核心问题：哪些规则不能继续只写在 Prompt 里，而必须下沉到 Runtime。

### #09 [Harness 到底应该管什么？从 Agent Loop 到 Reliability Boundary](/harness/what-should-agent-harness-own/)

定义 Harness 的职责边界：Context、Tool、State、Policy、Trace、Recovery 和 Verification Interface。

### #10 [Trace 不是日志：Harness 应该记录哪些执行证据？](/harness/trace-is-not-just-logs/)

从 Run、Turn、Tool、State、Artifact 和 Verification 六类事件设计可复盘的执行证据链。

### #11 [Agent 调错工具怎么办：Timeout、Retry、Budget 与 Side Effect](/harness/tool-failure-timeout-retry-budget-side-effect/)

处理 Tool Failure 的核心不是“失败就重试”，而是错误分类、幂等、副作用和真实状态验证。

### #12 [结果正确就够了吗？给 Agent 设计 Evidence Contract](/harness/agent-evidence-contract/)

把“Agent 说完成了”升级成 VERIFIED / UNVERIFIED：最终结论必须绑定可独立检查的 Evidence。

### #13 [一次 Agent 失败，怎么变成一条 Regression Case？](/harness/failure-to-regression-case/)

真实 Failure → 最小复现 → Root Cause → Oracle → Regression Case → Failure Corpus。

### #14 [Harness 和 Eval 平台到底是什么关系？](/harness/harness-vs-eval-platform/)

Harness 产出可信执行事实，Eval 把这些事实变成跨任务、跨版本的质量判断。

### #15 [Agent Harness 的终点：从执行引擎走向 Quality Gate](/harness/harness-to-quality-gate/)

最终把 Trace、Evidence、Regression 和 Eval 接到 Merge / Release，让 Reliability 真正影响交付。

## 推荐阅读路线

**刚入门：** #01 → #02 → #03 → #04 → #05 → #06 → #07

**已经在做 Agent：** #07 → #08 → #09 → #10 → #11

**做 Agent Reliability / Eval：** #08 → #10 → #12 → #13 → #14 → #15

**只想快速搭 Demo：** #03 → #04 → #05 → #06

## 几个常见问题

### Agent Harness 和 Agent Framework 是一回事吗？

不完全是。Framework / SDK 是开发组件集合，而 Harness 更关注 Agent 在运行时如何被驱动和控制。一个 Framework 可以内置 Harness，一个 Harness 也可以由多个 Framework / Runtime 组件组合而成。

### Agent Harness 和 Workflow 有什么区别？

Workflow 更强调预定义的流程和状态转移；Harness 更靠近模型驱动的动态 Agent Loop。真实系统通常会组合两者：Workflow 控制确定性业务流程，Harness 控制其中的 Agent 执行。

### Harness 只适用于 Coding Agent 吗？

不是。只要 Agent 会连续调用工具、维护状态并对外部环境产生影响，就会遇到 Context、Permission、Trace、Recovery 和 Verification 问题。

### 为什么这个系列最后会讲到 Quality Gate？

因为 Harness 的价值不应该停在“把 Agent 跑起来”。当执行过程能被记录、结果能被独立验证、失败能进入 Regression 后，这些信号最终应该影响 Merge、Release 或业务流程是否继续。

## 核心主线

**Harness → Trace → Evidence → Verification → Failure → Regression → Eval → Quality Gate**

这也是「runtime质量论」后续持续研究的主线。
