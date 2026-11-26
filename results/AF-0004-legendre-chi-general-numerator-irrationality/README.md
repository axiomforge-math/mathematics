# AF-0004 · Irrationality of χ₂(a/q) and Ti₂(a/q) for the numerators a = 3, 4, 5, 8: a candidate proof

> **Preprint.** A complete written argument, not yet independently verified. Its computations
> are reproduced; its Lean formalization is in preparation. The archive does not establish the
> main theorem until the contribution reaches level V4 (see `docs/verification-policy.md` of the
> archive).

| | |
|---|---|
| Identifier | AF-0004, version 0.1.0 (2026-11-26) |
| Status | preprint |
| Author | AxiomForge · axiomforge.math@gmail.com |
| MSC2020 | Primary 11J72; Secondary 33B30 |
| Manuscript | `paper/main.pdf` |
| Lean package | `lean/` (`axiomforge-af0004`, Lean v4.34.0-rc1, Mathlib `f385f9fd18abed332ebcd3df239cb357e264aceb`) |

Here χ₂(x) = Σ_{j≥0} x^{2j+1}/(2j+1)² is Legendre's chi function and Ti₂(x) = Σ_{j≥0} (−1)^j x^{2j+1}/(2j+1)² the inverse tangent integral. The ranges below begin well below the range q > 54 e⁴ a² that the authors read off from a general criterion for shifted polylogarithms (not re-derived from the criterion; no smaller explicit thresholds for these numerators were found in the literature). The approximations are Hankel determinants of a moment functional with poles at the negative half-integers, with more poles than rows (ratio 7/6 or 5/4), as in an earlier AxiomForge preprint on the numerator 2, which itself starts from work of Krisman. The numerators treated here need three arithmetic estimates that are absent for the numerator 2: a bound at the primes dividing a (each pole can be used only once), a bound at the prime 2 when a is odd (forward differences in a basis adapted to the poles), and the parity-minor bound at 2 for a = 4 and a = 8. A single inequality carries each case from its threshold to all larger denominators.

## Main result

| Label | Statement | Lean declaration |
|---|---|---|
| `thm:main` | Let a ∈ {3, 4, 5, 8} and q odd, prime to a. χ₂(a/q) is irrational if q ≥ 131 (a = 3), 995 (a = 4), 829 (a = 5), 12061 (a = 8); Ti₂(a/q) is irrational if q ≥ 257 (a = 3), 995 (a = 4), 1609 (a = 5), 12061 (a = 8). Both functions are odd, so the same holds at −a/q. | none yet (formalization in preparation); conditional versions below |

The thresholds are inclusive and sufficient for the estimates used; they are not claimed to be optimal.

## Status

* **Proved** (elementary, written in full): the irrationality criterion, oddness, the series identity, the final deduction.
* **Certified by computation and reproduced** (AI-internal): the profile integrals I(7/6) = −2.1131641365… and I(5/4) = −2.3556398320…, the six threshold margins A − B (≥ 0.013945786, 0.005113500, 0.001699724, 0.001300300, 0.000713481, 0.000758530 per h² for (a, q) = (3, 131), (3, 257), (4, 995), (5, 829), (5, 1609), (8, 12061)), the propagation check for larger q, and the six local determinants (integer polynomials with Cauchy bounds below 189).
* **Candidate** (written proof, not independently verified): the bound at the primes dividing a, the bound at the prime 2 for odd a and the parity-minor bound for a = 4, 8 (the weakest link, supported by finite checks only), the exceptional primes, the ordinary-prime profile, the archimedean decay, the nonvanishing reduction, and the propagation to all larger q. Status of each step: the introduction of the manuscript.
* **Lean:** the package builds and `#print axioms` reports only `propext`, `Classical.choice` and `Quot.sound` for each of its 36 audited declarations (`lean/AXIOMS.txt`). It proves unconditionally the irrationality criterion, the definitions and oddness of χ₂ and Ti₂, the explicit polynomials T_n and their degree bound, the exact constants c₂ and the six strict margins. The main theorem is proved only conditionally:

| Lean declaration | Hypotheses | Check |
|---|---|---|
| `AxiomForge.LegendreChiGeneral.irrational_legendreChi_div_of_estimates` | conditional on a hypothesis packaging the arithmetic estimate, the size estimate and the nonvanishing at prime indices, with rounded rates | build passing; axioms standard |
| `AxiomForge.LegendreChiGeneral.irrational_inverseTangentIntegral_div_of_estimates` | conditional on a hypothesis packaging the arithmetic estimate, the size estimate and the nonvanishing at prime indices, with rounded rates | build passing; axioms standard |
| `AxiomForge.LegendreChiGeneral.irrational_legendreChi_neg_div_of_estimates` | conditional on a hypothesis packaging the arithmetic estimate, the size estimate and the nonvanishing at prime indices, with rounded rates | build passing; axioms standard |
| `AxiomForge.LegendreChiGeneral.irrational_inverseTangentIntegral_neg_div_of_estimates` | conditional on a hypothesis packaging the arithmetic estimate, the size estimate and the nonvanishing at prime indices, with rounded rates | build passing; axioms standard |

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
computations `python-flint` and `mpmath` at the versions of `logs/experiments/requirements.txt`.

```bash
(cd paper && latexmk -pdf main.tex)                          # the manuscript
(cd lean && lake exe cache get && lake build)                 # the Lean package
python3 -m pip install -r logs/experiments/requirements.txt
(cd logs/experiments/scripts && python3 run_checks.py all)    # every computation
```

`run_checks.py` writes every output to `logs/experiments/runs/` and exits with status 1 if a
check fails; `logs/experiments/README.md` lists each program and what it establishes. From the
archive root, `python3 scripts/afm.py verify AF-0004` runs the archive checks.

## Known limitations and open points

* **No independent review.** No human expert independent of the AI systems has reviewed the argument; all checks and the reading of the arithmetic lemmas are AI-internal.
* **Small margins** (0.000713 to 0.0139 per h², the smallest for (5, 1609) and (8, 12061)) compared with the individual constants: an error of a few parts in 10⁴ in a constant would invalidate the corresponding row. No effective bound for h is given.
* **The parity-minor bound at 2 for even a** is the weakest link: new, checked on exact data at small sizes only; the bound at 2 for odd a is new as well; the O(h log h) terms are not explicit.
* **Ordinary primes** were tested at finite sizes only for the numerator 2 in an earlier audit; for these numerators only the exceptional primes were tested.
* **Thresholds** are sufficient for these estimates, not optimal; the literature range q > 54 e⁴ a² was not re-derived.
* **Literature.** References inherited from the numerator-2 work, and the unrefereed preprints of Krisman, were checked at the level of statements only.
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
reconstruction, check computations, manuscript and Lean development with Claude Sonnet 5.5, Claude Fable 5.2 and
Claude Opus 5.5 (Anthropic); no independent human review has taken place. Full disclosure: `logs/ai-contributions.md` and
the section *AI-assisted research disclosure* of the manuscript.

## Citation

AxiomForge, *Irrationality of χ₂(a/q) and Ti₂(a/q) for the numerators a = 3, 4, 5, 8*, preprint AF-0004, version 0.1.0, 2026-11-26,
https://github.com/axiomforge-math/mathematics/tree/main/results/AF-0004-legendre-chi-general-numerator-irrationality. See
[CITATION.cff](CITATION.cff).
