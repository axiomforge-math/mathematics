# AF-0003 · Irrationality of χ₂(2/q) and Ti₂(2/q) for odd q ≥ 81: a candidate proof

> **Preprint.** A complete written argument, not yet independently verified. Its computations
> are reproduced; its Lean formalization is in preparation. The archive does not establish the
> main theorem until the contribution reaches level V4 (see `docs/verification-policy.md` of the
> archive).

| | |
|---|---|
| Identifier | AF-0003, version 0.1.0 (2026-11-26) |
| Status | preprint |
| Author | AxiomForge · axiomforge.math@gmail.com |
| MSC2020 | Primary 11J72; Secondary 33B30 |
| Manuscript | `paper/main.pdf` |
| Lean package | `lean/` (`axiomforge-af0003`, Lean v4.34.0-rc1, Mathlib `f385f9fd18abed332ebcd3df239cb357e264aceb`) |

Here χ₂(x) = Σ_{j≥0} x^{2j+1}/(2j+1)² is Legendre's chi function and Ti₂(x) = Σ_{j≥0} (−1)^j x^{2j+1}/(2j+1)² the inverse tangent integral. The best previously claimed range, in an unrefereed and primarily AI-generated preprint, is odd q ≥ 175 for χ₂(2/q); the criterion of David, Hirata-Kohno and Kawashima applies at −4/q² as well and should give a threshold of the same order for Ti₂(2/q), which we have not computed and have not found stated. The approximations are Hankel determinants of a moment functional with poles at the negative half-integers, with 7/6 times as many poles as rows and, for q = 81, a band of double zeros. Three new estimates are needed: a parity-separated bound at the prime 2, a residue-class profile for the ordinary primes, and nonvanishing at prime indices by reduction to three local Hankel determinants.

## Main result

| Label | Statement | Lean declaration |
|---|---|---|
| `thm:main` | For every odd integer q ≥ 81 the numbers χ₂(2/q) and Ti₂(2/q) are irrational; since χ₂ and Ti₂ are odd, so are χ₂(−2/q) and Ti₂(−2/q). | none yet (formalization in preparation); conditional versions below |

## Status

* **Proved** (elementary, written in full): Elementary steps (the criterion, oddness, the series identity, the final deduction).
* **Certified by computation and reproduced:** The profile integrals I_G = −2.1131641365… and I_B = −1.9870895819… (exact, two implementations), the comparison densities with B − A₋ ≤ −0.0068631 (q ≥ 83, general construction; margin ≥ 0.006862 per h²) and ≤ −0.0056790 (q = 81, band construction; margin ≥ 0.005678 per h²), and the local determinants (general: integer polynomials with Cauchy root bound below 189; band: six nonzero exact determinants).
* **Candidate** (written proof, not independently verified): The bound at the prime 2 (Theorem 3.3), the exceptional primes, the ordinary-prime profile (Proposition 5.7 and Lemma 5.8, now written in full), the archimedean decay and the nonvanishing reduction. Status of each step: the introduction of the manuscript.
* **Lean:** the package builds and `#print axioms` reports only `propext`, `Classical.choice`
  and `Quot.sound` for each of its 29 audited declarations (`lean/AXIOMS.txt`). It proves
  unconditionally the oddness and irrationality-transfer lemmas, `decayRate_lt_contentRate` and `primeTwoProfile_min` (the minimum −1847/1100 of the prime-2 function of the band construction), and the irrationality criterion. The main theorem is proved only conditionally:

| Lean declaration | Hypotheses | Check |
|---|---|---|
| `AxiomForge.LegendreChi.irrational_legendreChi_two_div_of_estimates` | conditional on a hypothesis packaging the arithmetic estimate, the size estimate and the nonvanishing at prime indices, with rounded rates | build passing; axioms standard |
| `AxiomForge.LegendreChi.irrational_inverseTangentIntegral_two_div_of_estimates` | conditional on a hypothesis packaging the arithmetic estimate, the size estimate and the nonvanishing at prime indices, with rounded rates | build passing; axioms standard |
| `AxiomForge.LegendreChi.irrational_legendreChi_neg_two_div_of_estimates` | conditional on a hypothesis packaging the arithmetic estimate, the size estimate and the nonvanishing at prime indices, with rounded rates | build passing; axioms standard |
| `AxiomForge.LegendreChi.irrational_inverseTangentIntegral_neg_two_div_of_estimates` | conditional on a hypothesis packaging the arithmetic estimate, the size estimate and the nonvanishing at prime indices, with rounded rates | build passing; axioms standard |

  These conditional theorems are not a formalization of the main theorem.

| Dimension | `thm:main` |
|---|---|
| Conventional proof | candidate |
| Computational certificates | reproduced |
| Lean formalization | in preparation (conditional final deduction only) |
| Lean build | passing |
| Axiom audit | standard |
| Statement fidelity review | pending |
| Independent mathematical review | AI-internal only; no human review |
| Literature and novelty review | checked (AI-internal survey; scope in `logs/verification.md`) |

The authoritative values are in [result.toml](result.toml); the evidence for each is in
[logs/verification.md](logs/verification.md).

## Reproducing

Requirements: Python 3.11+, TeX Live 2023+ with `latexmk`, poppler-utils, elan; for the
computations `python-flint` and `mpmath` (and SymPy where listed) at the versions of
`logs/experiments/requirements.txt`.

```bash
(cd paper && latexmk -pdf main.tex)                          # the manuscript
(cd lean && lake exe cache get && lake build)                 # the Lean package
python3 -m pip install -r logs/experiments/requirements.txt
(cd logs/experiments/scripts && python3 run_checks.py all)    # every computation
```

`run_checks.py` writes every output to `logs/experiments/outputs/` and exits with status 1
if a check fails; `logs/experiments/README.md` lists each program, what it establishes and its
run time. From the archive root, `python3 scripts/afm.py verify AF-0003` runs the archive checks.

## Known limitations and open points

* **No independent review.** No human expert independent of the AI systems has reviewed the argument; all checks are AI-internal.
* **Small margins** (0.0069 and 0.0057 per h²; certified 0.006863 and 0.005679) compared with the individual constants: an error of a few thousandths in any constant would invalidate the corresponding case.
* **Ordinary primes.** Proposition 5.7 and Lemma 5.8 (passage from exact class counts to the limiting profile, breakpoints and convexity) are now proved in full but not independently verified; both profile implementations encode the same class-type model, so an error in the model would not be detected by their agreement.
* **Prime 2 and reduction of the local functionals** (Sections 3 and 7) are new estimates, checked only on exact data at small sizes.
* **The case q = 79 and the square construction** (Section 9) are not used in the proof and describe limits of these estimates, not of the determinants: the general construction does not reach q = 81 with the recorded density (the repaired verifier gives B − A₋ ≤ +0.005332 there), and the q = 79 numbers are floating point and rest on an unproved bound B ≤ 1 near 0; the remark on the square construction at q = 127 rests on earlier computations not re-verified.
* **Literature.** The threshold 11 795 for χ₂(2/q) is a specialisation reported in the literature, not re-derived, and the threshold of the same criterion for Ti₂(2/q) has not been computed; statements attributed to Hata (1990) are as reported by Krisman, whose preprint (version 2) was read for the citations of the manuscript, but only at the level of statements.
* **Formalization.** The estimates are not formalized; the Lean theorems are conditional on them.

## Contents

| Path | Content |
|---|---|
| `result.toml` | metadata and verification status |
| `paper/` | manuscript sources and `main.pdf` |
| `lean/` | Lake package (theorem map in `lean/README.md`) |
| `logs/` | history, verification record, experiments, AI contributions |
| `CHANGELOG.md` | versions and corrections |
| `CITATION.cff` | citation metadata |

## AI-assisted research

The original research was carried out with GPT-6.2 XHigh (web version), as stated by the AxiomForge owners, and the
reconstruction, audit, recomputations, manuscript, Lean development and packaging with Claude Opus 5.5 (Anthropic), an adversarial
AI-internal review and the resulting revision with Claude Fable 5.2 (Anthropic), and further revision and the packaging of
this release with Claude Sonnet 5.5 (Anthropic); no independent human review has taken place. Full disclosure: `logs/ai-contributions.md` and
the section *AI-assisted research disclosure* of the manuscript.

## Citation

AxiomForge, *Irrationality of χ₂(2/q) and Ti₂(2/q) for odd q ≥ 81: a candidate proof*, preprint AF-0003, version 0.1.0, 2026-11-26,
https://github.com/axiomforge-math/mathematics/tree/main/results/AF-0003-legendre-chi-inverse-tangent-irrationality. See
[CITATION.cff](CITATION.cff).
