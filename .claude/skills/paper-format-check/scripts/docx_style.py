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
