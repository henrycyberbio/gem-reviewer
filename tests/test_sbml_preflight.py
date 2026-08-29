from __future__ import annotations

import hashlib
import ipaddress
import json
import re
from pathlib import Path, PurePosixPath, PureWindowsPath

import pytest

from gem_reviewer.preflight import run_preflight


GEM_PATH = Path("data/gem/iEC1372_W3110.xml")
SOURCE_MANIFEST_PATH = Path("data/gem/iEC1372_W3110.source.json")
IP_CANDIDATE_PATTERN = re.compile(r"(?<![0-9A-Fa-f:.])[0-9A-Fa-f:.]{3,}(?![0-9A-Fa-f:.])")


def _serialized_strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [
            item
            for key, child in value.items()
            for item in (*_serialized_strings(key), *_serialized_strings(child))
        ]
    if isinstance(value, list):
        return [item for child in value for item in _serialized_strings(child)]
    return []


def _contains_ip_address(value: str) -> bool:
    for candidate in IP_CANDIDATE_PATTERN.findall(value):
        try:
            ipaddress.ip_address(candidate.strip("."))
        except ValueError:
            continue
        return True
    return False


def test_preflight_writes_traceable_read_only_artifacts(tmp_path: Path) -> None:
    before_hash = hashlib.sha256(GEM_PATH.read_bytes()).hexdigest()

    output_dir = tmp_path / "preflight"
    result = run_preflight(
        gem_path=GEM_PATH.resolve(),
        source_manifest_path=SOURCE_MANIFEST_PATH.resolve(),
        output_dir=output_dir,
    )

    input_integrity = json.loads((output_dir / "input-integrity.json").read_text(encoding="utf-8"))
    structural_summary = json.loads((output_dir / "structural-summary.json").read_text(encoding="utf-8"))
    findings = json.loads((output_dir / "findings.json").read_text(encoding="utf-8"))

    assert result == output_dir / "findings.json"
    assert input_integrity["sha256_before"] == before_hash
    assert input_integrity["sha256_after"] == before_hash
    assert input_integrity["matches_source_manifest"] is True
    assert input_integrity["gem_path"] == GEM_PATH.as_posix()
    assert input_integrity["source_manifest_path"] == SOURCE_MANIFEST_PATH.as_posix()
    assert structural_summary["entity_counts"] == {
        "genes": 1372,
        "metabolites": 1918,
        "reactions": 2758,
    }
    assert {finding["id"] for finding in findings} == {"input-integrity", "sbml-validation"}
    assert hashlib.sha256(GEM_PATH.read_bytes()).hexdigest() == before_hash


def test_preflight_json_metadata_contains_no_absolute_paths_or_ip_addresses(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "preflight"
    run_preflight(
        gem_path=GEM_PATH.resolve(),
        source_manifest_path=SOURCE_MANIFEST_PATH.resolve(),
        output_dir=output_dir,
    )

    serialized_strings = [
        item
        for artifact_path in output_dir.glob("*.json")
        for item in _serialized_strings(json.loads(artifact_path.read_text(encoding="utf-8")))
    ]

    assert not any(PurePosixPath(value).is_absolute() for value in serialized_strings)
    assert not any(PureWindowsPath(value).is_absolute() for value in serialized_strings)
    assert not any(_contains_ip_address(value) for value in serialized_strings)


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
