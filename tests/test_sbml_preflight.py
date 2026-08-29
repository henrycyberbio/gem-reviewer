from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from gem_reviewer.preflight import run_preflight


GEM_PATH = Path("data/gem/iEC1372_W3110.xml")
SOURCE_MANIFEST_PATH = Path("data/gem/iEC1372_W3110.source.json")


def test_preflight_writes_traceable_read_only_artifacts(tmp_path: Path) -> None:
    before_hash = hashlib.sha256(GEM_PATH.read_bytes()).hexdigest()

    output_dir = tmp_path / "preflight"
    result = run_preflight(
        gem_path=GEM_PATH,
        source_manifest_path=SOURCE_MANIFEST_PATH,
        output_dir=output_dir,
    )

    input_integrity = json.loads((output_dir / "input-integrity.json").read_text(encoding="utf-8"))
    structural_summary = json.loads((output_dir / "structural-summary.json").read_text(encoding="utf-8"))
    findings = json.loads((output_dir / "findings.json").read_text(encoding="utf-8"))

    assert result == output_dir / "findings.json"
    assert input_integrity["sha256_before"] == before_hash
    assert input_integrity["sha256_after"] == before_hash
    assert input_integrity["matches_source_manifest"] is True
    assert structural_summary["entity_counts"] == {
        "genes": 1372,
        "metabolites": 1918,
        "reactions": 2758,
    }
    assert {finding["id"] for finding in findings} == {"input-integrity", "sbml-validation"}
    assert hashlib.sha256(GEM_PATH.read_bytes()).hexdigest() == before_hash


def test_preflight_rejects_a_nonempty_output_directory(tmp_path: Path) -> None:
    output_dir = tmp_path / "preflight"
    output_dir.mkdir()
    (output_dir / "existing.json").write_text("{}", encoding="utf-8")

    with pytest.raises(FileExistsError, match="not empty"):
        run_preflight(
            gem_path=GEM_PATH,
            source_manifest_path=SOURCE_MANIFEST_PATH,
            output_dir=output_dir,
        )


def test_preflight_rejects_a_source_manifest_with_the_wrong_hash(tmp_path: Path) -> None:
    manifest = json.loads(SOURCE_MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest["artifact"]["sha256"] = "0" * 64
    wrong_manifest = tmp_path / "wrong.source.json"
    wrong_manifest.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="does not match source manifest"):
        run_preflight(
            gem_path=GEM_PATH,
            source_manifest_path=wrong_manifest,
            output_dir=tmp_path / "preflight",
        )
