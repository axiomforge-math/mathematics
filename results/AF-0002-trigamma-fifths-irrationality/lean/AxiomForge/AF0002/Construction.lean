import Mathlib.Algebra.Polynomial.Eval.Defs
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import AxiomForge.AF0002.Definitions

/-!
# The separated Löwner pencils of the trigamma construction

This file defines explicitly, without any hypothesis, the polynomials `P_sep,I(X)` of the
candidate proof, so that the unproved estimates of `MainTheorems` concern concrete objects.

Fix `s = k / 5` and `F(z) = ψ(z + s) - ψ(z + 1/2)`. The digamma recurrence gives the rational
node data
* `f_i = F(i) - F(0) = ∑_{j < i} ((j + s)⁻¹ - (j + 1/2)⁻¹)` (`nodeValue`),
* `d_i = F'(i) - F'(0) = ∑_{j < i} (-(j + s)⁻² + (j + 1/2)⁻²)` (`nodeSlope`).

For `m ≥ 1` put `h = 16 m`, common nodes `C = [0, h)`, separated row nodes `[0, h + m)` and
separated column nodes `C ∪ [h + m, h + 2 m)`, both in increasing order. Deleting at most one
common node `c ∈ C` from both, the pencil has entry `(f_b - f_a) / (b - a)` at row node `a`
and column node `b ≠ a`, and `X + d_a` on the common diagonal `a = b`;
`P_sep,I(X)` is its determinant (`separatedLownerDet`).

## Main definitions

* `nodeValue`, `nodeSlope`, `lownerEntry`;
* `skipNode`, `rowNode`, `colNode`: the ordered node sets after deletion;
* `Admissible m c`: `c` is `none` or a common node `c < 16 m`;
* `separatedLownerDet s m c`: the polynomial `P_sep,I(X)` with `I = c`.

## Main results

* `natDegree_separatedLownerDet_le`: `deg P_sep,I ≤ h + m`.
-/

namespace AxiomForge.Trigamma

open Polynomial Finset

/-- `f_i = ∑_{j < i} ((j + s)⁻¹ - (j + 1/2)⁻¹)`. -/
noncomputable def nodeValue (s : ℝ) (i : ℕ) : ℝ :=
  ∑ j ∈ range i, (1 / ((j : ℝ) + s) - 1 / ((j : ℝ) + 1 / 2))

/-- `d_i = ∑_{j < i} (-(j + s)⁻² + (j + 1/2)⁻²)`. -/
noncomputable def nodeSlope (s : ℝ) (i : ℕ) : ℝ :=
  ∑ j ∈ range i, (-(1 / ((j : ℝ) + s) ^ 2) + 1 / ((j : ℝ) + 1 / 2) ^ 2)

/-- The pencil entry at row node `a` and column node `b`. -/
noncomputable def lownerEntry (s : ℝ) (a b : ℕ) : ℝ[X] :=
  if a = b then X + C (nodeSlope s a)
  else C ((nodeValue s b - nodeValue s a) / ((b : ℝ) - a))

/-- Reindexing after the deletion of at most one node `c`: the `k`-th remaining index. -/
def skipNode (c : Option ℕ) (k : ℕ) : ℕ :=
  match c with
  | none => k
  | some c => if k < c then k else k + 1

/-- The `k`-th separated row node: the row nodes are `[0, h + m)`. -/
def rowNode (k : ℕ) : ℕ := k

/-- The `k`-th separated column node: the column nodes are `[0, h) ∪ [h + m, h + 2 m)`. -/
def colNode (h m k : ℕ) : ℕ := if k < h then k else k + m

/-- An admissible deletion: none, or one common node `c < h = 16 m`. -/
def Admissible (m : ℕ) (c : Option ℕ) : Prop := ∀ c₀ ∈ c, c₀ < 16 * m

/-- The size `h + m - |I|` of the pencil. -/
def pencilSize (m : ℕ) (c : Option ℕ) : ℕ := 16 * m + m - (if c.isSome then 1 else 0)

/-- The separated Löwner pencil determinant `P_sep,I(X)` (`h = 16 m`, `I = c`). -/
noncomputable def separatedLownerDet (s : ℝ) (m : ℕ) (c : Option ℕ) : ℝ[X] :=
  (Matrix.of fun k l : Fin (pencilSize m c) ↦
    lownerEntry s (rowNode (skipNode c k)) (colNode (16 * m) m (skipNode c l))).det

theorem natDegree_lownerEntry_le (s : ℝ) (a b : ℕ) : (lownerEntry s a b).natDegree ≤ 1 := by
  unfold lownerEntry
  split_ifs
  · exact (natDegree_add_le _ _).trans (by simp)
  · simp

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

theorem natDegree_separatedLownerDet_le (s : ℝ) (m : ℕ) (c : Option ℕ) :
    (separatedLownerDet s m c).natDegree ≤ pencilSize m c :=
  (natDegree_det_le_of_natDegree_le_one _ fun _ _ ↦ natDegree_lownerEntry_le _ _ _).trans
    (by simp)

end AxiomForge.Trigamma
