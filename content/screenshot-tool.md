Title: 让 Claude Code 也能"看图"——我开发了一个截图分析工具
Date: 2026-06-04 02:30
Category: 博客
Tags: AI, Claude Code, Python, 工具开发, 视觉识别
Slug: screenshot-tool
Author: ZeroToDev
Summary: Claude Code 终端版不能看图，每次都要截图→粘贴→描述，太痛苦了。我决定自己动手做个工具。这中间踩了不少坑，来回改了好几版，最终做成了一个通用的截图分析 Skill。

## 起因：终端不能看图，太痛苦了

我一直用 Claude Code 写代码，它是终端版的 AI 助手。但有个硬伤——**终端读不了图片**。

每次我遇到界面问题、设计稿、或者报错截图，都要：

1. 先截图
2. 再手动粘贴到对话框
3. 还得打字描述"你看这个图..."
4. 等 Claude 分析完再问具体的

太麻烦了。特别是跟网页版的一比（网页版直接黏贴图片就行），感觉回到原始时代。

而且 Claude Code 接 DeepSeek 之类的模型时，终端根本传不了图片，体验很差。

## 第一次尝试：托盘截图工具

最开始我打算做一个系统托盘程序，常驻后台，一键截图自动分析。

### 方案设计

想法很简单：
- 系统托盘里放个蓝色图标
- 按 Ctrl+Shift+Z 调出截图选框
- 选完区域自动发到 MiMo API 分析
- 结果弹窗显示，能复制、能追问

### 踩坑记录

**第一个坑：托盘图标不显示**

我用 Python 的 pystray 库做了托盘图标，结果：
- 双击启动后啥也没看到
- 调试发现进程确实在跑
- 原来图标藏在系统托盘折叠区（^ 箭头下面）
- 而且还启动了多个重复进程，托盘区出现了好几个蓝色 M 图标

**第二个坑：最大化窗口闪退**

中间有次我点终端最大化，结果 PowerShell 直接崩溃了。

查日志发现是 conhost.exe 的 BEX64 缓冲区溢出 bug：
```
应用程序: conhost.exe
异常类型: BEX64 (0xc0000409)
```

最后通过设置 Windows Terminal 为默认终端解决了，也不用担心再崩溃了。

**第三个坑：热键冲突**

设置 Ctrl+Shift+Z 做截图快捷键，结果半天没反应——
原来这个组合键被输入法占用了，根本触发不到我的程序。

换了 Ctrl+Shift+F1、Ctrl+Shift+F2，还把热键库从 pynput 换成 keyboard 又换成 Windows API RegisterHotKey。

**第四个坑：弹窗闪退循环**

好不容易能截图分析了，结果弹窗关了又自动弹——

原因：分析完后清除剪贴板的逻辑没写好，剪贴板里的图又被检测到了，陷入无限循环 "分析→弹窗→关→分析→弹窗→关..."

最终方案是分析完后 echo off | clip 清掉剪贴板 + 3 秒冷却时间。

## 第二次尝试：去托盘化

托盘程序太折腾了，干脆去掉 pystray，改成纯后台热键监听。

用 keyboard 库注册全局热键，控制台窗口显示"就绪"状态。

结果 keyboard 库在 Windows 后台也时不时掉线，热键监听不稳。

最后换成 Windows 原生 API GetAsyncKeyState 轮询 + RegisterHotKey 消息循环，终于稳定了。

## 第三次尝试：剪贴板监听模式（最终版）

我突然想通了——既然用户截图就是为了给我看，为什么还要多此一举按热键？

改成这样：

1. 用户按 Win+Shift+S（或设好的截图快捷键）
2. 后台程序自动检测到剪贴板有新图片
3. 保存到固定位置 ~/.claude/screenshot/last_screenshot.png
4. 用户直接来对话框问我
5. 我读图分析，回答，删除截图

**没有弹窗，没有多余的步骤，没有要用户复制粘贴。**

### 最终的架构

```
用户截图 (Ctrl+Shift+X)
      ↓
watcher.py (后台监听剪贴板)
      ↓
保存到 last_screenshot.png
      ↓
用户来对话框问问题
      ↓
Claude 检测到新截图
      ↓
analyze.py 通过 API 分析
      ↓
回答用户，删除截图
```

只需要 pip install pillow requests 两个依赖，不需要托盘、不需要 X11、不需要任何额外服务。

## 做成 Skill，分享给更多人

这个工具不只能我自己用——所有用终端 Claude Code 的人都有这个痛点。

所以我把它做成了 ECC Skill（/screenshot-tool），并且改造成通用多 API 支持：

### 支持的多模态 API

| 服务商 | 接入方式 |
|--------|---------|
| 小米 MiMo | provider=mimo，原生支持 |
| 硅基流动 | provider=openai |
| 阿里 Qwen | provider=openai |
| 智谱 GLM | provider=openai |
| DeepSeek | provider=openai |
| OpenAI GPT-4o | provider=openai |
| Anthropic Claude | provider=anthropic |

### 安装方式

```bash
# 1. 装依赖
pip install pillow requests

# 2. 复制配置文件
cp ~/.claude/screenshot/config.sh.template ~/.claude/screenshot/config.sh

# 3. 编辑配置文件，填自己的 API Key
vim ~/.claude/screenshot/config.sh

# 4. 启动监听器
pythonw ~/.claude/screenshot/watcher.py &

# 5. 截图，来问 Claude
```

### 核心代码

**watcher.py** — 剪贴板监听器（约 50 行）：
```python
import PIL.ImageGrab, subprocess, time
while True:
    img = PIL.ImageGrab.grabclipboard()
    if img and not seen:
        img.save("last_screenshot.png")
        subprocess.run(["cmd.exe", "/c", "echo off|clip"])
        time.sleep(1)
```

**analyze.py** — 通用视觉 API 调用器（支持 MiMo/OpenAI/Anthropic）：
```python
if provider == "mimo" or provider == "openai":
    # OpenAI 格式调用
    requests.post(f"{base}/chat/completions", json={"model": ...})
elif provider == "anthropic":
    # Anthropic 格式调用
    requests.post(f"{base}/messages", headers={"x-api-key": ...})
```

## 自动启动

为了让每个新对话都能自动使用，我把配置写进了 CLAUDE.md：

> 每次新会话自动检查 watcher 是否在运行，不在则启动。
> 用户不需要手动点任何东西。

## 遇到的坑总结

### Windows 终端崩溃

点最大化按钮时 PowerShell 崩了，查日志确认是 conhost.exe 的 BEX64 异常。这是 Windows 10 传统控制台宿主的历史 bug。安装 Windows Terminal 后解决。

### Python 后台进程管理

用 pythonw.exe 可以无窗口运行 Python 脚本。但调试时进程容易重复启动，退出清理也不干净。需要 taskkill 手动杀。

### 热键方案演变

从 pynput → keyboard → GetAsyncKeyState 轮询 → RegisterHotKey Windows API。最终结论：在 Windows 上做全局热键，用原生 API 最靠谱。

### 剪贴板循环

分析完后不清剪贴板 → 又被检测到 → 死循环。解决：分析完后执行 echo off | clip 清空剪贴板，再加冷却时间。

### API 适配

MiMo 和 OpenAI 的接口格式几乎一样，但 Anthropic 的 Claude API 格式完全不同（用 x-api-key 头 + 不同的 request body）。analyze.py 里做了分支处理，让用户切换 provider 只需改配置文件。

## 总结

从崩溃前的托盘程序，到最终的剪贴板监听器，虽然绕了不少路，但学到了很多东西：

1. Windows 终端编程的坑 — conhost.exe 崩溃、热键冲突、后台进程管理
2. Python GUI 编程 — tkinter 选框、pystray 托盘
3. Windows API — RegisterHotKey、GetAsyncKeyState、消息循环
4. 多 API 适配 — OpenAI 格式 vs Anthropic 格式的差异
5. 产品思维 — 从"我做了一个功能给你用"到"让用户在不知不觉中用完"

最重要的是想清楚了一个道理：**工具应该适配人的习惯，而不是让人去适配工具。**

所有的代码都在 GitHub 和 Gitee 上，欢迎围观和吐槽。

下一期预告：这个工具的思路还可以扩展——不仅是截图，能不能监听剪贴板里的文件、代码片段？做一个小型的"剪贴板 AI 管家"？敬请期待。
