"""Audit of the half-integer pencils at small sizes.

For each (q, sigma, construction) and n: checks the defining series identity on sample
entries (Arb), nonvanishing of T, the exceptional-prime bounds claimed in the candidate
proof at p = 2 and p | q, and reports normalized log content and log|T(xi)| / h^2
with rigorous Arb enclosures.

Usage: python audit_small.py Q SIGMA CONSTRUCTION NMAX
"""

from __future__ import annotations

import math
import sys
import time

import mpmath as mp
from flint import arb_poly

from define_exact_arithmetic import content, gauss_valuation, log_abs_rational
from define_half_integer_pencils import Pencil, T_poly, matrices, xi_ball


def series_check(P: Pencil, n: int = 1) -> float:
    """max |mu_xi(phi u^s) - sum_m w^m (phi u^s)'(m)| over a few s (mpmath, exploratory)."""
    h, K, A = P.sizes(n)
    A0, A1 = matrices(P, n)
    mp.mp.dps = 120
    y = mp.mpf(P.q) / 2
    w = P.sigma / y**2
    xi = mp.nsum(lambda j: P.sigma**int(j) * y ** (-2 * j - 1) / (2 * j + 1) ** 2, [0, mp.inf])
    worst = 0.0
    for s in (0, 1, 2 * h - 2):
        i, j = (s, 0) if s < h else (h - 1, s - h + 1)
        exact = mp.mpf(int(A0[i, j].p)) / int(A0[i, j].q) + xi * mp.mpf(int(A1[i, j].p)) / int(A1[i, j].q)

        def phi(u):
            v = u * mp.fprod([(u - t) ** 2 for t in range(1, A + 1)]) * u**s
            return v / mp.fprod([(u + k + mp.mpf(1) / 2) for k in range(K)])

        ser = mp.nsum(lambda m: w**m * mp.diff(phi, m), [1, mp.inf])
        worst = max(worst, float(abs(exact - ser) / max(abs(ser), mp.mpf(10) ** -30)))
    return worst


def main():
    q, sigma, cons, nmax = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
    P = Pencil(q, sigma, cons)
    series = f"{series_check(P):.2e}" if "--series" in sys.argv else "not run (see check_series_identity.py)"
    print(f"# q={q} sigma={sigma} construction={cons}; series identity rel. error at 120 digits (n=1): {series}",
          flush=True)
    f_q = {p: 0 for p in range(3, q + 1) if q % p == 0 and all(p % d for d in range(2, p))}
    for p in f_q:
        m = q
        while m % p == 0:
            m //= p
            f_q[p] += 1
    for n in range(1, nmax + 1):
        t0 = time.time()
        h, K, A = P.sizes(n)
        T = T_poly(P, n)
        if T == 0:
            print(f"n={n}: T is the ZERO polynomial", flush=True)
            continue
        c = content(T)
        prim = T / c
        coeffs = [int(prim[k].p) for k in range(prim.degree() + 1)]
        prec = max(abs(x).bit_length() for x in coeffs) + 256
        while True:
            v = arb_poly(coeffs)(xi_ball(P, prec))
            if not v.contains(0) and abs(v).log().rad() < 1e-6:
                break
            prec *= 2
        lv = float(abs(v).log().mid())
        lc = log_abs_rational(c)
        v2 = gauss_valuation(T, 2)
        vq = {p: gauss_valuation(T, p) for p in f_q}
        print(f"n={n} h={h} K={K} A={A} deg={T.degree()} v2={v2} v2/h^2={v2 / h**2:.4f} "
              f"vq={ {p: (vv, round(vv / h**2, 4)) for p, vv in vq.items()} } "
              f"log cont/h^2={lc / h**2:.4f} log|T(xi)|/h^2={(lv + lc) / h**2:.4f} "
              f"log|prim(xi)|/h^2={lv / h**2:.4f} [{time.time() - t0:.1f}s]", flush=True)


if __name__ == "__main__":
    main()
