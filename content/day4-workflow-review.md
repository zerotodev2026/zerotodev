Title: 学会用 Workflow 后，我给我的博客来了次"全身体检"
Date: 2026-06-06 21:00
Category: 博客
Tags: AI, Claude Code, Workflow, 重构, 代码审查
Slug: day4-workflow-review

用 Claude Code 这么久，我一直是一个问题一个问题地问，就像一个个排队办事。

今天试了试它的 **Workflow** 功能——一次性派出去 28 个"小助手"同时干活。7 分钟跑完，翻出 21 个真实问题。

挑几个值得说的。

<!-- more -->

## 一个配置，让本地预览断链了

`pelicanconf.py` 里有一行被注释掉的配置：

```python
# RELATIVE_URLS = True
```

啥意思呢？Pelican 默认生成的是绝对路径链接（比如 `https://zerotodev-4jq.pages.dev/post1.html`）。这在线上没问题，但在本地直接打开 HTML 文件时，所有链接都指向线上地址，本地根本预览不了。

我之前一直纳闷为什么本地打开 `index.html` 全是断链——原来这行注释一直没取消。

## 三个废弃的部署方式

项目是 Pelican 脚手架生成的，自带了一堆部署模板：

- **s3_upload** — 亚马逊 S3 部署
- **cf_upload** — Rackspace Cloud Files 部署
- **publish** — rsync SSH 部署

这三个我压根没用过，变量全是占位符（`my_s3_bucket`、`my_rackspace_username` 之类）。而且 rsync 那个还引用了没定义的变量，如果误运行会直接崩。

我实际用的是 Cloudflare Pages（`deploy.sh`），这些留着纯属占地方，删掉。

## 关于 Workflow 的效率

28 个子代理，7 分钟，150 万 token，费用大概 $7-8。

单个问的话对话要往返 28 次，时间上至少翻倍。而且 Workflow 有个**交叉验证**环节——每个问题由第二个代理独立验证真伪，这次 24 个发现里有 3 个是误报，直接过滤掉了，人工审根本不会这么细。

当然不是每次都要开。结论是：

> **平常单聊，打包前开 Workflow 扫一遍。**

## 改动清单

这次一共改了 3 个文件：

| 文件 | 改动 |
|------|------|
| `pelicanconf.py` | 启用 `RELATIVE_URLS`，新增 `STATIC_PATHS` |
| `Makefile` | 删除 S3/CloudFiles 废弃部署目标 |
| `tasks.py` | 删除 CloudFiles 和 rsync 废弃任务 |

## 代码

所有改动已推送到 [GitHub](https://github.com/zerotodev2026/zerotodev) 和 [Gitee](https://gitee.com/from-scratch-to-development/zerotodev)，网站也重新部署了。
