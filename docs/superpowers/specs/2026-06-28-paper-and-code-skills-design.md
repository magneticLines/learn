# 论文与代码 Skill 套件 — 设计

日期：2026-06-28
分支：exp（git worktree）

## 背景与目标

本项目（`java_learn`）的 `0626/` 下有真实场景：

- `大作业2026.doc` —— 作业要求（旧版 `.doc`）
- `大作业报告模版.docx` —— 报告格式模板（`.docx`）

需要在本项目（当前 worktree `exp`）建立三个项目级 skill，覆盖：

1. **论文格式校对** —— 按指定的 `.docx` 样例模板，校对并修正目标论文格式
2. **论文内容编辑** —— 润色、结构调整、表述优化
3. **代码设计与实现** —— 作业代码的方案设计到落地实现

底层文档读写**复用官方 `anthropic-skills:docx`**，不重造轮子。

## 关键决策

| 决策点 | 选择 |
|---|---|
| 拆分方式 | 3 个独立 skill（单一职责、触发精准） |
| 安装位置 | 当前 worktree：`.claude/skills/` |
| 格式模板来源 | `.docx` 样例文件，可有多份，每次由用户指定参考哪一份 |
| 校对/编辑输出 | **直接原地修改**（git 作为安全网，原件可 `git checkout` 找回） |
| 代码 skill 形态 | 薄调度入口，复用 superpowers 工作流 |

## 文件结构

```
.claude/skills/
├── paper-format-check/
│   ├── SKILL.md                 # 主流程
│   └── scripts/
│       ├── extract_styles.py    # 样例 docx → 样式标准 JSON
│       └── check_format.py      # 目标 docx vs 标准 → 差异清单
├── paper-content-edit/
│   └── SKILL.md
└── code-design-impl/
    └── SKILL.md
```

## Skill 1：paper-format-check（核心）

**输入**：目标论文 `.docx` + 用户指定的样例模板 `.docx`。

**提取阶段**（`extract_styles.py`，基于 `python-docx`）从样例提取真实样式标准：

- 命名样式 Normal / Heading 1–4：中文字体、西文字体、字号、加粗、行距、对齐、段前段后间距、首行缩进
- 节级：页边距、纸张方向/大小
- 输出结构化 `style_spec.json` 作为"标准"

**校对阶段**（`check_format.py`）：

- 遍历目标论文每个段落 → 判定类别（标题层级 / 正文）→ 取实际格式
- 与标准逐项比对，生成差异清单：`段落预览 | 项目 | 当前值 | 期望值`
- 需正确处理"直接设在 run 上、覆盖命名样式"的常见情况（run 级属性优先于样式继承）

**修正阶段**：

- 默认**直接原地修改**目标 `.docx`，把不符合项改为标准值
- 修改后输出一份简短的"已修改项"摘要给用户
- 原件依赖 git 版本控制兜底

**边界**：`python-docx` 不支持旧版 `.doc`（如 `大作业2026.doc`）；校对只针对 `.docx`。

## Skill 2：paper-content-edit

- 通过 `anthropic-skills:docx` 读取目标 docx，按章节给出润色/结构/表述优化
- 结合 `elements-of-style` 写作规范
- **只改文字、不动样式**，直接原地修改
- 大改动前向用户确认要点，避免改变原意

## Skill 3：code-design-impl

薄调度入口，把作业代码需求接入已有工作流：

`brainstorming → writing-plans → TDD 实现 → code-review`

叠加本项目约定：Java / Spring Boot 包结构、测试放置位置、命名规范等。

## 依赖

- `anthropic-skills:docx`（文档读写）
- `python-docx`（样式提取/比对脚本；需确认环境已安装或在脚本内提示安装）
- `elements-of-style`（内容编辑写作规范）
- superpowers 工作流 skills（代码设计实现）

## 非目标（YAGNI）

- 不支持旧版 `.doc` 的样式校对
- 不做参考文献的引用编号自动重排（首版仅校对样式，不重建引文系统）
- 不做 PPT/PDF（已有官方 skill 覆盖）
