---
layout: post
title: "Model Eval 和 Agent Eval 有什么区别？从单次输出到完整执行轨迹"
date: 2026-09-23 09:00:00 +0800
categories: [AI-Eval, Agent-Eval, Agent-Reliability]
permalink: /eval/model-eval-vs-agent-eval/
description: "Model Eval 主要评模型输出，Agent Eval 还必须评 Tool、State、Trace、Side Effect、Evidence 和最终任务完成度。本文拆开两者的评价对象和工程边界。"
tags: ["ai-eval", "agent-eval", "model-eval", "trace-evidence", "agent-reliability"]
series: ai-eval
series_order: 3
---

> **AI Eval 系列 #03**  
> 上一篇：[排行榜第一，为什么到了你的业务里可能不好用？](/eval/why-leaderboard-is-not-enough/)

Model Eval 和 Agent Eval 最大的区别，不是题目更难。

而是：

**被评对象变了。**

Model Eval 常常可以把一次任务近似成：

~~~text
Input → Model → Output
~~~

Agent 系统却更像：

~~~text
Goal
 ↓
Context
 ↓
Model Decision
 ↓
Tool Call
 ↓
Environment
 ↓
State Update
 ↓
Next Decision
 ↓
...
 ↓
Final Result
~~~

因此只检查最终答案，很容易漏掉真正的问题。

## 一、Model Eval 主要看“输出对不对”

一个典型 Model Eval 可能评：

- Answer Correctness；
- Instruction Following；
- Format；
- Relevance；
- Completeness；
- Safety；
- Reasoning / Coding Capability。

比如：

~~~text
Input:
把下面文本转换成 JSON

Output:
{...}

Grader:
Schema Validation
~~~

只要输入、输出和判定规则定义清楚，这类评测相对直接。

## 二、Agent Eval 还要看“过程有没有失控”

Agent 会真正操作外部世界。

它可能：

- 调 API；
- 改文件；
- 查数据库；
- 创建工单；
- 调用浏览器；
- 修改代码；
- 触发审批；
- 与其他 Agent 协作。

这时出现一种非常危险的情况：

**最终结果看起来正确，但执行过程已经错了。**

例如一个 Agent 的任务是更新配置。

最终文件内容正确，但它可能：

1. 先改错了生产环境；
2. 发现异常；
3. 又把内容改回来；
4. 最后输出“任务完成”。

只看最终文件：

~~~text
PASS
~~~

但如果看 Trace：

~~~text
Side Effect Violation
~~~

这就是 Agent Eval 和普通 Model Eval 的根本差异。

## 三、Agent Eval 至少要评六层

我更倾向于把 Agent Eval 拆成六层。

### 1. Task Success

最终任务有没有完成。

这是最基本的一层。

### 2. Action Correctness

中间动作是否合理，例如：

- Tool 是否选对；
- 参数是否正确；
- 是否出现无意义重复；
- 是否调用了禁止工具。

### 3. State Correctness

Agent 认为的状态，和真实环境是否一致。

例如：

~~~text
Agent:
部署成功

Real State:
服务其实启动失败
~~~

这是典型 State Desync。

### 4. Constraint Compliance

过程中有没有违反约束。

例如：

- 不允许修改生产；
- 不允许删除数据；
- 必须审批；
- 预算不能超过上限；
- 只能访问指定目录。

### 5. Evidence Completeness

Agent 说“完成”时，有没有提供足够证据。

例如测试任务至少应该能回答：

- 跑了什么；
- 结果是什么；
- 哪些失败；
- 日志在哪里；
- 哪个产物可以独立复核。

### 6. Efficiency

即使完成，也要看：

- Step 数；
- Token；
- Tool Calls；
- Retry；
- Latency；
- Cost。

一个 5 步能完成的任务跑 50 步，本身就可能是 Reliability 信号。

## 四、所以 Trace 会变成 Eval 的核心输入

Anthropic 在 Agent Eval 的工程文章中明确强调，多步 Agent 的能力让评测变得更困难，因为 Agent 会调用工具、修改状态并根据中间结果调整行为。

OpenAI 的 Agent Eval 文档也把 Trace Grading 放在非常核心的位置：通过完整 Trace 检查 Tool 选择、Handoff、指令违反和 Workflow 行为。

这意味着 Agent Eval 的输入不应该只有：

~~~text
Prompt + Final Answer
~~~

而应该更像：

~~~text
Goal
Context
Trace
Tool Calls
Tool Results
State Changes
Artifacts
Final Output
Evidence
~~~

Trace 不再只是 Debug 日志，而是评测数据。

## 五、Agent 的 Grader 也会变复杂

Model Eval 常见：

~~~text
Output → Grader
~~~

Agent Eval 更接近：

~~~text
Final Result ───────→ Result Grader
Trace ──────────────→ Behavior Grader
State ──────────────→ State Verifier
Artifacts ──────────→ Artifact Validator
Side Effects ───────→ Policy Check
Evidence ───────────→ Evidence Validator
~~~

最后组合成一个整体判断。

而且并不是所有结果都应该压缩成 0～100 分。

有些约束更适合直接做 Gate：

~~~text
Critical Side Effect = FAIL
Missing Evidence = UNVERIFIED
Permission Violation = FAIL
Task Success = PASS / FAIL
~~~

## 六、一个例子：让 Agent 修 Bug

任务：

~~~text
修复登录失败问题，并确保回归测试通过
~~~

只做 Model Eval，你可能评：

- 给出的补丁是否合理；
- 最终解释是否正确。

做 Agent Eval，则还要验证：

~~~text
是否定位到真实根因
是否修改了正确文件
是否运行了测试
测试是否真的通过
是否绕过失败测试
是否修改无关文件
是否产生额外副作用
是否留下可复核 Evidence
~~~

最终：

~~~text
Patch Correct
≠
Task Verified
~~~

这也是为什么 Coding Agent 的质量问题最终会进入 Harness、Trace、Evidence 和 Regression。

## 七、Model Eval 和 Agent Eval 怎么衔接

两者不是竞争关系。

更合理的是分层：

~~~text
Model Eval
   ↓
验证基础能力

Component Eval
   ↓
Prompt / Tool / RAG / Router

Agent Eval
   ↓
验证完整任务执行

Production Regression
   ↓
验证版本变化

Quality Gate
   ↓
决定能不能发布
~~~

Model Eval 告诉你：

**模型有没有这项能力。**

Agent Eval 告诉你：

**整个系统能不能把这项能力稳定转化成任务结果。**

## 八、这也是 AI Testing 会发生变化的地方

传统 AI 测试很容易停留在：

~~~text
Input → Output → Score
~~~

Agent 出现之后，测试对象开始扩张为：

~~~text
Decision
Execution
State
Evidence
Failure
Recovery
Regression
~~~

因此未来真正值得建设的，不只是“模型评测平台”。

而是一套能够把：

**真实任务 → 执行 Trace → Failure → Eval → Regression → Gate**

串起来的可靠性交付体系。

这也是后续 AI Eval 系列会继续讨论的方向。

下一篇可以继续进入最实际的问题：

**怎样构造一套真正有用的业务 Eval Dataset？**

## 参考资料

- [Anthropic — Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [OpenAI — Evaluate agent workflows](https://developers.openai.com/api/docs/guides/agent-evals)
- [OpenAI — Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)
