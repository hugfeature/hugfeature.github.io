---
layout: page
title: Agent Harness：从入门到 Reliability
description: 从 Agent Harness 的基本概念到执行机制、Trace、Eval、Regression 与 Quality Gate，建立 AI 工程可靠性的知识路径。
eyebrow: SERIES / 01
permalink: /harness/
---


这个专栏会从基础概念、工具和 Demo 写起，再逐步进入 Runtime、Trace、Evidence、Failure Regression 和 Quality Gate。

目标不是只介绍框架，而是回答一个更实际的问题：

> **一个 Agent 做完任务以后，我们凭什么相信它？**

## 已发布文章

{% assign entries = site.posts | where: 'series', 'agent-harness' | sort: 'series_order' %}
{% assign latest = entries | sort: 'last_modified_at' | last %}
当前 **{{ entries.size }} 篇** · 最近更新 {{ latest.last_modified_at | default: latest.date | date: '%Y.%m.%d' }}

{% for entry in entries %}
- [{{ entry.title }}]({{ entry.url | relative_url }})
{% endfor %}

## 系列规划

以下是写作路线；除已发布文章外，其余章节均为规划中。


1. [Agent Harness 是什么？为什么它正在成为 Agent 工程的关键一层](/harness/what-is-agent-harness/) ✅
2. [Agent、Framework、Workflow、Runtime、Harness 到底有什么区别？](/harness/agent-framework-workflow-runtime-harness/) ✅
3. [2026 年 Agent Harness / Runtime 工具有哪些？一张表看懂主流方案](/harness/agent-harness-runtime-tools-2026/) ✅
4. [OpenAI Agents SDK 入门：从安装到第一个可调用工具的 Agent](/harness/openai-agents-sdk-quickstart/) ✅
5. smolagents 入门：几十行代码跑一个 Agent Loop
6. [不用 Agent Framework，自己写一个最小 Harness](/harness/build-minimal-agent-harness/) ✅
7. 一个 Agent Loop 到底是怎么跑起来的？
8. [Agent 为什么需要 Harness：模型负责决策，系统负责约束](/harness/why-agent-needs-harness/) ✅
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


## 按问题探索

<div class="topic-path">{% for topic in site.data.topics %}<a href="{{ '/topics/' | append: topic.slug | append: '/' | relative_url }}">{{ topic.name }} →</a>{% endfor %}</div>
