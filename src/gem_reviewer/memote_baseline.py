"""Reproducible, read-only MEMOTE baseline runner."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import shutil
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from gem_reviewer.preflight import run_preflight


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _timestamp() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _artifact(path: Path, output_dir: Path) -> dict[str, Any]:
    present = path.is_file()
    return {
        "path": path.relative_to(output_dir).as_posix(),
        "present": present,
        "byte_count": path.stat().st_size if present else None,
        "sha256": _sha256(path) if present else None,
    }


def _project_relative_path(path: Path, *, fallback: str) -> str:
    """Return a portable path without exposing locations outside the project."""
    try:
        return path.relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return fallback


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _append_memote_finding(output_dir: Path, *, status: str, exit_code: int | None) -> None:
    findings_path = output_dir / "findings.json"
    findings = json.loads(findings_path.read_text(encoding="utf-8"))
    succeeded = status == "completed"
    findings.append(
        {
            "id": "memote-baseline-execution",
            "language": "en",
            "claim": (
                "MEMOTE completed and its raw log, collected result, and execution metadata were preserved."
                if succeeded
                else "MEMOTE did not complete successfully; available raw output and execution metadata were preserved."
            ),
            "severity": "info" if succeeded else "failure",
            "evidence": [
                {"kind": "generated-output", "locator": "memote-execution.json"},
                {"kind": "generated-output", "locator": "memote-run.log"},
                {"kind": "generated-output", "locator": "memote-results.json.gz"},
            ],
            "limitations": [
                "MEMOTE is a standardized quality baseline, not proof of biological validity.",
                f"The MEMOTE process exit code was {exit_code}." if exit_code is not None else "No MEMOTE process exit code was available.",
            ],
        }
    )
    _write_json(findings_path, findings)


def run_memote_baseline(
    *,
    gem_path: Path,
    source_manifest_path: Path,
    output_dir: Path,
    solver_timeout: int,
    wall_timeout: int,
) -> Path:
    """Run a bounded MEMOTE baseline while preserving the frozen input and raw artifacts."""
    if solver_timeout <= 0 or wall_timeout <= 0:
        raise ValueError("Solver and wall timeouts must each be a positive integer")

    gem_path = gem_path.resolve()
    source_manifest_path = source_manifest_path.resolve()
    output_dir = output_dir.resolve()
    hash_before = _sha256(gem_path)

    try:
        output_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError as error:
        raise FileExistsError(f"Output directory already exists: {output_dir}") from error

    run_preflight(
        gem_path=gem_path,
        source_manifest_path=source_manifest_path,
        output_dir=output_dir,
    )

    staged_input_path = output_dir / "memote-input.xml"
    shutil.copyfile(gem_path, staged_input_path)
    staged_hash = _sha256(staged_input_path)
    if staged_hash != hash_before:
        raise RuntimeError("Staged MEMOTE input does not match the frozen GEM")

    result_path = output_dir / "memote-results.json.gz"
    log_path = output_dir / "memote-run.log"
    memote_executable = shutil.which("memote") or "memote"
    subprocess_command = [
        str(Path(memote_executable).resolve()) if memote_executable != "memote" else memote_executable,
        "run",
        "--ignore-git",
        "--filename",
        str(result_path),
        "--solver-timeout",
        str(solver_timeout),
        str(staged_input_path),
    ]
    recorded_command = [
        "memote",
        "run",
        "--ignore-git",
        "--filename",
        result_path.name,
        "--solver-timeout",
        str(solver_timeout),
        staged_input_path.name,
    ]

    started_at = _timestamp()
    started_monotonic = time.monotonic()
    exit_code: int | None = None
    timed_out = False
    launch_error: str | None = None
    with log_path.open("wb") as log_file:
        try:
            completed = subprocess.run(
                subprocess_command,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                check=False,
                timeout=wall_timeout,
            )
            exit_code = completed.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
        except OSError as error:
            launch_error = type(error).__name__

    finished_at = _timestamp()
    duration_seconds = round(time.monotonic() - started_monotonic, 6)
    hash_after = _sha256(gem_path)
    input_unchanged = hash_before == hash_after

    if not input_unchanged:
        status = "input_changed"
    elif timed_out:
        status = "timed_out"
    elif launch_error is not None:
        status = "launch_error"
    elif exit_code == 0 and result_path.is_file():
        status = "completed"
    else:
        status = "failed"

    execution = {
        "schema_version": 1,
        "status": status,
        "command": recorded_command,
        "command_path_basis": "output_directory",
        "working_directory": "project-root",
        "started_at_utc": started_at,
        "finished_at_utc": finished_at,
        "duration_seconds": duration_seconds,
        "solver_timeout_seconds": solver_timeout,
        "wall_timeout_seconds": wall_timeout,
        "memote_exit_code": exit_code,
        "timed_out": timed_out,
        "launch_error": launch_error,
        "input": {
            "frozen_path": _project_relative_path(gem_path, fallback="frozen-input.xml"),
            "source_manifest_path": _project_relative_path(
                source_manifest_path, fallback="source-manifest.json"
            ),
            "staged_path": staged_input_path.relative_to(output_dir).as_posix(),
            "sha256_before": hash_before,
            "sha256_after": hash_after,
            "staged_sha256": staged_hash,
            "unchanged": input_unchanged,
        },
        "environment": {
            "memote_executable": "memote",
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "memote_version": importlib.metadata.version("memote"),
        },
        "artifacts": {
            "log": _artifact(log_path, output_dir),
            "result": _artifact(result_path, output_dir),
            "staged_input": _artifact(staged_input_path, output_dir),
        },
    }
    execution_path = output_dir / "memote-execution.json"
    _write_json(execution_path, execution)
    _append_memote_finding(output_dir, status=status, exit_code=exit_code)

    if not input_unchanged:
        raise RuntimeError("Frozen GEM changed while MEMOTE was running")
    return execution_path
