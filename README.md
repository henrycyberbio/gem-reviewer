# GEM Reviewer

A reproducible workflow for reviewing genome-scale metabolic models (GEMs). A GEM represents an organism's metabolic network as genes, reactions, metabolites, and constraints that can be analyzed computationally. This workflow reviews model provenance and identity, technical validity, structural and annotation quality, model diagnostics, and, in later stages, protocol-defined scientific questions.

Source GEM inputs are treated as immutable review evidence: the workflow reads or stages byte-identical copies but never modifies them.

> **Hermes experiment project.** This repository is an experimental project operated with Hermes Agent. Each Git commit created by the agent will include a `Co-authored-by: Hermes Agent <noreply@nousresearch.com>` trailer in addition to the repository's configured human author.

BiGG `iEC1372_W3110` is the proof-of-concept (POC) review case used to develop and demonstrate this workflow. Its scope, minimal architecture, tool choices, and staged acceptance criteria are recorded in [docs/architecture.md](docs/architecture.md).

## Project status — concluded early

This experimental project is concluded before a substantive GEM review is completed. The POC established an immutable-input intake path, reproducible technical preflight, and bounded MEMOTE-baseline evidence handling, but it did not complete a full local MEMOTE baseline or a protocol-defined scientific review for either POC model.

The reason is architectural rather than a claim about either GEM's quality. GEM validation is a strict, mathematically bounded pipeline: MEMOTE and continuous integration are better suited to execute standardized checks deterministically, retain raw evidence, and report regressions. An interactive Agent adds comparatively little value to that routine execution path while adding operational complexity for long-running jobs. Future work should therefore prioritize a versioned MEMOTE configuration and CI workflow; an Agent should be used only for clearly scoped tasks that require interpretation beyond those automated checks.

The repository remains a POC implementation and evidence-preservation reference. Its existing reports document the completed checks and limitations; they must not be read as completed biological or full-MEMOTE reviews.

## Approved tracked input

With explicit user approval, this repository tracks the immutable BiGG SBML artifact [`data/gem/iEC1372_W3110.xml`](data/gem/iEC1372_W3110.xml). Its source, publisher attribution, associated publication, retrieval record, byte count, and SHA-256 are recorded in [`data/gem/iEC1372_W3110.source.json`](data/gem/iEC1372_W3110.source.json). Every artifact under `data/`, `reports/`, or `outputs/` requires explicit user approval for that specific artifact before it may be added to Git, committed, or synchronized.

## Guarantees

- **GEM input is never modified.** Preflight reads the frozen file; the MEMOTE subprocess receives only a byte-identical staged copy in a new output directory.
- **Provenance is checked per run.** The frozen source manifest supplies source/version/hash facts; both preflight and MEMOTE baseline metadata record before/after input hashes.
- **Generated outputs are separate and approval-gated.** Write each run to a fresh subdirectory of `outputs/`; each specific output artifact requires explicit user approval before Git add, commit, or synchronization.
- **Conclusions are traceable.** Every generated conclusion includes evidence keys that point to fields in the generated report. Any future model-assisted conclusion must additionally record the model artifact, prompt/configuration, and raw output; any external assertion must cite its public source.
- **Findings and review reports are English-only.** Machine-readable findings declare `language: "en"`; tracked and generated reports must not contain Chinese text.
- **The technical preflight is rerunnable.** A single `uv run gem-preflight ...` command writes all Phase 2A evidence artifacts.
- **Preflight metadata is portable.** JSON metadata records project-relative input locators or neutral role names and excludes absolute local paths, usernames, IP addresses, and executable paths.
- **The MEMOTE baseline is reproducible and bounded.** `gem-memote-baseline` runs each installed test module in a separate bounded process and records portable commands, statuses, hashes, raw module evidence, and one validated merged result without persisting machine-specific paths.

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

Human-readable review reports belong under `reports/`. Each specific report requires explicit user approval before Git add, commit, or synchronization; the approved report is [`reports/iEC1372_W3110_REPORT.md`](reports/iEC1372_W3110_REPORT.md).

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

The wall timeout bounds each MEMOTE module subprocess to two hours; the solver timeout applies to each mathematical optimization. A run also preserves raw `modules/*.log` and `modules/*.json.gz` evidence, and publishes the merged `memote-results.json.gz` only after all 77 emitted test objects are represented.

- `memote-input.xml` — byte-identical staged input passed to MEMOTE
- `memote-run.log` — raw combined standard output and standard error
- `memote-results.json.gz` — validated merged MEMOTE result, only after every module succeeds
- `memote-execution.json` — atomic batched invocation metadata, tool versions, timing, status, input hashes, and artifact hashes; local installation and absolute filesystem paths are excluded
- Phase 2A preflight artifacts, with the MEMOTE execution finding appended to `findings.json`

For a bounded background run from Git Bash, use this launch sequence. The launcher log stays beside the new output directory so redirection does not create that directory before the baseline claims it:

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

## Normalize a completed MEMOTE baseline

After a baseline has completed successfully, derive grouped diagnostics and a run-specific human report with:

```bash
uv run gem-memote-summarize \
  --output-dir outputs/iEC1372_W3110-memote-baseline-<run-id>
```

The command verifies the execution status and raw result hash, then adds `memote-summary.json` and `memote-findings.json` to the existing run directory. It writes `reports/<run-directory-name>-report.md` separately and refuses to overwrite any derived artifact. Scalar MEMOTE results count as one terminal case; parameterized results count only their passed, failed, or skipped child cases. Results and claims are grouped by MEMOTE's default test families and explicitly describe default-condition diagnostics, not biological conclusions. The raw gzip result, execution metadata, logs, staged model, frozen GEM, and existing findings are not changed.

## Development

```bash
uv run pytest -q
```

The repository includes one explicitly approved, frozen GEM. The technical stages establish input integrity, validation evidence, structural and annotation evidence, and reproducible model diagnostics. Protocol-defined scientific review questions are addressed separately in later stages.
