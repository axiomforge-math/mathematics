# Reproducibility

Every published contribution can be rebuilt and re-verified from its own directory alone.
This document lists the requirements and the procedure.

## 1. Requirements

| Component | Version | Used for |
|---|---|---|
| Python | 3.11 or later (standard library only) | `scripts/afm.py`; certificate checkers, unless a contribution states otherwise |
| TeX distribution | TeX Live 2023 or later, with `latexmk`, `pdflatex`, `bibtex` | the manuscript |
| LaTeX packages | `amsart`, `lmodern`, `microtype`, `hyperref`, `cleveref`, `mathtools`, `thmtools`, `enumitem`, `booktabs`, `geometry`, `xcolor` | the manuscript |
| poppler-utils | any recent | PDF layout checks (`pdftotext`, `pdfinfo`, `pdffonts`) |
| elan | any recent | installs the Lean toolchain named in `lean/lean-toolchain` |
| Lean and Mathlib | exactly as pinned by the contribution | the formalization |

A contribution that needs anything else (for example a Python package for a certificate
checker) lists it, with exact versions, in its `README.md` and
`logs/experiments/README.md`.

## 2. Procedure

From the repository root, for a contribution `AF-NNNN`:

```bash
python3 scripts/afm.py check AF-NNNN    # metadata, files, gates, source scans (seconds)
python3 scripts/afm.py lean AF-NNNN     # lake exe cache get, lake build, axiom audit
python3 scripts/afm.py paper AF-NNNN    # latexmk, log and PDF layout checks
python3 scripts/afm.py verify AF-NNNN   # all three
python3 scripts/afm.py isolate AF-NNNN  # verify a copy in a fresh temporary directory
```

Without the archive tool, from the contribution's directory:

```bash
(cd lean && lake exe cache get && lake build)
(cd paper && latexmk -pdf main.tex)
```

and then the commands of `logs/experiments/README.md` for each certificate.

The first Lean build downloads the Mathlib build cache for the pinned revision (several
gigabytes); later builds reuse it. Shared toolchains and caches are an optimisation only.

## 3. What is reproduced

| Artefact | Reproduction | Expected outcome |
|---|---|---|
| Lean proofs | `lake build`, then `#print axioms` on each main theorem | build passes; axioms ⊆ {`propext`, `Classical.choice`, `Quot.sound`} |
| Manuscript | `latexmk -pdf main.tex` | no undefined reference or citation; same content as the committed `main.pdf` |
| Certificates | the checker commands in `logs/experiments/README.md` | exit status 0; the checker prints what it verified |
| Exploratory computations | the scripts in `logs/experiments/scripts/` | the recorded numbers, within the stated tolerance; they support no proof |

The committed `main.pdf` is the output of the committed sources; byte-for-byte identity
across TeX distributions is not expected.

## 4. Certificates

A certificate is a finite object (a file in `logs/experiments/certificates/`) together
with a checker and a proof, in the manuscript, that acceptance by the checker implies the
mathematical statement used. Requirements:

* the checker is separate from the program that generated the certificate, and is short
  enough to be read;
* exact rational or integer arithmetic, or rigorous interval arithmetic with outward
  rounding; floating-point arithmetic never proves an inequality;
* the checker exits non-zero on failure and does not rely on `assert` statements (which
  `python -O` removes);
* the certificate's SHA-256 and the exact checker command are recorded in
  `logs/verification.md`.

## 5. Self-containment

`python3 scripts/afm.py check` rejects symbolic links, absolute local paths, LaTeX inputs
outside the contribution and Lake dependencies by local path. `isolate` proves the point
by verifying a copy outside the repository.
