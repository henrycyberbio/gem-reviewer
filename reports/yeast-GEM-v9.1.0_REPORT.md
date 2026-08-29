# yeast-GEM v9.1.0 Technical Review Report

**Language:** English
**Status:** Proof-of-concept technical review of a frozen release artifact. This report is not biological validation.

## Scope and frozen source

This review covers the official SysBioChalmers `yeast-GEM` release `v9.1.0` and the exact SBML artifact identified below. The model was assessed as frozen input; the integrity record shows the same hash before and after technical preflight.

| Field | Verified value |
| --- | --- |
| Publisher and model | SysBioChalmers `yeast-GEM` |
| Release | `v9.1.0` |
| Release page | <https://github.com/SysBioChalmers/yeast-GEM/releases/tag/v9.1.0> |
| Tag commit | `2fd1a331abc422971e8a5a54ae185d1b33d68c10` |
| Frozen XML URL | <https://raw.githubusercontent.com/SysBioChalmers/yeast-GEM/v9.1.0/model/yeast-GEM.xml> |
| SHA-256 | `05d33f3e82c2e2d072e229e7588f06d33b7df9daa806288db548c140149fc8bb` |
| Size | `11,562,488` bytes |
| Technical preflight | `outputs/yeast-GEM-v9.1.0-memote-baseline-20260829T194527Z/` |

## Technical preflight findings

1. **Input integrity:** `input-integrity.json` records a source-manifest match and the expected SHA-256 both before and after processing. Hash equality establishes byte identity, not model correctness.
2. **Model structure:** `structural-summary.json` records 4,102 reactions, 2,748 metabolites, and 1,143 genes. It identifies `r_2111` as the objective reaction with maximization direction, plus 270 exchange reactions and 3 sink reactions.
3. **SBML diagnostics:** `sbml-validation.json` records zero COBRA errors, zero COBRA fatals, zero SBML errors, zero SBML fatals, and zero SBML schema errors. It records 52 SBML warnings. Every warning is the same class of species SBO branch-consistency diagnostic: `SBO:0000649` is reported as not being in the appropriate branch for a `Species` object.

These findings establish limited technical properties of the frozen artifact in the recorded environment. They do not establish biological correctness, predictive validity, or suitability for a particular scientific use.

## MEMOTE baseline status

The attempted full baseline used MEMOTE `0.17.0`, as pinned in `pyproject.toml`. It did **not** complete: the host terminated the external process during execution. The retained `memote-run.log` ends during the test sequence, and the run directory contains no completed MEMOTE report artifact.

Accordingly, this report claims no local MEMOTE score and no pass, fail, skip, or other test outcomes. Lines emitted before termination are partial execution trace only and must not be interpreted as a complete baseline result.

## Comparison with publisher-reported results

The release-tag README reports the same structural counts as the local preflight: 4,102 reactions, 2,748 metabolites, and 1,143 genes. It also reports gene-essentiality accuracy of `0.902` and growth-prediction R-squared of `0.901`:

- <https://github.com/SysBioChalmers/yeast-GEM/blob/v9.1.0/README.md#model-overview>
- <https://github.com/SysBioChalmers/yeast-GEM/blob/v9.1.0/README.md#gene-essentiality-prediction>
- <https://github.com/SysBioChalmers/yeast-GEM/blob/v9.1.0/README.md#growth-prediction>

Those two scientific performance values are publisher-reported context, not results of this project. This project did not rerun the gene-essentiality or growth assessments because their protocol and data are not frozen in this review.

The currently public `release_report.html` is a later `9.1.1` snapshot at `gh-pages` commit `9631a344eea0eceb103b3463521e4a3e02325d38`. It reports MEMOTE `0.13.0` and score `0.6971460566319498`:

- Public report: <https://sysbiochalmers.github.io/yeast-GEM/release_report.html>
- Snapshot locator: <https://github.com/SysBioChalmers/yeast-GEM/blob/9631a344eea0eceb103b3463521e4a3e02325d38/release_report.html>

That public score is not numerically comparable with this review: it describes model version `9.1.1` under MEMOTE `0.13.0`, whereas the frozen input here is `v9.1.0` and the incomplete local attempt used MEMOTE `0.17.0`.

## Evidence locators

| Claim | Evidence locator |
| --- | --- |
| Source identity, URL, size, and expected hash | `data/gem/yeast-GEM-v9.1.0.source.json` |
| Before/after hash match and byte count | `outputs/yeast-GEM-v9.1.0-memote-baseline-20260829T194527Z/input-integrity.json` |
| Reactions, metabolites, genes, objective, exchanges, and sinks | `outputs/yeast-GEM-v9.1.0-memote-baseline-20260829T194527Z/structural-summary.json` |
| COBRA and SBML diagnostic categories | `outputs/yeast-GEM-v9.1.0-memote-baseline-20260829T194527Z/sbml-validation.json` |
| Incomplete MEMOTE execution trace | `outputs/yeast-GEM-v9.1.0-memote-baseline-20260829T194527Z/memote-run.log` |
| MEMOTE version pin | `pyproject.toml` |
| Official release and tag commit | <https://github.com/SysBioChalmers/yeast-GEM/releases/tag/v9.1.0> |
| Publisher structural and scientific metrics | <https://github.com/SysBioChalmers/yeast-GEM/blob/v9.1.0/README.md> |
| Later public MEMOTE snapshot | <https://github.com/SysBioChalmers/yeast-GEM/blob/9631a344eea0eceb103b3463521e4a3e02325d38/release_report.html> |

## Explicit limitations

- This is a technical review, not biological validation.
- Hash matching demonstrates artifact identity only; it does not demonstrate correctness or scientific quality.
- Parser and SBML diagnostics are format-level evidence and do not validate biochemical content.
- Structural counts do not assess stoichiometric correctness, annotations, mass or charge balance, flux behavior, gene rules, media assumptions, or experimental agreement.
- The full local MEMOTE baseline did not complete, so no local score or test outcomes are available.
- The project did not rerun the publisher's gene-essentiality or growth-prediction assessments because the required protocol and data are not frozen here.
- Results from a different model version or MEMOTE version must not be used as a numerical substitute for the missing local baseline.
