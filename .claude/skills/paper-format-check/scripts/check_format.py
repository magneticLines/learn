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


def _cell(v):
    """转义表格单元格：管道符与换行会破坏 markdown 表格结构。"""
    return str(v).replace("|", "\\|").replace("\n", " ")


def render(diffs):
    if not diffs:
        return "✓ 未发现格式差异。"
    lines = [f"发现 {len(diffs)} 处格式差异：", ""]
    lines.append("> 注：标准取“样式定义值”，实际取“段落覆盖值”；标题等含直接排版的样式可能因此显示差异。")
    lines.append("")
    lines.append("| 样式 | 段落预览 | 项目 | 期望 | 当前 |")
    lines.append("|---|---|---|---|---|")
    for d in diffs:
        lines.append(
            f"| {_cell(d['style'])} | {_cell(d['sample'])} | {_cell(d['field_cn'])} | {_cell(d['expected'])} | {_cell(d['actual'])} |"
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
