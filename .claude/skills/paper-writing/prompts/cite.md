# Prompt — Citation Formatter

## Task
Format a bibliographic reference in the specified citation style.

## Supported Styles
- `apa` — APA 7th Edition
- `mla` — MLA 9th Edition
- `chicago` — Chicago 17th Edition (author-date or notes-bibliography)
- `ieee` — IEEE Reference Style
- `acm` — ACM Reference Format
- `gbt7714` — GB/T 7714-2015 (中文国家标准，顺序编码制)

## Input
Raw reference information (any format) or DOI.

## Instructions

1. Parse the input to extract: authors, title, journal/conference, year, volume, issue, pages, DOI.
2. Format according to the requested style.
3. If information is missing, mark it as `[unknown]` — do NOT fabricate.
4. For `gbt7714`, output both the formatted citation and the in-text citation marker (e.g., `[1]`).

## Examples

**APA:**
> Zhang, W., Li, H., & Wang, Y. (2023). Deep learning for medical image segmentation. *Nature Machine Intelligence*, *5*(3), 112–125. https://doi.org/10.xxxx

**GB/T 7714:**
> 张伟, 李红, 王阳. 深度学习在医学图像分割中的应用[J]. 自然机器智能, 2023, 5(3): 112-125.
