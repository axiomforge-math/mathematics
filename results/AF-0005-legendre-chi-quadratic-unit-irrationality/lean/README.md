# Lean development (in preparation): χ₂ and Ti₂ at quadratic units, the new traces

Lake package `axiomforge-af0005`, library and root module `AxiomForge.AF0005`.
Toolchain `leanprover/lean4:v4.34.0-rc1`; Mathlib pinned at
`f385f9fd18abed332ebcd3df239cb357e264aceb` (`lakefile.toml`, `lake-manifest.json`).

**Status.** A formal layer, not a formalization of the main theorem. Proved unconditionally: the
irrationality criterion; the definitions of χ₂ and Ti₂ with fidelity lemmas; the units
`z = 2/(n + √(n²+4σ))` with `0 < z < 1`, `z² + σ n z − σ = 0`, `1/z − σ z = n`, and
`T_σ(n) = χ₂(z)` or `Ti₂(z)`; the margins at `n = 14, 27` (rounded rates, by `norm_num`); the
final deduction from `PencilEstimates`. **Not formalized**: the Hankel polynomials `Δ_h`
(`PencilEstimates` is stated for an arbitrary polynomial family `Q`), the two new estimates of
the manuscript (odd primes dividing the trace; the prime 2 at odd trace), the four imported
results of Krisman (Hexagon 2611.00265v1: Thm 3.7, Prop 4.2, Thm 5.1, Lemma 6.1/8.6, with the
transfers of its Section 8), the shift lemma and the monotonicity argument for `n > 14, 27`, the
numerical certificates. The fields of `PencilEstimates` are exactly these unproved items;
every theorem that takes it has a name ending in `_of_estimates`.

## Build

```bash
lake exe cache get && lake build
```


## Module map

| Module | Content | Status |
|---|---|---|
| `AxiomForge/AF0005/IrrationalityCriterion.lean` | `irrational_of_scaled_int_poly`, `irrational_of_log_content_decay`, … | proved |
| `AxiomForge/AF0005/Definitions.lean` | `legendreChi`, `inverseTangentIntegral`, convergence, oddness, `χ₂(1) = π²/8` | proved |
| `AxiomForge/AF0005/Units.lean` | `unitZ`, `unitValue`, `Admissible`, `unitValue_one`, `unitValue_neg_one`, `unitZ_pos`, `unitZ_lt_one`, `unitZ_quadratic`, `inv_unitZ_sub` | proved |
| `AxiomForge/AF0005/Estimates.lean` | `PencilEstimates`, `irrational_of_pencilEstimates`, margins, the conditional theorems | see theorem map |

## Theorem map

Machine-readable: `theorem-map.toml`; audited declarations: `theorems.toml`; axiom report: `AXIOMS.txt`.
Names are in the namespace `AxiomForge.LegendreChi`.

| Statement | Lean name | Status |
|---|---|---|
| χ₂ at the unit of trace 14 irrational | `irrational_unitValue_14_pos_of_estimates` | conditional on `PencilEstimates` (rates −1.99310, −2.00461) |
| Ti₂ at the unit of trace 14 irrational | `irrational_unitValue_14_neg_of_estimates` | conditional (−1.99310, −1.99936) |
| χ₂ at the unit of trace 27 irrational | `irrational_unitValue_27_pos_of_estimates` | conditional (−2.33058, −2.33734) |
| Ti₂ at the unit of trace 27 irrational | `irrational_unitValue_27_neg_of_estimates` | conditional (−2.33058, −2.33595) |
| Generic deduction (any `n`, rates `d < a`) | `irrational_of_pencilEstimates` | proved as an implication |
| Negative arguments | `irrational_legendreChi_neg_unit_of_estimates`, `irrational_inverseTangentIntegral_neg_unit_of_estimates` | conditional |
| `T_σ(n)` is `χ₂(z)` / `Ti₂(z)` | `unitValue_one`, `unitValue_neg_one` | proved |
| `0 < z < 1`, quadratic and trace relations | `unitZ_pos`, `unitZ_lt_one`, `unitZ_quadratic`, `inv_unitZ_sub` | proved |
| Margins at 14, 27 | `margin_14_pos`, `margin_14_neg`, `margin_27_pos`, `margin_27_neg` | proved |
| New estimates (odd primes dividing n; prime 2 at odd n) | field `PencilEstimates.content` | not formalized |
| (K1), (K2), (K3), (K4) of Krisman | fields `content`, `decay`, `nonvanishing` | not formalized (imported) |
| Shift lemma, monotonicity for all larger traces | — | not formalized |

## Mathlib gaps

Neither χ₂ nor Ti₂ is defined in Mathlib; no prime number theorem and no logarithmic potential
theory, which the imported estimates use.

## Axiom audit

`AXIOMS.txt` is the output of `af lean audit` (`#print axioms` for every declaration of
`theorems.toml`).
