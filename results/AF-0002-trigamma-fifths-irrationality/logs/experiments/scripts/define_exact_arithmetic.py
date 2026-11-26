"""Exact arithmetic helpers: p-adic valuations, rational content, Gauss valuations, primes
and interpolation (python-flint). Shared by the exploratory scripts of this directory.

Conventions: vp(0, p) = +inf; the content of a nonzero rational polynomial Q is the positive
rational c such that Q / c is a primitive integer polynomial; the Gauss valuation at p is the
minimum of the p-adic valuations of the coefficients.
"""

from __future__ import annotations

import math

from flint import fmpq, fmpq_poly, fmpz

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


def floor_log(p: int, x: int) -> int:
    """Largest L >= 0 with p^L <= x (0 if x < p)."""
    L = 0
    while p ** (L + 1) <= x:
        L += 1
    return L


def coefficients(poly: fmpq_poly) -> list[fmpq]:
    return [poly[k] for k in range(poly.degree() + 1)]


def content(poly: fmpq_poly) -> fmpq:
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
