# 升级前审计

基线 commit：54b6705d13aefa4aa1c4d7b02397a557c82a420c。

仓库全部业务文件：`_config.yml`、`index.md`、`about.md`、`harness.md`、3 篇 `_posts` 文章、仅一行的 README。没有自定义 layouts/includes/assets、Gemfile、测试脚本或自定义 CI。GitHub 自带 Pages 构建最近一次成功。

1. Minima 默认布局，没有独立的视觉系统；`minima.skin` 不适用于当前 Pages 的 Minima 2.5.1。
2. 首页以 Markdown 列表为主，内容路径、文章摘要与项目信息没有形成层次。
3. Harness 页面正文还有 H1，与 page layout 标题重复。
4. 只有 categories，缺少统一 tags、series 与更新时间；缺少自动关联阅读。
5. 无目录、代码复制、正文进度、返回顶部等阅读辅助。
6. 没有站内搜索、标签页、系列聚合与自定义 404。
7. SEO 未显式配置插件/验证位置，缺少 robots、社交分享图及作者与面包屑结构化数据。
8. 无可复现的本地依赖声明、链接与结构验证脚本。
9. About 身份与项目连接较弱；仓库 Description、Website、Topics 为空。

约束：保留原始文章正文、日期、categories、文件名及显式 permalink，不迁移技术栈。未发表文章只保留规划，不伪造内容。

线上发现专利文章日期 URL 为 2026/09/21（原站 UTC 构建），虽然 Front Matter 是北京时间 9 月 22 日。本次固定为线上原 URL，避免设置 Asia/Shanghai 后漂移。两篇默认日期 URL 均写入显式 permalink；已有 Harness permalink 保留。
