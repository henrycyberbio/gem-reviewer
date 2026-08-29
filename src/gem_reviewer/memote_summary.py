"""Normalize a completed MEMOTE result without changing its raw artifacts."""

from __future__ import annotations

import gzip
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


DIAGNOSTIC_SCOPE = (
    "MEMOTE default-condition diagnostics only; these results are not biological conclusions."
)
OUTCOMES = ("passed", "failed", "skipped")

# Frozen from MEMOTE 0.17.0's default test_config.yml. Keeping this small mapping
# here makes result normalization independent of MEMOTE's reporting dependencies.
FAMILIES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (
        "consistency",
        "Consistency",
        (
            "test_stoichiometric_consistency",
            "test_reaction_mass_balance",
            "test_reaction_charge_balance",
            "test_find_disconnected",
            "test_find_reactions_unbounded_flux_default_condition",
        ),
    ),
    (
        "annotation_metabolites",
        "Annotation - Metabolites",
        (
            "test_metabolite_annotation_presence",
            "test_metabolite_annotation_overview",
            "test_metabolite_annotation_wrong_ids",
            "test_metabolite_id_namespace_consistency",
        ),
    ),
    (
        "annotation_reactions",
        "Annotation - Reactions",
        (
            "test_reaction_annotation_presence",
            "test_reaction_annotation_overview",
            "test_reaction_annotation_wrong_ids",
            "test_reaction_id_namespace_consistency",
        ),
    ),
    (
        "annotation_genes",
        "Annotation - Genes",
        (
            "test_gene_product_annotation_presence",
            "test_gene_product_annotation_overview",
            "test_gene_product_annotation_wrong_ids",
        ),
    ),
    (
        "annotation_sbo",
        "Annotation - SBO Terms",
        (
            "test_metabolite_sbo_presence",
            "test_metabolite_specific_sbo_presence",
            "test_reaction_sbo_presence",
            "test_metabolic_reaction_specific_sbo_presence",
            "test_transport_reaction_specific_sbo_presence",
            "test_exchange_specific_sbo_presence",
            "test_demand_specific_sbo_presence",
            "test_sink_specific_sbo_presence",
            "test_gene_sbo_presence",
            "test_gene_specific_sbo_presence",
            "test_biomass_specific_sbo_presence",
        ),
    ),
    ("sbml", "SBML", ("test_sbml_level", "test_fbc_presence")),
    (
        "basic_information",
        "Basic Information",
        (
            "test_model_id_presence",
            "test_metabolites_presence",
            "test_reactions_presence",
            "test_genes_presence",
            "test_compartments_presence",
            "test_metabolic_coverage",
            "test_unconserved_metabolites",
            "test_inconsistent_min_stoichiometry",
        ),
    ),
    (
        "metabolite_information",
        "Metabolite Information",
        (
            "test_find_unique_metabolites",
            "test_find_duplicate_metabolites_in_compartments",
            "test_metabolites_charge_presence",
            "test_metabolites_formula_presence",
            "test_find_medium_metabolites",
        ),
    ),
    (
        "reaction_information",
        "Reaction Information",
        (
            "test_find_pure_metabolic_reactions",
            "test_find_constrained_pure_metabolic_reactions",
            "test_find_transport_reactions",
            "test_find_constrained_transport_reactions",
            "test_find_candidate_irreversible_reactions",
            "test_find_reactions_with_partially_identical_annotations",
            "test_find_duplicate_reactions",
            "test_find_reactions_with_identical_genes",
        ),
    ),
    (
        "gpr_associations",
        "Gene-Protein-Reaction (GPR) Associations",
        (
            "test_gene_protein_reaction_rule_presence",
            "test_transport_reaction_gpr_presence",
            "test_protein_complex_presence",
        ),
    ),
    (
        "biomass",
        "Biomass",
        (
            "test_biomass_presence",
            "test_biomass_consistency",
            "test_biomass_default_production",
            "test_fast_growth_default",
            "test_biomass_open_production",
            "test_biomass_precursors_default_production",
            "test_biomass_precursors_open_production",
            "test_direct_metabolites_in_biomass",
            "test_essential_precursors_not_in_biomass",
        ),
    ),
    (
        "energy_metabolism",
        "Energy Metabolism",
        (
            "test_ngam_presence",
            "test_gam_in_biomass",
            "test_find_reversible_oxygen_reactions",
            "test_detect_energy_generating_cycles",
        ),
    ),
    (
        "network_topology",
        "Network Topology",
        (
            "test_blocked_reactions",
            "test_find_orphans",
            "test_find_deadends",
            "test_find_stoichiometrically_balanced_cycles",
            "test_find_metabolites_not_produced_with_open_bounds",
            "test_find_metabolites_not_consumed_with_open_bounds",
        ),
    ),
    (
        "matrix_conditioning",
        "Matrix Conditioning",
        (
            "test_absolute_extreme_coefficient_ratio",
            "test_number_independent_conservation_relations",
            "test_matrix_rank",
            "test_degrees_of_freedom",
        ),
    ),
    (
        "experimental_data",
        "Experimental Data Comparison",
        (
            "test_growth_from_data_qualitative",
            "test_gene_essentiality_from_data_qualitative",
        ),
    ),
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _json_pointer_token(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def _outcome_counts(outcomes: list[str]) -> dict[str, int]:
    counts = Counter(outcomes)
    return {outcome: counts[outcome] for outcome in OUTCOMES}


def _family_lookup() -> dict[str, tuple[str, str]]:
    return {
        test_id: (family_id, title)
        for family_id, title, tests in FAMILIES
        for test_id in tests
    }


def _normalize_test(test_id: str, raw_test: Any) -> dict[str, Any]:
    if not isinstance(raw_test, dict):
        raise ValueError(f"MEMOTE test {test_id!r} must be an object")
    result = raw_test.get("result")
    result_pointer = f"#/tests/{_json_pointer_token(test_id)}/result"
    cases: list[dict[str, Any]] = []
    if isinstance(result, str):
        if result not in OUTCOMES:
            raise ValueError(f"MEMOTE test {test_id!r} has unknown outcome {result!r}")
        cases.append(
            {
                "outcome": result,
                "parameter": None,
                "source_pointer": result_pointer,
            }
        )
        parameterized = False
    elif isinstance(result, dict):
        parameterized = True
        for parameter, outcome in sorted(result.items()):
            if not isinstance(parameter, str) or outcome not in OUTCOMES:
                raise ValueError(f"MEMOTE test {test_id!r} has an invalid parameter outcome")
            cases.append(
                {
                    "outcome": outcome,
                    "parameter": parameter,
                    "source_pointer": f"{result_pointer}/{_json_pointer_token(parameter)}",
                }
            )
    else:
        raise ValueError(f"MEMOTE test {test_id!r} result must be a string or object")
    return {
        "case_count": len(cases),
        "cases": cases,
        "outcome_counts": _outcome_counts([case["outcome"] for case in cases]),
        "parameterized": parameterized,
        "test_id": test_id,
    }


def _validate_execution(execution: Any, result_path: Path) -> str:
    if not isinstance(execution, dict):
        raise ValueError("memote-execution.json must contain an object")
    if execution.get("status") != "completed" or execution.get("memote_exit_code") != 0:
        raise ValueError("MEMOTE execution must be completed with exit code 0")
    if execution.get("input", {}).get("unchanged") is not True:
        raise ValueError("MEMOTE execution does not confirm that the frozen GEM was unchanged")
    result_artifact = execution.get("artifacts", {}).get("result", {})
    expected_hash = result_artifact.get("sha256")
    if (
        result_artifact.get("present") is not True
        or result_artifact.get("path") != result_path.name
        or not isinstance(expected_hash, str)
        or _sha256(result_path) != expected_hash
    ):
        raise ValueError("Raw MEMOTE result does not match memote-execution.json")
    version = execution.get("environment", {}).get("memote_version")
    if not isinstance(version, str) or not version:
        raise ValueError("MEMOTE version is missing from memote-execution.json")
    return version


def _render_report(summary: dict[str, Any], findings: dict[str, Any], run_name: str) -> str:
    counts = summary["outcome_counts"]
    lines = [
        f"# MEMOTE Default-Condition Diagnostic Report: `{run_name}`",
        "",
        "**Language:** English  ",
        "**Scope:** MEMOTE default-condition diagnostics only; this report does not make biological conclusions.",
        "",
        "## Run evidence",
        "",
        f"- MEMOTE version: `{summary['memote_version']}`",
        f"- Completed execution: `{summary['sources']['execution']}`",
        f"- Raw result: `{summary['sources']['result']}` (SHA-256 `{summary['sources']['result_sha256']}`)",
        f"- Normalized evidence: `{summary['sources']['normalized_summary']}` and `{summary['sources']['findings']}`",
        "",
        "## Outcome summary",
        "",
        (
            f"Under MEMOTE {summary['memote_version']} default test conditions, "
            f"{summary['case_count']} terminal cases across {summary['test_count']} tests recorded "
            f"{counts['passed']} passed, {counts['failed']} failed, and {counts['skipped']} skipped outcomes."
        ),
        "Parameterized child cases are counted instead of their parent test, so no outcome is counted twice.",
        "",
        "| Test family | Tests | Cases | Passed | Failed | Skipped |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for family in summary["families"]:
        family_counts = family["outcome_counts"]
        lines.append(
            f"| {family['title']} | {family['test_count']} | {family['case_count']} | "
            f"{family_counts['passed']} | {family_counts['failed']} | {family_counts['skipped']} |"
        )
    lines.extend(["", "## Evidence-linked findings", ""])
    for finding in findings["families"]:
        lines.extend(
            [
                f"### {finding['title']}",
                "",
                finding["claim"],
                "",
                f"Evidence: `{finding['evidence'][0]['locator']}`.",
                "",
            ]
        )
    lines.extend(
        [
            "## Limitations",
            "",
            "- Passed, failed, and skipped are MEMOTE outcomes under its default configured conditions.",
            "- These diagnostics do not establish biological validity, phenotype accuracy, or suitability for a scientific use case.",
            "- Biological interpretation requires a separate, versioned protocol with explicit conditions and acceptance criteria.",
            "",
        ]
    )
    return "\n".join(lines)


def summarize_memote(*, output_dir: Path, report_dir: Path = Path("reports")) -> tuple[Path, Path, Path]:
    """Create normalized MEMOTE diagnostics and a human report for a completed run."""
    output_dir = output_dir.resolve()
    report_dir = report_dir.resolve()
    execution_path = output_dir / "memote-execution.json"
    result_path = output_dir / "memote-results.json.gz"
    summary_path = output_dir / "memote-summary.json"
    findings_path = output_dir / "memote-findings.json"
    run_name = output_dir.name
    if not re.fullmatch(r"[A-Za-z0-9._-]+", run_name):
        raise ValueError("Output directory name must be safe for a run-specific report filename")
    report_path = report_dir / f"{run_name}-report.md"

    if not output_dir.is_dir():
        raise FileNotFoundError(f"Output directory does not exist: {output_dir}")
    for required in (execution_path, result_path):
        if not required.is_file():
            raise FileNotFoundError(f"Required completed-run artifact is missing: {required}")
    for target in (summary_path, findings_path, report_path):
        if target.exists():
            raise FileExistsError(f"Refusing to overwrite derived artifact: {target}")

    raw_hashes_before = {path: _sha256(path) for path in (execution_path, result_path)}
    execution = json.loads(execution_path.read_text(encoding="utf-8"))
    memote_version = _validate_execution(execution, result_path)
    try:
        with gzip.open(result_path, "rt", encoding="utf-8") as stream:
            raw_result = json.load(stream)
    except (gzip.BadGzipFile, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("memote-results.json.gz is not valid gzip JSON") from error
    tests = raw_result.get("tests") if isinstance(raw_result, dict) else None
    if not isinstance(tests, dict):
        raise ValueError("MEMOTE result must contain a tests object")

    lookup = _family_lookup()
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {
        (family_id, title): [] for family_id, title, _ in FAMILIES
    }
    miscellaneous: list[dict[str, Any]] = []
    for test_id, raw_test in sorted(tests.items()):
        if not isinstance(test_id, str):
            raise ValueError("MEMOTE test identifiers must be strings")
        normalized = _normalize_test(test_id, raw_test)
        family = lookup.get(test_id)
        if family is None:
            miscellaneous.append(normalized)
        else:
            grouped[family].append(normalized)

    families: list[dict[str, Any]] = []
    for (family_id, title), family_tests in grouped.items():
        if not family_tests:
            continue
        family_outcomes = [
            case["outcome"] for test in family_tests for case in test["cases"]
        ]
        families.append(
            {
                "case_count": len(family_outcomes),
                "family_id": family_id,
                "outcome_counts": _outcome_counts(family_outcomes),
                "test_count": len(family_tests),
                "tests": family_tests,
                "title": title,
            }
        )
    if miscellaneous:
        misc_outcomes = [case["outcome"] for test in miscellaneous for case in test["cases"]]
        families.append(
            {
                "case_count": len(misc_outcomes),
                "family_id": "miscellaneous",
                "outcome_counts": _outcome_counts(misc_outcomes),
                "test_count": len(miscellaneous),
                "tests": miscellaneous,
                "title": "Miscellaneous Tests",
            }
        )

    all_outcomes = [
        case["outcome"]
        for family in families
        for test in family["tests"]
        for case in test["cases"]
    ]
    summary = {
        "case_count": len(all_outcomes),
        "diagnostic_scope": DIAGNOSTIC_SCOPE,
        "families": families,
        "language": "en",
        "memote_version": memote_version,
        "outcome_counts": _outcome_counts(all_outcomes),
        "schema_version": 1,
        "sources": {
            "execution": execution_path.name,
            "findings": findings_path.name,
            "normalized_summary": summary_path.name,
            "result": result_path.name,
            "result_sha256": raw_hashes_before[result_path],
        },
        "test_count": len(tests),
    }
    findings_families = []
    for index, family in enumerate(families):
        counts = family["outcome_counts"]
        findings_families.append(
            {
                "claim": (
                    f"Under MEMOTE {memote_version} default test conditions, the {family['title']} "
                    f"family recorded {counts['passed']} passed, {counts['failed']} failed, and "
                    f"{counts['skipped']} skipped terminal cases across {family['test_count']} tests. "
                    "These are MEMOTE diagnostics, not biological conclusions."
                ),
                "evidence": [
                    {
                        "kind": "generated-output",
                        "locator": f"{summary_path.name}#/families/{index}",
                    }
                ],
                "family_id": family["family_id"],
                "id": f"memote-default-{family['family_id']}",
                "language": "en",
                "limitations": [DIAGNOSTIC_SCOPE],
                "outcome_counts": counts,
                "severity": "warning" if counts["failed"] else "info",
                "title": family["title"],
            }
        )
    findings = {
        "diagnostic_scope": DIAGNOSTIC_SCOPE,
        "families": findings_families,
        "language": "en",
        "schema_version": 1,
    }

    if any(_sha256(path) != digest for path, digest in raw_hashes_before.items()):
        raise RuntimeError("A raw MEMOTE artifact changed during normalization")
    report_dir.mkdir(parents=True, exist_ok=True)
    _write_json(summary_path, summary)
    _write_json(findings_path, findings)
    report_path.write_text(_render_report(summary, findings, run_name), encoding="utf-8")
    if any(_sha256(path) != digest for path, digest in raw_hashes_before.items()):
        raise RuntimeError("A raw MEMOTE artifact changed while derived artifacts were written")
    return summary_path, findings_path, report_path
