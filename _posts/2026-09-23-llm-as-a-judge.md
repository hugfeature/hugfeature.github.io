---
layout: post
title: "LLM-as-a-Judge 怎么做才靠谱？从 Rubric、偏差到人工校准"
date: 2026-09-23 09:35:00 +0800
categories: [AI-Eval, Model-Evaluation]
permalink: /eval/llm-as-a-judge/
description: "LLM-as-a-Judge 适合开放任务的大规模评测，但不能直接把模型分数当真值。本文给出 Rubric、Pairwise、Reference、偏差控制、人工校准与 Judge Regression 的实用方法。"
tags: ["ai-eval", "llm-as-a-judge", "grader", "rubric", "human-evaluation"]
series: ai-eval
series_order: 5
---

> **AI Eval 系列 #05**  
> 上一篇：[怎样构造一套真正有用的业务 Eval Dataset？](/eval/how-to-build-business-eval-dataset/)

开放式任务最麻烦的地方是：

**没有唯一标准答案。**

摘要、分析、测试用例、代码 Review、方案设计，都很难用 Exact Match 判断。

于是很多团队会自然走到：

**LLM-as-a-Judge。**

让一个更强模型来评价另一个模型的输出。

这个思路是可行的。

但前提是：

**Judge 也必须被测试。**

否则只是把“被测模型的不确定性”，转移成“评分模型的不确定性”。

## 一、先判断任务是否真的需要 LLM Judge

能不用 Judge，就先不用。

优先级我会这样排：

~~~text
Deterministic Check
↓
Executable Check
↓
Rule / Schema
↓
Reference-based Metric
↓
LLM Judge
↓
Human Review
~~~

例如：

JSON 格式正确不正确，用 Schema。

代码能不能运行，用 Test。

SQL 对不对，用真实数据库执行结果。

Tool 参数是否合法，用规则。

只有这些方法无法覆盖“质量”的时候，再引入 LLM Judge。

## 二、LLM Judge 最适合什么任务

比较适合：

- 完整性；
- 相关性；
- 正确性；
- 风格；
- 摘要质量；
- 解释质量；
- 方案覆盖度；
- 测试点覆盖度。

例如测试用例生成：

~~~text
输入：
PRD

输出：
测试用例

Judge：
是否覆盖核心业务规则？
是否包含异常路径？
是否遗漏关键权限条件？
~~~

这种任务很难写成 Exact Match。

但可以通过明确 Rubric 判断。

## 三、最关键的不是模型，而是 Rubric

一个差的 Judge Prompt：

~~~text
请给这个回答打 1～10 分。
~~~

基本等于：

**请凭感觉打分。**

更好的方式是先定义明确维度。

例如：

~~~text
正确性：
是否存在事实错误？

完整性：
是否覆盖所有必需业务规则？

可执行性：
测试步骤是否可以直接执行？

风险：
是否存在可能导致严重误判的内容？
~~~

甚至进一步定义等级：

~~~text
PASS
满足所有关键要求，无严重错误

PARTIAL
存在非关键遗漏，但不影响主要结论

FAIL
存在关键事实错误、关键遗漏或安全风险
~~~

Rubric 越明确，Judge 越稳定。

## 四、Pairwise 往往比绝对打分稳定

OpenAI 的评测最佳实践建议，在适合的场景里优先考虑比较、分类或通过/失败，而不是让模型做完全开放的绝对评分。

原因很简单。

判断：

~~~text
A 和 B 哪个更好？
~~~

通常比：

~~~text
A 是 7.2 分还是 7.8 分？
~~~

更容易。

所以做模型升级评测时，我更喜欢：

~~~text
Old Model Output
vs
New Model Output

Judge:
A better / B better / Tie
~~~

然后随机交换 A/B 顺序。

这可以降低位置偏差。

## 五、LLM Judge 有哪些典型偏差

### Position Bias

模型可能偏好第一个或第二个答案。

解决：

~~~text
A vs B
B vs A
~~~

双向评一次。

### Verbosity Bias

模型可能偏好更长、更详细的答案。

因此 Rubric 里应该明确：

**长度本身不加分。**

### Style Bias

语言更漂亮，不代表业务更正确。

所以要把：

~~~text
Correctness
Completeness
Style
~~~

拆开评分。

### Self-preference

某些 Judge 对和自身风格类似的输出可能有偏好。

所以重要任务不能只依赖单一 Judge。

## 六、Judge 必须和人工标签校准

这是最关键的一步。

先准备一小批人工 Gold：

~~~text
100 Cases

Human:
PASS / PARTIAL / FAIL
~~~

再让 Judge 评分。

比较：

~~~text
Human
vs
Judge
~~~

至少看：

- Agreement；
- Critical Error Recall；
- False Pass；
- False Fail。

尤其关注：

**False Pass。**

因为 Judge 把真正错误的结果判成 PASS，是最危险的。

## 七、不要只看 Agreement

例如：

~~~text
Human / Judge Agreement = 90%
~~~

看起来不错。

但如果 10% 的分歧全部来自“严重错误被 Judge 判 PASS”，那这个 Judge 仍然不能用于 Gate。

所以最好按风险分层：

~~~text
Overall Agreement
Critical Case Agreement
False Pass Rate
False Fail Rate
~~~

如果用于发布门禁，我会把：

**Critical False Pass**

单独作为硬指标。

## 八、一个实用 Judge 输出格式

Judge 不要只返回分数。

建议输出：

~~~json
{
  "verdict": "FAIL",
  "dimensions": {
    "correctness": "PASS",
    "completeness": "FAIL",
    "risk": "FAIL"
  },
  "evidence": [
    "遗漏审批金额阈值条件",
    "未覆盖越权操作"
  ],
  "confidence": "high"
}
~~~

这样后面才能做：

- Failure Analysis；
- Regression；
- 人工 Review；
- Judge Debug。

如果只保存：

~~~text
score = 6.5
~~~

几乎没有排查价值。

## 九、Judge 本身也要做 Regression

Judge Prompt 改了。

Judge Model 升级了。

Rubric 改了。

都可能导致评分体系变化。

所以 Judge 也应该有自己的测试集：

~~~text
Judge Dataset

Case
Expected Verdict
Expected Critical Error
~~~

每次升级 Judge：

~~~text
Judge v1
vs
Judge v2
~~~

先验证与 Human Gold 的一致性是否改善。

这一步非常像：

**测试评测系统本身。**

## 十、最终最好是多层 Grader

成熟一些的 Eval，不应该只有一个 Judge。

例如：

~~~text
Schema Check
      ↓
Executable Check
      ↓
Rule Check
      ↓
LLM Judge
      ↓
Human Sampling
~~~

能被确定性验证的，先确定性验证。

Judge 只负责那些必须依赖语义判断的部分。

人工则负责：

- 校准 Judge；
- 审核高风险分歧；
- 发现 Rubric 缺陷。

这比“所有东西都让 LLM 打分”可靠得多。

## 十一、从 Judge 到 Reliability

LLM-as-a-Judge 真正的价值，不是生成一个漂亮分数。

而是帮助你把原本只能靠人肉抽查的开放任务，变成：

~~~text
可规模运行
可重复比较
可定位失败
可持续回归
~~~

但前提永远是：

**Judge 本身有 Rubric、有 Gold、有校准、有 Regression。**

否则：

~~~text
LLM
评
LLM
~~~

并不会自动产生可靠性。

下一篇可以继续进入工程实现：

**一套 Eval 到底应该记录哪些指标？为什么 Pass Rate 远远不够？**

## 参考资料

- [OpenAI — Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)
- [OpenAI — Getting started with datasets](https://developers.openai.com/api/docs/guides/evaluation-getting-started)
- [Stanford CRFM — HELM](https://crfm.stanford.edu/helm/)
- [Anthropic — Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
