# 论文与代码 Skill 套件 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在本项目 `.claude/skills/` 下建立四个项目级 skill：论文格式校对、论文内容编辑、论文编写、代码设计与实现。

**Architecture:** 文档读写复用官方 `anthropic-skills:docx`。格式校对额外用两个 `python-docx` 脚本（提取样式标准 → 比对差异），脚本走 TDD。论文编写改造自开源 `xiaoshuntian/academic-paper-skill`（取其 prompts/templates，封装为原生 SKILL.md，不装 npm）。代码 skill 是调度入口，串接 superpowers 工作流。默认原地修改文档，git 兜底。

**Tech Stack:** Markdown (SKILL.md)、Python 3.13 + python-docx 1.2.0、pytest。

---

## File Structure

```
.claude/skills/
├── paper-format-check/
│   ├── SKILL.md
│   └── scripts/
│       ├── docx_style.py        # 共用：解析有效格式（样式继承 + run 覆盖）
│       ├── extract_styles.py    # 样例 docx → style_spec.json
│       └── check_format.py      # 目标 docx vs style_spec.json → 差异清单
├── paper-content-edit/
│   └── SKILL.md
├── paper-writing/
│   ├── SKILL.md
│   ├── prompts/                 # 来自上游
│   └── templates/               # 来自上游
└── code-design-impl/
    └── SKILL.md

tests/skills/
├── conftest.py                  # 构造临时 docx 夹具
├── test_docx_style.py
├── test_extract_styles.py
└── test_check_format.py
```

**约束**：脚本所有读写 JSON 用 `ensure_ascii=False, encoding="utf-8"`；脚本入口在打印中文前执行 `sys.stdout.reconfigure(encoding="utf-8")`，避开 Windows 控制台 GBK 乱码。

---

## Task 0: 脚手架与环境确认

**Files:**
- Create: `.claude/skills/.gitkeep`
- Create: `tests/skills/__init__.py`

- [ ] **Step 1: 确认 pytest 可用**

Run: `python -m pytest --version`
Expected: 打印 pytest 版本号；若报错，先 `pip install pytest`。

- [ ] **Step 2: 建目录骨架**

```bash
mkdir -p .claude/skills/paper-format-check/scripts
mkdir -p .claude/skills/paper-content-edit
mkdir -p .claude/skills/paper-writing
mkdir -p .claude/skills/code-design-impl
mkdir -p tests/skills
touch tests/skills/__init__.py
```

- [ ] **Step 3: 提交**

```bash
git add tests/skills/__init__.py
git commit -m "chore: skill 套件目录骨架"
```

---

## Task 1: docx_style.py — 有效格式解析（共用模块）

解析一个段落/样式的「有效格式」：字号、加粗、西文字体、中文字体、对齐、行距、首行缩进、段前段后。这是格式校对的基础，必须正确处理「样式继承 + run 直接覆盖」。

**Files:**
- Create: `.claude/skills/paper-format-check/scripts/docx_style.py`
- Test: `tests/skills/test_docx_style.py`
- Create: `tests/skills/conftest.py`

- [ ] **Step 1: 写夹具 conftest.py**

```python
# tests/skills/conftest.py
import pytest
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH


@pytest.fixture
def sample_docx(tmp_path):
    """构造一个含命名标题 + Normal 正文的 docx，返回路径。"""
    doc = Document()

    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)

    h1 = doc.add_paragraph("一级标题", style="Heading 1")
    h1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in h1.runs:
        r.font.size = Pt(16)
        r.font.bold = True

    body = doc.add_paragraph("这是正文段落。")
    body.paragraph_format.first_line_indent = Pt(24)

    path = tmp_path / "sample.docx"
    doc.save(str(path))
    return str(path)
```

- [ ] **Step 2: 写失败测试 test_docx_style.py**

```python
# tests/skills/test_docx_style.py
import importlib.util
from pathlib import Path
from docx import Document

SCRIPT = Path(".claude/skills/paper-format-check/scripts/docx_style.py")


def _load():
    spec = importlib.util.spec_from_file_location("docx_style", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_effective_format_of_body_paragraph(sample_docx):
    ds = _load()
    doc = Document(sample_docx)
    body = [p for p in doc.paragraphs if p.text.startswith("这是正文")][0]
    fmt = ds.effective_format(body)
    assert fmt["font_ascii"] == "Times New Roman"   # 继承自 Normal
    assert fmt["size_pt"] == 12.0
    assert fmt["first_line_indent_pt"] == 24.0


def test_run_override_beats_style(sample_docx):
    ds = _load()
    doc = Document(sample_docx)
    h1 = [p for p in doc.paragraphs if p.text == "一级标题"][0]
    fmt = ds.effective_format(h1)
    assert fmt["size_pt"] == 16.0      # run 覆盖样式
    assert fmt["bold"] is True
    assert fmt["alignment"] == "CENTER"
```

- [ ] **Step 3: 运行测试确认失败**

Run: `python -m pytest tests/skills/test_docx_style.py -v`
Expected: FAIL（`docx_style.py` 不存在 / `effective_format` 未定义）。

- [ ] **Step 4: 实现 docx_style.py**

```python
# .claude/skills/paper-format-check/scripts/docx_style.py
"""解析 docx 段落/样式的有效格式（样式继承 + run 覆盖）。"""
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH

_ALIGN_NAME = {
    WD_ALIGN_PARAGRAPH.LEFT: "LEFT",
    WD_ALIGN_PARAGRAPH.CENTER: "CENTER",
    WD_ALIGN_PARAGRAPH.RIGHT: "RIGHT",
    WD_ALIGN_PARAGRAPH.JUSTIFY: "JUSTIFY",
}


def _emu_to_pt(v):
    return None if v is None else round(v / 12700.0, 2)


def _east_asian_from_rpr(rpr):
    """从 rPr XML 取中文字体名。"""
    if rpr is None:
        return None
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        return None
    return rfonts.get(qn("w:eastAsia"))


def _style_chain(style):
    """样式自身 + base_style 链，由近及远。"""
    chain = []
    s = style
    seen = set()
    while s is not None and id(s) not in seen:
        seen.add(id(s))
        chain.append(s)
        s = s.base_style
    return chain


def _first(values):
    for v in values:
        if v is not None:
            return v
    return None


def effective_format(paragraph):
    """返回段落的有效格式 dict。run 级优先，其次段落，其次样式链。"""
    runs = paragraph.runs
    first_run = runs[0] if runs else None
    style = paragraph.style
    chain = _style_chain(style)

    # 字号
    size_candidates = []
    if first_run is not None:
        size_candidates.append(first_run.font.size)
    size_candidates += [s.font.size for s in chain]
    size = _first(size_candidates)

    # 加粗
    bold_candidates = []
    if first_run is not None:
        bold_candidates.append(first_run.font.bold)
    bold_candidates += [s.font.bold for s in chain]
    bold = _first(bold_candidates)

    # 西文字体
    ascii_candidates = []
    if first_run is not None:
        ascii_candidates.append(first_run.font.name)
    ascii_candidates += [s.font.name for s in chain]
    font_ascii = _first(ascii_candidates)

    # 中文字体（读 XML）
    ea_candidates = []
    if first_run is not None:
        ea_candidates.append(_east_asian_from_rpr(first_run._element.find(qn("w:rPr"))))
    for s in chain:
        ea_candidates.append(_east_asian_from_rpr(s.element.find(qn("w:rPr"))))
    font_east_asian = _first(ea_candidates)

    pf = paragraph.paragraph_format
    align_candidates = [pf.alignment] + [s.paragraph_format.alignment for s in chain]
    alignment = _first(align_candidates)

    ls_candidates = [pf.line_spacing] + [s.paragraph_format.line_spacing for s in chain]
    line_spacing = _first(ls_candidates)

    fli_candidates = [pf.first_line_indent] + [s.paragraph_format.first_line_indent for s in chain]
    first_line_indent = _first(fli_candidates)

    space_before = _first([pf.space_before] + [s.paragraph_format.space_before for s in chain])
    space_after = _first([pf.space_after] + [s.paragraph_format.space_after for s in chain])

    # line_spacing 可能是 float（倍数）或 Length（精确值）；Length 不可 JSON 序列化，统一处理
    if line_spacing is None:
        ls_out = None
    elif isinstance(line_spacing, float):
        ls_out = round(line_spacing, 2)          # 倍数，如 1.5
    else:
        ls_out = f"{_emu_to_pt(line_spacing.emu)}pt"   # 精确值

    return {
        "style": style.name,
        "size_pt": _emu_to_pt(size.emu) if size is not None else None,
        "bold": bool(bold) if bold is not None else None,
        "font_ascii": font_ascii,
        "font_east_asian": font_east_asian,
        "alignment": _ALIGN_NAME.get(alignment),
        "line_spacing": ls_out,
        "first_line_indent_pt": _emu_to_pt(first_line_indent.emu) if first_line_indent is not None else None,
        "space_before_pt": _emu_to_pt(space_before.emu) if space_before is not None else None,
        "space_after_pt": _emu_to_pt(space_after.emu) if space_after is not None else None,
    }
```

- [ ] **Step 5: 运行测试确认通过**

Run: `python -m pytest tests/skills/test_docx_style.py -v`
Expected: PASS（2 passed）。

- [ ] **Step 6: 提交**

```bash
git add .claude/skills/paper-format-check/scripts/docx_style.py tests/skills/conftest.py tests/skills/test_docx_style.py
git commit -m "feat(format-check): docx 有效格式解析模块 + 测试"
```

---

## Task 2: extract_styles.py — 提取样式标准

从样例 docx 输出 `style_spec.json`：包含页面设置 + 每个命名样式的有效格式 + 默认正文(Normal)有效格式。

**Files:**
- Create: `.claude/skills/paper-format-check/scripts/extract_styles.py`
- Test: `tests/skills/test_extract_styles.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/skills/test_extract_styles.py
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = ".claude/skills/paper-format-check/scripts/extract_styles.py"


def test_extract_writes_spec(sample_docx, tmp_path):
    out = tmp_path / "spec.json"
    r = subprocess.run(
        [sys.executable, SCRIPT, sample_docx, "-o", str(out)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    spec = json.loads(out.read_text(encoding="utf-8"))
    assert "page" in spec and "styles" in spec
    assert spec["styles"]["Normal"]["font_ascii"] == "Times New Roman"
    assert spec["styles"]["Normal"]["size_pt"] == 12.0
    assert spec["page"]["margins_pt"]["left"] is not None
```

- [ ] **Step 2: 运行确认失败**

Run: `python -m pytest tests/skills/test_extract_styles.py -v`
Expected: FAIL（脚本不存在）。

- [ ] **Step 3: 实现 extract_styles.py**

```python
# .claude/skills/paper-format-check/scripts/extract_styles.py
"""从样例 docx 提取格式标准 → style_spec.json。

用法: python extract_styles.py <样例.docx> [-o spec.json]
"""
import argparse
import json
import sys
from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE

sys.path.insert(0, str(Path(__file__).parent))
import docx_style as ds


def _emu_to_pt(v):
    return None if v is None else round(v / 12700.0, 2)


def _page(doc):
    sec = doc.sections[0]
    return {
        "margins_pt": {
            "top": _emu_to_pt(sec.top_margin),
            "bottom": _emu_to_pt(sec.bottom_margin),
            "left": _emu_to_pt(sec.left_margin),
            "right": _emu_to_pt(sec.right_margin),
        },
        "page_width_pt": _emu_to_pt(sec.page_width),
        "page_height_pt": _emu_to_pt(sec.page_height),
    }


def _style_format(style):
    """对一个段落样式，构造一个临时段落以复用 effective_format。"""
    from docx import Document as _D
    tmp = _D()
    p = tmp.add_paragraph("x")
    try:
        p.style = style.name
    except Exception:
        return None
    fmt = ds.effective_format(p)
    fmt.pop("style", None)
    return fmt


def extract(docx_path):
    doc = Document(docx_path)
    styles = {}
    for s in doc.styles:
        if s.type == WD_STYLE_TYPE.PARAGRAPH:
            fmt = _style_format(s)
            if fmt:
                styles[s.name] = fmt
    return {"source": str(docx_path), "page": _page(doc), "styles": styles}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("docx")
    ap.add_argument("-o", "--out", default="style_spec.json")
    args = ap.parse_args()
    spec = extract(args.docx)
    Path(args.out).write_text(
        json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"已写出标准: {args.out}（{len(spec['styles'])} 个样式）")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 运行确认通过**

Run: `python -m pytest tests/skills/test_extract_styles.py -v`
Expected: PASS。

- [ ] **Step 5: 对真实模板冒烟**

Run: `python .claude/skills/paper-format-check/scripts/extract_styles.py "0626/大作业报告模版.docx" -o /tmp/tpl_spec.json && python -c "import json;d=json.load(open('/tmp/tpl_spec.json',encoding='utf-8'));print(list(d['styles'])[:5]); print(d['page'])"`
Expected: 打印样式名列表与页面设置，无异常。

- [ ] **Step 6: 提交**

```bash
git add .claude/skills/paper-format-check/scripts/extract_styles.py tests/skills/test_extract_styles.py
git commit -m "feat(format-check): 提取样式标准脚本 + 测试"
```

---

## Task 3: check_format.py — 比对生成差异清单

读 `style_spec.json` + 目标 docx，按命名样式比对，输出差异清单（JSON + 人类可读文本）。v1 比对维度：字号、加粗、西文字体、中文字体、对齐、行距、首行缩进；以及页边距。

**Files:**
- Create: `.claude/skills/paper-format-check/scripts/check_format.py`
- Test: `tests/skills/test_check_format.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/skills/test_check_format.py
import importlib.util
import json
from pathlib import Path
from docx import Document
from docx.shared import Pt

SCRIPT = Path(".claude/skills/paper-format-check/scripts/check_format.py")


def _load():
    spec = importlib.util.spec_from_file_location("check_format", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_target(tmp_path):
    doc = Document()
    doc.styles["Normal"].font.name = "SimSun"   # 与标准 Times New Roman 不符
    doc.styles["Normal"].font.size = Pt(10)     # 与标准 12 不符
    doc.add_paragraph("正文一段")
    p = tmp_path / "target.docx"
    doc.save(str(p))
    return str(p)


def test_detects_font_and_size_diff(tmp_path):
    cf = _load()
    spec = {"page": {"margins_pt": {}}, "styles": {
        "Normal": {"font_ascii": "Times New Roman", "size_pt": 12.0,
                   "bold": None, "font_east_asian": None, "alignment": None,
                   "line_spacing": None, "first_line_indent_pt": None}}}
    target = _make_target(tmp_path)
    diffs = cf.compare(target, spec)
    items = {(d["style"], d["field"]) for d in diffs}
    assert ("Normal", "font_ascii") in items
    assert ("Normal", "size_pt") in items
```

- [ ] **Step 2: 运行确认失败**

Run: `python -m pytest tests/skills/test_check_format.py -v`
Expected: FAIL（脚本不存在）。

- [ ] **Step 3: 实现 check_format.py**

```python
# .claude/skills/paper-format-check/scripts/check_format.py
"""比对目标 docx 与 style_spec.json，输出差异清单。

用法: python check_format.py <目标.docx> <style_spec.json> [-o report.json]
"""
import argparse
import json
import sys
from pathlib import Path

from docx import Document

sys.path.insert(0, str(Path(__file__).parent))
import docx_style as ds

# 比对字段及中文名
FIELDS = {
    "font_ascii": "西文字体",
    "font_east_asian": "中文字体",
    "size_pt": "字号(pt)",
    "bold": "加粗",
    "alignment": "对齐",
    "line_spacing": "行距",
    "first_line_indent_pt": "首行缩进(pt)",
}


def compare(target_path, spec):
    """返回差异列表，每项 {style, field, field_cn, expected, actual, sample}。"""
    doc = Document(target_path)
    diffs = []
    # 按样式分组：取目标里每个命名样式的「首个非空段落」作为代表
    seen = {}
    for p in doc.paragraphs:
        name = p.style.name
        if name in spec.get("styles", {}) and name not in seen and p.text.strip():
            seen[name] = p
    for name, para in seen.items():
        expected = spec["styles"][name]
        actual = ds.effective_format(para)
        for field, field_cn in FIELDS.items():
            exp = expected.get(field)
            act = actual.get(field)
            if exp is None:        # 标准未规定该项 → 跳过
                continue
            if act != exp:
                diffs.append({
                    "style": name,
                    "field": field,
                    "field_cn": field_cn,
                    "expected": exp,
                    "actual": act,
                    "sample": para.text.strip()[:20],
                })
    return diffs


def render(diffs):
    if not diffs:
        return "✓ 未发现格式差异。"
    lines = [f"发现 {len(diffs)} 处格式差异：", ""]
    lines.append("| 样式 | 段落预览 | 项目 | 期望 | 当前 |")
    lines.append("|---|---|---|---|---|")
    for d in diffs:
        lines.append(
            f"| {d['style']} | {d['sample']} | {d['field_cn']} | {d['expected']} | {d['actual']} |"
        )
    return "\n".join(lines)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("spec")
    ap.add_argument("-o", "--out")
    args = ap.parse_args()
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    diffs = compare(args.target, spec)
    if args.out:
        Path(args.out).write_text(
            json.dumps(diffs, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    print(render(diffs))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 运行确认通过**

Run: `python -m pytest tests/skills/test_check_format.py -v`
Expected: PASS。

- [ ] **Step 5: 全量脚本测试**

Run: `python -m pytest tests/skills/ -v`
Expected: 全部 PASS。

- [ ] **Step 6: 提交**

```bash
git add .claude/skills/paper-format-check/scripts/check_format.py tests/skills/test_check_format.py
git commit -m "feat(format-check): 差异比对脚本 + 测试"
```

---

## Task 4: paper-format-check/SKILL.md

**Files:**
- Create: `.claude/skills/paper-format-check/SKILL.md`

- [ ] **Step 1: 写 SKILL.md**

````markdown
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
   python .claude/skills/paper-format-check/scripts/extract_styles.py "<模板.docx>" -o /tmp/style_spec.json
   ```
3. **比对差异**：
   ```bash
   python .claude/skills/paper-format-check/scripts/check_format.py "<目标.docx>" /tmp/style_spec.json -o /tmp/format_report.json
   ```
   把表格形式的差异清单展示给用户。
4. **原地修正**：依据差异清单，用 `anthropic-skills:docx` 技能修改目标 `.docx`（字体/字号/行距/对齐/缩进/页边距改为期望值）。**直接改原文件**——原件由 git 兜底，修改前确认目标文件已在 git 跟踪或已备份。
5. **复核**：重新跑 step 3，确认 `✓ 未发现格式差异` 或仅剩无法自动处理项，向用户汇报已改动项摘要。

## 注意
- 脚本只读首个代表段落判断每个命名样式；若文档大量用直接排版而非命名样式，需在汇报中说明局限，并对正文 `Normal` 重点核对。
- 中文字体读取的是 `w:eastAsia`；西文字体是 `w:ascii/hAnsi`。两者分别校对。
- 修改前务必 `git status` 确认目标文件状态，便于回滚。
````

- [ ] **Step 2: 校验 frontmatter 与命名一致**

Run: `python -c "import re,io; t=open('.claude/skills/paper-format-check/SKILL.md',encoding='utf-8').read(); assert t.startswith('---'); assert 'name: paper-format-check' in t; print('ok')"`
Expected: 打印 `ok`。

- [ ] **Step 3: 提交**

```bash
git add .claude/skills/paper-format-check/SKILL.md
git commit -m "feat(format-check): SKILL.md 主流程"
```

---

## Task 5: paper-content-edit/SKILL.md

**Files:**
- Create: `.claude/skills/paper-content-edit/SKILL.md`

- [ ] **Step 1: 写 SKILL.md**

````markdown
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
````

- [ ] **Step 2: 校验**

Run: `python -c "t=open('.claude/skills/paper-content-edit/SKILL.md',encoding='utf-8').read(); assert 'name: paper-content-edit' in t; print('ok')"`
Expected: `ok`。

- [ ] **Step 3: 提交**

```bash
git add .claude/skills/paper-content-edit/SKILL.md
git commit -m "feat(content-edit): SKILL.md"
```

---

## Task 6: paper-writing — 改造开源 prompts/templates

把 `xiaoshuntian/academic-paper-skill`（已 clone 到临时目录）的 `prompts/` 与 `src/templates/` 复制进来，写 SKILL.md，保留 MIT 归属。

**Files:**
- Create: `.claude/skills/paper-writing/prompts/*`（复制）
- Create: `.claude/skills/paper-writing/templates/*`（复制）
- Create: `.claude/skills/paper-writing/SKILL.md`
- Create: `.claude/skills/paper-writing/ATTRIBUTION.md`

- [ ] **Step 1: 确认上游已 clone**

Run: `ls "$TEMP/academic-paper-skill/prompts" && ls "$TEMP/academic-paper-skill/src/templates"`
Expected: 列出 abstract.md/caption.md/cite.md/draft.md/polish.md/review.md/system.md 与各模板。若目录不存在，先：
`git clone --depth 1 https://github.com/xiaoshuntian/academic-paper-skill.git "$TEMP/academic-paper-skill"`

- [ ] **Step 2: 复制 prompts 与 templates**

```bash
cp "$TEMP/academic-paper-skill/prompts/"*.md .claude/skills/paper-writing/prompts/
cp "$TEMP/academic-paper-skill/src/templates/"*.md .claude/skills/paper-writing/templates/
cp "$TEMP/academic-paper-skill/LICENSE" .claude/skills/paper-writing/LICENSE
```

- [ ] **Step 3: 写 ATTRIBUTION.md**

```markdown
# 来源与归属

本 skill 的 `prompts/` 与 `templates/` 改造自开源项目
[xiaoshuntian/academic-paper-skill](https://github.com/xiaoshuntian/academic-paper-skill)（MIT License，见 LICENSE）。

改造点：剥离其 npm CLI 与外部 LLM API 调用层，仅保留 prompt 与模板资产，
由 Claude 在 Claude Code 内直接执行，不依赖额外 API key。
```

- [ ] **Step 4: 写 SKILL.md**

````markdown
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
````

- [ ] **Step 5: 校验文件齐全**

Run: `ls .claude/skills/paper-writing/prompts/ && ls .claude/skills/paper-writing/templates/ && python -c "t=open('.claude/skills/paper-writing/SKILL.md',encoding='utf-8').read(); assert 'name: paper-writing' in t; print('ok')"`
Expected: prompts 含 7 个 .md，templates 含模板，打印 `ok`。

- [ ] **Step 6: 提交**

```bash
git add .claude/skills/paper-writing/
git commit -m "feat(paper-writing): 改造开源 prompts/templates 为原生 skill"
```

---

## Task 7: code-design-impl/SKILL.md

**Files:**
- Create: `.claude/skills/code-design-impl/SKILL.md`

- [ ] **Step 1: 写 SKILL.md**

````markdown
---
name: code-design-impl
description: Use when designing and implementing code for a coursework/assignment from scratch in this Java/Spring Boot project — routes the work through brainstorming → writing-plans → TDD → code-review. Triggers include "实现大作业代码", "设计并实现", "完成代码作业", "从需求到实现".
---

# 代码设计与实现

把作业代码需求接入既有 superpowers 工作流的调度入口。

## 何时使用
用户要从需求/作业要求出发，设计并实现一段较完整的代码（尤其是本项目的 Java/Spring Boot 大作业）。

## 流程

1. **理解需求**：若需求来自 `0626/大作业2026.doc` 等文档，先用 `anthropic-skills:docx`（旧 .doc 需另行转换或让用户提供 .docx/文本）读取要求。
2. **设计**：调用 `superpowers:brainstorming` 把需求澄清成设计与 spec。
3. **计划**：调用 `superpowers:writing-plans` 把 spec 拆成 bite-sized 任务计划。
4. **实现**：按计划用 `superpowers:test-driven-development` 逐任务实现，频繁提交。
5. **评审**：完成后用 `superpowers:requesting-code-review` / `code-reviewer` agent 复核。

## 本项目约定
- Java / Spring Boot：遵循现有包结构（见仓库 `src/` 与 `5f4ae2c 添加spring boot 项目基本结构`）。
- 测试与被测代码同模块对应放置，遵循 Maven/Gradle 约定目录。
- 命名、注释密度匹配周边既有代码。

## 注意
- 这是调度入口，不重复造工作流；具体纪律以被调用的 superpowers skill 为准。
````

- [ ] **Step 2: 校验**

Run: `python -c "t=open('.claude/skills/code-design-impl/SKILL.md',encoding='utf-8').read(); assert 'name: code-design-impl' in t; print('ok')"`
Expected: `ok`。

- [ ] **Step 3: 提交**

```bash
git add .claude/skills/code-design-impl/SKILL.md
git commit -m "feat(code-design-impl): SKILL.md 调度入口"
```

---

## Task 8: 端到端验证

**Files:** 无（仅验证）

- [ ] **Step 1: 全量测试**

Run: `python -m pytest tests/skills/ -v`
Expected: 全部 PASS。

- [ ] **Step 2: 真实模板端到端冒烟**

Run:
```bash
python .claude/skills/paper-format-check/scripts/extract_styles.py "0626/大作业报告模版.docx" -o /tmp/tpl_spec.json
python .claude/skills/paper-format-check/scripts/check_format.py "0626/大作业报告模版.docx" /tmp/tpl_spec.json
```
Expected: 第二条对模板自身比对，应输出 `✓ 未发现格式差异`（自比对无差异）。

- [ ] **Step 3: 确认四个 SKILL.md 均被识别**

Run: `for d in paper-format-check paper-content-edit paper-writing code-design-impl; do test -f ".claude/skills/$d/SKILL.md" && echo "$d ok" || echo "$d MISSING"; done`
Expected: 四行均 `ok`。

- [ ] **Step 4: 最终提交（如有遗漏）**

```bash
git add -A
git commit -m "test: skill 套件端到端验证" || echo "nothing to commit"
```
