# GEM Reviewer

A reproducible review workflow for an **immutable** GEM input. The project uses Python 3.11+ and [`uv`](https://docs.astral.sh/uv/) for all environments and dependencies.

> **Hermes experiment project.** This repository is an experimental project operated with Hermes Agent. Each Git commit created by the agent will include a `Co-authored-by: Hermes Agent <noreply@nousresearch.com>` trailer in addition to the repository's configured human author.

The first candidate model is BiGG `iEC1372_W3110`. Its scope, minimal architecture, tool choices, and staged acceptance criteria are recorded in [docs/architecture.md](docs/architecture.md). The source artifact is frozen; no substantive GEM review has been performed yet.

## Approved tracked input

With explicit user approval, this repository tracks the immutable BiGG SBML artifact [`data/gem/iEC1372_W3110.xml`](data/gem/iEC1372_W3110.xml). Its source, publisher attribution, associated publication, retrieval record, byte count, and SHA-256 are recorded in [`data/gem/iEC1372_W3110.source.json`](data/gem/iEC1372_W3110.source.json). Future GEMs remain ignored by default and may be added to Git **only after explicit user approval**.

## Guarantees

- **GEM input is never modified.** Preflight reads the frozen file; the MEMOTE subprocess receives only a byte-identical staged copy in a new output directory.
- **Provenance is checked per run.** The frozen source manifest supplies source/version/hash facts; both preflight and MEMOTE baseline metadata record before/after input hashes.
- **Generated outputs are separate and untracked.** Put an input under `data/gem/` or elsewhere; write each run to a fresh subdirectory of `outputs/`.
- **Conclusions are traceable.** Every generated conclusion includes evidence keys that point to fields in the generated report. Any future model-assisted conclusion must additionally record the model artifact, prompt/configuration, and raw output; any external assertion must cite its public source.
- **Findings and review reports are English-only.** Machine-readable findings declare `language: "en"`; tracked and generated reports must not contain Chinese text.
- **The technical preflight is rerunnable.** A single `uv run gem-preflight ...` command writes all Phase 2A evidence artifacts.
- **The MEMOTE baseline is reproducible and bounded.** `gem-memote-baseline` records a portable command, tool versions, timestamps, exit status, timeouts, artifact hashes, raw combined log, and raw collected result without persisting machine-specific paths.

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

Human-readable review reports belong under `reports/` and are ignored by Git by default. A report may be tracked only after explicit user approval for that exact report; the approved exception is [`reports/iEC1372_W3110_REPORT.md`](reports/iEC1372_W3110_REPORT.md).

The command refuses to overwrite a non-empty output directory. To rerun, use a different output directory or explicitly remove a previous **generated** directory after preserving it if needed.

## Run the reproducible MEMOTE baseline

The Phase 2C command reruns preflight, stages a byte-identical input copy, and then runs locked MEMOTE 0.17.0. The output directory must not exist before the command starts; it is never reused or overwritten.

Discover the entry point and all Fire-generated options with:

```bash
uv run gem-memote-baseline --help
```

```bash
uv run gem-memote-baseline \
  --gem data/gem/iEC1372_W3110.xml \
  --source-manifest data/gem/iEC1372_W3110.source.json \
  --output-dir outputs/iEC1372_W3110-memote-baseline-<run-id> \
  --solver-timeout 15 \
  --wall-timeout 7200
```

The wall timeout bounds the MEMOTE subprocess to two hours; the solver timeout applies to each mathematical optimization. A run preserves:

- `memote-input.xml` — byte-identical staged input passed to MEMOTE
- `memote-run.log` — raw combined standard output and standard error
- `memote-results.json.gz` — raw collected MEMOTE result, when MEMOTE produces one
- `memote-execution.json` — portable invocation, tool versions, timing, status, input hashes, and artifact hashes; local installation and absolute filesystem paths are excluded
- Phase 2A preflight artifacts, with the MEMOTE execution finding appended to `findings.json`

For a later bounded background run from Git Bash, use this launch sequence. The launcher log stays beside the new output directory so redirection does not create that directory before the baseline claims it. The baseline itself has intentionally not been run as part of development or testing:

```bash
run_id="iEC1372_W3110-memote-baseline-$(date -u +%Y%m%dT%H%M%SZ)"
launcher_log="outputs/${run_id}-launcher.log"
nohup uv run gem-memote-baseline \
  --gem data/gem/iEC1372_W3110.xml \
  --source-manifest data/gem/iEC1372_W3110.source.json \
  --output-dir "outputs/${run_id}" \
  --solver-timeout 15 \
  --wall-timeout 7200 \
  >"${launcher_log}" 2>&1 &
baseline_pid=$!
printf 'MEMOTE baseline PID: %s\nLauncher log: %s\n' "${baseline_pid}" "${launcher_log}"
```

Inspect `memote-execution.json` after the process exits. A completed baseline has `status: "completed"`; timeout status returns CLI exit code 124. Raw logs and metadata remain available for unsuccessful runs.

## Development

```bash
uv run pytest -q
```

The repository includes one explicitly approved, frozen GEM. Phase 2A establishes technical integrity, Phase 2B establishes MEMOTE compatibility, and Phase 2C provides the reproducible baseline command. None of these makes a substantive biological review finding.
