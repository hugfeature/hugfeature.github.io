---
layout: page
title: AI Eval：从大模型评测到 Agent Reliability
description: AI Eval 系统教程：从大模型 Benchmark、业务 Eval、Dataset、LLM-as-a-Judge 和指标体系，进入 Agent Eval、Trace Grading、Failure Corpus、Regression 与 Quality Gate。
eyebrow: SERIES / 02
permalink: /eval/
---

{% assign entries = site.posts | where: 'series', 'ai-eval' | sort: 'series_order' %}
{% assign latest = entries | sort: 'date' | last %}

这是一个围绕 **Model Eval / Business Eval / Agent Eval / AI Reliability** 的完整系列。

核心不是追一个“最高分”，而是逐步回答三个工程问题：

1. **怎么证明一个模型在我的任务上更好；**
2. **怎么证明一个 Agent 真的完成了任务，而且过程没有失控；**
3. **怎么把真实失败沉淀成持续回归，并最终进入发布门禁。**

当前 **{{ entries.size }} 篇** · 最近更新 {{ latest.date | date: '%Y.%m.%d' }}

## 快速入口

- **[大模型评测到底在评什么？](/eval/what-is-model-evaluation/)** — Benchmark、Model Eval、Business Eval、Grader 和持续回归。
- **[排行榜第一，为什么到了你的业务里可能不好用？](/eval/why-leaderboard-is-not-enough/)** — 为什么模型选型最终必须回到真实任务分布。
- **[怎样构造业务 Eval Dataset？](/eval/how-to-build-business-eval-dataset/)** — 从真实任务、高风险场景和历史失败建立数据集。
- **[LLM-as-a-Judge 怎么做才靠谱？](/eval/llm-as-a-judge/)** — Rubric、Pairwise、偏差控制和 Human Gold 校准。
- **[Agent Trace Grading 怎么设计？](/eval/agent-trace-grading/)** — 检查 Tool、State、Constraint、Side Effect 与 Evidence。
- **[怎么把 AI Eval 接进 CI / Quality Gate？](/eval/eval-ci-quality-gate/)** — 让 Eval 从报告变成 Merge / Release 判据。

## 第一部分：先把模型评测搞明白

### #01 [大模型评测到底在评什么？Benchmark、Eval、业务评测一次讲清](/eval/what-is-model-evaluation/)

建立 Dataset、Runner、Grader、Metrics 和 Failure Cases 的基本框架。

### #02 [排行榜第一，为什么到了你的业务里可能不好用？](/eval/why-leaderboard-is-not-enough/)

公开 Benchmark 用于理解通用能力，真实模型选型仍然需要自己的业务 Eval。

### #03 [Model Eval 和 Agent Eval 有什么区别？从单次输出到完整执行轨迹](/eval/model-eval-vs-agent-eval/)

评测对象从单次输出扩展到 Tool、State、Trace、Side Effect 和 Evidence。

## 第二部分：把业务 Eval 做实

### #04 [怎样构造一套真正有用的业务 Eval Dataset？](/eval/how-to-build-business-eval-dataset/)

Dataset 不应该只是随机样本集合，而应该覆盖真实任务、高风险 Case、历史失败与边界条件。

### #05 [LLM-as-a-Judge 怎么做才靠谱？从 Rubric、偏差到人工校准](/eval/llm-as-a-judge/)

Judge 自己也必须有 Rubric、Human Gold、偏差控制和 Regression。

### #06 [Eval 指标怎么设计？为什么 Pass Rate 远远不够](/eval/eval-metrics-beyond-pass-rate/)

从总体通过率进一步拆到 pass@k、pass^k、Critical Failure、False Pass、Evidence、Latency 与 Cost。

### #07 [Offline Eval 和 Online Eval 有什么区别？一套 AI 系统为什么两个都需要](/eval/offline-vs-online-eval/)

Offline 负责发布前的可重复验证，Online 负责在真实分布里发现新失败。

## 第三部分：从 Eval 进入 Agent Reliability

### #08 [线上失败怎么变成 Failure Corpus？从一次事故到持续回归](/eval/build-failure-corpus/)

把线上真实失败变成可复现、可归因、可检索、可回归的质量资产。

### #09 [Agent Trace Grading 怎么设计？结果正确，过程也可能已经失控](/eval/agent-trace-grading/)

不只判断最终结果，还验证 Tool、State、约束、副作用、Recovery 与 Evidence。

### #10 [怎么把 AI Eval 接进 CI / Quality Gate？让评测真正阻断坏版本](/eval/eval-ci-quality-gate/)

建立 Baseline、Hard Gate、Regression、Flaky Policy 与机器可读 Artifact，把 Eval 接进真实交付流程。

## 两条主线怎么衔接

如果把整个网站的内容压缩成一条链：

**Harness 产生可信执行事实，Eval 判断质量，Failure Corpus 保存失败记忆，Regression 防止问题回来，Quality Gate 决定能不能交付。**

如果你想继续往执行层走：

**[Agent Harness 系列](/harness/)**。
