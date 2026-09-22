---
layout: post
title: "Agent 调错工具怎么办：Timeout、Retry、Budget 与 Side Effect"
date: 2026-09-22 17:42:00 +0800
categories: [Agent-Harness, Agent-Reliability]
permalink: /harness/tool-failure-timeout-retry-budget-side-effect/
description: "把 Agent Tool 执行拆成错误分类、Timeout、Retry、Budget、Idempotency 和 Side Effect 六个控制点，避免最终成功掩盖过程失控。"
tags: ["agent-harness", "retry", "timeout", "side-effect", "agent-reliability"]
series: agent-harness
series_order: 11
---

> **Agent Harness 系列 #11**  
> 上一篇：[Trace 不是日志：Harness 应该记录哪些执行证据？](/harness/trace-is-not-just-logs/)

Tool 是 Agent 真正开始影响外部世界的地方。

模型选错一个词，问题可能只是回答不准。

模型选错一个 Tool，可能意味着：

- 改错文件；
- 重复创建数据；
- 发错消息；
- 重复支付；
- 错误发布；
- 删除不可恢复资源。

所以 Tool Reliability 的核心不是“失败以后 Retry”。

而是：

**先判断这次失败到底是什么，再决定系统能不能继续。**

## 一、先做错误分类

最少可以把 Tool Failure 分成四类。

### Transient

短暂性错误：

- 网络抖动；
- 429；
- 临时服务不可用；
- 可恢复 Timeout。

通常允许有限 Retry。

### Permanent

请求本身错误：

- 参数非法；
- 资源不存在；
- 权限不足；
- Schema 不匹配。

继续 Retry 没意义。

### Ambiguous

最危险的一类：

> 请求超时，但不知道操作到底有没有成功。

例如：

```text
create_order()
→ timeout
```

不能直接重试。

必须先查询真实状态。

### Policy Failure

系统主动阻断：

- 禁止目录；
- 超预算；
- 高风险 Tool 未审批；
- 不允许当前身份操作。

这种错误不应该 Retry。

## 二、Timeout 不是简单“等太久”

Timeout 后首先要问：

**外部世界有没有发生变化？**

对于 read-only Tool：

```text
search()
get_status()
read_file()
```

Timeout 后重试通常风险较低。

但对于：

```text
deploy()
send_email()
create_payment()
```

Timeout 可能意味着：

```text
结果未知
```

更合理流程：

```text
timeout
 ↓
verify_external_state()
 ↓
already_done?
 ├─ yes → continue
 ├─ no  → safe retry
 └─ unknown → stop / human
```

## 三、Retry 必须由 Policy 控制

一个最小 Retry Policy 可以是：

| Tool 类型 | 是否自动 Retry |
| --- | --- |
| Read-only | 可以 |
| 幂等 Write | 有条件可以 |
| 非幂等 Write | 默认不可以 |
| Destructive | 默认不可以 |
| Approval-required | 不可绕过审批 |

还需要：

```text
max_retry
backoff
retryable_errors
idempotency_key
```

否则 Agent 很容易陷入：

```text
失败 → 再试 → 失败 → 再试
```

最终把一个局部问题放大成系统事故。

## 四、Budget 是防失控边界

Budget 不只是 Token 和钱。

Harness 可以同时控制：

```text
max_turns
max_tool_calls
max_same_tool_calls
max_retry
max_wall_time
max_cost
max_write_actions
```

例如：

```text
同一 Tool 连续调用 5 次
↓
触发 repeated_action
↓
stop / re-plan
```

这类机制对 Rabbit Hole 和 Reasoning Loop 很有效。

## 五、Side Effect 必须成为一等公民

Tool Registry 不应该只有：

```text
name
description
schema
```

还应该考虑附加元数据：

```text
risk_level
read_only
idempotent
reversible
requires_approval
requires_verification
```

例如：

```yaml
name: deploy_prod
risk_level: high
read_only: false
idempotent: false
reversible: partial
requires_approval: true
requires_verification: true
```

Harness 才能自动应用不同策略。

## 六、执行后的 Verification 同样重要

一个 Write Tool 返回：

```text
success
```

不代表真实状态正确。

例如：

```text
edit_file
↓
success
```

应该继续验证：

```text
file_hash_changed?
diff_expected?
tests_pass?
```

所以更完整的 Tool Lifecycle 是：

```text
Request
↓
Policy
↓
Execute
↓
Result
↓
State Verification
↓
Evidence
```

## 七、一个最小 Tool Execution Contract

可以给每个 Tool 返回统一结果：

```json
{
  "status": "success",
  "retryable": false,
  "side_effect": true,
  "artifact_refs": ["artifact-123"],
  "verification_required": true
}
```

失败时：

```json
{
  "status": "failed",
  "error_type": "timeout_unknown_state",
  "retryable": false,
  "verification_required": true
}
```

这样 Retry 不再由模型拍脑袋决定。

## 八、真正危险的是“最终成功”

假设：

```text
Tool A fail
Tool A fail
Tool B wrong
Tool C success
Final = PASS
```

如果系统只看 Final：

> 任务成功。

过程风险就完全消失了。

所以 Harness 应该同时输出过程指标：

```text
retry_count
repeated_actions
failed_tools
high_risk_actions
unverified_side_effects
budget_usage
```

最终结果正确，不代表执行质量合格。

## 结语

Agent 调错 Tool 并不可怕。

可怕的是 Runtime 不知道：

- 这个错误能不能重试；
- 有没有产生副作用；
- 当前状态到底是什么；
- 是否还应该继续。

真正可靠的 Tool Runtime，不是“让 Agent 尽量成功”。

而是：

**只允许系统在状态明确时继续。**

下一篇：[结果正确就够了吗？给 Agent 设计 Evidence Contract](/harness/agent-evidence-contract/)
