---
name: paper-content-edit
description: Use when polishing or restructuring the textual content of a Word (.docx) paper — improving academic phrasing, fixing structure, tightening expression — while preserving all existing formatting/styles. Triggers include "润色论文", "改写表述", "调整结构", "论文内容编辑". For format/style checking against a template use paper-format-check instead.
---

# 论文内容编辑

对论文正文做润色、结构调整、表述优化，**只改文字、不动样式**，原地修改。

## 何时使用
用户要求润色/改写/精简论文文字，或调整章节结构。不涉及字体字号等格式（那是 paper-format-check）。

## 流程

1. **读取**：用 `anthropic-skills:docx` 读取目标 `.docx` 内容（按章节）。
2. **诊断**：结合 `elements-of-style:writing-clearly-and-concisely` 的规则，逐章给出可改进点（冗余、被动堆叠、口语化、逻辑跳跃、术语不一致等）。
3. **确认要点**：对会改变原意或结构的大改动，先列要点请用户确认；纯语言润色可直接进行。
4. **原地修改**：用 `anthropic-skills:docx` 做 find-and-replace / 段落改写，**保留原段落样式与 run 格式**，不新增或删除样式。
5. **汇报**：列出本次改动的章节与性质（润色/精简/结构）。原件由 git 兜底。

## 注意
- 不杜撰数据、引用或结论；不确定处保留 `[待补]` 标记。
- 中文论文保持术语首次出现给出英文原文，如"联邦学习（Federated Learning）"。
- 改写时保持引用编号、图表编号不变。
