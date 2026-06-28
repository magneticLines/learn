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


def _style_format(doc, style):
    """在样例 doc 内临时插入一个该样式的段落，复用 effective_format 解析，
    随后移除该临时段落，使提取结果反映样例文档自身的样式定义。"""
    p = doc.add_paragraph("x")
    try:
        p.style = style.name
    except Exception:
        p._element.getparent().remove(p._element)
        return None
    try:
        fmt = ds.effective_format(p)
    finally:
        p._element.getparent().remove(p._element)
    fmt.pop("style", None)
    return fmt


def extract(docx_path):
    doc = Document(docx_path)
    styles = {}
    for s in doc.styles:
        if s.type == WD_STYLE_TYPE.PARAGRAPH:
            fmt = _style_format(doc, s)
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
