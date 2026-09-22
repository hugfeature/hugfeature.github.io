---
layout: post
title: "Agent Harness 的终点：从执行引擎走向 Quality Gate"
date: 2026-09-22 17:46:00 +0800
categories: [Agent-Harness, Agent-Reliability]
permalink: /harness/harness-to-quality-gate/
description: "把 Trace、Evidence、Failure Regression、Eval 收束到 Merge / Release Gate，让 Agent 的结果从“能运行”走向“可交付”。"
tags: ["agent-harness", "quality-gate", "failure-regression", "agent-reliability"]
series: agent-harness
series_order: 15
---

> **Agent Harness 系列 #15**  
> 上一篇：[Harness 和 Eval 平台到底是什么关系？](/harness/harness-vs-eval-platform/)

写到这里，Harness 已经不再只是：

```text
Model + Tool Loop
```

它逐渐拥有：

- Policy；
- Trace；
- Evidence；
- Recovery；
- Failure Corpus；
- Regression；
- Eval。

那么最后一个问题是：

> 这些能力最终改变了什么？

如果答案只是：

> Dashboard 更漂亮了。

还不够。

真正的终点应该是：

**它能影响交付。**

## 一、Quality Gate 是什么

Quality Gate 的本质非常简单：

```text
Can this change move forward?
```

例如：

- 能不能 Merge；
- 能不能 Deploy；
- 能不能升级模型；
- 能不能发布新 Prompt；
- 能不能让 Agent 获得更高权限。

Gate 把 Reliability 从“观察”变成“约束”。

## 二、Gate 不应该只看最终 Pass

一个 Agent Run 可能：

```text
Final Result = PASS
```

但同时：

```text
critical evidence missing
high-risk tool unverified
known regression failed
forbidden action attempted
```

这种结果不应该进入下一阶段。

所以 Gate 条件至少要同时看：

```text
Outcome
Evidence
Process Risk
Regression
Policy
```

## 三、一个最小 Gate Contract

例如代码变更：

```yaml
gate: code-agent-merge

required:
  outcome: success
  evidence_complete: true
  tests_passed: true
  critical_regression_passed: true
  unresolved_p1_failure: false
  policy_violation: false

on_fail:
  action: block_merge
```

这里最关键的是：

**Gate 输入全部来自可追溯事实。**

不是让 Agent 最后再回答一句：

> 我认为可以合并。

## 四、Hard Gate 和 Soft Gate

不是所有信号都适合直接阻断。

### Hard Gate

明确不可接受：

- Security violation；
- Data corruption；
- Critical Regression；
- Missing mandatory Evidence；
- Unauthorized Tool；
- Required tests failed。

直接 BLOCK。

### Soft Gate

需要人工判断：

- Retry Density 上升；
- Cost 显著增加；
- Trajectory 变长；
- Judge Score 轻微下降。

可以：

```text
WARN
REVIEW
OBSERVE
```

不要一开始就把所有指标变成硬门禁，否则误报会迅速消耗团队信任。

## 五、Gate 最好至少有四种结果

不要只做 Pass / Fail。

建议：

```text
ALLOW
BLOCK
REVIEW
INCONCLUSIVE
```

### ALLOW

证据充分，规则满足。

### BLOCK

命中明确不可接受条件。

### REVIEW

高风险但需要人工判断。

### INCONCLUSIVE

关键 Evidence 缺失，系统无法确认。

尤其是 INCONCLUSIVE 很重要。

**不知道，不等于通过。**

## 六、Gate 应该放在哪

对于 Coding Agent：

```text
Change
↓
Agent
↓
Harness
↓
Verification
↓
Gate
↓
Merge
```

对于模型 / Prompt 升级：

```text
New Version
↓
Regression Eval
↓
Gate
↓
Rollout
```

对于企业 Workflow：

```text
Agent Result
↓
Evidence
↓
Gate
↓
Approval / Next Step
```

Gate 应该靠近真正的交付边界。

## 七、不要让 Gate 变成另一个 Judge

Gate 本身应该尽量简单。

它消费：

- deterministic checks；
- evaluator results；
- risk signals；
- policy results。

然后执行明确规则。

例如：

```python
if security_violation:
    return BLOCK

if mandatory_evidence_missing:
    return INCONCLUSIVE

if critical_regression_failed:
    return BLOCK

if risk_score > review_threshold:
    return REVIEW

return ALLOW
```

复杂判断应该在前面的 Verification / Eval 层完成。

Gate 负责决策。

## 八、真正完整的闭环

现在把整个系列收回来：

```text
Change
  ↓
Agent
  ↓
Harness
  ↓
Trace
  ↓
Evidence
  ↓
Verification
  ↓
Failure / Root Cause
  ↓
Regression
  ↓
Eval
  ↓
Quality Gate
  ↓
Merge / Release
```

其中：

- Harness 控制执行；
- Trace 保存事实；
- Evidence 证明结果；
- Failure 解释问题；
- Regression 防止复发；
- Eval 比较质量；
- Gate 决定交付。

这就是我理解的 **AI Engineering Reliability** 闭环。

## 九、Harness 为什么会走到这里

因为 Agent 越来越强以后，系统真正缺的不是：

> 再多一个能调用工具的 Agent。

而是：

> **谁来保证它的执行是可接受的。**

所以 Harness 的演化方向很自然：

```text
Agent Runner
↓
Execution Runtime
↓
Reliability Boundary
↓
Delivery Gate
```

这也是为什么我不把 Harness 只看成一个 Agent Framework 概念。

它最终会进入软件交付系统。

## 十、什么时候说明系统真的成熟了

我会看五个问题：

1. 一次 Agent Run 能不能完整重建？
2. 最终结果有没有独立 Evidence？
3. 真实失败能不能自动进入 Regression？
4. 新版本能不能证明没有重新引入旧 Failure？
5. 高风险结果能不能自动阻断 Merge / Release？

如果这五个问题都能回答“可以”，Agent Reliability 才真正从理念变成工程能力。

## 结语

Agent Harness 的终点不是：

**把 Loop 跑得更漂亮。**

而是：

**让 Agent 的执行可以进入真实交付体系。**

从“模型说完成了”，走到：

```text
执行受控
结果可验证
失败可定位
问题可回归
风险可阻断
```

这才是 Harness 真正值得长期建设的原因。

---

## Agent Harness 系列

从基础概念到 Quality Gate，完整目录见：

[Agent Harness：从入门到 Reliability](/harness/)
