"""EXPLORATORY (floating point, mpmath): do the closed-form external fields used by the
comparison-measure certificates match the actual finite weights?

Positive arguments (u = n for 2/11, u = h for 2/9), site x = u y:
    beta_x = x lambda^x W_n(x),   claim: log|beta_x| = -d' u log u + u V(y) + O(log(u + x))
Negative arguments (u = h), z = 1/2 + h c y:
    claim (Lemma 8.3): log|z W_n(z) k'(z)| <= -d h log h + h V_-(y) + O(log(h + hy)),
    k(z) = pi csc(pi z) exp(-t z),  k'(z) = -k(z) (pi cot(pi z) + t).
We print  D(y) = [log|actual| + d' u log u]/u - V(y)  for increasing u; it should be
O(log u / u) (here: D * u / log u stays bounded).  Not used in any assertion.

Usage: python check_external_fields.py
"""

from __future__ import annotations

import mpmath as mp

from define_parameters import CASES

mp.mp.dps = 40


def logabs_prod_shift(z, N):
    """sum_{j=1}^N log|z + j| = Re( loggamma(z+N+1) - loggamma(z+1) )."""
    return mp.re(mp.loggamma(z + N + 1) - mp.loggamma(z + 1))


def V_pos(case, y):
    al, ka = mp.mpf(case.alpha.numerator) / case.alpha.denominator, mp.mpf(case.kappa.numerator) / case.kappa.denominator
    t = mp.log(1 / abs(mp.mpf(case.lam.numerator) / case.lam.denominator))

    def F(s):
        return 0 if s == 0 else s * mp.log(abs(s))
    return 3 * F(y + al) - 2 * F(y) - F(y + ka) + (ka - 3 * al) - t * y


def V_neg(case, c, y):
    al, ka = mp.mpf(case.alpha.numerator) / case.alpha.denominator, mp.mpf(case.kappa.numerator) / case.kappa.denominator
    t = mp.log(1 / abs(mp.mpf(case.lam.numerator) / case.lam.denominator))
    T = mp.re(c) * t + mp.im(c) * mp.pi

    def zl(z):
        return 0 if z == 0 else z * mp.log(z)
    return (ka - 3 * al) + mp.re(3 * zl(c * y + al) - 2 * zl(c * y) - zl(c * y + ka)) - T * y


def positive(name):
    case = CASES[name]
    lam = mp.mpf(case.lam.numerator) / case.lam.denominator
    print(f"# {name}: D(y) = [log|beta_x| + d' u log u]/u - V(y), x = round(u y)")
    for y in (0.05, 0.25, 1.0, 3.0, 8.0):
        row = []
        for n in (100, 1000, 10000):
            u = n * case.scale
            h, K, A = case.H * n, case.C * n, case.B * n
            x = max(1, int(round(u * y)))
            lb = mp.log(x) + x * mp.log(lam) + 3 * logabs_prod_shift(mp.mpf(x), A) - logabs_prod_shift(mp.mpf(x), K)
            dprime = (case.kappa - 3 * case.alpha)
            D = (lb + float(dprime) * u * mp.log(u)) / u - V_pos(case, mp.mpf(x) / u)
            row.append(f"u={u}: D={float(D):+.5f} (D*u/log u={float(D * u / mp.log(u)):+.2f})")
        print(f"  y={y}: " + "; ".join(row))


def negative(name, c):
    case = CASES[name]
    lam = mp.mpf(case.lam.numerator) / case.lam.denominator
    t = mp.log(1 / abs(lam))
    d = float(case.kappa - 3 * case.alpha)
    print(f"# {name}: D(y) = [log|z W(z) k'(z)| + d h log h]/h - V_-(y), z = 1/2 + h c y")
    for y in (0.0, 0.02, 0.2, 0.6, 1.5):
        row = []
        for n in (100, 1000, 10000):
            h, K, A = case.H * n, case.C * n, case.B * n
            z = mp.mpf(1) / 2 + h * c * y
            k = mp.pi / mp.sin(mp.pi * z) * mp.exp(-t * z)
            kp = -k * (mp.pi * mp.cot(mp.pi * z) + t)
            lw = 3 * logabs_prod_shift(z, A) - logabs_prod_shift(z, K)
            tot = mp.log(abs(z)) + lw + mp.log(abs(kp))
            D = (tot + d * h * mp.log(h)) / h - V_neg(case, c, mp.mpf(y))
            row.append(f"h={h}: D={float(D):+.5f} (D*h/log h={float(D * h / mp.log(h)):+.2f})")
        print(f"  y={y}: " + "; ".join(row))


if __name__ == "__main__":
    positive("2/11")
    positive("2/9")
    negative("-2/9", mp.mpc(4, 3) / 5)
    negative("-2/7", mp.mpc(21, 20) / 29)
