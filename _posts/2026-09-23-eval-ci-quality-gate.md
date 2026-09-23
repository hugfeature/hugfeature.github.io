---
layout: post
title: "怎么把 AI Eval 接进 CI / Quality Gate？让评测真正阻断坏版本"
date: 2026-09-23 10:40:00 +0800
categories: [AI-Eval, Quality-Gate, Agent-Reliability]
permalink: /eval/eval-ci-quality-gate/
description: "Eval 只有进入 CI / Quality Gate 才真正参与交付。本文给出 Baseline、Hard Gate、Regression、Flaky Case、Artifact、Override 与发布准入的工程化设计。"
tags: ["ai-eval", "quality-gate", "ci", "regression", "agent-reliability"]
series: ai-eval
series_order: 10
---

> **AI Eval 系列 #10**  
> 上一篇：[Agent Trace Grading 怎么设计？](/eval/agent-trace-grading/)

很多团队已经有 Eval。

但它的工作方式是：

    提交代码
      ↓
    上线
      ↓
    某天人工跑一次 Eval
      ↓
    看 Dashboard

这时 Eval 仍然只是一个观察工具。

真正进入工程交付，要再往前一步：

**让 Eval 结果参与 Merge / Release 决策。**

也就是：

**Quality Gate。**

## 一、Eval 和 Gate 的区别

Eval 回答：

**“这个版本表现怎么样？”**

Gate 回答：

**“这个版本允许不允许继续往下走？”**

两者之间差的是：

    Metrics
      ↓
    Policy
      ↓
    Decision

例如：

    Overall Pass Rate = 91%

只是 Metric。

而：

    Failure Regression = 100%
    Critical Failure = 0
    High-risk Pass Rate >= 95%

才开始形成 Policy。

最终：

    PASS → release
    FAIL → block

这才是 Gate。

## 二、不要直接用 Overall Score 做 Gate

假设：

    v1 = 88%
    v2 = 91%

看起来 v2 应该发布。

但进一步看：

    Critical Case:
    v1 PASS
    v2 FAIL

那 3% 的总体提升可能根本不值得。

所以 Gate 最好拆成两层。

### Hard Gate

任何一项失败就阻断：

- Critical Failure > 0；
- Known Failure Regression < 100%；
- Permission Violation > 0；
- Critical Side Effect > 0；
- Required Evidence Missing；
- Judge Critical False Pass 超阈值。

### Soft / Diagnostic Metrics

用于比较和决策：

- Overall Pass Rate；
- Latency；
- Cost；
- Token；
- Tool Calls；
- Retry；
- Challenge Set 表现。

这样就不会让“平均分”掩盖严重问题。

## 三、第一步：建立 Baseline

Gate 不能凭空判断。

必须知道：

**当前版本是什么水平。**

例如：

    baseline:
      core_pass: 91%
      risk_pass: 96%
      regression_pass: 100%
      p95_latency: 8.2s
      cost_per_task: 0.14

每次变更产生 Candidate：

    candidate:
      core_pass: 93%
      risk_pass: 96%
      regression_pass: 98%
      p95_latency: 7.9s
      cost_per_task: 0.13

虽然大多数指标变好，但 Regression Pass 从 100% 变成 98%。

如果这两条都是已知真实失败，就应该直接 Block。

## 四、第二步：定义哪些改动触发哪些 Eval

不是每次提交都跑全量 Agent Eval。

可以分层。

### Fast Gate

每个 PR：

- Schema；
- Deterministic Grader；
- 核心 20～50 Cases；
- Critical Regression；
- 基础 Tool Contract。

目标是快。

### Full Eval

Merge 前或每天：

- Core Set；
- Risk Set；
- Failure Corpus；
- 多 Trial；
- LLM Judge；
- Trace Grading。

### Release Gate

正式发布前：

- 全量 Regression；
- Critical Cases；
- Environment Validation；
- Model / Prompt / Harness 版本锁定；
- 最终 Evidence Artifact。

这样兼顾速度和覆盖。

## 五、第三步：把 Eval 结果做成机器可读 Artifact

不要只有网页 Dashboard。

CI 至少需要一个稳定结果：

    {
      "status": "FAIL",
      "baseline": "eval-2026-09-22",
      "candidate": "commit-abc",
      "critical_failures": 1,
      "regressions": 2,
      "core_pass_rate": 0.93,
      "risk_pass_rate": 0.95
    }

同时保存：

- Eval Run ID；
- Dataset Version；
- Model Version；
- Prompt Version；
- Harness Version；
- Grader Version；
- Failure List；
- Evidence Link。

这样一个 Gate Decision 才可复核。

## 六、第四步：处理非确定性和 Flaky Case

Agent Eval 最大的问题之一是：

**今天 PASS，明天可能 FAIL。**

不能简单地看到一次失败就全部阻断，也不能无限 Retry 到通过。

更合理的是对 Case 定义策略。

例如：

    critical:
      trials: 3
      require: 3/3 pass

    normal:
      trials: 3
      require: >= 2/3 pass

同时记录：

    flaky = true

长期 Flaky 的 Case 要继续查：

- Agent 本身不稳定；
- Grader 不稳定；
- 环境有噪声；
- Case 定义模糊。

不要用 Retry 隐藏问题。

## 七、第五步：Regression 必须有更高优先级

新能力可以慢慢提升。

已经修过的真实失败不应该轻易回来。

所以我会让 Gate 优先级大致变成：

    Critical Safety / Side Effect
        ↓
    Known Failure Regression
        ↓
    High-risk Business Cases
        ↓
    Core Capability
        ↓
    Cost / Latency
        ↓
    Challenge Set

这和普通 Benchmark 排名完全不同。

它体现的是：

**交付风险，而不是模型炫技能力。**

## 八、Human Override 可以有，但必须留下证据

有时业务确实需要带风险发布。

例如：

- Grader 已知误判；
- Case 已过期；
- 线上紧急修复；
- 非关键 Regression 可接受。

可以允许 Override。

但至少记录：

    override_by
    reason
    failed_cases
    risk_acceptance
    expires_at

并且最好要求后续补：

- 修复 Grader；
- 更新 Dataset；
- 新建技术债；
- 重新执行 Eval。

否则 Override 很快会变成绕过 Gate 的常规入口。

## 九、不要让 Gate 只阻断 Model 变更

AI 系统的行为变化可能来自：

- Model；
- Prompt；
- Tool Schema；
- RAG；
- Context Builder；
- Workflow；
- Harness；
- Grader；
- Business Rule。

所以真正应该被 Gate 的是：

**AI System Change。**

而不是只在“换模型”时跑 Eval。

## 十、一个最小 CI 流程

第一版完全可以很简单：

    Pull Request
        ↓
    Build
        ↓
    Unit / Integration Test
        ↓
    AI Eval Fast Set
        ↓
    Regression Set
        ↓
    Gate Policy
        ↓
    PASS / BLOCK

Merge 后：

    Full Eval
        ↓
    Artifact
        ↓
    Release Gate

生产之后：

    Monitoring
        ↓
    New Failure
        ↓
    Failure Corpus

闭环就形成了。

## 十一、Eval 最终要从“报告”变成“判据”

如果 Eval 只告诉团队：

**这个版本是 87 分。**

它仍然离工程交付很远。

真正有价值的是：

    这次改动修复了什么？
    引入了什么 Regression？
    Critical Risk 有没有增加？
    Evidence 是否完整？
    是否满足发布条件？

最终形成：

    Change
      ↓
    Eval
      ↓
    Evidence
      ↓
    Failure / Regression
      ↓
    Gate
      ↓
    Merge / Release

到这里，Eval 才真正成为 AI Engineering Reliability 的一部分。

如果你想继续往执行层走，可以接着看：

- [Harness 到 Quality Gate：Agent Reliability 怎么进入交付准入](/harness/harness-to-quality-gate/)
- [Harness 和 Eval 平台到底是什么关系？](/harness/harness-vs-eval-platform/)
- [Trace 不是日志：Harness 应该记录哪些执行证据？](/harness/trace-is-not-just-logs/)

## 参考资料

- [OpenAI — Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)
- [OpenAI — Evaluate agent workflows](https://developers.openai.com/api/docs/guides/agent-evals)
- [Anthropic — Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
