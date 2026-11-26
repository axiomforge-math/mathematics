"""Audit of the separated-border identity and its 2-adic consequences.

Proposition 2.6 and Corollary 2.8 (Remark 2.10). Checks, for h = 16, 32, ... (m = h/16),
k in {1,2,3,4} and the deletions I in {(), (0,), (h-1,)}:
  (1)  P_sep,I(X) = 2^{-m(m-1)} P_alt,I(X) identically in X (sign +1 for increasing orderings);
  (2)  v_2 of the separated pencil >= -n * 2 floor(log_2(5N))   [entry bound, Lemma 4.2];
  (3)  odd-prime Gauss valuations of the two pencils agree;
and reports the normalized log content and log |P_sep(xi)| with Arb balls. Exit status 1 if
(1), (2) or (3) fails in some case.

Usage: python check_separation_identity.py HMAX [K]
"""

from __future__ import annotations

import math
import sys
import time

from flint import arb_poly, ctx, fmpq

from define_exact_arithmetic import content, floor_log, gauss_valuation, log_abs_rational, primes_upto
from define_lowner_family import det_pencil, pencil, xi_ball


def log_abs_at_xi(P, k):
    c = content(P)
    Pz = P / c
    coeffs = [int(Pz[i].p) for i in range(Pz.degree() + 1)]
    prec = max(abs(x).bit_length() for x in coeffs) + 256
    while True:
        xi = xi_ball(k, prec)
        v = arb_poly(coeffs)(xi)
        if not v.contains(0):
            lg = abs(v).log()
            if lg.rad() < 1e-6:
                return float(lg.mid()), log_abs_rational(c)
        prec *= 2


def main():
    hmax = int(sys.argv[1])
    ks = [int(sys.argv[2])] if len(sys.argv) > 2 else [1, 2, 3, 4]
    failures = 0
    for h in range(16, hmax + 1, 16):
        m = h // 16
        N, n = h + 2 * m, h + m
        for k in ks:
            for removed in [(), (0,), (h - 1,)]:
                t0 = time.time()
                A0s, A1s, cs = pencil(k, h, "separated", removed)
                A0a, A1a, ca = pencil(k, h, "alternating", removed)
                Ps = det_pencil(A0s, A1s, cs)
                Pa = det_pencil(A0a, A1a, ca)
                ratio = None
                if Pa != 0:
                    r = [Ps[i] / Pa[i] for i in range(Pa.degree() + 1) if Pa[i] != 0]
                    ratio = r[0] if all(x == r[0] for x in r) and Ps.degree() == Pa.degree() else "NOT PROPORTIONAL"
                expected = fmpq(1, 2 ** (m * (m - 1)))
                ok1 = ratio == expected
                v2s = gauss_valuation(Ps, 2)
                bound2 = -n * 2 * floor_log(2, 5 * N)
                odd_ok = all(gauss_valuation(Ps, p) == gauss_valuation(Pa, p) for p in primes_upto(5 * N + 10) if p > 2)
                line = (f"h={h} k={k} I={removed}: ratio={ratio} expected=2^-{m*(m-1)} identity={'OK' if ok1 else 'FAIL'}"
                        f" v2(sep)={v2s} (bound {bound2}) v2(alt)={gauss_valuation(Pa, 2)} odd-primes-equal={odd_ok}")
                if removed == ():
                    lv, lc = log_abs_at_xi(Ps, k)
                    line += (f" | log cont/h^2={lc / h**2:.4f} log|P_sep(xi)|/h^2={(lv + lc) / h**2:.4f}"
                             f" log|prim(xi)|/h^2={lv / h**2:.4f}")
                failures += (not ok1) or (not odd_ok) or (v2s < bound2)
                print(line + f" [{time.time() - t0:.1f}s]", flush=True)
    print(f"== failures: {failures}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
