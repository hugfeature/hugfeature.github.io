---
layout: post
title: "Offline Eval 和 Online Eval 有什么区别？一套 AI 系统为什么两个都需要"
date: 2026-09-23 10:10:00 +0800
categories: [AI-Eval, Agent-Eval]
permalink: /eval/offline-vs-online-eval/
description: "Offline Eval 负责发布前的可重复比较，Online Eval 负责发现真实生产分布与新失败。本文给出两者的边界、数据闭环与落地方式。"
tags: ["ai-eval", "offline-eval", "online-eval", "production-monitoring", "regression"]
series: ai-eval
series_order: 7
---

> **AI Eval 系列 #07**  
> 上一篇：[Eval 指标怎么设计？为什么 Pass Rate 远远不够](/eval/eval-metrics-beyond-pass-rate/)

很多团队做 Eval 时会走向两个极端。

一种是：

**“我们有离线 Benchmark，所以质量没问题。”**

另一种是：

**“线上有监控，真实用户会告诉我们问题。”**

两种都不够。

更完整的体系应该是：

~~~text
Offline Eval
      ↓
Release
      ↓
Online Observation
      ↓
New Failure
      ↓
Offline Regression
~~~

Offline 和 Online 不是替代关系。

它们解决的是不同问题。

## 一、Offline Eval：发布之前回答“这次改动安全吗”

Offline Eval 的特点是：

- 固定 Dataset；
- 可重复运行；
- 环境尽量稳定；
- 有明确 Grader；
- 可以对比版本。

典型用途：

~~~text
Model A vs Model B
Prompt v3 vs v4
Tool Schema old vs new
Harness old vs new
~~~

它最适合做回归验证。

因为你希望输入尽量不变，只观察系统改动带来的变化。

## 二、Offline Eval 的核心价值是可比较

例如：

~~~text
Eval Set = 200 cases

v1:
Pass = 81%

v2:
Pass = 87%
~~~

如果环境、数据和 Grader 都稳定，你才有资格说 v2 相对 v1 有改善。

所以 Offline Eval 特别强调：

- 环境隔离；
- Dataset 版本；
- Prompt / Model 版本；
- Trial 配置；
- Grader 版本。

否则每次跑出来的差异里，会混入大量基础设施噪声。

## 三、但 Offline 永远覆盖不了真实世界

再好的 Dataset，也只是：

**你已经知道要测什么。**

真实用户会不断带来：

- 新表达方式；
- 新业务组合；
- 新异常数据；
- 新攻击方式；
- 新长尾流程；
- 新环境状态。

因此上线之后还需要 Online。

## 四、Online Eval 更接近“生产质量观测”

Online Eval 不一定意味着“线上每个请求都让 Judge 再评一次”。

它可以包含很多方式：

~~~text
Production Metrics
User Feedback
Human Review
Shadow Evaluation
LLM Judge Sampling
Rule Violation Detection
Failure Mining
~~~

核心是：

**在真实分布里持续观察系统。**

成熟团队常见的组合也是自动 Eval、生产监控和周期性人工 Review 一起使用。

## 五、Online 最重要的产物不是分数，而是新 Case

假设线上发现：

~~~text
用户：
撤回刚才那个申请，但保留附件。

Agent：
直接删除整条业务单据。
~~~

这个失败不能只留在日志里。

应该变成：

~~~text
Production Failure
      ↓
Root Cause
      ↓
Eval Case
      ↓
Regression Set
~~~

下一版发布前必须重新跑。

这一步连接了 Online 和 Offline。

## 六、可以怎么做 Online Eval

### 1. 规则型监控

适合确定性风险：

- Tool Error；
- Timeout；
- Retry 次数；
- Permission Denied；
- Schema Invalid；
- Forbidden Tool；
- Critical State Change。

这些不需要 LLM。

### 2. 抽样 LLM Judge

从线上流量抽样：

~~~text
1% sessions
↓
Judge
↓
Correctness / Completeness / Risk
~~~

重点不是覆盖所有请求，而是发现趋势和新失败模式。

### 3. Human Sampling

高风险业务可以保留人工抽查，尤其用于校准 Judge、审核 Judge 分歧，以及检查新 Failure Type。

### 4. User Feedback

用户点踩、人工修改、重新执行、客服升级，都是非常强的质量信号。

不要只把它们当产品指标，它们应该进入 Eval 数据管道。

## 七、Shadow Eval 是升级模型时很有用的一层

如果准备从 Model A 切到 Model B，可以：

~~~text
Real Traffic
    ↓
Model A → production result

同一输入
    ↓
Model B → shadow result
~~~

Model B 不产生真实副作用，只记录输出。

然后比较：

- Task Success；
- Judge Preference；
- Tool Plan；
- Latency；
- Cost；
- Critical Failure。

这比只用静态 Benchmark 更接近真实任务分布。

## 八、Online Eval 不适合直接替代发布 Gate

线上数据有几个问题：

- 分布一直变化；
- Ground Truth 不完整；
- 用户反馈有偏；
- 事件存在延迟；
- 很多结果无法立即验证。

所以：

~~~text
Online → discover
Offline → verify
~~~

Online 更适合发现问题，Offline 更适合确认问题已经修复。

## 九、一条完整的数据闭环

成熟一点的系统应该逐渐形成：

~~~text
Production
  ↓
Trace / Feedback / Failure
  ↓
Failure Triage
  ↓
Failure Corpus
  ↓
Offline Eval
  ↓
Fix
  ↓
Regression
  ↓
Quality Gate
  ↓
Release
~~~

这时 Online 和 Offline 才真正连起来。

## 十、不要把 Production Monitoring 和 Eval 分成两个世界

常见问题是：

~~~text
Observability 团队看线上指标
Eval 团队跑离线测试
~~~

两边数据互不流通。

最后：

- 线上真实失败进不了 Eval；
- Eval 里修好的问题也无法确认线上是否消失。

更好的设计应该共享：

~~~text
Run ID
Task Type
Model Version
Prompt Version
Trace
Failure Type
Eval Case ID
~~~

让一次失败可以从 Production 追到 Regression。

## 十一、最小落地方式

如果系统刚开始，不需要复杂平台。

先做：

~~~text
Offline:
30～100 个真实 Case
每次关键改动自动跑

Online:
记录 Trace
收集用户反馈
每周抽样人工 Review

Bridge:
线上失败 → 新增 Regression Case
~~~

这已经能形成第一版质量闭环。

下一篇继续把这座桥做具体：

**线上失败到底怎么沉淀成 Failure Corpus？**

## 参考资料

- [Anthropic — Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [OpenAI — Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)
