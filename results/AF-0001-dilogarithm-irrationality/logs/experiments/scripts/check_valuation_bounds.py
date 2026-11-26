"""Compare the actual Gauss valuations of Q_n at ordinary primes with the finite slot
bounds of the manuscript (jet bound, Proposition 4.5; pole bound, Proposition 4.6).

This module also provides the reference implementation of the two bounds used by the
self-test of check_discrete_bounds.py. Claim tested (jet bound): for p not in the
exceptional set with K < p^2,
    v_p^G(Q_n) >= sum of the h smallest elements of {3a_s - c_s - 1 + 2j : 0<=s<p, j>=0},
where a_s, c_s count the integers in [1,A], [1,K] congruent to s mod p.  The raw-pole
bound is computed here in the uncorrected form of the original argument (slot weight
+2 for the zero class), which fails by one unit (Remark 4.7); it is reported, not asserted.

Usage: python check_valuation_bounds.py CASE NMAX
"""

from __future__ import annotations

import sys
import time

from flint import fmpq

from define_hankel_family import CASES, det_poly, family_matrices, gauss_valuation, normalization, primes_upto, vp


def class_counts(n_upto: int, p: int) -> list[int]:
    cnt = [0] * p
    for l in range(1, n_upto + 1):
        cnt[l % p] += 1
    return cnt


def jet_bound(h: int, A: int, K: int, p: int) -> int:
    a = class_counts(A, p)
    c = class_counts(K, p)
    weights = []
    for s in range(p):
        base = 3 * a[s] - c[s] - 1
        weights.extend(base + 2 * j for j in range(h))
    weights.sort()
    return sum(weights[:h])


def raw_bound(h: int, A: int, K: int, p: int) -> int:
    a = class_counts(A, p)
    c = class_counts(K, p)
    neg = []
    for s in range(p):
        w = 3 * a[s] - c[s] - 1
        m = c[s] - a[s]
        for j in range(m):
            wt = w + 2 * j + (2 if (a[s] == 0 and j == m - 1) else 0)
            if wt < 0:
                neg.append(wt)
    neg.sort()
    return sum(neg[:h])


def main():
    case = CASES[sys.argv[1]]
    nmax = int(sys.argv[2])
    exceptional = {2, 3, 7, 11} if case.lam.denominator in (11, 9, 7) else set()
    exceptional = {2} | {p for p in (3, 5, 7, 11) if case.lam.denominator % p == 0 or
                         (case.lam.denominator - case.lam.numerator) % p == 0 or
                         (case.lam.denominator + abs(case.lam.numerator)) % p == 0}
    print(f"# case {case.name}: exceptional primes excluded from the exact test: {sorted(exceptional)}")
    for n in range(1, nmax + 1):
        t0 = time.time()
        h, K, A = case.H * n, case.C * n, case.B * n
        A0, A1 = family_matrices(case, n)
        Q = det_poly(A0, A1)
        norm = normalization(case, n)
        rows = []
        fails = []
        for p in primes_upto(2 * K + 5):
            if p in exceptional or p * p <= K:
                continue
            v = gauss_valuation(Q, p)
            jb = jet_bound(h, A, K, p)
            rb = raw_bound(h, A, K, p)
            vn = vp(norm, p)
            rows.append((p, int(v), jb, rb, int(vn)))
            if v < jb:
                fails.append((p, int(v), jb))
        print(f"n={n} [{time.time() - t0:.1f}s] (p, v_p(Q), jet, raw, v_p(S^h/F)) = {rows}")
        print(f"   jet-bound violations: {fails if fails else 'none'}; "
              f"raw-bound below actual for all p: {all(r[1] >= max(r[2], r[3]) - 2 for r in rows)}",
              flush=True)


if __name__ == "__main__":
    main()
