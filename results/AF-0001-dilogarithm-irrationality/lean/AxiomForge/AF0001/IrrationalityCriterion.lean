import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.NumberTheory.Real.Irrational
import Mathlib.RingTheory.Polynomial.ScaleRoots
import Mathlib.Algebra.Polynomial.Degree.Lemmas
import Mathlib.Data.Nat.Prime.Infinite

/-!
# An irrationality criterion via integer polynomials

This file proves the elementary criterion that closes every Hankel- or Löwner-determinant
irrationality argument: a real number `x` is irrational as soon as it admits integer
polynomial approximations `P` that do not vanish at `x` but are so small at `x` that no fixed
denominator bound `B` can compensate, i.e. `B ^ deg P * |P x| < 1`.

If `x = a / b` were rational, then `b ^ deg P * P (a / b)` would be a nonzero integer, so
`1 ≤ b ^ deg P * |P x|`. Everything else in this file repackages this observation in the forms
in which it is used.

## Main results

* `one_le_pow_mul_abs_aeval_div`: clearing denominators. If `P : ℤ[X]` has degree at most `d`
  and `P (a / b) ≠ 0` with `b > 0`, then `1 ≤ b ^ d * |P (a / b)|`.
* `irrational_of_int_poly_approx`: if for every `B ≥ 1` there is `P : ℤ[X]` of degree at most
  `d` with `P x ≠ 0` and `B ^ d * |P x| < 1`, then `x` is irrational.
* `irrational_of_tendsto_int_poly`: the sequential form, with nonvanishing at every rational
  point required only along a frequent set of indices.
* `irrational_of_scaled_int_poly`: the form used by determinant constructions. Real
  polynomials `Q n` of degree at most `h n → ∞`, each a positive multiple `c n` of an integer
  polynomial (`c n` plays the role of the content), nonvanishing at each rational point for
  infinitely many `n`, with `|Q n x| ≤ c n * exp (-ε * h n ^ 2)` eventually.
* `irrational_of_log_content_decay`: the "content + decay + nonvanishing" form of the
  manuscripts for rational polynomials: `Q n / c n ∈ ℤ[X]` with `c n > 0`, degree at most
  `h n`, and `log |Q n x| - log (c n) ≤ -ε * h n ^ 2` eventually.
* `irrational_of_rat_value_decay`: the form of Löwner-determinant arguments, where the
  approximating quantities are values at a rational point with controlled denominators.
* `frequently_atTop_of_eventually_prime`: nonvanishing at all large primes gives nonvanishing
  along a frequent set of indices.

All statements are unconditional and depend only on the standard axioms.

The same file appears, with an adapted namespace, in the other irrationality packages of
this series: each package keeps its own copy so that it is self-contained.
-/

namespace AxiomForge.Dilogarithm

open Polynomial Filter Topology

/-- Evaluation of an integer polynomial through `aeval` is evaluation through `Int.cast`. -/
theorem aeval_int_eq_eval₂ (P : ℤ[X]) (x : ℝ) :
    aeval x P = P.eval₂ (Int.castRingHom ℝ) x := by
  rw [aeval_def, algebraMap_int_eq]

/-- Homogenisation: `b ^ deg P * P (a / b)` is the integer `(scaleRoots P b).eval a`. -/
theorem intCast_eval_scaleRoots (P : ℤ[X]) (a : ℤ) {b : ℕ} (hb : 0 < b) :
    (((scaleRoots P (b : ℤ)).eval a : ℤ) : ℝ) =
      (b : ℝ) ^ P.natDegree * aeval ((a : ℝ) / b) P := by
  have hb' : (b : ℝ) ≠ 0 := by positivity
  have hab : (Int.castRingHom ℝ) (b : ℤ) * ((a : ℝ) / b) = (a : ℝ) := by
    rw [eq_intCast, Int.cast_natCast]
    field_simp
  have h := scaleRoots_eval₂_mul (p := P) (Int.castRingHom ℝ) ((a : ℝ) / b) (b : ℤ)
  rw [hab, eq_intCast, Int.cast_natCast] at h
  rw [aeval_int_eq_eval₂, ← h, eval₂_at_intCast, eq_intCast, Int.cast_id]

/-- **Clearing denominators.** If `P : ℤ[X]` has degree at most `d` and does not vanish at the
rational point `a / b` (with `b > 0`), then `1 ≤ b ^ d * |P (a / b)|`. -/
theorem one_le_pow_mul_abs_aeval_div {P : ℤ[X]} {d : ℕ} (hd : P.natDegree ≤ d) (a : ℤ)
    {b : ℕ} (hb : 0 < b) (hP : aeval ((a : ℝ) / b) P ≠ 0) :
    1 ≤ (b : ℝ) ^ d * |aeval ((a : ℝ) / b) P| := by
  have hzR := intCast_eval_scaleRoots P a hb
  have hb1 : (1 : ℝ) ≤ b := by exact_mod_cast hb
  have hz0 : (scaleRoots P (b : ℤ)).eval a ≠ 0 := by
    intro h0
    rw [h0, Int.cast_zero] at hzR
    exact hP ((mul_eq_zero.mp hzR.symm).resolve_left (by positivity))
  calc (1 : ℝ) ≤ |(((scaleRoots P (b : ℤ)).eval a : ℤ) : ℝ)| := by
        rw [← Int.cast_abs]
        exact_mod_cast Int.one_le_abs hz0
    _ = (b : ℝ) ^ P.natDegree * |aeval ((a : ℝ) / b) P| := by
        rw [hzR, abs_mul, abs_of_pos (by positivity)]
    _ ≤ (b : ℝ) ^ d * |aeval ((a : ℝ) / b) P| := by
        gcongr

/-- A real number that is not irrational is a quotient `a / b` with `a : ℤ` and `0 < b : ℕ`. -/
theorem exists_eq_int_div_nat_of_not_irrational {x : ℝ} (hx : ¬Irrational x) :
    ∃ (a : ℤ) (b : ℕ), 0 < b ∧ x = a / b := by
  rw [Irrational, not_not, Set.mem_range] at hx
  obtain ⟨q, rfl⟩ := hx
  exact ⟨q.num, q.den, q.pos, by exact_mod_cast (Rat.num_div_den q).symm⟩

/-- **Irrationality criterion.** If for every denominator bound `B ≥ 1` there is an integer
polynomial `P` of degree at most `d` with `P x ≠ 0` and `B ^ d * |P x| < 1`, then `x` is
irrational. -/
theorem irrational_of_int_poly_approx {x : ℝ}
    (h : ∀ B : ℕ, 0 < B → ∃ (d : ℕ) (P : ℤ[X]),
      P.natDegree ≤ d ∧ aeval x P ≠ 0 ∧ (B : ℝ) ^ d * |aeval x P| < 1) :
    Irrational x := by
  by_contra hx
  obtain ⟨a, b, hb, rfl⟩ := exists_eq_int_div_nat_of_not_irrational hx
  obtain ⟨d, P, hd, hP, hlt⟩ := h b hb
  exact (one_le_pow_mul_abs_aeval_div hd a hb hP).not_gt hlt

/-- **Irrationality criterion, sequential form.** Let `P n : ℤ[X]` have degree at most `d n`.
Assume that at every rational point `r` the polynomials `P n` do not vanish for infinitely
many `n`, and that `B ^ d n * |P n x| → 0` for every `B : ℕ`. Then `x` is irrational. -/
theorem irrational_of_tendsto_int_poly {x : ℝ} (P : ℕ → ℤ[X]) (d : ℕ → ℕ)
    (hdeg : ∀ n, (P n).natDegree ≤ d n)
    (hnv : ∀ r : ℚ, ∃ᶠ n in atTop, aeval (r : ℝ) (P n) ≠ 0)
    (hsmall : ∀ B : ℕ, Tendsto (fun n ↦ (B : ℝ) ^ d n * |aeval x (P n)|) atTop (𝓝 0)) :
    Irrational x := by
  rintro ⟨r, rfl⟩
  obtain ⟨n, hlt, hne⟩ :=
    (((hsmall r.den).eventually_lt_const one_pos).and_frequently (hnv r)).exists
  have hr : (r : ℝ) = (r.num : ℝ) / r.den := by exact_mod_cast (Rat.num_div_den r).symm
  rw [hr] at hlt hne
  exact (one_le_pow_mul_abs_aeval_div (hdeg n) r.num r.pos hne).not_gt hlt

/-- `B ^ h * exp (-ε * h ^ 2) < 1` as soon as `0 < h` and `log B < ε * h`. -/
theorem pow_mul_exp_neg_sq_lt_one {B ε : ℝ} (hB : 0 < B) {h : ℕ} (hh : 0 < h)
    (hlog : Real.log B < ε * h) : B ^ h * Real.exp (-ε * (h : ℝ) ^ 2) < 1 := by
  have hhR : (0 : ℝ) < h := by exact_mod_cast hh
  calc B ^ h * Real.exp (-ε * (h : ℝ) ^ 2)
      = Real.exp (h * Real.log B + -ε * (h : ℝ) ^ 2) := by
        rw [Real.exp_add, ← Real.log_pow, Real.exp_log (pow_pos hB h)]
    _ < Real.exp 0 := Real.exp_lt_exp.mpr (by nlinarith)
    _ = 1 := Real.exp_zero

/-- **Irrationality criterion, scaled form.** Let `Q n` be real polynomials of degree at most
`h n`, where `h n → ∞`. Assume that

* at every rational point the polynomials `Q n` do not vanish for infinitely many `n`;
* for some `ε > 0`, eventually `Q n = c * P` for some real `c > 0` (a content) and some
  integer polynomial `P`, with `|Q n x| ≤ c * exp (-ε * h n ^ 2)`.

Then `x` is irrational. -/
theorem irrational_of_scaled_int_poly {x ε : ℝ} (hε : 0 < ε) {h : ℕ → ℕ}
    (hh : Tendsto h atTop atTop) (Q : ℕ → ℝ[X])
    (hdeg : ∀ᶠ n in atTop, (Q n).natDegree ≤ h n)
    (hnv : ∀ r : ℚ, ∃ᶠ n in atTop, (Q n).eval (r : ℝ) ≠ 0)
    (hbound : ∀ᶠ n in atTop, ∃ c : ℝ, 0 < c ∧
      (∃ P : ℤ[X], P.map (Int.castRingHom ℝ) = c⁻¹ • Q n) ∧
      |(Q n).eval x| ≤ c * Real.exp (-ε * (h n : ℝ) ^ 2)) :
    Irrational x := by
  rintro ⟨r, rfl⟩
  have hB : (0 : ℝ) < r.den := by exact_mod_cast r.pos
  obtain ⟨M, hM⟩ := exists_nat_gt (Real.log r.den / ε)
  obtain ⟨n, ⟨⟨hdegn, c, hc, ⟨P, hP⟩, hdec⟩, hn⟩, hne⟩ :=
    (((hdeg.and hbound).and (hh.eventually_ge_atTop (M + 1))).and_frequently (hnv r)).exists
  -- Evaluation of the integer polynomial `P` is evaluation of `Q n` divided by `c`.
  have heval : ∀ y : ℝ, aeval y P = c⁻¹ * (Q n).eval y := by
    intro y
    rw [aeval_def, algebraMap_int_eq, ← eval_map, hP, eval_smul, smul_eq_mul]
  have hdegP : P.natDegree ≤ h n := by
    rw [← natDegree_map_eq_of_injective (Int.castRingHom ℝ).injective_int P, hP]
    exact (natDegree_smul_le _ _).trans hdegn
  have hr : (r : ℝ) = (r.num : ℝ) / r.den := by exact_mod_cast (Rat.num_div_den r).symm
  have hPne : aeval ((r.num : ℝ) / r.den) P ≠ 0 := by
    rw [← hr, heval]
    exact mul_ne_zero (inv_ne_zero hc.ne') hne
  have hlow := one_le_pow_mul_abs_aeval_div hdegP r.num r.pos hPne
  rw [← hr, heval, abs_mul, abs_inv, abs_of_pos hc] at hlow
  have hhn : 0 < h n := by omega
  have hlog : Real.log r.den < ε * (h n : ℝ) := by
    have h1 : Real.log r.den < ε * M := by
      rw [div_lt_iff₀ hε] at hM
      linarith
    have h2 : (M : ℝ) ≤ h n := by exact_mod_cast (Nat.le_succ M).trans hn
    nlinarith
  have hsmall := pow_mul_exp_neg_sq_lt_one hB hhn hlog
  have hle : (r.den : ℝ) ^ h n * (c⁻¹ * |(Q n).eval (r : ℝ)|) ≤
      (r.den : ℝ) ^ h n * Real.exp (-ε * (h n : ℝ) ^ 2) := by
    gcongr
    rw [inv_mul_le_iff₀ hc]
    exact hdec
  linarith

/-- The logarithmic decay hypothesis of the manuscripts implies the multiplicative one (with
the convention `Real.log 0 = 0`, the implication still holds when `v = 0`). -/
theorem abs_le_mul_exp_of_log_sub_log_le {v c t : ℝ} (hc : 0 < c)
    (h : Real.log |v| - Real.log c ≤ t) : |v| ≤ c * Real.exp t := by
  rcases eq_or_ne v 0 with rfl | hv
  · simp only [abs_zero]
    positivity
  · have hv' : 0 < |v| := abs_pos.mpr hv
    calc |v| = Real.exp (Real.log |v|) := (Real.exp_log hv').symm
      _ ≤ Real.exp (Real.log c + t) := Real.exp_le_exp.mpr (by linarith)
      _ = c * Real.exp t := by rw [Real.exp_add, Real.exp_log hc]

/-- **Irrationality criterion, content form** (content + decay + nonvanishing), for rational
polynomials as in the manuscripts. Let `Q n : ℚ[X]` have degree at most `h n → ∞` and let
`c n > 0` be rationals with `Q n / c n ∈ ℤ[X]` (e.g. `c n` the content of `Q n`). If at every
rational point the `Q n` do not vanish for infinitely many `n`, and for some `ε > 0`,
eventually `log |Q n x| - log (c n) ≤ -ε * h n ^ 2`, then `x` is irrational. -/
theorem irrational_of_log_content_decay {x ε : ℝ} (hε : 0 < ε) {h : ℕ → ℕ}
    (hh : Tendsto h atTop atTop) (Q : ℕ → ℚ[X]) (c : ℕ → ℚ) (hc : ∀ n, 0 < c n)
    (hint : ∀ n, ∃ P : ℤ[X], P.map (Int.castRingHom ℚ) = (c n)⁻¹ • Q n)
    (hdeg : ∀ n, (Q n).natDegree ≤ h n)
    (hnv : ∀ r : ℚ, ∃ᶠ n in atTop, aeval (r : ℝ) (Q n) ≠ 0)
    (hdecay : ∀ᶠ n in atTop,
      Real.log |aeval x (Q n)| - Real.log (c n) ≤ -ε * (h n : ℝ) ^ 2) :
    Irrational x := by
  have hcomp : (algebraMap ℚ ℝ).comp (Int.castRingHom ℚ) = Int.castRingHom ℝ :=
    RingHom.ext_int _ _
  refine irrational_of_scaled_int_poly hε hh (fun n ↦ (Q n).map (algebraMap ℚ ℝ))
    (Eventually.of_forall fun n ↦ (natDegree_map_le).trans (hdeg n)) ?_ ?_
  · intro r
    simpa only [eval_map_algebraMap] using hnv r
  · filter_upwards [hdecay] with n hn
    obtain ⟨P, hP⟩ := hint n
    refine ⟨c n, by exact_mod_cast hc n, ⟨P, ?_⟩, ?_⟩
    · rw [← hcomp, ← Polynomial.map_map, hP, Polynomial.map_smul]
      simp
    · rw [eval_map_algebraMap]
      exact abs_le_mul_exp_of_log_sub_log_le (by exact_mod_cast hc n) hn

/-- A nonzero rational number `q` satisfies `|q| ≥ exp (-log q.den)`. -/
theorem exp_neg_log_den_le_abs {q : ℚ} (hq : q ≠ 0) :
    Real.exp (-Real.log q.den) ≤ |(q : ℝ)| := by
  have hden : (0 : ℝ) < q.den := by exact_mod_cast q.pos
  have hnum : (1 : ℝ) ≤ |(q.num : ℝ)| := by
    rw [← Int.cast_abs]
    exact_mod_cast Int.one_le_abs (Rat.num_ne_zero.mpr hq)
  rw [Real.exp_neg, Real.exp_log hden]
  calc (q.den : ℝ)⁻¹ ≤ |(q.num : ℝ)| / q.den := by
        rw [inv_eq_one_div]
        gcongr
    _ = |(q : ℝ)| := by
        rw [Rat.cast_def, abs_div, abs_of_pos hden]

/-- **Irrationality criterion, rational-value form.** Let `v n i : ℝ → ℝ` be a family of
functions indexed by `n : ℕ` and by `i` in an admissible set `adm n` (for instance determinants
with at most one deleted node), and let `s n → ∞` be a scale. Assume that

* for every rational `r`, for infinitely many `n` some admissible `v n i` takes at `r` a
  nonzero rational value `q` whose denominator satisfies `log q.den ≤ A * s n`;
* eventually, every admissible `v n i` satisfies `|v n i x| ≤ exp (-D * s n)`;

with `A < D`. Then `x` is irrational. -/
theorem irrational_of_rat_value_decay {x A D : ℝ} (hAD : A < D) {ι : Type*}
    (adm : ℕ → ι → Prop) (v : ℕ → ι → ℝ → ℝ) {s : ℕ → ℝ} (hs : Tendsto s atTop atTop)
    (hnv : ∀ r : ℚ, ∃ᶠ n in atTop, ∃ i, adm n i ∧ ∃ q : ℚ, q ≠ 0 ∧ v n i r = q ∧
      Real.log q.den ≤ A * s n)
    (hdecay : ∀ᶠ n in atTop, ∀ i, adm n i → |v n i x| ≤ Real.exp (-D * s n)) :
    Irrational x := by
  rintro ⟨r, rfl⟩
  obtain ⟨n, ⟨hdec, hpos⟩, i, hi, q, hq0, hq, hden⟩ :=
    ((hdecay.and (hs.eventually_gt_atTop 0)).and_frequently (hnv r)).exists
  have hlow := exp_neg_log_den_le_abs hq0
  rw [← hq] at hlow
  have hup := hdec i hi
  have : Real.exp (-D * s n) < Real.exp (-Real.log q.den) := by
    apply Real.exp_lt_exp.mpr
    nlinarith
  linarith

/-- Nonvanishing at all sufficiently large primes gives nonvanishing for infinitely many
indices, which is the form consumed by the criteria above. -/
theorem frequently_atTop_of_eventually_prime {p : ℕ → Prop}
    (h : ∀ᶠ n in atTop, n.Prime → p n) : ∃ᶠ n in atTop, p n := by
  rw [frequently_atTop]
  intro a
  obtain ⟨N, hN⟩ := eventually_atTop.mp h
  obtain ⟨q, hq, hqp⟩ := Nat.exists_infinite_primes (max a N)
  exact ⟨q, le_of_max_le_left hq, hN q (le_of_max_le_right hq) hqp⟩

end AxiomForge.Dilogarithm
