<!--
Template version 1.0.0. Copy templates/result/ to results/AF-NNNN-<slug>/, then copy
templates/paper/ to paper/ and templates/logs/ to logs/. Replace every <<...>> token
(`python3 scripts/afm.py check` reports any that remain). Delete this comment.
-->

# <<AF-NNNN>> · <<TITLE>>

| | |
|---|---|
| Identifier | <<AF-NNNN>>, version <<VERSION>> (<<YYYY-MM-DD>>) |
| Status | published |
| Author | AxiomForge · axiomforge.math@gmail.com |
| MSC2020 | Primary <<MSC PRIMARY>>; Secondary <<MSC SECONDARY>> |
| Manuscript | `paper/main.pdf` |
| Lean package | `lean/` (`axiomforge-af<<NNNN>>`, Lean <<LEAN VERSION>>, Mathlib `<<MATHLIB REV>>`) |

<<ONE-PARAGRAPH SUMMARY>>

## Main results

| Label | Statement | Lean declaration |
|---|---|---|
| <<THEOREM LABEL>> | <<STATEMENT>> | `<<LEAN NAME>>` |

## Verification status

| Dimension | <<THEOREM LABEL>> |
|---|---|
| Conventional proof | <<PROOF STATUS>> |
| Computational certificates | <<CERTIFICATES STATUS>> |
| Lean formalization | <<FORMALIZATION STATUS>> |
| Lean build | <<BUILD STATUS>> |
| Axiom audit | <<AXIOMS STATUS>> |
| Statement fidelity review | <<STATEMENT REVIEW STATUS>> |
| Independent mathematical review | <<INDEPENDENT REVIEW STATUS>> |
| Literature and novelty review | <<LITERATURE REVIEW STATUS>> |

The authoritative values are in [result.toml](result.toml); definitions in the archive's
verification policy (`docs/verification-policy.md`).

## Reproducing

Requirements: Python 3.11+, TeX Live 2023+ with `latexmk`, poppler-utils, elan.
<<ADDITIONAL REQUIREMENTS OR DELETE>>

```bash
(cd lean && lake exe cache get && lake build)
(cd paper && latexmk -pdf main.tex)
<<CERTIFICATE CHECKER COMMANDS OR DELETE>>
```

Axiom audit: `#print axioms <<LEAN NAME>>` reports only `propext`, `Classical.choice`
and `Quot.sound`. From the archive root, `python3 scripts/afm.py verify <<AF-NNNN>>`
runs every check.

## Contents

| Path | Content |
|---|---|
| `result.toml` | metadata and verification status |
| `paper/` | manuscript sources and `main.pdf` |
| `lean/` | Lake package |
| `logs/` | research history, experiments, certificates, AI contributions |
| `CHANGELOG.md` | versions and corrections |
| `CITATION.cff` | citation metadata |

## AI-assisted research

<<ONE SENTENCE>> Full disclosure: `logs/ai-contributions.md`
and the section *AI-assisted research disclosure* of the manuscript.

## Citation

See [CITATION.cff](CITATION.cff).
