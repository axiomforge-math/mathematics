"""EXPLORATORY: the finite-n sum of the per-prime lower bounds of Sections 3 and 4.

    L_n = sum_p b_p(n) log p,   with b_p(n) the finite lower bound for v_p(Qt_n):
      p = 2, P, G           : the exceptional finite bounds (see check_exceptional_primes.py)
      other p, p^2 <= K     : -2hL
      other p <= K, p^2 > K : v_p(S^h/F) + max(jet, raw - 1)
                              (raw - 1: the uncorrected pole bound minus one unit,
                               a simplification of the correction of Remark 4.7;
                               see check_discrete_bounds.py part 2)
      p > K                 : 0
The asymptotic claim (Theorem 5.5 with the certificates of Section 5.4) is
    liminf L_n / u^2 = claimed content rate,
so L_n/u^2 for large n (no determinant needed) tests the prime-sum step numerically,
and actual c_n >= L_n/u^2 on cached Q_n tests the finite bounds jointly.
Also prints the decomposition into ordinary/exceptional parts.

Usage: python compute_bound_sequence.py CASE n1 n2 ...
"""

from __future__ import annotations

import json
import math
import sys
from collections import Counter
from fractions import Fraction as Fr

sys.set_int_max_str_digits(0)

from define_parameters import CASES, OUT, Case  # noqa: E402
from check_discrete_bounds import load_Q, primes_upto, vp_frac  # noqa: E402


def floor_log(p, x):
    L = 0
    while p ** (L + 1) <= x:
        L += 1
    return L


def vp_fact(N, p):
    v, q = 0, p
    while q <= N:
        v += N // q
        q *= p
    return v


def sum_vp_fact(h, p):
    """sum_{i<h} v_p(i!) = sum_k sum_{i<h} floor(i/p^k)."""
    tot, q = 0, p
    while q <= h - 1:
        Q = h // q
        tot += q * Q * (Q - 1) // 2 + Q * (h - Q * q)
        q *= p
    return tot


def v_norm(h, K, A, p):
    return h * (vp_fact(K, p) - 3 * vp_fact(A, p)) - 2 * sum_vp_fact(h, p)


def types(N_A, N_K, p):
    """Counter of (a_s, c_s) over the p residue classes (O(1))."""
    qA, rA = divmod(N_A, p)
    qK, rK = divmod(N_K, p)
    lo, hi = min(rA, rK), max(rA, rK)
    cnt = Counter()
    cnt[(qA + 1, qK + 1)] += lo
    if rA > rK:
        cnt[(qA + 1, qK)] += hi - lo
    elif rK > rA:
        cnt[(qA, qK + 1)] += hi - lo
    cnt[(qA, qK)] += p - hi
    return {k: v for k, v in cnt.items() if v}


def jet(h, ty):
    cnt = Counter()
    for (a, c), mlt in ty.items():
        cnt[3 * a - c - 1] += mlt
    left, total, v = h, 0, min(cnt)
    while left > 0:
        k = sum(cw for w, cw in cnt.items() if w <= v and (v - w) % 2 == 0)
        d = min(k, left)
        total += d * v
        left -= d
        v += 1
    return total


def raw(h, ty):
    slots = Counter()
    for (a, c), mlt in ty.items():
        w = 3 * a - c - 1
        for j in range(c - a):
            wt = w + 2 * j + (2 if (a == 0 and j == c - a - 1) else 0)
            if wt < 0:
                slots[wt] += mlt
    left, total = h, 0
    for wt in sorted(slots):
        d = min(slots[wt], left)
        total += d * wt
        left -= d
        if not left:
            break
    return total


def bounds(case: Case, n: int, primes):
    h, K, A = case.H * n, case.C * n, case.B * n
    Lmax = 11 * n if case.name == "2/11" else 2 * h + 3 * A
    out = {}
    for p in primes:
        if p > K:
            break
        L = floor_log(p, Lmax)
        if p == 2:
            b = -sum(range(K - h + 1, K + 1)) - 2 * h * L
        elif p == case.P:
            b = -case.fP * sum(max(2 * i - (K - 3 * A) + 1, 0) for i in range(h)) - 2 * h * L
        elif p == case.G:
            b = case.eG * sum(A + 1 + k // 3 for k in range(h - 1)) - 2 * h * L
        elif p * p <= K:
            b = -2 * h * L
        else:
            ty = types(A, K, p)
            b = v_norm(h, K, A, p) + max(jet(h, ty), raw(h, ty) - 1)
        out[p] = b
    return out


def main():
    name = sys.argv[1]
    case = CASES[name]
    ns = [int(x) for x in sys.argv[2:]] or [10, 30, 100, 300, 1000]
    nmax = max(ns + [30])
    primes = primes_upto(case.C * nmax + 10)
    print(f"# case {name} ({case.unit}-units); claimed limit {case.claims['content_rate_reported']}")
    res = {}
    # part A: cached n -- actual content versus the finite bound
    cached = {}
    for n, coeffs in load_Q(case):
        nz = [c for c in coeffs if c != 0]
        h, K, A = case.H * n, case.C * n, case.B * n
        u = n * case.scale
        bd = bounds(case, n, primes)
        act = {}
        for p in bd:
            act[p] = min(vp_frac(c, p) for c in nz) + v_norm(h, K, A, p)
        viol = [(p, act[p], bd[p]) for p in bd if act[p] < bd[p]]
        Ln = sum(b * math.log(p) for p, b in bd.items()) / u ** 2
        cn = sum(v * math.log(p) for p, v in act.items()) / u ** 2  # primes > K contribute >= 0
        cached[n] = dict(Ln=Ln, cn_le_K=cn, violations=viol)
        print(f"  n={n:3d}: actual sum_(p<=K) v_p log p/u^2 = {cn:9.5f}  >=  L_n/u^2 = {Ln:9.5f} ?"
              f"  {'yes' if cn >= Ln else 'NO'}   per-prime violations: {viol if viol else 'none'}")
    # part B: large n
    print("     n        u     L_n/u^2   [ordinary p^2>K]  [small p^2<=K]  [2]   [P]   [G]")
    for n in ns:
        u = n * case.scale
        bd = bounds(case, n, primes)
        tot = sum(b * math.log(p) for p, b in bd.items()) / u ** 2
        K = case.C * n
        parts = dict(
            ordinary=sum(b * math.log(p) for p, b in bd.items() if p not in (2, case.P, case.G) and p * p > K) / u ** 2,
            small=sum(b * math.log(p) for p, b in bd.items() if p not in (2, case.P, case.G) and p * p <= K) / u ** 2,
            two=bd[2] * math.log(2) / u ** 2,
            P=bd[case.P] * math.log(case.P) / u ** 2,
            G=bd[case.G] * math.log(case.G) / u ** 2,
        )
        res[n] = dict(L=tot, **parts)
        print(f"  {n:6d} {u:7d}  {tot:9.5f}   {parts['ordinary']:9.5f}  {parts['small']:9.5f}  "
              f"{parts['two']:7.4f} {parts['P']:7.4f} {parts['G']:7.4f}", flush=True)
    (OUT / f"bound-sequence-{case.slug}.json").write_text(json.dumps(dict(cached=cached, large=res), indent=1, default=str))


if __name__ == "__main__":
    main()
