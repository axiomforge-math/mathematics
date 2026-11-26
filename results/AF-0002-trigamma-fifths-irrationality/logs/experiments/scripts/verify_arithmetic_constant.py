#!/usr/bin/env python
"""Checker for the arithmetic constant A (manuscript, Definition 4.12, Proposition 4.13, Appendix A).

Exact rational recomputation, written from the text of Sections 4.2-4.5, separately from the
original programs integrate_polar_profile.py and integrate_separated_profile.py.  Scaled geometry:
common nodes [0,1), border [1,1+c), c = 1/8, N = 1+c, n = 1 + c/2 (rows per h).
For a prime p = x h in the root class kappa (kappa = j/5, j = k p^{-1} mod 5) a residue
position t in (0,x) carries the fibre of digits l = 0..total-1 (nodes t + l x < N), the first
`common` of which are common (t + l x < 1); border digits alternate row/column, both parities
in equal proportion.  Bits eps1 = [t > kappa x], eps2 = [t > x/2].  Polar values

    V_l =  sum_{a<l+eps1} 1/(kappa+a) - sum_{a<l+eps2} 1/(1/2+a)
    W_l = -sum_{a<l+eps1} 1/(kappa+a)^2 + sum_{a<l+eps2} 1/(1/2+a)^2

block A[l][l'] = W_l (l = l' common), (V_l' - V_l)/(l' - l) otherwise.  Over Q: rank, left and
right nullspaces, moment map B(u) = (sum u_l, sum u_l V_l), its image dimension (0,1,2) and
(when 1) the projective line.  Profile (per h):

    R0 = sum rank,  a = sum dim B(left null),  b = sum dim B(right null),
    a_L, b_L = contributions on the projective line L,
    q = min(a, b, min_L (a + b - a_L - b_L)),   bound(x) = 2 R0 + q.

Two labelling conventions for fibres whose moment image is 2-dimensional:
  'fixed'   : the basis is labelled by the lines 0 and infinity (as in the original programs);
  'optimal' : for each L the basis is re-chosen so that one vector lies on L (also valid,
              since a different basis may be used for each L in the rank bound).

Exact integration: all cut functions 0, x, 1 - j x, N - j x, kappa x, x/2 are affine in x;
breakpoints = all pairwise coincidences of these lines in (1/20, 5N) (a superset of the needed
ones); on each interval the piece lengths and hence all candidates are affine; their minimum
is integrated exactly after splitting at pairwise intersections.  The combinatorial type is
checked to be constant at two interior points of every interval.

A = (2+c)/20 + (1/4) sum_kappa int_{1/20}^{5N} bound_kappa(x) dx.

Usage: python verify_arithmetic_constant.py [fixed|optimal|both]
Exit status 1 if the 'fixed' value differs from the claimed rational or if A >= 3.512131.
"""

from __future__ import annotations

import sys
import time
from collections import defaultdict
from functools import lru_cache

from flint import fmpq, fmpq_mat, fmpz_mat

C = fmpq(1, 8)
N = 1 + C
NROWS = 1 + C / 2
CUT = fmpq(1, 20)
TOP = 5 * N
CLAIMED = fmpq(304227995343501721142691896310988016794079029050925423,
               86622067750624596685118168422516024981216422248448000)


def floor_q(x: fmpq) -> int:
    return int(x.p) // int(x.q)


def nullspace_q(rows: list[list[fmpq]], ncols: int) -> list[list[fmpq]]:
    """Basis of {z in Q^ncols : rows z = 0} via fmpz_mat.nullspace after clearing denominators."""
    if ncols == 0:
        return []
    if not rows:
        return [[fmpq(int(i == j)) for i in range(ncols)] for j in range(ncols)]
    M = fmpq_mat(len(rows), ncols, [e for r in rows for e in r])
    num, den = M.numer_denom()
    X, nullity = num.nullspace()
    return [[fmpq(X[i, j]) for i in range(ncols)] for j in range(nullity)]


def line_of(v):
    x, y = v
    return ("inf",) if x == 0 else ("slope", y / x)


@lru_cache(None)
def block(kap: fmpq, common: int, total: int, e1: int, e2: int, parity: int):
    half = fmpq(1, 2)
    V, W = [], []
    for l in range(total):
        V.append(sum((1 / (kap + a) for a in range(l + e1)), fmpq(0))
                 - sum((1 / (half + a) for a in range(l + e2)), fmpq(0)))
        W.append(-sum((1 / (kap + a) ** 2 for a in range(l + e1)), fmpq(0))
                 + sum((1 / (half + a) ** 2 for a in range(l + e2)), fmpq(0)))
    rows = [l for l in range(total) if l < common or (l - common) % 2 == parity]
    cols = [l for l in range(total) if l < common or (l - common) % 2 != parity]
    A = [[W[i] if i == j else (V[j] - V[i]) / (j - i) for j in cols] for i in rows]
    right = nullspace_q(A, len(cols))
    left = nullspace_q([[A[i][j] for i in range(len(rows))] for j in range(len(cols))], len(rows))
    rank = len(cols) - len(right)
    assert rank == len(rows) - len(left)

    def moments(basis, ids):
        if not basis:
            return 0, None
        Mm = [[sum((z[t] for t in range(len(ids))), fmpq(0)) for z in basis],
              [sum((z[t] * V[ids[t]] for t in range(len(ids))), fmpq(0)) for z in basis]]
        mat = fmpq_mat(2, len(basis), Mm[0] + Mm[1])
        r = mat.rank()
        if r == 1:
            j = next(j for j in range(len(basis)) if Mm[0][j] != 0 or Mm[1][j] != 0)
            return 1, line_of((Mm[0][j], Mm[1][j]))
        return r, None

    dl, Ll = moments(left, rows)
    dr, Lr = moments(right, cols)
    return rank, dl, Ll, dr, Lr


# ---------------------------------------------------------------- affine bookkeeping
class Aff:
    __slots__ = ("a", "b")

    def __init__(self, a, b):
        self.a, self.b = fmpq(a), fmpq(b)

    def __add__(self, o):
        return Aff(self.a + o.a, self.b + o.b)

    def __sub__(self, o):
        return Aff(self.a - o.a, self.b - o.b)

    def scale(self, s):
        return Aff(self.a * s, self.b * s)

    def __call__(self, x):
        return self.a + self.b * x

    def __eq__(self, o):
        return self.a == o.a and self.b == o.b

    def __repr__(self):
        return "Aff(%s,%s)" % (self.a, self.b)


ZERO = Aff(0, 0)


def cut_lines(kap, x):
    R0 = floor_q(1 / x)
    N0 = floor_q(N / x)
    return R0, N0, [Aff(0, 0), Aff(0, 1), Aff(1, -R0), Aff(N, -N0), Aff(0, kap), Aff(0, fmpq(1, 2))]


def combinatorics(kap, x):
    R0, N0, cuts = cut_lines(kap, x)
    order = sorted(range(len(cuts)), key=lambda i: (cuts[i](x), i))
    vals = [cuts[i](x) for i in order]
    ties = tuple(vals[i] == vals[i + 1] for i in range(len(vals) - 1))
    return R0, N0, tuple(order), ties


def profile(kap, xm):
    """Affine profile (valid on the breakpoint interval containing xm)."""
    R0, N0, cuts = cut_lines(kap, xm)
    srt = sorted(cuts, key=lambda f: f(xm))
    rk = ZERO
    zl = ZERO
    zr = ZERO
    a = ZERO
    b = ZERO
    two_l = ZERO   # weight of left 2-dim fibres
    two_r = ZERO
    linel = defaultdict(lambda: ZERO)
    liner = defaultdict(lambda: ZERO)
    rowcount = ZERO
    for f, g in zip(srt, srt[1:]):
        length = g - f
        lo, hi = f(xm), g(xm)
        if lo == hi:
            continue
        t = (lo + hi) / 2
        common = R0 + int(t < 1 - R0 * xm)
        total = N0 + int(t < N - N0 * xm)
        e1 = int(t > kap * xm)
        e2 = int(t > xm / 2)
        w = length.scale(fmpq(1, 2))
        for parity in (0, 1):
            rank, dl, Ll, dr, Lr = block(kap, common, total, e1, e2, parity)
            nrow = sum(1 for l in range(total) if l < common or (l - common) % 2 == parity)
            ncol = total - (nrow - common)
            rk = rk + w.scale(rank)
            rowcount = rowcount + w.scale(nrow)
            zl = zl + w.scale(nrow - rank - dl)
            zr = zr + w.scale(ncol - rank - dr)
            a = a + w.scale(dl)
            b = b + w.scale(dr)
            if dl == 1:
                linel[Ll] = linel[Ll] + w
            elif dl == 2:
                two_l = two_l + w
            if dr == 1:
                liner[Lr] = liner[Lr] + w
            elif dr == 2:
                two_r = two_r + w
    # consistency: total rows = n, and left/right deficiencies equal d = n - R0
    assert rowcount == Aff(NROWS, 0), rowcount
    d = Aff(NROWS, 0) - rk
    assert zl + a == d and zr + b == d
    return rk, a, b, linel, liner, two_l, two_r


def candidates(kap, xm, mode):
    rk, a, b, linel, liner, two_l, two_r = profile(kap, xm)
    base = rk.scale(2)
    out = [base + a, base + b]
    keys = set(linel) | set(liner)
    if mode == "fixed":
        zero, inf = ("slope", fmpq(0)), ("inf",)
        L2 = defaultdict(lambda: ZERO)
        R2 = defaultdict(lambda: ZERO)
        for k in keys | {zero, inf}:
            L2[k] = linel[k] + (two_l if k in (zero, inf) else ZERO)
            R2[k] = liner[k] + (two_r if k in (zero, inf) else ZERO)
        has2 = not (two_l == ZERO and two_r == ZERO)
        for k in keys | ({zero, inf} if has2 else set()):
            out.append(base + a + b - L2[k] - R2[k])
    else:  # optimal: a 2-dim fibre puts one basis vector on any prescribed line
        for k in keys:
            out.append(base + a + b - linel[k] - liner[k] - two_l - two_r)
        out.append(base + a + b - two_l - two_r)  # a line used by no 1-dim fibre
    return sorted(out, key=lambda f: (f.a, f.b))


def integrate_min(funcs, l, r):
    pts = {l, r}
    for i, f in enumerate(funcs):
        for g in funcs[:i]:
            if f.b != g.b:
                x = (g.a - f.a) / (f.b - g.b)
                if l < x < r:
                    pts.add(x)
    pts = sorted(pts)
    tot = fmpq(0)
    for u, v in zip(pts, pts[1:]):
        m = (u + v) / 2
        tot += (v - u) * min(f(m) for f in funcs)
    return tot


def breakpoints(kap):
    lines = [Aff(0, 0), Aff(0, 1), Aff(0, kap), Aff(0, fmpq(1, 2))]
    J1 = floor_q(1 / CUT) + 2
    JN = floor_q(N / CUT) + 2
    lines += [Aff(1, -j) for j in range(J1 + 1)] + [Aff(N, -j) for j in range(JN + 1)]
    pts = {CUT, TOP}
    for i, f in enumerate(lines):
        for g in lines[:i]:
            if f.b != g.b:
                x = (g.a - f.a) / (f.b - g.b)
                if CUT < x < TOP:
                    pts.add(x)
    return sorted(pts)


def integral(kap, mode):
    pts = breakpoints(kap)
    tot = fmpq(0)
    for l, r in zip(pts, pts[1:]):
        u, v = (2 * l + r) / 3, (l + 2 * r) / 3
        assert combinatorics(kap, u) == combinatorics(kap, v), (kap, l, r)
        fu = candidates(kap, u, mode)
        fv = candidates(kap, v, mode)
        assert fu == fv, (kap, l, r)  # same affine candidates at two interior points
        tot += integrate_min(fu, l, r)
    return tot, len(pts) - 1


def main():
    modes = sys.argv[1:] or ["both"]
    modes = ["fixed", "optimal"] if modes == ["both"] else modes
    ok = True
    for mode in modes:
        t0 = time.time()
        per = []
        for j in range(1, 5):
            kap = fmpq(j, 5)
            I, nint = integral(kap, mode)
            per.append(I + (2 + C) * CUT)
            print("mode %s kappa %s: (2+c)/20 + integral = %.16f  [%d intervals, %.0fs]"
                  % (mode, kap, float(per[-1].p) / float(per[-1].q), nint, time.time() - t0), flush=True)
        A = sum(per, fmpq(0)) / 4
        print("mode %s: A = %s" % (mode, A))
        print("mode %s: A = %.16f" % (mode, float(A.p) / float(A.q)), flush=True)
        if mode == "fixed":
            same = A == CLAIMED
            print(("PASS" if same else "FAIL") + " fixed-labelling A equals the claimed rational (5)")
            ok &= same
        lt = A < fmpq(3512131, 10**6)
        print(("PASS" if lt else "FAIL") + " A < 3.512131 (mode %s)" % mode, flush=True)
        ok &= lt
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
