import AxiomForge.AF0002.IrrationalityCriterion
import AxiomForge.AF0002.Construction
import AxiomForge.AF0002.PiSquared

/-!
# Irrationality of `ψ₁(k/5) - π²/2`: unconditional and conditional results

## Unconditional results (proved)

* `irrational_xi_one_or_xi_two_or_xi_three_or_xi_four`: at least one of
  `ξ₁, ξ₂, ξ₃, ξ₄` is irrational. Proof: `ξ₁ + ξ₂ + ξ₃ + ξ₄ = 2 π²` (Gauss' multiplication
  formula at fifths, `Definitions`) and `π²` is irrational (`PiSquared`).
* `arithmeticRate_lt`, `arithmetic_lt_decay`: the finite rational comparisons of the
  certificate, `A = 304227995343501721142691896310988016794079029050925423 /
  86622067750624596685118168422516024981216422248448000 < 3.512131 < 3.512607`.

## Conditional results

The candidate proof reduces the irrationality of `ξ = ψ₁(s) - π²/2`, `s = k / 5`, to three
statements about the explicit separated pencils `P_sep,I = separatedLownerDet s m I`
(`h = 16 m`, at most one deleted common node):

1. **nonvanishing with one deletion**: for every rational `X` and every
   `m ≥ 1` some admissible `I` has `P_sep,I(X) ≠ 0`;
2. **arithmetic estimate**: at a fixed rational `X`, eventually every admissible
   `P_sep,I(X)` is a rational number with `log den ≤ 3.512131 h²` (the certified integral is
   `A = 3.5121303755…`, see `arithmeticRate_lt`);
3. **archimedean estimate**: eventually every admissible `|P_sep,I(ξ)| ≤ exp(-3.512607 h²)`
   (the recomputed certificate gives the stronger rate `3.5128848`).

The structure `LownerEstimates s` records exactly these statements.
**Its fields are unproved candidate estimates**; the theorems `*_of_estimates` prove only
the final deduction. In particular they are not formalizations of the main theorem.

## Main results

* `irrational_trigamma_sub_of_lownerEstimates`: the general conditional deduction.
* `irrational_xi_one_of_estimates`, …, `irrational_xi_four_of_estimates`: the four
  conditional target statements `Irrational (ψ₁(k/5) - π²/2)`.
-/

namespace AxiomForge.Trigamma

open Polynomial Filter Real

/-- **At least one of `ξ₁, ξ₂, ξ₃, ξ₄` is irrational** (unconditional). -/
theorem irrational_xi_one_or_xi_two_or_xi_three_or_xi_four :
    Irrational (xi 1) ∨ Irrational (xi 2) ∨ Irrational (xi 3) ∨ Irrational (xi 4) := by
  by_contra h
  simp only [not_or, Irrational, not_not, Set.mem_range] at h
  obtain ⟨⟨q₁, h₁⟩, ⟨q₂, h₂⟩, ⟨q₃, h₃⟩, ⟨q₄, h₄⟩⟩ := h
  apply irrational_pi_sq
  refine ⟨(q₁ + q₂ + q₃ + q₄) / 2, ?_⟩
  have hsum := xi_one_add
  push_cast
  rw [h₁, h₂, h₃, h₄]
  linarith

/-- The exact rational value `A` of the arithmetic integral of the certificate. -/
def arithmeticRate : ℚ :=
  304227995343501721142691896310988016794079029050925423 /
    86622067750624596685118168422516024981216422248448000

/-- `A < 3.512131` (kernel-checked rational comparison). -/
theorem arithmeticRate_lt : arithmeticRate < 3512131 / 1000000 := by
  norm_num [arithmeticRate]

/-- The margin of the candidate proof: `3.512131 < 3.512607`. -/
theorem arithmetic_lt_decay : (3.512131 : ℝ) < 3.512607 := by norm_num

/-- **Unproved candidate estimates** for `ξ = ψ₁(s) - π²/2` (see the module docstring). -/
structure LownerEstimates (s : ℝ) : Prop where
  /-- Nonvanishing with one deletion: for every rational `X` and `m ≥ 1`, some admissible
  pencil does not vanish at `X`. -/
  nonvanishing : ∀ r : ℚ, ∀ m : ℕ, 0 < m →
    ∃ c, Admissible m c ∧ (separatedLownerDet s m c).eval (r : ℝ) ≠ 0
  /-- Arithmetic estimate: at a rational `X`, eventually every admissible value is a rational
  with `log den ≤ 3.512131 h²`, `h = 16 m`. -/
  denominator : ∀ r : ℚ, ∀ᶠ m in atTop, ∀ c, Admissible m c →
    ∃ q : ℚ, (separatedLownerDet s m c).eval (r : ℝ) = q ∧
      Real.log q.den ≤ 3.512131 * ((16 * m : ℕ) : ℝ) ^ 2
  /-- Archimedean estimate: eventually `|P_sep,I(ξ)| ≤ exp (-3.512607 h²)` for every admissible
  deletion. -/
  decay : ∀ᶠ m in atTop, ∀ c, Admissible m c →
    |(separatedLownerDet s m c).eval (trigamma s - π ^ 2 / 2)| ≤
      Real.exp (-3.512607 * ((16 * m : ℕ) : ℝ) ^ 2)

theorem tendsto_sixteen_mul_sq :
    Tendsto (fun m : ℕ ↦ ((16 * m : ℕ) : ℝ) ^ 2) atTop atTop :=
  (tendsto_pow_atTop two_ne_zero).comp
    (tendsto_natCast_atTop_atTop.comp (tendsto_id.const_mul_atTop' (by norm_num)))

/-- **The final deduction** (proved): the three estimates imply the irrationality of
`ψ₁(s) - π²/2`. -/
theorem irrational_trigamma_sub_of_lownerEstimates {s : ℝ} (h : LownerEstimates s) :
    Irrational (trigamma s - π ^ 2 / 2) := by
  refine irrational_of_rat_value_decay arithmetic_lt_decay Admissible
    (fun m c y ↦ (separatedLownerDet s m c).eval y) tendsto_sixteen_mul_sq ?_ h.decay
  intro r
  refine Eventually.frequently ?_
  filter_upwards [h.denominator r, eventually_gt_atTop 0] with m hden hm
  obtain ⟨c, hc, hne⟩ := h.nonvanishing r m hm
  obtain ⟨q, hq, hlog⟩ := hden c hc
  refine ⟨c, hc, q, ?_, hq, hlog⟩
  rintro rfl
  exact hne (by simpa using hq)

/-- **Conditional** (on the unproved `LownerEstimates`): `ψ₁(1/5) - π²/2` is irrational. -/
theorem irrational_xi_one_of_estimates (h : LownerEstimates (1 / 5)) :
    Irrational (trigamma (1 / 5) - π ^ 2 / 2) :=
  irrational_trigamma_sub_of_lownerEstimates h

/-- **Conditional** (on the unproved `LownerEstimates`): `ψ₁(2/5) - π²/2` is irrational. -/
theorem irrational_xi_two_of_estimates (h : LownerEstimates (2 / 5)) :
    Irrational (trigamma (2 / 5) - π ^ 2 / 2) :=
  irrational_trigamma_sub_of_lownerEstimates h

/-- **Conditional** (on the unproved `LownerEstimates`): `ψ₁(3/5) - π²/2` is irrational. -/
theorem irrational_xi_three_of_estimates (h : LownerEstimates (3 / 5)) :
    Irrational (trigamma (3 / 5) - π ^ 2 / 2) :=
  irrational_trigamma_sub_of_lownerEstimates h

/-- **Conditional** (on the unproved `LownerEstimates`): `ψ₁(4/5) - π²/2` is irrational. -/
theorem irrational_xi_four_of_estimates (h : LownerEstimates (4 / 5)) :
    Irrational (trigamma (4 / 5) - π ^ 2 / 2) :=
  irrational_trigamma_sub_of_lownerEstimates h

end AxiomForge.Trigamma
