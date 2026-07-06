# AI-Agent 模块 · 设计文档

日期:2026-07-06

## 背景

现有学习项目的模块都以「一本(或多本)经典书为骨架」组织,骨架相对固定。
AI-Agent 领域概念、框架、开源项目迭代极快,没有一本教材能覆盖全貌,
也不适合用"一次性写完"的方式对待——它需要按照现有 CLAUDE.md 的
「路线图 + 1:1 叶子文件」规范落地,但骨架来源要换成「多本书 + 精选
GitHub 仓库/教程」的组合,并在框架文件里明确标注"持续演进,后续按需追加节点"。

## 目标

新增模块 `20-AI-Agent`,建立路线图框架 + 根 index 入口,本次先完成
框架文件和 index 卡片(节点内容待后续逐篇填充,叶子暂为 `<span class="leaf">`)。

## 目录结构

```
20-AI-Agent/
  ai-agent-roadmap.html      路线图框架文件
  concepts/                  Tab1 节点文件目录(概念与 AI 基础)
  development/                Tab2 节点文件目录(Agent 开发核心)
  frameworks/                 Tab3 节点文件目录(框架生态)
  dissection/                 Tab4 节点文件目录(OpenHands 源码拆解)
  practice/                   Tab5 节点文件目录(实战演练)
```

编号沿用根 index.html 现有序号顺序,新模块取 `20`。

## 路线图页面(ai-agent-roadmap.html)

复用 `19-系统设计/system-design-roadmap.html` 的暗色视觉与 Tab 交互结构
(`.tabs` / `.tab-panel` / `switchTab()`),主色调选未占用的靛蓝色 `#818cf8`。

### 顶部横幅调整

不用单一"骨架书"banner,改为「持续演进模块」说明框:
- 标注这个模块没有单一骨架书,而是多本书 + GitHub 精选仓库/教程组合
- 说明会随生态变化持续追加节点,当前是初始框架

### 5 个 Tab 及节点规划

1. **概念与 AI 基础**(`concepts/`)
   - 什么是 Agent(与传统程序、Chatbot 的区别)
   - LLM 基础回顾:Prompt / Token / Context Window
   - 主流模型能力边界与选型
   - Prompt Engineering 基础

2. **Agent 开发核心**(`development/`)
   - ReAct 循环(Reason + Act)
   - 工具调用(Function Calling)机制
   - 记忆机制:短期上下文 vs 长期记忆(向量库)
   - 规划与任务分解
   - 多 Agent 协作模式
   - 开发难点与业界解法:幻觉/上下文爆炸/工具调用可靠性/成本与延迟控制

3. **框架生态**(`frameworks/`)
   - LangChain / LangGraph
   - AutoGen / CrewAI
   - smolagents(HuggingFace)
   - 框架选型对比与取舍

4. **OpenHands 源码拆解**(`dissection/`)
   - 选定拆解对象:OpenHands(原 OpenDevin,~70k star,事件流架构清晰,文档教程完整)
   - 整体架构总览
   - Event-Stream 机制(Agent → Action → Environment → Observation)
   - Docker 沙箱与 Runtime 隔离设计
   - Agent 与 Runtime 解耦的设计取舍

5. **实战演练**(`practice/`)
   - Java 手写最小 Agent(ReAct 循环 + 工具调用,不依赖框架,贴合项目整体 Java 技术栈)
   - Python + 框架(LangChain/smolagents)实战一个小任务型 Agent,体验工业级开发方式

### 资源角(区别于其他模块的关键差异点)

每个 Tab 的 `part-src` 说明行之外,新增一行 **GitHub 教程/仓库推荐**
(外链样式,如 🔗 图标 + 仓库名),因为该领域的"活文档"常在 GitHub
README / awesome-list 里而非书本中。本次先在框架文件里为每个 Tab
填好占位推荐(书籍 + GitHub 链接各至少一条),节点文件后续填充时可引用。

## index.html 改动

在"Step 9 综合应用"之后新增一张卡片(不单独起新 Step,归入综合应用之后
的补充位置,或作为独立 Step 10,标题「持续演进 · AI 前沿」),要点:
- `count` 用 `pending` 样式,文案为"持续更新中"而非固定篇数
- desc 说明这是持续演进模块,覆盖概念/开发/框架/开源拆解/实战

## 范围边界

本次只完成:
1. `20-AI-Agent/ai-agent-roadmap.html` 框架文件(5 个 Tab,节点为待学 `<span class="leaf">`,资源角占位好书籍+GitHub链接)
2. 5 个空子目录占位(或按需在首篇文件产出时创建)
3. `index.html` 新增入口卡片

节点讲解文件(如"01-什么是Agent.html"等)不在本次范围内,后续按 CLAUDE.md
规范逐篇产出,产出一篇就把对应 `span.leaf` 换成 `a.leaf`。
