---
layout: post
title: "Agent 会跳步骤：从测试用例生成失败到 Execution Contract Drift"
date: 2026-09-24 18:40:00 +0800
categories: [Agent-Reliability, Agent-Harness]
permalink: /reliability/execution-contract-drift/
description: "从一次测试用例生成 Agent 的重构出发，讨论为什么 Prompt 无法保证执行流程，以及如何用 Execution Contract、Validator、Trace 和 Drift 检测把 Agent 的过程可靠性变成可验证问题。"
tags: ["agent-reliability", "agent-harness", "trace-evidence", "failure-regression", "quality-gate"]
updated: 2026-09-24 21:13:00 +0800
last_modified_at: 2026-09-24 21:13:00 +0800
---

最近在重构一个测试用例生成 Agent 时，我遇到一个很典型的问题：

**流程已经写得很清楚，Agent 还是会跳步骤。**

一开始我把它当成测试用例生成质量问题：生成得太浅、覆盖不完整、步骤描述不够直接。

继续往下拆以后才发现，真正的问题不在最后那份测试用例，而在前面的执行过程。

本文来自一次真实工程重构，但已经抽象掉具体业务、公司、工具和项目细节。留下来的，是一个更通用的问题：

**当 Agent 的最终结果看起来“差不多正确”，但它没有按照预期过程执行时，我们应该怎么判断它是否可靠？**

我的结论是：

> Prompt 可以描述期望，Harness 必须约束执行，Trace 负责记录事实，而 Drift 检测负责判断事实和期望之间发生了什么偏离。

这类问题，我暂时把它称为 **Execution Contract Drift**。

## 一、最开始，我们以为这是“生成质量”问题

一个测试用例生成 Agent，最直观的流程是：

```text
PRD
  ↓
理解需求
  ↓
生成测试用例
```

如果结果不好，很自然会想到继续优化：

- Prompt；
- 测试用例规范；
- Few-shot 示例；
- Skill 规则；
- 输出模板。

这些手段都有效，但它们有一个共同前提：

**Agent 确实执行了我们以为它执行的过程。**

问题就在这里。

测试用例写得浅，有时不是“不会写测试用例”，而是它根本没有完整理解需求。

覆盖不全，也可能不是“覆盖策略不够好”，而是需求里的关键规则根本没有进入它后面的上下文。

于是流程需要前移。

## 二、第一步：把“理解需求”从隐式推理变成显式产物

比起让 Agent 在上下文里“自己理解一下”，更可靠的做法是让它先产出结构化需求模型。

例如：

```text
PRD
  ↓
requirements.json
  ↓
coverage-plan.json
  ↓
test cases
```

这里真正重要的并不是 JSON。

重要的是：**原本藏在模型内部的推理过程，开始留下可以检查的中间状态。**

于是我们第一次可以问：

- 需求是否被完整解析？
- 哪些业务规则进入了测试范围？
- 哪些测试点来自哪些需求？
- 最终用例是否真的覆盖了 coverage plan？

这时测试用例生成就不再是一次黑盒调用，而变成一条可观察的数据链：

```text
Requirement
    ↓
Test Point
    ↓
Test Case
```

如果中间状态错了，就不需要等最终用例出来以后再猜原因。

## 三、第二步：结构化中间产物仍然不够

很快又会遇到另一个问题。

即使你明确要求：

```text
PRD
  ↓
requirements.json
  ↓
coverage-plan.json
  ↓
cases
```

Agent 仍然可能实际执行成：

```text
PRD
  ↓
cases
```

或者：

```text
PRD
  ↓
requirements.json
  ↓
cases
```

它可能“知道”应该先生成 coverage plan，但为了更快完成任务，直接跳过。

也可能生成了一个文件，却没有真正使用。

甚至可能 Validator 已经报告失败，它仍然继续往下执行，并最终告诉你：

> 任务已完成。

这暴露出一个非常重要的边界：

**流程写在 Prompt 里，不等于流程被系统执行了。**

Prompt 本质上是在告诉模型：

> 你应该怎么做。

但可靠性真正需要的是：

> 你不满足条件时，系统不允许你继续做。

这就是 Harness 应该接管的部分。

## 四、把流程升级为 Execution Contract

对于这类任务，我现在更愿意把预期流程看成一份 **Execution Contract**。

这里的 Execution Contract 不是某个特定框架的正式标准，而是一个工程抽象：

**它描述一个 Agent 在完成任务时必须经过哪些状态、产出哪些证据、满足哪些条件，才能进入下一阶段。**

例如：

```text
PRD
  ↓
Requirement Interpreter
  ↓
requirements.json
  ↓
[Gate 1: requirement validator]
  ↓
Coverage Planner
  ↓
coverage-plan.json
  ↓
[Gate 2: coverage validator]
  ↓
Case Generator
  ↓
cases
  ↓
[Gate 3: case validator]
  ↓
Done
```

这条链路里至少有四种东西：

| 类型 | 作用 |
| --- | --- |
| State | 当前执行到了哪里 |
| Artifact | 当前阶段生成了什么 |
| Validator | 产物是否满足约束 |
| Gate | 是否允许进入下一阶段 |

真正关键的是 Gate。

如果 Requirement Validator 没通过：

```text
validator = FAIL
      ↓
不能进入 Coverage Planner
```

而不是：

```text
validator = FAIL
      ↓
Agent：问题不大，我继续生成吧
```

**能用 Harness 强制的规则，不应该只依赖模型记住。**

## 五、这时出现了一类以前很难描述的失败

假设最后生成的测试用例看起来还不错。

传统验证可能会判断：

```text
Final Result = PASS
```

但 Trace 告诉我们，它实际走的是：

```text
PRD
  ↓
requirements.json
  ↓
cases
```

预期轨迹却是：

```text
PRD
  ↓
requirements.json
  ↓
Gate 1
  ↓
coverage-plan.json
  ↓
Gate 2
  ↓
cases
  ↓
Gate 3
```

这时问题已经不只是“结果对不对”。

而是：

```text
Expected Trajectory
        ≠
Actual Trajectory
```

这就是我觉得非常值得关注的一类 Drift。

## 六、Execution Contract Drift 可以有哪些形式

如果把 Contract 和 Trace 放在一起比较，会出现一些很具体的失败模式。

### 1. Stage Skipping

预期：

```text
A → B → C → D
```

实际：

```text
A → B → D
```

Agent 跳过了必需阶段。

### 2. Gate Bypass

Validator 已经失败，但执行仍然继续：

```text
Validator = FAIL
      ↓
Next Stage Executed
```

这类问题尤其危险，因为最终结果可能仍然“看起来正常”。

### 3. Silent State Mutation

前一阶段已经确认的需求，在后续阶段被模型静默改写。

例如：

```text
Requirement v1
      ↓
Coverage Planning
      ↓
Requirement v2
```

但没有任何显式 change event。

### 4. Evidence Gap

Agent 声称某个阶段已经完成，却找不到对应证据：

```text
"coverage analysis completed"
          ↓
coverage-plan.json missing
```

### 5. Recovery Violation

执行失败以后，本来应该：

```text
FAIL → Retry / Stop / Human Review
```

实际却变成：

```text
FAIL → Ignore → Continue
```

### 6. Output-Contract Mismatch

最终产物存在，但无法建立：

```text
Requirement → Test Point → Test Case
```

的追溯关系。

这些失败的共同点是：

**它们未必让最终结果立即失败，但说明执行过程已经失去控制。**

## 七、为什么 Trace 在这里不再只是“日志”

很多系统已经有 Trace。

但如果 Trace 只是方便排查：

> Agent 刚才调用了什么 Tool？

它的价值还没有完全发挥出来。

当系统已经存在 Execution Contract 时，Trace 可以变成真正的验证输入：

```text
Execution Contract
        +
Actual Trace
        ↓
Contract Validator
        ↓
Violation
```

于是 Trace 不只是“发生了什么”的记录，而变成：

**证明 Agent 是否按照可靠执行路径完成任务的 Evidence。**

这时我们甚至可以产生结构化结果：

```json
{
  "expected_stage": "coverage_validation",
  "actual_stage": "case_generation",
  "violation": "gate_bypass",
  "evidence": ["trace_event_12", "trace_event_13"]
}
```

这比一句“Agent 没按 Prompt 执行”有用得多。

因为它可检测、可聚合、可回归。

## 八、这对 Drift 项目意味着什么

我之前做 Drift 时，更关注的是 **Goal Drift**：

Agent 在长时间执行过程中，是否逐渐偏离了最初目标、约束或任务状态。

例如：

- constraint relaxation；
- false environment assumption；
- rabbit hole；
- reasoning loop；
- state desync。

这次测试用例生成场景让我意识到，还有另外一条很具体的方向：

**Execution Contract Drift。**

两者关注的问题不同。

```text
Goal Drift
  ↓
Agent 还在做正确的事情吗？

Execution Contract Drift
  ↓
Agent 还在按照允许的方式做这件事吗？
```

一个 Agent 完全可能：

```text
Goal = 正确
Result = 看起来正确
Execution = 已经违约
```

例如它最终确实生成了一份不错的测试用例，但跳过了必须执行的需求验证和覆盖验证。

从结果视角看，它成功了。

从 Reliability 视角看，这次 Run 应该至少被标记为：

```text
SUCCESS_WITH_CONTRACT_VIOLATION
```

这类样本对 Drift 很有价值。

因为检测对象不再完全依赖模糊的“模型是否跑偏”，而是可以直接比较：

```text
Contract → Trace → Violation
```

## 九、真实系统比人为构造的 Fixture 更重要

这里还有一个我觉得更值得长期做的事情。

不要为了 Drift 专门制造大量漂亮的 Demo。

真正有价值的 Failure Corpus，应该来自真实 Agent 系统里的失败。

例如：

```text
真实任务
  ↓
Harness 执行
  ↓
Trace
  ↓
Contract Violation
  ↓
Root Cause
  ↓
Fix
  ↓
Regression
```

一条真实的 Gate Bypass，就可以沉淀成一个 Regression Fixture。

下一次 Harness、Prompt、Skill 或 Model 发生变化以后，重新跑：

```text
同一 Contract
    +
同一 Failure Fixture
    ↓
是否再次违反？
```

于是一次线上或试点问题，不再只是一个 Bug。

它开始成为可靠性资产。

## 十、最终，我想把这条链路做成什么

现在我更认可这样一条工程链路：

```text
Intent / Requirement
        ↓
Execution Contract
        ↓
Agent
        ↓
Harness
        ↓
Trace
        ↓
Contract Validation
        ↓
Violation / Evidence
        ↓
Failure Corpus
        ↓
Regression
        ↓
Quality Gate
```

这里每一层解决的问题都不一样。

**Prompt 定义行为倾向。**

**Execution Contract 定义必须满足的执行约束。**

**Harness 负责把约束变成真正的运行边界。**

**Trace 记录实际发生的事实。**

**Drift 检测负责发现实际执行和预期执行之间的偏离。**

**Regression 保证同样的失败不要再次回来。**

这也是我最近对 Agent Reliability 越来越明确的一个判断：

> Agent 最危险的情况，不一定是直接失败，而是最终看起来成功，但执行过程已经悄悄脱离了我们以为它遵守的约束。

如果只验最终结果，这类问题很容易被漏掉。

而当 Contract、Trace、Validator 和 Failure Regression 被连起来以后，Agent 的“过程是否可靠”才第一次开始变成一个可以被工程化验证的问题。

---

**相关项目**

- [Drift](https://github.com/hugfeature/drift)：Agent Runtime Observability，关注 Agent 执行过程中的任务偏移、状态异常与可解释 Trace。
- [Agent Harness 是什么？为什么它正在成为 Agent 工程的关键一层](/harness/what-is-agent-harness/)
