---
layout: post
title: "结果正确就够了吗？给 Agent 设计 Evidence Contract"
date: 2026-09-22 17:43:00 +0800
categories: [Agent-Harness, Agent-Reliability]
permalink: /harness/agent-evidence-contract/
description: "把 Agent 的“我完成了”升级为可验证结果：定义 Evidence Contract、独立验证、Artifact 引用和 VERIFIED / UNVERIFIED 状态。"
tags: ["agent-harness", "evidence", "verification", "agent-reliability"]
series: agent-harness
series_order: 12
---

> **Agent Harness 系列 #12**  
> 上一篇：[Agent 调错工具怎么办](/harness/tool-failure-timeout-retry-budget-side-effect/)

Agent 最常见的最终输出是：

> 已完成。

或者：

> 测试全部通过。

问题是：

**谁证明的？**

如果“执行任务的人”和“证明任务完成的人”是同一个 Agent，那么系统实际上只拿到了 self-report。

这也是为什么我认为 Agent Runtime 需要一个明确的 **Evidence Contract**。

## 一、Outcome 和 Evidence 是两回事

Outcome 回答：

> 结果是什么？

Evidence 回答：

> 你凭什么相信这个结果？

例如：

```text
Outcome:
bug fixed

Evidence:
git diff
pytest exit_code = 0
test report
changed files
build id
```

只有 Outcome，没有 Evidence，系统很难做可靠的 Gate。

## 二、Evidence Contract 是什么

可以把它理解成：

**某类任务要被判定为 VERIFIED，必须提供哪些可独立检查的证据。**

例如 Coding Agent：

```yaml
task_type: code_change
required_evidence:
  - changed_files
  - git_diff
  - test_command
  - test_exit_code
  - test_report
```

UI 测试 Agent：

```yaml
task_type: ui_validation
required_evidence:
  - target_url
  - executed_steps
  - screenshots
  - assertion_results
  - final_page_state
```

## 三、Evidence 必须尽量来自独立来源

最弱的 Evidence：

```text
Agent:
"测试通过了"
```

更强：

```text
Agent:
"我执行了 pytest，返回 0"
```

再强：

```text
Harness:
command = pytest
exit_code = 0
artifact = junit.xml
hash = ...
```

原则是：

**越靠近真实执行事实，Evidence 越强。**

## 四、Evidence 应该结构化

不要让最终结果只有一段自然语言。

可以定义：

```json
{
  "outcome": "fixed",
  "evidence": [
    {
      "type": "git_diff",
      "artifact_id": "a-101"
    },
    {
      "type": "test_result",
      "command": "pytest",
      "exit_code": 0,
      "artifact_id": "a-102"
    }
  ]
}
```

这样 Verification 才能程序化。

## 五、Verifier 不应该完全依赖原 Agent

更健康的结构：

```text
Agent
  ↓
Produces Result + Evidence
  ↓
Verifier
  ↓
VERIFIED / UNVERIFIED / FAILED
```

Verifier 可以是：

- deterministic checker；
- test runner；
- schema validator；
- diff checker；
- policy engine；
- 独立模型 Judge。

能程序验证的，优先程序验证。

## 六、Evidence 缺失和任务失败不是一回事

建议至少区分：

```text
SUCCESS_VERIFIED
SUCCESS_UNVERIFIED
FAILED
BLOCKED
INCONCLUSIVE
```

Agent 可能确实做对了，但没提供足够证据。

这时系统不应该硬说“失败”，也不应该当作“可信成功”。

应该是：

**UNVERIFIED。**

这个状态对 Quality Gate 很重要。

## 七、Evidence 也要有生命周期

证据可能过期。

例如：

```text
tests passed
```

只对某个 Commit 有效。

如果代码之后又变了，旧测试结果不能继续支撑新状态。

所以 Evidence 最好绑定：

```text
run_id
commit_sha
environment
timestamp
artifact_hash
tool_version
```

这让 Verification 变成可追溯事实，而不是一句历史结论。

## 八、一个实用的 Evidence Contract 模板

```yaml
task_type: <type>

required:
  - evidence_type_1
  - evidence_type_2

optional:
  - evidence_type_3

freshness:
  max_age: 30m

binding:
  - commit_sha
  - environment

verification:
  deterministic_first: true

on_missing:
  status: UNVERIFIED
```

一开始不用复杂。

先把最关键任务的“可信成功条件”写清楚，就已经非常有价值。

## 九、Evidence Contract 和 Harness 的关系

Harness 负责：

- 捕获执行事实；
- 保存 Artifact；
- 绑定 Run；
- 输出 Evidence；
- 触发 Verification。

Eval 负责：

- 判断不同版本整体表现；
- 聚合指标。

Gate 负责：

- 根据 Verification / Risk 决定能否进入下一阶段。

所以：

```text
Harness → Evidence
Evidence → Verification
Verification → Gate
```

这条链非常关键。

## 结语

Agent Reliability 不能停在：

> Agent 说自己成功了。

真正的工程系统应该问：

> **成功的证据是什么？这个证据能不能被独立验证？**

Evidence Contract 就是把这件事从“经验判断”变成“系统契约”。

下一篇：[一次 Agent 失败，怎么变成一条 Regression Case？](/harness/failure-to-regression-case/)
