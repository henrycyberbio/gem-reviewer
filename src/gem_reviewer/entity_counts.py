"""Print core entity counts for a frozen SBML GEM."""

from __future__ import annotations

import argparse
from pathlib import Path

from gem_reviewer.sbml import count_entities


def main() -> None:
    parser = argparse.ArgumentParser(description="Print metabolite, reaction, and gene counts from an SBML GEM.")
    parser.add_argument("--gem", required=True, type=Path, help="Path to a read-only SBML GEM")
    args = parser.parse_args()

    counts = count_entities(args.gem)
    print(f"Metabolites: {counts['metabolites']}")
    print(f"Reactions: {counts['reactions']}")
    print(f"Genes: {counts['genes']}")


if __name__ == "__main__":
    main()
