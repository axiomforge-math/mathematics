"""Local Gram determinants det H_0, det H_1 and the Lean certificate modules (lean/.../LocalGram).

For lam in {2/11, 2/9, -2/9, -2/7} the prime-index nonvanishing argument of the
manuscript (Section 6, Table 6) reduces to the Hankel matrices

    H_b = ( V(u^(i+j) w_b(u)) )_{0 <= i, j < H},   b in {0, 1},

where the linear functional V on rational functions with simple poles at u = -l,
l >= 0, is fixed by

    V(u^k) = k M_{k-1}(lam)  (k >= 1),   V(1) = 0,   V(1/(u+l)) = lam^(-l) tau_l(lam),

with M_k(lam) = sum_{u>=1} lam^u u^k and tau_l(lam) = sum_{u=1}^l lam^u / u^2.

This script does not reuse the original certificate programs. It differs from them in every step:

* M_k is obtained from the Euler operator theta = lam d/dlam applied k times to
  lam/(1-lam), as an exact rational function (python-flint fmpq_poly);
* partial fractions use flint polynomial division and residues N(-l)/D'(-l);
* determinants are computed by flint's fraction-free fmpq_mat.det;
* each entry is cross-checked numerically (mpmath, 120 digits) against the analytic
  form V(R) = sum_{u>=1} lam^u R'(u) + Li2(lam) * sum_l r_l lam^(-l), which follows
  from the three defining rules.

It also emits an exact LDU-type certificate (M = L U, L unit lower triangular) for the
Lean kernel check, and the Lean source of the certificate modules.

Usage: python generate_local_gram_certificates.py [--write-lean]
(with --write-lean the four Lean modules are regenerated in place; the committed modules are
the output of this script). Writes ../outputs/local-gram-certificates.json.

Exit status is non-zero on any mismatch.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

import mpmath
from flint import fmpq, fmpq_mat, fmpq_poly

mpmath.mp.dps = 120

X = fmpq_poly([0, 1])


def moment(lam: fmpq, k: int) -> fmpq:
    """M_k(lam) = sum_{u>=1} lam^u u^k via theta^k (x/(1-x)), evaluated at lam."""
    num, m = fmpq_poly([0, 1]), 1  # x / (1-x)^1
    for _ in range(k):
        # theta(N/(1-x)^m) = (x N' (1-x) + m x N) / (1-x)^(m+1)
        num, m = X * num.derivative() * (1 - X) + m * X * num, m + 1
    return num(lam) / (1 - lam) ** m


def tau(lam: fmpq, l: int) -> fmpq:
    return sum((lam ** u / fmpq(u * u) for u in range(1, l + 1)), fmpq(0))


def local_value(lam: fmpq, numer: fmpq_poly, poles: list[int]) -> tuple[fmpq, fmpq_poly, dict]:
    den = fmpq_poly([1])
    for l in poles:
        den *= fmpq_poly([l, 1])
    q, r = divmod(numer, den)
    dden = den.derivative()
    res = {l: r(fmpq(-l)) / dden(fmpq(-l)) for l in poles}
    coeffs = [q[k] for k in range(q.degree() + 1)] if q.degree() >= 0 else []
    val = sum((k * c * moment(lam, k - 1) for k, c in enumerate(coeffs) if k >= 1), fmpq(0))
    val += sum((res[l] * lam ** (-l) * tau(lam, l) for l in poles), fmpq(0))
    return val, q, res


def numeric_check(lam: fmpq, numer: fmpq_poly, poles: list[int], res: dict, exact: fmpq) -> float:
    lm = mpmath.mpf(int(lam.p)) / int(lam.q)
    num_c = [mpmath.mpf(int(c.p)) / int(c.q) for c in numer.coeffs()]

    def R(u):
        n = mpmath.polyval(num_c[::-1], u)
        d = mpmath.fprod([u + l for l in poles])
        return n / d

    # Direct summation: |lam| <= 2/7, so 400 terms give an error far below 10^-100.
    s = mpmath.mpf(0)
    for u in range(1, 400):
        s += lm ** u * mpmath.diff(R, u)
    li2 = mpmath.polylog(2, lm)
    s += li2 * sum(mpmath.mpf(int(res[l].p)) / int(res[l].q) * lm ** (-l) for l in poles)
    ex = mpmath.mpf(int(exact.p)) / int(exact.q)
    return float(abs(s - ex) / max(1, abs(ex)))


CASES = {
    # name: (lam, H, nonzero-class weight (numerator, poles), zero-class weight)
    "two-elevenths": (fmpq(2, 11), 4, (X ** 2, list(range(1, 6))),
                      (X * (X + 1) ** 2, list(range(2, 7)))),
    "two-ninths": (fmpq(2, 9), 8, (fmpq_poly([1]), list(range(0, 9))),
                   (X, list(range(1, 10)))),
    "minus-two-ninths": (fmpq(-2, 9), 4, (X ** 2, list(range(1, 7))),
                         (X * (X + 1) ** 2, list(range(2, 8)))),
    "minus-two-sevenths": (fmpq(-2, 7), 5, (X ** 2, list(range(1, 8))),
                           (X * (X + 1) ** 2, list(range(2, 9)))),
}

CLAIMED = {  # values printed in Table 6 of the manuscript
    ("two-elevenths", 1): "17828022563089333969/1224440064",
    ("two-elevenths", 0): "12598972834814973210048467/2295825120",
    ("two-ninths", 1): "3951366107675153857566158184061855291890957151/50404062960731160576000000000000",
    ("two-ninths", 0): "75748065809620696385810762379349631101207641762772048941/23344937339644196864000000000000",
    ("minus-two-ninths", 1): "1677163510311484581/15488000",
    ("minus-two-ninths", 0): "16417954848664067036722569/524733440",
    ("minus-two-sevenths", 1): "14067971871496713969085291850153/1057916215296000000",
    ("minus-two-sevenths", 0): "17800469908791563702231968746821382359/495898225920000000",
}


def lu(M: list[list[Fraction]]):
    n = len(M)
    L = [[Fraction(int(i == j)) for j in range(n)] for i in range(n)]
    U = [row[:] for row in M]
    for k in range(n):
        if U[k][k] == 0:
            raise SystemExit("zero pivot: LU without pivoting fails")
        for i in range(k + 1, n):
            L[i][k] = U[i][k] / U[k][k]
            for j in range(k, n):
                U[i][j] -= L[i][k] * U[k][j]
    return L, U


def frac(x: fmpq) -> Fraction:
    return Fraction(int(x.p), int(x.q))


def main() -> int:
    out = {}
    failures = 0
    for name, (lam, H, w1, w0) in CASES.items():
        for b, (wn, poles) in ((1, w1), (0, w0)):
            vals, worst = [], 0.0
            for k in range(2 * H - 1):
                numer = X ** k * wn
                v, _, res = local_value(lam, numer, poles)
                worst = max(worst, numeric_check(lam, numer, poles, res, v))
                vals.append(v)
            M = fmpq_mat(H, H, [vals[i + j] for i in range(H) for j in range(H)])
            d = M.det()
            claimed = CLAIMED[(name, b)]
            ok = str(d) == claimed
            failures += (not ok) or worst > 1e-90
            Mf = [[frac(vals[i + j]) for j in range(H)] for i in range(H)]
            L, U = lu(Mf)
            prod = Fraction(1)
            for i in range(H):
                prod *= U[i][i]
            lu_ok = prod == frac(d) and all(
                sum(L[i][k] * U[k][j] for k in range(H)) == Mf[i][j] for i in range(H) for j in range(H))
            failures += not lu_ok
            print(f"{name} H_{b}: size {H}, det = {d}  claimed {'MATCH' if ok else 'MISMATCH: ' + claimed}"
                  f"  numeric rel. error {worst:.1e}")
            out[f"{name}/H{b}"] = {
                "lambda": str(lam), "size": H, "b": b,
                "weight_numerator": str(wn), "poles": poles,
                "hankel_values": [str(v) for v in vals],
                "det": str(d), "claimed": claimed, "match": ok,
                "L": [[str(x) for x in row] for row in L], "U": [[str(x) for x in row] for row in U],
            }
    path = Path(__file__).resolve().parent.parent / "outputs" / "local-gram-certificates.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(out, indent=1) + "\n")
    print(f"wrote outputs/{path.name}; failures: {failures}")
    if not failures and "--write-lean" in sys.argv:
        emit_lean(out)
    return 1 if failures else 0


# --------------------------------------------------------------------------- Lean emission

# The Lean package of this contribution: <contribution>/lean (scripts -> experiments -> logs -> contribution).
LEAN_DIR = Path(__file__).resolve().parents[3] / "lean" / "AxiomForge" / "AF0001" / "LocalGram"

MODULES = {  # case: (Lean module name, LaTeX-free description of lambda, weights)
    "two-elevenths": ("TwoElevenths", "2/11", "u ^ 2 / ((u + 1) ⋯ (u + 5))",
                      "u (u + 1) ^ 2 / ((u + 2) ⋯ (u + 6))"),
    "two-ninths": ("TwoNinths", "2/9", "1 / (u (u + 1) ⋯ (u + 8))", "u / ((u + 1) ⋯ (u + 9))"),
    "minus-two-ninths": ("MinusTwoNinths", "-2/9", "u ^ 2 / ((u + 1) ⋯ (u + 6))",
                         "u (u + 1) ^ 2 / ((u + 2) ⋯ (u + 7))"),
    "minus-two-sevenths": ("MinusTwoSevenths", "-2/7", "u ^ 2 / ((u + 1) ⋯ (u + 7))",
                           "u (u + 1) ^ 2 / ((u + 2) ⋯ (u + 8))"),
}


def lean_rat(x: Fraction, indent: str) -> str:
    """A rational literal, splitting numerator and denominator over two lines if long."""
    if x.denominator == 1:
        return str(x.numerator)
    one = f"{x.numerator} / {x.denominator}"
    if len(indent) + len(one) + 1 <= 100:
        return one
    return f"{x.numerator} /\n{indent}  {x.denominator}"


def lean_eq(lhs: str, d: Fraction) -> str:
    """`lhs = d`, broken over lines so that no line exceeds 100 characters."""
    one = f"    {lhs} = {d.numerator} / {d.denominator} := by"
    if len(one) <= 100:
        return one
    return f"    {lhs} =\n      {d.numerator} /\n        {d.denominator} := by"


def lean_vector(name: str, doc: str, vals: list[Fraction]) -> str:
    ind = "  "
    body = ",\n".join(ind + lean_rat(v, ind) for v in vals)
    return f"/-- {doc} -/\ndef {name} : Fin {len(vals)} → ℚ := ![\n{body}]\n"


def lean_matrix(name: str, doc: str, M: list[list[Fraction]]) -> str:
    n = len(M)
    ind = "    "
    rows = []
    for row in M:
        flat = "  ![" + ", ".join(lean_rat(v, ind) for v in row) + "]"
        if "\n" not in flat and len(flat) <= 99:
            rows.append(flat)
        else:
            rows.append("  ![" + ",\n".join(("" if j == 0 else ind) + lean_rat(v, ind)
                                              for j, v in enumerate(row)) + "]")
    body = ",\n".join(rows)
    return (f"/-- {doc} -/\ndef {name} : Matrix (Fin {n}) (Fin {n}) ℚ :=\n"
            f"  Matrix.of ![\n{body}]\n")


def lean_block(tag: str, b: int, case: dict, weight: str) -> str:
    H = case["size"]
    vals = [Fraction(v) for v in case["hankel_values"]]
    L = [[Fraction(x) for x in row] for row in case["L"]]
    U = [[Fraction(x) for x in row] for row in case["U"]]
    d = Fraction(case["det"])
    m, G, Lo, Up = f"moments{tag}", f"gram{tag}", f"lower{tag}", f"upper{tag}"
    out = []
    out.append(lean_vector(m, f"The local moments `V(u ^ k w_{b}(u))`, `k < {2 * H - 1}`, with\n"
                              f"`w_{b}(u) = {weight}`.", vals))
    out.append(f"/-- The local Hankel Gram matrix `H_{b} = (V(u ^ (i + j) w_{b}(u)))_{{i, j < {H}}}`. -/\n"
               f"def {G} : Matrix (Fin {H}) (Fin {H}) ℚ :=\n"
               f"  Matrix.of fun i j ↦ {m} ⟨i.val + j.val, by omega⟩\n")
    out.append(lean_matrix(Lo, f"Unit lower triangular factor of `H_{b}`.", L))
    out.append(lean_matrix(Up, f"Upper triangular factor of `H_{b}`.", U))
    out.append(f"theorem {G}_eq_mul : {G} = {Lo} * {Up} := by\n"
               f"  ext i j\n"
               f"  fin_cases i <;> fin_cases j <;>\n"
               f"    norm_num [{G}, {Lo}, {Up}, {m}, Matrix.mul_apply, Fin.sum_univ_succ]\n")
    out.append(f"theorem det_{Lo} : {Lo}.det = 1 := by\n"
               f"  rw [Matrix.det_of_isLowerTriangular]\n"
               f"  · simp [{Lo}, Fin.prod_univ_succ]\n"
               f"  · intro i j hij\n"
               f"    rw [OrderDual.toDual_lt_toDual] at hij\n"
               f"    fin_cases i <;> fin_cases j <;> simp_all [{Lo}]\n")
    out.append(f"theorem det_{Up} :\n{lean_eq(Up + '.det', d)}\n"
               f"  rw [Matrix.det_of_isUpperTriangular]\n"
               f"  · norm_num [{Up}, Fin.prod_univ_succ]\n"
               f"  · intro i j hij\n"
               f"    fin_cases i <;> fin_cases j <;> simp_all [{Up}]\n")
    out.append(f"/-- The exact value of `det H_{b}` (manuscript value, recomputed independently):\n"
               f"`{d}`. -/\n"
               f"theorem det_{G} :\n{lean_eq(G + '.det', d)}\n"
               f"  rw [{G}_eq_mul, Matrix.det_mul, det_{Lo}, det_{Up}, one_mul]\n")
    out.append(f"theorem det_{G}_ne_zero : {G}.det ≠ 0 := by\n"
               f"  rw [det_{G}]\n"
               f"  norm_num\n")
    return "\n".join(out)


def emit_lean(out: dict) -> None:
    LEAN_DIR.mkdir(parents=True, exist_ok=True)
    for case, (mod, lam, w1, w0) in MODULES.items():
        H = out[f"{case}/H1"]["size"]
        head = f"""import Mathlib.LinearAlgebra.Matrix.Block
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum

/-!
# Local Gram determinants for `λ = {lam}`

Kernel-checked finite certificate for the prime-index nonvanishing argument of the
manuscript for `Li₂({lam})`. The diagonal blocks of the reduced Gram matrix are, up to nonzero
constants, the `{H} × {H}` Hankel matrices `H_b = (V(u ^ (i + j) w_b(u)))_{{i, j < {H}}}`,
`b ∈ {{0, 1}}`, where `V` is the rational functional with
`V(u ^ k) = k M_(k-1)(λ)` (`k ≥ 1`), `V(1) = 0`, `V((u + l)⁻¹) = λ ^ (-l) τ_l(λ)`, and the
local weights are
* `w_1(u) = {w1}` (nonzero residue classes),
* `w_0(u) = {w0}` (zero residue class).

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

namespace AxiomForge.Dilogarithm.LocalGram.{mod}

"""
        body = lean_block("One", 1, out[f"{case}/H1"], w1) + "\n" + lean_block("Zero", 0, out[f"{case}/H0"], w0)
        tail = f"\nend AxiomForge.Dilogarithm.LocalGram.{mod}\n"
        (LEAN_DIR / f"{mod}.lean").write_text(head + body + tail)
        print(f"wrote Lean certificate AF0001/LocalGram/{mod}.lean")


if __name__ == "__main__":
    sys.exit(main())
