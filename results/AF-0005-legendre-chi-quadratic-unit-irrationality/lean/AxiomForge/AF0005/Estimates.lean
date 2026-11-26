import AxiomForge.AF0005.IrrationalityCriterion
import AxiomForge.AF0005.Units

/-!
# Conditional irrationality of `T_σ(n)` for the new traces

The manuscript reduces the irrationality of `T_σ(n)` to estimates on a sequence of polynomials
`Q m = Δ_{2m} ∈ ℚ[X]` (Hankel determinants of Krisman's symmetric pencil) of degree at most
`h m = 2m`:

* **content** (arithmetic estimate): `Q m = c • P` with `P ∈ ℤ[X]`, `log c ≥ a h²`, where
  `-a` is the arithmetic constant `C(n)`; it combines the unreproved results (K1) (ordinary
  odd primes) and (K2) (prime 2, even `n`) of Krisman with the two new estimates of the
  manuscript, which are also not formalised;
* **decay** (size estimate): `|Q m (T)| ≤ exp (d h²)`, the result (K3) of Krisman with the new
  certificates;
* **nonvanishing** (K4): `Q m (r) ≠ 0` for infinitely many `m`, at every rational `r`.

`PencilEstimates` records them.  **Its fields are unproved**: the Hankel polynomials are not
defined in this package, and the theorems below prove only the final deduction and the margins.
Every such theorem has a name ending in `_of_estimates`.
-/

namespace AxiomForge.LegendreChi

open Polynomial Filter Topology

/-- **Unproved estimates** for a target `ξ` and a sequence of real polynomials `Q` of degree at
most `h`, with content rate `a` and decay rate `d` per `h ^ 2`. -/
structure PencilEstimates (ξ : ℝ) (Q : ℕ → ℝ[X]) (h : ℕ → ℕ) (a d : ℝ) : Prop where
  degree : ∀ m, (Q m).natDegree ≤ h m
  content : ∀ᶠ m in atTop, ∃ c : ℝ, 0 < c ∧
    (∃ P : ℤ[X], P.map (Int.castRingHom ℝ) = c⁻¹ • Q m) ∧ a * ((h m : ℕ) : ℝ) ^ 2 ≤ Real.log c
  decay : ∀ᶠ m in atTop, |(Q m).eval ξ| ≤ Real.exp (d * ((h m : ℕ) : ℝ) ^ 2)
  nonvanishing : ∀ r : ℚ, ∃ᶠ m in atTop, (Q m).eval (r : ℝ) ≠ 0

/-- **The final deduction** (proved): the estimates with `d < a` imply irrationality. -/
theorem irrational_of_pencilEstimates {ξ a d : ℝ} {Q : ℕ → ℝ[X]} {h : ℕ → ℕ}
    (hh : Tendsto h atTop atTop) (had : d < a) (H : PencilEstimates ξ Q h a d) :
    Irrational ξ := by
  refine irrational_of_scaled_int_poly (sub_pos.mpr had) hh Q
    (Eventually.of_forall H.degree) H.nonvanishing ?_
  filter_upwards [H.content, H.decay] with m ⟨c, hc, hP, hlog⟩ hdec
  refine ⟨c, hc, hP, hdec.trans ?_⟩
  set s : ℝ := ((h m : ℕ) : ℝ) ^ 2
  calc Real.exp (d * s) = Real.exp (a * s) * Real.exp (-(a - d) * s) := by
        rw [← Real.exp_add]
        ring_nf
    _ ≤ c * Real.exp (-(a - d) * s) := by
        gcongr
        calc Real.exp (a * s) ≤ Real.exp (Real.log c) := Real.exp_le_exp.mpr hlog
          _ = c := Real.exp_log hc

/-- Margin of `(n, σ) = (14, 1)`: `C(14) + Φ ≤ -0.0115` (rounded rates). -/
theorem margin_14_pos : (-2.00461 : ℝ) < -1.99310 := by norm_num
/-- Margin of `(14, -1)`. -/
theorem margin_14_neg : (-1.99936 : ℝ) < -1.99310 := by norm_num
/-- Margin of `(27, 1)`. -/
theorem margin_27_pos : (-2.33734 : ℝ) < -2.33058 := by norm_num
/-- Margin of `(27, -1)`. -/
theorem margin_27_neg : (-2.33595 : ℝ) < -2.33058 := by norm_num

/-- **Conditional**: `χ₂(z)` with `z = z₁(14)` is irrational, for any pencil data satisfying the
estimates with the rates certified for `(14, +1)`. -/
theorem irrational_unitValue_14_pos_of_estimates {Q : ℕ → ℝ[X]} {h : ℕ → ℕ}
    (hh : Tendsto h atTop atTop)
    (H : PencilEstimates (unitValue 1 14) Q h (-1.99310) (-2.00461)) :
    Irrational (legendreChi (unitZ 1 14)) := by
  rw [← unitValue_one]; exact irrational_of_pencilEstimates hh margin_14_pos H

/-- **Conditional**: `Ti₂(z)` with `z = z₋₁(14)` is irrational. -/
theorem irrational_unitValue_14_neg_of_estimates {Q : ℕ → ℝ[X]} {h : ℕ → ℕ}
    (hh : Tendsto h atTop atTop)
    (H : PencilEstimates (unitValue (-1) 14) Q h (-1.99310) (-1.99936)) :
    Irrational (inverseTangentIntegral (unitZ (-1) 14)) := by
  rw [← unitValue_neg_one]; exact irrational_of_pencilEstimates hh margin_14_neg H

/-- **Conditional**: `χ₂(z)` with `z = z₁(27)` is irrational. -/
theorem irrational_unitValue_27_pos_of_estimates {Q : ℕ → ℝ[X]} {h : ℕ → ℕ}
    (hh : Tendsto h atTop atTop)
    (H : PencilEstimates (unitValue 1 27) Q h (-2.33058) (-2.33734)) :
    Irrational (legendreChi (unitZ 1 27)) := by
  rw [← unitValue_one]; exact irrational_of_pencilEstimates hh margin_27_pos H

/-- **Conditional**: `Ti₂(z)` with `z = z₋₁(27)` is irrational. -/
theorem irrational_unitValue_27_neg_of_estimates {Q : ℕ → ℝ[X]} {h : ℕ → ℕ}
    (hh : Tendsto h atTop atTop)
    (H : PencilEstimates (unitValue (-1) 27) Q h (-2.33058) (-2.33595)) :
    Irrational (inverseTangentIntegral (unitZ (-1) 27)) := by
  rw [← unitValue_neg_one]; exact irrational_of_pencilEstimates hh margin_27_neg H

/-- Negative arguments, by oddness (proved). -/
theorem irrational_legendreChi_neg_unit_of_estimates {n : ℕ} {Q : ℕ → ℝ[X]} {h : ℕ → ℕ} {a d : ℝ}
    (hh : Tendsto h atTop atTop) (had : d < a) (H : PencilEstimates (unitValue 1 n) Q h a d) :
    Irrational (legendreChi (-unitZ 1 n)) := by
  rw [irrational_legendreChi_neg_iff, ← unitValue_one]
  exact irrational_of_pencilEstimates hh had H

theorem irrational_inverseTangentIntegral_neg_unit_of_estimates {n : ℕ} {Q : ℕ → ℝ[X]}
    {h : ℕ → ℕ} {a d : ℝ} (hh : Tendsto h atTop atTop) (had : d < a)
    (H : PencilEstimates (unitValue (-1) n) Q h a d) :
    Irrational (inverseTangentIntegral (-unitZ (-1) n)) := by
  rw [irrational_inverseTangentIntegral_neg_iff, ← unitValue_neg_one]
  exact irrational_of_pencilEstimates hh had H

end AxiomForge.LegendreChi
