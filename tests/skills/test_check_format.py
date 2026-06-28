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


def test_render_empty_returns_sentinel():
    cf = _load()
    assert cf.render([]) == "✓ 未发现格式差异。"


def test_render_escapes_pipe():
    cf = _load()
    diff = {"style": "Normal", "field": "size_pt", "field_cn": "字号(pt)",
            "expected": 12.0, "actual": 10.0, "sample": "P(A|B)"}
    out = cf.render([diff])
    # 原始裸管道符（来自 sample）必须被转义
    assert "P(A\\|B)" in out
    # 数据行去掉转义序列后应恰好剩 6 个列分隔符（5 列结构）
    row = [ln for ln in out.splitlines() if ln.startswith("| Normal")][0]
    assert row.replace("\\|", "##").count("|") == 6
