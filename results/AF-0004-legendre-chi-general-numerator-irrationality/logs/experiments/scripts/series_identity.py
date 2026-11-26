"""Direct check of Lemma 2.2 (pole series): mu_xi(phi u^s) = sum_{m>=1} w^m (phi u^s)'(m),
with exact rational derivatives and xi summed to high precision (mpmath, 700 digits).
A numerical consistency check; exit status 1 if a relative error exceeds 1e-500."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction as Fr
import mpmath as mp
from pencil import Pencil
mp.mp.dps = 700


def check(a, q, sigma, t, c, n=1, M=260):
    P = Pencil(a, q, sigma, t, c)
    h, K = t * n, c * n
    A0, A1 = P.matrices(n)
    y = mp.mpf(q) / a
    w = sigma / y ** 2
    xi = mp.fsum(sigma ** j * y ** (-2 * j - 1) / (2 * j + 1) ** 2 for j in range(600))
    worst = mp.mpf(0)
    for s in (0, 1, h - 1, 2 * h - 3, 2 * h - 2):
        i, j = (s, 0) if s < h else (h - 1, s - h + 1)
        val = mp.mpf(int(A0[i, j].p)) / int(A0[i, j].q) + xi * mp.mpf(int(A1[i, j].p)) / int(A1[i, j].q)
        tot = mp.mpf(0)
        for m in range(1, M + 1):
            den = Fr(1)
            for k in range(K):
                den *= Fr(2 * m + 2 * k + 1, 2)
            f = Fr(m) ** (s + 1) / den
            d = f * (Fr(s + 1, m) - sum(Fr(2, 2 * m + 2 * k + 1) for k in range(K)))
            tot += w ** m * mp.mpf(d.numerator) / d.denominator
        worst = max(worst, abs(val - tot) / abs(tot))
    print(f"a={a} q={q} sigma={sigma:+d} (t,c)=({t},{c}) n={n}: max relative error {mp.nstr(worst, 5)}", flush=True)
    return worst < mp.mpf(10) ** -500


ok = all([check(3, 131, 1, 6, 7), check(3, 257, -1, 4, 5), check(4, 995, 1, 4, 5), check(4, 995, -1, 4, 5),
          check(5, 829, 1, 4, 5), check(5, 1609, -1, 4, 5), check(8, 12061, 1, 4, 5), check(8, 12061, -1, 4, 5)])
sys.exit(0 if ok else 1)
