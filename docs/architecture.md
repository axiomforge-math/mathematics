# Architecture

The AxiomForge archive is a collection of **independent, self-contained mathematical
contributions**, together with the policies, templates and tools needed to read,
reproduce and catalogue them.

```text
mathematics/
├── README.md, AGENTS.md, CLAUDE.md, GEMINI.md, CONTRIBUTING.md, CITATION.cff, Makefile
├── results/AF-NNNN-<slug>/     one self-contained contribution per directory
├── catalogue/                  generated from results/*/result.toml (never edited by hand)
├── templates/                  canonical scaffolding, copied (never imported) into results
├── docs/                       policies: verification, writing, formalization, naming, …
├── scripts/afm.py              archive tool: check, verify, catalogue, isolation test
├── tests/                      test suite of the archive tool (pytest)
└── .github/                    pull-request template, assistant instructions
```

## Self-contained contributions

Each `results/AF-NNNN-<slug>/` can be copied anywhere and reproduced on its own:

```text
AF-NNNN-<slug>/
├── README.md         entry point: statements, status, how to reproduce
├── result.toml       authoritative metadata (theorems, Lean names, verification)
├── CITATION.cff, CHANGELOG.md
├── paper/            amsart manuscript: main.tex, sections/, references.bib, main.pdf
├── lean/             independent Lake package (own lean-toolchain, manifest, Mathlib pin)
└── logs/             curated research history, experiments and certificates
```

No contribution imports another contribution, a global macro file, a shared Lean
library, or repository-level scripts. Different contributions may pin different Lean and
Mathlib versions. Templates are copied at creation and their version is recorded in
`result.toml`; later template changes never alter a published contribution. Reusing
machinery from an earlier contribution means citing it and including a verified copy.

The archive tool (`scripts/afm.py`, wrapped by the `Makefile`) only discovers, checks
and catalogues contributions. It is never required to reproduce one: every
contribution documents its own reproduction commands.

## Metadata and catalogue

`result.toml` is the single source of truth for a contribution: identifiers, MSC2020
classification, main theorems with their Lean declaration names, and the verification
status of each theorem in every dimension of the [verification policy](verification-policy.md).
The files in `catalogue/` are generated from these records by `make catalogue`
(`python3 scripts/afm.py catalogue`); `make catalogue-check` fails when they are stale.
No continuous integration is configured yet: run the checks locally.

## Optional shared caches

Toolchains (`~/.elan`), Mathlib build caches and TeX installations may be shared between
packages to save time and disk. This is an optimisation only: every package also builds
from a clean checkout with `lake exe cache get && lake build`.

## Versioning

Each contribution is versioned independently with tags `af-NNNN-vMAJOR.MINOR.PATCH`.
Corrections never silently change a published statement; see the
[publication policy](publication-policy.md). Requirements and the reproduction procedure
are in [reproducibility.md](reproducibility.md).
