"""EXPLORATORY: the exceptional and small-prime finite bounds versus the exact Q_n.

Appendix C, items (c) and (d). Finite bounds of Propositions 3.1, 3.2, 3.3 and 3.5 of the
manuscript, with L = floor(log_p(Lmax)),
Lmax = 11n (2/11) or 2h + 3A (others):
    ordinary p <= K           : v_p(Qt) >= -2hL
    p = 2                     : v_2(Qt) >= -(sum of the h largest pole indices l <= K) - 2hL
    loss prime P (exponent f) : v_P(Qt) >= -f sum_{i<h} (2i - (K-3A) + 1)_+ - 2hL
    gain prime G (e=v_G(1/l)) : v_G(Qt) >= e sum_{k=0}^{h-2} (A + 1 + floor(k/3)) - 2hL
    ordinary p > K            : v_p(Qt) >= 0
Exit status 1 if any bound fails on the available data.

Usage: python check_exceptional_primes.py [CASE ...]
"""

from __future__ import annotations

import sys

sys.set_int_max_str_digits(0)

from define_parameters import CASES, Case  # noqa: E402
from check_discrete_bounds import load_Q, primes_upto, v_norm, vp_frac  # noqa: E402


def floor_log(p, x):
    L = 0
    while p ** (L + 1) <= x:
        L += 1
    return L


def check(case: Case) -> list:
    bad = []
    print(f"# case {case.name}: P={case.P} (f={case.fP}), G={case.G} (e={case.eG})")
    for n, coeffs in load_Q(case):
        h, K, A = case.H * n, case.C * n, case.B * n
        Lmax = 11 * n if case.name == "2/11" else 2 * h + 3 * A
        nz = [c for c in coeffs if c != 0]
        worst = {}
        plist = sorted(set(primes_upto(K)) | {2, case.P, case.G})
        for p in plist:
            v = min(vp_frac(c, p) for c in nz) + v_norm(h, K, A, p)
            L = floor_log(p, Lmax)
            if p == 2:
                bound = -sum(range(K - h + 1, K + 1)) - 2 * h * L
            elif p == case.P:
                bound = -case.fP * sum(max(2 * i - (K - 3 * A) + 1, 0) for i in range(h)) - 2 * h * L
            elif p == case.G:
                bound = case.eG * sum(A + 1 + k // 3 for k in range(h - 1)) - 2 * h * L
            else:
                bound = -2 * h * L
            if p in (2, case.P, case.G):
                worst[p] = (v, bound)
            if v < bound:
                bad.append((case.name, n, p, v, bound))
        # primes > K: no prime > K may divide a denominator of Qt
        import math
        from fractions import Fraction as Fr
        den = 1
        for c in nz:
            den = math.lcm(den, c.denominator)
        # Qt = norm * Q: the normalization's denominator primes are <= h <= K; check Q's
        for p in plist:  # primes <= K and the exceptional primes (which have their own bounds)
            while den % p == 0:
                den //= p
        if den != 1:
            bad.append((case.name, n, ">K", "denominator has a prime > K", den))
        print(f"  n={n:2d}: (v_p, bound) at 2,{case.P},{case.G}: "
              + ", ".join(f"{p}:({v},{b})" for p, (v, b) in sorted(worst.items()))
              + f"; primes > K in denominators: {'none' if den == 1 else den}")
    return bad


def main():
    names = sys.argv[1:] or list(CASES)
    bad = []
    for nm in names:
        bad += check(CASES[nm])
    print(f"== violations: {bad if bad else 'none'}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
