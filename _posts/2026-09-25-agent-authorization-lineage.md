---
layout: post
title: "用户授权了 Agent，为什么它仍然没有权力执行？"
date: 2026-09-25 10:00:00 +0800
description: "Agent 的权限不是一个布尔值。真正可靠的 Harness，需要把用户、Agent、工具、目标系统和副作用连成可验证的授权链。"
tags: [Agent Reliability, Agent Harness, Trace, Evidence, Security, Quality Gate]
---

Agent 能调用工具，不代表它有权执行这次动作。

这是很多 Agent 系统正在混淆的两件事：**能力表示“能不能做”，授权表示“这一次凭什么做”。** 当 Agent 只能生成文本时，这个区别还不明显；当它开始读取代码库、发送邮件、审批单据、修改 ERP 数据甚至代表用户购物时，授权就变成了运行时可靠性的核心边界。

近期几件事把这个问题集中暴露了出来。

Meta Muse 的 macOS 客户端被发现存在一个可被本地进程修改的隐藏配置。攻击者可以改变转写端点、获得会话令牌，并借助 Muse 已经取得的文件、消息、日历等权限执行动作。Amazon 随后又阻止 Muse 访问其购物平台，争议并不是 Muse “做不到”，而是它没有以平台认可的方式标识和授权自己。另一边，ZCode 因默认代码库索引引发数据上传争议，也说明 Agent 的副作用不只有“改文件”，还包括索引、缓存、遥测和数据外发。

这些事件看起来分别属于客户端安全、平台政策和隐私问题，底层却是同一个工程缺口：**系统只有权限开关，没有授权链。**

## 一次“允许”为什么不够

传统应用通常把权限理解为静态配置：用户登录了、授予了文件访问权、配置了 API Token，之后应用就可以持续工作。

Agent 不一样。它会动态规划、选择工具、重试、切换路径、恢复历史任务，还可能把一个系统的数据带到另一个系统。执行路径不是开发者预先写死的，权限的使用方式也随每一步决策变化。

因此，一次授权至少回答不了下面这些问题：

- 这次动作是谁发起的：用户、Agent，还是恢复后的后台任务？
- Agent 当前执行的目标，是否仍然等于用户最初批准的目标？
- 使用的是谁的凭据，权限范围是否超出任务需要？
- 目标系统是否允许第三方 Agent 代表用户操作？
- 这次读取、索引、上传、修改产生了哪些副作用？
- 失败、重试或恢复后，旧授权是否仍然有效？

如果 Trace 只能回答“调用了哪个工具”，它还不能成为交付证据。

## 授权不是一个点，而是一条链

更可靠的设计，是把每次高风险动作表示为一条 Authorization Lineage：

```text
用户意图
  → Agent 身份与版本
  → 当前任务 / 当前步骤
  → 使用的 Skill / Tool / MCP
  → 凭据主体与权限范围
  → 目标系统策略
  → 实际副作用
  → 独立验证结果
```

这条链里任何一段缺失，都不应该自动推导出“允许执行”。

例如，在 ERP 场景中，用户说“帮我处理这批采购申请”，不能直接等价为“允许 Agent 审批全部申请”。Harness 至少需要进一步知道：用户是否拥有审批权、Agent 是否被允许代理审批、金额和组织范围是什么、目标系统是否接受 Agent 身份、写入前是否需要人工确认，以及写入后如何验证实际生效对象。

这不是为了给流程增加更多弹窗，而是把原本隐含在人员经验、系统配置和审批规则里的判断，变成机器可检查的执行契约。

## Harness 最少要保存哪些证据

我建议把授权证据拆成五组，而不是只记录一个 `permission_granted=true`。

第一组是**主体证据**：用户是谁，Agent、Skill、模型和 Harness 分别是什么版本，最终使用了哪个服务账号或用户凭据。

第二组是**意图证据**：原始任务、允许的资源范围、有效时间、预算，以及是否允许写操作、外发数据和跨系统调用。

第三组是**策略证据**：执行前命中了哪些规则，规则版本是什么，哪些条件通过，是否发生过人工审批或二次确认。

第四组是**动作与副作用证据**：读取、写入、删除、索引、上传、通知等实际发生了什么，而不是只保存 Agent 自己生成的总结。

第五组是**验证证据**：由独立验证器确认目标对象、变更结果和未授权副作用，并给出 VERIFIED、REJECTED 或 UNVERIFIED，而不是让执行 Agent 自证完成。

这些字段可以压缩成一个最小动作记录：

```json
{
  "actor": "agent:test-case-agent@1.4.2",
  "on_behalf_of": "user:1234",
  "task_id": "TASK-2026-0925",
  "action": "erp.purchase_request.update",
  "resource_scope": ["org:CN-01", "amount<=5000"],
  "credential_subject": "service-account:erp-agent",
  "policy_version": "erp-write-policy@3.1",
  "decision": "require_approval",
  "side_effects": [],
  "evidence_refs": ["trace://run/step-18", "approval://AP-8842"]
}
```

具体字段可以因系统而变，但核心关系不能丢：**谁，代表谁，在什么任务下，依据哪条策略，对哪个对象，产生了什么结果。**

## Retry 和恢复为什么特别危险

很多系统在首次执行前做了审批，却在 Retry、Fallback 或 Resume 时直接沿用旧授权。这在长任务里很危险。

重试可能改变参数，Fallback 可能切换工具或目标端点，恢复可能发生在数小时后、由另一个 Agent 版本接管。即使业务目标没有变化，执行主体、环境和风险都可能已经变化。

因此，checkpoint 不应只保存“任务做到哪一步”，还要保存授权上下文；恢复时也不能只检查状态是否完整，而应重新评估：凭据是否过期、策略是否更新、资源范围是否漂移、接管者是否仍满足原审批条件。

**可恢复不等于可继承权限。** 这是 Agent Continuity 和 Agent Security 必须分开设计、再在 Harness 中汇合的地方。

## 从权限控制走向交付 Gate

授权链最终不是为了生成更漂亮的审计日志，而是为了影响执行和交付。

一个可落地的 Gate 可以先从四条规则开始：

1. 高风险写操作没有完整主体和意图证据，不执行。
2. 实际资源范围超出授权范围，立即阻断并保留 Trace。
3. Retry、Fallback 或 Resume 改变主体、工具或目标端点，重新做策略判定。
4. 动作完成但副作用无法独立验证，标记为 UNVERIFIED，不进入后续交付。

这样，Trace 才从“发生过什么”升级为“为什么允许发生”，Evidence Contract 也从结果证明扩展到权限证明。

## 结语

Agent Reliability 不能只检查任务有没有完成。越是能代表用户行动的 Agent，越需要证明自己的每一步权力从哪里来。

未来企业 Agent 的核心边界，不只是模型、Prompt 或 Tool，而是贯穿整个执行过程的授权链：身份可识别、意图有范围、策略可复现、副作用可追踪、结果可验证。

只有这条链完整，Agent 的“我可以做”才有资格变成系统的“允许它做”。

## 参考资料

- [Un-Mused: How a Single Debug Setting Bypassed macOS Security in Meta’s AI Client](https://www.infoq.com/news/2026/09/meta-muse-zeroday/)
- [Amazon blocks Meta’s Muse AI agent](https://www.theverge.com/tech/998078/amazon-blocks-meta-muse-ai-agent-shopping)
- [Z.ai disables AI coding assistant features after security issue](https://indianexpress.com/article/technology/artificial-intelligence/chinas-z-ai-disables-ai-coding-assistant-features-after-security-issue-10888434/)
- [Koi Agentic Endpoint Security](https://www.paloaltonetworks.com/resources/techbriefs/koi-agentic-endpoint-security)
