import AxiomForge.AF0004.IrrationalityCriterion
import AxiomForge.AF0004.Construction

/-!
# Conditional irrationality of `χ₂(±a/q)` and `Ti₂(±a/q)`, `a ∈ {3, 4, 5, 8}`

The candidate proofs reduce the irrationality of `ξ = targetValue σ (q / a)` (that is
`χ₂(a/q)` for `σ = 1` and `Ti₂(a/q)` for `σ = -1`) to three estimates on the explicit
normalized pencils `T_n = halfHankelDet σ (q / a) p n` of `Construction`:

1. an **arithmetic estimate**: `liminf h⁻² log cont(T_n) ≥ A`;
2. an **archimedean estimate**: `limsup h⁻² log |T_n(ξ)| ≤ B` with `B < A`;
3. **prime-index nonvanishing**: for each rational `r`, `T_p(r) ≠ 0` for all large primes.

`HalfIntegerEstimates σ y p a d` records these statements, in the eventual form implied by
the `liminf`/`limsup` claims. **Its fields are unproved candidate estimates**; the theorems
`*_of_estimates` prove only the final deduction and are not formalizations of the main
theorems.

## Rows and rates (per `h ²`) taken from the candidate proofs

Each row `(a, σ)` has a threshold `q₀`, pole ratio `(H, K') ∈ {(6, 7), (4, 5)}` and, at `q₀`,
certified bounds `A(q₀) ≥ content` and `B(q₀) ≤ decay` (rounded in the safe direction, see
`rowData`). For `q ≥ q₀` the manuscript derives `A(q) ≥ A(q₀) + s log(q/q₀)` with
`s = 1/3 - (8/3) D`, `D = (2 - K'/H) ² / 4` (`s = -7/54` for `7/6`, `s = -1/24` for `5/4`) and
`B(q) ≤ B(q₀) - (1/2) log(q/q₀)`. For `a = 4, 8` both signs use the constants of `σ = -1`.

## Unconditional finite certificates (by `norm_num`/`nlinarith`)

* `rowData_margin`: `decay < content` in each of the six rows;
* `contentRate_gt_decayRate`: the margin for every `q ≥ q₀`;
* the exact constants `c₂` of the manuscript: `oddConst_*`, `evenConst_two_ge`,
  `evenConst_three_ge`.

## Main results

* `irrational_targetValue_of_halfIntegerEstimates`: the general conditional deduction.
* `irrational_legendreChi_div_of_estimates`, `irrational_inverseTangentIntegral_div_of_estimates`
  and the negative-argument versions: the six rows.
-/

namespace AxiomForge.LegendreChiGeneral

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

/-- Data of one row of the main theorem: threshold, pole ratio `(H, K')`, and the rounded
certified rates `content ≤ A(q₀)`, `decay ≥ B(q₀)` per `h ^ 2`. -/
structure RowData where
  /-- The threshold `q₀`. -/
  q0 : ℕ
  /-- Dimension multiplier `H`. -/
  H : ℕ
  /-- Pole multiplier `K'`. -/
  K : ℕ
  /-- Rounded lower bound of the arithmetic constant at `q₀`. -/
  content : ℝ
  /-- Rounded upper bound of the size exponent at `q₀`. -/
  decay : ℝ

/-- The six rows `(a, σ)`; for `a = 4, 8` both signs use the constants of `σ = -1`.
Values of any other `a` are junk. -/
noncomputable def rowData (a : ℕ) (σ : ℝ) : RowData :=
  if a = 3 then
    (if σ = 1 then ⟨131, 6, 7, -3.17388, -3.18782⟩ else ⟨257, 4, 5, -3.54128, -3.54638⟩)
  else if a = 4 then ⟨995, 4, 5, -4.08176, -4.08345⟩
  else if a = 5 then
    (if σ = 1 then ⟨829, 4, 5, -3.87826, -3.87955⟩ else ⟨1609, 4, 5, -4.21197, -4.21267⟩)
  else ⟨12061, 4, 5, -4.98534, -4.98609⟩

/-- Rows are the numerators `3, 4, 5, 8`. -/
def IsRowNumerator (a : ℕ) : Prop := a = 3 ∨ a = 4 ∨ a = 5 ∨ a = 8

/-- The parameters `(H, K')` of a row. -/
noncomputable def parameters (a : ℕ) (σ : ℝ) : Parameters :=
  ⟨(rowData a σ).H, (rowData a σ).K⟩

/-- Slope `s = 1/3 - (8/3) D` of the arithmetic constant in `log q`:
`-7/54` for `κ = 7/6` and `-1/24` for `κ = 5/4`. -/
noncomputable def slope (a : ℕ) (σ : ℝ) : ℝ := if (rowData a σ).H = 6 then -7 / 54 else -1 / 24

/-- Content rate at `q ≥ q₀`. -/
noncomputable def contentRate (a : ℕ) (σ : ℝ) (q : ℕ) : ℝ :=
  (rowData a σ).content + slope a σ * Real.log (q / (rowData a σ).q0)

/-- Decay rate at `q ≥ q₀`. -/
noncomputable def decayRate (a : ℕ) (σ : ℝ) (q : ℕ) : ℝ :=
  (rowData a σ).decay - Real.log (q / (rowData a σ).q0) / 2

/-- The six strict margins, with the rounded rates (kernel-checked by `norm_num`). -/
theorem rowData_margin {a : ℕ} (ha : IsRowNumerator a) (σ : ℝ) :
    (rowData a σ).decay < (rowData a σ).content := by
  unfold rowData
  rcases ha with rfl | rfl | rfl | rfl <;> split_ifs <;> norm_num

/-- The thresholds of the main theorem. -/
theorem rowData_threshold :
    (rowData 3 1).q0 = 131 ∧ (rowData 3 (-1)).q0 = 257 ∧ (rowData 4 1).q0 = 995 ∧
      (rowData 4 (-1)).q0 = 995 ∧ (rowData 5 1).q0 = 829 ∧ (rowData 5 (-1)).q0 = 1609 ∧
        (rowData 8 1).q0 = 12061 ∧ (rowData 8 (-1)).q0 = 12061 := by
  unfold rowData
  norm_num

theorem slope_nonneg_margin (a : ℕ) (σ : ℝ) : -1 / 2 < slope a σ := by
  unfold slope
  split_ifs <;> norm_num

/-- The margin for every `q ≥ q₀`: `decayRate < contentRate`. -/
theorem decayRate_lt_contentRate {a : ℕ} (ha : IsRowNumerator a) {σ : ℝ} {q : ℕ}
    (hq : (rowData a σ).q0 ≤ q) : decayRate a σ q < contentRate a σ q := by
  have hpos : (0 : ℝ) < ((rowData a σ).q0 : ℝ) := by
    have : 0 < (rowData a σ).q0 := by
      unfold rowData
      split_ifs <;> norm_num
    exact_mod_cast this
  have hlog : 0 ≤ Real.log (q / (rowData a σ).q0) := by
    apply Real.log_nonneg
    rw [le_div_iff₀ hpos]
    exact_mod_cast (by omega : 1 * (rowData a σ).q0 ≤ q)
  have h1 := rowData_margin ha σ
  have h2 := slope_nonneg_margin a σ
  unfold decayRate contentRate
  nlinarith

/-- The estimates assumed for the row `(a, σ)` at the denominator `q`, with the rates of the
manuscript. -/
def FamilyEstimates (a : ℕ) (σ : ℝ) (q : ℕ) : Prop :=
  HalfIntegerEstimates σ ((q : ℝ) / a) (parameters a σ) (contentRate a σ q) (decayRate a σ q)

theorem irrational_targetValue_of_familyEstimates {a : ℕ} (ha : IsRowNumerator a) {σ : ℝ}
    {q : ℕ} (hq : (rowData a σ).q0 ≤ q) (h : FamilyEstimates a σ q) :
    Irrational (targetValue σ ((q : ℝ) / a)) := by
  refine irrational_targetValue_of_halfIntegerEstimates ?_ (decayRate_lt_contentRate ha hq) h
  unfold parameters rowData
  rcases ha with rfl | rfl | rfl | rfl <;> split_ifs <;> norm_num

/-- **Conditional** (on the unproved `FamilyEstimates a 1 q`): `χ₂(a/q)` is irrational for
`a ∈ {3, 4, 5, 8}` and `q ≥ q₀`. Oddness and coprimality of `q` are not used by the deduction;
they matter only for the unproved estimates. -/
theorem irrational_legendreChi_div_of_estimates {a : ℕ} (ha : IsRowNumerator a) {q : ℕ}
    (hq : (rowData a 1).q0 ≤ q) (h : FamilyEstimates a 1 q) :
    Irrational (legendreChi (a / q)) := by
  rw [← targetValue_one]
  exact irrational_targetValue_of_familyEstimates ha hq h

/-- **Conditional** (on `FamilyEstimates a (-1) q`): `Ti₂(a/q)` is irrational. -/
theorem irrational_inverseTangentIntegral_div_of_estimates {a : ℕ} (ha : IsRowNumerator a)
    {q : ℕ} (hq : (rowData a (-1)).q0 ≤ q) (h : FamilyEstimates a (-1) q) :
    Irrational (inverseTangentIntegral (a / q)) := by
  rw [← targetValue_neg_one]
  exact irrational_targetValue_of_familyEstimates ha hq h

/-- **Conditional** (on `FamilyEstimates a 1 q`): `χ₂(-a/q)` is irrational. -/
theorem irrational_legendreChi_neg_div_of_estimates {a : ℕ} (ha : IsRowNumerator a) {q : ℕ}
    (hq : (rowData a 1).q0 ≤ q) (h : FamilyEstimates a 1 q) :
    Irrational (legendreChi (-a / q)) := by
  rw [neg_div, irrational_legendreChi_neg_iff]
  exact irrational_legendreChi_div_of_estimates ha hq h

/-- **Conditional** (on `FamilyEstimates a (-1) q`): `Ti₂(-a/q)` is irrational. -/
theorem irrational_inverseTangentIntegral_neg_div_of_estimates {a : ℕ} (ha : IsRowNumerator a)
    {q : ℕ} (hq : (rowData a (-1)).q0 ≤ q) (h : FamilyEstimates a (-1) q) :
    Irrational (inverseTangentIntegral (-a / q)) := by
  rw [neg_div, irrational_inverseTangentIntegral_neg_iff]
  exact irrational_inverseTangentIntegral_div_of_estimates ha hq h

/-! ### The exact arithmetic constants `c₂` -/

/-- `c₂ = 2 (κ - 1) + 2 D` for `a` odd, `σ = 1`, `κ = 7/6`. -/
theorem oddConst_plus_seven_sixths :
    2 * ((7 : ℚ) / 6 - 1) + 2 * ((2 - 7 / 6) ^ 2 / 4) = 49 / 72 := by norm_num

/-- `c₂ = 2 (κ - 1) + 2 D` for `a` odd, `σ = 1`, `κ = 5/4`. -/
theorem oddConst_plus_five_fourths :
    2 * ((5 : ℚ) / 4 - 1) + 2 * ((2 - 5 / 4) ^ 2 / 4) = 25 / 32 := by norm_num

/-- `c₂ = κ - 1` for `a` odd, `σ = -1`, `κ = 5/4`: `1/4`. -/
theorem oddConst_minus_five_fourths : ((5 : ℚ) / 4 - 1) = 1 / 4 := by norm_num

/-- The quadratic `f_e(x) = 2 (κ - 1) - 2 (e + 1) κ x + (e + 2) x ² + (e/2 + 2) (1 - x) ²`. -/
def evenProfile (e : ℚ) (κ : ℚ) (x : ℚ) : ℚ :=
  2 * (κ - 1) - 2 * (e + 1) * κ * x + (e + 2) * x ^ 2 + (e / 2 + 2) * (1 - x) ^ 2

/-- `C₂(5/4) = -337/112` (minimum of `f₂` at `x = 27/28`). -/
theorem evenConst_two_ge (x : ℚ) : -337 / 112 ≤ evenProfile 2 (5 / 4) x := by
  unfold evenProfile
  nlinarith [sq_nonneg (x - 27 / 28)]

theorem evenConst_two_min : evenProfile 2 (5 / 4) (27 / 28) = -337 / 112 := by
  norm_num [evenProfile]

/-- `C₃(5/4) = -9/2 = -e (2κ - 1)` (minimum of `f₃` at `x = 1`). -/
theorem evenConst_three_ge (x : ℚ) : -9 / 2 ≤ evenProfile 3 (5 / 4) x := by
  unfold evenProfile
  nlinarith [sq_nonneg (x - 1)]

theorem evenConst_three_min : evenProfile 3 (5 / 4) 1 = -9 / 2 := by
  norm_num [evenProfile]

end AxiomForge.LegendreChiGeneral
