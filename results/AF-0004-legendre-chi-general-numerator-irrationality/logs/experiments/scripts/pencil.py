"""Exact implementation of the half-integer pencils for chi_2(a/q), Ti_2(a/q).

Written from the definitions of Section 2 of the manuscript (python-flint rationals); it
does not import the code that produced the candidate certificates.

a >= 1, q odd, gcd(a, q) = 1, sigma = +1 (chi_2) or -1 (Ti_2); y = q/a, w = sigma / y^2,
xi = sum_{j>=0} sigma^j y^{-2j-1} / (2j+1)^2,  tau_k = partial sum through j = k.
Poles x_k = -k - 1/2 (0 <= k < K); D_K(u) = prod (u - x_k); phi = u / D_K.
mu_X(R) = sum_{m>=1} w^m R'(m) on polynomials (rational geometric moments),
mu_X(1/(u - x_k)) = -4 sigma^k y^{2k+1} (X - tau_k).
Sizes h = t n, K = c n with (t, c) = (6, 7) or (4, 5).
Delta(X) = det[mu_X(phi u^{i+j})],  T = S Delta,  S = (K!)^h / prod_{i<h} (i!)^2.
"""
import math
import sys
from flint import fmpq, fmpq_mat, fmpq_poly

sys.set_int_max_str_digits(0)


def interpolate(xs, ys):
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
    """det(A0 + X A1) as a polynomial in X (degree <= size), exactly."""
    h = A0.nrows()
    xs = [fmpq(t) for t in range(h + 1)]
    return interpolate(xs, [(A0 + t * A1).det() for t in xs])


def geometric_moments(w, kmax):
    """M_k(w) = sum_{m>=1} w^m m^k, k = 0..kmax."""
    S = [[fmpq(0)] * (kmax + 2) for _ in range(kmax + 2)]
    S[0][0] = fmpq(1)
    for k in range(1, kmax + 1):
        for j in range(1, k + 1):
            S[k][j] = j * S[k - 1][j] + S[k - 1][j - 1]
    one = fmpq(1)
    out = [w / (one - w)]
    for k in range(1, kmax + 1):
        out.append(sum((S[k][j] * math.factorial(j) * w ** j / (one - w) ** (j + 1) for j in range(1, k + 1)),
                       fmpq(0)))
    return out


class Pencil:
    def __init__(self, a, q, sigma, t, c):
        assert math.gcd(a, q) == 1 and q % 2 == 1 and sigma in (1, -1)
        self.a, self.q, self.sigma, self.t, self.c = a, q, sigma, t, c
        self.y = fmpq(q, a)
        self.w = sigma / self.y ** 2

    def setup(self, n):
        h, K = self.t * n, self.c * n
        u = fmpq_poly([0, 1])
        xs = [-(k + fmpq(1, 2)) for k in range(K)]
        DK = fmpq_poly([1])
        for x in xs:
            DK *= u - x
        tau, acc = [], fmpq(0)
        for k in range(K):
            acc += self.sigma ** k * self.y ** (-(2 * k + 1)) / fmpq((2 * k + 1) ** 2)
            tau.append(acc)
        return h, K, xs, DK, DK.derivative(), tau, geometric_moments(self.w, 2 * h + 2)

    def mu(self, N, env):
        """(v0, v1) with mu_X(N / D_K) = v0 + X v1, N a polynomial."""
        h, K, xs, DK, dDK, tau, M = env
        quo, _ = divmod(N, DK)
        dq = quo.derivative()
        v0 = sum((dq[k] * M[k] for k in range(dq.degree() + 1)), fmpq(0)) if quo.degree() >= 1 else fmpq(0)
        v1 = fmpq(0)
        for k, x in enumerate(xs):
            res = N(x) / dDK(x)
            if res != 0:
                cf = res * (-4) * self.sigma ** k * self.y ** (2 * k + 1)
                v1 += cf
                v0 -= cf * tau[k]
        return v0, v1

    def matrices(self, n):
        env = self.setup(n)
        h = env[0]
        u = fmpq_poly([0, 1])
        cache = {s: self.mu(u ** (s + 1), env) for s in range(2 * h - 1)}
        A0, A1 = fmpq_mat(h, h), fmpq_mat(h, h)
        for i in range(h):
            for j in range(h):
                A0[i, j], A1[i, j] = cache[i + j]
        return A0, A1

    def normalization(self, n):
        h, K = self.t * n, self.c * n
        return fmpq(math.factorial(K)) ** h / math.prod(math.factorial(i) ** 2 for i in range(h))

    def T_poly(self, n):
        A0, A1 = self.matrices(n)
        return det_affine(A0, A1) * self.normalization(n)


def vp(x, p):
    """p-adic valuation of a nonzero fmpq."""
    a, b, v = abs(int(x.p)), int(x.q), 0
    while a % p == 0:
        a //= p; v += 1
    while b % p == 0:
        b //= p; v -= 1
    return v


def gauss_valuation(T, p):
    return min(vp(T[k], p) for k in range(T.degree() + 1) if T[k] != 0)
