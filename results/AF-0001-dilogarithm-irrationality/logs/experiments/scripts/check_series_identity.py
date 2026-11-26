"""Lemma 2.2 on sample entries (Appendix C, item (a)): Lambda_xi(W x^s) computed from the
exact affine matrices agrees with the defining series sum_x lambda^x (x W(x) x^s)'.

Floating point with 80 digits (mpmath); numerical evidence only. Exit status 1 if a
relative difference exceeds 1e-40.

Usage: python check_series_identity.py
"""
import sys
import mpmath as mp
from define_hankel_family import CASES, family_matrices
mp.mp.dps = 80
bad = []
for cname, case in CASES.items():
    n = 1
    A0, A1 = family_matrices(case, n)
    lam = mp.mpf(case.lam.numerator) / case.lam.denominator
    xi = mp.polylog(2, lam)
    A, K = case.B * n, case.C * n
    for s in (0, 3, 2 * case.H * n - 2):
        i, j = (s, 0) if s < case.H * n else (case.H * n - 1, s - case.H * n + 1)
        exact = mp.mpf(int(A0[i, j].p)) / int(A0[i, j].q) + xi * mp.mpf(int(A1[i, j].p)) / int(A1[i, j].q)
        def R(x):
            return mp.fprod([(x + t) ** 3 for t in range(1, A + 1)]) * x**s / mp.fprod([(x + t) for t in range(1, K + 1)])
        ser = mp.nsum(lambda x: lam**x * mp.diff(lambda t: t * R(t), x), [1, mp.inf])
        print(cname, s, mp.nstr(exact, 25), mp.nstr(ser, 25), "diff", mp.nstr(exact - ser, 5))
        if abs(exact - ser) > mp.mpf(10) ** -40 * abs(ser):
            bad.append((cname, s))
print(f"== entries with relative difference above 1e-40: {bad if bad else 'none'}")
sys.exit(1 if bad else 0)
