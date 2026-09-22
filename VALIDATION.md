# 升级验收记录

## 本地构建

2026-09-22 完成。本地从原始 GitHub 仓库检出，保留现有文章正文。

- 实际执行 Jekyll **3.10.0** production build，启用 `--strict_front_matter`，成功。
- Minima **2.5.1**；jekyll-seo-tag **2.8.0**；jekyll-feed **0.17.0**；jekyll-sitemap **1.4.0**。
- 环境初始没有 Ruby。测试通过临时 Ruby 3.2.3 及最小 Gemfile 加载上述依赖；没有声称本地安装了完整 `github-pages` 依赖集。仓库 Gemfile 使用 GitHub Pages 232，实际托管构建由已有 Pages workflow 运行。
- `python3 scripts/check_site.py _site`：**PASS**，17 个 HTML 页面。
- `git diff --check`、3 个 JavaScript 文件的语法检查：**PASS**。

检查范围：单一 H1、标题唯一性、非空 description、正确 canonical、中文 lang、heading hierarchy、JSON-LD 有效性、文章 BlogPosting 时间、站内 URL 与锚点、sitemap、Atom feed、全文搜索索引以及原文章 URL。

## 浏览器检查

Chromium + Playwright 实际执行，无页面 JavaScript 错误：

- 1440 / 768 / 390 / 320px，首页、Harness、About、Tags、Series、404、Harness 文章共 **28 项布局检查**；没有页面级横向溢出。
- 桌面浅色/深色、移动端首页与文章截图已目视检查。
- 系统主题跟随、手动三态循环、刷新后持久化：通过。
- 桌面 TOC sticky；移动 TOC 默认折叠；目录锚点：通过。
- 代码复制与实际剪贴板内容、文章链接复制：通过。
- 文章末尾阅读进度到 100%、返回顶部入口：通过。
- 搜索标题、中文正文、空结果、查询参数深链、HTML 输入安全渲染：通过。
- 键盘跳过导航、无 JavaScript 内容与系统深色回退：通过。
- axe-core 的 WCAG 2.1 A/AA 自动检查：首页 / 文章 / 搜索 × 桌面 / 手机 × 浅色 / 深色，**12 组无违规**。自动检查不等于完整无障碍认证。

## 页面与资源

| 路径 | 本地结果 |
| --- | --- |
| `/` | 通过 |
| `/harness/`、`/harness/what-is-agent-harness/` | 通过 |
| `/about/`、`/tags/`、`/series/`、6 个 `/topics/` | 通过 |
| `/archive/`、`/search/`、`/search.json` | 通过 |
| `/404.html` | 页面与 noindex 通过；线上真实 HTTP 404 由 GitHub Pages 提供 |
| `/robots.txt`、`/sitemap.xml`、`/feed.xml` | 生成与解析通过 |

原有三篇文章的线上 URL 均保留。特别保留专利文章 `/engineering/patent/2026/09/21/how-to-apply-technical-patent.html`，防止原 UTC 日期与北京时间转换后改变路径。

站外链接抓取：13 个 URL 返回 200（包括 GitHub 项目与反馈入口）。Cloudflare Harness 文档和 OpenAI Agents API 文章受本次请求环境影响未验证成功，保留原文链接，不能据此断言死链；本次没有重新审查或重写文章事实。

## 性能成本

- CSS 约 **17 KB**，三个原生 JS 合计约 **9 KB**（未压缩）；无前端框架，无第三方运行资源。
- 全站脚本 gzip 约 **2.3 KB**；搜索脚本另外约 **1.5 KB**，仅搜索页加载。
- 当前全文索引约 **30 KB**（gzip 约 **13 KB**），首次搜索时才请求。
- 本地社交分享 PNG 约 **43 KB**，通过元数据供分享抓取，不作为首页可见大图下载。
- 字体使用系统字体；不会请求为截图环境安装的测试字体。
- 未声称取得 Lighthouse 分数或真实用户 Core Web Vitals；移动布局和交互经过真实浏览器验证。

人工站长平台验证与仓库 About 信息见 README 的 SEO Setup。
