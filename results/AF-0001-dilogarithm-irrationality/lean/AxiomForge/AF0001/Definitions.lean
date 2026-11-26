import Mathlib.NumberTheory.ZetaValues
import Mathlib.Analysis.PSeries

/-!
# The real dilogarithm as a power series

We define the real dilogarithm `Li₂ x = ∑_{k ≥ 1} x ^ k / k ^ 2` as a `tsum` and prove the
elementary facts that pin down the meaning of the irrationality statements:

## Main definitions

* `AxiomForge.Dilogarithm.dilogTerm x k = x ^ (k + 1) / (k + 1) ^ 2`, the term of index
  `k + 1` of the series.
* `AxiomForge.Dilogarithm.dilog x = ∑' k, dilogTerm x k`.

## Main results

* `summable_dilogTerm`, `hasSum_dilog`: absolute convergence on the closed disc `|x| ≤ 1`.
* `hasSum_pow_div_sq`, `dilog_eq_tsum`: statement fidelity,
  `Li₂ x = ∑_{k ≥ 1} x ^ k / k ^ 2` written with the summation index starting at `k = 1`
  (the `k = 0` term vanishes by the convention `a / 0 = 0`).
* `dilog_zero`, `dilog_one`: `Li₂ 0 = 0` and `Li₂ 1 = π ^ 2 / 6` (from Mathlib's `ζ(2)`).
* `dilog_add_dilog_neg`: the duplication formula `Li₂ x + Li₂ (-x) = Li₂ (x ^ 2) / 2`.
* `dilog_neg_one`: `Li₂ (-1) = -π ^ 2 / 12`.
* `dilog_pos`, `dilog_neg_of_neg`: `Li₂ x > 0` on `(0, 1]` and `Li₂ x < 0` on `[-1, 0)`.

Mathlib (at the pinned revision) has no polylogarithm, so there is nothing to relate to; the
values at `±1` serve as a check that the definition is the classical one.
-/

namespace AxiomForge.Dilogarithm

open Real

/-- The term `x ^ (k + 1) / (k + 1) ^ 2` of index `k + 1` of the dilogarithm series. -/
noncomputable def dilogTerm (x : ℝ) (k : ℕ) : ℝ := x ^ (k + 1) / ((k : ℝ) + 1) ^ 2

/-- The real dilogarithm `Li₂ x = ∑_{k ≥ 1} x ^ k / k ^ 2`. The series converges absolutely
for `|x| ≤ 1`, the only range used; outside it `tsum` returns its junk value `0`. -/
noncomputable def dilog (x : ℝ) : ℝ := ∑' k : ℕ, dilogTerm x k

theorem summable_one_div_succ_sq : Summable fun k : ℕ ↦ 1 / ((k : ℝ) + 1) ^ 2 := by
  have h := (summable_nat_add_iff 1).mpr (Real.summable_one_div_nat_pow.mpr one_lt_two)
  simpa only [Nat.cast_add, Nat.cast_one] using h

theorem abs_dilogTerm_le {x : ℝ} (hx : |x| ≤ 1) (k : ℕ) :
    |dilogTerm x k| ≤ 1 / ((k : ℝ) + 1) ^ 2 := by
  rw [dilogTerm, abs_div, abs_pow, abs_of_pos (by positivity : (0 : ℝ) < ((k : ℝ) + 1) ^ 2)]
  gcongr
  exact pow_le_one₀ (abs_nonneg x) hx

theorem summable_dilogTerm {x : ℝ} (hx : |x| ≤ 1) : Summable (dilogTerm x) :=
  Summable.of_norm_bounded summable_one_div_succ_sq fun k ↦ by
    simpa only [Real.norm_eq_abs] using abs_dilogTerm_le hx k

theorem hasSum_dilog {x : ℝ} (hx : |x| ≤ 1) : HasSum (dilogTerm x) (dilog x) :=
  (summable_dilogTerm hx).hasSum

/-- Statement fidelity: `Li₂ x = ∑_{k ≥ 1} x ^ k / k ^ 2`, written over all `k : ℕ` (the term
`k = 0` is `x ^ 0 / 0 = 0`). -/
theorem hasSum_pow_div_sq {x : ℝ} (hx : |x| ≤ 1) :
    HasSum (fun k : ℕ ↦ x ^ k / (k : ℝ) ^ 2) (dilog x) := by
  rw [← hasSum_nat_add_iff' 1]
  simp only [Finset.range_one, Finset.sum_singleton, Nat.cast_zero, ne_eq, OfNat.ofNat_ne_zero,
    not_false_eq_true, zero_pow, div_zero, sub_zero, Nat.cast_add, Nat.cast_one]
  exact hasSum_dilog hx

theorem dilog_eq_tsum {x : ℝ} (hx : |x| ≤ 1) : dilog x = ∑' k : ℕ, x ^ k / (k : ℝ) ^ 2 :=
  (hasSum_pow_div_sq hx).tsum_eq.symm

@[simp] theorem dilog_zero : dilog 0 = 0 := by simp [dilog, dilogTerm]

/-- `Li₂ 1 = ζ(2) = π ^ 2 / 6`. -/
theorem dilog_one : dilog 1 = π ^ 2 / 6 :=
  (hasSum_pow_div_sq (by simp)).unique (by simpa using hasSum_zeta_two)

/-- The duplication formula `Li₂ x + Li₂ (-x) = Li₂ (x ^ 2) / 2` for `|x| ≤ 1`. -/
theorem dilog_add_dilog_neg {x : ℝ} (hx : |x| ≤ 1) :
    dilog x + dilog (-x) = dilog (x ^ 2) / 2 := by
  have hx2 : |x ^ 2| ≤ 1 := by
    rw [abs_pow]
    exact pow_le_one₀ (abs_nonneg x) hx
  set f : ℕ → ℝ := fun k ↦ x ^ k / (k : ℝ) ^ 2 + (-x) ^ k / (k : ℝ) ^ 2 with hf
  have hsum : HasSum f (dilog x + dilog (-x)) :=
    (hasSum_pow_div_sq hx).add (hasSum_pow_div_sq (by rwa [abs_neg]))
  have heven : HasSum (fun k ↦ f (2 * k)) (dilog (x ^ 2) / 2) := by
    have h := (hasSum_pow_div_sq hx2).div_const 2
    refine h.congr_fun fun k ↦ ?_
    simp only [hf, Even.neg_pow (even_two_mul k), Nat.cast_mul, Nat.cast_ofNat]
    ring
  have hodd : HasSum (fun k ↦ f (2 * k + 1)) 0 := by
    refine (hasSum_zero).congr_fun fun k ↦ ?_
    simp only [hf, Odd.neg_pow (odd_two_mul_add_one k)]
    ring
  have h := heven.even_add_odd hodd
  rw [add_zero] at h
  exact hsum.unique h

/-- `Li₂ (-1) = -π ^ 2 / 12`. -/
theorem dilog_neg_one : dilog (-1) = -(π ^ 2 / 12) := by
  have h := dilog_add_dilog_neg (x := 1) (by simp)
  rw [one_pow, dilog_one] at h
  linarith

/-- The dilogarithm is positive on `(0, 1]`. -/
theorem dilog_pos {x : ℝ} (hx0 : 0 < x) (hx1 : x ≤ 1) : 0 < dilog x := by
  have hx : |x| ≤ 1 := by rwa [abs_of_pos hx0]
  refine (summable_dilogTerm hx).tsum_pos (fun k ↦ by unfold dilogTerm; positivity) 0 ?_
  simp [dilogTerm, hx0]

/-- The dilogarithm is monotone on `[0, 1]`. -/
theorem dilog_le_dilog {x y : ℝ} (hx : 0 ≤ x) (hxy : x ≤ y) (hy : y ≤ 1) :
    dilog x ≤ dilog y := by
  have hxa : |x| ≤ 1 := by rw [abs_of_nonneg hx]; linarith
  have hya : |y| ≤ 1 := by rw [abs_of_nonneg (hx.trans hxy)]; exact hy
  refine (summable_dilogTerm hxa).tsum_le_tsum (fun k ↦ ?_) (summable_dilogTerm hya)
  unfold dilogTerm
  gcongr

/-- The dilogarithm is negative on `[-1, 0)`. -/
theorem dilog_neg_of_neg {x : ℝ} (hx1 : -1 ≤ x) (hx0 : x < 0) : dilog x < 0 := by
  have hy0 : 0 < -x := neg_pos.mpr hx0
  have hy1 : -x ≤ 1 := by linarith
  have hdup := dilog_add_dilog_neg (x := -x) (by rw [abs_of_pos hy0]; exact hy1)
  rw [neg_neg] at hdup
  have hsq : (-x) ^ 2 ≤ -x := by nlinarith
  have hmono := dilog_le_dilog (sq_nonneg (-x)) hsq hy1
  have hpos := dilog_pos hy0 hy1
  linarith

end AxiomForge.Dilogarithm
