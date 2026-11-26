"""Independent exact implementation of the Löwner pencils for psi_1(k/5) - pi^2/2.

Written from the definitions in the candidate proof (Section 1), not from its scripts.

s = k/5, t = 1/2, F(z) = psi(z+s) - psi(z+t), xi = F'(0) = psi_1(k/5) - psi_1(1/2)
                                                   = psi_1(k/5) - pi^2/2.
f_i = F(i) - F(0) = sum_{j<i} [1/(j+s) - 1/(j+t)],
d_i = F'(i) - F'(0) = sum_{j<i} [-1/(j+s)^2 + 1/(j+t)^2].
For h = 16m:  N = h + 2m, n = h + m, common nodes C = [0, h).
  alternating: rows C + {h, h+2, ...}, columns C + {h+1, h+3, ...}   (m border nodes each)
  separated:   rows [0, h+m),          columns C + [h+m, h+2m)
Entry (row i, column j): X + d_i if i == j (common node), else (f_j - f_i)/(j - i).
P_I(X) is the determinant after removing a common subset I from rows and columns.
"""

from __future__ import annotations

import sys
from fractions import Fraction

from flint import acb, arb, ctx, fmpq, fmpq_mat, fmpq_poly

from define_exact_arithmetic import interpolate

sys.set_int_max_str_digits(0)


def increments(k: int, N: int):
    s = fmpq(k, 5)
    t = fmpq(1, 2)
    f = [fmpq(0)]
    d = [fmpq(0)]
    for j in range(N):
        f.append(f[-1] + 1 / (j + s) - 1 / (j + t))
        d.append(d[-1] - 1 / (j + s) ** 2 + 1 / (j + t) ** 2)
    return f, d


def node_sets(h: int, layout: str):
    m = h // 16
    C = list(range(h))
    if layout == "alternating":
        R = C + [h + 2 * r for r in range(m)]
        Q = C + [h + 2 * r + 1 for r in range(m)]
    elif layout == "separated":
        R = list(range(h + m))
        Q = C + list(range(h + m, h + 2 * m))
    else:
        raise ValueError(layout)
    return sorted(R), sorted(Q)


def pencil(k: int, h: int, layout: str, removed=()):
    """Return (A0, A1, common_count) with the pencil A0 + X*A1."""
    m = h // 16
    N = h + 2 * m
    f, d = increments(k, N)
    R, Q = node_sets(h, layout)
    R = [i for i in R if i not in removed]
    Q = [j for j in Q if j not in removed]
    n = len(R)
    A0 = fmpq_mat(n, n)
    A1 = fmpq_mat(n, n)
    for a, i in enumerate(R):
        for b, j in enumerate(Q):
            if i == j:
                A0[a, b] = d[i]
                A1[a, b] = 1
            else:
                A0[a, b] = (f[j] - f[i]) / (j - i)
    return A0, A1, sum(1 for i in R if i in Q)


def det_pencil(A0, A1, degree_bound: int) -> fmpq_poly:
    xs = [fmpq(t) for t in range(degree_bound + 1)]
    return interpolate(xs, [(A0 + x * A1).det() for x in xs])


def xi_ball(k: int, prec: int):
    """Certified enclosure of psi_1(k/5) - pi^2/2 = zeta(2, k/5) - pi^2/2 (Arb)."""
    ctx.prec = prec
    return arb(2).zeta(arb(k) / 5) - arb.pi() ** 2 / 2
