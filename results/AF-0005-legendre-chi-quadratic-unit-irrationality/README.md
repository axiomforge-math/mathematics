# AF-0005 · Irrationality of χ₂ and Ti₂ at units of real quadratic fields: further traces: a candidate proof

> **Preprint, conditional.** The main theorem is proved only **assuming four results of an
> unrefereed preprint of Krisman** (Hexagon 2611.00265v1: K1 Theorem 3.7, K2 Proposition 4.2,
> K3 Theorem 5.1 for even h ≥ 100, K4 Lemmas 6.1 and 8.6 for ℓ ≥ 7, ℓ ∤ n, ℓ² ∤ b), which are stated and not reproved here. A complete
> written argument for the rest, not yet independently verified; its computations are reproduced;
> its Lean formalization is in preparation. The archive does not establish the main theorem
> until the contribution reaches level V4 (see `docs/verification-policy.md` of the archive).

| | |
|---|---|
| Identifier | AF-0005, version 0.1.0 (2026-11-26) |
| Status | preprint |
| Author | AxiomForge · axiomforge.math@gmail.com |
| MSC2020 | Primary 11J72; Secondary 33B30 |
| Manuscript | `paper/main.pdf` |
| Lean package | `lean/` (`axiomforge-af0005`, Lean v4.34.0-rc1, Mathlib `f385f9fd18abed332ebcd3df239cb357e264aceb`) |

Here χ₂(x) = Σ_{j≥0} x^{2j+1}/(2j+1)² is Legendre's chi function and Ti₂(x) = Σ_{j≥0} (−1)^j x^{2j+1}/(2j+1)² the inverse tangent integral. For an integer n and a sign σ let z = 2/(n + √(n² + 4σ)), a unit of norm −σ of a real quadratic field, and T_σ(n) = χ₂(z) (σ = +1) or Ti₂(z) (σ = −1). Krisman proved, in an unrefereed preprint, that these numbers are irrational outside 47 and 57 explicit values of n, and named two improvements of his local estimates that he did not prove. This contribution proves both and deduces irrationality for further traces, **assuming four results of his preprint**.

## Main result (conditional)

| Label | Statement | Lean declaration |
|---|---|---|
| `thm:main` | **Assuming (K1)–(K4)** (K2 only for even n; K3 for even h ≥ 100; K4 for ℓ ≥ 7, ℓ ∤ n, ℓ² ∤ b): for σ = ±1 and n even ≥ 14 or odd ≥ 27, T_σ(n) is irrational (and so is its value at −z, since χ₂ and Ti₂ are odd). | none yet (formalization in preparation); conditional versions below |

The assumed results, with their exact scope, all from the unrefereed preprint (Hexagon 2611.00265v1), are **stated and not reproved here**:

* **K1**, Theorem 3.7: the bound (4/3) h² for the logarithmic denominators at the odd primes not dividing n;
* **K2**, Proposition 4.2: for even n, the bound at the prime 2;
* **K3**, Theorem 5.1: the size estimate by a dual energy, for even h ≥ 100 (applied here to four new certificates, after checking its hypotheses literally);
* **K4**, Lemmas 6.1 and 8.6: the nonvanishing lemma, for primes ℓ ≥ 7 with ℓ ∤ n and ℓ² ∤ b (T_σ(n) = a/b).

The conclusion therefore depends on that preprint, which is unrefereed and largely AI-generated; a later correction of it could invalidate the conclusion. What is proved here without that assumption: the two local estimates, the size comparison at n = 14 and 27 (certificates), the shift lemma and the monotonicity step for larger traces, and the construction. The result covers 31 of the 47 traces excluded for χ₂ and 42 of the 57 excluded for Ti₂; 16 and 15 traces remain open here.

## Status

* **Conditional on (K1)–(K4)**: the main theorem. These four results are *imported, not reproved*; the manuscript's status table lists them as such.
* **Proved here** (written in full, AI-internal reading only): the bound at an odd prime dividing n (Lemma A: no cost beyond the one forced by the valuation of n), the bound at the prime 2 for odd n (Lemma B: half of the proved cost), the shift lemma and the monotonicity step, the construction, the irrationality criterion.
* **Certified by computation and reproduced** (AI-internal): the four new size certificates at n = 14, 27 for both signs (margins C(n) + Φ ≤ −0.0115, −0.0063 at n = 14 and −0.0068, −0.0054 at n = 27, per h²), the diagnostics at n = 10, 25, the exceptional sets of the cited preprint, and 16 418 exact arithmetic checks.
* **Candidate** (written proof, not independently verified): Lemmas A and B, the odd-trace and Ti₂ transfers of the cited preprint's Section 8 (prose statements there), and the assembly.
* **Lean:** the package builds and `#print axioms` reports only `propext`, `Classical.choice` and `Quot.sound` for each of its 33 audited declarations (`lean/AXIOMS.txt`). It proves unconditionally the irrationality criterion, the definitions of χ₂ and Ti₂, the units z, and the margins at n = 14, 27. The Hankel polynomials are not defined in the package, and neither the two new estimates, the shift lemma nor (K1)–(K4) are formalized. The main theorem is proved only conditionally:

| Lean declaration | Hypotheses | Check |
|---|---|---|
| `AxiomForge.LegendreChi.irrational_unitValue_14_pos_of_estimates` | conditional on `PencilEstimates` (the four imported results (K1)-(K4), the two new estimates and the shift lemma, at the rounded rates of the manuscript) | build passing; axioms standard |
| `AxiomForge.LegendreChi.irrational_unitValue_14_neg_of_estimates` | conditional on `PencilEstimates` (the four imported results (K1)-(K4), the two new estimates and the shift lemma, at the rounded rates of the manuscript) | build passing; axioms standard |
| `AxiomForge.LegendreChi.irrational_unitValue_27_pos_of_estimates` | conditional on `PencilEstimates` (the four imported results (K1)-(K4), the two new estimates and the shift lemma, at the rounded rates of the manuscript) | build passing; axioms standard |
| `AxiomForge.LegendreChi.irrational_unitValue_27_neg_of_estimates` | conditional on `PencilEstimates` (the four imported results (K1)-(K4), the two new estimates and the shift lemma, at the rounded rates of the manuscript) | build passing; axioms standard |
| `AxiomForge.LegendreChi.irrational_legendreChi_neg_unit_of_estimates` | conditional on `PencilEstimates` (the four imported results (K1)-(K4), the two new estimates and the shift lemma, at the rounded rates of the manuscript) | build passing; axioms standard |
| `AxiomForge.LegendreChi.irrational_inverseTangentIntegral_neg_unit_of_estimates` | conditional on `PencilEstimates` (the four imported results (K1)-(K4), the two new estimates and the shift lemma, at the rounded rates of the manuscript) | build passing; axioms standard |

  These conditional theorems are not a formalization of the main theorem.

| Dimension | `thm:main` |
|---|---|
| Conventional proof | candidate (conditional on K1–K4) |
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

`run_checks.py` writes every output to `logs/experiments/outputs/` and exits with status 1 if a
check fails; `logs/experiments/README.md` lists each program and what it establishes. From the
archive root, `python3 scripts/afm.py verify AF-0005` runs the archive checks.

## Known limitations and open points

* **Conditional on four imported results (K1–K4)** of an unrefereed, largely AI-generated preprint (Hexagon 2611.00265v1). None is reproved here; the Lean development that preprint reports was neither built nor audited by us; a later correction of the preprint could invalidate the conclusion. The odd-trace and Ti₂ transfers are stated there in prose.
* **No independent review.** No human expert has reviewed the argument; Lemmas A and B were written and read by AI systems of the same organisation; all checks are AI-internal.
* **Use of K3 with new certificates.** The certificates were not produced in the cited preprint; its Theorem 5.1 is applied to them after checking its hypotheses literally.
* **Thin margins.** The smallest margin is 0.0054 per h² (n = 27, σ = −1); the estimates carry O(h log h) terms and no effective h₀ is claimed.
* **Remaining traces.** n ≤ 25 odd and n ∈ {2, 6, 10} (resp. {4, 6, 10}) are not covered; at n = 10 and 25 a lower bound shows that this comparison cannot close them (a statement about the method, not about the numbers).
* **Priority.** Checked relative to the one available version of the cited preprint and its repository (both improvements are stated as unproved there); not an absolute priority claim.
* **Formalization.** The estimates and (K1)–(K4) are not formalized; the Lean theorems are conditional.

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
reconstruction, verification computations, manuscript and Lean development with Claude Sonnet 5.5, Claude Fable 5.2 and
Claude Opus 5.5 (Anthropic); the review (numeric audit, adversarial reading, dependency check) was made with Claude Fable 5.2;
no independent human review has taken place. Full disclosure: `logs/ai-contributions.md` and
the section *AI-assisted research disclosure* of the manuscript.

## Citation

AxiomForge, *Irrationality of χ₂ and Ti₂ at units of real quadratic fields: further traces* (conditional on four results of an unrefereed preprint), preprint AF-0005, version 0.1.0, 2026-11-26,
https://github.com/axiomforge-math/mathematics/tree/main/results/AF-0005-legendre-chi-quadratic-unit-irrationality. See
[CITATION.cff](CITATION.cff).
