---
name: code-design-impl
description: Use when designing and implementing code for a coursework/assignment from scratch in this Java/Spring Boot project — routes the work through brainstorming → writing-plans → TDD → code-review. Triggers include "实现大作业代码", "设计并实现", "完成代码作业", "从需求到实现".
---

# 代码设计与实现

把作业代码需求接入既有 superpowers 工作流的调度入口。

## 何时使用
用户要从需求/作业要求出发，设计并实现一段较完整的代码（尤其是本项目的 Java/Spring Boot 大作业）。

## 流程

1. **理解需求**：若需求来自 `0626/大作业2026.doc` 等文档，先用 `anthropic-skills:docx` 读取要求（旧版 `.doc` 需先转换为 `.docx` 或让用户提供文本）。
2. **设计**：调用 `superpowers:brainstorming` 把需求澄清成设计与 spec。
3. **计划**：调用 `superpowers:writing-plans` 把 spec 拆成 bite-sized 任务计划。
4. **实现**：按计划用 `superpowers:test-driven-development` 逐任务实现，频繁提交。
5. **评审**：完成后用 `superpowers:requesting-code-review` / `code-reviewer` agent 复核。

## 本项目约定
- Java / Spring Boot：遵循现有包结构（见仓库 `src/` 与提交 `添加spring boot 项目基本结构`）。
- 测试与被测代码同模块对应放置，遵循 Maven/Gradle 约定目录。
- 命名、注释密度匹配周边既有代码。

## 注意
- 这是调度入口，不重复造工作流；具体纪律以被调用的 superpowers skill 为准。
