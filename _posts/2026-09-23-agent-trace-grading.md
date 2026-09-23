---
layout: post
title: "Agent Trace Grading 怎么设计？结果正确，过程也可能已经失控"
date: 2026-09-23 10:30:00 +0800
categories: [AI-Eval, Agent-Eval, Trace-Evidence]
permalink: /eval/agent-trace-grading/
description: "Agent Eval 不能只看最终答案。本文讲清如何用 Trace Grading 检查 Tool、State、Constraint、Side Effect、Evidence 与 Recovery，同时避免把评测写成僵硬的路径匹配。"
tags: ["agent-eval", "trace-grading", "trace-evidence", "tool-calling", "agent-reliability"]
series: ai-eval
series_order: 9
---

> **AI Eval 系列 #09**  
> 上一篇：[线上失败怎么变成 Failure Corpus？](/eval/build-failure-corpus/)

传统模型评测很容易把任务简化成：

    Input
      ↓
    Output
      ↓
    Grader

但 Agent 真正执行任务时，中间可能经历几十个 Step：

    Goal
      ↓
    Context
      ↓
    Model Decision
      ↓
    Tool Call
      ↓
    Tool Result
      ↓
    State Update
      ↓
    Retry / Recovery
      ↓
    Final Result

如果只检查 Final Result，就会漏掉一种越来越重要的失败：

**结果是对的，但过程已经失控。**

这正是 Trace Grading 要解决的问题。

## 一、什么是 Trace Grading

Trace 是一次 Agent 运行的完整轨迹。

通常至少包括：

- Model Calls；
- Tool Calls；
- Tool Results；
- Handoff；
- Guardrail；
- State Change；
- Retry；
- Error；
- Final Output。

OpenAI 当前的 Agent Eval 文档把 Trace Grading 放在工作流评测的核心位置：先记录端到端执行，再使用 Grader 对 Tool 选择、Handoff、指令违反和 Workflow 行为进行结构化判断。

简单说：

**Result Grading 判断“做成没有”，Trace Grading 判断“怎么做成的”。**

## 二、为什么 Final Result 不够

假设任务是：

**修改测试环境配置，并验证服务正常。**

最终结果看起来完全正确。

但 Trace 可能是：

    Step 1 修改测试环境
    Step 2 配置错误
    Step 3 服务启动失败
    Step 4 Agent 未验证状态
    Step 5 误修改生产环境
    Step 6 发现异常
    Step 7 回滚生产
    Step 8 修复测试环境
    Step 9 输出“任务完成”

最终测试环境是正确的。

如果只看最终状态：

    PASS

但整个过程至少发生了一次严重 Side Effect Violation。

所以：

**End State Correct 不等于 Execution Safe。**

## 三、Trace Grading 最值得检查什么

我更推荐先从五类信号开始。

### 1. Tool Correctness

检查：

- 是否选择正确工具；
- 参数是否正确；
- 是否调用不必要工具；
- 是否调用禁止工具。

例如：

    expected_tool = query_order
    actual_tool = delete_order

即使后面没有真正执行删除，也已经是重要风险信号。

### 2. Constraint Compliance

检查过程中有没有违反明确约束：

- 必须审批；
- 禁止访问生产；
- 不允许删除；
- 只能修改指定目录；
- 不允许绕过测试。

这类规则适合做 Hard Assertion。

### 3. State Verification

Agent 执行一个动作之后，是否验证真实状态。

例如：

    Tool Result:
    deploy requested

不能直接推导出：

    deploy succeeded

需要独立检查健康状态、版本或环境。

缺少这一步，很容易出现 State Desync。

### 4. Side Effect

Agent 是否造成了任务目标之外的修改。

例如 Coding Agent：

- 修改无关文件；
- 删除测试；
- 改配置绕过失败；
- 提交凭据。

Computer Use Agent：

- 多创建订单；
- 修改错误客户；
- 发送重复消息。

这些通常不能只靠 Final Output 发现。

### 5. Evidence

Agent 最终的成功声明是否绑定可独立检查的证据。

例如：

    claim:
    tests passed

    evidence:
    pytest exit_code = 0
    report = artifacts/test-report.xml

如果只有 claim，没有 evidence，更合理的状态可能是：

    UNVERIFIED

而不是 PASS。

## 四、不要把 Trace Grading 写成固定路径匹配

这是一个很容易踩的坑。

例如定义：

    正确路径必须是：
    search
    → open
    → edit
    → test

但 Agent 可能找到另一条同样合法甚至更短的路径：

    open
    → edit
    → test

如果 Eval 强行要求固定 Tool Sequence，就会把合理行为判错。

Anthropic 的 Agent Eval 实践也强调：过度检查具体执行路径会让 Eval 变脆，通常应该优先验证结果、约束和关键不变量，而不是要求 Agent 完全照设计者预想的步骤执行。

所以：

**Trace Grading 不等于 Path Matching。**

## 五、更稳定的方法：检查 Invariant

不要写：

    必须先调用 tool_A，再调用 tool_B

更适合写：

    修改前必须读取当前状态
    修改后必须验证新状态
    禁止访问 production
    最终必须存在测试证据

也就是检查：

**必须一直成立的规则。**

这比固定步骤更适合 Agent。

## 六、哪些 Trace Rule 适合确定性判断

优先用程序判断：

    forbidden_tool_called
    retry_count > limit
    production_write == true
    test_exit_code != 0
    evidence_missing
    changed_files outside allowed_paths

这类规则不需要 LLM Judge。

它们应该稳定、快速、可复现。

## 七、哪些适合 LLM Trace Grader

LLM 更适合语义层问题：

- Agent 是否忽略用户关键约束；
- 某次 Handoff 是否合理；
- 重复操作是否属于无效 Loop；
- 是否在证据不足时过早宣布完成；
- Recovery 是否偏离原目标。

但仍然要提供明确 Rubric。

例如：

    FAIL:
    Agent 在未验证真实环境状态前宣布成功。

    PASS:
    Agent 使用独立信号验证目标状态，再给出完成结论。

不要只问：

**“这条 Trace 好不好？”**

## 八、Trace Grading 应该输出 Evidence

一个有用的 Trace Grader 输出不应该只有：

    score = 0.7

更应该是：

    verdict: FAIL
    failure_type: state_desync
    step: 12
    evidence:
      - deployment request returned 202
      - no health verification followed
      - agent declared success at step 13

这样才能进入：

- Failure Triage；
- Root Cause；
- Failure Corpus；
- Regression。

## 九、Result Grading 和 Trace Grading 要同时存在

最终可以形成二维结果：

| Result | Trace | 判断 |
| --- | --- | --- |
| PASS | PASS | VERIFIED |
| PASS | FAIL | PROCESS FAILURE |
| FAIL | PASS | CAPABILITY / TASK FAILURE |
| FAIL | FAIL | SYSTEM FAILURE |

最值得关注的是第二类：

**Result PASS / Trace FAIL。**

这就是“最终看起来成功，但过程已经失控”。

## 十、Trace Grading 最终要服务 Failure 定位

一条 Trace 有几十甚至几百个事件。

如果 Grader 只是告诉你：

    FAIL

价值不够。

最好能够回答：

    失败发生在哪一步？
    属于哪一层？
    哪个 Evidence 支持判断？
    是第一次发生还是已知 Failure？
    能不能转成 Regression？

这时 Trace 就从 Observability 数据，变成了 Eval 数据。

## 十一、Trace 是 Agent Reliability 的连接层

它连接了：

    Execution
       ↓
    Evidence
       ↓
    Eval
       ↓
    Failure
       ↓
    Regression
       ↓
    Gate

没有 Trace，很多 Agent Failure 只能看到结果。

有了 Trace Grading，系统才开始有能力判断：

**为什么成功，为什么失败，以及这个成功到底可信不可信。**

下一篇是本系列最后一篇：

**怎么把 Eval 真正接进 CI / Quality Gate，而不是停在一张 Dashboard 上。**

## 参考资料

- [OpenAI — Evaluate agent workflows](https://developers.openai.com/api/docs/guides/agent-evals)
- [Anthropic — Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
