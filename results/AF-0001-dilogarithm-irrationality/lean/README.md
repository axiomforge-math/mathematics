# Lean development (in preparation): irrationality of Li₂(2/11), Li₂(2/9), Li₂(−2/9), Li₂(−2/7)

Lake package `axiomforge-af0001`, library and root module `AxiomForge.AF0001`.
Toolchain `leanprover/lean4:v4.34.0-rc1` (`lean-toolchain`); Mathlib pinned at
`f385f9fd18abed332ebcd3df239cb357e264aceb` (`lakefile.toml`, `lake-manifest.json`).

**Status.** This is the formal layer of the candidate proofs, not a formalization of the main
theorems. Proved unconditionally: the irrationality criterion, the definitions and their
fidelity lemmas, the explicit determinant polynomials `Q̃_n` and their degree bound, the eight
local Gram determinants of the prime-index argument (kernel-checked), and the final
deduction. The four irrationality statements are proved **only conditionally** on the
structure `HankelEstimates`, whose fields are the unproved asymptotic estimates of the
manuscripts (arithmetic content bound, archimedean decay, prime-index nonvanishing). Every
theorem that takes these hypotheses has a name ending in `_of_estimates` (or
`_of_hankelEstimates`) and is not a formalization of a main theorem.

## Build

```bash
lake exe cache get && lake build
```

## Module map

| Module | Content | Status |
|---|---|---|
| `AxiomForge/AF0001/IrrationalityCriterion.lean` | clearing denominators; `irrational_of_int_poly_approx`, `irrational_of_tendsto_int_poly`, `irrational_of_scaled_int_poly`, `irrational_of_log_content_decay` (content + decay + nonvanishing for rational polynomials), `irrational_of_rat_value_decay`, `frequently_atTop_of_eventually_prime` | proved |
| `AxiomForge/AF0001/Definitions.lean` | `dilog x = ∑ x^(k+1)/(k+1)²`; summability on `|x| ≤ 1`; `hasSum_pow_div_sq` (the series from `k = 1`); `Li₂(1) = π²/6`; `Li₂(x) + Li₂(−x) = Li₂(x²)/2`; `Li₂(−1) = −π²/12`; sign of `Li₂` on `(0, 1]` and `[−1, 0)` | proved |
| `AxiomForge/AF0001/Construction.lean` | explicit `D_m`, moments `M_k(λ)` (as series), `τ_l(λ)`, the affine functional `Λ_X` (division by the monic `D_K` and residues), the Hankel matrix, `normalizedHankelDet λ (H, C, B) n = Q̃_n`; `deg Q̃_n ≤ H n` | definitions; degree bound proved |
| `AxiomForge/AF0001/LocalGram/{TwoElevenths,TwoNinths,MinusTwoNinths,MinusTwoSevenths}.lean` | the rational Hankel matrices `H_1`, `H_0`; exact determinant and nonvanishing via a kernel-checked factorization `H = L U` (`norm_num`; no `decide`, no `native_decide`) | proved (finite certificates) |
| `AxiomForge/AF0001/ContentRates.lean` | the final logarithmic comparisons of the arithmetic certificates: `content_rate_two_elevenths_gt` (9/2 − 16 log 2 − (25/4) log 9 + (20/3) log 11 > −4.338) and `content_rate_neg_two_sevenths_gt` (0.07694503668343355 − (11/10) log 2 − (1/2) log 3 + (11/30) log 7 > −0.521323) | proved |
| `AxiomForge/AF0001/MainTheorems.lean` | `HankelEstimates`; `irrational_dilog_of_hankelEstimates`; the four `*_of_estimates` statements with the numerical margins checked by `norm_num` | conditional |

## Theorem map

Machine-readable versions: `theorem-map.toml`; audited declarations: `theorems.toml`;
axiom report: `AXIOMS.txt`. All names below are in the namespace `AxiomForge.Dilogarithm`.

| Statement | Lean name | Status |
|---|---|---|
| Li₂(2/11) is irrational | `irrational_dilog_two_elevenths_of_estimates` | conditional on `HankelEstimates (2/11) ⟨4, 6, 1⟩ (−4.338/16) (−4.9/16)` |
| Li₂(2/9) is irrational | `irrational_dilog_two_ninths_of_estimates` | conditional on `HankelEstimates (2/9) ⟨8, 9, 0⟩ (−1.33) (−1.34)` |
| Li₂(−2/9) is irrational | `irrational_dilog_neg_two_ninths_of_estimates` | conditional on `HankelEstimates (−2/9) ⟨4, 7, 1⟩ (−0.40) (−0.49)` |
| Li₂(−2/7) is irrational | `irrational_dilog_neg_two_sevenths_of_estimates` | conditional on `HankelEstimates (−2/7) ⟨5, 8, 1⟩ (−0.521323) (−0.526078)` |
| Final contradiction: content + decay + nonvanishing imply irrationality | `irrational_dilog_of_hankelEstimates`, `irrational_of_log_content_decay`, `irrational_of_scaled_int_poly` | proved |
| `deg Q̃_n ≤ h` | `natDegree_normalizedHankelDet_le` | proved |
| Local determinants `det H_1`, `det H_0` (four cases) | `LocalGram.*.det_gramOne`, `det_gramZero`, `det_gramOne_ne_zero`, `det_gramZero_ne_zero` | proved |
| Final logarithmic comparison of the arithmetic certificate (2/11 and −2/7) | `content_rate_two_elevenths_gt`, `content_rate_neg_two_sevenths_gt` | proved (the rational lower bounds 9/2 and 0.07694503668343355 for the profile integrals are inputs, not formalized) |
| Arithmetic estimate `liminf log cont(Q̃_n) / h² > a` | field `HankelEstimates.content` | not formalized (hypothesis) |
| Archimedean estimate `limsup log |Q̃_n(ξ)| / h² < d` | field `HankelEstimates.decay` | not formalized (hypothesis) |
| Prime-index nonvanishing `Q̃_p(r) ≠ 0` | field `HankelEstimates.nonvanishing` | not formalized (hypothesis); its finite input, the local determinants, is proved |
| Binomial normalization of `Q̃_n` | — | not formalized |
| Series identity `Λ_ξ(R) = ∑_{x ≥ 1} λ^x (x R(x))′` | — | not formalized (not needed by the conditional deduction, which states the decay for the polynomial `Q̃_n` itself) |
| Landen pairs: one of Li₂(2/11), Li₂(−2/9) and one of Li₂(2/9), Li₂(−2/7) is irrational | — | not formalized (see Mathlib gaps) |
| `Li₂(x) = ∑_{k ≥ 1} x^k/k²`, `Li₂(1) = π²/6`, `Li₂(−1) = −π²/12` | `hasSum_pow_div_sq`, `dilog_one`, `dilog_neg_one` | proved |

The rates (per `h²`, `h = H n`) are the strict `liminf`/`limsup` bounds printed in the
manuscripts, rounded so as to weaken the hypothesis; strictness implies the "eventually" form
of the fields. For ±2/9 the certified strict bounds −1.33/−1.34 and −0.40/−0.49 are used.

## Local determinant certificate

The rational matrices were produced by an exact recomputation (python-flint) written from
the defining rules of the local functional `V`: Euler-operator moments, flint partial
fractions and fraction-free determinants, with every Hankel entry cross-checked against a
120-digit evaluation of `∑_u λ^u R′(u) + Li₂(λ) ∑_l r_l λ^(−l)`. All eight determinants
agree with the manuscripts:

| λ | `det H_1` | `det H_0` |
|---|---|---|
| 2/11 (4×4) | 17828022563089333969/1224440064 | 12598972834814973210048467/2295825120 |
| 2/9 (8×8) | 3951366107675153857566158184061855291890957151/50404062960731160576000000000000 | 75748065809620696385810762379349631101207641762772048941/23344937339644196864000000000000 |
| −2/9 (4×4) | 1677163510311484581/15488000 | 16417954848664067036722569/524733440 |
| −2/7 (5×5) | 14067971871496713969085291850153/1057916215296000000 | 17800469908791563702231968746821382359/495898225920000000 |

The Lean files prove the determinants of these explicit rational matrices; that the matrices
are the reduced diagonal blocks of the scaled Gram matrix belongs to the unformalized
prime-index argument.

## Mathlib gaps

* No polylogarithm, and no Hermite–Lindemann theorem (only the analytic part of Lindemann's
  proof, `NumberTheory/Transcendental/Lindemann/AnalyticalPart`). The Landen-pair consequence
  needs `log²(9/11) ∉ ℚ` and `log²(7/9) ∉ ℚ`.
* Chebyshev's bounds are available (`NumberTheory/Chebyshev`) but not the prime number
  theorem used to integrate the arithmetic profiles, and there is no logarithmic potential
  theory for the archimedean estimates.

## Axiom audit

`AXIOMS.txt` is the verbatim output of `#print axioms` for the 37 declarations of
`theorems.toml`, obtained with `lake env lean` on a probe file importing `AxiomForge.AF0001`.
Every declaration depends only on `propext`, `Classical.choice` and `Quot.sound`. The
sources contain no `sorry`, `admit`, `axiom`, `native_decide`, `implemented_by` or `extern`.
