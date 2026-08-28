"""Read-only summaries for frozen SBML GEM inputs."""

from __future__ import annotations

from pathlib import Path

from cobra.io import read_sbml_model


def count_entities(gem_path: Path) -> dict[str, int]:
    """Load an SBML GEM without writing to it and return core entity counts."""
    model = read_sbml_model(str(gem_path))
    return {
        "metabolites": len(model.metabolites),
        "reactions": len(model.reactions),
        "genes": len(model.genes),
    }
