import Mathlib.Analysis.Complex.ExponentialBounds
import Mathlib.Analysis.SpecialFunctions.Log.Deriv

/-!
# The logarithmic comparisons of the arithmetic certificates

The arithmetic estimates of the manuscripts end with an explicit comparison between a
rational lower bound for the integral of the ordinary-prime profile and a combination of
logarithms coming from the exceptional primes. This file proves these final comparisons in
the kernel for `λ = 2/11` and `λ = -2/7`, from Mathlib's enclosures of `log 2` and `log 3`
and the series `-log (1 - x) = ∑_{k ≥ 1} x ^ k / k` with its explicit remainder
bound (`Real.abs_log_sub_add_sum_range_le`).

The profile-integral lower bounds themselves (`9/2` for `2/11`, `0.07694503668343355` for
`-2/7`) are results of exact rational computations that are not formalized here.

## Main results

* `content_rate_two_elevenths_gt`:
  `9/2 - 16 log 2 - (25/4) log 9 + (20/3) log 11 > -4.338`.
* `content_rate_neg_two_sevenths_gt`:
  `0.07694503668343355 - (κ - 1/2) log 2 - ((2 - d) ^ 2 / 2) log 3 + (a + 1/6) log 7 > -0.521323`
  with `κ = 8/5`, `d = 1`, `a = 1/5`.
-/

namespace AxiomForge.Dilogarithm

open Real Finset

theorem log_eleven_eq : log 11 = 3 * log 2 - log (8 / 11) := by
  rw [log_div (by norm_num) (by norm_num), show (8 : ℝ) = 2 ^ 3 by norm_num, log_pow]
  push_cast
  ring

theorem log_nine_eq : log 9 = 2 * log 3 := by
  rw [show (9 : ℝ) = 3 ^ 2 by norm_num, log_pow]
  push_cast
  ring

theorem log_seven_eq : log 7 = 3 * log 2 + log (7 / 8) := by
  rw [log_div (by norm_num) (by norm_num), show (8 : ℝ) = 2 ^ 3 by norm_num, log_pow]
  push_cast
  ring

/-- `log (8/11) = log (1 - 3/11)` to six decimals, from ten terms of the series. -/
theorem log_eight_elevenths_bounds :
    -0.318455 < log (8 / 11) ∧ log (8 / 11) < -0.318452 := by
  have hs := abs_log_sub_add_sum_range_le (x := 3 / 11) (by norm_num [abs_of_pos]) 10
  rw [abs_le] at hs
  norm_num [Finset.sum_range_succ, abs_of_pos] at hs
  constructor <;> linarith [hs.1, hs.2]

/-- `log (7/8) = log (1 - 1/8)` to nine decimals, from ten terms of the series. -/
theorem log_seven_eighths_bounds :
    -0.133531393 < log (7 / 8) ∧ log (7 / 8) < -0.133531392 := by
  have hs := abs_log_sub_add_sum_range_le (x := 1 / 8) (by norm_num [abs_of_pos]) 10
  rw [abs_le] at hs
  norm_num [Finset.sum_range_succ, abs_of_pos] at hs
  constructor <;> linarith [hs.1, hs.2]

/-- The final comparison of the arithmetic estimate for `λ = 2/11` (per `n ²`):
`9/2 - 16 log 2 - (25/4) log 9 + (20/3) log 11 > -4.338`. -/
theorem content_rate_two_elevenths_gt :
    (-4.338 : ℝ) < 9 / 2 - 16 * log 2 - 25 / 4 * log 9 + 20 / 3 * log 11 := by
  rw [log_eleven_eq, log_nine_eq]
  have h := log_eight_elevenths_bounds
  linarith [log_two_gt_d9, log_two_lt_d9, log_three_gt_d9, log_three_lt_d9, h.1, h.2]

/-- The final comparison of the arithmetic estimate for `λ = -2/7` (per `h ²`), with
`κ = 8/5`, `d = 1`, `a = 1/5`:
`0.07694503668343355 - (κ - 1/2) log 2 - ((2 - d) ^ 2 / 2) log 3 + (a + 1/6) log 7 > -0.521323`. -/
theorem content_rate_neg_two_sevenths_gt :
    (-0.521323 : ℝ) < 0.07694503668343355 - (8 / 5 - 1 / 2) * log 2 -
      (2 - 1) ^ 2 / 2 * log 3 + (1 / 5 + 1 / 6) * log 7 := by
  rw [log_seven_eq]
  have h := log_seven_eighths_bounds
  linarith [log_two_gt_d9, log_two_lt_d9, log_three_gt_d9, log_three_lt_d9, h.1, h.2]

end AxiomForge.Dilogarithm
