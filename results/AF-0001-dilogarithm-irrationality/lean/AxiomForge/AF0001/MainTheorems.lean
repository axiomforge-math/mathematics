import AxiomForge.AF0001.IrrationalityCriterion
import AxiomForge.AF0001.Construction

/-!
# Conditional irrationality of `Li₂(2/11)`, `Li₂(2/9)`, `Li₂(-2/9)`, `Li₂(-2/7)`

The manuscripts reduce the irrationality of `ξ = Li₂(λ)` to three estimates on the explicit
normalized Hankel determinants `Q̃_n = normalizedHankelDet λ (H, C, B) n` of `Construction`:

1. an **arithmetic estimate** (lower bound for the content):
   `liminf h⁻² log cont(Q̃_n) > a`, with `h = H n`;
2. an **archimedean estimate** (decay at `ξ`):
   `limsup h⁻² log |Q̃_n(ξ)| < d`, with `d < a`;
3. **prime-index nonvanishing**: for each fixed rational `r`, `Q̃_p(r) ≠ 0` for all
   sufficiently large primes `p`.

The structure `HankelEstimates λ (H, C, B) a d` records exactly these three statements (in the
slightly weaker "eventually" form implied by the `liminf`/`limsup` statements, and with the
convention `log 0 = -∞` of the manuscripts built in by stating the decay without logarithm).

**The fields of `HankelEstimates` are unproved candidate estimates.** They are the asymptotic
content of the manuscripts (prime number theorem profiles, energy and contour bounds,
nonvanishing reduction), which is not formalized. The theorems below are therefore
conditional: they prove only the final deduction "estimates ⇒ irrationality", with the
numerical margin `d < a` of each manuscript checked by `norm_num`. Their names carry the
suffix `_of_estimates`.

The rates are normalized by `h ^ 2 = (H n) ^ 2`. The constants are the certified bounds
printed in the manuscripts, rounded in the direction that makes the hypothesis weaker:

| `λ` | `(H, C, B)` | content rate `a` | decay rate `d` |
|---|---|---|---|
| `2/11` | `(4, 6, 1)` | `-4.338 / 16` (that is `-4.338` per `n²`) | `-4.900 / 16` |
| `2/9` | `(8, 9, 0)` | `-1.33` | `-1.34` |
| `-2/9` | `(4, 7, 1)` | `-0.40` | `-0.49` |
| `-2/7` | `(5, 8, 1)` | `-0.521323` | `-0.526078` |

## Main results

* `irrational_dilog_of_hankelEstimates`: the general deduction.
* `irrational_dilog_two_elevenths_of_estimates`, `irrational_dilog_two_ninths_of_estimates`,
  `irrational_dilog_neg_two_ninths_of_estimates`,
  `irrational_dilog_neg_two_sevenths_of_estimates`: the four conditional target statements.
-/

namespace AxiomForge.Dilogarithm

open Polynomial Filter Topology

/-- **Unproved candidate estimates** of the Hankel-determinant method for `Li₂(λ)`, with
content rate `a` and decay rate `d` (both per `h ^ 2`, `h = H n`). See the module docstring:
these are hypotheses, not theorems. -/
structure HankelEstimates (lam : ℝ) (p : Parameters) (a d : ℝ) : Prop where
  /-- Arithmetic estimate: eventually `Q̃_n = c * P` with `P ∈ ℤ[X]`, `c > 0` and
  `log c ≥ a h ^ 2` (implied by `liminf h⁻² log cont(Q̃_n) > a`). -/
  content : ∀ᶠ n in atTop, ∃ c : ℝ, 0 < c ∧
    (∃ P : ℤ[X], P.map (Int.castRingHom ℝ) = c⁻¹ • normalizedHankelDet lam p n) ∧
    a * ((p.H * n : ℕ) : ℝ) ^ 2 ≤ Real.log c
  /-- Archimedean estimate: eventually `|Q̃_n(Li₂ λ)| ≤ exp (d h ^ 2)` (implied by
  `limsup h⁻² log |Q̃_n(ξ)| < d` with the convention `log 0 = -∞`). -/
  decay : ∀ᶠ n in atTop,
    |(normalizedHankelDet lam p n).eval (dilog lam)| ≤ Real.exp (d * ((p.H * n : ℕ) : ℝ) ^ 2)
  /-- Prime-index nonvanishing: for every rational `r`, `Q̃_p(r) ≠ 0` for all large primes. -/
  nonvanishing : ∀ r : ℚ, ∀ᶠ m in atTop, m.Prime → (normalizedHankelDet lam p m).eval (r : ℝ) ≠ 0

/-- **The final deduction** (proved): the three estimates with a positive margin `a - d > 0`
imply the irrationality of `Li₂(λ)`. -/
theorem irrational_dilog_of_hankelEstimates {lam : ℝ} {p : Parameters} (hH : 0 < p.H)
    {a d : ℝ} (had : d < a) (h : HankelEstimates lam p a d) : Irrational (dilog lam) := by
  have hh : Tendsto (fun n ↦ p.H * n) atTop atTop :=
    tendsto_id.const_mul_atTop' hH
  refine irrational_of_scaled_int_poly (sub_pos.mpr had) hh (normalizedHankelDet lam p)
    (Eventually.of_forall fun n ↦ natDegree_normalizedHankelDet_le lam p n)
    (fun r ↦ frequently_atTop_of_eventually_prime (h.nonvanishing r)) ?_
  filter_upwards [h.content, h.decay] with n ⟨c, hc, hP, hlog⟩ hdec
  refine ⟨c, hc, hP, hdec.trans ?_⟩
  set s : ℝ := ((p.H * n : ℕ) : ℝ) ^ 2
  calc Real.exp (d * s) = Real.exp (a * s) * Real.exp (-(a - d) * s) := by
        rw [← Real.exp_add]
        ring_nf
    _ ≤ c * Real.exp (-(a - d) * s) := by
        gcongr
        calc Real.exp (a * s) ≤ Real.exp (Real.log c) := Real.exp_le_exp.mpr hlog
          _ = c := Real.exp_log hc

/-- **Conditional** (on the unproved `HankelEstimates`): `Li₂(2/11)` is irrational. -/
theorem irrational_dilog_two_elevenths_of_estimates
    (h : HankelEstimates (2 / 11) ⟨4, 6, 1⟩ (-4.338 / 16) (-4.9 / 16)) :
    Irrational (dilog (2 / 11)) :=
  irrational_dilog_of_hankelEstimates (by norm_num) (by norm_num) h

/-- **Conditional** (on the unproved `HankelEstimates`): `Li₂(2/9)` is irrational. -/
theorem irrational_dilog_two_ninths_of_estimates
    (h : HankelEstimates (2 / 9) ⟨8, 9, 0⟩ (-1.33) (-1.34)) :
    Irrational (dilog (2 / 9)) :=
  irrational_dilog_of_hankelEstimates (by norm_num) (by norm_num) h

/-- **Conditional** (on the unproved `HankelEstimates`): `Li₂(-2/9)` is irrational. -/
theorem irrational_dilog_neg_two_ninths_of_estimates
    (h : HankelEstimates (-2 / 9) ⟨4, 7, 1⟩ (-0.40) (-0.49)) :
    Irrational (dilog (-2 / 9)) :=
  irrational_dilog_of_hankelEstimates (by norm_num) (by norm_num) h

/-- **Conditional** (on the unproved `HankelEstimates`): `Li₂(-2/7)` is irrational. -/
theorem irrational_dilog_neg_two_sevenths_of_estimates
    (h : HankelEstimates (-2 / 7) ⟨5, 8, 1⟩ (-0.521323) (-0.526078)) :
    Irrational (dilog (-2 / 7)) :=
  irrational_dilog_of_hankelEstimates (by norm_num) (by norm_num) h

end AxiomForge.Dilogarithm
