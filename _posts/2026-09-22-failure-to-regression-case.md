---
layout: post
title: "一次 Agent 失败，怎么变成一条 Regression Case？"
date: 2026-09-22 17:44:00 +0800
categories: [Agent-Harness, Agent-Reliability]
permalink: /harness/failure-to-regression-case/
description: "把一次真实 Agent 事故沉淀成可复现、可判断、可长期执行的 Regression Case，形成 Failure Corpus。"
tags: ["agent-harness", "failure-regression", "eval", "agent-reliability"]
series: agent-harness
series_order: 13
---

> **Agent Harness 系列 #13**  
> 上一篇：[给 Agent 设计 Evidence Contract](/harness/agent-evidence-contract/)

一次 Agent 失败，如果最后只是：

> 修好了。

那它很快会被忘掉。

真正有价值的 Reliability 工作，是把它变成：

```text
Real Failure
→ Reproduction
→ Root Cause
→ Regression Case
→ Failure Corpus
```

这样下一次换模型、改 Prompt、升级 Harness 时，系统可以自动回答：

> 这个问题回来了吗？

## 一、先保存原始失败

第一步不是立刻“抽象”。

先保存原始事实：

```text
run_id
goal
input
environment
model
prompt_version
toolset
trace
artifacts
final_result
failure_symptom
```

原始 Failure 永远不要被后续总结替代。

因为 Root Cause 可能会重新判断。

## 二、区分 Symptom 和 Root Cause

例如：

```text
Symptom:
最终页面提交失败

Root Cause:
Agent 在 Step 7 使用了过期页面状态，
导致后续 locator 全部基于旧 DOM。
```

Regression 不应该只检查“页面最后有没有成功”。

它最好能锁定真正导致失败的机制。

## 三、做最小可复现

真实生产 Trace 往往很大。

需要把它缩成：

```text
Minimal Reproduction
```

删除无关步骤，只保留触发失败所需条件。

目标是：

- 稳定复现；
- 成本低；
- 运行快；
- 失败原因明确。

如果一个 Case 每次执行 40 分钟，就很难进日常回归。

## 四、定义 Oracle

Regression Case 必须知道：

**什么算通过。**

例如：

```yaml
case_id: F-0042
trigger: stale_context

expected:
  - agent_detects_state_change
  - no_write_before_refresh
  - final_status: verified
```

Oracle 可以是：

- deterministic assert；
- artifact check；
- state diff；
- trace pattern；
- 独立 evaluator。

优先确定性判断。

## 五、保存 Failure Signature

为了做聚类和去重，可以给失败提取结构化 Signature：

```text
failure_type
first_error_step
tool
state_before
state_after
side_effect
recovery_attempted
recovery_success
```

以后新的线上失败，可以先和已有 Failure Corpus 匹配。

## 六、Regression Case 不是一次性 Fixture

一个 Case 需要生命周期：

```text
NEW
↓
CONFIRMED
↓
REGRESSION_READY
↓
ACTIVE
↓
DEPRECATED
```

同时记录：

- 来源；
- Owner；
- 首次发现版本；
- 修复版本；
- 最近执行；
- 是否仍有价值。

## 七、什么时候应该进入 Gate

不是所有 Failure 都值得阻断发布。

可以按风险分层：

### P0

安全、数据破坏、越权。

必须 Gate。

### P1

核心任务错误、结果伪成功。

通常 Gate。

### P2

效率退化、重复 Retry、可恢复失败。

可以先做趋势监控。

### P3

低影响行为偏差。

保留 Corpus，不一定阻断。

关键是：

**Failure Corpus 和 Quality Gate 不必一一对应。**

## 八、一个 Regression Case 模板

```yaml
id: F-0042
title: stale context after environment change

source:
  run_id: r-9182

trigger:
  state_changed_after_step: 5

input:
  fixture: fixture_42.json

expected:
  first_required_action: refresh_state
  forbidden_actions:
    - write_before_refresh

oracle:
  type: deterministic

risk:
  severity: P1

gate:
  blocking: true
```

这种 Case 比一段事故总结更有长期价值。

## 九、Failure Corpus 的真正价值

有了几十、几百条真实 Failure 以后，你才能开始回答：

- 新模型真的更可靠吗？
- Prompt 改动修了哪个问题，又引入了什么？
- Harness 新策略有没有降低 Retry Density？
- 某类 Failure 是否持续回归？
- 哪些问题应该上升为 Gate？

这时 Eval 才开始和真实工程风险连接。

## 结语

一次失败的价值，不在于这次修得多快。

而在于：

**它以后还能不能再次伤到系统。**

所以最重要的闭环不是：

```text
Failure → Fix
```

而是：

```text
Failure → Reproduce → Fix → Regression
```

下一篇：[Harness 和 Eval 平台到底是什么关系？](/harness/harness-vs-eval-platform/)
