from __future__ import annotations

import json
import re
from pathlib import Path


CJK_PATTERN = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")
GEM_PATH = Path("data/gem/iEC1372_W3110.xml")
SOURCE_MANIFEST_PATH = Path("data/gem/iEC1372_W3110.source.json")


def test_preflight_findings_declare_english_and_contain_no_cjk(tmp_path: Path) -> None:
    from gem_reviewer.preflight import run_preflight

    output_dir = tmp_path / "preflight"
    run_preflight(
        gem_path=GEM_PATH,
        source_manifest_path=SOURCE_MANIFEST_PATH,
        output_dir=output_dir,
    )

    findings = json.loads((output_dir / "findings.json").read_text(encoding="utf-8"))
    assert all(finding["language"] == "en" for finding in findings)
    assert not CJK_PATTERN.search(json.dumps(findings, ensure_ascii=False))
