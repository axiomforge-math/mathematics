# Lean development (in preparation): irrationality of χ₂(±a/q) and Ti₂(±a/q), a ∈ {3, 4, 5, 8}

Lake package `axiomforge-af0004`, library and root module `AxiomForge.AF0004`, namespace
`AxiomForge.LegendreChiGeneral`. Toolchain `leanprover/lean4:v4.34.0-rc1` (`lean-toolchain`);
Mathlib pinned at `f385f9fd18abed332ebcd3df239cb357e264aceb` (`lakefile.toml`,
`lake-manifest.json`). Adapted from the package of the numerator-2 preprint.

**Status.** This is the formal layer of the candidate proofs, not a formalization of the main
theorems. Proved unconditionally: the irrationality criterion; the definitions of χ₂ and Ti₂ with
fidelity lemmas; the reduction of negative arguments to positive ones; the explicit half-integer
Hankel pencils `T_n` for general numerator and their degree bound; the six strict margins with
the rounded rates and the margin for every `q ≥ q₀` (all by `norm_num`/`nlinarith`, no
`native_decide`); the exact arithmetic constants `c₂` (`49/72`, `25/32`, `1/4`, `−337/112`,
`−9/2`); and the final deduction. The irrationality statements are proved **only conditionally**
on `FamilyEstimates a σ q` (that is, `HalfIntegerEstimates` with the rates of the manuscript),
whose fields are the unproved estimates (arithmetic content bound, archimedean decay, prime-index
nonvanishing). Every theorem that takes these hypotheses has a name ending in `_of_estimates`
(or `_of_<hypothesis>`) and is not a formalization of a main theorem. The rates in `rowData` are
rounded values of the certified bounds of the manuscript; they are not re-derived in Lean.

## Build

```bash
lake exe cache get && lake build
```


## Module map

| Module | Content | Status |
|---|---|---|
| `AxiomForge/AF0004/IrrationalityCriterion.lean` | the irrationality criteria (`irrational_of_scaled_int_poly`, `irrational_of_log_content_decay`, …) | proved |
| `AxiomForge/AF0004/Definitions.lean` | `legendreChi`, `inverseTangentIntegral`; summability on `|x| ≤ 1`; oddness; irrationality at `−x` ⇔ at `x`; χ₂(1) = π²/8; χ₂ > 0 on `(0, 1]` | proved |
| `AxiomForge/AF0004/Construction.lean` | `targetValue σ y` (= χ₂(a/q), Ti₂(a/q) for `y = q/a`, proved); `τ_k`, moments, `D_K`, the affine functional `μ_X`, `halfHankelDet σ y p n = T_n(X)`; `deg T_n ≤ h` | definitions; fidelity and degree bound proved |
| `AxiomForge/AF0004/MainTheorems.lean` | `HalfIntegerEstimates`, `rowData`, `FamilyEstimates`; margins; constants `c₂`; the conditional deduction and the `*_of_estimates` statements | see theorem map |

## Theorem map

Machine-readable versions: `theorem-map.toml`; audited declarations: `theorems.toml`; axiom
report: `AXIOMS.txt`. All names are in the namespace `AxiomForge.LegendreChiGeneral`.

| Statement | Lean name | Status |
|---|---|---|
| χ₂(a/q) irrational, a ∈ {3,4,5,8}, q ≥ q₀ (131, 995, 829, 12061) | `irrational_legendreChi_div_of_estimates` | conditional on `FamilyEstimates a 1 q` |
| Ti₂(a/q) irrational, q ≥ q₀ (257, 995, 1609, 12061) | `irrational_inverseTangentIntegral_div_of_estimates` | conditional on `FamilyEstimates a (−1) q` |
| χ₂(−a/q), Ti₂(−a/q) irrational | `irrational_legendreChi_neg_div_of_estimates`, `irrational_inverseTangentIntegral_neg_div_of_estimates` | conditional |
| Final contradiction for one value | `irrational_targetValue_of_halfIntegerEstimates`, `irrational_targetValue_of_familyEstimates` | proved (as implications) |
| Negative arguments follow by oddness | `legendreChi_neg`, `inverseTangentIntegral_neg`, `irrational_legendreChi_neg_iff`, `irrational_inverseTangentIntegral_neg_iff` | proved |
| ξ = ∑ σ^j y^(−2j−1)/(2j+1)² is χ₂(a/q), resp. Ti₂(a/q) | `targetValue_one`, `targetValue_neg_one` | proved |
| `deg T_n ≤ h` | `natDegree_halfHankelDet_le` | proved |
| Thresholds of the six rows | `rowData_threshold` | proved |
| Six strict margins (rounded rates) | `rowData_margin` | proved |
| Margin for every q ≥ q₀ (slopes −7/54, −1/24 and −1/2) | `decayRate_lt_contentRate`, `slope_nonneg_margin` | proved |
| c₂ = 49/72, 25/32, 1/4 (a odd) | `oddConst_plus_seven_sixths`, `oddConst_plus_five_fourths`, `oddConst_minus_five_fourths` | proved |
| C₂(5/4) = −337/112, C₃(5/4) = −9/2 | `evenConst_two_ge`, `evenConst_three_ge` (and `_min`) | proved |
| Arithmetic estimate liminf h⁻² log cont(T_n) ≥ A_σ(a, q) | field `HalfIntegerEstimates.content` | not formalized (hypothesis) |
| Archimedean estimate limsup h⁻² log \|T_n(ξ)\| ≤ B_q | field `HalfIntegerEstimates.decay` | not formalized (hypothesis) |
| Prime-index nonvanishing | field `HalfIntegerEstimates.nonvanishing` | not formalized (hypothesis) |
| Series identity μ_ξ(R) = ∑_{m ≥ 1} w^m R′(m) | — | not formalized (not needed by the conditional deduction) |

Rounded rates per `h²` at the thresholds (`rowData`): content `−3.17388`, `−3.54128`, `−4.08176`,
`−3.87826`, `−4.21197`, `−4.98534` and decay `−3.18782`, `−3.54638`, `−4.08345`, `−3.87955`,
`−4.21267`, `−4.98609` for the rows (3,+), (3,−), (4), (5,+), (5,−), (8); for `q > q₀` the content
rate gains `s·log(q/q₀)` with `s = −7/54` (κ = 7/6) or `−1/24` (κ = 5/4) and the decay rate
`−½ log(q/q₀)`. For a = 4, 8 both signs use the constants of σ = −1.

## Mathlib gaps

* Neither χ₂ nor Ti₂ (nor any polylogarithm) is defined in Mathlib.
* No prime number theorem (only Chebyshev's bounds) and no logarithmic potential theory, which
  the arithmetic and archimedean estimates use.

## Axiom audit

`AXIOMS.txt` is the verbatim output of `#print axioms` for the 36 declarations of
`theorems.toml` (`python3 scripts/afm.py lean`). Every declaration
depends only on `propext`, `Classical.choice` and `Quot.sound`. The sources contain no `sorry`,
`admit`, `axiom`, `native_decide`, `implemented_by` or `extern`.
