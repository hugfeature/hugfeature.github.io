---
layout: post
title: "Trace 不是日志：Harness 应该记录哪些执行证据？"
date: 2026-09-22 17:41:00 +0800
categories: [Agent-Harness, Agent-Reliability]
permalink: /harness/trace-is-not-just-logs/
description: "Agent Trace 不只是日志。本文从 Run、Turn、Tool、State、Artifact、Verification 六类事件设计一条可定位、可验证、可回归的执行证据链。"
tags: ["agent-harness", "trace-evidence", "observability", "agent-reliability"]
series: agent-harness
series_order: 10
---

> **Agent Harness 系列 #10**  
> 上一篇：[Harness 到底应该管什么？](/harness/what-should-agent-harness-own/)

很多 Agent 系统说自己有“可观测性”，实际打开以后只有：

```text
2026-09-22 10:03 calling model
2026-09-22 10:03 calling tool
2026-09-22 10:04 success
```

这类日志能帮你确认系统有没有报错，但很难回答真正重要的问题：

> Agent 为什么走到这里？第一次错误发生在哪？最终结果到底有没有证据？

所以我更愿意把 Agent Trace 定义成：

**一次执行过程的结构化证据链。**

## 一、日志和 Trace 的区别

传统日志通常关注单个组件：

```text
API error
timeout
database connection failed
```

Agent Trace 关注的是整条 trajectory：

```text
Goal
→ Context
→ Model Decision
→ Tool Call
→ Tool Result
→ State Change
→ Retry
→ Verification
→ Final Result
```

它的目标不是“多记录一点”，而是让一次 Run 能被重新解释。

## 二、第一层：Run 级信息

每次运行至少要有：

```text
run_id
task_id
goal
agent_version
model
harness_version
prompt_version
toolset_version
start_time
end_time
final_status
```

这层解决的是：

**这到底是哪一次执行？**

如果模型、Prompt、Tool 都会变化，没有版本信息，后面的 Regression 很难成立。

## 三、第二层：Model Turn

每一次模型决策最好记录：

```text
turn_id
context_snapshot_id
model
latency
token_usage
decision_type
requested_tool
finish_reason
```

不一定要永久保存完整 Chain-of-Thought。

真正重要的是保存**可用于工程复盘的输入输出边界和决策结果**。

例如：

```text
Turn 12
Context v18
Decision = tool_call
Tool = run_tests
Reason category = verify_change
```

## 四、第三层：Tool Call

Tool Event 至少包括：

```text
tool_name
arguments
risk_level
permission_result
start_time
duration
exit_status
retry_count
side_effect
```

尤其要区分：

```text
requested
approved
started
completed
failed
```

否则你会遇到一种很常见的错觉：

> Trace 里有 Tool Call，所以 Tool 肯定执行成功了。

并不一定。

## 五、第四层：State Change

这是很多系统最缺的一层。

例如执行：

```text
edit_file("app.py")
```

真正重要的不只是 Tool 返回：

```text
success
```

还要知道：

```text
changed_files = ["app.py"]
before_hash = ...
after_hash = ...
checkpoint = ...
```

因为 Reliability 关注的是：

**真实世界状态到底变了什么。**

## 六、第五层：Artifact

一次 Agent Run 可能产生：

- Git diff；
- Test report；
- Screenshot；
- SQL result；
- Generated file；
- Build artifact；
- Browser state；
- Approval record。

这些最好不要只作为文本塞进日志。

应该有稳定 Artifact Reference：

```text
artifact_id
type
uri
hash
producer_step
created_at
```

这样 Evidence 才能真正被后续系统消费。

## 七、第六层：Verification

如果系统最终宣称：

```text
PASS
```

Trace 应该能回答：

**谁验证的？依据是什么？**

例如：

```text
verification_id
verifier = pytest
command = pytest tests/test_login.py
exit_code = 0
artifact = test-report.xml
verified_at = ...
```

如果只是：

```text
agent_output = "tests passed"
```

这不是独立证据。

## 八、一条最小 Trace Schema

可以从这种结构开始：

```json
{
  "run_id": "r-1024",
  "goal": "fix login timeout",
  "events": [
    {
      "type": "model_decision",
      "step": 1,
      "context_version": "ctx-1",
      "action": "read_file"
    },
    {
      "type": "tool_result",
      "step": 1,
      "tool": "read_file",
      "status": "success"
    },
    {
      "type": "state_change",
      "step": 4,
      "changed_files": ["src/login.py"]
    },
    {
      "type": "verification",
      "step": 7,
      "command": "pytest",
      "exit_code": 0
    }
  ],
  "final_status": "verified"
}
```

开始时不需要设计得特别复杂。

关键是：

**结构稳定。**

## 九、Trace 最重要的三个用途

### 1. Failure Localization

找到第一次偏离正确轨迹的位置。

### 2. Evidence Verification

判断最终结果有没有独立证据支撑。

### 3. Regression Replay

把真实失败重新执行。

这三件事其实是一条链：

```text
Trace
→ Failure
→ Reproduction
→ Regression
```

## 十、什么不应该无脑记录

Trace 不是越多越好。

要考虑：

- Secret；
- PII；
- 凭证；
- 大体积文件；
- 完整数据库结果；
- 不必要的敏感 Prompt 内容。

更健康的是：

```text
原始数据
↓
Redaction / Hash / Reference
↓
Trace
```

既能定位，又不把风险复制到 Observability 系统里。

## 十一、怎么判断 Trace 是否够用

可以做一个很简单的“事故复盘测试”。

拿到一条失败 Run，只看 Trace，问：

1. 任务目标是什么？
2. 模型用了哪个版本？
3. 第一次异常发生在哪一步？
4. 当时模型看到了什么状态？
5. Tool 是否真的执行？
6. 产生了什么副作用？
7. 最终结果依据什么被判为成功？
8. 能不能重新构造最小复现？

如果大部分回答不了，说明现在记录的只是日志，不是 Evidence-grade Trace。

## 结语

Agent Reliability 不可能建立在：

> “我看日志感觉应该没问题。”

真正有价值的 Trace 应该让系统能够：

**还原事实、定位失败、验证结果、生成回归。**

下一篇：[Agent 调错工具怎么办：Timeout、Retry、Budget 与 Side Effect](/harness/tool-failure-timeout-retry-budget-side-effect/)
