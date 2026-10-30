---
related_posts:
  - /harness/agent-evidence-contract/
  - /harness/verification-loops-and-budget-exhaustion/
  - /eval/agent-trace-grading/
layout: post
title: "Agent 验证报告不能只写 PASS：把结果绑定到代码、模型与 Skill 快照"
description: "从 Qwen Code Verify PR 的轮次快照与版本溯源变更出发，设计可追溯、可复核的 Agent 验证报告契约。"
date: 2026-10-30 10:00:00 +0800
updated: 2026-10-30 10:00:00 +0800
last_modified_at: 2026-10-30 10:00:00 +0800
categories: [Agent-Harness, Agent-Reliability, Trace-Evidence, Failure-Regression]
permalink: /harness/verification-report-provenance/
tags: [agent-harness, agent-reliability, trace-evidence, failure-regression, quality-gate]
series: agent-harness
series_order: 18
---

一份 Agent 验证报告写着 <code>PASS</code>，并不意味着它已经具备交付价值。

至少还要回答三个问题：它检查的是哪个代码版本？执行验证时使用了哪个模型、CLI 和 Skill？这份报告属于哪一轮执行？

如果这些信息没有绑定在一起，报告就可能出现两种问题：代码已经变化，旧报告仍被当成当前结果；或者模型、CLI、Skill 已经变化，却无法判断前后两次验证是否使用了相同的方法。

2026 年 10 月 29 日，Qwen Code v0.26.4 的发布记录出现了两项值得关注的 Verify PR 变化：验证报告绑定到各自轮次的代码快照，以及发布报告时标记模型、CLI 和 Skill 版本。[官方 Release](https://github.com/QwenLM/qwen-code/releases/tag/v0.26.4)

这不是完整的可靠性方案，但它把一个容易被忽略的问题推到了台前：**验证报告本身也需要身份和来源。**

## 一、PASS 不是一份完整的验证证据

假设一个 Agent 对 PR 执行了验证，评论里只留下：

~~~text
Verification passed.
~~~

这句话没有说明：

- 检查的是 PR 当前 HEAD，还是更早的提交；
- 使用的是哪个模型和 CLI 版本；
- 加载的是哪一版 Skill；
- 这是首次验证，还是针对修复后的增量复验；
- 报告中的证据究竟属于哪一轮。

只要 PR 在验证后又发生提交，或者 Skill 在两轮之间更新，原来的 <code>PASS</code> 就可能失去适用范围。

这里有两个不同的问题。

**目标漂移**：报告检查的代码版本与当前代码版本不一致。

**方法漂移**：报告由不同模型、CLI 或 Skill 生成，却没有留下足够的版本信息。

它们都可能让一份表面正常的报告被错误复用。

## 二、Qwen Code 这次具体补了什么

Qwen Code v0.26.4 于 10 月 29 日发布。Release Notes 中有三项变化与验证链路直接相关：

1. <code>verify-pr</code> 发布报告时附带模型、CLI 和 Skill 版本；
2. 验证报告绑定到本轮执行的代码快照；
3. 将“更新后重新验证”作为明确的 follow-up 触发方式，而不是把它当作一轮全新的验证。

对应实现可以从三个 PR 继续核对：

- [PR #15838：发布报告增加模型、CLI 和 Skill 版本标识](https://github.com/QwenLM/qwen-code/pull/15838)
- [PR #15746：报告绑定到本轮快照](https://github.com/QwenLM/qwen-code/pull/15746)
- [PR #15816：更新后的重新验证触发机制](https://github.com/QwenLM/qwen-code/pull/15816)

其中，PR #15746 处理的是一个具体的快照覆盖问题：同一个 PR 准备了新一轮验证后，如果所有轮次共用一份可变快照，后续准备可能覆盖前一轮的代码身份，导致旧报告被拿去和错误的 HEAD 比较。

修复后，新准备的轮次绑定自己的 HEAD 身份。旧报告再次检查时，仍然使用它自己的快照；如果轮次快照不可读或无效，则明确告警，不静默借用后续轮次的 HEAD。没有独立快照的历史报告仍保留共享元数据回退路径，并显示实际来源。

PR #15838 则补充了验证方法的来源信息。发布评论会标记本轮使用的模型、Qwen Code 版本和 Skill 内容哈希。值得注意的是，这些值由 Workflow 自己收集，而不是从 Agent 可以修改的报告产物目录中读取。

Skill 使用内容哈希而不是只引用 Git commit，是因为浅克隆或本地未提交修改场景下，提交号不一定能准确表示本轮实际加载的指令内容。

这两项变化分别解决了目标身份和方法身份问题。

## 三、验证报告至少要绑定三类身份

结合上述实现，可以把验证报告的身份拆成三层。

### 1. 目标身份：这轮到底检查了什么

最少需要：

- 仓库标识；
- 目标分支或 PR；
- 被验证的 HEAD SHA；
- 验证范围。

HEAD SHA 是最关键的目标身份。没有它，<code>PASS</code> 只能说明“某个版本通过了”，不能说明当前代码通过了。

### 2. 方法身份：这轮是怎么验证的

建议记录：

- 模型标识；
- Agent CLI 版本；
- Harness 版本；
- Skill 内容哈希；
- 关键验证策略或配置版本。

模型、CLI 和 Skill 都可能改变执行结果。尤其是 Skill，它定义了 Agent 如何理解任务、选择步骤和执行验证。只记录模型名称，并不能说明验证方法保持不变。

Qwen Code 的做法值得注意：由 Workflow 收集这些信息，而不是相信 Agent 在报告正文里自报版本。报告内容可以由 Agent 生成，但决定报告来源的元数据应来自可信执行环境。

### 3. 执行身份：这份报告属于哪一轮

建议为每轮验证生成独立的 <code>round_id</code>，并关联：

- 开始和结束时间；
- 执行环境；
- 测试集或验证规则版本；
- 本轮输入和变更范围；
- 原始 Trace、日志、截图和其他证据引用；
- 本轮判定及未覆盖项。

下面是一个建议的数据结构。它是用于说明 Evidence Contract 的设计示例，不代表 Qwen Code 已经实现了所有字段：

~~~json
{
  "round_id": "verify-<unique-id>",
  "target": {
    "repository": "org/repo",
    "head_sha": "<commit-sha>"
  },
  "executor": {
    "model": "<model-id>",
    "cli_version": "<version>",
    "harness_version": "<version>",
    "skill_hash": "<content-hash>"
  },
  "scope": {
    "suite_version": "<suite-version>",
    "environment": "<environment-id>"
  },
  "result": {
    "verdict": "PASS",
    "evidence_refs": [
      "trace://<trace-id>",
      "artifact://<artifact-id>"
    ]
  }
}
~~~

三类身份要一起保存。只保存目标 HEAD，无法解释验证方法是否变化；只保存模型和 Skill，也无法说明它们验证的是哪一版代码。

## 四、来源元数据不能让 Agent 自己填写

如果 Agent 可以修改验证报告产物，那么它也可能修改报告里的版本声明。

例如，报告正文写着：

~~~text
model: model-A
skill_version: v1
~~~

但实际执行使用的是 model-B 和 Skill v2。若发布系统直接信任这段文本，版本信息就失去了审计意义。

更可靠的方式是把来源信息分成两类：

| 信息 | 推荐来源 |
| --- | --- |
| 本轮目标 HEAD | Git / PR 运行环境 |
| 模型标识 | Workflow 配置或实际请求元数据 |
| CLI 版本 | Runner 安装信息 |
| Skill 内容哈希 | 实际加载的 Skill 文件内容 |
| Harness 版本 | 执行环境构建信息 |
| 测试结果 | 验证器输出 |
| 原始证据 | Trace / Artifact 存储 |

Agent 可以提交验证结果，但不能单方面决定“自己到底运行了哪个版本”。

Qwen Code PR #15838 的实现也考虑了元数据缺失：模型、CLI 或 Skill 标识不完整时，发布评论会退回通用签名，不会伪造一个看似完整的来源信息，也不会因为署名采集失败就修改验证判定。

这是一种值得保留的边界：**来源不完整应降低报告的可追溯性，而不是篡改原始验证结论。**

## 五、重新验证应该围绕代码变化，而不是重复启动

报告绑定轮次快照之后，follow-up 才有可靠的比较基础。

Qwen Code PR #15816 将“更新后重新验证”做成明确的后续触发：先找到上一轮实质验证对应的 HEAD，再检查 PR 的 HEAD 是否真的变化。若只是评论或 CI 状态变化，并没有新的代码提交，就不必直接消耗一轮完整验证。

当 HEAD 发生变化时，再沿用之前的验证坐标，保留已有 finding 状态，并对修复后的变化做增量复核。

这与简单地重新启动 Agent 不同：

~~~text
上一轮验证
    ↓
保存 HEAD + 方法版本 + Findings
    ↓
收到“更新后重新验证”
    ↓
检查 HEAD 是否变化
    ├── 未变化：不启动新一轮
    └── 已变化：创建新 round
                    ↓
              比较 Findings Delta
                    ↓
              生成新报告
~~~

它也与预算管理有关。v0.26.4 同时增加了有界 takeover 轮次预算。对应 PR #15388 明确规定，失败、超时和崩溃的轮次同样消耗预算，因此 N 表示最多尝试 N 次，而不是必须成功 N 次。

这让系统有机会同时回答两个问题：本轮是否产生了新的验证证据，以及继续执行是否仍在预算范围内。

## 六、Quality Gate 应检查报告是否仍然适用

当验证报告开始携带明确身份，Merge Gate 就不应该只读取 <code>verdict == PASS</code>。

至少还应检查：

1. 报告中的 HEAD 是否等于当前待合并 HEAD；
2. 模型、CLI、Harness 和 Skill 版本是否完整；
3. 报告是否属于当前 PR 和当前验证轮次；
4. 关键 Evidence 引用是否仍可读取；
5. 报告是否覆盖本次变更要求的验证范围；
6. 是否存在尚未处理的高风险 finding。

可以把结果拆成不同状态：

| 状态 | 含义 | Gate 动作 |
| --- | --- | --- |
| <code>VERIFIED</code> | 目标版本、验证方法和证据均满足契约 | 允许按策略继续 |
| <code>STALE</code> | 报告检查的 HEAD 已变化 | 要求重新验证 |
| <code>UNATTRIBUTED</code> | 模型、CLI 或 Skill 来源不完整 | 降级或要求补证 |
| <code>INCOMPLETE</code> | 必要验证范围或证据缺失 | 不得视为通过 |
| <code>FAILED</code> | 存在未通过的验证判据 | 按风险规则阻断 |

这只是建议的状态模型，不是 Qwen Code 的实际状态枚举。具体系统可以采用不同名称，但不能把“报告过期”“来源不明”和“验证失败”混成一个 PASS/FAIL。

## 七、这套设计仍然不能证明业务正确

版本和快照溯源解决的是“这份报告到底对应什么”，不是“这份报告的判断一定正确”。

即使代码 HEAD、模型、CLI 和 Skill 都完全一致，Agent 仍可能遗漏需求、错误解释业务规则，或者使用了不充分的测试集。外部数据、权限配置和运行环境也可能变化。

还需要注意公开 PR 的验证边界：

- PR #15838 描述的发布测试使用了 Stubbed Comments API，没有执行真实沙箱验证轮次；
- PR #15746 报告了聚焦测试和独立 CLI 复现通过，但其描述也明确说明全工作区测试存在未修改套件的超时和失败，不能把它包装成全量测试无条件通过。

因此，这些变化证明的是项目正在补强报告来源和轮次快照机制，不等于已经证明整个 Verify PR 流程在所有生产环境下可靠。

## 八、可以从一条真实验证链路开始

如果要在现有 Harness × Eval 流程中验证这套设计，不需要先改造全部执行引擎。

可以先选一条已有的 Agent 验证链路，做一个最小闭环：

1. 每轮开始时保存目标代码 SHA、模型、CLI 和 Skill 内容哈希；
2. 将本轮元数据写入独立的 round snapshot，不与其他轮次共享可变文件；
3. 验证报告引用该 snapshot 和原始 Evidence；
4. 发布或进入 Gate 前，重新检查当前代码 HEAD 是否与报告一致；
5. 如果代码发生变化，创建新轮次并比较 Finding Delta；
6. 对缺少来源或证据的报告明确降级，不自动补成完整结论。

第一阶段只需要观察三个问题：旧报告会不会被新轮次覆盖、代码变化后旧 PASS 会不会继续被复用、模型或 Skill 变化后能不能识别方法漂移。

如果这三个问题都能被系统明确回答，验证报告才开始从一段自然语言总结，变成真正可用于交付判断的工程证据。

## 结语

Agent 验证的结果，不应该只是一句“通过了”。

它必须说明检查的是哪个版本、使用了什么方法、属于哪一轮执行，以及支持结论的证据在哪里。

代码快照解决目标身份，模型和 Skill 版本解决方法身份，独立轮次快照解决报告归属。它们不能替代业务 Eval，却能防止一份旧报告被错误地当成新证据。

**验证报告不只是记录结论，它还必须证明这个结论属于哪一次执行。**

## 参考资料

- [Qwen Code v0.26.4 Release Notes（2026-10-29）](https://github.com/QwenLM/qwen-code/releases/tag/v0.26.4)
- [PR #15746：Bind reports to their round snapshot](https://github.com/QwenLM/qwen-code/pull/15746)
- [PR #15838：Stamp model, CLI and Skill version on published reports](https://github.com/QwenLM/qwen-code/pull/15838)
- [PR #15816：Make re-verify after update a follow-up trigger](https://github.com/QwenLM/qwen-code/pull/15816)
- [PR #15388：Bound autofix takeover with a round budget](https://github.com/QwenLM/qwen-code/pull/15388)
- [结果正确就够了吗？给 Agent 设计 Evidence Contract](https://hugfeature.github.io/harness/agent-evidence-contract/)
- [Harness 什么时候开始为了验证而验证？](https://hugfeature.github.io/harness/verification-loops-and-budget-exhaustion/)
