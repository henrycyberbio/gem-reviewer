"""CLI for read-only GEM SBML preflight checks."""

from __future__ import annotations

import argparse
from pathlib import Path

from gem_reviewer.preflight import run_preflight


def main() -> None:
    parser = argparse.ArgumentParser(description="Write read-only SBML preflight artifacts for a frozen GEM.")
    parser.add_argument("--gem", required=True, type=Path, help="Path to the frozen SBML GEM")
    parser.add_argument("--source-manifest", required=True, type=Path, help="Path to the approved source manifest")
    parser.add_argument("--output-dir", required=True, type=Path, help="New or empty directory for generated artifacts")
    args = parser.parse_args()

    print(
        run_preflight(
            gem_path=args.gem,
            source_manifest_path=args.source_manifest,
            output_dir=args.output_dir,
        )
    )


if __name__ == "__main__":
    main()
