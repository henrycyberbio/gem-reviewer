from __future__ import annotations

import re
from pathlib import Path


CJK_PATTERN = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")
REPORT_PATH = Path("reports/iEC1372_W3110_REPORT.md")


def test_tracked_iEC1372_report_is_english_only() -> None:
    report = REPORT_PATH.read_text(encoding="utf-8")

    assert "**Language:** English" in report
    assert not CJK_PATTERN.search(report)
