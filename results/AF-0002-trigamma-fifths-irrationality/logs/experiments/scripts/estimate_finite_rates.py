#!/usr/bin/env python
"""Exploratory (NOT a certificate): finite-h trends of the separated pencil P_sep(X).

For h = 16 m and k = 1..4 (no deletion) report, per h^2:
  lden   = log den(content(P_sep))           (all primes)
  lden_* = same restricted to primes p > sqrt(5N), p != 2, 5  (the part bounded by A)
  lval   = log |P_sep(xi)|                    (Arb ball, xi = psi_1(k/5) - pi^2/2)
  gap    = lden + lval                        (must tend to <= A - D_sep < 0 for the proof)
Compare lden_* with A = 3.5121304 and lval with -D_sep <= -3.512607 (claimed limsup bounds).

Usage: python estimate_finite_rates.py H1 H2 ...
"""

from __future__ import annotations

import math
import sys
import time

from flint import arb, arb_poly, ctx, fmpz

from define_exact_arithmetic import content, gauss_valuation, primes_upto
from compute_separated_pencils import pencil_poly


def xi_ball(k: int, prec: int):
    ctx.prec = prec
    return arb(2).zeta(arb(k) / 5) - arb.pi() ** 2 / 2


def log_abs_at_xi(P, k):
    c = content(P)
    Pz = P / c
    coeffs = [int(Pz[i].p) for i in range(Pz.degree() + 1)]
    assert all(int(Pz[i].q) == 1 for i in range(Pz.degree() + 1))
    prec = max(abs(x).bit_length() for x in coeffs) + 256
    while True:
        xi = xi_ball(k, prec)
        v = arb_poly(coeffs)(xi)
        if not v.contains(0):
            lg = abs(v).log()
            if lg.rad() < 1e-9:
                ctx.prec = 53
                return float(lg.mid()), c
        prec *= 2


def main():
    hs = [int(t) for t in sys.argv[1:]]
    print("h k | lden lden_big lden_small | lval | gap | lprim(xi)   (all per h^2)", flush=True)
    for h in hs:
        m = h // 16
        N = h + 2 * m
        for k in (1, 2, 3, 4):
            t0 = time.time()
            P = pencil_poly(k, h, "separated")
            lv, c = log_abs_at_xi(P, k)
            den = int(c.q)
            lden = math.log(den)
            big = 0.0
            for p in primes_upto(5 * N):
                if p in (2, 5) or p * p <= 5 * N:
                    continue
                v = gauss_valuation(P, p)
                if v < 0:
                    big += -v * math.log(p)
            lc = math.log(int(c.p)) - lden
            lval = lv + lc
            H = h * h
            print("%d %d | %.5f %.5f %.5f | %.5f | %.5f | %.5f   [%.0fs]"
                  % (h, k, lden / H, big / H, (lden - big) / H, lval / H, (lden + lval) / H, lv / H, time.time() - t0),
                  flush=True)


if __name__ == "__main__":
    main()
