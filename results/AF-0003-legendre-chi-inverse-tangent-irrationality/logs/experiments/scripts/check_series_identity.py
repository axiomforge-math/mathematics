"""Direct check of mu_xi(phi u^s) = sum_{m>=1} w^m (phi u^s)'(m) for both constructions,
with exact rational derivatives (no numerical differentiation, no series acceleration).
Manuscript, Lemma 2.2 and Appendix B.1. Numerical evidence only, at 1500 decimal digits.
Exit status 1 if a relative error exceeds 1e-1000.

Usage: python check_series_identity.py"""
import sys
sys.set_int_max_str_digits(0)
import os
from fractions import Fraction as Fr
import mpmath as mp
from define_half_integer_pencils import Pencil, matrices
mp.mp.dps = 1500
def check(q, sigma, cons, n=1, M=600):
    P = Pencil(q, sigma, cons); h, K, A = P.sizes(n)
    A0, A1 = matrices(P, n)
    y = mp.mpf(q)/2; w = sigma/y**2
    xi = mp.fsum(sigma**j*y**(-2*j-1)/(2*j+1)**2 for j in range(1200))
    worst = 0
    for s in (0, 1, h-1, 2*h-3, 2*h-2):
        i, j = (s, 0) if s < h else (h-1, s-h+1)
        val = mp.mpf(int(A0[i,j].p))/int(A0[i,j].q) + xi*mp.mpf(int(A1[i,j].p))/int(A1[i,j].q)
        tot = mp.mpf(0)
        for m in range(1, M+1):
            # phi(u) u^s = u^{s+1} prod (u-j)^2 / prod (u+k+1/2); derivative via exact rationals
            num = Fr(m)**(s+1); 
            for t in range(1, A+1): num *= (m-t)**2
            den = Fr(1)
            for k in range(K): den *= Fr(2*m+2*k+1, 2)
            f = num/den
            if f == 0:
                # double zero at m in 1..A: derivative also zero
                continue
            ld = Fr(s+1, m) + sum(Fr(2, m-t) for t in range(1, A+1)) - sum(Fr(2, 2*m+2*k+1) for k in range(K))
            d = f*ld
            tot += (mp.mpf(w))**m * mp.mpf(d.numerator)/d.denominator
        rel = abs(val - tot)/max(abs(tot), mp.mpf(10)**-150)
        worst = max(worst, rel)
    print(f"q={q} sigma={sigma} {cons} n={n}: max relative error {mp.nstr(worst, 5)}")
    return worst < mp.mpf(10) ** -1000
ok = all([check(q, s, c) for q, s, c in ((83, 1, 'general'), (83, -1, 'general'), (81, 1, 'band'), (81, -1, 'band'))])
print(f"== {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
