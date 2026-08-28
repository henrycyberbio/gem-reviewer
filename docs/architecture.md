# GEM Reviewer architecture decisions

**Status:** proposed for the first target; implementation is deliberately deferred pending approval of the phase gates.

## 1. Boundary and known target

The first proposed target is BiGG `iEC1372_W3110`: *Escherichia coli* K-12 W3110 (genome `NC_007779.1`). The BiGG record lists 1,918 metabolites, 2,758 reactions, and 1,372 genes; it offers SBML, JSON, and MAT downloads and identifies 31 October 2019 as the download update date.[1]

This document records a **review harness**, not a model-curation project. The GEM must never be edited, normalized in place, or committed as if it were source code. No model file was downloaded, parsed, or reviewed while making these decisions.

## 2. Smallest useful architecture

```text
immutable source artifact ──> input manifest ──> staged review checks ──> outputs/<run-id>/
                                               \                         └─> review report
                                                └─ source ledger / protocol
```

Keep only these durable areas:

| Location | Role | Git policy |
| --- | --- | --- |
| `data/gem/` | Original downloaded GEM bytes, read-only | ignored by default; track only with explicit user approval |
| `docs/source-ledger.json` | URLs used to define/interpret the review | tracked |
| `docs/architecture.md` | decisions, boundaries, acceptance criteria | tracked |
| `src/gem_reviewer/` | reproducible orchestration and checks | tracked |
| `outputs/<run-id>/` | generated manifests, tool results, figures, and machine-readable findings | ignored |
| `reports/REVIEW_REPORT.md` | review report skeleton; later filled only from evidence | tracked |

No notebooks, manual spreadsheet analyses, or stateful GUI operations belong in the pipeline.

## 3. Decisions

### ADR-001 — Use the BiGG SBML download as the canonical first input

When acquisition is authorized, retrieve the `iEC1372_W3110.xml` artifact linked from the BiGG model page, preserving its bytes exactly. Record the model-page URL, direct-download URL, publisher update date, retrieval time, filename, size, and SHA-256 in a tracked source manifest for the approved input and in each review run's `outputs/<run-id>/input-manifest.json`. The supplied JSON and MAT exports are not substitutes; they may be separately compared later only after each is frozen and hashed.[1]

**Why:** SBML is the exchange format that the current COBRApy documentation can validate, so it supports a minimal parser/validator path without converting the source artifact.[2]

### ADR-002 — Start with structural and solver-independent checks

The first implemented review stage will parse and validate the frozen SBML, then report reproducible structural facts and validation diagnostics. It must not imply biological correctness from successful parsing.

### ADR-003 — Treat COBRApy as the first parser/validation candidate; defer installation

COBRApy documents SBML reading/writing and `validate_sbml_model`, so it is the smallest candidate to spike for parsing and validation.[2] It is **not installed today**; do not add it until the next phase includes a compatibility spike against the frozen input.

### ADR-004 — Treat MEMOTE as an optional benchmark, not a gate

MEMOTE supplies standardized model tests and report generation, including basic, biomass, stoichiometry, SBML, and annotation-oriented tests.[3] Add it only if its installation and execution are reproducible under the locked environment. Preserve its raw report and command output as evidence. A MEMOTE score/report is a benchmark artifact, not an unqualified biological conclusion.

### ADR-005 — Separate claim generation from evidence rendering

Every finding—whether structural, solver-based, model-assisted, or literature-backed—must contain:

```json
{
  "id": "stable-finding-id",
  "claim": "precise, scoped statement",
  "severity": "info|warning|failure",
  "evidence": [
    {
      "kind": "generated-output|model-output|public-source",
      "locator": "relative file plus JSON pointer, artifact hash, or source URL",
      "command": "exact producing command when applicable"
    }
  ],
  "limitations": ["assumptions and non-claims"]
}
```

The human report is rendered from these evidence-bearing records; it is never the only record of a conclusion.

### ADR-006 — Do not define biological scenarios before a protocol exists

Flux balance analysis, growth tests, gene knockouts, media assumptions, objective selection, and literature comparisons are all deferred. Each needs a versioned review protocol that says what is being tested, why its assumptions apply, what result would count as a finding, and which public source supports the setup.

## 4. Workflow and stage gates

| Phase | Work | Acceptance criterion | Explicit non-goal |
| --- | --- | --- | --- |
| 0 — Environment and scope | Record interpreter, `uv`, Git, available model tools, model identity, and architecture | This document exists; no GEM is acquired or analyzed | Installing scientific stacks or running a model |
| 1 — Acquire and freeze | Download the specified SBML exactly once into `data/gem/`; write a source/hash manifest | Recomputed SHA-256 matches the manifest before and after the run; source bytes remain unchanged | Format conversion or repair |
| 2 — Compatibility spike | Add pinned parser dependency and load the frozen SBML | A scripted load/validation produces machine-readable diagnostics and tool versions | Interpreting diagnostics as biological validity |
| 3 — Baseline quality | Run structural checks; optionally run MEMOTE if the spike proves reproducible | One command creates a fresh output directory containing raw tool artifacts and normalized findings | Silent fixes or scoring-only conclusions |
| 4 — Directed review protocol | Agree review questions, conditions, external references, and pass/fail interpretation | Protocol is versioned before scenarios execute | Exploratory/manual scenario tuning |
| 5 — Review report | Render report strictly from artifacts and cited sources | Every report conclusion resolves to an output pointer, model artifact, or public source | Untraceable prose |

## 5. Current environment assessment

- Available: Python 3.11.13, `uv` 0.12.5, and Git 2.39.1.
- Not installed: COBRApy, python-libSBML, and MEMOTE.
- The repository has an initial, uncommitted generic JSON scaffold. It is not yet an implementation for the SBML target and must not be presented as having reviewed `iEC1372_W3110`.
- Git lacks a configured author identity, so no commits can be created until the user supplies a repository-local name and email.

## 6. Next decision required

Authorize Phase 1 only when ready: acquire **the exact SBML artifact** from BiGG and freeze its provenance. Before Phase 4, provide or approve the scientific questions and acceptance criteria; the model URL alone does not define a substantive biological review.

## Sources

[1] http://bigg.ucsd.edu/models/iEC1372_W3110 — BiGG iEC1372_W3110 model record
[2] https://cobrapy.readthedocs.io/en/latest/building_model.html — COBRApy model validation documentation
[3] https://memote.readthedocs.io/en/latest — MEMOTE documentation
