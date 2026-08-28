# GEM Reviewer

A reproducible review workflow for an **immutable** GEM input. The project uses Python 3.11+ and [`uv`](https://docs.astral.sh/uv/) for all environments and dependencies.

> **Hermes experiment project.** This repository is an experimental project operated with Hermes Agent. Each Git commit created by the agent will include a `Co-authored-by: Hermes Agent <noreply@nousresearch.com>` trailer in addition to the repository's configured human author.

The first candidate model is BiGG `iEC1372_W3110`. Its scope, minimal architecture, tool choices, and staged acceptance criteria are recorded in [docs/architecture.md](docs/architecture.md). No GEM has been acquired or reviewed yet.

## Guarantees

- **GEM input is never modified.** The command reads the specified file and writes only to a new output directory.
- **Provenance is captured per run.** `provenance.json` stores the source URL, declared GEM version, SHA-256, byte count, and review timestamp.
- **Generated outputs are separate and untracked.** Put an input under `data/gem/` or elsewhere; write each run to a fresh subdirectory of `outputs/`.
- **Conclusions are traceable.** Every generated conclusion includes evidence keys that point to fields in the generated report. Any future model-assisted conclusion must additionally record the model artifact, prompt/configuration, and raw output; any external assertion must cite its public source.
- **The review is rerunnable.** A single `uv run gem-review ...` command executes the full pipeline.

## Input contract

The present structural reviewer accepts a JSON object containing:

```json
{
  "gem_version": "optional string version",
  "items": []
}
```

`items` is required; `gem_version` defaults to `"undeclared"` if absent. The GEM file is ignored by Git to preserve its immutable-source role. Keep its canonical acquisition location in `--source-url`.

## Reproduce a review

1. Install `uv` and clone this repository.
2. Place or reference the immutable GEM JSON file. Do **not** edit it.
3. Choose a brand-new, empty output directory.
4. Run one command:

```bash
uv run gem-review \
  --gem data/gem/GEM.json \
  --source-url "https://publisher.example/GEM/version" \
  --output-dir outputs/2026-08-28
```

5. Inspect the resulting artifacts:
   - `outputs/2026-08-28/provenance.json` — source/version/hash manifest
   - `outputs/2026-08-28/review.json` — generated findings, evidence pointers, and limitations
   - `reports/REVIEW_REPORT.md` — human-readable report template; update it only with claims linked to generated output, model artifacts, or public sources.

The command refuses to overwrite a non-empty output directory. To rerun, use a different output directory or explicitly remove a previous **generated** directory after preserving it if needed.

## Development

```bash
uv run pytest -q
```

No GEM is bundled with the repository, so the committed report intentionally contains no substantive review finding.
