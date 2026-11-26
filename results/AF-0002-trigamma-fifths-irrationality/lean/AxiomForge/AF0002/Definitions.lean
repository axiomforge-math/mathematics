import Mathlib.NumberTheory.ZetaValues
import Mathlib.Analysis.PSeries
import Mathlib.Analysis.SumOverResidueClass
import Mathlib.NumberTheory.LSeries.HurwitzZeta

/-!
# The trigamma function at fifths and the numbers `ξ_k = ψ₁(k/5) - π²/2`

We define the trigamma function on `(0, ∞)` by its series `ψ₁(s) = ∑_{j ≥ 0} (j + s)⁻²` and
the four target numbers `ξ_k = ψ₁(k/5) - π²/2`, `k = 1, 2, 3, 4`.

## Main definitions

* `AxiomForge.Trigamma.trigamma s = ∑' j, 1 / (j + s) ^ 2`.
* `AxiomForge.Trigamma.xi k = trigamma (k / 5) - π ^ 2 / 2`.

## Main results

* `summable_trigamma`, `hasSum_trigamma`: convergence for `s > 0`.
* `trigamma_eq_hurwitzZeta`: on `(0, 1]` the definition agrees with Mathlib's Hurwitz zeta
  function, `ψ₁(s) = ζ(2, s)`.
* `trigamma_add_one`: the recurrence `ψ₁(s) = s⁻² + ψ₁(s + 1)`.
* `trigamma_one`, `trigamma_one_half`: `ψ₁(1) = π²/6` and `ψ₁(1/2) = π²/2`, so that
  `ξ_k = ψ₁(k/5) - ψ₁(1/2)` (`xi_eq_trigamma_sub_trigamma`), and `hasSum_xi` writes `ξ_k` as
  the series `∑_j ((j + k/5)⁻² - (j + 1/2)⁻²)`.
* `trigamma_one_fifth_add`: the multiplication formula
  `ψ₁(1/5) + ψ₁(2/5) + ψ₁(3/5) + ψ₁(4/5) = 4 π²`, an instance of Gauss' multiplication theorem
  proved by splitting `ζ(2)` into residue classes modulo `5`.
* `xi_one_add`: `ξ₁ + ξ₂ + ξ₃ + ξ₄ = 2 π²`.
-/

namespace AxiomForge.Trigamma

open Real

/-- The trigamma function `ψ₁(s) = ∑_{j ≥ 0} 1 / (j + s) ^ 2`, used for `s > 0`. -/
noncomputable def trigamma (s : ℝ) : ℝ := ∑' j : ℕ, 1 / ((j : ℝ) + s) ^ 2

/-- The target numbers `ξ_k = ψ₁(k/5) - π²/2`. -/
noncomputable def xi (k : ℕ) : ℝ := trigamma (k / 5) - π ^ 2 / 2

theorem summable_one_div_succ_sq : Summable fun k : ℕ ↦ 1 / ((k : ℝ) + 1) ^ 2 := by
  have h := (summable_nat_add_iff 1).mpr (Real.summable_one_div_nat_pow.mpr one_lt_two)
  simpa only [Nat.cast_add, Nat.cast_one] using h

theorem summable_trigamma {s : ℝ} (hs : 0 < s) :
    Summable fun j : ℕ ↦ 1 / ((j : ℝ) + s) ^ 2 := by
  rw [← summable_nat_add_iff 1]
  refine Summable.of_nonneg_of_le (fun j ↦ by positivity) (fun j ↦ ?_) summable_one_div_succ_sq
  push_cast
  refine one_div_le_one_div_of_le (by positivity) ?_
  have hj : (0 : ℝ) ≤ j := j.cast_nonneg
  nlinarith

theorem hasSum_trigamma {s : ℝ} (hs : 0 < s) :
    HasSum (fun j : ℕ ↦ 1 / ((j : ℝ) + s) ^ 2) (trigamma s) :=
  (summable_trigamma hs).hasSum

/-- On `(0, 1]` the trigamma function is the Hurwitz zeta function at `2`. -/
theorem trigamma_eq_hurwitzZeta {s : ℝ} (hs0 : 0 < s) (hs1 : s ≤ 1) :
    (trigamma s : ℂ) = HurwitzZeta.hurwitzZeta s 2 := by
  rw [← (HurwitzZeta.hasSum_hurwitzZeta_of_one_lt_re ⟨hs0.le, hs1⟩
    (by norm_num : 1 < (2 : ℂ).re)).tsum_eq, trigamma, Complex.ofReal_tsum]
  congr 1
  funext j
  push_cast
  rw [← Complex.cpow_natCast]
  norm_num

/-- The recurrence `ψ₁(s) = s⁻² + ψ₁(s + 1)`. -/
theorem trigamma_add_one {s : ℝ} (hs : 0 < s) : trigamma s = 1 / s ^ 2 + trigamma (s + 1) := by
  rw [trigamma, (summable_trigamma hs).tsum_eq_zero_add, trigamma]
  congr 1
  · simp
  · congr 1
    funext j
    push_cast
    ring_nf

theorem trigamma_one : trigamma 1 = π ^ 2 / 6 := by
  refine HasSum.tsum_eq ?_
  have h := (hasSum_nat_add_iff' 1).mpr hasSum_zeta_two
  simp only [Finset.range_one, Finset.sum_singleton, Nat.cast_zero, ne_eq, OfNat.ofNat_ne_zero,
    not_false_eq_true, zero_pow, div_zero, sub_zero, Nat.cast_add, Nat.cast_one] at h
  exact h

/-- The sum of `1 / (2 j + 1) ^ 2` is `π ^ 2 / 8`. -/
theorem hasSum_one_div_odd_sq :
    HasSum (fun j : ℕ ↦ 1 / ((2 * j + 1 : ℕ) : ℝ) ^ 2) (π ^ 2 / 8) := by
  set f : ℕ → ℝ := fun n ↦ 1 / (n : ℝ) ^ 2 with hfdef
  have hf : HasSum f (π ^ 2 / 6) := hasSum_zeta_two
  have he : HasSum (fun j : ℕ ↦ f (2 * j)) (π ^ 2 / 24) := by
    have h24 : π ^ 2 / 24 = π ^ 2 / 6 / 4 := by ring
    rw [h24]
    refine (hf.div_const 4).congr_fun fun j ↦ ?_
    simp only [hfdef]
    push_cast
    ring
  have hinj : Function.Injective fun j : ℕ ↦ 2 * j + 1 := fun a b hab ↦ by
    simp only at hab
    omega
  have hos : Summable fun j : ℕ ↦ f (2 * j + 1) := hf.summable.comp_injective hinj
  have huniq : π ^ 2 / 6 = π ^ 2 / 24 + ∑' j : ℕ, f (2 * j + 1) :=
    hf.unique (he.even_add_odd hos.hasSum)
  have hval : ∑' j : ℕ, f (2 * j + 1) = π ^ 2 / 8 := by linarith
  rw [← hval]
  exact hos.hasSum

theorem trigamma_one_half : trigamma (1 / 2) = π ^ 2 / 2 := by
  refine HasSum.tsum_eq ?_
  have h2 : π ^ 2 / 2 = 4 * (π ^ 2 / 8) := by ring
  rw [h2]
  refine (hasSum_one_div_odd_sq.mul_left 4).congr_fun fun j ↦ ?_
  push_cast
  field_simp
  ring

theorem xi_eq_trigamma_sub_trigamma (k : ℕ) : xi k = trigamma (k / 5) - trigamma (1 / 2) := by
  rw [xi, trigamma_one_half]

/-- Statement fidelity: for `k ≥ 1`, `ξ_k = ∑_{j ≥ 0} ((j + k/5)⁻² - (j + 1/2)⁻²)`. -/
theorem hasSum_xi {k : ℕ} (hk : 0 < k) :
    HasSum (fun j : ℕ ↦ 1 / ((j : ℝ) + k / 5) ^ 2 - 1 / ((j : ℝ) + 1 / 2) ^ 2) (xi k) := by
  rw [xi_eq_trigamma_sub_trigamma]
  exact (hasSum_trigamma (by positivity)).sub (hasSum_trigamma (by norm_num))

/-- The multiplication formula at fifths:
`ψ₁(1/5) + ψ₁(2/5) + ψ₁(3/5) + ψ₁(4/5) = 4 π²`. -/
theorem trigamma_one_fifth_add :
    trigamma (1 / 5) + trigamma (2 / 5) + trigamma (3 / 5) + trigamma (4 / 5) = 4 * π ^ 2 := by
  -- Split `ζ(2) = ∑_{N ≥ 0} (N + 1)⁻²` into residue classes modulo `5`.
  have hsum : Summable fun N : ℕ ↦ 1 / ((N : ℝ) + 1) ^ 2 := summable_one_div_succ_sq
  have hsplit := Nat.sumByResidueClasses hsum 5
  have hclass : ∀ j : ℕ, ∑' t : ℕ, 1 / (((j + 5 * t : ℕ) : ℝ) + 1) ^ 2 =
      trigamma ((j + 1) / 5) / 25 := by
    intro j
    rw [trigamma, ← tsum_div_const]
    congr 1
    funext t
    push_cast
    field_simp
    ring
  have h1 : ∑' N : ℕ, 1 / ((N : ℝ) + 1) ^ 2 = π ^ 2 / 6 := by
    rw [← trigamma_one, trigamma]
  have huniv : (Finset.univ : Finset (ZMod 5)) = {0, 1, 2, 3, 4} := by decide
  rw [h1, huniv, Finset.sum_insert (by decide), Finset.sum_insert (by decide),
    Finset.sum_insert (by decide), Finset.sum_insert (by decide), Finset.sum_singleton] at hsplit
  have v0 : (0 : ZMod 5).val = 0 := rfl
  have v1 : (1 : ZMod 5).val = 1 := rfl
  have v2 : (2 : ZMod 5).val = 2 := rfl
  have v3 : (3 : ZMod 5).val = 3 := rfl
  have v4 : (4 : ZMod 5).val = 4 := rfl
  rw [v0, v1, v2, v3, v4, hclass, hclass, hclass, hclass, hclass] at hsplit
  norm_num at hsplit
  rw [trigamma_one] at hsplit
  linarith

/-- `ξ₁ + ξ₂ + ξ₃ + ξ₄ = 2 π²`. -/
theorem xi_one_add : xi 1 + xi 2 + xi 3 + xi 4 = 2 * π ^ 2 := by
  have h := trigamma_one_fifth_add
  simp only [xi, Nat.cast_one, Nat.cast_ofNat]
  linarith

end AxiomForge.Trigamma
