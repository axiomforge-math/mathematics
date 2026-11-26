"""Exact implementation of the half-integer pencils for chi_2(2/q), Ti_2(2/q).

Written from the definitions of Section 2 of the manuscript, separately from the programs that
produced the certificates.

q odd, sigma = +1 (chi_2) or -1 (Ti_2); y = q/2, w = sigma / y^2,
xi = sum_{j>=0} sigma^j y^{-2j-1} / (2j+1)^2,  tau_k = partial sum through j = k.
Poles x_k = -k - 1/2 (0 <= k < K); D_K(u) = prod (u - x_k).
Affine functional:  mu_X(R) = sum_{m>=1} w^m R'(m) on polynomials (rational geometric
moments), mu_X(1/(u - x_k)) = -4 sigma^k y^{2k+1} (X - tau_k).
Construction "general" (odd q >= 83): h = 6n, K = 7n, A = 0, phi = u / D_K.
Construction "band" (q = 81):        h = 40n, K = 49n, A = 2n, phi = u prod_{j<=A}(u-j)^2 / D_K.
Construction "square" (any q):       h = n, K = h, A = 0, phi = u / D_K (the size n is h itself).
Delta(X) = det[mu_X(phi u^{i+j})], T = S * Delta with S = (K!/(A!)^2)^h / prod_{i<h} (i!)^2.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass

from flint import acb, arb, ctx, fmpq, fmpq_mat, fmpq_poly



def interpolate(xs, ys):
    """Exact Newton interpolation over Q."""
    coef = list(ys)
    n = len(xs)
    for j in range(1, n):
        for i in range(n - 1, j - 1, -1):
            coef[i] = (coef[i] - coef[i - 1]) / (xs[i] - xs[i - j])
    X = fmpq_poly([0, 1])
    poly = fmpq_poly([coef[-1]])
    for i in range(n - 2, -1, -1):
        poly = poly * (X - xs[i]) + coef[i]
    return poly


def det_affine(A0, A1):
    """Exact det(A0 + X*A1) as a polynomial in X (degree <= size)."""
    h = A0.nrows()
    xs = [fmpq(t) for t in range(h + 1)]
    ys = [(A0 + t * A1).det() for t in xs]
    return interpolate(xs, ys)

sys.set_int_max_str_digits(0)


@dataclass(frozen=True)
class Pencil:
    q: int
    sigma: int
    construction: str  # "general" or "band"

    def sizes(self, n: int) -> tuple[int, int, int]:
        if self.construction == "general":
            return 6 * n, 7 * n, 0
        if self.construction == "square":  # K = h = n, A = 0 (Appendix B); n is the size h itself
            return n, n, 0
        return 40 * n, 49 * n, 2 * n


def stirling_moments(w: fmpq, kmax: int) -> list[fmpq]:
    """M_k(w) = sum_{m>=1} w^m m^k, k = 0..kmax, via Stirling numbers of the second kind."""
    S = [[fmpq(0)] * (kmax + 2) for _ in range(kmax + 2)]
    S[0][0] = fmpq(1)
    for k in range(1, kmax + 1):
        for j in range(1, k + 1):
            S[k][j] = j * S[k - 1][j] + S[k - 1][j - 1]
    one = fmpq(1)
    out = [w / (one - w)]
    for k in range(1, kmax + 1):
        out.append(sum((S[k][j] * math.factorial(j) * w**j / (one - w) ** (j + 1) for j in range(1, k + 1)),
                       fmpq(0)))
    return out


def matrices(P: Pencil, n: int):
    h, K, A = P.sizes(n)
    y = fmpq(P.q, 2)
    w = P.sigma / y**2
    u = fmpq_poly([0, 1])
    num = u
    for j in range(1, A + 1):
        num *= (u - j) ** 2
    DK = fmpq_poly([1])
    xs = [-(k + fmpq(1, 2)) for k in range(K)]
    for x in xs:
        DK *= u - x
    dDK = DK.derivative()
    tau = []
    acc = fmpq(0)
    for k in range(K):
        acc += P.sigma**k * y ** (-(2 * k + 1)) / fmpq((2 * k + 1) ** 2)
        tau.append(acc)
    M = stirling_moments(w, max(1, num.degree() + 2 * h - K) + 1)
    cache = {}
    for s in range(2 * h - 1):
        N = num * u**s
        quo, _ = divmod(N, DK)
        dq = quo.derivative()
        v0 = sum((dq[k] * M[k] for k in range(dq.degree() + 1)), fmpq(0)) if quo.degree() >= 1 else fmpq(0)
        v1 = fmpq(0)
        for k, x in enumerate(xs):
            res = N(x) / dDK(x)
            if res != 0:
                c = res * (-4) * P.sigma**k * y ** (2 * k + 1)
                v1 += c
                v0 -= c * tau[k]
        cache[s] = (v0, v1)
    A0, A1 = fmpq_mat(h, h), fmpq_mat(h, h)
    for i in range(h):
        for j in range(h):
            A0[i, j], A1[i, j] = cache[i + j]
    return A0, A1


def normalization(P: Pencil, n: int) -> fmpq:
    h, K, A = P.sizes(n)
    S = fmpq(math.factorial(K), math.factorial(A) ** 2)
    return S**h / math.prod(math.factorial(i) ** 2 for i in range(h))


def T_poly(P: Pencil, n: int) -> fmpq_poly:
    A0, A1 = matrices(P, n)
    return det_affine(A0, A1) * normalization(P, n)


def xi_ball(P: Pencil, prec: int):
    ctx.prec = prec
    x = arb(2) / P.q
    if P.sigma == 1:  # chi_2(x) = (Li_2(x) - Li_2(-x)) / 2
        return ((acb(x).polylog(2) - acb(-x).polylog(2)) / 2).real
    return acb(0, x).polylog(2).imag  # Ti_2(x) = Im Li_2(i x)
