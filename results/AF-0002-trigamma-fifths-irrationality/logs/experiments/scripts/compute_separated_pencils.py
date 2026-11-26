"""Fast exact Löwner pencils P_I(X) = det(Phi(X)) via a Schur complement and a characteristic polynomial.

Node conventions are those of Definition 2.1 of the manuscript (and of define_lowner_family.py):
h = 16 m, N = h + 2m, common nodes C = [0,h);
  alternating: rows C + {h, h+2, ...}, cols C + {h+1, h+3, ...}
  separated:   rows [0, h+m),          cols C + [h+m, N).
Entry (i,j): X + d_i if i == j (common), (f_j - f_i)/(j - i) otherwise.

Since the common nodes occupy the same leading positions in the sorted row and column lists,
Phi(X) = [[A11 + X I, A12], [A21, A22]] and, when A22 (border x border) is invertible,
    P(X) = det(A22) * charpoly(K)(X),   K = A12 A22^{-1} A21 - A11.
Falls back to interpolation otherwise.  Cross-checked against define_lowner_family.det_pencil.
"""

from __future__ import annotations

from flint import fmpq, fmpq_mat, fmpq_poly


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


def pencil_poly(k: int, h: int, layout: str, removed=()) -> fmpq_poly:
    m = h // 16
    N = h + 2 * m
    f, d = increments(k, N)
    R, Q = node_sets(h, layout)
    R = [i for i in R if i not in removed]
    Q = [j for j in Q if j not in removed]
    common = [i for i in R if i in Q]
    nc = len(common)
    assert R[:nc] == common and Q[:nc] == common
    n = len(R)

    def ent(i, j):
        return d[i] if i == j else (f[j] - f[i]) / (j - i)

    A11 = fmpq_mat(nc, nc, [ent(i, j) for i in R[:nc] for j in Q[:nc]])
    if n == nc:
        return (-A11).charpoly()  # det(X I + A11)
    A12 = fmpq_mat(nc, n - nc, [ent(i, j) for i in R[:nc] for j in Q[nc:]])
    A21 = fmpq_mat(n - nc, nc, [ent(i, j) for i in R[nc:] for j in Q[:nc]])
    A22 = fmpq_mat(n - nc, n - nc, [ent(i, j) for i in R[nc:] for j in Q[nc:]])
    d22 = A22.det()
    if d22 != 0:
        K = A12 * A22.inv() * A21 - A11
        return d22 * K.charpoly()
    # fallback: interpolation at nc + 1 integer points
    from define_exact_arithmetic import interpolate
    xs = [fmpq(t) for t in range(nc + 1)]
    ys = []
    for x in xs:
        M = fmpq_mat(n, n, [ent(i, j) + (x if i == j else 0) for i in R for j in Q])
        ys.append(M.det())
    return interpolate(xs, ys)
