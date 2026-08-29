from __future__ import annotations

import hashlib
import ipaddress
import json
import re
import subprocess
from pathlib import Path, PurePosixPath, PureWindowsPath

import pytest
from fire.core import FireExit

from gem_reviewer.memote_baseline import run_memote_baseline
from gem_reviewer.memote_baseline_cli import main


GEM_PATH = Path("data/gem/iEC1372_W3110.xml")
SOURCE_MANIFEST_PATH = Path("data/gem/iEC1372_W3110.source.json")
CJK_PATTERN = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")
IP_CANDIDATE_PATTERN = re.compile(r"(?<![0-9A-Fa-f:.])[0-9A-Fa-f:.]{3,}(?![0-9A-Fa-f:.])")


def _serialized_strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [
            item
            for pair in value.items()
            for child in pair
            for item in _serialized_strings(child)
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


def _fake_success(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[list[str]]:
    stdout = kwargs["stdout"]
    stdout.write(b"MEMOTE raw output\n")  # type: ignore[union-attr]
    stdout.flush()  # type: ignore[union-attr]
    result_path = Path(command[command.index("--filename") + 1])
    result_path.write_bytes(b"raw compressed MEMOTE result")
    return subprocess.CompletedProcess(command, 0)


def test_memote_baseline_preserves_raw_artifacts_and_records_execution_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    before_hash = hashlib.sha256(GEM_PATH.read_bytes()).hexdigest()
    observed_command: list[str] = []

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[list[str]]:
        observed_command.extend(command)
        assert command[0] == str((tmp_path / "bin" / "memote.exe").resolve())
        assert kwargs["stderr"] is subprocess.STDOUT
        assert kwargs["check"] is False
        assert kwargs["timeout"] == 120
        return _fake_success(command, **kwargs)

    monkeypatch.setattr("gem_reviewer.memote_baseline.subprocess.run", fake_run)
    monkeypatch.setattr(
        "gem_reviewer.memote_baseline.shutil.which",
        lambda executable: str(tmp_path / "bin" / f"{executable}.exe"),
    )
    output_dir = tmp_path / "baseline"

    execution_path = run_memote_baseline(
        gem_path=GEM_PATH,
        source_manifest_path=SOURCE_MANIFEST_PATH,
        output_dir=output_dir,
        solver_timeout=15,
        wall_timeout=120,
    )

    execution = json.loads(execution_path.read_text(encoding="utf-8"))
    findings = json.loads((output_dir / "findings.json").read_text(encoding="utf-8"))
    staged_input = output_dir / "memote-input.xml"

    assert execution_path == output_dir / "memote-execution.json"
    assert execution["status"] == "completed"
    assert execution["memote_exit_code"] == 0
    assert execution["timed_out"] is False
    assert execution["solver_timeout_seconds"] == 15
    assert execution["wall_timeout_seconds"] == 120
    assert execution["command"] == [
        "memote",
        "run",
        "--ignore-git",
        "--filename",
        "memote-results.json.gz",
        "--solver-timeout",
        "15",
        "memote-input.xml",
    ]
    assert execution["command_path_basis"] == "output_directory"
    assert execution["working_directory"] == "project-root"
    assert execution["input"]["sha256_before"] == before_hash
    assert execution["input"]["sha256_after"] == before_hash
    assert execution["input"]["unchanged"] is True
    assert execution["input"]["frozen_path"] == GEM_PATH.as_posix()
    assert execution["input"]["source_manifest_path"] == SOURCE_MANIFEST_PATH.as_posix()
    assert execution["artifacts"]["log"]["sha256"]
    assert execution["artifacts"]["result"]["sha256"]
    assert execution["artifacts"]["result"]["present"] is True
    assert execution["environment"]["memote_version"] == "0.17.0"
    assert execution["environment"]["memote_executable"] == "memote"
    assert observed_command[-1] == str(staged_input.resolve())
    assert str(GEM_PATH.resolve()) not in observed_command
    assert staged_input.read_bytes() == GEM_PATH.read_bytes()
    assert (output_dir / "memote-run.log").read_text(encoding="utf-8") == "MEMOTE raw output\n"
    assert (output_dir / "memote-results.json.gz").read_bytes() == b"raw compressed MEMOTE result"
    assert {finding["id"] for finding in findings} == {
        "input-integrity",
        "memote-baseline-execution",
        "sbml-validation",
    }
    assert all(finding["language"] == "en" for finding in findings)
    assert not CJK_PATTERN.search(json.dumps(findings, ensure_ascii=False))
    assert hashlib.sha256(GEM_PATH.read_bytes()).hexdigest() == before_hash

    serialized_strings = _serialized_strings(execution)
    assert not any(PurePosixPath(value).is_absolute() for value in serialized_strings)
    assert not any(PureWindowsPath(value).is_absolute() for value in serialized_strings)
    assert not any(_contains_ip_address(value) for value in serialized_strings)
    assert not any(part.lower() in json.dumps(execution).lower() for part in tmp_path.parts if part)


@pytest.mark.parametrize("create_file", [False, True])
def test_memote_baseline_rejects_any_existing_output_directory(
    tmp_path: Path, create_file: bool
) -> None:
    output_dir = tmp_path / "baseline"
    output_dir.mkdir()
    if create_file:
        (output_dir / "preserve.txt").write_text("preserve", encoding="utf-8")

    with pytest.raises(FileExistsError, match="already exists"):
        run_memote_baseline(
            gem_path=GEM_PATH,
            source_manifest_path=SOURCE_MANIFEST_PATH,
            output_dir=output_dir,
            solver_timeout=15,
            wall_timeout=120,
        )

    if create_file:
        assert (output_dir / "preserve.txt").read_text(encoding="utf-8") == "preserve"


def test_memote_baseline_keeps_metadata_and_log_when_memote_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_failure(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[list[str]]:
        stdout = kwargs["stdout"]
        stdout.write(b"MEMOTE failure details\n")  # type: ignore[union-attr]
        stdout.flush()  # type: ignore[union-attr]
        return subprocess.CompletedProcess(command, 7)

    monkeypatch.setattr("gem_reviewer.memote_baseline.subprocess.run", fake_failure)
    output_dir = tmp_path / "failed-baseline"

    execution_path = run_memote_baseline(
        gem_path=GEM_PATH,
        source_manifest_path=SOURCE_MANIFEST_PATH,
        output_dir=output_dir,
        solver_timeout=15,
        wall_timeout=120,
    )

    execution = json.loads(execution_path.read_text(encoding="utf-8"))
    assert execution["status"] == "failed"
    assert execution["memote_exit_code"] == 7
    assert execution["artifacts"]["result"]["present"] is False
    assert (output_dir / "memote-run.log").read_text(encoding="utf-8") == "MEMOTE failure details\n"
    assert execution["input"]["unchanged"] is True


def test_memote_baseline_records_timeout_and_preserves_partial_log(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_timeout(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[list[str]]:
        stdout = kwargs["stdout"]
        stdout.write(b"partial MEMOTE output\n")  # type: ignore[union-attr]
        stdout.flush()  # type: ignore[union-attr]
        raise subprocess.TimeoutExpired(command, timeout=kwargs["timeout"])

    monkeypatch.setattr("gem_reviewer.memote_baseline.subprocess.run", fake_timeout)
    output_dir = tmp_path / "timed-out-baseline"

    execution_path = run_memote_baseline(
        gem_path=GEM_PATH,
        source_manifest_path=SOURCE_MANIFEST_PATH,
        output_dir=output_dir,
        solver_timeout=15,
        wall_timeout=1,
    )

    execution = json.loads(execution_path.read_text(encoding="utf-8"))
    assert execution["status"] == "timed_out"
    assert execution["memote_exit_code"] is None
    assert execution["timed_out"] is True
    assert execution["input"]["unchanged"] is True
    assert (output_dir / "memote-run.log").read_text(encoding="utf-8") == "partial MEMOTE output\n"


@pytest.mark.parametrize("solver_timeout, wall_timeout", [(0, 1), (1, 0), (-1, 1)])
def test_memote_baseline_requires_positive_timeouts(
    tmp_path: Path, solver_timeout: int, wall_timeout: int
) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        run_memote_baseline(
            gem_path=GEM_PATH,
            source_manifest_path=SOURCE_MANIFEST_PATH,
            output_dir=tmp_path / f"baseline-{solver_timeout}-{wall_timeout}",
            solver_timeout=solver_timeout,
            wall_timeout=wall_timeout,
        )


def test_memote_baseline_fire_cli_parses_named_options_and_returns_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    output_dir = tmp_path / "cli-baseline"
    execution_path = output_dir / "memote-execution.json"
    observed: dict[str, object] = {}

    def fake_baseline(**kwargs: object) -> Path:
        observed.update(kwargs)
        output_dir.mkdir()
        execution_path.write_text(
            json.dumps({"status": "completed", "memote_exit_code": 0}),
            encoding="utf-8",
        )
        return execution_path

    monkeypatch.setattr("gem_reviewer.memote_baseline_cli.run_memote_baseline", fake_baseline)
    monkeypatch.setattr(
        "sys.argv",
        [
            "gem-memote-baseline",
            "--gem",
            str(GEM_PATH),
            "--source-manifest",
            str(SOURCE_MANIFEST_PATH),
            "--output-dir",
            str(output_dir),
            "--solver-timeout",
            "20",
            "--wall-timeout",
            "300",
        ],
    )
    main()

    assert observed["gem_path"] == GEM_PATH
    assert observed["source_manifest_path"] == SOURCE_MANIFEST_PATH
    assert observed["output_dir"] == output_dir
    assert observed["solver_timeout"] == 20
    assert observed["wall_timeout"] == 300
    assert capsys.readouterr().out.strip() == str(execution_path)


def test_memote_baseline_fire_cli_help_is_discoverable(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("sys.argv", ["gem-memote-baseline", "--help"])
    with pytest.raises(FireExit) as exit_info:
        main()

    output = capsys.readouterr()
    help_text = output.out + output.err
    assert exit_info.value.code == 0
    assert "Run MEMOTE without modifying the frozen GEM" in help_text
    assert "GEM" in help_text
    assert "SOURCE_MANIFEST" in help_text
    assert "OUTPUT_DIR" in help_text
    assert "--solver_timeout" in help_text
    assert "--wall_timeout" in help_text
