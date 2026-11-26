"""Rigorous ball-arithmetic (Arb) check of the six strict margins A_sigma(a, q0) - B > m.

For each row of ../certificates/comparison_densities.json (step density rho on the mesh 1/mesh with masses
m_i / M, and a rational lambda):

  B = C - E(rho) + lambda + 2 int_0^1 (G - lambda)_+ dx,
  G(x) = 2 U(x) + x log W + psi(x) - psi(x + kappa),   W = (a/q)^2,
  C = kappa log kappa + 3/2 - kappa,   psi(t) = t log|t| - t,

  A (a odd)      = I_kappa - (2 kappa - 1) log a + (1/3) log q - D log(q^2 - sigma a^2)
                   + C_sigma log 2,  C_+ = 2(kappa - 1) + 2D, C_- = kappa - 1,
  A (a = 2^e)    = I_kappa + C_e(kappa) log 2 + (1/3) log q - D log(q^2 + a^2),
  D = (2 - kappa)^2 / 4,
  C_e(kappa) = min_{0<=x<=1} 2(kappa-1) - 2(e+1) kappa x + (e+2) x^2 + (e/2+2)(1-x)^2.

Independent of the fixed-point verifier that produced the candidate certificates: logarithms are Arb balls; the
cell bound is  sup_cell G <= max(endpoint values) + sum_terms |c_j| dev_j  with
dev_j <= l^2/(8 dist) (singularity off the cell) and <= l/e (singularity at an endpoint).

Usage: decay_ball.py [L] [--shift]     (L = fine grid, default 24000)
  --shift : additionally evaluate the same density at larger admissible q with
            lambda' = lambda - log(q/q0) and check the propagation inequality
            margin(q) >= margin(q0) + (1/6) log(q/q0) numerically (consistency only).
Exit status 1 if any margin fails.
"""
import json, os, sys
from fractions import Fraction as Fr
from math import gcd
from flint import arb, ctx
ctx.prec = 200

I_KAPPA = {Fr(7, 6): Fr(-2113164137, 10**9), Fr(5, 4): Fr(-2355639833, 10**9)}
MARGIN = {(3, 131, 1): Fr(13, 1000), (3, 257, -1): Fr(1, 200), (4, 995, -1): Fr(1, 625),
          (5, 829, 1): Fr(3, 2500), (5, 1609, -1): Fr(7, 10000), (8, 12061, -1): Fr(7, 10000)}


def psi(t):
    return arb(0) if t == 0 else t * abs(t).log() - t


def g2(t):  # double primitive of log|t|
    return arb(0) if t == 0 else t * t * abs(t).log() / 2 - 3 * t * t / 4


def q2a(x):
    x = Fr(x)
    return arb(x.numerator) / x.denominator


def c_even(e, kap):
    x = min(Fr(1), ((e + 1) * kap + Fr(e, 2) + 2) / (Fr(3 * e, 2) + 4))
    return 2 * (kap - 1) - 2 * (e + 1) * kap * x + (e + 2) * x * x + (Fr(e, 2) + 2) * (1 - x) ** 2


def arithmetic_lower(a, q, sign, kap):
    D = (2 - kap) ** 2 / 4
    I = q2a(I_KAPPA[kap])
    if a % 2:
        C2 = 2 * (kap - 1) + 2 * D if sign == 1 else kap - 1
        A = I - q2a(2 * kap - 1) * arb(a).log() + arb(q).log() / 3 \
            - q2a(D) * arb(q * q - sign * a * a).log() + q2a(C2) * arb(2).log()
    else:
        e = a.bit_length() - 1
        assert a == 2 ** e
        A = I + q2a(c_even(e, kap)) * arb(2).log() + arb(q).log() / 3 - q2a(D) * arb(q * q + a * a).log()
    return A


class Density:
    def __init__(self, rec, L):
        self.mesh, self.M, self.ms = rec['mesh'], rec['mass_den'], rec['masses']
        self.kap = Fr(rec['kappa'])
        self.L = L
        ms, mesh, M, kap = self.ms, self.mesh, self.M, self.kap
        assert len(ms) <= mesh and sum(ms) == M and all(0 <= m * mesh <= 2 * M for m in ms)
        assert L % mesh == 0 and (kap * L).denominator == 1
        step = L // mesh
        nz = [(i, m) for i, m in enumerate(ms) if m]
        cache = {}

        def G2(k):
            if k not in cache:
                cache[k] = g2(q2a(Fr(k, mesh)))
            return cache[k]
        E = arb(0)
        for i, x in nz:
            for j, y in nz:
                d = i - j
                E += (x * y) * (G2(d + 1) + G2(d - 1) - 2 * G2(d))
        self.E = E * (mesh * mesh) / (M * M)
        C = {}

        def add(j, c):
            C[j] = C.get(j, Fr(0)) + c
        for i, m in nz:
            add(i * step, Fr(2 * mesh * m, M)); add((i + 1) * step, -Fr(2 * mesh * m, M))
        add(0, Fr(1)); add(-int(kap * L), Fr(-1))
        self.C = {j: c for j, c in C.items() if c}
        tab = {}

        def P(d):
            if d not in tab:
                tab[d] = psi(arb(d) / L)
            return tab[d]
        self.G0 = []       # G without the x log W term, at k/L
        for k in range(L + 1):
            v = arb(0)
            for j, c in self.C.items():
                v += q2a(c) * P(k - j)
            self.G0.append(v)
        self.dev = []
        for k in range(L):
            dev = Fr(0)
            for j, c in self.C.items():
                if j == k or j == k + 1:
                    dev += abs(c) * Fr(10, 27 * L)      # l/e < 10 l/27
                else:
                    dev += abs(c) / (8 * L * min(abs(k - j), abs(k + 1 - j)))
            self.dev.append(q2a(dev).upper())
        self.Cst = q2a(kap) * q2a(kap).log() + q2a(Fr(3, 2) - kap)

    def B_upper(self, a, q, lam):
        """lam: arb.  Returns an arb upper bound for B at W = (a/q)^2."""
        L = self.L
        lW = 2 * (arb(a) / q).log()
        assert 1 + lW < 0 and lW < lam, 'tail conditions fail'
        vals = [(self.G0[k] + arb(k) / L * lW).upper() for k in range(L + 1)]
        total = arb(0)
        for k in range(L):
            diff = max(vals[k], vals[k + 1]) + self.dev[k] - lam
            if diff > 0:
                total += diff
        return (self.Cst - self.E + lam + 2 * total / L).upper()


def main():
    args = [x for x in sys.argv[1:] if not x.startswith('--')]
    L = int(args[0]) if args else 24000
    here = os.path.dirname(os.path.abspath(__file__))
    data = json.load(open(os.path.join(here, '..', 'certificates', 'comparison_densities.json')))
    ok = True
    for rec in data:
        a, q, sign = rec['a'], rec['q'], rec['sign']
        kap = Fr(rec['kappa'])
        assert gcd(a, q) == 1 and q % 2 == 1 and q >= 2 * a and 2 * q >= 83 * a
        den = Density(rec, L)
        lam = q2a(Fr(rec['lambda_num'], rec['lambda_den']))
        B = den.B_upper(a, q, lam)
        A = arithmetic_lower(a, q, sign, kap).lower()
        m = A - B                      # arb; lower() is a rigorous lower bound of the margin
        need = MARGIN[(a, q, sign)]
        good = bool(m > q2a(need))
        ok &= good
        print(f"a={a} q={q} sigma={sign:+d} kappa={kap}: E={den.E.str(12)} B<={B.str(12)} "
              f"A>={A.str(12)} margin>={m.lower().str(10)} need>{need} {'PASS' if good else 'FAIL'}", flush=True)
        if '--shift' in sys.argv:
            for q2 in (q + 2, q + 12, 2 * q + 1, 10 * q + 1, 1000 * q + 1):
                while gcd(a, q2) != 1 or q2 % 2 == 0:
                    q2 += 1
                t = (arb(q2) / q).log()
                B2 = den.B_upper(a, q2, lam - t)
                A2 = arithmetic_lower(a, q2, sign, kap).lower()
                m2 = A2 - B2
                good2 = bool(m2 > m.lower() + t / 6 - arb(10) ** -12)
                dB = bool(B2 <= B - t / 2 + t / L + arb(10) ** -12)   # t/L: discretisation of int (1/2 - x)_+
                ok &= good2 and dB
                print(f"    q={q2}: margin>={m2.lower().str(8)}  (margin(q0)+log(q/q0)/6 = {(m.lower() + t / 6).str(8)}) "
                      f"B(q) <= B(q0) - log(q/q0)/2 + log(q/q0)/L: {dB} {'ok' if good2 else 'FAIL'}", flush=True)
    print('ALL PASS' if ok else 'FAILURE')
    sys.exit(0 if ok else 1)


main()
