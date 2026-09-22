---
layout: post
title: "Harness 和 Eval 平台到底是什么关系？"
date: 2026-09-22 17:45:00 +0800
categories: [Agent-Harness, AI-Eval]
permalink: /harness/harness-vs-eval-platform/
description: "Harness 负责产生可信执行事实，Eval 负责跨任务和版本判断质量。本文拆开 Runtime、Trace、Evaluator、Regression 和 Gate 的职责。"
tags: ["agent-harness", "ai-eval", "failure-regression", "trace-evidence"]
series: agent-harness
series_order: 14
---

> **Agent Harness 系列 #14**  
> 上一篇：[一次 Agent 失败，怎么变成一条 Regression Case？](/harness/failure-to-regression-case/)

Harness 和 Eval 很容易做成两套互不相干的平台。

一边负责“跑 Agent”。

另一边负责“跑 Benchmark”。

结果是：

**线上真实失败进不了 Eval，Eval 的结论也进不了真实交付。**

我更倾向于把它们看成一条闭环里的两个角色。

## 一、Harness 负责 Execution Truth

Harness 最核心的输出应该是：

```text
这次 Agent 到底做了什么。
```

包括：

- Goal；
- Context；
- Tool Calls；
- Tool Results；
- State Changes；
- Artifacts；
- Retry；
- Failure；
- Evidence；
- Final Status。

这是真实执行事实。

## 二、Eval 负责 Quality Judgment

Eval 更关注：

```text
这些执行结果整体上好不好。
```

例如：

- Task Success；
- Pass Rate；
- Failure Rate；
- Retry Density；
- Evidence Completeness；
- Cost；
- Latency；
- Regression；
- Judge Score。

所以可以简单拆成：

```text
Harness = produce facts
Eval = evaluate facts
```

## 三、Offline Eval 和 Online Eval

### Offline Eval

固定数据集：

```text
Dataset
↓
Agent / Harness
↓
Results
↓
Evaluator
```

适合：

- 模型对比；
- Prompt 版本对比；
- Regression；
- 发布前验证。

### Online Eval

真实生产 Run：

```text
Real Task
↓
Harness
↓
Trace / Evidence
↓
Evaluator
```

适合：

- 线上质量监控；
- 新 Failure 发现；
- Risk Signal；
- Drift。

两者应该共用尽可能一致的 Trace / Evidence Schema。

## 四、Eval 不应该重新猜执行事实

一个常见错误是：

> Harness 什么都没记，Eval 再让一个 LLM 根据最终回答猜过程质量。

这非常脆弱。

更好的结构：

```text
Harness
  ↓
Structured Trace
  ↓
Deterministic Metrics
  ↓
Evaluator / Judge
```

能从事实直接计算的：

- Tool Count；
- Retry Count；
- Forbidden Action；
- Missing Evidence；
- Exit Code；

不要再让 LLM Judge 猜。

## 五、Evaluator 应该分层

一个健康 Eval Stack：

### Level 1：Deterministic

```text
schema check
exit code
artifact exists
policy violation
trace completeness
```

### Level 2：Rule / Heuristic

```text
retry density
trajectory length
repeated action
risk score
```

### Level 3：Model Judge

用于难以程序化的：

- 任务语义正确性；
- 方案质量；
- 开放式输出质量。

顺序最好是：

**程序能判断的，不交给 Judge。**

## 六、Failure Corpus 是 Harness 和 Eval 的桥

线上 Harness 发现一个真实失败：

```text
Production Failure
```

经过整理：

```text
Failure Corpus
```

进入 Offline Eval：

```text
Regression Set
```

新版本上线后：

```text
Production Trace
```

又继续产生新 Failure。

闭环变成：

```text
Harness
↓
Trace
↓
Failure
↓
Corpus
↓
Eval / Regression
↓
Release
↓
Harness
```

这才是真正持续变强的 Reliability System。

## 七、Eval 结果最终应该影响什么

如果 Eval 永远只出一张 Dashboard，它的工程价值有限。

真正关键的是：

```text
Eval Result
↓
Decision
```

例如：

- 是否允许升级模型；
- 是否允许合并 Prompt；
- 是否允许 Skill 新版本上线；
- 是否允许 Agent 进入更高权限；
- 是否允许 Merge / Release。

这时 Eval 才从“评测平台”变成“交付判据”。

## 八、Harness 和 Eval 的接口应该长什么样

至少统一这些字段：

```text
run_id
task_id
agent_version
model_version
prompt_version
harness_version
trace_ref
artifact_refs
evidence
final_status
failure_type
metrics
```

Harness 产出。

Eval 消费。

不要每个团队自己重新解释一次。

## 结语

Harness 和 Eval 不是两个独立方向。

它们之间真正的关系是：

**Harness 负责产生可信事实，Eval 负责把事实变成质量判断。**

再往前一步：

**Quality Gate 把判断变成工程动作。**

下一篇：[Agent Harness 的终点：从执行引擎走向 Quality Gate](/harness/harness-to-quality-gate/)
