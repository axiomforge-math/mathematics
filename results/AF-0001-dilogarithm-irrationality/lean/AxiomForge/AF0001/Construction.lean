import Mathlib.Algebra.Polynomial.Div
import Mathlib.Algebra.Polynomial.Derivative
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import AxiomForge.AF0001.Definitions

/-!
# The normalized Hankel determinants of the dilogarithm construction

This file defines, explicitly and without any hypothesis, the polynomials `Q̃_n(X)` of the
manuscripts, so that the unproved asymptotic estimates (see `MainTheorems`) are statements
about concrete objects.

For `λ` with `0 < |λ| < 1` and parameters `(H, C, B)` put `h = H n`, `K = C n`, `A = B n`,
`D_m(x) = ∏_{j=1}^m (x + j)`, `W_n = D_A ^ 3 / D_K`. The affine functional `Λ_X` on rational
functions with at most simple poles at `-1, …, -K` is
`Λ_X(x ^ k) = (k + 1) M_k(λ)` and `Λ_X((x + l)⁻¹) = l λ^{-l} (X - τ_l(λ))`, extended by
polynomial division and partial fractions, where `M_k(λ) = ∑_{u ≥ 1} λ ^ u u ^ k` and
`τ_l(λ) = ∑_{u=1}^{l} λ ^ u / u ^ 2`. Then
`Q_n(X) = det (Λ_X(W_n x ^ (i + j)))_{i, j < h}` and
`Q̃_n = (K! / (A!) ^ 3) ^ h / ∏_{i < h} (i!) ^ 2 * Q_n`.

## Main definitions

* `risingPoly m = ∏_{j=1}^{m} (X + j)`;
* `geomMoment λ k = ∑' u, λ ^ (u + 1) (u + 1) ^ k` (the moments `M_k(λ)`);
* `dilogPartial λ l = ∑_{u=1}^{l} λ ^ u / u ^ 2` (the partial sums `τ_l(λ)`);
* `affineFunctional λ K N = Λ_X(N / D_K)` as a polynomial in `X` (division with remainder by
  the monic `D_K`, residues `ρ(-l) / D_K'(-l)` of the proper part `ρ / D_K`);
* `hankelMatrix`, `Parameters`, `normalizedHankelDet` (the polynomial `Q̃_n`).

## Main results

* `natDegree_affineFunctional_le`: every entry is affine in `X`;
* `natDegree_normalizedHankelDet_le`: `deg Q̃_n ≤ h = H n`.

Every entry is computed over `ℝ`: the moments are defined as series, so no closed form of
`M_k(λ)` is assumed. Rationality of the coefficients is never used; the content hypothesis of
`MainTheorems` asks directly for a factorization `Q̃_n = c * P` with `P ∈ ℤ[X]`.
-/

namespace AxiomForge.Dilogarithm

open Polynomial Finset

/-- `D m = ∏_{j=1}^{m} (X + j)`. -/
noncomputable def risingPoly (m : ℕ) : ℝ[X] := ∏ j ∈ range m, (X + C ((j : ℝ) + 1))

theorem monic_risingPoly (m : ℕ) : (risingPoly m).Monic :=
  monic_prod_of_monic _ _ fun _ _ ↦ monic_X_add_C _

/-- The geometric moments `M_k(λ) = ∑_{u ≥ 1} λ ^ u u ^ k`. -/
noncomputable def geomMoment (lam : ℝ) (k : ℕ) : ℝ :=
  ∑' u : ℕ, lam ^ (u + 1) * ((u : ℝ) + 1) ^ k

/-- The partial sums `τ_l(λ) = ∑_{u=1}^{l} λ ^ u / u ^ 2` of the dilogarithm series. -/
noncomputable def dilogPartial (lam : ℝ) (l : ℕ) : ℝ := ∑ u ∈ range l, dilogTerm lam u

/-- The affine functional `Λ_X` applied to the rational function `N / D_K`, as a polynomial
in `X`. Writing `N = q D_K + ρ` with `deg ρ < K`, the proper part is
`ρ / D_K = ∑_{l=1}^{K} r_l / (x + l)` with `r_l = ρ(-l) / D_K'(-l)`, and
`Λ_X(N / D_K) = ∑_m (m + 1) q_m M_m(λ) + ∑_{l=1}^{K} r_l l λ^{-l} (X - τ_l(λ))`. -/
noncomputable def affineFunctional (lam : ℝ) (K : ℕ) (N : ℝ[X]) : ℝ[X] :=
  C (∑ m ∈ range ((N /ₘ risingPoly K).natDegree + 1),
      ((m : ℝ) + 1) * (N /ₘ risingPoly K).coeff m * geomMoment lam m) +
    ∑ l ∈ range K,
      C ((N %ₘ risingPoly K).eval (-((l : ℝ) + 1)) /
          (derivative (risingPoly K)).eval (-((l : ℝ) + 1)) * ((l : ℝ) + 1) *
            (lam ^ (l + 1))⁻¹) *
        (X - C (dilogPartial lam (l + 1)))

/-- The Hankel matrix `(Λ_X(x ^ (i + j) D_A(x) ^ 3 / D_K(x)))_{i, j < h}`. -/
noncomputable def hankelMatrix (lam : ℝ) (h A K : ℕ) : Matrix (Fin h) (Fin h) ℝ[X] :=
  Matrix.of fun i j ↦ affineFunctional lam K (X ^ (i.val + j.val) * risingPoly A ^ 3)

/-- The parameters `(H, C, B)` of a determinant family: dimension `h = H n`, `K = C n`
denominator factors and `A = B n` cubed numerator factors. -/
structure Parameters where
  /-- Dimension multiplier: `h = H n`. -/
  H : ℕ
  /-- Pole multiplier: `K = C n`. -/
  C : ℕ
  /-- Numerator multiplier: `A = B n`. -/
  B : ℕ

/-- The normalized determinant
`Q̃_n(X) = (K! / (A!) ^ 3) ^ h / ∏_{i < h} (i!) ^ 2 * det (Λ_X(W_n x ^ (i + j)))_{i, j < h}`. -/
noncomputable def normalizedHankelDet (lam : ℝ) (p : Parameters) (n : ℕ) : ℝ[X] :=
  C ((((p.C * n).factorial : ℝ) / ((p.B * n).factorial : ℝ) ^ 3) ^ (p.H * n) /
      ∏ i ∈ range (p.H * n), ((i.factorial : ℝ)) ^ 2) *
    (hankelMatrix lam (p.H * n) (p.B * n) (p.C * n)).det

theorem natDegree_affineFunctional_le (lam : ℝ) (K : ℕ) (N : ℝ[X]) :
    (affineFunctional lam K N).natDegree ≤ 1 := by
  unfold affineFunctional
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

/-- `deg Q̃_n ≤ h = H n`. -/
theorem natDegree_normalizedHankelDet_le (lam : ℝ) (p : Parameters) (n : ℕ) :
    (normalizedHankelDet lam p n).natDegree ≤ p.H * n := by
  refine (natDegree_C_mul_le _ _).trans ?_
  refine (natDegree_det_le_of_natDegree_le_one _ fun i j ↦ ?_).trans (by simp)
  exact natDegree_affineFunctional_le _ _ _

end AxiomForge.Dilogarithm
