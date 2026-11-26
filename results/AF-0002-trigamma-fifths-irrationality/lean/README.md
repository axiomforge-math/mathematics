# Lean development (in preparation): irrationality of ξ_k = ψ₁(k/5) − π²/2, k = 1, 2, 3, 4

Lake package `axiomforge-af0002`, library and root module `AxiomForge.AF0002`.
Toolchain `leanprover/lean4:v4.34.0-rc1` (`lean-toolchain`); Mathlib pinned at
`f385f9fd18abed332ebcd3df239cb357e264aceb` (`lakefile.toml`, `lake-manifest.json`).

**Status.** This is the formal layer of the candidate proof, not a formalization of the main
theorem. Proved unconditionally: the irrationality criterion; the definitions with fidelity
lemmas (ψ₁(1/2) = π²/2, agreement with Mathlib's Hurwitz zeta function); the multiplication
formula at fifths; the irrationality of π² (not in Mathlib); the partial result **at least
one of ξ₁, ξ₂, ξ₃, ξ₄ is irrational**; the explicit separated Löwner pencils; the rational
comparisons of the certificate; and the final deduction. The four irrationality statements
are proved **only conditionally** on `LownerEstimates`, whose fields are the unproved
estimates of the proof (nonvanishing with one deletion, arithmetic denominator bound,
archimedean decay). Every theorem that takes these hypotheses has a name ending in
`_of_estimates` (or `_of_lownerEstimates`) and is not a formalization of a main theorem.

## Build

```bash
lake exe cache get && lake build
```

## Module map

| Module | Content | Status |
|---|---|---|
| `AxiomForge/AF0002/IrrationalityCriterion.lean` | the irrationality criteria, in particular `irrational_of_rat_value_decay` (values at a rational point with controlled denominators, uniformly over admissible deletions) | proved |
| `AxiomForge/AF0002/Definitions.lean` | `trigamma s = ∑_{j ≥ 0} 1/(j+s)²`, `xi k = trigamma (k/5) − π²/2`; summability; `trigamma_eq_hurwitzZeta` (on `(0, 1]`, ψ₁(s) = ζ(2, s) of Mathlib); recurrence; ψ₁(1) = π²/6; ψ₁(1/2) = π²/2; `hasSum_xi`; `trigamma_one_fifth_add` (ψ₁(1/5) + ψ₁(2/5) + ψ₁(3/5) + ψ₁(4/5) = 4π²); `xi_one_add` (ξ₁ + ξ₂ + ξ₃ + ξ₄ = 2π²) | proved |
| `AxiomForge/AF0002/PiSquared.lean` | `irrational_pi_sq : Irrational (π ^ 2)` (Cartwright's integrals with the parity of the polynomials tracked; the analytic lemmas are copied from Mathlib's proof of `irrational_pi`, Apache 2.0) | proved |
| `AxiomForge/AF0002/Construction.lean` | explicit node data `f_i`, `d_i`, separated node sets, admissible deletions, `separatedLownerDet s m I = P_sep,I(X)` with `h = 16 m`; degree bound | definitions; degree bound proved |
| `AxiomForge/AF0002/MainTheorems.lean` | `irrational_xi_one_or_xi_two_or_xi_three_or_xi_four`; `arithmeticRate_lt`, `arithmetic_lt_decay`; `LownerEstimates`; the conditional deduction and the four `*_of_estimates` statements | see theorem map |

## Theorem map

Machine-readable versions: `theorem-map.toml`; audited declarations: `theorems.toml`;
axiom report: `AXIOMS.txt`. All names below are in the namespace `AxiomForge.Trigamma`.

| Statement | Lean name | Status |
|---|---|---|
| ξ₁ = ψ₁(1/5) − π²/2 is irrational | `irrational_xi_one_of_estimates` | conditional on `LownerEstimates (1/5)` |
| ξ₂ = ψ₁(2/5) − π²/2 is irrational | `irrational_xi_two_of_estimates` | conditional on `LownerEstimates (2/5)` |
| ξ₃ = ψ₁(3/5) − π²/2 is irrational | `irrational_xi_three_of_estimates` | conditional on `LownerEstimates (3/5)` |
| ξ₄ = ψ₁(4/5) − π²/2 is irrational | `irrational_xi_four_of_estimates` | conditional on `LownerEstimates (4/5)` |
| Irrationality deduction from the three estimates | `irrational_trigamma_sub_of_lownerEstimates`, `irrational_of_rat_value_decay` | proved |
| At least one of ξ₁, ξ₂, ξ₃, ξ₄ is irrational | `irrational_xi_one_or_xi_two_or_xi_three_or_xi_four` | **proved (unconditional)** |
| π² is irrational | `irrational_pi_sq` | proved |
| ψ₁(1/2) = π²/2, hence ξ_k = ψ₁(k/5) − ψ₁(1/2) = ∑_j ((j + k/5)⁻² − (j + 1/2)⁻²) | `trigamma_one_half`, `xi_eq_trigamma_sub_trigamma`, `hasSum_xi` | proved |
| A = 304227995343501721142691896310988016794079029050925423/86622067750624596685118168422516024981216422248448000 < 3.512131 | `arithmeticRate_lt` | proved (only the rational comparison; A as the value of the arithmetic profile integral is not formalized) |
| Margin 3.512131 < 3.512607 | `arithmetic_lt_decay` | proved |
| Separation identity P_sep,I = 2^(−m(m−1)) P_alt,I | — | not formalized (for m = 1 the two pencils coincide by definition; already for m = 2 it is an identity between 34 × 34 determinants with polynomial entries) |
| Nonvanishing with one deletion | field `LownerEstimates.nonvanishing` | not formalized (hypothesis) |
| Arithmetic estimate limsup h⁻² log den P_sep,I(X) < 3.512131 | field `LownerEstimates.denominator` | not formalized (hypothesis) |
| Archimedean estimate limsup h⁻² log |P_sep,I(ξ)| ≤ −3.512607 | field `LownerEstimates.decay` | not formalized (hypothesis) |
| Reflection ξ_k + ξ_{5−k} = π² cot²(πk/5); one of ξ₁, ξ₄ is irrational | — | not formalized (see Mathlib gaps) |

The hypothesis constants are 3.512131 (denominators) and 3.512607 (decay). The certified
values are A = 3.5121303755913638… and a decay rate of at least 3.5128848; both certified
`limsup` bounds are strictly better than the constants used, so the "eventually" form of the
fields is implied by them.

## Mathlib gaps

* No transcendence of π (only `irrational_pi`; Lindemann's theorem is present only through
  its analytic part). Since ξ₁ + ξ₄ = π²(1 + 2/√5) and ξ₂ + ξ₃ = π²(1 − 2/√5), deducing that
  one of ξ₁, ξ₄ (resp. ξ₂, ξ₃) is irrational needs π² ∉ ℚ(√5). The unconditional statement
  above needs only π² ∉ ℚ, proved here, and the multiplication formula.
* No reflection formula for ψ₁: Mathlib's series for the derivatives of `π cot (π z)` is
  stated on the upper half plane only (`iteratedDerivWithin_cot_pi_mul_eq_mul_tsum_div_pow`).
* No prime number theorem in arithmetic progressions; no logarithmic potential theory.

## Axiom audit

`AXIOMS.txt` is the verbatim output of `#print axioms` for the 25 declarations of
`theorems.toml`, obtained with `lake env lean` on a probe file importing `AxiomForge.AF0002`.
Every declaration depends only on `propext`, `Classical.choice` and `Quot.sound`. The
sources contain no `sorry`, `admit`, `axiom`, `native_decide`, `implemented_by` or `extern`.
