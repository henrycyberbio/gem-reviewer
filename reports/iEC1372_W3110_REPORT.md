# iEC1372_W3110 Technical Review Report

**Language:** English
**Status:** Example tracked report approved by the user. This report records Phase 2A technical preflight only; it is not a biological validation or a model-curation proposal.

## Scope

- Model: `iEC1372_W3110`
- Organism: *Escherichia coli* K-12 W3110
- Frozen artifact: `data/gem/iEC1372_W3110.xml`
- Source manifest: `data/gem/iEC1372_W3110.source.json`
- Input SHA-256: `109290d2e2407a94f8088f9ef9fd40f6db6b73b1cf36574d6d987527ece8d9b7`

The model was read without conversion, normalization, repair, or in-place modification.

## Reproduction

```bash
uv run gem-preflight \
  --gem data/gem/iEC1372_W3110.xml \
  --source-manifest data/gem/iEC1372_W3110.source.json \
  --output-dir outputs/iEC1372_W3110-preflight-<run-id>
```

The command writes `input-integrity.json`, `environment.json`, `sbml-validation.json`, `structural-summary.json`, and `findings.json` under the supplied output directory.

## Technical Findings

1. **Input integrity.** The preflight command verifies that the frozen model's byte count and SHA-256 match the source manifest before processing and recomputes the SHA-256 after processing. Evidence: `outputs/<run-id>/input-integrity.json`.
2. **SBML validation.** The preflight command captures COBRApy/libSBML validation categories without modifying the input. Evidence: `outputs/<run-id>/sbml-validation.json`.
3. **Structural counts.** The frozen input is expected to contain 1,918 metabolites, 2,758 reactions, and 1,372 genes, matching the BiGG model record. Evidence: `outputs/<run-id>/structural-summary.json`; BiGG record: http://bigg.ucsd.edu/models/iEC1372_W3110.

## Limitations

- Successful parsing and structural validation do not establish biological correctness.
- No medium, objective modification, flux balance analysis, flux variability analysis, gene deletion, growth prediction, or experimental comparison has been performed.
- MEMOTE results, when generated, are benchmark diagnostics and require scoped interpretation; they are not automatic biological findings.

## Provenance

- BiGG model record: http://bigg.ucsd.edu/models/iEC1372_W3110
- Associated publication: Monk JM, Koza A, Campodonico MA, Machado D, Seoane JM, Palsson BO, Herrgard MJ, Feist AM. *Multi-omics Quantification of Species Variation of Escherichia coli Links Molecular Features with Strain Phenotypes*. Cell Systems. 2016;3(3):238-251.e12. PMID: 27667363. https://pubmed.ncbi.nlm.nih.gov/27667363/
- Source-specific URLs, retrieval timestamp, publisher update date, license URL, byte count, and SHA-256 are recorded in `data/gem/iEC1372_W3110.source.json`.
