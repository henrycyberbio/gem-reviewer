"""Fire CLI for completed MEMOTE result normalization."""

from __future__ import annotations

from pathlib import Path

import fire

from gem_reviewer.memote_summary import summarize_memote


def run(output_dir: str, report_dir: str = "reports") -> None:
    """Normalize a completed MEMOTE run and render its English report.

    Args:
        output_dir: Existing run directory containing raw MEMOTE result and execution files.
        report_dir: Directory for the run-specific Markdown report.
    """
    for path in summarize_memote(output_dir=Path(output_dir), report_dir=Path(report_dir)):
        print(path)


def main() -> None:
    """Expose result normalization through Python Fire."""
    fire.Fire(run, name="gem-memote-summarize")


if __name__ == "__main__":
    main()
