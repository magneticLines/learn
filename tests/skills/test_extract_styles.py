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
        capture_output=True,
    )
    assert r.returncode == 0, r.stderr.decode("utf-8", "replace")
    spec = json.loads(out.read_text(encoding="utf-8"))
    assert "page" in spec and "styles" in spec
    assert spec["styles"]["Normal"]["font_ascii"] == "Times New Roman"
    assert spec["styles"]["Normal"]["size_pt"] == 12.0
    assert spec["page"]["margins_pt"]["left"] is not None
