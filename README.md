# AxiomForge Mathematics

Open mathematical research with AI-assisted proofs and Lean 4 formal verification.

AxiomForge publishes self-contained mathematical contributions. Each contribution states
its theorems precisely, proves them in a conventional manuscript, verifies them in Lean 4
against a pinned version of Mathlib, and documents how AI systems were used. Nothing is
published until every advertised theorem meets the verification gate described below.

## Current state

**No contribution has been published yet.** The `results/` directory is empty and the
[catalogue](catalogue/results.md) lists no result. This repository currently contains the
policies, templates and tooling under which contributions will be published.

## What a contribution contains

Every contribution lives in its own directory `results/AF-NNNN-<slug>/` and can be copied
anywhere and reproduced on its own.

| Part | Content |
|---|---|
| `README.md` | statements, verification status, reproduction commands |
| `result.toml` | authoritative metadata: identifier, MSC2020 classes, theorems, Lean names, verification status |
| `paper/` | the manuscript (`amsart`), its sources and the compiled `main.pdf` |
| `lean/` | an independent Lake package with its own Lean toolchain and Mathlib revision |
| `logs/` | curated research history: attempts, obstructions, experiments, certificates, AI contributions |
| `CITATION.cff`, `CHANGELOG.md` | citation metadata and version history |

See [docs/architecture.md](docs/architecture.md) for the layout and
[docs/naming-conventions.md](docs/naming-conventions.md) for identifiers and names.

## Verification standard

Correctness is recorded in several independent dimensions (conventional proof,
computational certificates, Lean formalization, Lean build, axiom audit, statement
fidelity, independent review, literature review), never as a single flag. A contribution
is published only when every main theorem reaches level **V4**: a complete conventional
proof, a complete Lean formalization that builds, an axiom audit reporting only
`propext`, `Classical.choice` and `Quot.sound`, and a review that the Lean statement
expresses the claimed theorem. Whether an independent human review has taken place is
always stated explicitly.

Before V4 a contribution may be released as a clearly labelled **preprint**: a complete
written argument with reproduced computations and a checked literature review, whose
Lean development is marked "in preparation". Preprints carry versions `0.x`, say
"Preprint" on the title page and are listed in a separate catalogue section. The archive
does not establish a preprint's main theorems until they reach V4 (version `1.0.0`). See
the [preprint tier](docs/verification-policy.md#preprint-tier).

| Document | Subject |
|---|---|
| [Verification policy](docs/verification-policy.md) | dimensions, gates, levels V0–V5, certificates |
| [Formalization policy](docs/formalization-policy.md) | Lean packages, trust policy, statement fidelity |
| [Mathematical writing](docs/mathematical-writing.md) | manuscript structure and layout |
| [Reproducibility](docs/reproducibility.md) | requirements and reproduction procedure |
| [Publication policy](docs/publication-policy.md) | identifiers, versions, corrections, withdrawals, attribution, licensing |
| [AI disclosure policy](docs/ai-disclosure-policy.md) | how AI involvement is reported |

## Reproducing a result

Requirements: Python 3.11 or later, a TeX distribution with `latexmk` (TeX Live 2023 or
later), `poppler-utils`, and [elan](https://github.com/leanprover/elan) for Lean. Each
contribution's README gives its own commands; in outline:

```bash
cd results/AF-NNNN-<slug>
(cd paper && latexmk -pdf main.tex)              # rebuild the manuscript
(cd lean && lake exe cache get && lake build)     # rebuild the formal proofs
```

The archive tool runs the same checks that gate publication, using only the Python
standard library:

```bash
python3 scripts/afm.py check AF-NNNN      # metadata, files, publication gate (no builds)
python3 scripts/afm.py verify AF-NNNN     # check + Lean build and axiom audit + manuscript build
python3 scripts/afm.py isolate AF-NNNN    # verify a copy in a fresh temporary directory
```

Details: [docs/reproducibility.md](docs/reproducibility.md).

## Citing

Cite an individual contribution with the `CITATION.cff` file in its directory. To cite
the archive as a whole, use the repository [CITATION.cff](CITATION.cff).

## AI-assisted research

AxiomForge uses AI systems for exploration, proof search, computation, auditing,
manuscript preparation, formalization and engineering. Every contribution names the
systems used and their roles, on the title page of its manuscript, in a dedicated
manuscript section and in `logs/ai-contributions.md`. AI involvement is never presented
as independent certification, and AI systems are not listed as authors. See the
[AI disclosure policy](docs/ai-disclosure-policy.md).

## Contributing and corrections

Error reports are the most valuable contribution: see [CONTRIBUTING.md](CONTRIBUTING.md).
Corrections and withdrawals follow the [publication policy](docs/publication-policy.md).

## Licence

The licence of this repository is to be decided by its owners. No `LICENSE` file exists
yet, so no licence is currently granted beyond what the law allows without one.

## Contact

AxiomForge · <axiomforge.math@gmail.com> · <https://github.com/axiomforge-math>
