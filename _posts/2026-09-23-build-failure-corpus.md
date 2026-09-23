---
layout: post
title: "线上失败怎么变成 Failure Corpus？从一次事故到持续回归"
date: 2026-09-23 10:20:00 +0800
categories: [AI-Eval, Agent-Reliability]
permalink: /eval/build-failure-corpus/
description: "Failure Corpus 不是错误日志堆积，而是把真实失败结构化成可复现、可归因、可回归的质量资产。本文给出 Failure → Root Cause → Regression Case 的完整闭环。"
tags: ["failure-corpus", "ai-eval", "regression", "agent-reliability", "root-cause"]
series: ai-eval
series_order: 8
---

> **AI Eval 系列 #08**  
> 上一篇：[Offline Eval 和 Online Eval 有什么区别？](/eval/offline-vs-online-eval/)

很多 AI 系统上线之后，失败其实不少。

但几个月后回头看，会发现真正留下来的只有日志、截图、一张 Bug 单，或者一句“这个问题之前好像修过”。

这不叫质量资产。

真正有价值的做法是把失败沉淀成 **Failure Corpus**：一套可以被检索、复现、归因、重放和持续回归的真实失败集合。

## 一、Failure Corpus 和 Bug List 不一样

Bug List 更关注：发生了什么问题、谁来修、现在状态是什么。

Failure Corpus 更关注：

- 在什么输入和环境下失败；
- 系统实际执行了什么；
- 失败属于哪一类；
- 应该怎样独立验证；
- 修复后如何保证不再出现。

所以它的最终目的不是“记录问题”，而是：

**让同类失败以后可以自动被挡住。**

## 二、一条 Failure 至少要保留什么

最小结构可以包含：

    failure_id: F-2026-017
    task_type: test-case-generation
    severity: high

    input:
      prd: ...

    environment:
      model: ...
      prompt_version: ...
      harness_version: ...

    actual:
      output: ...
      trace_id: ...

    expected:
      must_cover:
        - approval_threshold

    failure:
      type: missing_constraint
      evidence: ...

    root_cause:
      layer: context

    regression:
      case_id: REG-017

这里最关键的是三件事：**输入、证据、失败类型。**

没有这三件，后面很难复现。

## 三、第一步不是分类，而是保证可复现

线上失败发生以后，先问：

**同样的输入还能不能重现？**

如果模型具有随机性，就多跑几次。

例如 5 次执行里 3 次失败，这已经告诉你：这是概率性失败，而不是一次偶然截图。

同时要记录 Model Version、Prompt Version、Tool Version、Context、Business Rule Version、Harness Version 和环境状态。

否则修复前后无法公平比较。

## 四、第二步：区分 Symptom 和 Root Cause

例如症状是：

**生成的测试用例遗漏审批阈值。**

但根因可能是：

- PRD 没被完整加载；
- Context 被截断；
- 模型理解失败；
- Prompt 没要求覆盖；
- Judge 没发现遗漏。

如果只把 Failure Type 写成 missing test case，价值有限。

更好的方式是至少区分层级：

    Input
    Context
    Model Decision
    Tool
    State
    Harness
    Grader
    Environment

这样后面才能知道应该修哪一层。

## 五、Failure Taxonomy 不要一开始设计得太复杂

第一版建议从 5～10 类开始，例如：

    instruction_violation
    missing_constraint
    wrong_tool
    wrong_argument
    state_desync
    unsupported_claim
    side_effect_violation
    loop_or_retry
    missing_evidence
    grader_error

遇到新失败再扩。

分类体系应该来自真实失败，而不是先设计一个看起来完整的分类树。

## 六、第三步：把 Failure 变成 Regression Case

不是所有线上失败都值得进入回归集。

我会优先收：

- Critical / High Severity；
- 重复出现；
- 用户真实投诉；
- 已经修复；
- 代表一种新的 Failure Mode；
- 很容易再次发生。

Regression Case 必须重新定义成功条件。

例如原始失败是：

**Agent 忘记审批阈值。**

Regression 不应该只是保存旧输出，而应该定义：

    must_include:
      - approval_threshold

    critical_error:
      - approve_without_threshold_check

这样未来模型即使换一种表达方式，也能正确判断。

## 七、第四步：绑定 Fix 和 Evidence

每条 Regression Case 最好知道它为什么存在。

例如：

    introduced_by: F-2026-017
    fixed_by: commit-abc
    root_cause: context-truncation
    verification:
      - context_contains_rule
      - output_covers_rule

以后如果它再次失败，就能快速判断：老问题回来了，还是新原因导致同样症状。

## 八、不要只保存失败输出，要保存 Trace

对于 Agent，Final Answer 往往不是根因所在。

例如最终表现只是“任务失败”，但 Trace 可能显示：

    Step 3 Tool Timeout
    Step 4 自动 Retry
    Step 5 切换到错误环境
    Step 6 State 未重新验证

真正的问题其实是 Recovery Policy。

所以 Failure Corpus 对 Agent 来说应该尽量保存 Goal、Context、Trace、Tool Calls、State Changes、Artifacts、Final Result 和 Evidence。

## 九、Failure Corpus 应该支持两个方向的检索

第一类是按业务检索，例如采购、审批、库存、权限，回答：

**这个业务过去发生过哪些 AI 失败？**

第二类是按 Failure Mode 检索，例如 state_desync、wrong_tool、missing_evidence，回答：

**这个技术失败模式在哪些业务里出现过？**

第二种对 Reliability 尤其重要，因为同一种 Runtime Failure 可能跨多个业务重复出现。

## 十、Corpus 不是越大越好

如果 Corpus 里有 5000 条重复低价值失败，会变得越来越难维护。

例如 20 个 Case 都是“长上下文下遗漏早期约束”，可以保留少量代表 Case、若干业务变体和一个统一 Failure Type。

重点是：

**覆盖 Failure Mode，而不是堆数量。**

## 十一、什么时候 Failure 才算真正关闭

传统 Bug 常见的是：

    代码修了
    → close

AI Reliability 更合理的关闭条件应该是：

    Failure reproduced
    +
    Root cause identified
    +
    Fix implemented
    +
    Independent verification passed
    +
    Regression case added
    +
    Gate includes regression

也就是：

**没有 Regression，就不算真正修完。**

## 十二、Failure Corpus 最终会成为系统的“免疫记忆”

它会逐渐回答：

- 我们以前在哪些地方失败过；
- 为什么失败；
- 怎么验证已经修复；
- 下一次改动会不会再次触发。

当它和 Eval、Trace、Quality Gate 串起来之后：

    Failure
    ↓
    Evidence
    ↓
    Root Cause
    ↓
    Regression
    ↓
    Gate

真实事故才真正变成了系统能力。

下一篇继续进入 Agent 场景：

**Trace 到底应该怎么 Grade，才能发现“结果对了但过程错了”？**

## 参考资料

- [Anthropic — Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [OpenAI — Evaluate agent workflows](https://developers.openai.com/api/docs/guides/agent-evals)
