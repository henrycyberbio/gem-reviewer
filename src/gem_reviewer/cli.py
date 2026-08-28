"""Command-line interface for running a complete GEM review."""

from __future__ import annotations

import argparse
from pathlib import Path

from gem_reviewer.pipeline import run_review


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a traceable review of an immutable GEM JSON file.")
    parser.add_argument("--gem", required=True, type=Path, help="Path to the immutable GEM JSON file")
    parser.add_argument("--source-url", required=True, help="Public or internal source URL for the GEM")
    parser.add_argument("--output-dir", required=True, type=Path, help="New, empty directory for generated artifacts")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report_path = run_review(gem_path=args.gem, output_dir=args.output_dir, source_url=args.source_url)
    print(report_path)


if __name__ == "__main__":
    main()
