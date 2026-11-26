import Mathlib.LinearAlgebra.Matrix.Block
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum

/-!
# Local Gram determinants for `λ = -2/7`

Kernel-checked finite certificate for the prime-index nonvanishing argument of the
manuscript for `Li₂(-2/7)`. The diagonal blocks of the reduced Gram matrix are, up to nonzero
constants, the `5 × 5` Hankel matrices `H_b = (V(u ^ (i + j) w_b(u)))_{i, j < 5}`,
`b ∈ {0, 1}`, where `V` is the rational functional with
`V(u ^ k) = k M_(k-1)(λ)` (`k ≥ 1`), `V(1) = 0`, `V((u + l)⁻¹) = λ ^ (-l) τ_l(λ)`, and the
local weights are
* `w_1(u) = u ^ 2 / ((u + 1) ⋯ (u + 7))` (nonzero residue classes),
* `w_0(u) = u (u + 1) ^ 2 / ((u + 2) ⋯ (u + 8))` (zero residue class).

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

namespace AxiomForge.Dilogarithm.LocalGram.MinusTwoSevenths

/-- The local moments `V(u ^ k w_1(u))`, `k < 9`, with
`w_1(u) = u ^ 2 / ((u + 1) ⋯ (u + 7))`. -/
def momentsOne : Fin 9 → ℚ := ![
  24744013 / 69120,
  -1237994233 / 576000,
  843960831 / 64000,
  -142389087323 / 1728000,
  180741311569 / 345600,
  -5812535189419 / 1728000,
  37816400557957 / 1728000,
  -745432662972529 / 5184000,
  2963991646597177 / 3110400]

/-- The local Hankel Gram matrix `H_1 = (V(u ^ (i + j) w_1(u)))_{i, j < 5}`. -/
def gramOne : Matrix (Fin 5) (Fin 5) ℚ :=
  Matrix.of fun i j ↦ momentsOne ⟨i.val + j.val, by omega⟩

/-- Unit lower triangular factor of `H_1`. -/
def lowerOne : Matrix (Fin 5) (Fin 5) ℚ :=
  Matrix.of ![
  ![1, 0, 0, 0, 0],
  ![-530568957 / 88371475, 1, 0, 0, 0],
  ![3255277491 / 88371475, -4402583826956993 / 385640955118836, 1, 0, 0],
  ![-20341298189 / 88371475,
    19261838994595711 / 192820477559418,
    -277123079114571424162 / 17086332788099659285,
    1,
    0],
  ![25820187367 / 17674295,
    -305211270968567905 / 385640955118836,
    3062600501802961391141 / 17086332788099659285,
    -600320153254164669140417 / 29449812016204597733229,
    1]]

/-- Upper triangular factor of `H_1`. -/
def upperOne : Matrix (Fin 5) (Fin 5) ℚ :=
  Matrix.of ![
  ![24744013 / 69120,
    -1237994233 / 576000,
    843960831 / 64000,
    -142389087323 / 1728000,
    180741311569 / 345600],
  ![0,
    74985741273107 / 265114425000,
    -30818086788698951 / 9544119300000,
    134832872962169977 / 4772059650000,
    -427295779355995067 / 1908823860000],
  ![0,
    0,
    119604329516697614995 / 333193785222674304,
    -969930776900999984567 / 166596892611337152,
    21438203512620729737987 / 333193785222674304],
  ![0,
    0,
    0,
    160337865421558365436469 / 307553990185793867130,
    -29415687509454068787880433 / 2767985911672144804170],
  ![0, 0, 0, 0, 1674061030701102394131646558 / 2385434773312572416391549]]

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
    upperOne.det = 14067971871496713969085291850153 / 1057916215296000000 := by
  rw [Matrix.det_of_isUpperTriangular]
  · norm_num [upperOne, Fin.prod_univ_succ]
  · intro i j hij
    fin_cases i <;> fin_cases j <;> simp_all [upperOne]

/-- The exact value of `det H_1` (manuscript value, recomputed independently):
`14067971871496713969085291850153/1057916215296000000`. -/
theorem det_gramOne :
    gramOne.det = 14067971871496713969085291850153 / 1057916215296000000 := by
  rw [gramOne_eq_mul, Matrix.det_mul, det_lowerOne, det_upperOne, one_mul]

theorem det_gramOne_ne_zero : gramOne.det ≠ 0 := by
  rw [det_gramOne]
  norm_num

/-- The local moments `V(u ^ k w_0(u))`, `k < 9`, with
`w_0(u) = u (u + 1) ^ 2 / ((u + 2) ⋯ (u + 8))`. -/
def momentsZero : Fin 9 → ℚ := ![
  26537070947 / 3024000,
  -674482991 / 10800,
  10816480843 / 24000,
  -142227670627 / 43200,
  5250882345653 / 216000,
  -869747068183 / 4800,
  882490989264871 / 648000,
  -4008961891856551 / 388800,
  1374770458172832973 / 17496000]

/-- The local Hankel Gram matrix `H_0 = (V(u ^ (i + j) w_0(u)))_{i, j < 5}`. -/
def gramZero : Matrix (Fin 5) (Fin 5) ℚ :=
  Matrix.of fun i j ↦ momentsZero ⟨i.val + j.val, by omega⟩

/-- Unit lower triangular factor of `H_0`. -/
def lowerZero : Matrix (Fin 5) (Fin 5) ℚ :=
  Matrix.of ![
  ![1, 0, 0, 0, 0],
  ![-188855237480 / 26537070947, 1, 0, 0, 0],
  ![1362876586218 / 26537070947, -9934436848010500165 / 729521773826576761, 1, 0, 0],
  ![-9955936943890 / 26537070947,
    102874179152998174359 / 729521773826576761,
    -367338356268017945274475 / 18858832640236680226899,
    1,
    0],
  ![73512352839142 / 26537070947,
    -958523511764316763145 / 729521773826576761,
    1404057439109535830613379 / 5475144960068713614261,
    -2293627710403928164816880270 / 93010765447121471265298693,
    1]]

/-- Upper triangular factor of `H_0`. -/
def upperZero : Matrix (Fin 5) (Fin 5) ℚ :=
  Matrix.of ![
  ![26537070947 / 3024000,
    -674482991 / 10800,
    10816480843 / 24000,
    -142227670627 / 43200,
    5250882345653 / 216000],
  ![0,
    35746566917502261289 / 5732007324552000,
    -97357481110502901617 / 1146401464910400,
    1680278259498970181197 / 1910669108184000,
    -9393530415290304278821 / 1146401464910400],
  ![0,
    0,
    308027599790532443706017 / 43771306429594605660,
    -3599915891426575863689855 / 26262783857756763396,
    2132763250007384926701722701 / 1181825273599054352820],
  ![0,
    0,
    0,
    4557527506908952091999635957 / 509188481286390366126273,
    -3625411542251370325033133330 / 16425434880206140842783],
  ![0, 0, 0, 0, 2118220968500215827004458707303074 / 203414544032854657657208241591]]

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
    upperZero.det = 17800469908791563702231968746821382359 / 495898225920000000 := by
  rw [Matrix.det_of_isUpperTriangular]
  · norm_num [upperZero, Fin.prod_univ_succ]
  · intro i j hij
    fin_cases i <;> fin_cases j <;> simp_all [upperZero]

/-- The exact value of `det H_0` (manuscript value, recomputed independently):
`17800469908791563702231968746821382359/495898225920000000`. -/
theorem det_gramZero :
    gramZero.det = 17800469908791563702231968746821382359 / 495898225920000000 := by
  rw [gramZero_eq_mul, Matrix.det_mul, det_lowerZero, det_upperZero, one_mul]

theorem det_gramZero_ne_zero : gramZero.det ≠ 0 := by
  rw [det_gramZero]
  norm_num

end AxiomForge.Dilogarithm.LocalGram.MinusTwoSevenths
