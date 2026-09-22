---
title: "Agent 说“完成了”，你凭什么相信？我给它加了一份 Evidence Contract"
channel: wechat
status: ready
source: /harness/agent-evidence-contract/
---

# Agent 说“完成了”，你凭什么相信？我给它加了一份 Evidence Contract

Agent 最常见的一句话是什么？

> 已完成。

Coding Agent 会说：

> Bug 已修复，测试全部通过。

测试 Agent 会说：

> 页面验证通过，没有发现异常。

Research Agent 会说：

> 信息已完成核验。

但我现在越来越不愿意直接接受这句话。

原因很简单：

**执行任务的人和证明任务完成的人，是同一个 Agent。**

这本质上仍然是一份 self-report。

## Outcome 和 Evidence 是两回事

假设 Coding Agent 返回：

Outcome：

Bug fixed。

这只是结论。

真正让我愿意相信它的，是另一组东西：

Git diff。

Changed files。

实际执行的 test command。

Exit code。

Test report。

Commit SHA。

这些才是 Evidence。

所以一个 Agent 任务至少应该拆成两部分：

**结果是什么？**

以及：

**你凭什么证明这个结果？**

这两个问题看起来很像，但工程意义完全不同。

## 我把它叫做 Evidence Contract

Evidence Contract 可以很简单：

> 某一类任务想被判定为 VERIFIED，必须提供哪些证据。

比如 Code Change：

必须提供 Changed Files、Git Diff、Test Command、Test Exit Code、Test Report。

UI 自动化：

必须提供 Target URL、Executed Steps、Screenshot、Assertion Result、Final Page State。

数据处理：

必须提供 Input Version、Query、Output Artifact、Row Count、Validation Result。

关键不是字段多少。

而是：

**先把“可信成功”的条件定义出来。**

## Agent 自己说测试通过，不算独立证据

Evidence 也有强弱。

最弱：

Agent：“测试通过了。”

稍强：

Agent：“我运行了 pytest，结果是 0。”

更强：

Harness 真实记录：

command = pytest

exit_code = 0

artifact = junit.xml

commit_sha = abc123

区别是什么？

越靠近真实执行事实，Evidence 越强。

所以我更倾向于：

**能从 Runtime 直接采集的证据，不让 Agent 自己总结。**

## 最终状态不应该只有 Success / Failed

如果一个 Agent 确实完成了任务，但没有足够 Evidence 怎么办？

我不认为应该简单判 Fail。

但也绝对不能直接当作可信 Success。

更合理的是：

SUCCESS_VERIFIED

SUCCESS_UNVERIFIED

FAILED

BLOCKED

INCONCLUSIVE

其中我最喜欢的是：

**UNVERIFIED。**

因为它把一件过去很模糊的事情说清楚了：

> 结果可能是对的，但系统没有足够证据证明它。

这对 Agent 非常重要。

## Evidence 必须绑定真实状态

测试结果不是永久有效的。

例如：

pytest 在 Commit A 上通过。

随后 Agent 又修改了一次代码，变成 Commit B。

那么 Commit A 的 Test Evidence 已经不能继续证明 Commit B。

所以 Evidence 至少应该绑定：

Run ID、Commit SHA、Environment、Timestamp、Artifact Hash。

这意味着 Evidence 不是“附件”。

它是执行状态的一部分。

## 再往下一步，就是独立 Verification

Agent 产生：

Result + Evidence。

然后交给独立 Verifier：

Deterministic Check、Test Runner、Schema Validator、Policy Engine，必要时再用独立 Model Judge。

最终才得到：

VERIFIED / UNVERIFIED / FAILED。

这里有一个我认为非常重要的原则：

> **能程序判断的，不交给 LLM Judge。**

Exit Code 是 0 还是 1，不需要模型判断。

文件存不存在，不需要模型判断。

有没有调用 Forbidden Tool，也不需要模型判断。

模型应该负责那些真正需要语义判断的部分。

## 为什么我觉得 Evidence Contract 会成为 Agent Reliability 的基础设施

因为有了 Evidence，很多东西才开始连起来：

Harness 留下执行事实。

Evidence 证明结果。

Verification 判断事实是否支持结论。

真实 Failure 进入 Regression。

Regression 结果进入 Quality Gate。

最后系统才能真正决定：

> 这个 Agent 的结果能不能 Merge？能不能 Release？能不能进入下一业务步骤？

所以我现在越来越觉得：

Agent Reliability 最重要的一次升级，不是：

**让 Agent 更会说“我完成了”。**

而是：

**让系统不再需要相信它自己说“完成了”。**

Agent 可以做任务。

但证明任务完成，应该成为系统能力。
