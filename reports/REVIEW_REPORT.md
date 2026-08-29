# GEM Review Report

**Status:** Frozen source acquired; Phase 2A technical preflight completed. No substantive biological review has been performed.

## Scope

This report is intentionally limited to a review run's generated artifacts. It must not state a conclusion that cannot be traced to one of the following:

- a JSON pointer or field in `outputs/<run>/review.json`;
- `outputs/<run>/provenance.json`, which records the input path, source URL, declared GEM version, SHA-256, and byte count;
- an explicitly cited public source; or
- a versioned model artifact, including its identifier, hash, prompt/configuration, and raw output.

## Required review-run record

| Field | Value |
| --- | --- |
| GEM source URL | `http://bigg.ucsd.edu/models/iEC1372_W3110` |
| GEM declared version | BiGG download updated 2019-10-31 |
| GEM SHA-256 | `109290d2e2407a94f8088f9ef9fd40f6db6b73b1cf36574d6d987527ece8d9b7` |
| Generated report | Phase 2A preflight artifacts under an ignored `outputs/iEC1372_W3110-preflight-<run-id>/` directory |
| Reproduction command | `uv run gem-preflight --gem data/gem/iEC1372_W3110.xml --source-manifest data/gem/iEC1372_W3110.source.json --output-dir outputs/iEC1372_W3110-preflight-<run-id>` |

## Findings

Phase 2A establishes only that the stored bytes match the source manifest and that the frozen SBML can be read and validated by the locked technical environment. Its generated diagnostics must be consulted for the exact run-specific result. These are technical facts, not a biological quality conclusion.

## Limitations

The current implementation performs a read-only SBML preflight, including source-integrity checks, environment capture, SBML diagnostics, and a structural summary. Domain-specific evaluation criteria, MEMOTE benchmark interpretation, experimental conditions, and model-assisted review remain out of scope until supplied and versioned.
