Title: 部署个人网站：从 Pelican 到 Cloudflare Pages
Date: 2026-06-03 22:45
Category: 博客
Tags: Pelican, Cloudflare, 部署, 静态网站
Slug: day3-deploy
Author: ZeroToDev
Summary: 用 Pelican 搭建静态博客，部署到 Cloudflare Pages，实现一键构建发布。记录整个流程和踩坑经历。

前两篇文章是在本地写的，网站一直只有我自己能看到。今天的目标很明确：**让这个网站上线**。

## 选型：为什么是 Pelican + Cloudflare Pages？

之前试过不少方案：

- **Hexo / Next.js** — 需要 Node.js 环境，对我这个 Python 初学者不太友好
- **WordPress** — 太重了，还要维护数据库
- **GitHub Pages** — 访问速度在国内不太理想

最后选了 **Pelican**（Python 静态站点生成器）+ **Cloudflare Pages**（免费托管）。

Pelican 最大的好处是：**用 Markdown 写文章，一个命令生成静态 HTML**。Python 生态对我这种刚入门的人也更友好。

Cloudflare Pages 的好处：
- 免费额度很慷慨
- 全球 CDN 加速
- 支持自定义域名
- 国内访问速度比 GitHub Pages 好

## 主题设计

既然是自己做，就不想用现成的模板。用了一晚上写了个自定义主题：

- 简洁的卡片式设计
- 支持亮色/暗色模式（跟随系统）
- 响应式布局，手机也能看
- 紫色系 accent 配色

CSS 直接手写，没上框架，因为站点结构简单，犯不着为了一个博客引一堆依赖。

## 部署踩坑记

### 第一步：修复配置

第一次构建时发现 `publishconf.py` 里的 `SITEURL` 还是 `example.com`，赶紧改成了实际域名。

### 第二步：安装 wrangler

用 Cloudflare Pages 需要 wrangler CLI 来上传文件：

```bash
npm install -g wrangler
npx wrangler login
```

登录 Cloudflare 账号后，它会生成一个 OAuth Token，之后部署就不用重复登录了。

### 第三步：一键部署脚本

不想每次打字敲长长的命令，写了个 `deploy.sh`：

```bash
# 先构建静态站点
pelican content -o output -s publishconf.py

# 再上传到 Cloudflare Pages
npx wrangler pages deploy output --project-name zerotodev --branch main
```

以后更新网站只需要：

```bash
bash deploy.sh
```

### 第四步：自动部署的计划

本来想搞 GitHub + Cloudflare Pages 自动同步——推送代码就自动构建部署。但国内连 GitHub 实在太慢了，连 CLI 都装不上。

退而求其次，目前在等 **Gitee Pages** 的实名认证审核。通过后，连 `deploy.sh` 都不用跑，`git push` 完 Gitee 自动帮我构建部署。

## 成果

网站已上线：[https://zerotodev-4jq.pages.dev](https://zerotodev-4jq.pages.dev)

从零搭建到部署完成，用了一晚上加一个傍晚。说麻烦也不算太麻烦，但踩的坑确实不少——网络问题、配置问题、工具链问题，一个一个解决过来。

## 感想

做这个网站本身就是一个学习过程：

1. **静态网站生成器** — 理解了 Markdown → HTML 的转换流程
2. **CSS 主题设计** — 手写了一套还算能看的样式
3. **云部署** — 接触了 CDN 和 CI/CD 的基本概念
4. **Git 工作流** — 日常使用 commit、push、pull

作为一个从零开始的人，每次搞定一个技术问题都挺有成就感的。虽然都是些基础操作，但能亲手把东西做出来放到网上让全世界看到，这感觉不错。

下一步计划：
- 写更多文章记录学习过程
- 完善网站样式和功能
- 做点小工具放上来

继续加油 🚀
