# Lean development (in preparation): irrationality of χ₂(±2/q) and Ti₂(±2/q), odd q ≥ 81

Lake package `axiomforge-af0003`, library and root module `AxiomForge.AF0003`.
Toolchain `leanprover/lean4:v4.34.0-rc1` (`lean-toolchain`); Mathlib pinned at
`f385f9fd18abed332ebcd3df239cb357e264aceb` (`lakefile.toml`, `lake-manifest.json`).

**Status.** This is the formal layer of the candidate proofs, not a formalization of the main
theorems. Proved unconditionally: the irrationality criterion; the definitions of χ₂ and Ti₂
with fidelity lemmas (convergence, oddness, χ₂(1) = π²/8, alternating structure of Ti₂); the
reduction of negative arguments to positive ones; the explicit half-integer Hankel pencils
`T_n` and their degree bound; the margin inequalities for every odd q ≥ 81; the prime-2
profile minimum −1847/1100 at q = 81; and the final deduction. The irrationality statements
are proved **only conditionally** on `FamilyEstimates σ q` (that is, `HalfIntegerEstimates`
with the rates of the manuscripts), whose fields are the unproved estimates (arithmetic
content bound, archimedean decay, prime-index nonvanishing). Every theorem that takes these
hypotheses has a name ending in `_of_estimates` (or `_of_<hypothesis>`) and is not a
formalization of a main theorem.

## Build

```bash
lake exe cache get && lake build
```

## Module map

| Module | Content | Status |
|---|---|---|
| `AxiomForge/AF0003/IrrationalityCriterion.lean` | the irrationality criteria (`irrational_of_scaled_int_poly`, `irrational_of_log_content_decay`, …) | proved |
| `AxiomForge/AF0003/Definitions.lean` | `legendreChi x = ∑ x^(2j+1)/(2j+1)²`, `inverseTangentIntegral x = ∑ (−1)^j x^(2j+1)/(2j+1)²`; summability on `|x| ≤ 1`; oddness of both; irrationality at `−x` ⇔ at `x`; χ₂(1) = π²/8; χ₂ > 0 on `(0, 1]`; alternating, decreasing terms of Ti₂ on `[0, 1]` | proved |
| `AxiomForge/AF0003/Construction.lean` | `targetValue σ y` (= χ₂(2/q) for σ = 1, Ti₂(2/q) for σ = −1, y = q/2, proved); `τ_k`, moments, `D_K`, `N_A`, the affine functional `μ_X`, `halfHankelDet σ y (H, K′, A′) n = T_n(X)`; `deg T_n ≤ H n` | definitions; fidelity and degree bound proved |
| `AxiomForge/AF0003/MainTheorems.lean` | `HalfIntegerEstimates`, `FamilyEstimates`; margins `decayRate_lt_contentRate` (all q ≥ 83) and `decay_lt_content_eighty_one`; prime-2 profile minimum; the conditional deduction and the `*_of_estimates` statements | see theorem map |

## Theorem map

Machine-readable versions: `theorem-map.toml`; audited declarations: `theorems.toml`;
axiom report: `AXIOMS.txt`. All names below are in the namespace `AxiomForge.LegendreChi`.

| Statement | Lean name | Status |
|---|---|---|
| χ₂(2/q) is irrational for every odd q ≥ 81 | `irrational_legendreChi_two_div_of_estimates` | conditional on `FamilyEstimates 1 q` |
| Ti₂(2/q) is irrational for every odd q ≥ 81 | `irrational_inverseTangentIntegral_two_div_of_estimates` | conditional on `FamilyEstimates (−1) q` |
| χ₂(−2/q) is irrational for every odd q ≥ 81 | `irrational_legendreChi_neg_two_div_of_estimates` | conditional on `FamilyEstimates 1 q` |
| Ti₂(−2/q) is irrational for every odd q ≥ 81 | `irrational_inverseTangentIntegral_neg_two_div_of_estimates` | conditional on `FamilyEstimates (−1) q` |
| Final contradiction for one value | `irrational_targetValue_of_halfIntegerEstimates`, `irrational_targetValue_of_familyEstimates` | proved (as implications) |
| Negative arguments follow by oddness | `legendreChi_neg`, `inverseTangentIntegral_neg`, `irrational_legendreChi_neg_iff`, `irrational_inverseTangentIntegral_neg_iff` | proved |
| ξ = ∑ σ^j y^(−2j−1)/(2j+1)² is χ₂(2/q), resp. Ti₂(2/q) | `targetValue_one`, `targetValue_neg_one` | proved |
| `deg T_n ≤ h` | `natDegree_halfHankelDet_le` | proved |
| Margin of the q ≥ 83 family: B_83 − ½ log(q/83) < A_−(83) − (1/72) log(q/83) (rounded rates) | `decayRate_lt_contentRate` | proved |
| Margin at q = 81 (rounded rates −3.3741 < −3.3685) | `decay_lt_content_eighty_one` | proved |
| Prime-2 profile at q = 81: min f = −1847/1100 at x = 51/55 | `primeTwoProfile_ge`, `primeTwoProfile_min` | proved |
| Arithmetic estimate liminf h⁻² log cont(T_n) ≥ A_σ(q) | field `HalfIntegerEstimates.content` | not formalized (hypothesis) |
| Archimedean estimate limsup h⁻² log |T_n(ξ)| ≤ B_q | field `HalfIntegerEstimates.decay` | not formalized (hypothesis) |
| Prime-index nonvanishing (symbolic local determinants for q ≥ 83, modular witnesses at q = 81) | field `HalfIntegerEstimates.nonvanishing` | not formalized (hypothesis) |
| Series identity μ_ξ(R) = ∑_{m ≥ 1} w^m R′(m) | — | not formalized (not needed by the conditional deduction) |

Rates used (per h²): for q ≥ 83, `contentRate q = −3.1549 − log(q/83)/72` and
`decayRate q = −3.1617 − log(q/83)/2`, which follow from the certified bounds
A_−(83) > −3.15484583292, B_83 < −3.16170895858 and the uniform extension in q; for q = 81,
−3.3685 and −3.3741 (certified values A_−(81) ≈ −3.368497051, B_81 ≈ −3.374176113). All
are strict with respect to the certified bounds, so the "eventually" form of the fields is
implied by them.

## Mathlib gaps

* Neither χ₂ nor Ti₂ (nor any polylogarithm) is defined in Mathlib.
* No prime number theorem (only Chebyshev's bounds) and no logarithmic potential theory, which
  the arithmetic and archimedean estimates use.

## Axiom audit

`AXIOMS.txt` is the verbatim output of `#print axioms` for the 29 declarations of
`theorems.toml`, obtained with `lake env lean` on a probe file importing `AxiomForge.AF0003`.
Every declaration depends only on `propext`, `Classical.choice` and `Quot.sound`. The
sources contain no `sorry`, `admit`, `axiom`, `native_decide`, `implemented_by` or `extern`.
