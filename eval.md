---
layout: page
title: AI Eval：从模型评测到 Agent Reliability
description: AI Eval 系列：从大模型 Benchmark、模型评测、业务 Eval 和 LLM-as-a-Judge，一路进入 Agent Eval、Trace、Failure Corpus、Regression 与 Quality Gate。
eyebrow: SERIES / 02
permalink: /eval/
---

{% assign entries = site.posts | where: 'series', 'ai-eval' | sort: 'series_order' %}
{% assign latest = entries | sort: 'date' | last %}

这是一个围绕 **Model Eval / Business Eval / Agent Eval / AI Reliability** 的系列。

我更关心的不是“哪个模型排行榜第一”，而是三个更工程化的问题：

1. **怎么证明一个模型在我的任务上更好；**
2. **怎么证明一个 Agent 真的完成了任务；**
3. **怎么把真实失败沉淀成持续回归和发布门禁。**

当前 **{{ entries.size }} 篇** · 最近更新 {{ latest.date | date: '%Y.%m.%d' }}

## 快速入口

- **[大模型评测到底在评什么？](/eval/what-is-model-evaluation/)** — 拆开 Benchmark、Model Eval、Business Eval、Grader 和持续回归。
- **[排行榜第一，为什么到了你的业务里可能不好用？](/eval/why-leaderboard-is-not-enough/)** — 从任务分布、成本、延迟、Tool 和 Failure Set 解释模型选型。
- **[怎样构造一套真正有用的业务 Eval Dataset？](/eval/how-to-build-business-eval-dataset/)** — 从真实任务、高风险场景和历史失败建立可持续扩展的数据集。
- **[LLM-as-a-Judge 怎么做才靠谱？](/eval/llm-as-a-judge/)** — Rubric、Pairwise、偏差控制、人工 Gold 和 Judge Regression。
- **[Model Eval 和 Agent Eval 有什么区别？](/eval/model-eval-vs-agent-eval/)** — 从单次输出评测扩展到 Trace、State、Side Effect 和 Evidence。

## 第一部分：模型评测

### #01 [大模型评测到底在评什么？Benchmark、Eval、业务评测一次讲清](/eval/what-is-model-evaluation/)

先建立 Eval 的基本框架：Dataset、Runner、Grader、Metrics 和 Failure Cases。

### #02 [排行榜第一，为什么到了你的业务里可能不好用？](/eval/why-leaderboard-is-not-enough/)

公开 Benchmark 用于理解通用能力，真实模型选型仍然需要自己的业务 Eval。

## 第二部分：把业务 Eval 做实

### #03 [Model Eval 和 Agent Eval 有什么区别？从单次输出到完整执行轨迹](/eval/model-eval-vs-agent-eval/)

Agent 不只生成内容，还会调用工具、修改状态和产生副作用，因此 Eval 必须开始检查 Trace、Evidence 与执行过程。

### #04 [怎样构造一套真正有用的业务 Eval Dataset？](/eval/how-to-build-business-eval-dataset/)

Dataset 不是随机样本集合，而应该覆盖真实任务、高风险 Case、历史失败与边界条件，并逐步沉淀为 Failure Corpus。

### #05 [LLM-as-a-Judge 怎么做才靠谱？从 Rubric、偏差到人工校准](/eval/llm-as-a-judge/)

开放任务可以引入 LLM Judge，但 Judge 自己也必须有 Rubric、Human Gold、偏差控制和 Regression。

## 下一阶段

接下来继续补：

- Eval 指标应该怎么设计，为什么 Pass Rate 不够；
- Offline Eval 与 Online Eval 怎么分工；
- 线上失败如何进入 Failure Corpus；
- Agent Trace Grading 怎么设计；
- Eval 如何进入 CI / Quality Gate。

如果你更关注 Agent 的执行控制层，可以继续看：

**[Agent Harness 系列](/harness/)**。
