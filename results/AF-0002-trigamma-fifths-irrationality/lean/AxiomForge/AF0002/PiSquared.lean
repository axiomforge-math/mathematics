import Mathlib.Analysis.SpecialFunctions.Integrals.Basic
import Mathlib.Topology.Algebra.Order.Floor
import Mathlib.NumberTheory.Real.Irrational

/-!
# `π ^ 2` is irrational

Mathlib proves `irrational_pi` by Cartwright's method; it does not contain the classical
strengthening (Legendre, 1794) that `π ^ 2` is irrational. This file proves it by the same
method, keeping track of the parity of the polynomials involved.

Let `I n θ = ∫_{-1}^{1} (1 - x ^ 2) ^ n cos (x θ) dx`. Integration by parts gives
`I n θ * θ ^ (2 n + 1) = n! (S_n(θ ^ 2) sin θ + θ C_n(θ ^ 2) cos θ)` with integer polynomials
`S_n`, `C_n` of degree at most `n / 2`. At `θ = π / 2`, if `π ^ 2 = a / b`, then
`(4 b) ^ (n / 2) S_n(a / (4 b))` is an integer which is positive and tends to zero.

The analytic lemmas `I`, `recursion'`, `I_zero`, `I_one`, `I_pos`, `I_le` and the integrality
lemma are copied from `Mathlib/Analysis/Real/Pi/Irrational.lean` (Bhavik Mehta, Apache 2.0),
where they are private; only the polynomials and the final argument are new.

## Main results

* `AxiomForge.Trigamma.irrational_pi_sq`: `Irrational (π ^ 2)`.
-/

noncomputable section

namespace AxiomForge.Trigamma

open intervalIntegral MeasureTheory.MeasureSpace Set Polynomial Real Filter
open scoped Nat

namespace PiSquared

/-- The integrals of Cartwright's proof (as in Mathlib). -/
def I (n : ℕ) (θ : ℝ) : ℝ := ∫ x in (-1)..1, (1 - x ^ 2) ^ n * cos (x * θ)

variable {n : ℕ} {θ : ℝ}

theorem I_zero : I 0 θ * θ = 2 * sin θ := by
  rw [mul_comm, I]
  simp [mul_integral_comp_mul_right, two_mul]

/-- The integration by parts step (copied from Mathlib's proof of `irrational_pi`). -/
theorem recursion' (n : ℕ) :
    I (n + 1) θ * θ ^ 2 = - (2 * 2 * ((n + 1) * (0 ^ n * cos θ))) +
      2 * (n + 1) * (2 * n + 1) * I n θ - 4 * (n + 1) * n * I (n - 1) θ := by
  rw [I]
  let f (x : ℝ) : ℝ := 1 - x ^ 2
  let u₁ (x : ℝ) : ℝ := f x ^ (n + 1)
  let u₁' (x : ℝ) : ℝ := - (2 * (n + 1) * x * f x ^ n)
  let v₁ (x : ℝ) : ℝ := sin (x * θ)
  let v₁' (x : ℝ) : ℝ := cos (x * θ) * θ
  let u₂ (x : ℝ) : ℝ := x * (f x) ^ n
  let u₂' (x : ℝ) : ℝ := (f x) ^ n - 2 * n * x ^ 2 * (f x) ^ (n - 1)
  let v₂ (x : ℝ) : ℝ := cos (x * θ)
  let v₂' (x : ℝ) : ℝ := -sin (x * θ) * θ
  have hfd : Continuous f := by fun_prop
  have hu₁d : Continuous u₁' := by fun_prop
  have hv₁d : Continuous v₁' := by fun_prop
  have hu₂d : Continuous u₂' := by fun_prop
  have hv₂d : Continuous v₂' := by fun_prop
  have hu₁_eval_one : u₁ 1 = 0 := by simp only [u₁, f]; simp
  have hu₁_eval_neg_one : u₁ (-1) = 0 := by simp only [u₁, f]; simp
  have t : u₂ 1 * v₂ 1 - u₂ (-1) * v₂ (-1) = 2 * (0 ^ n * cos θ) := by
    simp [u₂, v₂, f, ← two_mul]
  have hf (x) : HasDerivAt f (- 2 * x) x := by
    convert! (hasDerivAt_pow 2 x).const_sub 1 using 1
    simp
  have hu₁ (x) : HasDerivAt u₁ (u₁' x) x := by
    convert! (hf x).pow _ using 1
    simp only [Nat.add_succ_sub_one, u₁', Nat.cast_add_one]
    ring
  have hv₁ (x) : HasDerivAt v₁ (v₁' x) x := (hasDerivAt_mul_const θ).sin
  have hu₂ (x) : HasDerivAt u₂ (u₂' x) x := by
    convert! (hasDerivAt_id' x).fun_mul ((hf x).fun_pow _) using 1
    simp only [u₂']
    ring
  have hv₂ (x) : HasDerivAt v₂ (v₂' x) x := (hasDerivAt_mul_const θ).cos
  convert_to (∫ (x : ℝ) in (-1)..1, u₁ x * v₁' x) * θ = _ using 1
  · simp_rw [u₁, v₁', f, ← intervalIntegral.integral_mul_const, sq θ, mul_assoc]
  rw [integral_mul_deriv_eq_deriv_mul (fun x _ => hu₁ x) (fun x _ => hv₁ x)
    (hu₁d.intervalIntegrable _ _) (hv₁d.intervalIntegrable _ _), hu₁_eval_one, hu₁_eval_neg_one,
    zero_mul, zero_mul, sub_zero, zero_sub, ← integral_neg, ← integral_mul_const]
  convert_to ((-2 : ℝ) * (n + 1)) * ∫ (x : ℝ) in (-1)..1, (u₂ x * v₂' x) = _ using 1
  · rw [← integral_const_mul]
    congr 1 with x
    dsimp [u₁', v₁, u₂, v₂']
    ring
  rw [integral_mul_deriv_eq_deriv_mul (fun x _ => hu₂ x) (fun x _ => hv₂ x)
    (hu₂d.intervalIntegrable _ _) (hv₂d.intervalIntegrable _ _),
    mul_sub, t, neg_mul, neg_mul, neg_mul, sub_neg_eq_add]
  have (x : _) : u₂' x = (2 * n + 1) * f x ^ n - 2 * n * f x ^ (n - 1) := by
    cases n with
    | zero => simp [u₂']
    | succ n => ring!
  simp_rw [this, sub_mul, mul_assoc _ _ (v₂ _)]
  have : Continuous v₂ := by fun_prop
  rw [mul_mul_mul_comm, integral_sub, mul_sub, add_sub_assoc]
  · congr 1
    simp_rw [integral_const_mul]
    ring!
  all_goals exact Continuous.intervalIntegrable (by fun_prop) _ _

theorem recursion (n : ℕ) :
    I (n + 2) θ * θ ^ 2 =
      2 * (n + 2) * (2 * n + 3) * I (n + 1) θ - 4 * (n + 2) * (n + 1) * I n θ := by
  rw [recursion' (n + 1)]
  push_cast
  ring

theorem I_one : I 1 θ * θ ^ 3 = 4 * sin θ - 4 * θ * cos θ := by
  rw [_root_.pow_succ, ← mul_assoc, recursion' 0, sub_mul, add_mul, mul_assoc _ (I 0 θ), I_zero]
  ring

/-- The even part: `sinPoly n = S_n(X ^ 2)` in Mathlib's notation. -/
def sinPolySq : ℕ → ℤ[X]
  | 0 => C 2
  | 1 => C 4
  | n + 2 => ((2 : ℤ) * (2 * n + 3)) • sinPolySq (n + 1) + monomial 1 (-4) * sinPolySq n

/-- The odd part: `cosPoly n = X * C_n(X ^ 2)` in Mathlib's notation. -/
def cosPolySq : ℕ → ℤ[X]
  | 0 => 0
  | 1 => C (-4)
  | n + 2 => ((2 : ℤ) * (2 * n + 3)) • cosPolySq (n + 1) + monomial 1 (-4) * cosPolySq n

/-- The degree of `S_n` is at most `n / 2`: this is the gain over Mathlib's bound `n`. -/
theorem sinPolySq_natDegree_le : ∀ n : ℕ, (sinPolySq n).natDegree ≤ n / 2
  | 0
  | 1 => by simp [sinPolySq]
  | n + 2 => by
    rw [sinPolySq]
    refine natDegree_add_le_of_degree_le ((natDegree_smul_le _ _).trans ?_) ?_
    · exact (sinPolySq_natDegree_le (n + 1)).trans (by omega)
    refine natDegree_mul_le.trans ?_
    have h1 := sinPolySq_natDegree_le n
    have h2 : (monomial 1 (-4 : ℤ)).natDegree ≤ 1 := natDegree_monomial_le _
    omega

/-- The key identity
`I n θ * θ ^ (2 n + 1) = n! (S_n(θ ^ 2) sin θ + θ C_n(θ ^ 2) cos θ)`. -/
theorem sinPolySq_add_cosPolySq_eval (θ : ℝ) :
    ∀ n : ℕ,
      I n θ * θ ^ (2 * n + 1) = n ! * ((sinPolySq n).eval₂ (Int.castRingHom _) (θ ^ 2) * sin θ +
        θ * (cosPolySq n).eval₂ (Int.castRingHom _) (θ ^ 2) * cos θ)
  | 0 => by simp [sinPolySq, cosPolySq, I_zero]
  | 1 => by simp [I_one, sinPolySq, cosPolySq]; ring
  | n + 2 => by
      calc I (n + 2) θ * θ ^ (2 * (n + 2) + 1) = I (n + 2) θ * θ ^ 2 * θ ^ (2 * n + 3) := by ring
        _ = 2 * (n + 2) * (2 * n + 3) * (I (n + 1) θ * θ ^ (2 * (n + 1) + 1)) -
            4 * (n + 2) * (n + 1) * θ ^ 2 * (I n θ * θ ^ (2 * n + 1)) := by rw [recursion]; ring
        _ = _ := by
          simp [sinPolySq_add_cosPolySq_eval, sinPolySq, cosPolySq, Nat.factorial_succ]
          ring

/-- Integrality after clearing denominators (copied from Mathlib's proof). -/
theorem is_integer {p : ℤ[X]} (a b : ℤ) {k : ℕ} (hp : p.natDegree ≤ k) :
    ∃ z : ℤ, p.eval₂ (Int.castRingHom ℝ) (a / b) * b ^ k = z := by
  rcases eq_or_ne b 0 with rfl | hb
  · rcases k.eq_zero_or_pos with rfl | hk
    · exact ⟨p.coeff 0, by simp⟩
    exact ⟨0, by simp [hk.ne']⟩
  refine ⟨∑ i ∈ p.support, p.coeff i * a ^ i * b ^ (k - i), ?_⟩
  conv => lhs; rw [← sum_monomial_eq p]
  rw [eval₂_sum, sum, Finset.sum_mul, Int.cast_sum]
  simp only [eval₂_monomial, eq_intCast, div_pow, Int.cast_mul, Int.cast_pow]
  refine Finset.sum_congr rfl (fun i hi => ?_)
  have ik := (le_natDegree_of_mem_supp i hi).trans hp
  rw [mul_assoc, div_mul_comm, ← Int.cast_pow, ← Int.cast_pow, ← Int.cast_pow,
    ← pow_sub_mul_pow b ik, ← Int.cast_div_charZero, Int.mul_ediv_cancel _ (pow_ne_zero _ hb),
    ← mul_assoc, mul_right_comm, ← Int.cast_pow]
  exact dvd_mul_left _ _

theorem I_pos : 0 < I n (π / 2) := by
  refine integral_pos (by simp) (by fun_prop) ?_ ⟨0, by simp⟩
  refine fun x hx => mul_nonneg (pow_nonneg ?_ _) ?_
  · rw [sub_nonneg, sq_le_one_iff_abs_le_one, abs_le]
    exact ⟨hx.1.le, hx.2⟩
  refine cos_nonneg_of_neg_pi_div_two_le_of_le ?_ ?_ <;>
  nlinarith [hx.1, hx.2, pi_pos]

theorem I_le (n : ℕ) : I n (π / 2) ≤ 2 := by
  rw [← norm_of_nonneg I_pos.le]
  refine (norm_integral_le_of_norm_le_const ?_).trans (show (1 : ℝ) * _ ≤ _ by norm_num)
  intro x hx
  simp only [uIoc_of_le, neg_le_self_iff, zero_le_one, mem_Ioc] at hx
  rw [norm_eq_abs, abs_mul, abs_pow]
  refine mul_le_one₀ (pow_le_one₀ (abs_nonneg _) ?_) (abs_nonneg _) (abs_cos_le_one _)
  rw [abs_le]
  constructor <;> nlinarith

end PiSquared

open PiSquared in
/-- **`π ^ 2` is irrational** (Legendre). -/
theorem irrational_pi_sq : Irrational (π ^ 2) := by
  rw [Irrational]
  rintro ⟨q, hq⟩
  -- Write `π ^ 2 = a / b` with `a b : ℤ`, `b > 0`; then `(π / 2) ^ 2 = a / B` with `B = 4 b`.
  set a : ℤ := q.num
  set B : ℤ := 4 * q.den
  have hB : (0 : ℝ) < B := by simp only [B]; push_cast; positivity
  have hB1 : (1 : ℝ) ≤ B := by
    simp only [B]; push_cast
    have : (1 : ℝ) ≤ q.den := by exact_mod_cast q.pos
    linarith
  have hθ : (π / 2) ^ 2 = (a : ℝ) / B := by
    rw [div_pow, ← hq, ← Rat.num_div_den q]
    simp only [a, B]
    push_cast
    ring
  have key (n : ℕ) :
      I n (π / 2) * (π / 2) ^ (2 * n + 1) =
        n ! * (sinPolySq n).eval₂ (Int.castRingHom ℝ) ((π / 2) ^ 2) := by
    simpa using sinPolySq_add_cosPolySq_eval (π / 2) n
  have tend : Tendsto (fun n : ℕ ↦ 2 * (π / 2) * ((π / 2) ^ 2 * B) ^ n / n !) atTop (nhds 0) := by
    have := (FloorSemiring.tendsto_pow_div_factorial_atTop ((π / 2) ^ 2 * B)).const_mul
      (2 * (π / 2))
    simpa only [mul_zero, mul_div_assoc] using this
  obtain ⟨n, hn⟩ := (tend.eventually_lt_const one_pos).exists
  obtain ⟨z, hz⟩ := is_integer (p := sinPolySq n) a B (sinPolySq_natDegree_le n)
  have hfac : (0 : ℝ) < n ! := by exact_mod_cast Nat.factorial_pos n
  -- `z = I_n (π / 2) * (π / 2) ^ (2 n + 1) / n! * B ^ (n / 2)`.
  have hzval : (z : ℝ) = I n (π / 2) * (π / 2) ^ (2 * n + 1) / n ! * (B : ℝ) ^ (n / 2) := by
    rw [← hz, ← hθ, key n]
    field_simp
  have hz0 : (0 : ℝ) < z := by
    rw [hzval]
    have := I_pos (n := n)
    positivity
  have hz1 : (z : ℝ) < 1 := by
    rw [hzval]
    calc I n (π / 2) * (π / 2) ^ (2 * n + 1) / n ! * (B : ℝ) ^ (n / 2)
        ≤ 2 * (π / 2) ^ (2 * n + 1) / n ! * (B : ℝ) ^ n := by
          have h1 : I n (π / 2) ≤ 2 := I_le n
          have h2 : (B : ℝ) ^ (n / 2) ≤ (B : ℝ) ^ n :=
            pow_le_pow_right₀ hB1 (Nat.div_le_self n 2)
          have h3 : 0 ≤ I n (π / 2) := I_pos.le
          gcongr
      _ = 2 * (π / 2) * ((π / 2) ^ 2 * B) ^ n / n ! := by
          rw [mul_pow, ← pow_mul, pow_succ]
          ring
      _ < 1 := hn
  have h0 : (0 : ℤ) < z := by exact_mod_cast hz0
  have h1 : z < (1 : ℤ) := by exact_mod_cast hz1
  omega

end AxiomForge.Trigamma
