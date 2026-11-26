import Mathlib.NumberTheory.ZetaValues
import Mathlib.Analysis.PSeries
import Mathlib.NumberTheory.Real.Irrational

/-!
# Legendre's chi function and the inverse tangent integral

## Main definitions

* `AxiomForge.LegendreChi.legendreChi x = ∑_{j ≥ 0} x ^ (2 j + 1) / (2 j + 1) ^ 2` (`χ₂`);
* `AxiomForge.LegendreChi.inverseTangentIntegral x =
  ∑_{j ≥ 0} (-1) ^ j x ^ (2 j + 1) / (2 j + 1) ^ 2` (`Ti₂`).

## Main results

* `summable_legendreChi`, `summable_inverseTangentIntegral`: absolute convergence for
  `|x| ≤ 1`.
* `legendreChi_neg`, `inverseTangentIntegral_neg`: both functions are odd (for every `x`).
* `irrational_legendreChi_neg_iff`, `irrational_inverseTangentIntegral_neg_iff`: hence the
  irrationality at `-x` is equivalent to the irrationality at `x`.
* `legendreChi_one`: `χ₂(1) = π² / 8` (a check of the definition against `ζ(2) = π²/6`).
* `legendreChi_pos`: `χ₂(x) > 0` on `(0, 1]`.
* `inverseTangentIntegral_term`: the series of `Ti₂` is alternating, with terms of
  decreasing absolute value on `[0, 1]`.

Mathlib (at the pinned revision) defines neither function.
-/

namespace AxiomForge.LegendreChi

open Real

/-- Legendre's chi function `χ₂(x) = ∑_{j ≥ 0} x ^ (2 j + 1) / (2 j + 1) ^ 2`. -/
noncomputable def legendreChi (x : ℝ) : ℝ :=
  ∑' j : ℕ, x ^ (2 * j + 1) / ((2 * j + 1 : ℕ) : ℝ) ^ 2

/-- The inverse tangent integral `Ti₂(x) = ∑_{j ≥ 0} (-1) ^ j x ^ (2 j + 1) / (2 j + 1) ^ 2`. -/
noncomputable def inverseTangentIntegral (x : ℝ) : ℝ :=
  ∑' j : ℕ, (-1) ^ j * x ^ (2 * j + 1) / ((2 * j + 1 : ℕ) : ℝ) ^ 2

theorem summable_one_div_odd_sq : Summable fun j : ℕ ↦ 1 / ((2 * j + 1 : ℕ) : ℝ) ^ 2 := by
  have hinj : Function.Injective fun j : ℕ ↦ 2 * j + 1 := fun a b hab ↦ by
    simp only at hab
    omega
  exact (Real.summable_one_div_nat_pow.mpr one_lt_two).comp_injective hinj

theorem summable_legendreChi {x : ℝ} (hx : |x| ≤ 1) :
    Summable fun j : ℕ ↦ x ^ (2 * j + 1) / ((2 * j + 1 : ℕ) : ℝ) ^ 2 := by
  refine Summable.of_norm_bounded summable_one_div_odd_sq fun j ↦ ?_
  rw [Real.norm_eq_abs, abs_div, abs_pow,
    abs_of_pos (show (0 : ℝ) < ((2 * j + 1 : ℕ) : ℝ) ^ 2 by positivity)]
  gcongr
  exact pow_le_one₀ (abs_nonneg x) hx

theorem summable_inverseTangentIntegral {x : ℝ} (hx : |x| ≤ 1) :
    Summable fun j : ℕ ↦ (-1) ^ j * x ^ (2 * j + 1) / ((2 * j + 1 : ℕ) : ℝ) ^ 2 := by
  refine Summable.of_norm_bounded summable_one_div_odd_sq fun j ↦ ?_
  rw [Real.norm_eq_abs, abs_div, abs_mul, abs_pow, abs_pow, abs_neg, abs_one, one_pow, one_mul,
    abs_of_pos (show (0 : ℝ) < ((2 * j + 1 : ℕ) : ℝ) ^ 2 by positivity)]
  gcongr
  exact pow_le_one₀ (abs_nonneg x) hx

/-- `χ₂` is odd. -/
theorem legendreChi_neg (x : ℝ) : legendreChi (-x) = -legendreChi x := by
  rw [legendreChi, legendreChi, ← tsum_neg]
  congr 1
  funext j
  rw [Odd.neg_pow (odd_two_mul_add_one j), neg_div]

/-- `Ti₂` is odd. -/
theorem inverseTangentIntegral_neg (x : ℝ) :
    inverseTangentIntegral (-x) = -inverseTangentIntegral x := by
  rw [inverseTangentIntegral, inverseTangentIntegral, ← tsum_neg]
  congr 1
  funext j
  rw [Odd.neg_pow (odd_two_mul_add_one j), mul_neg, neg_div]

theorem irrational_legendreChi_neg_iff {x : ℝ} :
    Irrational (legendreChi (-x)) ↔ Irrational (legendreChi x) := by
  rw [legendreChi_neg, irrational_neg_iff]

theorem irrational_inverseTangentIntegral_neg_iff {x : ℝ} :
    Irrational (inverseTangentIntegral (-x)) ↔ Irrational (inverseTangentIntegral x) := by
  rw [inverseTangentIntegral_neg, irrational_neg_iff]

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
  have hos : Summable fun j : ℕ ↦ f (2 * j + 1) := summable_one_div_odd_sq
  have huniq : π ^ 2 / 6 = π ^ 2 / 24 + ∑' j : ℕ, f (2 * j + 1) :=
    hf.unique (he.even_add_odd hos.hasSum)
  have hval : ∑' j : ℕ, f (2 * j + 1) = π ^ 2 / 8 := by linarith
  rw [← hval]
  exact hos.hasSum

/-- `χ₂(1) = π ^ 2 / 8`. -/
theorem legendreChi_one : legendreChi 1 = π ^ 2 / 8 := by
  rw [legendreChi]
  simpa only [one_pow] using hasSum_one_div_odd_sq.tsum_eq

/-- `χ₂` is positive on `(0, 1]`. -/
theorem legendreChi_pos {x : ℝ} (hx0 : 0 < x) (hx1 : x ≤ 1) : 0 < legendreChi x := by
  have hx : |x| ≤ 1 := by rwa [abs_of_pos hx0]
  refine (summable_legendreChi hx).tsum_pos (fun j ↦ by positivity) 0 ?_
  simp [hx0]

/-- The series of `Ti₂` is alternating: its `j`-th term is `(-1) ^ j` times a nonnegative
term which, for `0 ≤ x ≤ 1`, decreases with `j`. -/
theorem inverseTangentIntegral_term {x : ℝ} (hx0 : 0 ≤ x) (hx1 : x ≤ 1) (j : ℕ) :
    0 ≤ x ^ (2 * j + 1) / ((2 * j + 1 : ℕ) : ℝ) ^ 2 ∧
      x ^ (2 * (j + 1) + 1) / ((2 * (j + 1) + 1 : ℕ) : ℝ) ^ 2 ≤
        x ^ (2 * j + 1) / ((2 * j + 1 : ℕ) : ℝ) ^ 2 := by
  refine ⟨by positivity, ?_⟩
  have hpow : x ^ (2 * (j + 1) + 1) ≤ x ^ (2 * j + 1) := pow_le_pow_of_le_one hx0 hx1 (by omega)
  have hden : ((2 * j + 1 : ℕ) : ℝ) ^ 2 ≤ ((2 * (j + 1) + 1 : ℕ) : ℝ) ^ 2 := by
    gcongr
    omega
  calc x ^ (2 * (j + 1) + 1) / ((2 * (j + 1) + 1 : ℕ) : ℝ) ^ 2
      ≤ x ^ (2 * j + 1) / ((2 * (j + 1) + 1 : ℕ) : ℝ) ^ 2 := by gcongr
    _ ≤ x ^ (2 * j + 1) / ((2 * j + 1 : ℕ) : ℝ) ^ 2 := by
        gcongr

end AxiomForge.LegendreChi
