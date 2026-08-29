"""Fire CLI for a reproducible MEMOTE baseline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence

import fire

from gem_reviewer.memote_baseline import run_memote_baseline


def run(
    gem: str,
    source_manifest: str,
    output_dir: str,
    solver_timeout: int = 15,
    wall_timeout: int = 7200,
) -> None:
    """Run MEMOTE without modifying the frozen GEM.

    Args:
        gem: Path to the frozen SBML GEM.
        source_manifest: Path to the approved source manifest.
        output_dir: Brand-new directory for generated artifacts.
        solver_timeout: Per-optimization solver timeout in seconds.
        wall_timeout: Maximum MEMOTE process runtime in seconds.
    """
    execution_path = run_memote_baseline(
        gem_path=Path(gem),
        source_manifest_path=Path(source_manifest),
        output_dir=Path(output_dir),
        solver_timeout=solver_timeout,
        wall_timeout=wall_timeout,
    )
    print(execution_path)
    execution = json.loads(execution_path.read_text(encoding="utf-8"))
    if execution["status"] == "completed":
        return
    if execution["status"] == "timed_out":
        raise SystemExit(124)
    raise SystemExit(execution["memote_exit_code"] or 1)


def main(command: Sequence[str] | None = None) -> None:
    """Expose the baseline command through Python Fire."""
    fire.Fire(run, command=command, name="gem-memote-baseline")


if __name__ == "__main__":
    main()
