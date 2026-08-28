from __future__ import annotations

import hashlib
import json
from pathlib import Path

from gem_reviewer.pipeline import run_review


def test_run_review_records_input_hash_and_writes_traceable_report(tmp_path: Path) -> None:
    gem_path = tmp_path / "gem.json"
    gem_payload = {
        "gem_version": "2026.08",
        "items": [
            {"id": "sample-1", "score": 0.8},
            {"id": "sample-2", "score": 0.6},
        ],
    }
    gem_path.write_text(json.dumps(gem_payload), encoding="utf-8")
    expected_hash = hashlib.sha256(gem_path.read_bytes()).hexdigest()

    report_path = run_review(
        gem_path=gem_path,
        output_dir=tmp_path / "outputs",
        source_url="https://example.org/gem/2026.08",
    )

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["input"]["sha256"] == expected_hash
    assert report["input"]["gem_version"] == "2026.08"
    assert report["summary"]["item_count"] == 2
    assert report["conclusions"] == [
        {
            "id": "item-count",
            "claim": "The GEM contains 2 items.",
            "evidence": ["summary.item_count"],
        }
    ]
    assert gem_path.read_text(encoding="utf-8") == json.dumps(gem_payload)


def test_run_review_refuses_to_overwrite_existing_output_directory(tmp_path: Path) -> None:
    gem_path = tmp_path / "gem.json"
    gem_path.write_text('{"items": []}', encoding="utf-8")
    output_dir = tmp_path / "outputs"
    output_dir.mkdir()
    (output_dir / "existing.txt").write_text("preserve", encoding="utf-8")

    try:
        run_review(gem_path=gem_path, output_dir=output_dir, source_url="https://example.org/gem")
    except FileExistsError as error:
        assert "not empty" in str(error)
    else:
        raise AssertionError("Expected an existing output directory to be rejected")
