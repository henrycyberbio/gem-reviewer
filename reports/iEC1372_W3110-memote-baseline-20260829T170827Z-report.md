# MEMOTE Default-Condition Diagnostic Report: `iEC1372_W3110-memote-baseline-20260829T170827Z`

**Language:** English
**Scope:** MEMOTE default-condition diagnostics only; this report does not make biological conclusions.

## Run evidence

- MEMOTE version: `0.17.0`
- Completed execution: `memote-execution.json`
- Raw result: `memote-results.json.gz` (SHA-256 `250f957002bfeefaacb0a76ce144acff43ff53a5a741a92d0bfe9db2d1673254`)
- Normalized evidence: `memote-summary.json` and `memote-findings.json`

## Outcome summary

Under MEMOTE 0.17.0 default test conditions, 155 terminal cases across 77 tests recorded 69 passed, 81 failed, and 5 skipped outcomes.
Parameterized child cases are counted instead of their parent test, so no outcome is counted twice.

| Test family | Tests | Cases | Passed | Failed | Skipped |
| --- | ---: | ---: | ---: | ---: | ---: |
| Consistency | 5 | 5 | 2 | 3 | 0 |
| Annotation - Metabolites | 4 | 24 | 10 | 14 | 0 |
| Annotation - Reactions | 4 | 20 | 8 | 12 | 0 |
| Annotation - Genes | 3 | 21 | 1 | 20 | 0 |
| Annotation - SBO Terms | 11 | 11 | 1 | 9 | 1 |
| SBML | 2 | 2 | 2 | 0 | 0 |
| Basic Information | 8 | 8 | 6 | 2 | 0 |
| Metabolite Information | 5 | 5 | 3 | 2 | 0 |
| Reaction Information | 7 | 7 | 5 | 2 | 0 |
| Gene-Protein-Reaction (GPR) Associations | 3 | 3 | 2 | 1 | 0 |
| Biomass | 9 | 17 | 13 | 4 | 0 |
| Energy Metabolism | 4 | 20 | 12 | 6 | 2 |
| Network Topology | 6 | 6 | 0 | 6 | 0 |
| Matrix Conditioning | 4 | 4 | 4 | 0 | 0 |
| Experimental Data Comparison | 2 | 2 | 0 | 0 | 2 |

## Evidence-linked findings

### Consistency

Under MEMOTE 0.17.0 default test conditions, the Consistency family recorded 2 passed, 3 failed, and 0 skipped terminal cases across 5 tests. These are MEMOTE diagnostics, not biological conclusions.

Evidence: `memote-summary.json#/families/0`.

### Annotation - Metabolites

Under MEMOTE 0.17.0 default test conditions, the Annotation - Metabolites family recorded 10 passed, 14 failed, and 0 skipped terminal cases across 4 tests. These are MEMOTE diagnostics, not biological conclusions.

Evidence: `memote-summary.json#/families/1`.

### Annotation - Reactions

Under MEMOTE 0.17.0 default test conditions, the Annotation - Reactions family recorded 8 passed, 12 failed, and 0 skipped terminal cases across 4 tests. These are MEMOTE diagnostics, not biological conclusions.

Evidence: `memote-summary.json#/families/2`.

### Annotation - Genes

Under MEMOTE 0.17.0 default test conditions, the Annotation - Genes family recorded 1 passed, 20 failed, and 0 skipped terminal cases across 3 tests. These are MEMOTE diagnostics, not biological conclusions.

Evidence: `memote-summary.json#/families/3`.

### Annotation - SBO Terms

Under MEMOTE 0.17.0 default test conditions, the Annotation - SBO Terms family recorded 1 passed, 9 failed, and 1 skipped terminal cases across 11 tests. These are MEMOTE diagnostics, not biological conclusions.

Evidence: `memote-summary.json#/families/4`.

### SBML

Under MEMOTE 0.17.0 default test conditions, the SBML family recorded 2 passed, 0 failed, and 0 skipped terminal cases across 2 tests. These are MEMOTE diagnostics, not biological conclusions.

Evidence: `memote-summary.json#/families/5`.

### Basic Information

Under MEMOTE 0.17.0 default test conditions, the Basic Information family recorded 6 passed, 2 failed, and 0 skipped terminal cases across 8 tests. These are MEMOTE diagnostics, not biological conclusions.

Evidence: `memote-summary.json#/families/6`.

### Metabolite Information

Under MEMOTE 0.17.0 default test conditions, the Metabolite Information family recorded 3 passed, 2 failed, and 0 skipped terminal cases across 5 tests. These are MEMOTE diagnostics, not biological conclusions.

Evidence: `memote-summary.json#/families/7`.

### Reaction Information

Under MEMOTE 0.17.0 default test conditions, the Reaction Information family recorded 5 passed, 2 failed, and 0 skipped terminal cases across 7 tests. These are MEMOTE diagnostics, not biological conclusions.

Evidence: `memote-summary.json#/families/8`.

### Gene-Protein-Reaction (GPR) Associations

Under MEMOTE 0.17.0 default test conditions, the Gene-Protein-Reaction (GPR) Associations family recorded 2 passed, 1 failed, and 0 skipped terminal cases across 3 tests. These are MEMOTE diagnostics, not biological conclusions.

Evidence: `memote-summary.json#/families/9`.

### Biomass

Under MEMOTE 0.17.0 default test conditions, the Biomass family recorded 13 passed, 4 failed, and 0 skipped terminal cases across 9 tests. These are MEMOTE diagnostics, not biological conclusions.

Evidence: `memote-summary.json#/families/10`.

### Energy Metabolism

Under MEMOTE 0.17.0 default test conditions, the Energy Metabolism family recorded 12 passed, 6 failed, and 2 skipped terminal cases across 4 tests. These are MEMOTE diagnostics, not biological conclusions.

Evidence: `memote-summary.json#/families/11`.

### Network Topology

Under MEMOTE 0.17.0 default test conditions, the Network Topology family recorded 0 passed, 6 failed, and 0 skipped terminal cases across 6 tests. These are MEMOTE diagnostics, not biological conclusions.

Evidence: `memote-summary.json#/families/12`.

### Matrix Conditioning

Under MEMOTE 0.17.0 default test conditions, the Matrix Conditioning family recorded 4 passed, 0 failed, and 0 skipped terminal cases across 4 tests. These are MEMOTE diagnostics, not biological conclusions.

Evidence: `memote-summary.json#/families/13`.

### Experimental Data Comparison

Under MEMOTE 0.17.0 default test conditions, the Experimental Data Comparison family recorded 0 passed, 0 failed, and 2 skipped terminal cases across 2 tests. These are MEMOTE diagnostics, not biological conclusions.

Evidence: `memote-summary.json#/families/14`.

## Limitations

- Passed, failed, and skipped are MEMOTE outcomes under its default configured conditions.
- These diagnostics do not establish biological validity, phenotype accuracy, or suitability for a scientific use case.
- Biological interpretation requires a separate, versioned protocol with explicit conditions and acceptance criteria.
