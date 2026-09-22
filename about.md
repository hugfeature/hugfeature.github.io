---
layout: page
title: 关于 runtime质量论
description: hugfeature 的技术笔记与开源实验，关注 AI Engineering Reliability、Agent Harness、AI Testing 与 AI Eval。
permalink: /about/
eyebrow: ABOUT
---
我是 **hugfeature**，有测试开发背景，目前关注 **AI Engineering Reliability / Agent Reliability**。

这里研究 AI 系统从生成、执行、验证到交付过程中的可靠性问题，记录真实项目中的方法、实验、失败案例与可复用工具。

## 我关注的问题

- **执行受控**：Agent Harness 如何管理工具调用、状态、权限与异常。
- **结果可验证**：AI Testing / AI Eval 如何连接 Trace、Evidence 与独立验证。
- **失败可回归**：如何把真实失败沉淀为 Failure Corpus、Regression 与 Quality Gate。

## 从哪里开始阅读

从 [Agent Harness：从入门到 Reliability]({{ '/harness/' | relative_url }}) 开始建立整体认识，再通过[专题与标签]({{ '/tags/' | relative_url }})追踪具体问题。

## 开源项目

{% for project in site.data.projects %}
- [{{ project.name }}]({{ project.url }})：{{ project.description }}
{% endfor %}

## 找到我

- GitHub：[hugfeature](https://github.com/hugfeature)
- 公众号：**runtime质量论**
- 订阅：[RSS / Atom]({{ '/feed.xml' | relative_url }})

欢迎通过[网站 GitHub Issues](https://github.com/hugfeature/hugfeature.github.io/issues)反馈文章问题或交流实践。
