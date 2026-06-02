Title: Day 2：折腾 Codex CLI、EchoBird 和一堆 API Key 的一天
Date: 2026-06-02 23:50
Category: 博客
Tags: Codex, EchoBird, DeepSeek, Claude Code, API Key, 环境变量, conhost
Slug: day2-codex-echobird
Author: ZeroToDev
Summary: 第二天的折腾记录——装 Codex CLI、下载 EchoBird、更新 DeepSeek Key、发现终端最大化闪退的元凶，以及一个重要的教训：不是所有 AI 工具都能接国产模型

## 前言

Day 1 搭好了网站，Day 2 决定搞点硬核的——装 OpenAI 的 Codex CLI，再找个好用的 GUI 工具来管理 AI 模型。

结果一天下来，收获不少，坑也踩了不少。

---

## 一、装 Codex CLI

### 什么是 Codex CLI

Codex CLI 是 OpenAI 官方出的一个命令行 AI 编程助手，类似 Claude Code，但它是 OpenAI 家的。装了它就能在终端里跟 AI 对话、让它帮你写代码。

### 安装过程

```bash
npm install -g @openai/codex
```

一行命令，装上了 v0.136.0。过程很顺利，下载速度还行。

### ⚠️ 问题来了：登录墙

装完一跑 `codex doctor`，傻眼了：

```
✗ auth         stored credentials are incomplete
✗ reachability one or more required provider endpoints are unreachable
```

Codex 启动后弹出三个登录选项：
1. **Sign in with ChatGPT** — 需要 ChatGPT 账号
2. **Sign in with Azure** — 需要 Azure 账号
3. **Use API Key** — 需要 OpenAI API Key

**三个都要花钱，三个在国内网络下都不好使。**

ChatGPT 和 OpenAI 的 API 端点（`chatgpt.com`）在国内根本连不上，连 DNS 都解析不出来。

### 尝试接入 DeepSeek

不死心，试了用环境变量的方式接入 DeepSeek：

```powershell
[System.Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "你的DeepSeek Key", "User")
[System.Environment]::SetEnvironmentVariable("OPENAI_BASE_URL", "https://api.deepseek.com/v1", "User")
```

Codex 确实连上了 DeepSeek，显示 `model: deepseek-chat, provider: openai`，看起来没问题。但等了半天没有回复，最后超时了。

**原因：** Codex 用的是 OpenAI 的 **Responses API**，而 DeepSeek 支持的是 **Chat Completions API**，接口格式不兼容。

### 结论

> **Codex CLI 目前无法直接使用国产模型（DeepSeek、GLM 等）。**
>
> 它的 `--oss` 模式只支持本地的 Ollama 和 LMStudio，不支持在线 API 中转。

最后决定暂时放弃 Codex，先把 Claude Code 用好。

---

## 二、下载 EchoBird

### 什么是 EchoBird

EchoBird 是一个桌面端的 AI Agent 管理工具，可以配置各种模型（包括国产模型），提供 GUI 界面来使用 Claude Code、Codex 等工具。简单说就是一个"AI 工具的控制面板"。

### 下载过程

GitHub 地址：`https://github.com/edison7009/EchoBird`

下载 v5.1.5 Windows x64 安装包，8MB 左右。GitHub 下载速度一般，但还能接受。

### 体验

装好之后接入国产模型确实不错，DeepSeek、GLM 都能用。Claude Code 在小窗口里运行正常。

---

## 三、⚠️ 重大发现：终端最大化闪退

### 现象

EchoBird 里启动 Claude Code 时，会弹出一个黑色终端窗口（类似 cmd 的小窗口）。在小窗口状态下一切正常，但**只要点最大化按钮，窗口就闪退**。

闪退之后对话丢失，找了半天不知道去哪恢复。

### 排查过程

1. 先怀疑是 EchoBird 的 bug，去 GitHub Issues 搜了一圈，没找到相关报告
2. 打开 Windows 事件查看器，发现了关键线索：

```
事件名称: BEX64
P1: conhost.exe
P8: c0000409    ← 栈缓冲区溢出
```

3. **崩溃的不是 EchoBird，是 `conhost.exe`！**

`conhost.exe` 是 Windows 的控制台主机进程，所有终端窗口（cmd、PowerShell、以及 EchoBird 里嵌入的终端）都靠它来渲染。

### 根本原因

我的 Windows 10 版本是 `10.0.19041`（2004 版），这个版本的 `conhost.exe` 有已知的窗口大小调整崩溃 bug。当终端窗口从小尺寸突然变为最大化时，触发了缓冲区溢出，直接崩掉。

### 解决办法

| 方案 | 操作 |
|------|------|
| **最佳** | 更新 Windows 10 到最新版本，微软已修复此 bug |
| **临时** | 不用最大化按钮，用 `Win + ←/→` 分屏，或拖拽窗口边框 |
| **进阶** | 安装 Windows Terminal 替代 conhost |

### 恢复丢失的对话

好消息是 Claude Code 的对话历史保存在本地：

```
C:\Users\asus\.claude\projects\
```

恢复命令：

```bash
claude --resume              # 选择恢复哪个对话
claude --resume <session-id> # 恢复指定对话
```

---

## 四、更新 DeepSeek API Key

### 问题

之前的 DeepSeek API Key 过期了，Claude Code 连不上 DeepSeek。

### 解决

去 `https://platform.deepseek.com/api_keys` 新建了一个 Key，然后更新了三个地方：

**1. Hermes 配置文件**
```yaml
# C:\Users\asus\.hermes\config.yaml
- name: deepseek
  api_key: sk-新Key
```

**2. 系统环境变量**
```powershell
[System.Environment]::SetEnvironmentVariable("DEEPSEEK_API_KEY", "新Key", "User")
```

**3. VS Code Cline 插件**

Cline 的 API Key 存在 VS Code 的加密存储里，需要在插件设置界面手动更新。

⚠️ **教训：换 Key 的时候要记得所有用到这个 Key 的地方都要改，不然就会出现"这边能用那边不能用"的诡异问题。**

---

## 五、今天踩的坑总结

| # | 问题 | 原因 | 解决 |
|---|------|------|------|
| 1 | Codex 连不上 | 国内网络无法访问 chatgpt.com | 暂时无解，等网络环境改善 |
| 2 | Codex 接 DeepSeek 无响应 | Responses API 和 Chat Completions API 不兼容 | 放弃 Codex，用 Claude Code |
| 3 | 终端最大化闪退 | conhost.exe 栈溢出（Win10 旧版本 bug） | 更新系统或不点最大化 |
| 4 | Claude Code 连不上 DeepSeek | API Key 过期 | 新建 Key，更新所有配置 |
| 5 | 换 Key 后 Cline 还是不能用 | 只改了部分配置，遗漏了 VS Code 插件 | 手动在插件设置里更新 |

---

## 六、花了多少钱

| 项目 | 花费 |
|------|------|
| DeepSeek API | 充值中（旧 Key 过期） |
| Codex CLI | 免费（但用不了） |
| EchoBird | 免费 |
| Claude Code | 免费（接 DeepSeek 用） |
| 其他工具 | 免费 |

今天的花费：**基本为零**，主要花的是时间和耐心。

---

## 七、接下来的计划

- [ ] 测试 EchoBird + Codex 接国产模型的效果
- [ ] 更新 Windows 系统，修复 conhost 闪退问题
- [ ] 把博客自动部署到 Cloudflare Pages
- [ ] 继续学 Python

## 感想

今天最大的收获不是装了什么工具，而是学会了**排查问题的方法**。

终端闪退的时候，第一反应是"EchoBird 有 bug"。但实际去事件查看器一查，发现是 Windows 系统的问题。**不要凭感觉猜，要看日志。**

还有就是：**换 API Key 的时候，一定要把所有用到的地方都找出来一起改。** 这个教训值一顿火锅。

**ZeroToDev，Day 2 完成 ✅**
