---
layout: post
title: "Eval 指标怎么设计？为什么 Pass Rate 远远不够"
date: 2026-09-23 10:00:00 +0800
categories: [AI-Eval, Agent-Eval]
permalink: /eval/eval-metrics-beyond-pass-rate/
description: "AI Eval 不能只看 Pass Rate。本文拆解 Task Success、pass@k、pass^k、Critical Failure、False Pass、Latency、Cost、Retry、Evidence 与 Regression Delta。"
tags: ["ai-eval", "eval-metrics", "agent-eval", "pass-at-k", "reliability"]
series: ai-eval
series_order: 6
---

> **AI Eval 系列 #06**  
> 上一篇：[LLM-as-a-Judge 怎么做才靠谱？](/eval/llm-as-a-judge/)

很多 Eval 最终会被压缩成一个数字：

**Pass Rate = 87%。**

这个数字当然有用。

但它通常只回答：

**“平均有多少任务通过？”**

它没有告诉你：失败是不是集中在关键任务、同一个任务多跑几次是否稳定、成功是不是靠大量 Retry 换来的、结果是否真的有 Evidence，以及延迟和成本是否已经不可接受。

所以生产级 Eval 的指标，至少应该从“单一准确率”升级成一组质量信号。

## 一、第一层：Task Success

最基础指标仍然是：

~~~text
Task Success Rate
=
成功任务数 / 总任务数
~~~

它适合回答总体趋势，但至少要按任务类型拆开：

~~~text
Overall
Core Tasks
Risk Tasks
Failure Regression
Long Context
Tool Calling
~~~

否则总体提升可能掩盖关键场景退化。

## 二、第二层：Critical Failure Rate

不是所有失败权重都一样。

例如“少一个解释字段”和“漏掉关键审批条件”都可能被算作 FAIL，但业务后果完全不同。

所以建议给 Case 加 Risk：

~~~text
low
medium
high
critical
~~~

然后单独统计：

~~~text
Critical Failure Rate
High-risk Pass Rate
~~~

真正用于发布门禁时，我更关心：

~~~text
Critical Failure = 0
~~~

而不是 Overall 从 91% 提升到 92%。

## 三、第三层：pass@k 和 pass^k

Agent 和生成式模型具有非确定性。同一个 Case 跑一次成功，不代表下一次还成功。

Anthropic 在 Agent Eval 实践中区分了两个很重要的指标。

### pass@k

k 次尝试里，**至少一次成功**。

它适合 Coding Agent、搜索多个候选方案，以及允许多次尝试、最终有一个结果即可的任务。

~~~text
能力上限 → 更适合看 pass@k
~~~

### pass^k

k 次尝试里，**每次都成功**。

它更接近生产稳定性。

客服、审批、企业自动化不能接受“多试几次总有一次对”，这类任务更应该关注连续成功能力。

~~~text
生产稳定性 → 更适合看 pass^k
~~~

只看一次 Pass Rate，很难看到这种差异。

## 四、第四层：First-pass Success

如果 Agent 最终成功，但中间 Retry 了 7 次，这个成功和一次完成不是一回事。

建议增加：

~~~text
First-pass Success Rate
Retry Rate
Average Retry Count
~~~

例如：

~~~text
Version A
Success = 92%
First-pass = 89%

Version B
Success = 93%
First-pass = 61%
~~~

只看 Success，B 好像更强；实际上它已经变得非常不稳定。

## 五、第五层：False Pass

如果你使用 LLM Judge 或复杂自动 Grader，最危险的指标不是 False Fail，而是：

**错误结果被判成 PASS。**

所以要单独记录：

~~~text
Judge False Pass Rate
Critical False Pass Rate
~~~

尤其是 Gate 场景，因为：

~~~text
真实错误
+
Grader 误判成功
=
风险被完全隐藏
~~~

这是评测系统本身的 Reliability 问题。

## 六、第六层：Evidence Completeness

Agent 说任务成功，不代表你能验证它。

因此可以定义：

~~~text
Evidence Completeness Rate
Verified Success Rate
~~~

例如：

~~~text
Task Success = 90%
Verified Success = 74%
~~~

差出来的 16%，说明 Agent 声称成功，但证据不足。

不同任务可以绑定不同 Evidence：

~~~text
Coding:
test result + diff + changed files

Testing:
executed cases + result + artifact

Deployment:
target version + health check + environment state
~~~

## 七、第七层：执行效率

成功并不是免费得到的。

至少记录：

~~~text
Latency P50 / P95
Token / Task
Cost / Task
Tool Calls / Task
Steps / Task
Retry / Task
~~~

对于 Agent，我尤其建议看 P95 Steps 和 P95 Tool Calls，因为长尾执行往往最容易隐藏 Loop、Rabbit Hole、重复搜索、Retry Storm 和状态不同步。

## 八、第八层：Regression Delta

版本对比不能只看新版本总分。

要看：

~~~text
Fixed
Regressed
Unchanged Pass
Unchanged Fail
~~~

例如：

~~~text
v2 相比 v1

Fixed: 18
Regressed: 7
Unchanged Pass: 65
Unchanged Fail: 10
~~~

这时最重要的问题不是“总分涨了多少”，而是：

**那 7 个 Regression 是什么？**

如果其中一个是 Critical Case，新版本可能仍然不能发布。

## 九、一个更实用的 Eval Scorecard

我会把结果拆成四组。

### Quality

~~~text
Overall Success
Core Pass Rate
Risk Pass Rate
Failure Regression Rate
~~~

### Reliability

~~~text
First-pass Success
pass^k
Retry Rate
Critical Failure
~~~

### Verification

~~~text
Verified Success
Evidence Completeness
Judge False Pass
~~~

### Efficiency

~~~text
P95 Latency
Cost / Task
Tool Calls
Steps
~~~

最后再结合具体业务定义 Gate。

## 十、不要急着做“总分”

很容易有人想把所有指标加权成：

~~~text
Quality Score = 87.3
~~~

这对 Dashboard 可以有帮助，但不要让总分覆盖底层事实。

因为：

~~~text
Critical Failure = 1
~~~

不能被：

~~~text
Latency +3 分
Cost +2 分
~~~

抵消。

更合理的是：

~~~text
Hard Gate
+
Diagnostic Metrics
~~~

Critical Failure、权限违规、已知 Regression 这类指标做 Hard Gate；Latency、Cost、Token 等用于权衡。

## 十一、最终目标不是“指标多”，而是能支持决策

一个指标值不值得留，判断标准很简单：

**它会改变你的工程决策吗？**

好的 Eval Metrics 应该能够回答：

~~~text
哪里变好了？
哪里变差了？
失败是否严重？
结果是否可信？
执行是否稳定？
现在能不能发布？
~~~

下一篇继续解决另一个常见混淆：

**Offline Eval 和 Online Eval 到底分别解决什么问题？**

## 参考资料

- [Anthropic — Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [OpenAI — Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)
