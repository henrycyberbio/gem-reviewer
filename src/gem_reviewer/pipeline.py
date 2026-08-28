"""Deterministic review pipeline for immutable GEM JSON inputs."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _load_gem(gem_path: Path) -> tuple[bytes, Mapping[str, Any]]:
    """Read a GEM once without mutating it and validate the minimal JSON shape."""
    raw_bytes = gem_path.read_bytes()
    try:
        payload = json.loads(raw_bytes)
    except json.JSONDecodeError as error:
        raise ValueError(f"GEM must be valid JSON: {gem_path}") from error
    if not isinstance(payload, dict):
        raise ValueError("GEM root must be a JSON object")
    items = payload.get("items")
    if not isinstance(items, list):
        raise ValueError("GEM must contain an 'items' list")
    return raw_bytes, payload


def run_review(*, gem_path: Path, output_dir: Path, source_url: str) -> Path:
    """Create a self-contained, traceable review report without changing GEM."""
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"Output directory is not empty: {output_dir}")

    raw_bytes, gem = _load_gem(gem_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    gem_version = gem.get("gem_version", "undeclared")
    if not isinstance(gem_version, str):
        raise ValueError("'gem_version' must be a string when supplied")

    provenance = {
        "input_path": str(gem_path.resolve()),
        "source_url": source_url,
        "gem_version": gem_version,
        "sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "byte_count": len(raw_bytes),
        "reviewed_at_utc": datetime.now(UTC).isoformat(),
    }
    summary = {"item_count": len(gem["items"])}
    report = {
        "schema_version": "1.0",
        "input": provenance,
        "summary": summary,
        "conclusions": [
            {
                "id": "item-count",
                "claim": f"The GEM contains {summary['item_count']} items.",
                "evidence": ["summary.item_count"],
            }
        ],
        "limitations": [
            "Only structural review conclusions are produced until GEM-specific review criteria are supplied.",
        ],
    }
    (output_dir / "provenance.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    report_path = output_dir / "review.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report_path
