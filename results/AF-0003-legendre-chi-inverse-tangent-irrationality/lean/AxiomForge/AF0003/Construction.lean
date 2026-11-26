import Mathlib.Algebra.Polynomial.Div
import Mathlib.Algebra.Polynomial.Derivative
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import AxiomForge.AF0003.Definitions

/-!
# The half-integer Hankel pencils of the Legendre chi construction

This file defines explicitly, without any hypothesis, the polynomials `T_n(X)` of the
candidate proofs, so that the unproved estimates of `MainTheorems` concern concrete objects.

Fix an odd `q`, a sign `σ = ±1`, `y = q / 2`, `w = σ / y ²` and
`ξ = ∑_{j ≥ 0} σ ^ j y ^ (-2 j - 1) / (2 j + 1) ^ 2`, which is `χ₂(2/q)` for `σ = 1` and
`Ti₂(2/q)` for `σ = -1` (`targetValue_one`, `targetValue_neg_one`). Let
`τ_k = ∑_{j=0}^{k} σ ^ j y ^ (-2 j - 1) / (2 j + 1) ^ 2`, `x_k = -k - 1/2`,
`D_K(u) = ∏_{k < K} (u - x_k)` and `N_A(u) = ∏_{j=1}^{A} (u - j) ^ 2`. The affine functional
`μ_X` is `μ_X(R) = ∑_{m ≥ 1} w ^ m R'(m)` on polynomials and
`μ_X(1 / (u - x_k)) = -4 σ ^ k y ^ (2 k + 1) (X - τ_k)` on simple poles. With
`φ(u) = u N_A(u) / D_K(u)`, `h = H n`, `K = K' n`, `A = A' n`,
`T_n(X) = (K! / (A!) ^ 2) ^ h / ∏_{i < h} (i!) ^ 2 * det (μ_X(φ(u) u ^ (i + j)))_{i, j < h}`.
The manuscripts use `(H, K', A') = (6, 7, 0)` for `q ≥ 83` (then `φ = u / D_K`) and
`(40, 49, 2)` for `q = 81`.

## Main definitions

* `targetValue σ y`, `chiPartial σ y k` (the partial sums `τ_k`), `geomMoment w k`;
* `halfPoly K = D_K`, `zeroBandPoly A = N_A`;
* `halfFunctional σ y K N = μ_X(N / D_K)` as a polynomial in `X`;
* `Parameters`, `halfHankelDet σ y p n` (the polynomial `T_n`).

## Main results

* `targetValue_one`, `targetValue_neg_one`: statement fidelity of `ξ`;
* `natDegree_halfHankelDet_le`: `deg T_n ≤ h`.
-/

namespace AxiomForge.LegendreChi

open Polynomial Finset

/-- `ξ = ∑_{j ≥ 0} σ ^ j y ^ (-2 j - 1) / (2 j + 1) ^ 2`. -/
noncomputable def targetValue (σ y : ℝ) : ℝ :=
  ∑' j : ℕ, σ ^ j * (y ^ (2 * j + 1))⁻¹ / ((2 * j + 1 : ℕ) : ℝ) ^ 2

/-- With `σ = 1` and `y = q / 2`, `ξ = χ₂(2/q)`. -/
theorem targetValue_one (q : ℝ) : targetValue 1 (q / 2) = legendreChi (2 / q) := by
  rw [targetValue, legendreChi]
  congr 1
  funext j
  rw [one_pow, one_mul, ← inv_pow, inv_div]

/-- With `σ = -1` and `y = q / 2`, `ξ = Ti₂(2/q)`. -/
theorem targetValue_neg_one (q : ℝ) :
    targetValue (-1) (q / 2) = inverseTangentIntegral (2 / q) := by
  rw [targetValue, inverseTangentIntegral]
  congr 1
  funext j
  rw [← inv_pow, inv_div]

/-- The partial sums `τ_k = ∑_{j=0}^{k} σ ^ j y ^ (-2 j - 1) / (2 j + 1) ^ 2`. -/
noncomputable def chiPartial (σ y : ℝ) (k : ℕ) : ℝ :=
  ∑ j ∈ range (k + 1), σ ^ j * (y ^ (2 * j + 1))⁻¹ / ((2 * j + 1 : ℕ) : ℝ) ^ 2

/-- The geometric moments `M_k(w) = ∑_{m ≥ 1} w ^ m m ^ k`. -/
noncomputable def geomMoment (w : ℝ) (k : ℕ) : ℝ :=
  ∑' m : ℕ, w ^ (m + 1) * ((m : ℝ) + 1) ^ k

/-- `D_K(u) = ∏_{k < K} (u + k + 1/2)`. -/
noncomputable def halfPoly (K : ℕ) : ℝ[X] := ∏ k ∈ range K, (X + C ((k : ℝ) + 1 / 2))

/-- `N_A(u) = ∏_{j=1}^{A} (u - j) ^ 2`. -/
noncomputable def zeroBandPoly (A : ℕ) : ℝ[X] := ∏ j ∈ range A, (X - C ((j : ℝ) + 1)) ^ 2

/-- The affine functional `μ_X` applied to `N / D_K`, as a polynomial in `X`. Writing
`N = Q D_K + ρ` with `deg ρ < K`, the polynomial part contributes
`μ(Q) = ∑_{m ≥ 1} m Q_m M_{m-1}(w)` (`w = σ / y ²`) and the residue
`r_k = ρ(x_k) / D_K'(x_k)` at `x_k = -k - 1/2` contributes
`r_k (-4 σ ^ k y ^ (2 k + 1)) (X - τ_k)`. -/
noncomputable def halfFunctional (σ y : ℝ) (K : ℕ) (N : ℝ[X]) : ℝ[X] :=
  C (∑ m ∈ range ((N /ₘ halfPoly K).natDegree + 1),
      (m : ℝ) * (N /ₘ halfPoly K).coeff m * geomMoment (σ / y ^ 2) (m - 1)) +
    ∑ k ∈ range K,
      C ((N %ₘ halfPoly K).eval (-((k : ℝ) + 1 / 2)) /
          (derivative (halfPoly K)).eval (-((k : ℝ) + 1 / 2)) *
            (-4 * σ ^ k * y ^ (2 * k + 1))) *
        (X - C (chiPartial σ y k))

/-- The parameters `(H, K', A')`: dimension `h = H n`, `K = K' n` half-integer poles and
`A = A' n` double zeros at `1, …, A`. -/
structure Parameters where
  /-- Dimension multiplier: `h = H n`. -/
  H : ℕ
  /-- Pole multiplier: `K = K' n`. -/
  K : ℕ
  /-- Double-zero multiplier: `A = A' n`. -/
  A : ℕ

/-- The Hankel matrix `(μ_X(u ^ (i + j) φ(u)))_{i, j < h}`, `φ = u N_A / D_K`. -/
noncomputable def halfHankelMatrix (σ y : ℝ) (h K A : ℕ) : Matrix (Fin h) (Fin h) ℝ[X] :=
  Matrix.of fun i j ↦ halfFunctional σ y K (X ^ (i.val + j.val) * X * zeroBandPoly A)

/-- The normalized determinant
`T_n(X) = (K! / (A!) ^ 2) ^ h / ∏_{i < h} (i!) ^ 2 * det (μ_X(u ^ (i + j) φ(u)))`. -/
noncomputable def halfHankelDet (σ y : ℝ) (p : Parameters) (n : ℕ) : ℝ[X] :=
  C ((((p.K * n).factorial : ℝ) / ((p.A * n).factorial : ℝ) ^ 2) ^ (p.H * n) /
      ∏ i ∈ range (p.H * n), ((i.factorial : ℝ)) ^ 2) *
    (halfHankelMatrix σ y (p.H * n) (p.K * n) (p.A * n)).det

theorem natDegree_halfFunctional_le (σ y : ℝ) (K : ℕ) (N : ℝ[X]) :
    (halfFunctional σ y K N).natDegree ≤ 1 := by
  unfold halfFunctional
  refine natDegree_add_le_of_degree_le ((natDegree_C _).trans_le zero_le_one) ?_
  refine natDegree_sum_le_of_forall_le _ _ fun l _ ↦ ?_
  refine (natDegree_C_mul_le _ _).trans ?_
  exact (natDegree_sub_le _ _).trans (by simp)

/-- A determinant of a matrix with affine entries has degree at most the dimension. -/
theorem natDegree_det_le_of_natDegree_le_one {ι : Type*} [Fintype ι] [DecidableEq ι]
    (M : Matrix ι ι ℝ[X]) (hM : ∀ i j, (M i j).natDegree ≤ 1) :
    M.det.natDegree ≤ Fintype.card ι := by
  rw [Matrix.det_apply']
  refine natDegree_sum_le_of_forall_le _ _ fun σ _ ↦ ?_
  refine natDegree_mul_le.trans ?_
  rw [natDegree_intCast, zero_add]
  refine (natDegree_prod_le _ _).trans ?_
  calc ∑ i, (M (σ i) i).natDegree ≤ ∑ _i : ι, 1 := sum_le_sum fun i _ ↦ hM _ _
    _ = Fintype.card ι := by simp

/-- `deg T_n ≤ h = H n`. -/
theorem natDegree_halfHankelDet_le (σ y : ℝ) (p : Parameters) (n : ℕ) :
    (halfHankelDet σ y p n).natDegree ≤ p.H * n := by
  refine (natDegree_C_mul_le _ _).trans ?_
  refine (natDegree_det_le_of_natDegree_le_one _ fun i j ↦ ?_).trans (by simp)
  exact natDegree_halfFunctional_le _ _ _ _

end AxiomForge.LegendreChi
