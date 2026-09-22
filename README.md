# runtime质量论

轻量的 Jekyll + GitHub Pages 技术站点。线上地址：https://hugfeature.github.io/

## 本地开发

依赖 Ruby 3.3、Bundler 和 Python 3（验证脚本只用标准库）。

```sh
bundle install
bundle exec jekyll serve
# 发布前：
JEKYLL_ENV=production bundle exec jekyll build --strict_front_matter
python3 scripts/check_site.py _site
```

`Gemfile` 使用 GitHub Pages 官方依赖集 `github-pages 232`，与 https://pages.github.com/versions.json 核对后固定；升级时重新核对官方清单。Minima 保留为兼容的主题基础，本站通过 `_layouts` 和 `_includes` 覆盖呈现，不加载 Minima 默认 CSS。无自定义 Jekyll 插件、Node 构建依赖或前端框架。

现有发布方式保持为 GitHub Pages 从 `main` 根目录构建。已有 `pages build and deployment` 工作流可在 Actions 查看。不要同时配置另一套部署工作流。

## 内容约定

```yaml
---
layout: post
title: "文章标题"
description: "清晰、独立的文章摘要，说明解决什么问题。"
date: 2026-09-22 10:00:00 +0800
updated: 2026-09-22
last_modified_at: 2026-09-22
tags: [agent-harness, trace-evidence]
series: agent-harness
series_order: 2
# permalink: /harness/your-existing-slug/
---
```

- 保留已发布文件名、日期、categories 与 permalink，否则默认文章 URL 可能改变。本次保留原有字段，并为两篇默认日期 URL 补充与线上完全一致的 permalink，防止时区引起日期路径变化。
- 正文从 H2 开始，H1 由 layout 输出。摘要使用 `description`，不复制整段正文。
- `updated` 用于界面；`last_modified_at` 用于 SEO、sitemap 与系列更新时间。修改时二者同步，未提供时回退到发布日期。本次日期反映元数据整理，不表示正文重写。
- 阅读时间按正文源文本约 400 字符/分钟估计，中英混排与代码仅作近似。
- 已发布的 Harness 正文有 ASCII 示意，保留原文；新文章建议使用易读的代码、表格和静态图，不引入全站图表运行库。
- 系列定义在 `_data/series.yml`；系列成员由 `series` 和 `series_order` 维护。首页/系列页自动统计数量与最新更新时间。新增系列还需创建相应入口页。
- 6 个核心 tag 使用稳定 slug：`agent-harness`、`agent-reliability`、`ai-eval`、`trace-evidence`、`failure-regression`、`quality-gate`。核心专题说明在 `_data/topics.yml`，静态入口在 `topics/`，GitHub Pages 不需要标签生成插件。其他标签自动聚合到 `/tags/`。
- Related Posts 仅展示相同系列或共享标签的真实文章，最多 3 篇；没有关联就不显示，不把所有文章强行归类。
- 项目列表维护 `_data/projects.yml`。规划中的文章只列标题，不生成假链接。

## 交互与性能

- 系统/浅色/深色三态循环，优先跟随系统，选择保存于本地；禁用存储或 JavaScript 时系统主题仍可用。
- TOC 桌面 sticky、移动端折叠；原生代码复制、正文阅读进度、回到顶部、复制文章链接、GitHub Issues 反馈。
- `/search/` 首次查询才下载 `/search.json`，搜索标题/摘要/标签/全文，多词 AND 匹配；按命中字段权重排序。输入仅用 textContent 渲染。
- CSS、脚本和分享图均本地托管，没有第三方字体、分析脚本、评论库或外部运行请求。
- 正文图片使用 lazy loading；新内容务必填写图片 width/height，避免布局位移。
- 随文章增长注意搜索索引体积，必要时截断正文或拆分索引。

## SEO Setup

已启用 GitHub Pages 支持的 `jekyll-seo-tag 2.8.0`、`jekyll-sitemap 1.4.0`、`jekyll-feed 0.17.0`（兼容性来源：https://pages.github.com/versions.json）。

- `jekyll-seo-tag` 负责 title、description、canonical、OpenGraph、Twitter Card 与文章 BlogPosting JSON-LD；其余 WebSite、Person、BreadcrumbList 按页面类型补充。
- `lang=zh-CN`、站点 URL、文章摘要、社交分享图、favicon 已配置。
- `/robots.txt` 开放抓取并声明 sitemap；`/sitemap.xml` 自动生成；`/feed.xml` 是供 RSS 阅读器订阅的 Atom feed。
- 404 和搜索页标记 noindex 并从 sitemap 排除，搜索索引也不进入 sitemap。
- SEO 基础设施不能保证收录或排名；本次没有编造任何验证 token。

需要站主手动完成：

1. 在 [Google Search Console](https://search.google.com/search-console/) 添加 URL 前缀资源 `https://hugfeature.github.io/`。这是 GitHub 托管子域，优先用 HTML meta 验证，不要求为 github.io 配置 DNS。
2. 把真实验证码填到 `_config.yml` 的 `webmaster_verifications.google`，部署完成后验证；提交 `https://hugfeature.github.io/sitemap.xml`。
3. 在 [Bing Webmaster Tools](https://www.bing.com/webmasters/) 导入 Google 资源，或添加同一站点并将真实 token 填到 `webmaster_verifications.bing`；提交 sitemap。
4. 使用站长平台检查首页、Harness 入口和文章 URL 的抓取与索引状态。新文章发布后检查 sitemap 与 feed，避免只靠手动提交。
5. 在仓库 About 设置 Description / Website / Topics（当前 GitHub 连接没有这些设置的写入工具）：
   - Description：`runtime质量论 — Agent Reliability、Harness、AI Testing / Eval 与 Runtime Quality 的工程笔记和开源实践。`
   - Website：`https://hugfeature.github.io/`
   - Topics：`agent-reliability`、`ai-testing`、`agent-harness`、`ai-evaluation`、`llm-testing`、`runtime-reliability`

## 验证

`python3 scripts/check_site.py _site` 验证所有生成 HTML 的 H1、标题、摘要、canonical、JSON-LD、heading hierarchy、站内链接与锚点，并解析 sitemap、feed 和搜索索引。它也会检查已发布文章 URL 的兼容性。浏览器功能与移动端检查的本次结果见 `VALIDATION.md`。
