import AxiomForge.AF0005.Definitions

/-!
# The quadratic units and the numbers `T_σ(n)`

For a sign `σ` and a trace `n` put `z = 2 / (n + √(n² + 4σ))` and
`T_σ(n) = ∑_{s ≥ 0} σ^s z^(2s+1) / (2s+1)²`.  For `σ = 1` this is `χ₂(z)` and for `σ = -1` it
is `Ti₂(z)`; `z` is a unit of norm `-σ` of `ℚ(√(n² + 4σ))`, a root of `z² + σ n z - σ`, and
`1/z - σ z = n`.

## Main results

* `unitValue_one`, `unitValue_neg_one`: `T_1(n) = χ₂(z)`, `T_{-1}(n) = Ti₂(z)`;
* `unitZ_pos`, `unitZ_lt_one`: `0 < z < 1` (for `n ≥ 1`, resp. `n ≥ 3`);
* `unitZ_quadratic`, `inv_unitZ_sub`: the quadratic relation and the trace relation.
-/

namespace AxiomForge.LegendreChi

open Real

/-- The unit `z_σ(n) = 2 / (n + √(n² + 4σ))`. -/
noncomputable def unitZ (σ : ℝ) (n : ℕ) : ℝ := 2 / (n + Real.sqrt ((n : ℝ) ^ 2 + 4 * σ))

/-- The number `T_σ(n) = ∑ σ^s z^(2s+1) / (2s+1)²`. -/
noncomputable def unitValue (σ : ℝ) (n : ℕ) : ℝ :=
  ∑' s : ℕ, σ ^ s * unitZ σ n ^ (2 * s + 1) / ((2 * s + 1 : ℕ) : ℝ) ^ 2

theorem unitValue_one (n : ℕ) : unitValue 1 n = legendreChi (unitZ 1 n) := by
  unfold unitValue legendreChi
  simp

theorem unitValue_neg_one (n : ℕ) :
    unitValue (-1) n = inverseTangentIntegral (unitZ (-1) n) := rfl

/-- Admissible parameters: `n ≥ 1` for `σ = 1`, `n ≥ 3` for `σ = -1`. -/
def Admissible (σ : ℝ) (n : ℕ) : Prop := (σ = 1 ∧ 1 ≤ n) ∨ (σ = -1 ∧ 3 ≤ n)

theorem sqrt_pos_of_admissible {σ : ℝ} {n : ℕ} (h : Admissible σ n) :
    0 < Real.sqrt ((n : ℝ) ^ 2 + 4 * σ) := by
  apply Real.sqrt_pos.mpr
  rcases h with ⟨rfl, hn⟩ | ⟨rfl, hn⟩
  · positivity
  · have : (3 : ℝ) ≤ n := by exact_mod_cast hn
    nlinarith

theorem unitZ_pos {σ : ℝ} {n : ℕ} (h : Admissible σ n) : 0 < unitZ σ n := by
  have hs := sqrt_pos_of_admissible h
  have hn : (1 : ℝ) ≤ n := by
    rcases h with ⟨_, hn⟩ | ⟨_, hn⟩ <;> exact_mod_cast (by omega : 1 ≤ n)
  unfold unitZ
  positivity

theorem unitZ_lt_one {σ : ℝ} {n : ℕ} (h : Admissible σ n) : unitZ σ n < 1 := by
  have hs := sqrt_pos_of_admissible h
  unfold unitZ
  rw [div_lt_one (by
    have hn : (1 : ℝ) ≤ n := by
      rcases h with ⟨_, hn⟩ | ⟨_, hn⟩ <;> exact_mod_cast (by omega : 1 ≤ n)
    positivity)]
  rcases h with ⟨rfl, hn⟩ | ⟨rfl, hn⟩
  · have h1 : (1 : ℝ) ≤ n := by exact_mod_cast hn
    have : (1 : ℝ) < Real.sqrt ((n : ℝ) ^ 2 + 4 * 1) := by
      rw [Real.lt_sqrt (by norm_num)]
      nlinarith
    linarith
  · have h3 : (3 : ℝ) ≤ n := by exact_mod_cast hn
    linarith

/-- `z² + σ n z - σ = 0`. -/
theorem unitZ_quadratic {σ : ℝ} {n : ℕ} (h : Admissible σ n) :
    unitZ σ n ^ 2 + σ * n * unitZ σ n - σ = 0 := by
  have hσ : σ ^ 2 = 1 := by rcases h with ⟨rfl, _⟩ | ⟨rfl, _⟩ <;> norm_num
  have hnn : 0 ≤ (n : ℝ) ^ 2 + 4 * σ := by
    rcases h with ⟨rfl, _⟩ | ⟨rfl, hn⟩
    · positivity
    · have : (3 : ℝ) ≤ n := by exact_mod_cast hn
      nlinarith
  have hs2 := Real.sq_sqrt hnn
  have hs := sqrt_pos_of_admissible h
  have hn : (1 : ℝ) ≤ n := by
    rcases h with ⟨_, hn⟩ | ⟨_, hn⟩ <;> exact_mod_cast (by omega : 1 ≤ n)
  have hden : (n : ℝ) + Real.sqrt ((n : ℝ) ^ 2 + 4 * σ) ≠ 0 := by positivity
  unfold unitZ
  field_simp
  nlinarith [hs2, hσ]

/-- The trace relation `1/z - σ z = n`. -/
theorem inv_unitZ_sub {σ : ℝ} {n : ℕ} (h : Admissible σ n) :
    (unitZ σ n)⁻¹ - σ * unitZ σ n = n := by
  have hz := unitZ_pos h
  have hq := unitZ_quadratic h
  have hσ : σ ^ 2 = 1 := by rcases h with ⟨rfl, _⟩ | ⟨rfl, _⟩ <;> norm_num
  have h1 : σ * unitZ σ n ^ 2 + n * unitZ σ n = 1 := by
    linear_combination σ * hq - (n * unitZ σ n - 1) * hσ
  field_simp
  nlinarith [h1]

end AxiomForge.LegendreChi
