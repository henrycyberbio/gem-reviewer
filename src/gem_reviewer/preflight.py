"""Read-only, evidence-producing preflight checks for frozen SBML GEMs."""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import cobra
import libsbml
from cobra.io import validate_sbml_model


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_source_manifest(path: Path) -> Mapping[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or not isinstance(manifest.get("artifact"), dict):
        raise ValueError(f"Source manifest must contain an artifact object: {path}")
    return manifest


def _write_json(path: Path, payload: Mapping[str, Any] | list[Mapping[str, Any]]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_preflight(*, gem_path: Path, source_manifest_path: Path, output_dir: Path) -> Path:
    """Validate a frozen SBML input and write evidence artifacts without mutating it."""
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"Output directory is not empty: {output_dir}")

    manifest = _read_source_manifest(source_manifest_path)
    artifact = manifest["artifact"]
    expected_hash = artifact.get("sha256")
    expected_size = artifact.get("byte_count")
    if not isinstance(expected_hash, str) or not isinstance(expected_size, int):
        raise ValueError("Source manifest artifact must declare sha256 and byte_count")

    sha256_before = _sha256(gem_path)
    byte_count = gem_path.stat().st_size
    if sha256_before != expected_hash or byte_count != expected_size:
        raise ValueError("Frozen GEM does not match source manifest")

    output_dir.mkdir(parents=True, exist_ok=True)
    model, validation = validate_sbml_model(str(gem_path))
    if model is None:
        raise ValueError("COBRApy could not load the SBML model")

    sha256_after = _sha256(gem_path)
    if sha256_after != sha256_before:
        raise RuntimeError("Frozen GEM changed while the preflight was running")

    validation_counts = {category: len(messages) for category, messages in validation.items()}
    finding_severity = "failure" if any("ERROR" in key or "FATAL" in key for key, count in validation_counts.items() if count) else "warning" if any("WARNING" in key for key, count in validation_counts.items() if count) else "info"
    input_integrity = {
        "gem_path": str(gem_path),
        "source_manifest_path": str(source_manifest_path),
        "byte_count": byte_count,
        "sha256_before": sha256_before,
        "sha256_after": sha256_after,
        "matches_source_manifest": True,
    }
    environment = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "cobra_version": cobra.__version__,
        "libsbml_version": libsbml.getLibSBMLDottedVersion(),
    }
    structural_summary = {
        "model_id": model.id,
        "entity_counts": {
            "metabolites": len(model.metabolites),
            "reactions": len(model.reactions),
            "genes": len(model.genes),
        },
        "compartments": dict(sorted(model.compartments.items())),
        "objective_direction": model.objective.direction,
        "objective_reaction_ids": sorted(
            reaction.id for reaction in model.reactions if reaction.objective_coefficient != 0
        ),
        "boundary_reaction_counts": {
            "exchanges": len(model.exchanges),
            "demands": len(model.demands),
            "sinks": len(model.sinks),
        },
    }
    findings = [
        {
            "id": "input-integrity",
            "language": "en",
            "claim": "The frozen GEM bytes match the approved source manifest before and after preflight.",
            "severity": "info",
            "evidence": [{"kind": "generated-output", "locator": "input-integrity.json"}],
            "limitations": ["Hash equality establishes byte identity, not model correctness."],
        },
        {
            "id": "sbml-validation",
            "language": "en",
            "claim": "COBRApy SBML validation diagnostics were captured without modifying the frozen GEM.",
            "severity": finding_severity,
            "evidence": [{"kind": "generated-output", "locator": "sbml-validation.json"}],
            "limitations": ["Format and parser diagnostics do not establish biological validity."],
        },
    ]
    _write_json(output_dir / "input-integrity.json", input_integrity)
    _write_json(output_dir / "environment.json", environment)
    _write_json(output_dir / "sbml-validation.json", validation)
    _write_json(output_dir / "structural-summary.json", structural_summary)
    findings_path = output_dir / "findings.json"
    _write_json(findings_path, findings)
    return findings_path
