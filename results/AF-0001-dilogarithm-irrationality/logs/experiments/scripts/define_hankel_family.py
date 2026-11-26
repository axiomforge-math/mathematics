"""Exact implementation of the enlarged Hankel family for Li_2(lambda) (manuscript, Section 2).

Written from the mathematical definitions only, separately from the original certificate
programs. Used by the exploratory scripts of Appendix C; it proves nothing.

For a rational lambda with 0 < |lambda| < 1 and integer parameters (H, C, B), put
    h = H n,  K = C n,  A = B n,
    D_m(x) = prod_{j=1}^m (x + j),
    W(x) = D_A(x)^3 / D_K(x),
    S = K! / (A!)^3,   F = prod_{i<h} (i!)^2.
The affine functional Lambda_X on rational functions with at most simple poles at
negative integers is
    Lambda_X(x^k)        = (k+1) M_k(lambda),   M_k(q) = sum_{u>=1} q^u u^k,
    Lambda_X(1/(x+l))    = l lambda^{-l} (X - tau_l(lambda)),  tau_l = sum_{u<=l} lambda^u/u^2,
so that Lambda_xi(R) = sum_{x>=1} lambda^x (x R(x))' at xi = Li_2(lambda).
Then Q(X) = det[Lambda_X(W x^{i+j})]_{i,j<h} and Qt = S^h / F * Q.
"""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

from flint import fmpq, fmpq_mat, fmpq_poly, fmpz

# Exact polynomials Q_n are written by compute_hankel_polynomials.py to
# DATA_DIR/<slug>/Q_NNN.json (generated data, not part of the archive). The directory can
# be changed with the environment variable HANKEL_DATA_DIR.
DATA_DIR = Path(os.environ.get("HANKEL_DATA_DIR", Path(__file__).resolve().parent.parent / "data"))
SLUG = {"2/11": "two-elevenths", "2/9": "two-ninths", "-2/9": "minus-two-ninths", "-2/7": "minus-two-sevenths"}


@dataclass(frozen=True)
class Case:
    name: str
    lam: Fraction
    H: int
    C: int
    B: int


CASES = {
    "2/11": Case("2/11", Fraction(2, 11), 4, 6, 1),
    "2/9": Case("2/9", Fraction(2, 9), 8, 9, 0),
    "-2/9": Case("-2/9", Fraction(-2, 9), 4, 7, 1),
    "-2/7": Case("-2/7", Fraction(-2, 7), 5, 8, 1),
}


def q(fr: Fraction) -> fmpq:
    return fmpq(fr.numerator, fr.denominator)


@lru_cache(maxsize=None)
def stirling2(k: int, j: int) -> int:
    if k == j:
        return 1
    if j == 0 or j > k:
        return 0
    return j * stirling2(k - 1, j) + stirling2(k - 1, j - 1)


def moments(lam: fmpq, kmax: int) -> list[fmpq]:
    """M_k(lam) = sum_{u>=1} lam^u u^k for k = 0..kmax (exact rational)."""
    one = fmpq(1)
    out = [lam / (one - lam)]
    for k in range(1, kmax + 1):
        s = fmpq(0)
        for j in range(1, k + 1):
            s += stirling2(k, j) * math.factorial(j) * lam**j / (one - lam) ** (j + 1)
        out.append(s)
    return out


def family_matrices(case: Case, n: int):
    """Return (A0, A1) with Lambda_X(W x^{i+j}) = A0[i,j] + X * A1[i,j]."""
    lam = q(case.lam)
    h, K, A = case.H * n, case.C * n, case.B * n
    x = fmpq_poly([0, 1])
    DA = fmpq_poly([1])
    for j in range(1, A + 1):
        DA *= x + j
    DK = fmpq_poly([1])
    for j in range(1, K + 1):
        DK *= x + j
    num_base = DA**3
    # tau_l and lam^{-l}
    tau = [fmpq(0)]
    for l in range(1, K + 1):
        tau.append(tau[-1] + lam**l / fmpq(l * l))
    lam_inv_pow = [lam ** (-l) for l in range(K + 1)]
    # derivative of D_K at -l: prod_{j != l} (j - l)
    dK_at = [None] + [
        fmpq(math.prod(j - l for j in range(1, K + 1) if j != l)) for l in range(1, K + 1)
    ]
    maxdeg = max(0, 3 * A + 2 * (h - 1) - K)
    M = moments(lam, maxdeg + 1)
    A0 = fmpq_mat(h, h)
    A1 = fmpq_mat(h, h)
    cache = {}
    for s in range(2 * h - 1):
        N = num_base * x**s
        quo, _rem = divmod(N, DK)
        val0 = fmpq(0)
        for k in range(quo.degree() + 1):
            c = quo[k]
            if c != 0:
                val0 += c * (k + 1) * M[k]
        val1 = fmpq(0)
        for l in range(A + 1, K + 1):
            res = N(fmpq(-l)) / dK_at[l]  # residue of N/DK at x=-l
            if res != 0:
                coef = res * l * lam_inv_pow[l]
                val1 += coef
                val0 -= coef * tau[l]
        cache[s] = (val0, val1)
    for i in range(h):
        for j in range(h):
            A0[i, j], A1[i, j] = cache[i + j]
    return A0, A1


# ---------------------------------------------------------------------------
# Exact helpers: valuations, content, interpolation, determinants
# ---------------------------------------------------------------------------
INF = math.inf


def vp_int(a: int, p: int):
    a = abs(int(a))
    if a == 0:
        return INF
    v = 0
    while a % p == 0:
        a //= p
        v += 1
    return v


def vp(x, p: int):
    """p-adic valuation of a rational number (+inf at zero)."""
    x = x if isinstance(x, fmpq) else fmpq(x)
    if x == 0:
        return INF
    return vp_int(int(x.p), p) - vp_int(int(x.q), p)


def primes_upto(n: int) -> list[int]:
    if n < 2:
        return []
    sieve = bytearray([1]) * (n + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            sieve[i * i :: i] = bytearray(len(sieve[i * i :: i]))
    return [i for i, f in enumerate(sieve) if f]


def coefficients(poly: fmpq_poly) -> list[fmpq]:
    return [poly[k] for k in range(poly.degree() + 1)]


def content(poly: fmpq_poly) -> fmpq:
    """Positive rational content: poly / content(poly) is a primitive integer polynomial."""
    num, den = fmpz(0), fmpz(1)
    for c in coefficients(poly):
        if c != 0:
            num = num.gcd(c.p)
            den = den.lcm(c.q)
    if num == 0:
        raise ValueError("content of the zero polynomial is undefined")
    return fmpq(num, den)


def gauss_valuation(poly: fmpq_poly, p: int):
    vals = [vp(c, p) for c in coefficients(poly) if c != 0]
    return min(vals) if vals else INF


def log_abs_rational(x) -> float:
    x = x if isinstance(x, fmpq) else fmpq(x)
    return math.log(abs(int(x.p))) - math.log(int(x.q))


def interpolate(xs, ys) -> fmpq_poly:
    """Exact Lagrange interpolation (Newton form) over Q."""
    n = len(xs)
    coef = list(ys)
    for j in range(1, n):
        for i in range(n - 1, j - 1, -1):
            coef[i] = (coef[i] - coef[i - 1]) / (xs[i] - xs[i - j])
    X = fmpq_poly([0, 1])
    poly = fmpq_poly([coef[-1]])
    for i in range(n - 2, -1, -1):
        poly = poly * (X - xs[i]) + coef[i]
    return poly


def det_poly(A0: fmpq_mat, A1: fmpq_mat) -> fmpq_poly:
    """Exact det(A0 + X*A1) as a polynomial in X (degree <= size), by interpolation."""
    h = A0.nrows()
    xs = [fmpq(t) for t in range(h + 1)]
    ys = [(A0 + t * A1).det() for t in xs]
    return interpolate(xs, ys)


def load_polynomials(cname: str):
    """Yield (n, Q_n) for the polynomials stored by compute_hankel_polynomials.py."""
    d = DATA_DIR / SLUG[cname]
    for f in sorted(d.glob("Q_*.json")):
        data = json.loads(f.read_text())
        coeffs = []
        for s in data["coefficients_ascending"]:
            if "/" in s:
                a, b = s.split("/")
                coeffs.append(fmpq(int(a), int(b)))
            else:
                coeffs.append(fmpq(int(s)))
        yield data["n"], fmpq_poly(coeffs)



def normalization(case: Case, n: int) -> fmpq:
    h, K, A = case.H * n, case.C * n, case.B * n
    S = fmpq(math.factorial(K), math.factorial(A) ** 3)
    F = math.prod(math.factorial(i) ** 2 for i in range(h))
    return S**h / F
