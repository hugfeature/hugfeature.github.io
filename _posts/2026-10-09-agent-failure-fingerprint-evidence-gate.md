---
layout: post
title: "Agent 反复验证却没有收敛：给 Harness 加上失败指纹与证据增量门禁"
date: 2026-10-09 10:00:00 +0800
description: "用失败指纹、证据增量和停止条件判断 Agent 重试是否产生有效进展。"
tags: [agent-harness, agent-reliability, trace-evidence, failure-regression, quality-gate]
---

> 建议归入：Agent Harness / Agent Reliability / Trace & Evidence / Failure Regression / Quality Gate

## 不是所有重试都在推进问题

Agent 工作流失败后，最直觉的处理通常是再跑一次：增加轮次、增加预算、再启动一个验证 Agent，或者把同一组检查完整执行一遍。

但“又执行了一轮”不等于“离解决更近了一步”。

最近一次多 Agent 工作流验证中，我把预算从 4 轮增加到 8 轮，结果仍然是同样 4 项失败。这个观察只能说明：在当时那组输入、环境和策略下，增加轮次没有改变结果。它不能单独证明具体根因，也不能证明所有增加预算的做法都无效。

真正需要追问的是：第 5 到第 8 轮带来了什么新信息？失败位置变了吗？错误类型变了吗？执行真的走到了不同阶段吗？如果答案都是否定的，更多轮次只是把同一个失败复制了四次。

公开项目里也能看到类似现象。DeepSeek Harness 的一条社区问题报告显示，auto-review 因缺少会话 Header，在工具执行前就拒绝全部调用；复现记录里出现了 21 次同类失败。切换模型没有解决，因为根因不在业务工具或模型能力，而在审批请求的上下文传递。[问题报告](https://github.com/deepseek-ai/deepseek-harness/discussions/8726)

这类问题提醒我们：Harness 不仅要会重试，还要知道**重试是否可能产生新证据**。

## 一、先区分“重复失败”和“新的失败”

如果每次失败都只保存一段自然语言日志，系统很难判断两轮失败是否相同。

可以先给失败建立一个最小指纹：

```json
{
  "stage": "approval",
  "component": "auto-review",
  "error_code": "MissingSessionID",
  "normalized_message": "request missing session routing header",
  "tool_executed": false,
  "environment": "windows/dsh-0.2.0-rc.2",
  "config_version": "permission-auto/v1",
  "evidence_refs": ["trace:event-184", "log:reviewer-400"]
}
```

字段不必一次设计得很复杂，关键是能够回答五个问题：

1. 失败发生在哪个阶段？
2. 哪个组件首先产生了可观察错误？
3. 业务动作是否真的执行？
4. 本轮环境和策略与上一轮有什么不同？
5. 支持结论的原始证据在哪里？

两轮失败的指纹相同，不代表根因已经确定；但它足以触发一个重要判断：继续按原样执行，大概率不会增加信息。

## 二、轮次增加之前，先检查证据增量

一次重试值得执行，至少应该满足下面一项：

- 输入发生了变化，例如补充了缺失规则或新的测试数据；
- 实现发生了变化，例如修复了审批 Header 或工具参数；
- 环境发生了变化，例如切换了运行时版本或权限配置；
- 验证策略发生了变化，例如从端到端复跑改为最小复现；
- 可观测性发生了变化，例如新增原始事件、网络请求或状态快照。

可以把这些变化记为 `change_set`。如果新一轮没有 `change_set`，失败指纹也没有变化，Harness 就不应把它标记为“继续修复”，更准确的状态是：

```text
NO_PROGRESS
reason: same_failure_fingerprint
evidence_delta: 0
next_action: root_cause_investigation
```

这里的 `evidence_delta: 0` 不需要一开始就做成复杂分数。最简单的实现，是比较本轮是否新增了能够缩小根因范围的证据引用。

例如，同样是工具调用失败：

- 只多了一段相同的 400 日志，没有证据增量；
- 新增了请求抓包，确认 Header 未注入，有证据增量；
- 修复 Header 后错误从审批阶段移动到工具执行阶段，失败指纹发生变化；
- 工具执行成功，但业务断言失败，说明系统进入了新的诊断阶段。

“仍然失败”并不等于“没有进展”。关键是失败是否变得更具体、更靠近真正的业务验证。

## 三、不要让低层通过冒充高层成功

验证不收敛的另一种形式，是不断证明已经证明过的事情。

以移动端功能为例，可以把证据拆成一条阶梯：

| 层级 | 能证明什么 | 不能证明什么 |
| --- | --- | --- |
| Build | 代码能够生成 APK | APK 能安装、启动或完成业务功能 |
| Install | APK 能安装到目标设备 | 应用运行正确 |
| Launch | 应用能启动并进入目标页面 | 关键交互和后台行为正确 |
| Interaction | 指定操作产生预期前台结果 | 锁屏、后台、系统权限场景正确 |
| Real scenario | 在目标设备状态下观察到最终行为 | 其他设备、系统版本也必然正确 |

如果目标是验证锁屏通知，build 和 install 都通过，只能说明前两层成立。反复重新构建、重新安装，不能替代锁屏状态、通知权限、系统通道和实际通知展示的证据。

因此，每个验证动作都应该声明：

```yaml
claim: 锁屏状态下能够收到指定通知
required_evidence:
  - device_state: locked
  - notification_permission: granted
  - channel_state: enabled
  - observed_notification: screenshot_or_system_log
```

当现有证据只覆盖 build/install 时，Harness 应报告“尚未验证目标主张”，而不是把低层通过汇总成整体成功。

## 四、失败指纹如何进入 Failure Corpus

Failure Corpus 不能只是错误日志集合。要支持回归与门禁，至少需要把一次失败拆成四层：

```text
Failure Case
├── Trigger：什么输入和环境触发
├── Fingerprint：失败发生在哪一层、以什么形式出现
├── Evidence：原始 Trace、日志、截图、状态快照
└── Resolution：什么变化让指纹消失或移动
```

其中最容易缺失的是 `Resolution`。

如果只记录“后来通过了”，我们不知道是代码修复、环境变化、模型随机性，还是验证被放宽。更可靠的记录方式是保存：

- 修复前指纹；
- 本次唯一或主要变化；
- 修复后指纹或通过证据；
- 是否新增回归用例；
- 哪个 Gate 会阻止同类问题再次交付。

这样，一次故障才能从复盘材料变成可运行的质量资产。

## 五、给重试增加一个最小门禁

可以先从很小的规则开始，不需要重构整套 Harness：

```python
def should_retry(previous, current_plan):
    if current_plan.change_set:
        return True
    if current_plan.new_observability:
        return True
    if previous.fingerprint is None:
        return True
    return False
```

执行一轮后再判断：

```python
if current.fingerprint == previous.fingerprint:
    if current.evidence_refs <= previous.evidence_refs:
        status = "NO_PROGRESS"
        next_action = "ROOT_CAUSE_INVESTIGATION"
```

这不是通用实现，只表达两个约束：

1. 开始重试前，要说清本轮改变了什么；
2. 重试结束后，要检查失败和证据是否发生变化。

实际系统还需要处理非确定性、偶发故障和统计性 Eval。对于 flaky case，重复运行可能本身就是为了估计失败率；这时 `change_set` 可以为空，但运行计划必须声明采样目标、样本数和停止条件。不能把探索性采样和修复性重试混在一起。

## 六、什么时候应该停止自动重试

下面几类情况适合触发停止或转人工：

- 同一失败指纹连续出现，且没有新增证据；
- 失败发生在审批、权限、会话或环境层，业务工具从未执行；
- 本轮只是重复低层验证，未覆盖目标主张；
- 缺少业务规则或人工决定，Agent 无法通过重写产物补齐；
- 修复同时改动多个变量，无法判断哪项变化有效。

停止不是放弃任务，而是改变工作模式：从“继续执行”切换到“最小复现、补充观测、确认规则或人工决策”。

DeepSeek Harness 在 0.2.0 候选版本的发布说明中提到：工具调度异常后，对于已经执行但结果未知的操作，应先核实副作用，而不是盲目重试。这种原则可以再向前扩展：对于失败原因和执行状态没有变化的任务，也不应盲目增加轮次。[版本说明](https://github.com/deepseek-ai/deepseek-harness/releases)

## 七、先在一条真实链路上验证

如果要把这套方法用于测试用例 Agent、UI Agent 或自动化测试引擎，可以先选一条失败频繁的链路，做一个有界实验：

1. 为最近 10 次失败补充最小指纹；
2. 合并明显相同的失败族；
3. 检查每次重试前是否存在明确变化；
4. 检查重试后是否增加了新证据或缩小了范围；
5. 统计哪些轮次可以被 `NO_PROGRESS` 规则提前停止；
6. 人工复核是否误停了有价值的探索。

这组数字需要来自实际运行，不能预先假设节省比例。实验的第一目标不是证明“重试越少越好”，而是验证失败指纹能否稳定区分：重复消耗、有效诊断和必要的统计采样。

## 结语

Agent Reliability 不只是让任务成功，也不只是让失败留下 Trace。

更进一步的问题是：系统能否知道自己有没有在推进问题。

当 Harness 能识别相同失败、要求重试声明变化、比较证据增量，并在没有进展时切换模式，验证才不再是“为了验证而验证”。轮次、预算和 Agent 数量也不再是进展的替代指标。

下一步值得建立的，不是更大的重试预算，而是一套能够回答这句话的机制：**这一轮，到底新增了什么我们上一轮不知道的东西？**

## 参考资料

- [DeepSeek Harness v0.2.1-alpha.1 Release Notes](https://github.com/deepseek-ai/deepseek-harness/releases/tag/dsh-v0.2.1-alpha.1)
- [DeepSeek Harness：auto-review 缺少 session header 的问题报告](https://github.com/deepseek-ai/deepseek-harness/discussions/8726)
- [OpenViking v0.4.23 Release Notes](https://github.com/volcengine/OpenViking/releases/tag/v0.4.23)
- [runtime质量论：线上失败怎么变成 Failure Corpus？](https://hugfeature.github.io/eval/failure-corpus-to-regression/)
- [runtime质量论：Agent Trace Grading 怎么设计？](https://hugfeature.github.io/eval/agent-trace-grading/)
