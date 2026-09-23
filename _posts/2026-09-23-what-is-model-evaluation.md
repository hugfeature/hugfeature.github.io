---
layout: post
title: "大模型评测到底在评什么？Benchmark、Eval、业务评测一次讲清"
date: 2026-09-23 08:40:00 +0800
categories: [AI-Eval, Model-Evaluation]
permalink: /eval/what-is-model-evaluation/
description: "大模型评测不只是跑 Benchmark。本文拆开公开基准、模型能力评测、业务 Eval、自动 Grader 与持续回归，给出一套工程化评测框架。"
tags: ["ai-eval", "model-evaluation", "llm-eval", "benchmark", "llm-as-a-judge"]
series: ai-eval
series_order: 1
---

> **AI Eval 系列 #01**  
> 从模型评测开始，一路进入业务 Eval、Agent Eval、Failure Corpus 和持续回归。

“大模型评测”这个词现在很容易混在一起。

有人说的是 MMLU、GPQA、SWE-bench 这类公开 Benchmark；有人说的是不同模型之间的横向比较；还有一些团队说 Eval，真正想解决的却是：

**这个模型换到我的业务里，到底会不会更好？**

这三件事有关，但不是一回事。

如果只盯着公开排行榜，很容易得到一个看起来精确、实际上无法直接指导生产决策的数字。

## 一、先把三个概念拆开

### 1. Benchmark：统一试卷

Benchmark 更像一套公开试卷。

它的价值是让不同模型在相同数据、相同任务和相近规则下比较，例如知识、数学、代码、推理、长上下文等能力。

它主要回答：

**这个模型在某一类标准任务上的能力大概处于什么水平？**

Benchmark 很重要，因为没有统一试卷，模型之间很难比较。

但 Benchmark 不等于你的生产环境。

### 2. Model Eval：针对模型能力做结构化测试

Model Eval 的范围比 Benchmark 更大。

除了公开 Benchmark，还可以针对某一类能力自己设计评测，例如：

- JSON 格式遵循；
- 信息抽取准确率；
- SQL 生成正确率；
- 长文本摘要完整性；
- Function Call 参数正确率；
- 特定领域知识问答；
- 拒答和安全边界。

OpenAI 把 evals 定义为用于衡量模型表现的结构化测试，并强调评测应该尽量反映真实任务分布，而不是只依赖通用学术指标。

这里的重点不是“跑一个分数”，而是：

**先定义什么叫好，再构造足以区分好坏的测试。**

### 3. Business Eval：回答“对我的业务有没有用”

真正到了工程现场，最终需要的是业务 Eval。

例如你正在做 ERP 测试用例生成，公开 Benchmark 再高，也不能直接回答：

- 是否识别了 PRD 中的关键业务规则；
- 是否遗漏高风险测试点；
- 是否生成重复用例；
- 是否生成不可执行步骤；
- 是否正确引用依赖数据；
- 是否能够稳定输出团队要求的格式。

这时测试集应该来自真实业务任务，而不是只来自公开 Benchmark。

因此我更倾向于把它们理解成：

~~~text
Public Benchmark
      ↓
Model Capability Eval
      ↓
Domain / Business Eval
      ↓
Production Regression
~~~

越往下，越接近真实价值。

## 二、一套 Eval 至少需要五个部分

一个最小的模型评测系统，可以拆成：

~~~text
Dataset
  ↓
Runner
  ↓
Model Output
  ↓
Grader
  ↓
Metrics + Failure Cases
~~~

### Dataset：拿什么考

Dataset 决定了你到底在测什么。

数据可以来自：

- 公开 Benchmark；
- 专家构造；
- 历史业务数据；
- 线上失败；
- 用户反馈；
- 合成数据。

对于业务 Eval，我更看重最后三类。

因为真实失败往往比“想象出来的标准题”更有价值。

### Runner：怎么跑

Runner 负责保证不同模型、不同 Prompt、不同版本在尽可能一致的条件下运行。

至少要控制：

- Prompt；
- Temperature；
- Tool 配置；
- Context；
- Max Token；
- Retry；
- Timeout；
- Model Version。

否则比较的可能不是模型，而是运行条件。

### Grader：怎么判

评测最难的通常不是生成答案，而是定义“什么叫正确”。

常见 Grader 包括：

- Exact Match；
- Rule / Schema Check；
- Unit Test；
- Executable Check；
- Human Review；
- LLM-as-a-Judge；
- Pairwise Comparison。

能用确定性程序判断的，优先不要交给 LLM。

例如 JSON Schema、代码测试、SQL 执行结果、字段完整性，都应该优先使用程序验证。

### Metrics：怎么汇总

平均分通常不够。

至少应该同时看：

- Pass Rate；
- Failure Rate；
- 分任务类型表现；
- P50 / P95 Latency；
- Token / Cost；
- 稳定性；
- 高风险 Case 通过率。

否则一个总体 90 分，可能掩盖了关键任务 50% 的失败率。

### Failure Cases：失败怎么留下来

真正有价值的 Eval，不应该只留下一个分数。

每次失败都应该尽量沉淀成：

~~~text
Input
Expected
Actual
Failure Type
Evidence
Model / Prompt Version
~~~

然后进入下一轮 Regression。

这一步会把“评测”从一次性比赛，变成持续改进机制。

## 三、为什么不能只看平均分

模型质量很少是单维度的。

一个模型可能：

- 推理更强，但慢；
- 指令遵循更好，但成本高；
- 平均分高，但某个关键场景明显退化；
- 文本生成很好，但 Tool Call 经常出错。

Stanford HELM 的核心思路之一，就是把模型评估拆成多个场景和指标，而不是用一个数字描述全部能力。

所以生产环境里更有意义的问题应该是：

**它在哪些任务上更好？在哪些任务上更差？这个差异是否影响我的业务？**

而不是简单问：

“哪个模型分最高？”

## 四、LLM-as-a-Judge 能不能用

能用，而且非常有价值。

但不要把它当绝对真值。

LLM Judge 适合：

- 文本质量；
- 完整性；
- 相关性；
- 风格；
- Pairwise Preference；
- 难以写确定性规则的开放问题。

但它本身也会有偏差，例如位置偏差、长度偏好和 Rubric 理解偏差。

更稳妥的方式是：

~~~text
Human Labels
     ↓ calibration
LLM Judge
     ↓
Large Scale Eval
~~~

先用人工样本校准 Judge，再把它用于大规模自动评测。

## 五、我更推荐的业务评测方法

如果今天要为一个真实 AI 功能建立 Eval，我不会先找几十个 Benchmark。

我会先做四件事：

1. 收集 30～100 个真实任务；
2. 定义每个任务的明确成功条件；
3. 优先使用确定性 Grader；
4. 把线上真实失败持续加入 Eval Set。

最终形成：

~~~text
Real Task
   ↓
Eval
   ↓
Failure
   ↓
Fix
   ↓
Regression
   ↓
Release
~~~

这时 Eval 才真正进入软件工程。

## 六、模型评测的终点不是排行榜

公开 Benchmark 解决的是：

**模型之间怎么比较。**

业务 Eval 解决的是：

**我的系统是否变好了。**

而持续 Regression 最终解决的是：

**一次改动之后，我敢不敢把它发布出去。**

这也是我更关心 AI Eval 的原因。

它最终不应该停留在模型分数，而应该进入：

**Failure → Regression → Quality Gate。**

下一篇继续讨论一个更现实的问题：

**为什么排行榜第一的模型，到了你的业务里未必最好用？**

## 参考资料

- [OpenAI — Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)
- [Stanford CRFM — HELM](https://crfm.stanford.edu/helm/)
- [Anthropic — Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [OpenAI — A shared playbook for trustworthy third party evaluations](https://openai.com/index/trustworthy-third-party-evaluations-foundations/)
