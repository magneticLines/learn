---
name: paper-writing
description: Use when drafting or generating academic paper content from a topic/requirements — outlines, full drafts, abstracts, literature reviews, figure/table captions, citation formatting, and language polishing. Supports bilingual (中文/English) writing with journal templates (IEEE/ACM/Nature/中文核心期刊/学报) and citation styles (APA/MLA/Chicago/IEEE/ACM/GB-T 7714). Triggers include "写论文", "生成大纲", "生成草稿", "文献综述", "格式化参考文献".
---

# 论文编写

从选题/要求生成论文内容。改造自开源 academic-paper-skill（见 ATTRIBUTION.md），prompt 与模板在本目录，由 Claude 直接执行，无需外部 API key。

## 能力（对应 prompts/ 中的 prompt 文件）

| 任务 | prompt 文件 | 说明 |
|---|---|---|
| 大纲/草稿 | `prompts/draft.md` | 按模板生成 outline 或 full 草稿 |
| 润色 | `prompts/polish.md` | 学术语言润色 |
| 引用格式化 | `prompts/cite.md` | APA/MLA/Chicago/IEEE/ACM/GB-T 7714 |
| 摘要 | `prompts/abstract.md` | 从全文生成摘要 |
| 文献综述 | `prompts/review.md` | 从参考文献列表生成综述 |
| 图题/表题 | `prompts/caption.md` | 生成专业图表题注 |

## 流程

1. 判断用户意图属于上表哪一类，**读取**对应的 `prompts/<file>.md` 作为本次执行的指令；同时读取 `prompts/system.md` 作为总体写作规则。
2. 若涉及期刊格式，按用户指定从 `templates/` 读取对应模板（ieee/acm/nature/chinese_journal/chinese_sci/chinese_social/chinese_science_series）。
3. 严格遵循 system.md 约定：
   - **语言自动检测**：中文输入→中文输出 + GB/T 7714；英文输入→英文输出 + APA。
   - **不杜撰**：不编造引用、数据、结果；需用户填写处标 `[PLACEHOLDER]` 或 `<!-- TODO -->`。
   - 中文术语首次出现保留英文原文。
4. 输出 Markdown（默认）；用户要 LaTeX 时输出 LaTeX。
5. 与其它 skill 协同：成稿后可交 `paper-content-edit` 润色、落入 docx 后交 `paper-format-check` 按模板校对格式。

## 注意
- 本 skill 不调用任何外部 LLM——所有内容由当前 Claude 会话直接生成，prompt 文件是给我执行的指令模板。
