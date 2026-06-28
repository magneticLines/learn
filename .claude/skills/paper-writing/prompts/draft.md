# Prompt — Paper Draft Generation

## Task
Generate a complete academic paper draft (or outline) based on the user's research topic, field, and requirements.

## Input Variables
- `{{topic}}` — Research topic or title
- `{{field}}` — Academic discipline (e.g., computer science, biology, economics)
- `{{template}}` — Target journal/conference template (ieee | acm | nature | chinese)
- `{{lang}}` — Output language (en | zh)
- `{{mode}}` — Output mode: `outline` (section headings + bullet points) or `full` (complete draft)

## Instructions

1. Start with a brief clarification of the paper's research question and contribution.
2. Generate the structure according to `{{template}}`:
   - **IMRaD** (Introduction, Methods, Results, and Discussion) for empirical papers
   - **Survey structure** for review papers
   - **Chinese journal structure** for `chinese` template (按照中文核心期刊规范)
3. For `full` mode, write each section with appropriate academic language.
4. Mark all data-dependent content with `<!-- TODO: insert real data -->`.
5. Append a placeholder References section at the end.

## Example Output (outline mode, IEEE template)

```
# [Paper Title]

## Abstract
<!-- TODO: write after completing full draft -->

## I. Introduction
- Background and motivation
- Problem statement
- Main contributions (bullet list)
- Paper organization

## II. Related Work
- Subtopic A
- Subtopic B

## III. Methodology
- System overview
- Component 1
- Component 2

## IV. Experiments
- Setup
- Results
- Analysis

## V. Conclusion

## References
<!-- TODO: add formatted references -->
```
