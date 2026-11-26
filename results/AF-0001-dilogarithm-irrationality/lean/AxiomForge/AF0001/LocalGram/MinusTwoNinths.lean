import Mathlib.LinearAlgebra.Matrix.Block
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum

/-!
# Local Gram determinants for `λ = -2/9`

Kernel-checked finite certificate for the prime-index nonvanishing argument of the
manuscript for `Li₂(-2/9)`. The diagonal blocks of the reduced Gram matrix are, up to nonzero
constants, the `4 × 4` Hankel matrices `H_b = (V(u ^ (i + j) w_b(u)))_{i, j < 4}`,
`b ∈ {0, 1}`, where `V` is the rational functional with
`V(u ^ k) = k M_(k-1)(λ)` (`k ≥ 1`), `V(1) = 0`, `V((u + l)⁻¹) = λ ^ (-l) τ_l(λ)`, and the
local weights are
* `w_1(u) = u ^ 2 / ((u + 1) ⋯ (u + 6))` (nonzero residue classes),
* `w_0(u) = u (u + 1) ^ 2 / ((u + 2) ⋯ (u + 7))` (zero residue class).

The rational entries were computed by the exact recomputation script distributed with the
certificates of this contribution, with two independent methods (exact Euler-operator
moments with flint partial fractions, and a 120-digit numerical evaluation of
`∑_u λ ^ u R'(u) + Li₂(λ) ∑_l r_l λ ^ (-l)`); both
determinants agree with the values printed in the manuscript. Here the kernel checks an exact
factorization `H_b = L_b U_b` (`L_b` unit lower triangular, `U_b` upper triangular), hence
`det H_b = ∏ (U_b)_ii`, and the nonvanishing of the determinant.

The link between these rational matrices and the analytic functional (the identification of
the reduced diagonal blocks) is part of the unformalized prime-index argument.

## Main results

* `det_gramOne`, `det_gramZero`: the exact values of `det H_1` and `det H_0`;
* `det_gramOne_ne_zero`, `det_gramZero_ne_zero`: both are nonzero.
-/

namespace AxiomForge.Dilogarithm.LocalGram.MinusTwoNinths

/-- The local moments `V(u ^ k w_1(u))`, `k < 7`, with
`w_1(u) = u ^ 2 / ((u + 1) ⋯ (u + 6))`. -/
def momentsOne : Fin 7 → ℚ := ![
  1592281 / 1500,
  -4265093 / 750,
  186209839 / 6000,
  -515941517 / 3000,
  5791441579 / 6000,
  -180688065607 / 33000,
  22751640084499 / 726000]

/-- The local Hankel Gram matrix `H_1 = (V(u ^ (i + j) w_1(u)))_{i, j < 4}`. -/
def gramOne : Matrix (Fin 4) (Fin 4) ℚ :=
  Matrix.of fun i j ↦ momentsOne ⟨i.val + j.val, by omega⟩

/-- Unit lower triangular factor of `H_1`. -/
def lowerOne : Matrix (Fin 4) (Fin 4) ℚ :=
  Matrix.of ![
  ![1, 0, 0, 0],
  ![-8530186 / 1592281, 1, 0, 0],
  ![186209839 / 6369124, -48571722276 / 4837418555, 1, 0],
  ![-515941517 / 3184562, 372842825411 / 4837418555, -2452074218598382 / 174790618817397, 1]]

/-- Upper triangular factor of `H_1`. -/
def upperOne : Matrix (Fin 4) (Fin 4) ℚ :=
  Matrix.of ![
  ![1592281 / 1500, -4265093 / 750, 186209839 / 6000, -515941517 / 3000],
  ![0, 14512255665 / 25476496, -36428791707 / 6369124, 1118528476233 / 25476496],
  ![0, 0, 143010506305143 / 309594787520, -11034333983692719 / 1702771331360],
  ![0, 0, 0, 248468668194294012 / 640898935663789]]

theorem gramOne_eq_mul : gramOne = lowerOne * upperOne := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [gramOne, lowerOne, upperOne, momentsOne, Matrix.mul_apply, Fin.sum_univ_succ]

theorem det_lowerOne : lowerOne.det = 1 := by
  rw [Matrix.det_of_isLowerTriangular]
  · simp [lowerOne, Fin.prod_univ_succ]
  · intro i j hij
    rw [OrderDual.toDual_lt_toDual] at hij
    fin_cases i <;> fin_cases j <;> simp_all [lowerOne]

theorem det_upperOne :
    upperOne.det = 1677163510311484581 / 15488000 := by
  rw [Matrix.det_of_isUpperTriangular]
  · norm_num [upperOne, Fin.prod_univ_succ]
  · intro i j hij
    fin_cases i <;> fin_cases j <;> simp_all [upperOne]

/-- The exact value of `det H_1` (manuscript value, recomputed independently):
`1677163510311484581/15488000`. -/
theorem det_gramOne :
    gramOne.det = 1677163510311484581 / 15488000 := by
  rw [gramOne_eq_mul, Matrix.det_mul, det_lowerOne, det_upperOne, one_mul]

theorem det_gramOne_ne_zero : gramOne.det ≠ 0 := by
  rw [det_gramOne]
  norm_num

/-- The local moments `V(u ^ k w_0(u))`, `k < 7`, with
`w_0(u) = u (u + 1) ^ 2 / ((u + 2) ⋯ (u + 7))`. -/
def momentsZero : Fin 7 → ℚ := ![
  3826292501 / 126000,
  -782461353 / 4000,
  5097731721 / 4000,
  -33537254547 / 4000,
  2447527006119 / 44000,
  -179923804004163 / 484000,
  13310215147027551 / 5324000]

/-- The local Hankel Gram matrix `H_0 = (V(u ^ (i + j) w_0(u)))_{i, j < 4}`. -/
def gramZero : Matrix (Fin 4) (Fin 4) ℚ :=
  Matrix.of fun i j ↦ momentsZero ⟨i.val + j.val, by omega⟩

/-- Unit lower triangular factor of `H_0`. -/
def lowerZero : Matrix (Fin 4) (Fin 4) ℚ :=
  Matrix.of ![
  ![1, 0, 0, 0],
  ![-49295065239 / 7652585002, 1, 0, 0],
  ![321157098423 / 7652585002, -71382311960183437 / 5857891589507201, 1, 0],
  ![-2112847036461 / 7652585002,
    7259677331623510909 / 64436807484579211,
    -1515339121026968789757 / 88090536083435274664,
    1]]

/-- Upper triangular factor of `H_0`. -/
def upperZero : Matrix (Fin 4) (Fin 4) ℚ :=
  Matrix.of ![
  ![3826292501 / 126000, -782461353 / 4000, 5097731721 / 4000, -33537254547 / 4000],
  ![0,
    17573674768521603 / 1224413600320,
    -214146935880550311 / 1224413600320,
    21779031994870532727 / 13468549603520],
  ![0,
    0,
    648666674796205204344 / 64436807484579211,
    -122742468803184471970317 / 708804882330371321],
  ![0, 0, 0, 76009050225296606651493375 / 10658954866095668234344]]

theorem gramZero_eq_mul : gramZero = lowerZero * upperZero := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [gramZero, lowerZero, upperZero, momentsZero, Matrix.mul_apply, Fin.sum_univ_succ]

theorem det_lowerZero : lowerZero.det = 1 := by
  rw [Matrix.det_of_isLowerTriangular]
  · simp [lowerZero, Fin.prod_univ_succ]
  · intro i j hij
    rw [OrderDual.toDual_lt_toDual] at hij
    fin_cases i <;> fin_cases j <;> simp_all [lowerZero]

theorem det_upperZero :
    upperZero.det = 16417954848664067036722569 / 524733440 := by
  rw [Matrix.det_of_isUpperTriangular]
  · norm_num [upperZero, Fin.prod_univ_succ]
  · intro i j hij
    fin_cases i <;> fin_cases j <;> simp_all [upperZero]

/-- The exact value of `det H_0` (manuscript value, recomputed independently):
`16417954848664067036722569/524733440`. -/
theorem det_gramZero :
    gramZero.det = 16417954848664067036722569 / 524733440 := by
  rw [gramZero_eq_mul, Matrix.det_mul, det_lowerZero, det_upperZero, one_mul]

theorem det_gramZero_ne_zero : gramZero.det ≠ 0 := by
  rw [det_gramZero]
  norm_num

end AxiomForge.Dilogarithm.LocalGram.MinusTwoNinths
