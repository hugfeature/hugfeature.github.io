---
layout: post
title: "Agent 最危险的不是失败，而是“最终通过，但过程已经失控”"
date: 2026-09-21 21:00:00 +0800
categories: [Agent-Reliability, AI-Testing]
---

很多团队评估 Agent，最后都会落到一个最简单的问题：

> 任务完成了吗？

代码是否通过测试，页面是否操作成功，报告是否生成，目标是否达成。

这个指标当然重要，但它正在变得不够用了。

因为对长链路 Agent 来说，**最终结果正确，不代表执行过程可靠**。一个 Agent 完全可能在中间走错路、破坏环境、制造错误数据，最后又绕回来得到一个“通过”的结果。

如果我们只看最终结果，这些问题几乎都是隐形的。

## 一项值得警惕的新研究

2026 年 9 月发布的论文 [Locating Hidden Failures Makes Long-Horizon Agents More Reliable](https://arxiv.org/abs/2609.17930) 对这个问题做了一次很有价值的拆解。

研究者分析了 **2,518 条 Agent 执行轨迹**，覆盖软件工程、Computer Use 和科学任务，并人工标注出 **6,967 个错误、78 类失败模式**。

最值得关注的不是 Agent 会犯错，而是它犯错之后发生了什么。

研究发现，一个 Agent 出现第一次错误之后，经常无法真正恢复，而且很少能够主动发现自己的错误。任务仍然会继续执行，于是错误被一路带到后面的步骤。

更麻烦的是，一些最终被判定为 solved 的任务，在执行过程中依然可能出现：

- 删除数据
- 破坏系统状态
- 伪造成功
- 通过错误路径“碰巧”得到正确结果

也就是说：

**Pass ≠ Reliable。**

论文进一步测试了 6 个前沿模型作为 judge，让它们判断一条 Agent trajectory 的第一次错误出现在哪里。即使表现最好的 judge，也只能在不到三分之一的运行中正确定位第一次错误。

这说明一个现实问题：

**当 Agent 的任务越来越长，仅靠最终结果和一次 LLM Judge，已经不足以承担可靠性判断。**

## 我们过去的测试逻辑正在失效

传统自动化测试天然偏向最终状态：

输入 → 执行 → Assert → Pass / Fail。

对于 API、函数或者相对确定的软件流程，这套模型非常有效。

但 Agent 的执行更像：

Goal  
→ Plan  
→ Tool Call  
→ Observation  
→ Re-plan  
→ Retry  
→ Side Effect  
→ Final Result

它不是一次调用，而是一条 trajectory。

这意味着测试对象已经发生变化。

过去我们测试的是：

**结果是否正确。**

现在需要测试的是：

**这个结果是怎么得到的。**

如果仍然只保留最终 Assert，就会出现一种很危险的情况：

Agent 已经偏离目标、错误调用工具、污染环境甚至产生副作用，但只要最后结果碰巧满足断言，整条执行链仍然显示为绿色。

绿色，不再等于健康。

## Agent Reliability 至少需要五层判断

我更倾向于把 Agent 的质量标准从单一的“任务成功率”，升级成五层：

**结果正确 + 过程可解释 + 副作用可控 + 失败可回归 + 发布可阻断**

第一层仍然是 Outcome。

任务最终有没有完成，这是底线。

第二层是 Trace。

Agent 调用了什么工具、读取了什么证据、在哪一步改变了计划、发生过几次 Retry，这些过程必须可以被重建。

第三层是 Evidence。

不是“Agent 说自己完成了”，而是它必须拿出能够证明完成的证据。

例如代码 Agent 不能只返回“测试已通过”，而应该关联真实测试结果、修改文件、执行日志和环境状态。

第四层是 Failure Regression。

一次失败如果只能靠人工看日志解决，那么它只是一次事故。

真正有价值的是把失败沉淀成：

**Failure → Corpus → Regression Case**

以后 Agent、Prompt、Skill、Model 或 Harness 发生变化，都重新验证这个失败是否再次出现。

第五层是 Quality Gate。

如果 Trace 缺失、关键 Evidence 不足、出现高风险副作用或者命中已知 Failure Pattern，即使最终任务通过，也应该能够阻止 Merge 或 Release。

到这里，AI 测试才真正从“评测一个回答”进入“控制一个执行系统”。

## Harness 才是 Reliability 真正发生的地方

很多 Agent 优化最后都会落到 Prompt。

Agent 不稳定，就改 Prompt；工具调用错误，就再加一句约束；输出不符合格式，就继续补规则。

这些手段当然有用，但它解决不了长链路系统的根本问题。

因为真正的 Reliability 不应该依赖 Agent 自己承诺“我会做对”。

它应该由 Agent 外部的 Harness 提供。

Harness 至少应该知道：

**Agent 想完成什么、实际做了什么、依据是什么、改变了什么、失败发生在哪里，以及最终结果是否值得信任。**

这也是为什么 Trace、Evaluator、Failure Corpus 和 Quality Gate 不应该是四套独立系统。

它们其实是一条链：

**Change → Agent → Harness → Trace → Verification → Failure / Root Cause → Regression → Quality Gate**

Trace 负责留下事实。

Verification 判断事实是否支持结果。

Failure 把异常结构化。

Regression 保证问题不会回来。

Quality Gate 最终决定这个结果能不能进入下一阶段。

这条链一旦跑通，Agent Reliability 才开始变成工程能力，而不是模型调参经验。

## 真正值得优化的指标，也许不是 Success Rate

Success Rate 当然还要看。

但对于一个逐渐进入真实研发流程的 Agent，我更关心另外几个问题：

第一次错误发生在哪里？

Agent 有没有意识到自己错了？

错误之后有没有恢复？

恢复花了多少额外步骤？

有没有产生不可逆副作用？

最终 Pass 是否有独立 Evidence 支撑？

同类 Failure 下一版本还会不会再次出现？

这些指标比单纯的“成功率从 82% 提升到 87%”更接近工程现实。

因为一个成功率略低、但失败可定位、可恢复、可回归的 Agent，往往比一个成功率很高、但失败完全不可观察的 Agent 更容易进入生产系统。

## 结语

Agent 最危险的状态，不一定是明确失败。

明确失败至少会触发处理。

真正麻烦的是：

**任务显示通过了，但执行过程已经失控，而系统没有任何机制发现它。**

这也是我理解的 Agent Reliability 的核心问题。

我们最终需要建立的，不只是一个更聪明的 Agent，而是一套即使 Agent 会犯错，也能够发现、定位、恢复、回归并阻断风险的工程系统。

当这一套能力建立起来之后，所谓 AI Testing 才真正从“验证模型输出”，走向了“保障 Agent Runtime”。

---

## 参考

1. Salman Rahman et al. [Locating Hidden Failures Makes Long-Horizon Agents More Reliable](https://arxiv.org/abs/2609.17930), 2026.
2. Aagam Sogani et al. [When Web Agents Finish but Still Fail: Reproducible Triggers and Trace Diagnostics for Parallel Web Exploration](https://arxiv.org/abs/2606.20724), 2026.
