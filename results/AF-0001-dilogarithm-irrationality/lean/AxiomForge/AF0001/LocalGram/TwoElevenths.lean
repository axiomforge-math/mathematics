import Mathlib.LinearAlgebra.Matrix.Block
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum

/-!
# Local Gram determinants for `λ = 2/11`

Kernel-checked finite certificate for the prime-index nonvanishing argument of the
manuscript for `Li₂(2/11)`. The diagonal blocks of the reduced Gram matrix are, up to nonzero
constants, the `4 × 4` Hankel matrices `H_b = (V(u ^ (i + j) w_b(u)))_{i, j < 4}`,
`b ∈ {0, 1}`, where `V` is the rational functional with
`V(u ^ k) = k M_(k-1)(λ)` (`k ≥ 1`), `V(1) = 0`, `V((u + l)⁻¹) = λ ^ (-l) τ_l(λ)`, and the
local weights are
* `w_1(u) = u ^ 2 / ((u + 1) ⋯ (u + 5))` (nonzero residue classes),
* `w_0(u) = u (u + 1) ^ 2 / ((u + 2) ⋯ (u + 6))` (zero residue class).

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

namespace AxiomForge.Dilogarithm.LocalGram.TwoElevenths

/-- The local moments `V(u ^ k w_1(u))`, `k < 7`, with
`w_1(u) = u ^ 2 / ((u + 1) ⋯ (u + 5))`. -/
def momentsOne : Fin 7 → ℚ := ![
  43373 / 72,
  -1445543 / 432,
  1309517 / 72,
  -41968487 / 432,
  12282787 / 24,
  -3456085765 / 1296,
  26780823047 / 1944]

/-- The local Hankel Gram matrix `H_1 = (V(u ^ (i + j) w_1(u)))_{i, j < 4}`. -/
def gramOne : Matrix (Fin 4) (Fin 4) ℚ :=
  Matrix.of fun i j ↦ momentsOne ⟨i.val + j.val, by omega⟩

/-- Unit lower triangular factor of `H_1`. -/
def lowerOne : Matrix (Fin 4) (Fin 4) ℚ :=
  Matrix.of ![
  ![1, 0, 0, 0],
  ![-131413 / 23658, 1, 0, 0],
  ![119047 / 3943, -3603170880 / 370893013, 1, 0],
  ![-3815317 / 23658, 25877603173 / 370893013, -22834788161326 / 1823350685049, 1]]

/-- Upper triangular factor of `H_1`. -/
def upperOne : Matrix (Fin 4) (Fin 4) ℚ :=
  Matrix.of ![
  ![43373 / 72, -1445543 / 432, 1309517 / 72, -41968487 / 432],
  ![0, -4079823143 / 10220256, 137621110 / 35487, -284653634903 / 10220256],
  ![0, 0, 2228539726171 / 6676074234, -125591334887293 / 30042334053],
  ![0, 0, 0, -26788914444912598 / 147691405488969]]

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
    upperOne.det = 17828022563089333969 / 1224440064 := by
  rw [Matrix.det_of_isUpperTriangular]
  · norm_num [upperOne, Fin.prod_univ_succ]
  · intro i j hij
    fin_cases i <;> fin_cases j <;> simp_all [upperOne]

/-- The exact value of `det H_1` (manuscript value, recomputed independently):
`17828022563089333969/1224440064`. -/
theorem det_gramOne :
    gramOne.det = 17828022563089333969 / 1224440064 := by
  rw [gramOne_eq_mul, Matrix.det_mul, det_lowerOne, det_upperOne, one_mul]

theorem det_gramOne_ne_zero : gramOne.det ≠ 0 := by
  rw [det_gramOne]
  norm_num

/-- The local moments `V(u ^ k w_0(u))`, `k < 7`, with
`w_0(u) = u (u + 1) ^ 2 / ((u + 2) ⋯ (u + 6))`. -/
def momentsZero : Fin 7 → ℚ := ![
  -93817961 / 4320,
  60546343 / 432,
  -192875815 / 216,
  303977531 / 54,
  -11398295953 / 324,
  212181475231 / 972,
  -11780116211809 / 8748]

/-- The local Hankel Gram matrix `H_0 = (V(u ^ (i + j) w_0(u)))_{i, j < 4}`. -/
def gramZero : Matrix (Fin 4) (Fin 4) ℚ :=
  Matrix.of fun i j ↦ momentsZero ⟨i.val + j.val, by omega⟩

/-- Unit lower triangular factor of `H_0`. -/
def lowerZero : Matrix (Fin 4) (Fin 4) ℚ :=
  Matrix.of ![
  ![1, 0, 0, 0],
  ![-605463430 / 93817961, 1, 0, 0],
  ![3857516300 / 93817961, -3725955814061 / 322427773905, 1, 0],
  ![-24318202480 / 93817961,
    288585009819307 / 2901849965145,
    -8065168469509041 / 524197824977447,
    1]]

/-- Upper triangular factor of `H_0`. -/
def upperZero : Matrix (Fin 4) (Fin 4) ℚ :=
  Matrix.of ![
  ![-93817961 / 4320, 60546343 / 432, -192875815 / 216, 303977531 / 54],
  ![0, 13004586880835 / 1125815532, -450840653501381 / 3377446596, 34918786188136147 / 30397019364],
  ![0, 0, -63427936822271087 / 8705549895435, 108431709423399329 / 967283321715],
  ![0, 0, 0, 3442107187983053947148 / 1146420643225676589]]

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
    upperZero.det = 12598972834814973210048467 / 2295825120 := by
  rw [Matrix.det_of_isUpperTriangular]
  · norm_num [upperZero, Fin.prod_univ_succ]
  · intro i j hij
    fin_cases i <;> fin_cases j <;> simp_all [upperZero]

/-- The exact value of `det H_0` (manuscript value, recomputed independently):
`12598972834814973210048467/2295825120`. -/
theorem det_gramZero :
    gramZero.det = 12598972834814973210048467 / 2295825120 := by
  rw [gramZero_eq_mul, Matrix.det_mul, det_lowerZero, det_upperZero, one_mul]

theorem det_gramZero_ne_zero : gramZero.det ≠ 0 := by
  rw [det_gramZero]
  norm_num

end AxiomForge.Dilogarithm.LocalGram.TwoElevenths
