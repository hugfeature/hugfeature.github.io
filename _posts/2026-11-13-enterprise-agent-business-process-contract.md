---
related_posts:
  - /eval/test-case-gates-with-incomplete-requirements/
  - /harness/agent-authorization-lineage/
  - /eval/how-to-build-business-eval-dataset/
  - /harness/long-running-agent-runtime-contract/
layout: post
title: "企业 Agent 的真正接口：不是 Prompt，而是业务流程契约"
description: "从百度智能组织、IBM 与 Microsoft 的企业 Agent 平台，以及 Qwen Code 1.0 Preview 的工程变化出发，拆解企业知识、流程、权限和证据如何变成可执行、可验证的系统契约。"
date: 2026-11-13 07:30:00 +0800
updated: 2026-11-13 07:30:00 +0800
last_modified_at: 2026-11-13 07:30:00 +0800
categories: [Enterprise-AI, Agent-Harness, Agent-Reliability, AI4SE]
permalink: /enterprise/agent-business-process-contract/
tags: [enterprise-ai, business-process, domain-model, agent-harness, agent-reliability, ai4se, eval, quality-gate]
series: agent-harness
series_order: 20
---

企业 Agent 能理解一句自然语言，不代表它理解了企业。

“把这批单据处理一下”对员工来说可能非常明确：哪些单据、当前处于什么状态、谁有权处理、哪些情况需要审批、什么结果才算完成。这些信息往往分散在 ERP 字段、制度文档、岗位职责、历史操作和团队经验里，并不完整地存在于一段 Prompt 中。

模型可以把自然语言转成计划，但企业系统真正需要的是：**这次任务对应哪个业务对象、遵循哪条规则、由谁授权、允许产生什么副作用，以及用什么证据证明结果正确。**

因此，企业 Agent 的关键接口不应该只有 Prompt 和 Tool Schema，还应该有一层可版本化的业务流程契约（Business Process Contract）。

## 一、本周三个信号：企业 AI 正在从模型能力走向组织和流程能力

### 1. 百度世界 2026：把隐性知识、组织流程和 Agent 资产放在一起讨论

2026 年 11 月 12 日，百度世界 2026 以“下一幕，智能组织”为主题发布多项产品和平台更新。百度创始人李彦宏提出组织进化的三个方向：打破岗位边界、沉淀隐性知识、设计流程闭环。

百度在发布材料中披露，过去一年内部日活 Agent 从 5,000 增至 37,000，每周完成任务从 84,000 增至 100 万，已建立 4,300 个工作空间并沉淀超过 20,000 个组织 Skill。百度还称，通用 Agent DuMate 开放了 Harness Engine 和 Agent API；面向复杂行业运营的 Famou 3.0 将 Agent 平台与 FDE 服务结合，客户覆盖 41 个工业大类中的 25 个。

同场发布的 Token Exchange 以模型指纹、能力测试、性能和可用性验证，以及服务商抽检和调用监控来组织模型服务供需。百度披露该平台已接入 100 多种模型资源，日均请求超过 5,000 万次、Token 量超过 7,000 亿。

这些数字均来自百度提供的发布材料，属于厂商自报数据，不是独立审计结果。它们可以说明百度正在把组织 Skill、Agent 执行入口、模型服务和 FDE 交付放在同一套企业 AI 叙事中，但不能单独证明这些 Agent 已在所有业务场景稳定运行，也不能证明组织效率提升了多少。

来源：[百度世界 2026 发布材料（百度提供）](https://www.prnewswire.com/news-releases/baidu-unveils-latest-ernie-models-amid-broader-full-stack-ai-lineup-and-debuts-token-exchange-to-power-intelligent-organizations-302937959.html)；[百度世界 2026 大会官网](https://baiduworld2026.events.net.cn/)

### 2. IBM 与 Microsoft：企业 Agent 平台把行业资产和 FDE 交付组合起来

2026 年 11 月 10 日，IBM 与 Microsoft 发布 Imagine Enterprise，定位为面向行业流程的 Agent 构建、运行和治理平台。

IBM 表示，该平台结合了 IBM Consulting Advantage 中超过 6,000 个预构建 Agent 和相关资产，以及 Microsoft 的 AI、数据、云和安全能力；双方还为符合条件的客户提供 Forward-Deployed Engineering 支持。平台初始行业框架覆盖金融服务、保险和零售，并强调连接客户既有数据、流程和系统，而不是要求客户从头替换现有平台。

发布材料提到，金融科技与资产管理服务商 SEI 正与 IBM Consulting、Microsoft 探索 Agentic 技术在企业转型中的应用。这里的表述是“探索”，不是已完成规模化生产部署。Imagine Enterprise 可以通过 IBM Consulting 部署和运营，也提供自管理选项。

这反映出一种值得关注的交付组合：通用平台能力、行业预制资产、企业系统集成和现场工程服务共同构成产品。真正难以标准化的部分，可能不是 Agent Runtime 本身，而是行业知识、流程差异、权限规则和组织变更。

来源：[IBM Newsroom：Imagine Enterprise 发布公告（2026-11-10）](https://newsroom.ibm.com/2026-11-10-ibm-and-microsoft-announce-a-new-ai-agent-platform-designed-for-industry-specific-transformation)

### 3. Qwen Code 1.0 Preview：AI4SE 的 Agent 能力开始以可复用运行时形态交付

2026 年 11 月 11 日，Qwen Code 发布 v1.0.0-preview，将 Qoder 与 Qwen Code 的 Agent 能力结合，覆盖代码理解、实现、调试和测试；支持 Qwen、Qoder 账号、多模型提供方和兼容接口，并提供会话恢复与非交互执行能力。

前一天发布的 v0.27.2 还增加了 Skill 从原 Runtime 工作区导入并显式安装、Tool v4 执行测量、待审批提醒，以及 Managed Agent 的会话回顾等能力。执行测量包含持续时间、有效样本数，以及建议修改与实际应用修改的行数。

这些变化把 AI Coding 从交互式助手进一步推向可嵌入开发流程的执行环境。不过 v1.0 仍是 Preview，官方明确提示接口、配置和行为可能变化；发布说明也没有提供企业级交付成功率或实际 ROI 的独立数据。

来源：[Qwen Code 官方 Releases](https://github.com/QwenLM/qwen-code/releases)

## 二、企业 Agent 需要的不是更长的 Prompt，而是四类业务契约

把企业知识直接塞进 Prompt，短期可能让 Agent 更容易回答问题，却没有解决执行时的歧义。更可维护的做法，是把业务知识拆成四类契约，并让 Harness 在执行前后引用它们。

### 1. 业务语义契约：先确定企业到底在说什么

企业术语经常存在别名、缩写、部门口径和历史叫法。同一个词在不同业务流程中也可能指向不同对象。

业务语义契约至少需要描述：

- 规范术语、别名和定义；
- 对应的业务对象、字段和关系；
- 数据类型、单位、枚举和值域；
- 权威数据来源（System of Record）；
- 术语和字段的责任人、版本及生效范围；
- 无法消歧时的处理方式。

例如，“客户”可能指客户主数据、合同中的交易对手，也可能指某张业务单据上的联系人。Agent 不能只根据词面相似度选择一个 API 字段，而应该根据流程上下文和数据来源确定对象；仍有歧义时，输出待确认项。

### 2. 流程契约：把“应该怎么做”变成状态转换

业务流程不是一串自然语言步骤。它通常包含触发条件、前置条件、允许动作、状态转换、异常分支和完成条件。

流程契约需要明确：

- 任务适用的业务对象和范围；
- 开始执行前必须满足的条件；
- 每一步允许调用的工具或业务操作；
- 状态转换及其触发事件；
- 异常、撤销、重复提交和人工处理分支；
- 哪个系统状态代表流程真正完成。

如果一个 Agent 只检查页面出现“提交成功”，却没有查询业务系统中的最终状态，它证明的只是界面反馈，不是业务流程完成。

### 3. 权限契约：把“能调用”与“允许这次调用”分开

工具注册表说明 Agent 技术上能调用什么，权限策略说明它在当前任务中被允许做什么。

权限契约至少应关联：

- 发起任务的用户或系统主体；
- Agent、Skill 和执行器身份；
- 代表谁执行；
- 允许访问的对象范围；
- 允许执行的操作类型；
- 审批条件、授权有效期和策略版本；
- Retry、Resume 或切换执行主体时是否需要重新判权。

用户拥有某项业务权限，不意味着 Agent 可以自动继承全部权限。尤其是写入、审批、付款、删除和跨系统传输数据，应由执行层实施策略，而不是只依赖 Prompt 中的“不要越权”。

### 4. 证据契约：明确什么事实可以证明任务完成

执行 Agent 的总结不能替代目标系统中的事实。证据契约需要把输入、规则、动作和结果连起来：

- 输入需求及其版本；
- 业务对象 ID 和执行前状态；
- 流程契约、权限策略和 Skill 版本；
- 每次工具调用的 ID、参数摘要和返回状态；
- 外部系统产生的记录 ID 或状态变化；
- 独立验证结果；
- 未覆盖项、异常和人工接管记录。

这与 Trace、Evidence、Eval 和 Quality Gate 的关系是：Trace 记录过程，Evidence 指向可核验事实，Eval 判断是否满足规则，Gate 决定是否允许继续或交付。

## 三、哪些应该做成平台能力，哪些必须保留企业差异

企业 AI 平台不能把所有业务逻辑都硬编码进 Runtime，也不能把每家企业的差异都留给 Agent 临场猜测。

| 能力层 | 适合标准化的平台能力 | 必须由企业定义或确认的内容 |
| --- | --- | --- |
| 语义 | 术语注册、Schema、版本和来源管理机制 | 企业术语、主数据、字段口径、对象关系 |
| 流程 | Workflow 执行、状态持久化、重试和恢复 | 流程节点、前置条件、状态转换、例外处理 |
| 工具 | Tool Registry、参数校验、幂等和超时机制 | ERP/API 映射、操作语义、数据边界 |
| 权限 | Policy Engine、身份传递、审批和审计接口 | 组织角色、职责分离、授权范围和审批规则 |
| 可靠性 | Trace、Eval、Failure Corpus、Regression、Quality Gate | 业务验收标准、风险等级、容错阈值 |
| 运营 | 成本、延迟、使用量、异常和版本监控 | 业务收益基线、流程 KPI、责任归属 |

平台可以提供通用的状态机、权限执行点、工具调用协议、证据格式和评测流水线，但不能替企业决定“什么叫合规”“谁能审批”“哪些例外可以放行”。

这也是企业 AI 的潜在壁垒：基础模型、通用 Agent Loop、工具协议和部分运行时组件会逐步标准化；企业独有的术语、隐性知识、组织职责、历史数据、流程例外和验收口径则需要持续治理。它们可以被抽象为可配置的业务资产，却不能在没有业务确认的情况下被通用化。

## 四、一个可落地的 Business Process Contract 示例

下面是一个示意结构，用于表达业务对象、规则、操作、权限和完成证据之间的关系。字段名和状态均为占位符，不代表任何特定 ERP 的真实接口或流程。

~~~yaml
process_contract:
  id: <business-process-id>
  version: <rule-version>
  owner: <business-owner>

  domain:
    object: <business-object>
    canonical_terms:
      - term: <canonical-term>
        aliases: [<alias-1>, <alias-2>]
        source_of_truth: <system-or-document>

  preconditions:
    - rule_ref: <precondition-rule-id>

  transitions:
    - from: <source-state>
      event: <allowed-action>
      to: <target-state>
      tool_ref: <registered-tool>

  authorization:
    policy_ref: <policy-id>
    approval_ref: <approval-rule-id>

  completion:
    assertions:
      - source: <system-of-record>
        predicate: <verification-rule>

  unresolved:
    behavior: require_human
~~~

这里有三个关键点。

第一，规则通过引用管理，而不是把业务口径散落在 Prompt 和 Skill 中。规则变更后，可以知道哪些 Workflow、Skill 和 Eval Case 需要重新验证。

第二，工具调用只是流程中的动作，不是流程完成的证据。写入后必须查询权威系统，确认目标对象和状态符合预期。

第三，未知规则必须有显式处理策略。对于缺失的审批条件、冲突的术语或无法确认的状态转换，应进入待确认或人工审批，而不是让模型补全一个看似合理的答案。

## 五、如何把这套契约接入 ERP 测试闭环

在 ERP 场景中，可以沿着以下链路把业务知识转成可验证执行：

~~~text
PRD / 业务文档 / 页面 / API
              |
              v
      术语与业务对象提取
              |
              v
      业务规则与流程建模
              |
              v
       Business Process Contract
              |
       +------+------+
       |             |
       v             v
   Skill / Workflow  Eval Case
       |             |
       v             |
  Harness 受控执行    |
       |             |
       v             |
  API / UI / ERP     |
       |             |
       v             v
  独立查询与结果验证
              |
              v
      Trace / Evidence
              |
              v
      Failure Analysis
              |
              v
      Regression / Quality Gate
              |
              v
       规则与平台持续改进
~~~

这里最重要的变化，是让 Skill 和测试用例共享同一份业务规则来源。

如果 Skill 认为某个状态可以提交，而 Eval Case 认为必须先满足另一项前置条件，两者就存在规则漂移。将流程规则独立版本化后，可以在规则变更时定位受影响的 Skill、Workflow 和 Regression Case。

对于当前 ERP 测试工作，第一步不必建设完整的企业知识图谱或通用 BPM 平台。可以从一个真实业务流程开始，先建立最小契约：

1. 术语能映射到 PRD、字段或权威数据源；
2. 每个关键动作能映射到 API 或 UI 操作；
3. 前置条件、权限和状态转换有明确来源；
4. 完成条件可以通过独立查询验证；
5. 未知规则不会被 Agent 静默补全；
6. 失败可以关联到规则版本、工具调用和执行证据，并进入回归。

## 六、怎样判断是单点提效，还是流程级提效

模型生成更多测试用例、自动填写更多表单、代码补全更快，都只能说明某个环节发生了变化。

企业真正关心的是端到端流程是否改善。至少要区分三层指标：

| 层级 | 观察指标 | 需要避免的误判 |
| --- | --- | --- |
| 单点能力 | 生成耗时、调用成功率、单步准确率 | 单步变快不代表整个流程变快 |
| 流程质量 | 端到端完成率、人工接管率、返工率、异常率 | Agent 报告完成不等于业务系统完成 |
| 组织收益 | 流程周期、单位任务成本、吞吐量、业务差错和风险 | Token 使用量或 Agent 活跃数不等于 ROI |

基线也必须先定义。例如，流程周期从哪个业务事件开始，到哪个权威状态结束；人工接管是否计入总耗时；失败重试和后续返工是否纳入成本。没有统一口径，就无法判断 AI 是否真正改善了流程。

百度披露的内部 Agent 活跃度和任务量、Token Exchange 调用量，以及 IBM 提供的预构建 Agent 数量，都可以作为使用规模或供给规模的信号，但它们不是企业业务 ROI 的替代指标。IBM 与 SEI 的合作目前公开表述为探索阶段，也不能当作已验证的生产收益。

## 七、AI4SE 是重要试验场，但不是企业 AI 转型的全部

AI4SE 的优势是工程对象相对清晰：需求、代码仓库、提交、测试、构建和发布都有可定位的工件与状态。Qwen Code 1.0 Preview 的会话恢复、非交互执行和多模型接入，说明 Coding Agent 正在向可集成的工程执行环境演进。

这为企业 AI 平台提供了很好的试验场：可以验证任务状态管理、工具权限、Workflow 编排、执行证据、自动评测、Failure Regression 和 Quality Gate。

但软件工程里的“代码通过测试”，不能直接类比 ERP 里的“业务流程正确”。ERP 还需要处理主数据、组织职责、审批矩阵、跨系统一致性、业务期间、历史规则和流程例外。把 AI4SE 的 Runtime 机制迁移到企业业务时，必须重新定义业务语义和完成条件。

因此，合理的关系是：**AI4SE 帮助验证通用 Agent 工程能力；企业业务流程提供真正的领域约束；AI Engineering Reliability 把两者连接成可受控、可验证、可持续改进的系统。**

## 结语：平台负责执行机制，企业负责定义业务事实

企业 AI 平台可以提供通用 Runtime、Workflow、Skill 管理、权限执行、Trace、Eval 和质量门禁，但不能替企业发明业务规则。

真正可持续的企业 AI 系统，需要把业务术语、对象关系、隐性知识、组织职责和流程例外显性化，再通过可版本化的契约连接 Agent 执行和独立验证。

对于平台工程来说，目标不是把所有企业流程做成同一个模板，而是建立一套机制：**企业差异可以被明确表达，执行边界可以被系统强制，结果可以被独立验证，失败可以沉淀为回归资产。**

这才是从一个能演示的 Agent，走向真正嵌入企业流程的生产力系统的工程路径。

## 参考资料

- [百度世界 2026：百度关于智能组织、Token Exchange、DuMate 和 Famou 3.0 的发布材料（2026-11-12，百度提供）](https://www.prnewswire.com/news-releases/baidu-unveils-latest-ernie-models-amid-broader-full-stack-ai-lineup-and-debuts-token-exchange-to-power-intelligent-organizations-302937959.html)
- [百度世界 2026 大会官网](https://baiduworld2026.events.net.cn/)
- [IBM 与 Microsoft 发布 Imagine Enterprise（2026-11-10）](https://newsroom.ibm.com/2026-11-10-ibm-and-microsoft-announce-a-new-ai-agent-platform-designed-for-industry-specific-transformation)
- [Qwen Code 官方 Releases：v1.0.0-preview、v0.27.2（2026-11-10 至 11-11）](https://github.com/QwenLM/qwen-code/releases)
- [需求不完整时，测试用例生成的 Gate 应该怎么判？](https://hugfeature.github.io/eval/test-case-gates-with-incomplete-requirements/)
- [用户授权了 Agent，为什么它仍然没有权力执行？](https://github.com/hugfeature/hugfeature.github.io/blob/main/_posts/2026-09-25-agent-authorization-lineage.md)
- [如何构建业务 Eval Dataset](https://hugfeature.github.io/eval/how-to-build-business-eval-dataset/)
- [长程 Agent 不能只靠一个 completed：把中止、接管与恢复纳入 Runtime 契约](https://hugfeature.github.io/harness/long-running-agent-runtime-contract/)
