---
layout: post
title: "怎样构造一套真正有用的业务 Eval Dataset？"
date: 2026-09-23 09:25:00 +0800
categories: [AI-Eval, Model-Evaluation]
permalink: /eval/how-to-build-business-eval-dataset/
description: "业务 Eval Dataset 不应该只是随机抽样。本文给出从真实任务、失败案例、边界条件到数据分层、Gold Label、Holdout 与持续回归的一套工程化构造方法。"
tags: ["ai-eval", "eval-dataset", "business-eval", "failure-corpus", "regression"]
series: ai-eval
series_order: 4
---

> **AI Eval 系列 #04**  
> 上一篇：[Model Eval 和 Agent Eval 有什么区别？](/eval/model-eval-vs-agent-eval/)

很多团队开始做 Eval 时，第一步就是：

**“先找 100 条数据。”**

问题是，如果这 100 条数据不能代表真实任务，那么后面的模型对比、Prompt 优化和版本回归都会建立在一个错误坐标系上。

所以构造 Eval Dataset，最重要的并不是“数量够不够”，而是：

**这套数据能不能暴露你真正关心的失败。**

## 一、Dataset 不是样本集合，而是风险模型

我更倾向于把业务 Eval Dataset 理解成：

~~~text
真实任务分布
+
高风险场景
+
历史失败
+
边界条件
+
对抗性输入
~~~

OpenAI 的评测最佳实践强调，Eval 应该尽量反映真实生产分布，并持续从日志、用户反馈和历史失败中扩展测试集。

这和传统测试用例设计其实很像。

你不会因为“随机抽了 100 个输入”就认为系统被充分测试。

AI 系统一样。

## 二、先定义 Eval Objective，再收集数据

不要反过来。

错误方式：

~~~text
先收集数据
↓
再看看这些数据能评什么
~~~

更合理的是：

~~~text
Business Goal
↓
Failure Risk
↓
Eval Objective
↓
Dataset
↓
Grader
~~~

例如：

~~~text
业务目标：
从 PRD 自动生成测试用例

主要风险：
遗漏关键业务规则
生成不可执行步骤
重复用例过多
异常路径覆盖不足

Eval Objective：
验证测试点完整性、步骤可执行性和风险覆盖
~~~

这时 Dataset 才有明确方向。

## 三、第一批数据应该从哪里来

我会按下面的优先级收集。

### 1. 真实生产任务

这是最重要的来源。

例如：

- 用户真实问题；
- 历史 PRD；
- 真实工单；
- 真实代码变更；
- 真实测试任务；
- 真实客服对话。

因为这些输入最接近未来系统真正面对的数据。

### 2. 历史失败

这是 Dataset 里最值钱的一类数据。

例如：

~~~text
模型遗漏审批条件
模型把“不得删除”理解成“可以归档”
Agent 在 Tool Call 中传错 ID
长上下文导致早期约束丢失
~~~

每一个真实失败，都可以变成一个 Regression Case。

最终：

~~~text
Production Failure
      ↓
Eval Case
      ↓
Regression
~~~

这会让 Dataset 越跑越贴近真实风险。

### 3. 专家构造的高风险 Case

有些高风险场景在线上出现频率低，但不能不测。

例如 ERP：

- 金额边界；
- 权限越权；
- 审批绕过；
- 跨组织数据；
- 负数库存；
- 重复记账；
- 高风险删除。

这类 Case 需要业务专家主动补。

### 4. Edge Case

例如：

- 空输入；
- 超长输入；
- 格式异常；
- 字段缺失；
- 冲突指令；
- 模糊表达；
- 多语言；
- 特殊字符。

### 5. Synthetic Data

合成数据可以快速扩量。

但不要让 Synthetic 成为主体。

它更适合：

- 补覆盖；
- 生成变体；
- 构造极端 Case；
- 做 Stress Test。

而不是替代真实生产数据。

## 四、Dataset 至少要分四层

如果只把所有 Case 混在一个 JSON 文件里，很快就会失控。

我更推荐：

~~~text
Core Set
Risk Set
Failure Set
Challenge Set
~~~

### Core Set

代表最常见任务。

用途：

**判断整体能力有没有明显变化。**

### Risk Set

高风险但不一定高频。

用途：

**防止关键业务能力退化。**

### Failure Set

来自历史真实失败。

用途：

**保证已经修过的问题不再回来。**

### Challenge Set

极端、复杂、对抗性或长尾任务。

用途：

**探索能力边界。**

不同 Set 不应该用同一个发布门槛。

例如：

~~~text
Core Pass Rate >= 90%
Risk Critical Failure = 0
Failure Regression = 100%
Challenge = observation only
~~~

这比一个总体平均分有意义得多。

## 五、每个 Case 应该保存什么

最小结构可以是：

~~~yaml
id: ERP-017
input: ...
category: approval
risk: critical
source: production
expected:
  must_cover:
    - approval_threshold
    - requester_permission
grader:
  type: rubric
tags:
  - permission
  - approval
~~~

如果是 Agent Eval，还应该增加：

~~~yaml
constraints:
  - do_not_modify_production
  - approval_required

expected_evidence:
  - test_result
  - artifact_path
~~~

核心原则是：

**Case 必须包含可以被独立判断的成功条件。**

否则它只是 Prompt 集合，不是 Eval Dataset。

## 六、Gold Label 不一定是一段“标准答案”

开放任务里，经常不存在唯一正确答案。

所以不要强行给每个 Case 写一段固定输出。

Gold 可以是：

### Exact Gold

适合：

- 分类；
- 数值；
- JSON；
- SQL 结果；
- API 参数。

### Rubric Gold

适合：

- 总结；
- 分析；
- 测试用例；
- 方案设计。

例如：

~~~text
必须覆盖：
- 正常路径
- 权限异常
- 审批阈值
- 重复提交

严重错误：
- 允许越权操作
- 忽略审批规则
~~~

### Executable Gold

适合代码、SQL、Tool 等任务。

不是比较文本，而是执行：

~~~text
Output
↓
Run
↓
Assertion
~~~

这通常比文本相似度可靠得多。

## 七、不要把开发集和评测集混在一起

如果你不断根据 Eval Case 修改 Prompt，然后仍然用同一批 Case 验证，最终很可能只是：

**Prompt 过拟合 Eval Set。**

所以最好至少拆成：

~~~text
Development Set
Holdout Set
Regression Set
~~~

Development Set：日常调试。

Holdout Set：平时不看，用于阶段性验证。

Regression Set：历史失败，必须持续跑。

如果数据量很小，哪怕只保留 20% 做 Holdout，也比完全没有强。

## 八、Dataset 需要版本化

模型变了、Prompt 变了、业务规则也会变。

所以 Eval Dataset 本身也必须版本化。

至少记录：

~~~text
Dataset Version
Case Version
Source
Created At
Label Version
Business Rule Version
~~~

否则半年之后你很难解释：

“为什么这个 Case 当时被判 Fail？”

## 九、从 30 个 Case 开始，比憋 1000 个更好

第一版不用追求规模。

我更推荐：

~~~text
10 个核心任务
10 个高风险任务
10 个真实失败
~~~

先做 30 个。

跑一次。

看看：

- 哪些 Case 根本区分不了模型；
- 哪些 Rubric 太模糊；
- 哪些 Grader 不稳定；
- 哪些失败其实不重要。

然后再扩到：

~~~text
30
↓
100
↓
300
↓
持续增长
~~~

Eval 更适合被当成持续过程：先构造最小可用评测，再随着生产日志和新失败不断扩充。

## 十、一套好的 Dataset 最终会变成 Failure Corpus

开始时，你可能只是想：

**“比较两个模型。”**

但当真实失败不断进入之后，它会逐渐变成：

~~~text
Business Tasks
+
Known Failures
+
Risk Cases
+
Regression Cases
~~~

这时 Dataset 不再只是评测数据。

它开始成为 AI 系统的：

**质量资产。**

下一篇继续解决 Dataset 之后最常见的问题：

**开放任务没有唯一答案时，LLM-as-a-Judge 到底该怎么做，才不会变成“让另一个模型凭感觉打分”？**

## 参考资料

- [OpenAI — Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)
- [OpenAI — Getting started with datasets](https://developers.openai.com/api/docs/guides/evaluation-getting-started)
- [Anthropic — Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
