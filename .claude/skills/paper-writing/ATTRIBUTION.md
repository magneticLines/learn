# 来源与归属

本 skill 的 `prompts/` 与 `templates/` 改造自开源项目
[xiaoshuntian/academic-paper-skill](https://github.com/xiaoshuntian/academic-paper-skill)（MIT License，见 LICENSE）。

改造点：剥离其 npm CLI 与外部 LLM API 调用层，仅保留 prompt 与模板资产，
由 Claude 在 Claude Code 内直接执行，不依赖额外 API key。
