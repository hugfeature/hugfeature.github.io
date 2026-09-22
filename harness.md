---
layout: page
title: Agent Harness
permalink: /harness/
---

# Agent Harness：从入门到 Reliability

这个专栏会从基础概念、工具和 Demo 写起，再逐步进入 Runtime、Trace、Evidence、Failure Regression 和 Quality Gate。

目标不是只介绍框架，而是回答一个更实际的问题：

> **一个 Agent 做完任务以后，我们凭什么相信它？**

## 系列目录

1. [Agent Harness 是什么？为什么它正在成为 Agent 工程的关键一层](/harness/what-is-agent-harness/) ✅
2. Agent、Agent Framework、Workflow、Runtime、Harness 到底有什么区别？
3. 2026 年 Agent Harness / Runtime 工具有哪些？
4. OpenAI Agents SDK 入门：从安装到第一个 Agent
5. smolagents 入门：几十行代码跑一个 Agent Loop
6. 不用框架，自己写一个最小 Agent Harness
7. 一个 Agent Loop 到底是怎么跑起来的？
8. Agent 为什么需要 Harness：模型负责决策，系统负责约束
9. Harness 到底应该管什么？
10. Trace 不是日志：Harness 应该记录哪些执行证据？
11. Agent 调错工具怎么办：Timeout、Retry、Budget 与 Side Effect
12. 结果正确就够了吗？给 Agent 设计 Evidence Contract
13. 一次 Agent 失败，怎么变成一条 Regression Case？
14. Harness 和 Eval 平台到底是什么关系？
15. Agent Harness 的终点：从执行引擎走向 Quality Gate

## 阅读路线

如果你刚开始接触 Agent，建议从 **#01 → #02 → #04 → #06** 开始。

如果你已经在做 Agent 工程，建议直接进入 **#08 → #09 → #10 → #13 → #15**。

如果你更关心 Agent Reliability，可以重点关注：

**Harness → Trace → Verification → Failure → Regression → Quality Gate**
