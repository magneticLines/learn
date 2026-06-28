---
name: paper-format-check
description: Use when checking or fixing a Word (.docx) paper's formatting against a specified .docx sample template — extracts the template's real styles (fonts, sizes, line spacing, alignment, indents, page margins) and corrects the target document in place. Triggers include "格式校对", "按模板检查格式", "对照模版排版".
---

# 论文格式校对

按用户指定的 `.docx` 样例模板，校对并**原地修正**目标论文格式。

## 何时使用
用户给出一份目标论文 `.docx` 和一份样例模板 `.docx`，要求"按模板校对/修正格式"。
仅支持 `.docx`（不支持旧版 `.doc`）。

## 流程

1. **确认输入**：让用户明确（a）目标论文路径（b）作为标准的样例模板路径。若有多份模板，必须确认用哪一份。
2. **提取标准**：
   ```bash
   python .claude/skills/paper-format-check/scripts/extract_styles.py "<模板.docx>" -o ./_style_spec.json
   ```
3. **比对差异**：
   ```bash
   python .claude/skills/paper-format-check/scripts/check_format.py "<目标.docx>" ./_style_spec.json -o ./_format_report.json
   ```
   把表格形式的差异清单展示给用户。
4. **原地修正**：依据差异清单，用 `anthropic-skills:docx` 技能修改目标 `.docx`（字体/字号/行距/对齐/缩进/页边距改为期望值）。**直接改原文件**——原件由 git 兜底，修改前先 `git status` 确认目标文件已在 git 跟踪或已备份。
5. **复核**：重新跑 step 3，确认 `✓ 未发现格式差异` 或仅剩无法自动处理项，向用户汇报已改动项摘要。
6. **清理**：删除临时文件 `./_style_spec.json`、`./_format_report.json`。

## 比对口径与局限（重要）
- **标准 = 样式定义值**：`extract_styles.py` 读取模板里每个命名样式的**样式定义**（裸样式继承值），而非模板正文里被直接排版覆盖后的实际效果。
- **实际 = 段落覆盖值**：`check_format.py` 对目标文档**每个命名样式取首个非空段落作代表**，读其有效格式（run 级直接排版优先于样式继承）。
- 因此：若文档大量用「直接排版」而非命名样式（标题、封面常见），自比对/校对会出现差异，这是**正常设计行为**——`render` 输出已含该说明行。汇报时需向用户点明这一口径，并对正文 `Normal` 重点核对。
- 工具按样式抽样一个代表段落，不逐段全量检查；个别段落的个性化偏差可能不被覆盖。

## 注意
- 中文字体读取的是 `w:eastAsia`，西文字体是 `w:ascii/hAnsi`，两者分别校对。
- 脚本运行需 `python-docx`（环境已安装 1.2.0）。从仓库根目录运行命令。
