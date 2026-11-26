import AxiomForge.AF0003.IrrationalityCriterion
import AxiomForge.AF0003.Construction

/-!
# Conditional irrationality of `χ₂(±2/q)` and `Ti₂(±2/q)` for odd `q ≥ 81`

The candidate proofs reduce the irrationality of `ξ = targetValue σ (q / 2)` (that is
`χ₂(2/q)` for `σ = 1` and `Ti₂(2/q)` for `σ = -1`) to three estimates on the explicit
normalized pencils `T_n = halfHankelDet σ (q / 2) p n` of `Construction`:

1. an **arithmetic estimate**: `liminf h⁻² log cont(T_n) ≥ a`;
2. an **archimedean estimate**: `limsup h⁻² log |T_n(ξ)| ≤ d` with `d < a`;
3. **prime-index nonvanishing**: for each rational `r`, `T_p(r) ≠ 0` for all large primes.

`HalfIntegerEstimates σ y p a d` records these statements, in the eventual form implied by
the `liminf`/`limsup` claims. **Its fields are unproved candidate estimates**; the theorems
`*_of_estimates` prove only the final deduction and are not formalizations of the main
theorems.

## Rates (per `h ²`) taken from the candidate proofs

* `q ≥ 83`, `(H, K', A') = (6, 7, 0)`: the certificates give `A_-(83) > -3.15484583292` and
  `B_83 < -3.16170895858`; the extension to all `q ≥ 83` gives the content rate
  `A_σ(q) ≥ A_-(83) - (1/72) log(q/83)` and the decay rate `B_q ≤ B_83 - (1/2) log(q/83)`.
  We use the rounded rates `contentRate q = -3.1549 - log(q/83) / 72` and
  `decayRate q = -3.1617 - log(q/83) / 2`, which are implied by those claims;
  `decayRate_lt_contentRate` checks the margin for every `q ≥ 83`.
* `q = 81`, `(H, K', A') = (40, 49, 2)`: `A_-(81) ≈ -3.368497051454495`,
  `B_81 ≈ -3.374176113235810`; we use `-3.3685` and `-3.3741`.

## Unconditional finite certificate

* `primeTwoProfile_ge`: the minimum `-1847/1100` of the prime-2 profile at `q = 81`
  (prime-2 estimate of the `q = 81` construction), with equality at `x = 51/55`.

## Main results

* `irrational_targetValue_of_halfIntegerEstimates`: the general conditional deduction.
* `irrational_legendreChi_two_div_of_estimates`,
  `irrational_inverseTangentIntegral_two_div_of_estimates`: odd `q ≥ 81`;
* `irrational_legendreChi_neg_two_div_of_estimates`,
  `irrational_inverseTangentIntegral_neg_two_div_of_estimates`: negative arguments, by
  oddness (the oddness itself is proved unconditionally in `Definitions`).
-/

namespace AxiomForge.LegendreChi

open Polynomial Filter Topology

/-- **Unproved candidate estimates** of the half-integer Hankel method for
`ξ = targetValue σ y`, with content rate `a` and decay rate `d` per `h ^ 2`, `h = H n`. -/
structure HalfIntegerEstimates (σ y : ℝ) (p : Parameters) (a d : ℝ) : Prop where
  /-- Arithmetic estimate: eventually `T_n = c * P` with `P ∈ ℤ[X]`, `c > 0`,
  `log c ≥ a h ^ 2`. -/
  content : ∀ᶠ n in atTop, ∃ c : ℝ, 0 < c ∧
    (∃ P : ℤ[X], P.map (Int.castRingHom ℝ) = c⁻¹ • halfHankelDet σ y p n) ∧
    a * ((p.H * n : ℕ) : ℝ) ^ 2 ≤ Real.log c
  /-- Archimedean estimate: eventually `|T_n(ξ)| ≤ exp (d h ^ 2)`. -/
  decay : ∀ᶠ n in atTop,
    |(halfHankelDet σ y p n).eval (targetValue σ y)| ≤ Real.exp (d * ((p.H * n : ℕ) : ℝ) ^ 2)
  /-- Prime-index nonvanishing at every fixed rational point. -/
  nonvanishing : ∀ r : ℚ, ∀ᶠ m in atTop, m.Prime → (halfHankelDet σ y p m).eval (r : ℝ) ≠ 0

/-- **The final deduction** (proved): the three estimates with `d < a` imply that
`targetValue σ y` is irrational. -/
theorem irrational_targetValue_of_halfIntegerEstimates {σ y : ℝ} {p : Parameters}
    (hH : 0 < p.H) {a d : ℝ} (had : d < a) (h : HalfIntegerEstimates σ y p a d) :
    Irrational (targetValue σ y) := by
  have hh : Tendsto (fun n ↦ p.H * n) atTop atTop := tendsto_id.const_mul_atTop' hH
  refine irrational_of_scaled_int_poly (sub_pos.mpr had) hh (halfHankelDet σ y p)
    (Eventually.of_forall fun n ↦ natDegree_halfHankelDet_le σ y p n)
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

/-- The parameters of the construction: `(40, 49, 2)` for `q = 81`, `(6, 7, 0)` otherwise. -/
def parameters (q : ℕ) : Parameters := if q = 81 then ⟨40, 49, 2⟩ else ⟨6, 7, 0⟩

/-- Content rate for `q ≥ 83` (rounded down from `A_-(83) - (1/72) log(q/83)`). -/
noncomputable def contentRate (q : ℕ) : ℝ := -3.1549 - Real.log (q / 83) / 72

/-- Decay rate for `q ≥ 83` (rounded up from `B_83 - (1/2) log(q/83)`). -/
noncomputable def decayRate (q : ℕ) : ℝ := -3.1617 - Real.log (q / 83) / 2

/-- The margin of the `q ≥ 83` family: `decayRate q < contentRate q`. -/
theorem decayRate_lt_contentRate {q : ℕ} (hq : 83 ≤ q) : decayRate q < contentRate q := by
  have hlog : 0 ≤ Real.log (q / 83) := by
    apply Real.log_nonneg
    rw [le_div_iff₀ (by norm_num)]
    exact_mod_cast (by omega : 1 * 83 ≤ q)
  unfold decayRate contentRate
  linarith

/-- The margin at `q = 81`: `-3.3741 < -3.3685`. -/
theorem decay_lt_content_eighty_one : (-3.3741 : ℝ) < -3.3685 := by norm_num

/-- The estimates assumed for the odd `q ≥ 81` family, with the rates of the manuscripts. -/
def FamilyEstimates (σ : ℝ) (q : ℕ) : Prop :=
  if q = 81 then HalfIntegerEstimates σ (q / 2) (parameters q) (-3.3685) (-3.3741)
  else HalfIntegerEstimates σ (q / 2) (parameters q) (contentRate q) (decayRate q)

theorem irrational_targetValue_of_familyEstimates {σ : ℝ} {q : ℕ} (hodd : Odd q)
    (hq : 81 ≤ q) (h : FamilyEstimates σ q) : Irrational (targetValue σ (q / 2)) := by
  unfold FamilyEstimates at h
  split_ifs at h with h81
  · exact irrational_targetValue_of_halfIntegerEstimates (by simp [parameters, h81])
      decay_lt_content_eighty_one h
  · have h83 : 83 ≤ q := by
      obtain ⟨k, rfl⟩ := hodd
      omega
    exact irrational_targetValue_of_halfIntegerEstimates (by simp [parameters, h81])
      (decayRate_lt_contentRate h83) h

/-- **Conditional** (on the unproved `FamilyEstimates 1 q`): `χ₂(2/q)` is irrational for
every odd `q ≥ 81`. -/
theorem irrational_legendreChi_two_div_of_estimates {q : ℕ} (hodd : Odd q) (hq : 81 ≤ q)
    (h : FamilyEstimates 1 q) : Irrational (legendreChi (2 / q)) := by
  rw [← targetValue_one]
  exact irrational_targetValue_of_familyEstimates hodd hq h

/-- **Conditional** (on the unproved `FamilyEstimates (-1) q`): `Ti₂(2/q)` is irrational for
every odd `q ≥ 81`. -/
theorem irrational_inverseTangentIntegral_two_div_of_estimates {q : ℕ} (hodd : Odd q)
    (hq : 81 ≤ q) (h : FamilyEstimates (-1) q) : Irrational (inverseTangentIntegral (2 / q)) := by
  rw [← targetValue_neg_one]
  exact irrational_targetValue_of_familyEstimates hodd hq h

/-- **Conditional** (on the unproved `FamilyEstimates 1 q`): `χ₂(-2/q)` is irrational for
every odd `q ≥ 81`. -/
theorem irrational_legendreChi_neg_two_div_of_estimates {q : ℕ} (hodd : Odd q) (hq : 81 ≤ q)
    (h : FamilyEstimates 1 q) : Irrational (legendreChi (-2 / q)) := by
  rw [neg_div, irrational_legendreChi_neg_iff]
  exact irrational_legendreChi_two_div_of_estimates hodd hq h

/-- **Conditional** (on the unproved `FamilyEstimates (-1) q`): `Ti₂(-2/q)` is irrational for
every odd `q ≥ 81`. -/
theorem irrational_inverseTangentIntegral_neg_two_div_of_estimates {q : ℕ} (hodd : Odd q)
    (hq : 81 ≤ q) (h : FamilyEstimates (-1) q) :
    Irrational (inverseTangentIntegral (-2 / q)) := by
  rw [neg_div, irrational_inverseTangentIntegral_neg_iff]
  exact irrational_inverseTangentIntegral_two_div_of_estimates hodd hq h

/-- The prime-2 profile of the `q = 81` construction:
`f(x) = 2 (d - 1) - 4 κ x + 3 x ² + (5/2) (1 - x) ² + 6 α (1 - x)` with `κ = 49/40`,
`α = 1/20`, `d = 9/8`. -/
def primeTwoProfile (x : ℚ) : ℚ :=
  2 * (9 / 8 - 1) - 4 * (49 / 40) * x + 3 * x ^ 2 + 5 / 2 * (1 - x) ^ 2 + 6 * (1 / 20) * (1 - x)

/-- Its minimum is `-1847/1100` (kernel-checked). -/
theorem primeTwoProfile_ge (x : ℚ) : -1847 / 1100 ≤ primeTwoProfile x := by
  unfold primeTwoProfile
  nlinarith [sq_nonneg (x - 51 / 55)]

theorem primeTwoProfile_min : primeTwoProfile (51 / 55) = -1847 / 1100 := by
  norm_num [primeTwoProfile]

end AxiomForge.LegendreChi
