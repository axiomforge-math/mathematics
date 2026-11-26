# AF-0002 · The irrationality of ψ₁(k/5) − π²/2: a candidate proof with separated Löwner determinants

> **Preprint.** A complete written argument, not yet independently verified. Its computations
> are reproduced; its Lean formalization is in preparation. The archive does not establish the
> main theorem until the contribution reaches level V4 (see `docs/verification-policy.md` of the
> archive).

| | |
|---|---|
| Identifier | AF-0002, version 0.1.0 (2026-11-26) |
| Status | preprint |
| Author | AxiomForge · axiomforge.math@gmail.com |
| MSC2020 | Primary 11J72; Secondary 33B15, 31A15 |
| Manuscript | `paper/main.pdf` |
| Lean package | `lean/` (`axiomforge-af0002`, Lean v4.34.0-rc1, Mathlib `f385f9fd18abed332ebcd3df239cb357e264aceb`) |

Since ψ₁(1/2) = π²/2, ξ_k is the difference ψ₁(k/5) − ψ₁(1/2). The proof studies determinants of Löwner (divided-difference) matrices of ψ(z + k/5) − ψ(z + 1/2) on h common nodes and h/8 border nodes, in the framework of S. Litsey, who lists these numbers among those that his interleaved (alternating) border does not reach (the statement concerns neither ψ₁(k/5) itself nor ψ₁(k/5) − π²/6). The new ingredient separates the border rows from the border columns: an Andréief–Cauchy factorization divides every determinant by exactly 2^{m(m−1)}, m = h/16, without changing any odd-prime valuation, for a net gain of (log 2)/256 per h². With a two-layer p-adic bound for the denominators and a logarithmic-energy bound on a contour, two computer-assisted certificates give the comparison with a certified margin of 0.00075448 per h².

## Main result

| Label | Statement | Lean declaration |
|---|---|---|
| `thm:main` | For each k ∈ {1, 2, 3, 4} the number ξ_k = ψ₁(k/5) − π²/2 is irrational (ψ₁ the trigamma function). | none yet (formalization in preparation); conditional versions below |

## Status

* **Proved** (written in full; AI-internal reviews only): the separation identity (Proposition 2.6, Corollaries 2.7–2.8; AI-internal adversarial review, exact checks for h ≤ 64), the entrywise bounds (Lemma 4.2; AI-internal adversarial review, which reported exact checks with no violation in 10,640 comparisons, programs not part of this package, and led to the corrected Corollary 4.3(c)), the final deduction.
* **Certified by computation and reproduced:** The arithmetic constant 𝒜 = 3.5121303755913638… (an exact rational, Proposition 4.15) and the decay constant 𝒟_sep ≥ 3.5128848577 (Proposition 5.10), hence the margin 𝒟_sep − 𝒜 ≥ 0.00075448 per h² (certified 0.00075448215…); the original programs state the rounded margin 0.000476.
* **Candidate** (written proof, not independently verified): Nonvanishing with one deletion (Proposition 3.1), the polar congruences and the nullspace bound (Lemma 4.5, Proposition 4.8), the profile lemmas (Lemmas 4.12–4.13, on which the exact integration of 𝒜 rests), the prime-number-theorem bookkeeping (Theorem 4.1), the contour representation and the energy criterion (Lemma 5.3, Proposition 5.7). Status of each step: Table 2 of the manuscript.
* **Lean:** the package builds and `#print axioms` reports only `propext`, `Classical.choice`
  and `Quot.sound` for each of its 25 audited declarations (`lean/AXIOMS.txt`). It proves
  unconditionally `irrational_xi_one_or_xi_two_or_xi_three_or_xi_four` (at least one ξ_k is irrational), `irrational_pi_sq`, `xi_one_add` (ξ₁ + ξ₂ + ξ₃ + ξ₄ = 2π²) and `arithmeticRate_lt` (the rational 𝒜 is below 3.512131). The main theorem is proved only conditionally:

| Lean declaration | Hypotheses | Check |
|---|---|---|
| `AxiomForge.Trigamma.irrational_xi_one_of_estimates` | conditional on `LownerEstimates` (nonvanishing with one deletion, log den ≤ 3.512131 h², |P_sep,I(ξ)| ≤ e^{−3.512607 h²}) | build passing; axioms standard |
| `AxiomForge.Trigamma.irrational_xi_two_of_estimates` | conditional on `LownerEstimates` (nonvanishing with one deletion, log den ≤ 3.512131 h², |P_sep,I(ξ)| ≤ e^{−3.512607 h²}) | build passing; axioms standard |
| `AxiomForge.Trigamma.irrational_xi_three_of_estimates` | conditional on `LownerEstimates` (nonvanishing with one deletion, log den ≤ 3.512131 h², |P_sep,I(ξ)| ≤ e^{−3.512607 h²}) | build passing; axioms standard |
| `AxiomForge.Trigamma.irrational_xi_four_of_estimates` | conditional on `LownerEstimates` (nonvanishing with one deletion, log den ≤ 3.512131 h², |P_sep,I(ξ)| ≤ e^{−3.512607 h²}) | build passing; axioms standard |

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
run time. From the archive root, `python3 scripts/afm.py verify AF-0002` runs the archive checks.

## Known limitations and open points

* **No independent review.** No person has reviewed the argument; all reviews and recomputations are AI-internal. Nonvanishing (Proposition 3.1) and the prime-number-theorem bookkeeping have had no review of any kind.
* **Thin margin.** 𝒟_sep − 𝒜 ≥ 0.00075448 per h² is about 2·10⁻⁴ of the compared quantities: a relative error of order 10⁻⁴ in either certificate could invalidate the proof. Finite-h data cannot test it, since the separation affects den·|P| only for h of the order of several thousand.
* **Energy criterion.** Step 4 of Proposition 5.7 near the atoms closest to the origin and on the vertical rays, the Riemann sums of Step 7, and the h-independence of the constant C₁(k) of Lemma 5.3 deserve scrutiny.
* **The constant p₀** of Definition 4.6: only its finiteness is used; it was not computed. In the finite tests (`check_polar_bounds.py`), primes whose block ranks modulo p differ from the rational ranks occur in four of the finite tests (the largest p = 31, at h = 128; Appendix A.4); all are below 120 and none contradicts Proposition 4.8, but the set of such primes over all types has not been determined.
* **Literature.** The deficit of about 0.0014 per h² of Litsey's alternating border (his Section 12.1, numerical observations outside his proofs) is quoted as reported there, not reproduced; our own certified bounds for the alternating geometry differ by 0.00195, an upper bound for the deficit of our estimates and not a measurement of the true one. Both works cited for the framework are unrefereed and largely AI-generated; the novelty search did not cover MathSciNet or Google Scholar.
* **Formalization.** The three estimates and the separation identity are not formalized; the Lean theorems are conditional on them.

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

AxiomForge, *The irrationality of ψ₁(k/5) − π²/2: a candidate proof with separated Löwner determinants*, preprint AF-0002, version 0.1.0, 2026-11-26,
https://github.com/axiomforge-math/mathematics/tree/main/results/AF-0002-trigamma-fifths-irrationality. See
[CITATION.cff](CITATION.cff).
