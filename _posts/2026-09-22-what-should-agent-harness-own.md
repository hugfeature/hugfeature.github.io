---
layout: post
title: "Harness 到底应该管什么？从 Agent Loop 到 Reliability Boundary"
date: 2026-09-22 17:40:00 +0800
categories: [Agent-Harness, Agent-Reliability]
permalink: /harness/what-should-agent-harness-own/
description: "从 Context、Tool、State、Policy、Trace、Recovery 到 Verification，定义 Agent Harness 应该负责什么，以及哪些能力不应该继续塞进 Prompt。"
tags: ["agent-harness", "agent-reliability", "runtime", "architecture"]
series: agent-harness
series_order: 9
---

> **Agent Harness 系列 #09**  
> 上一篇：[Agent 为什么需要 Harness：模型负责决策，系统负责约束](/harness/why-agent-needs-harness/)

前面几篇一直在强调一句话：

**Model proposes. Harness controls execution.**

但真正开始设计 Harness 时，会马上遇到一个问题：

> Harness 到底应该管到哪里？

如果什么都往 Harness 里塞，它会迅速变成一个巨型平台；如果只负责调用模型和工具，它又很难真正承担 Reliability。

我更倾向于把 Harness 定义成一个**执行控制边界**：凡是决定“Agent 实际能做什么、做了什么、失败后怎么办、结果能不能被信任”的能力，都应该优先落在 Harness，而不是只存在于 Prompt。

## 一、Harness 至少应该拥有七类职责

### 1. Context Control

Harness 应该明确控制：

- 这一轮给模型什么上下文；
- 哪些信息必须保留；
- 哪些历史可以压缩；
- 当前环境状态从哪里读取；
- Tool Schema 用哪个版本；
- Prompt / Policy 用哪个版本。

关键不是“拼 Prompt”，而是让每次模型决策都能追溯到一个明确 Context Snapshot。

### 2. Tool Control

模型只能**请求**调用工具。

Harness 决定：

- Tool 是否存在；
- 参数是否合法；
- 当前身份有没有权限；
- 是否需要审批；
- 超时是多少；
- 是否允许重试；
- Tool Result 怎么标准化。

真正的 Tool Runtime 应该在模型之外。

### 3. State Control

Conversation History 不是完整状态。

Harness 还应该维护：

```text
goal
plan
completed_steps
pending_steps
artifacts
tool_results
side_effects
checkpoint
budget
verification_state
```

这样 Agent 中断后才能恢复，失败后才能知道“已经做了什么”。

### 4. Policy Control

任何关键规则，只要能写成确定性判断，就不应该只留在 Prompt 里。

例如：

```text
禁止访问 /prod
写操作必须审批
单次运行最多 30 个 Tool Call
数据库删除操作不可自动 Retry
```

Prompt 可以提醒。

Policy 必须能真正阻断。

### 5. Trace Control

Harness 应该留下结构化执行轨迹，而不是只输出一堆 stdout。

至少要关联：

```text
run_id
goal
context_version
model_turn
tool_call
tool_result
state_change
retry
error
artifact
verification
final_status
```

Trace 是后续 Eval、Failure Analysis 和 Regression 的事实来源。

### 6. Recovery Control

恢复不能只是：

> 再把错误丢给模型试一次。

Harness 需要知道：

- 哪些错误可以 Retry；
- 哪些动作幂等；
- 哪一步已经产生副作用；
- 最近可恢复 Checkpoint 在哪里；
- Resume 前是否需要重新验证环境。

### 7. Verification Interface

Harness 不一定自己完成所有验证，但必须为验证提供稳定接口。

例如 Coding Agent 最终返回：

```text
changed_files
test_command
test_exit_code
test_report
diff
artifacts
```

这些不是“回答内容”，而应该是 Runtime 级 Evidence。

## 二、哪些东西不应该全部交给 Harness

Harness 不是万能平台。

有些能力更适合在相邻层。

### Workflow

如果业务要求固定经过：

```text
审批 → 执行 → 审计 → 发布
```

这种确定性流程更适合 Workflow Engine，而不是让 Agent 自己规划。

### Eval Platform

Eval 更关注：

- 跨版本比较；
- Benchmark；
- Regression Set；
- Judge；
- 指标趋势。

Harness 负责产出执行事实，Eval 消费这些事实做评估。

### CI / CD

Harness 不应该重新实现完整发布平台。

它应该把 Verification / Risk / Gate Result 接进现有 CI、Merge、Release 流程。

## 三、一个实用边界：谁负责“事实”，谁负责“判断”

我很喜欢用这个方式拆系统。

Harness 负责尽量稳定地产出事实：

```text
发生了什么
调用了什么
改了什么
失败在哪里
证据是什么
```

Eval / Gate 再基于这些事实做判断：

```text
是否通过
风险是否可接受
是否需要阻断
```

如果 Harness 连事实都留不下来，后面所有质量判断都会变成猜测。

## 四、不要让 Harness 变成“Prompt 管理平台”

一个常见反模式是：

```text
Harness
=
Prompt Template
+
Model API
+
Tool Registry
```

这只能算 Agent Runner 的早期形态。

真正进入生产后，Harness 至少应该回答：

- 当前 Run 的边界是什么？
- 谁允许它执行这个 Tool？
- 出错以后谁决定 Retry？
- Side Effect 怎么记录？
- Trace 是否完整？
- 最终结果有没有 Evidence？
- 失败是否能被复现？

这些问题，才决定 Harness 有没有真正承担 Runtime Responsibility。

## 五、我会怎么画 Harness 的边界

```text
                ┌───────────────────┐
                │      Agent        │
                │ Goal / Reasoning  │
                └─────────┬─────────┘
                          ↓
        ┌────────────────────────────────┐
        │            Harness             │
        │                                │
        │ Context       Tool Runtime     │
        │ State         Policy           │
        │ Budget        Trace            │
        │ Recovery      Evidence API     │
        └───────────────┬────────────────┘
                        ↓
      ┌───────────────────────────────────┐
      │ Workflow / Eval / CI / Release    │
      └───────────────────────────────────┘
```

Harness 是中间那层。

它把模型的不确定决策，变成有边界的系统行为。

## 六、判断一个 Harness 是否成熟，可以看这张清单

```text
□ Context 是否版本化
□ Tool 是否有统一执行层
□ State 是否独立于聊天历史
□ Policy 是否能硬阻断
□ Retry 是否按错误类型处理
□ Side Effect 是否有记录
□ Trace 是否可重建
□ Checkpoint / Resume 是否明确
□ Evidence 是否结构化
□ Eval / Gate 是否能直接消费输出
```

前四项解决“能不能控制”。

中间三项解决“出了问题能不能定位”。

最后三项解决“结果能不能进入交付”。

## 结语

Harness 不应该变成一个什么都管的平台。

但它必须牢牢掌握一件事：

**执行事实和执行边界。**

模型负责决定下一步想做什么。

Harness 负责决定：

**这一步是否允许发生，以及发生之后系统如何留下证据。**

下一篇：[Trace 不是日志：Harness 应该记录哪些执行证据？](/harness/trace-is-not-just-logs/)
