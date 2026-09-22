---
title: "Agent 真正危险的不是不会做，而是“能做，但没人管”"
channel: wechat
status: ready
source: /harness/why-agent-needs-harness/
---

# Agent 真正危险的不是不会做，而是“能做，但没人管”

做 Agent 时，我们很容易形成一种思路：

Agent 不稳定，就继续改 Prompt。

于是 System Prompt 越来越长：

修改文件前先读文件。

删除之前必须确认。

失败以后最多重试三次。

任务完成后必须执行测试。

不要访问 production。

不要重复调用同一个工具。

这些规则有没有用？

当然有。

但问题是：

**Prompt 只能告诉模型“应该怎么做”，不能决定系统“允许发生什么”。**

这两个概念一旦混在一起，Agent 越强，风险反而越大。

## 模型说“我要删除”，谁来决定真的删不删？

假设 Prompt 中明确写着：

> 不允许删除 production 数据。

但 Tool 里依然暴露着：

delete_database("prod")

如果 Runtime 没有任何检查，那么最终权限其实仍然掌握在模型手里。

模型只要一次判断错误，这条规则就失效了。

真正可靠的结构应该是：

Model → Proposed Action → Harness Policy → ALLOW / DENY / REQUIRE APPROVAL。

这就是我现在理解 Harness 最核心的一句话：

> **Model proposes. Harness enforces.**

模型负责提出下一步。

系统负责决定这一步到底能不能发生。

## Retry 也不是一句“再试一次”

例如 Agent 调用了：

send_payment()

然后请求 Timeout。

最直觉的处理是什么？

再试一次。

但第一次到底有没有支付成功？

如果实际上成功了，只是响应没有回来，第二次 Retry 就可能重复支付。

所以真正的 Retry 不是 Prompt 里的：

> 如果失败，请重试。

而是 Runtime 需要知道：

这个 Tool 是 Read 还是 Write？

是否幂等？

是否产生 Side Effect？

这个错误是 Transient、Permanent，还是“状态未知”？

状态未知时，是应该 Retry，还是先 Verify？

Reliability 的核心不是：

**出错以后继续跑。**

而是：

**知道什么时候绝对不能继续跑。**

## Budget 也应该在模型之外

长任务 Agent 很容易遇到：

重复搜索、重复 Tool Call、Rabbit Hole、Reasoning Loop。

如果只写一句：

> 请尽可能少调用工具。

约束其实很弱。

Harness 可以真正维护：

max turns、max tool calls、max retry、max wall time、max cost、max write actions。

一旦越界，Runtime 直接停止。

这时候 Budget 不只是成本控制。

它本质上也是：

**失控保护。**

## Agent 说“完成”，系统为什么要相信？

Coding Agent 很典型。

Agent 最终回答：

> Bug 已修复，测试全部通过。

很多系统到这里就结束了。

但真正值得问的是：

**证据呢？**

系统有没有真实保存：

Git diff？

Changed files？

Test command？

Exit code？

Test report？

如果都没有，那系统拿到的其实只是：

**Agent 的自我报告。**

这也是为什么我越来越认为 Harness 不应该只负责执行。

它还应该负责把真实执行证据留下来。

最终状态不应该只有：

SUCCESS / FAILED。

还应该有：

SUCCESS_VERIFIED、SUCCESS_UNVERIFIED、BLOCKED、INCONCLUSIVE。

“不知道是否真的完成”，不能被自动翻译成“完成”。

## Trace 也不是多打一堆日志

传统日志告诉我们：

系统有没有 Error。

Agent Trace 更应该回答：

Agent 为什么走到这里？

它当时看到了什么？

调用了什么 Tool？

Tool 返回了什么？

真实状态发生了什么变化？

哪一步开始偏离？

最后的 PASS 到底有没有独立 Evidence？

只有这些信息存在，失败才有可能进入下一步：

Failure → Root Cause → Regression。

否则，每一次 Agent 事故都只能重新人工翻日志。

## Harness 的价值会越来越大，而不是越来越小

很多人会想：

模型越来越强以后，是不是 Harness 就没那么重要了？

我反而认为相反。

模型从：

生成文本

变成：

修改代码、执行命令、操作浏览器、调用企业 API、创建数据、部署系统。

模型能力越强，它能够改变真实世界的范围就越大。

这时候真正需要保证的，不再只是：

> 它聪不聪明？

而是：

> **系统有没有能力控制它做什么、证明它做对了，以及在它做错时及时阻断。**

所以 Harness 最终不是一个 Agent Framework 的新名词。

它是 Agent 从 Demo 进入真实生产系统以后，必然出现的一层工程边界。

模型负责做决定。

**系统必须负责承担后果。**
