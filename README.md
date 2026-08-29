# GEM Reviewer

A reproducible review workflow for an **immutable** GEM input. The project uses Python 3.11+ and [`uv`](https://docs.astral.sh/uv/) for all environments and dependencies.

> **Hermes experiment project.** This repository is an experimental project operated with Hermes Agent. Each Git commit created by the agent will include a `Co-authored-by: Hermes Agent <noreply@nousresearch.com>` trailer in addition to the repository's configured human author.

The first candidate model is BiGG `iEC1372_W3110`. Its scope, minimal architecture, tool choices, and staged acceptance criteria are recorded in [docs/architecture.md](docs/architecture.md). The source artifact is frozen; no substantive GEM review has been performed yet.

## Approved tracked input

With explicit user approval, this repository tracks the immutable BiGG SBML artifact [`data/gem/iEC1372_W3110.xml`](data/gem/iEC1372_W3110.xml). Its source, publisher attribution, associated publication, retrieval record, byte count, and SHA-256 are recorded in [`data/gem/iEC1372_W3110.source.json`](data/gem/iEC1372_W3110.source.json). Future GEMs remain ignored by default and may be added to Git **only after explicit user approval**.

## Guarantees

- **GEM input is never modified.** The command reads the specified file and writes only to a new output directory.
- **Provenance is checked per preflight run.** The frozen source manifest supplies source/version/hash facts; `input-integrity.json` records the before/after hash check.
- **Generated outputs are separate and untracked.** Put an input under `data/gem/` or elsewhere; write each run to a fresh subdirectory of `outputs/`.
- **Conclusions are traceable.** Every generated conclusion includes evidence keys that point to fields in the generated report. Any future model-assisted conclusion must additionally record the model artifact, prompt/configuration, and raw output; any external assertion must cite its public source.
- **The technical preflight is rerunnable.** A single `uv run gem-preflight ...` command writes all Phase 2A evidence artifacts.

## Reproduce the SBML preflight

1. Install `uv` and clone this repository.
2. Use the approved frozen SBML input. Do **not** edit it.
3. Choose a brand-new, empty output directory.
4. Run one command:

```bash
uv run gem-preflight \
  --gem data/gem/iEC1372_W3110.xml \
  --source-manifest data/gem/iEC1372_W3110.source.json \
  --output-dir outputs/iEC1372_W3110-preflight-<run-id>
```

5. Inspect the resulting artifacts:
   - `input-integrity.json` — source-manifest and before/after hash checks
   - `environment.json` — Python, COBRApy, and libSBML versions
   - `sbml-validation.json` — raw COBRApy/libSBML diagnostic categories
   - `structural-summary.json` and `findings.json` — evidence-bearing structural facts and limitations

Generated human-readable review reports belong under `reports/` and are intentionally ignored by Git, like other evidence artifacts.

The command refuses to overwrite a non-empty output directory. To rerun, use a different output directory or explicitly remove a previous **generated** directory after preserving it if needed.

## Development

```bash
uv run pytest -q
```

The repository includes one explicitly approved, frozen GEM. Phase 2A establishes only technical integrity and SBML compatibility; it does not make a substantive biological review finding.
