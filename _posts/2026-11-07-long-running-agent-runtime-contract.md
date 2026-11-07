---
related_posts:
  - /harness/verification-report-provenance/
  - /harness/agent-evidence-contract/
  - /harness/verification-loops-and-budget-exhaustion/
layout: post
title: "长程 Agent 不能只靠一个 completed：把中止、接管与恢复纳入 Runtime 契约"
description: "结合 Kimi Hosted Agents 与 Qwen Code 的公开工程变化，拆解长程 Agent 的运行生命周期，以及 Harness 应如何验证中止、等待、恢复和交付。"
date: 2026-11-07 08:00:00 +0800
updated: 2026-11-07 08:00:00 +0800
last_modified_at: 2026-11-07 08:00:00 +0800
categories: [Agent-Harness, Agent-Reliability, Trace-Evidence, Quality-Gate]
permalink: /harness/long-running-agent-runtime-contract/
tags: [agent-harness, agent-runtime, agent-reliability, execution-control, recovery, quality-gate]
series: agent-harness
series_order: 19
---

一个运行了二十分钟的 Agent，最后返回 `completed`，并不能说明它可靠地完成了任务。

它可能在等待人工输入时丢失上下文，可能在用户要求停止后仍继续调用工具，也可能在进程恢复后重复执行已经产生过副作用的步骤。即使最终报告写着成功，也还需要确认：执行是否真的停止、未完成工作是否被正确保留、恢复后有没有重复操作，以及最终结果是否经过独立验证。

长程 Agent 把问题从“模型能不能完成下一步”，扩展成了“系统能不能管理一段持续变化的执行生命周期”。

2026 年 11 月 5 日，Kimi 发布 Hosted Agents，将 Harness 作为云端服务提供，公开能力包括独立沙箱、网络访问权限控制、会话中止、执行留痕和审计导出。[官方发布](https://www.kimi.com/news/kimi-hosted-agents)

11 月 6 日，Qwen Code v0.26.9 更新了 Managed Agent 的自动化、持久化结构化用户问题、执行恢复，以及 Verify PR 和 Skill 安装管理能力。[官方 Release](https://github.com/QwenLM/qwen-code/releases)

两项变化来自不同产品，不能据此认定它们实现了相同的内部架构。但它们共同提示了一个工程问题：**长程 Agent 的可靠性，不能只由模型输出和最终任务状态定义，还要由运行时对生命周期的控制能力定义。**

## 一、长程执行引入了新的失败类型

短任务通常可以用一次调用、一次工具执行和一次结果校验来描述。长程任务则会跨越多个边界：

- 等待外部系统返回；
- 等待用户补充信息或审批；
- 多个工具并发执行；
- 执行环境或网络暂时不可用；
- 进程重启、租约续期或工作区恢复；
- 用户要求取消，或者系统触发预算上限；
- 任务恢复后继续执行并最终交付。

这些边界会产生不同于普通模型错误的故障。

例如，用户要求停止任务，但工具调用仍在运行；系统显示任务暂停，却没有持久化下一步需要的输入；执行器恢复后重新读取任务，却再次提交已经成功的付款或写入操作；或者任务已经结束，但后台进程仍持有资源。

把这些问题统称为“Agent 执行失败”，会掩盖真正需要验证的对象：运行时状态、任务所有权、工具副作用和恢复协议。

## 二、近期产品变化说明了什么

### 1. Kimi Hosted Agents：把 Harness 的运行控制交给托管平台

Kimi Hosted Agents 于 2026 年 11 月 5 日发布。官方说明将 Harness 和运行环境作为云服务提供，支持长程任务和多 Agent 协作，并公开列出独立沙箱、网络访问权限控制、会话中止、执行过程留痕、审计导出以及用量报表等能力。

这组能力值得放在一起理解：

- **沙箱和网络策略**限制 Agent 能影响哪些外部资源；
- **会话中止**提供执行控制入口；
- **执行留痕和审计导出**让事后调查有材料；
- **用量统计**帮助识别持续运行带来的资源消耗。

官方还介绍了 Kimi Inference Hook：在模型推理前检查任务输入和工具返回内容，由企业定义安全规则。该组件目前仅向企业认证用户定向开放。

这些是官方公开的产品能力，不等于已经证明每一种取消、恢复或异常场景都具备完整保证。尤其要注意：提供“中止会话”的产品入口，不自动等于所有正在执行的外部副作用都能被撤销。

### 2. Qwen Code：Managed Agent 和 Skill 管理开始处理更长的生命周期

Qwen Code v0.26.9 于 2026 年 11 月 6 日发布。Release Notes 中与运行时可靠性相关的变化包括：

- Managed Agent 支持持久化的结构化用户问题；
- Managed Agent 默认启用自动化；
- Activation Lease 续期查找得到优化；
- HTTP Managed Session Writer Recovery 保留仍有效的进行中续期授权，避免不必要地重新获取 Writer；
- Verify PR 沙箱执行轮次可以读取 PR Review Threads；
- Autofix PR 的拒绝结果提供机器可读的拒绝代码和下一步信息；
- Skill 安装增加大 ZIP 的磁盘处理、恢复备份保护，以及安装失败后的 Receipt 查询。

这些改动分别触及用户交互持久化、会话续期、写入恢复、验证上下文和 Skill 安装恢复。它们不构成一套完整的长程 Agent 状态机，但说明实际工程问题已经超出“调用模型并等待答案”。

## 三、把 Runtime 生命周期拆成明确状态

一个可验证的 Runtime 不应该只暴露 `running` 和 `completed` 两个状态。可以先采用如下逻辑状态模型：

| 状态 | 含义 | 关键保证 |
| --- | --- | --- |
| `ACCEPTED` | 任务已接收 | 任务 ID 和初始配置已持久化 |
| `RUNNING` | 正在执行 | 执行器与任务归属明确 |
| `WAITING_INPUT` | 等待用户或外部输入 | 等待原因、问题和恢复位置已保存 |
| `CANCELLING` | 正在取消 | 不再启动新的非必要动作，并跟踪在途工具 |
| `CANCELLED` | 取消完成 | 已知在途操作有明确终态或风险说明 |
| `RECOVERING` | 正在恢复 | 校验检查点、租约和副作用状态 |
| `BLOCKED` | 无法安全继续 | 记录阻塞原因和需要的人工动作 |
| `COMPLETED` | 执行流程结束 | 结果已提交，后置验证状态明确 |
| `FAILED` | 执行失败 | 错误、部分副作用和恢复建议可追溯 |

这是一份建议的设计模型，不是 Kimi 或 Qwen 已公开声明采用的状态枚举。实际系统可以使用不同名称，但状态之间的转换必须有明确条件。

例如，`WAITING_INPUT` 不应该只是 UI 上的一条提示。系统需要持久化问题内容、任务版本、等待原因和恢复所需的上下文。用户回答后，执行器应能确认该回答属于哪个任务、哪个等待轮次，避免旧输入被错误地用于新任务。

同样，`CANCELLED` 也不能简单等于“收到了取消请求”。如果工具调用已经发出，系统必须区分取消请求已接受、执行器已停止派发新动作、在途调用已结束，以及外部副作用是否可撤销。

## 四、中止不是回滚：必须区分控制面与副作用

这是长程 Agent 最容易被混淆的地方。

**中止控制面**回答：运行时是否停止继续调度任务、调用工具和生成新动作。

**副作用处理**回答：已经发出的请求是否完成、是否成功写入外部系统、能否撤销，以及恢复后是否允许重试。

例如，一个 Agent 正在调用 ERP 接口创建采购订单。用户点击停止后，Harness 可以阻止下一步工具调用，但已经发出的 HTTP 请求可能仍在服务端执行。

因此，取消流程至少要记录：

1. 取消请求时间和请求来源；
2. 当时正在执行的工具调用及其调用 ID；
3. 哪些动作尚未派发，哪些已经发出；
4. 每个在途动作的最终状态；
5. 外部副作用是否确认、未知或已补偿；
6. 是否允许恢复，以及恢复时从哪个检查点继续。

不能因为客户端超时就推断服务端没有执行，也不能因为 Agent 没收到响应就直接重试非幂等操作。

对于有副作用的工具，优先使用业务幂等键、操作状态查询和明确的补偿机制。无法确认外部操作结果时，应进入 `BLOCKED` 或人工核对，而不是自动重复执行。

## 五、恢复的核心是重新建立执行事实

恢复不是把之前的对话文本重新塞给模型。

至少需要重新确认四类事实：

**任务事实：** 当前任务 ID、任务版本、目标和剩余工作是什么。

**执行事实：** 哪些步骤已经开始、结束或仍在运行，当前执行器是否仍拥有有效租约。

**副作用事实：** 外部系统中哪些操作已经发生，哪些状态仍未知，哪些步骤可以安全重试。

**验证事实：** 上一次验证针对哪个输入版本，哪些证据仍然有效，恢复后是否需要重新验证。

可以把恢复流程表达为：

~~~text
加载持久化任务
      |
      v
校验任务版本与执行租约
      |
      v
读取检查点和工具调用记录
      |
      v
查询不确定的外部副作用
      |
      +---- 状态明确且可继续 ----> 恢复执行
      |
      +---- 需要人工确认 -------> BLOCKED
      |
      +---- 关键状态不一致 -----> FAILED / 隔离
      |
      v
执行后置验证并保存新证据
~~~

这里最重要的不是检查点保存得有多频繁，而是恢复时能够区分“已完成”“未执行”和“结果未知”。

如果把结果未知的操作直接当成未执行，恢复就可能制造重复副作用。

## 六、为长程 Agent 建立最小 Trace 契约

要定位上述问题，Trace 需要关联的不只是模型请求和工具输出，还包括运行时生命周期。

建议至少保存：

~~~json
{
  "task_id": "task-123",
  "task_version": 4,
  "run_id": "run-456",
  "state": "WAITING_INPUT",
  "state_version": 12,
  "checkpoint_ref": "checkpoint://...",
  "executor_id": "worker-7",
  "lease_id": "lease-9",
  "pending_question_id": "question-2",
  "tool_calls": [
    {
      "tool_call_id": "call-88",
      "operation_key": "business-operation-001",
      "status": "UNKNOWN"
    }
  ],
  "evidence_refs": [
    "trace://...",
    "artifact://..."
  ]
}
~~~

这只是说明字段关系的示例，不代表任何一个被引用产品已经采用了这套 Schema。

其中有几个设计约束值得注意：

- `task_version` 和 `state_version` 用于识别过期状态更新；
- `executor_id` 和 `lease_id` 用于判断执行所有权；
- `pending_question_id` 用于把用户输入绑定到正确等待轮次；
- `operation_key` 用于关联外部副作用和幂等控制；
- `evidence_refs` 用于关联执行日志、外部状态和验证产物。

状态更新应具备版本检查，避免旧 Worker 在恢复后覆盖新状态。敏感输入、凭据和业务数据不应为了可观测性而无边界地写入 Trace；应根据审计需要进行脱敏、访问控制和保留期限管理。

## 七、把生命周期保证转成回归测试

只测一次正常完成，覆盖不了长程 Agent 的主要风险。可以从以下场景建立最小回归集：

| 场景 | 注入条件 | 核心断言 |
| --- | --- | --- |
| 等待用户输入 | 任务进入等待后进程重启 | 问题和恢复位置仍然存在 |
| 用户取消 | 工具调用执行前取消 | 不再派发新的工具调用 |
| 在途取消 | 工具调用已发出后取消 | 记录真实副作用状态，不伪造回滚 |
| Worker 崩溃 | 执行中终止 Worker | 新 Worker 能校验租约和检查点 |
| 租约续期 | 续期请求与恢复交错 | 不产生两个有效执行所有者 |
| 重复恢复 | 对同一检查点触发两次恢复 | 不重复执行非幂等操作 |
| 结果未知 | 外部接口超时但服务端可能已执行 | 先查询操作状态，不盲目重试 |
| 预算耗尽 | 达到执行或重试上限 | 进入明确阻塞或失败状态 |

每条用例都应保留任务状态变化、工具调用记录和外部副作用证据。否则即使测试失败，也很难判断问题发生在模型决策、Harness 调度、工具执行还是恢复逻辑。

## 八、Quality Gate 不应只检查最终结果

当长程任务进入交付阶段，Gate 至少要回答：

1. 任务是否处于允许交付的终态；
2. 是否仍存在在途工具调用或未确认副作用；
3. 是否有未处理的人工问题或审批；
4. 执行是否超过预算或权限边界；
5. 恢复前后的任务版本和执行记录是否一致；
6. 最终结果是否通过与当前目标版本匹配的验证；
7. Trace 和关键证据是否可以读取。

这与上一期《Agent 验证报告不能只写 PASS：把结果绑定到代码、模型与 Skill 快照》形成递进：上一期解决验证报告属于哪一轮、对应什么代码和方法；本期进一步讨论验证发生之前和之后，Runtime 如何保证执行可以被停止、接管和恢复。

两者共同构成一条更完整的链路：

```
受控执行
   ↓
生命周期状态可追踪
   ↓
中止与恢复边界明确
   ↓
外部副作用可核验
   ↓
验证报告绑定执行快照
   ↓
Quality Gate 决定是否交付
```

## 结语

长程 Agent 的可靠性，不是让它永远不失败，而是让系统知道它正在做什么、为什么停下来、已经产生了什么副作用，以及怎样安全地继续或结束。

`completed` 只能描述一个状态，不能替代对任务生命周期的证明。

**当 Agent 从几分钟的调用变成持续运行的业务执行者，Harness 就必须从工具调度器进一步成为生命周期控制器。**

## 参考资料

- [Kimi Hosted Agents 正式发布：Harness as a Service（2026-11-05）](https://www.kimi.com/news/kimi-hosted-agents)
- [Qwen Code v0.26.9 Release Notes（2026-11-06）](https://github.com/QwenLM/qwen-code/releases)
- [Qwen Code v0.26.8 Release Notes（2026-11-05）](https://github.com/QwenLM/qwen-code/releases)
- [腾讯混元发布 Hy4（2026-11-04）](https://www.tencent.com/zh-cn/tencent-launches-hy4-joining-the-ranks-of-the-worlds-leading-open-source-ai-models/)
- [Agent 验证报告不能只写 PASS：把结果绑定到代码、模型与 Skill 快照](https://hugfeature.github.io/harness/verification-report-provenance/)
- [结果正确就够了吗？给 Agent 设计 Evidence Contract](https://hugfeature.github.io/harness/agent-evidence-contract/)
