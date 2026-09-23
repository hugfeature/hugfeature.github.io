---
layout: post
title: "排行榜第一，为什么到了你的业务里可能不好用？"
date: 2026-09-23 08:50:00 +0800
categories: [AI-Eval, Model-Evaluation]
permalink: /eval/why-leaderboard-is-not-enough/
description: "模型排行榜能帮助理解通用能力，但不能替代业务评测。本文从任务分布、Harness、Prompt、Tool、Latency、Cost 和 Failure Set 解释为什么生产选型必须自己做 Eval。"
tags: ["ai-eval", "llm-benchmark", "model-selection", "business-eval", "llm-as-a-judge"]
series: ai-eval
series_order: 2
---

> **AI Eval 系列 #02**  
> 上一篇：[大模型评测到底在评什么？](/eval/what-is-model-evaluation/)

每次新模型发布，大家最先看的往往是排行榜。

数学多少分、代码多少分、推理多少分、Arena 排名第几。

这些数据当然有价值。

但如果你的问题是：

**“我要不要把生产系统切到这个模型？”**

公开排行榜只能提供部分证据。

它无法替你完成最终判断。

## 一、排行榜回答的是“标准题表现”

公开 Benchmark 最大的价值，是统一比较条件。

相同 Dataset、相近 Prompt、固定指标，让不同模型至少可以在一个共同坐标系中比较。

但生产环境通常不是标准题。

真实业务输入可能包含：

- 不完整需求；
- 脏数据；
- 超长上下文；
- 多轮交互；
- Tool Call；
- RAG；
- 权限限制；
- 特定输出格式；
- 延迟和成本约束。

因此：

~~~text
Benchmark Distribution ≠ Production Distribution
~~~

这就是第一层偏差。

## 二、你真正使用的不是“裸模型”

一个模型上线后，真正工作的通常是：

~~~text
Model
+ System Prompt
+ Context
+ RAG
+ Tools
+ Workflow
+ Harness
+ Retry / Timeout
+ Output Parser
~~~

所以最终效果不是单纯由模型决定。

OpenAI 在 2026 年关于第三方评测的文章中也特别强调：随着模型能够使用工具、跨多步执行任务，表现不仅取决于模型，还取决于任务环境和支撑执行的 setup。

这意味着：

同一个模型换一套 Harness，最终成功率都可能变化。

更不要说换模型。

## 三、平均分会掩盖真正重要的失败

假设两个模型：

~~~text
Model A overall pass rate = 92%
Model B overall pass rate = 89%
~~~

看起来 A 更好。

但拆开之后：

| Task | Model A | Model B |
| --- | ---: | ---: |
| 普通问答 | 98% | 94% |
| 信息抽取 | 96% | 95% |
| 高风险审批判断 | 61% | 88% |

如果你的业务最关心第三项，整体平均分已经失去意义。

生产评测更应该关注：

**关键任务上的条件成功率。**

例如：

~~~text
P(success | high-risk-task)
P(success | long-context)
P(success | tool-call)
P(success | ambiguous-input)
~~~

这比一个 overall score 更接近真实决策。

## 四、模型更强，不代表系统更好

生产系统还有几个排行榜通常不会替你解决的问题。

### 延迟

推理能力提高 5%，但 P95 延迟从 3 秒变成 15 秒，对实时业务可能无法接受。

### 成本

模型单次调用成本提高几倍，如果任务量很大，最终系统成本可能完全不同。

### 输出稳定性

某模型平均质量更高，但格式遵循不稳定，会导致 Parser、Workflow 或后续 Tool 经常失败。

### Tool Calling

一个在文本 Benchmark 上很强的模型，不一定在你的工具 Schema 和参数组合下同样稳定。

### 长任务

单轮回答正确，不代表 20 步之后仍然保持目标、状态和约束一致。

所以模型选型最终是一个多目标问题：

~~~text
Quality
+ Reliability
+ Latency
+ Cost
+ Operability
~~~

而不是单目标追分。

## 五、真正有效的选型应该怎么做

我更推荐三层筛选。

### 第一层：公开 Benchmark 做初筛

先看公开评测，排除能力明显不满足的模型。

例如你做 Coding Agent，可以重点关注代码、推理和 Agent 相关 Benchmark。

这一层的目标不是决定谁上线，而是缩小候选范围。

### 第二层：领域 Eval

拿自己的真实任务跑。

例如 ERP 场景可以覆盖：

- PRD 理解；
- 业务规则抽取；
- 测试点生成；
- 用例生成；
- SQL / API 调用；
- 异常路径；
- 权限和审批规则。

### 第三层：Production Shadow Eval

如果条件允许，让新旧模型在相同线上任务上同时运行，但只有旧模型真正影响生产。

比较：

~~~text
Old Model
vs
Candidate Model
~~~

记录真实输入分布下的：

- Success；
- Failure；
- Latency；
- Cost；
- Tool Error；
- Human Override。

最后再做切换。

## 六、不要只保存分数，要保存“输在哪里”

模型对比最有价值的产物不是：

~~~text
A = 87.2
B = 88.6
~~~

而应该是：

~~~text
Case 017
A PASS
B FAIL

Failure:
遗漏了审批条件

Case 042
A FAIL
B PASS

Failure:
A 在长上下文中忽略早期约束
~~~

这些 Case 才是未来真正有价值的资产。

因为下一次模型升级时，可以直接回归这些失败。

最后你的 Eval Set 会逐渐从“测试题”变成：

**业务 Failure Corpus。**

## 七、什么时候可以换模型

我不会设一个“总分高于旧模型就切换”的规则。

更稳妥的是定义升级门槛，例如：

~~~text
Critical Task Pass Rate: 不下降
Overall Success Rate: 提升
Known Failure Regression: 全部通过
P95 Latency: 在预算内
Cost / Task: 在预算内
New Critical Failure: 0
~~~

这就从“排行榜选模型”，变成了一次工程变更验证。

## 八、真正要问的问题

下次再看到一个新模型排名第一，可以先不急着问：

**“这个模型是不是最强？”**

换成：

**“在哪些任务上更强，这些任务是不是我的任务？”**

再进一步：

**“它进入我的 Prompt、Tool、Harness 和真实数据之后，还能不能稳定更好？”**

这才是 Model Eval 真正应该回答的问题。

下一篇继续往 Agent 场景走：

**Model Eval 和 Agent Eval 到底有什么区别？**

## 参考资料

- [OpenAI — Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)
- [OpenAI — A shared playbook for trustworthy third party evaluations](https://openai.com/index/trustworthy-third-party-evaluations-foundations/)
- [Stanford CRFM — HELM](https://crfm.stanford.edu/helm/)
