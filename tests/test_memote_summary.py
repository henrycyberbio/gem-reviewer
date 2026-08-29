from __future__ import annotations

import gzip
import hashlib
import json
import re
from pathlib import Path

import pytest
from fire.core import FireExit

from gem_reviewer.memote_summary import summarize_memote
from gem_reviewer.memote_summary_cli import main


CJK_PATTERN = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")


def _write_completed_run(output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir()
    result_path = output_dir / "memote-results.json.gz"
    result = {
        "meta": {"release": "synthetic"},
        "tests": {
            "test_stoichiometric_consistency": {
                "result": "failed",
                "message": "Synthetic raw message with non-English text: \u6d4b\u8bd5",
            },
            "test_biomass_consistency": {
                "result": {"biomass/a": "passed", "biomass~b": "failed"},
                "metric": {"biomass/a": 0.0, "biomass~b": 1.0},
            },
            "test_detect_energy_generating_cycles": {
                "result": {"ATP": "passed", "NADH": "skipped"},
                "metric": {"ATP": 0.0},
            },
            "test_future_case": {"result": "passed"},
        },
    }
    with gzip.open(result_path, "wt", encoding="utf-8") as stream:
        json.dump(result, stream)
    execution_path = output_dir / "memote-execution.json"
    execution_path.write_text(
        json.dumps(
            {
                "status": "completed",
                "memote_exit_code": 0,
                "input": {"unchanged": True},
                "environment": {"memote_version": "0.17.0"},
                "artifacts": {
                    "result": {
                        "path": result_path.name,
                        "present": True,
                        "sha256": hashlib.sha256(result_path.read_bytes()).hexdigest(),
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    return execution_path, result_path


def test_normalizes_scalar_and_parameterized_results_without_double_counting(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "synthetic-run"
    execution_path, result_path = _write_completed_run(output_dir)
    raw_before = {path: path.read_bytes() for path in (execution_path, result_path)}

    summary_path, findings_path, report_path = summarize_memote(
        output_dir=output_dir, report_dir=tmp_path / "reports"
    )

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["test_count"] == 4
    assert summary["case_count"] == 6
    assert summary["outcome_counts"] == {"passed": 3, "failed": 2, "skipped": 1}
    biomass = next(family for family in summary["families"] if family["family_id"] == "biomass")
    assert biomass["test_count"] == 1
    assert biomass["case_count"] == 2
    assert biomass["tests"][0]["parameterized"] is True
    assert [case["source_pointer"] for case in biomass["tests"][0]["cases"]] == [
        "#/tests/test_biomass_consistency/result/biomass~1a",
        "#/tests/test_biomass_consistency/result/biomass~0b",
    ]
    assert any(family["family_id"] == "miscellaneous" for family in summary["families"])

    findings = json.loads(findings_path.read_text(encoding="utf-8"))
    assert findings["language"] == "en"
    assert all(finding["language"] == "en" for finding in findings["families"])
    assert all("default test conditions" in finding["claim"] for finding in findings["families"])
    assert all("not biological conclusions" in finding["claim"] for finding in findings["families"])
    assert not CJK_PATTERN.search(json.dumps(summary, ensure_ascii=False))
    assert not CJK_PATTERN.search(json.dumps(findings, ensure_ascii=False))
    assert not CJK_PATTERN.search(report_path.read_text(encoding="utf-8"))
    assert report_path.name == "synthetic-run-report.md"
    assert all(path.read_bytes() == content for path, content in raw_before.items())


def test_rejects_incomplete_or_tampered_run(tmp_path: Path) -> None:
    output_dir = tmp_path / "incomplete-run"
    execution_path, result_path = _write_completed_run(output_dir)
    execution = json.loads(execution_path.read_text(encoding="utf-8"))
    execution["status"] = "timed_out"
    execution_path.write_text(json.dumps(execution), encoding="utf-8")
    with pytest.raises(ValueError, match="completed with exit code 0"):
        summarize_memote(output_dir=output_dir, report_dir=tmp_path / "reports")

    execution["status"] = "completed"
    execution_path.write_text(json.dumps(execution), encoding="utf-8")
    result_path.write_bytes(result_path.read_bytes() + b"tampered")
    with pytest.raises(ValueError, match="does not match"):
        summarize_memote(output_dir=output_dir, report_dir=tmp_path / "reports")


def test_refuses_to_overwrite_derived_artifacts(tmp_path: Path) -> None:
    output_dir = tmp_path / "existing-run"
    _write_completed_run(output_dir)
    (output_dir / "memote-summary.json").write_text("keep", encoding="utf-8")
    with pytest.raises(FileExistsError, match="Refusing to overwrite"):
        summarize_memote(output_dir=output_dir, report_dir=tmp_path / "reports")
    assert (output_dir / "memote-summary.json").read_text(encoding="utf-8") == "keep"


def test_fire_cli_uses_named_options(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    output_dir = tmp_path / "cli-run"
    _write_completed_run(output_dir)
    report_dir = tmp_path / "human-reports"
    monkeypatch.setattr(
        "sys.argv",
        [
            "gem-memote-summarize",
            "--output-dir",
            str(output_dir),
            "--report-dir",
            str(report_dir),
        ],
    )
    main()
    assert (output_dir / "memote-summary.json").is_file()
    assert (output_dir / "memote-findings.json").is_file()
    assert (report_dir / "cli-run-report.md").is_file()


def test_fire_cli_help_is_discoverable(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr("sys.argv", ["gem-memote-summarize", "--help"])
    with pytest.raises(FireExit) as exit_info:
        main()
    assert exit_info.value.code == 0
    output = capsys.readouterr()
    help_text = output.out + output.err
    assert "Normalize a completed MEMOTE run" in help_text
    assert "OUTPUT_DIR" in help_text
    assert "--report_dir" in help_text
