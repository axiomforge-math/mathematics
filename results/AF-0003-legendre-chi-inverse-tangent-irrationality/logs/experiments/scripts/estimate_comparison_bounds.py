"""Independent floating-point recomputation of the archimedean bound
   B = C - E(rho) + lam + 2 int_alpha^1 (G - lam)_+ dx,  G = 2U + V,
   V(x) = x log W + 3 psi(x) - psi(x + kappa) - 2 psi(x - alpha),
   C = kappa log kappa - 2 alpha log alpha + 3/2 - kappa + 2 alpha,
and of the arithmetic constant A_-(q) (manuscript, Appendix A.2 and Section 9).
Data: the step densities of ../certificates/ (mesh 240).
Not a certificate: double precision, used only as a cross-check of the exact verifier.

Usage: python estimate_comparison_bounds.py
"""
import json, math, sys


def psi(t):
    return 0.0 if t == 0 else t * math.log(abs(t)) - t


def g2(t):
    return 0.0 if t == 0 else t * t * math.log(abs(t)) / 2 - 0.75 * t * t


def run(rec, kap, alp, I, f2, label):
    q = rec['q']; mesh = rec['mesh']; M = rec['mass_den']; ms = rec['masses']
    lam = rec['theta_num'] / rec['theta_den']
    s = 1.0 / mesh
    rho = [mesh * m / M for m in ms]
    assert abs(sum(m for m in ms) - M) == 0
    assert all(r <= 2 + 1e-12 for r in rho)
    # energy
    E = 0.0
    nz = [(i, r) for i, r in enumerate(rho) if r]
    for i, ri in nz:
        for j, rj in nz:
            d = (i - j) * s
            E += ri * rj * (g2(d + s) + g2(d - s) - 2 * g2(d))
    W = 4.0 / q ** 2
    lW = math.log(W)

    def U(x):
        return sum(r * (psi(x - i * s) - psi(x - (i + 1) * s)) for i, r in nz)

    def G(x):
        V = x * lW + 3 * psi(x) - psi(x + kap) - 2 * psi(x - alp)
        return 2 * U(x) + V
    # integral of (G - lam)_+ on [alp, 1]: fine midpoint rule
    Nq = 48000
    h = (1 - alp) / Nq
    integ = 0.0; gmax = -1e9
    for k in range(Nq):
        x = alp + (k + 0.5) * h
        v = G(x) - lam
        gmax = max(gmax, v)
        if v > 0:
            integ += v * h
    C = kap * math.log(kap) - (2 * alp * math.log(alp) if alp else 0) + 1.5 - kap + 2 * alp
    B = C - E + lam + 2 * integ
    d = kap - 2 * alp
    A = I + f2 * math.log(2) + math.log(q) / 3 - (2 - d) ** 2 / 4 * math.log(q * q + 4)
    # tail conditions
    tail1 = lW + 1 + kap * kap / 4                       # tau_1 of the tail lemma
    tail0 = lW - kap / 2 * math.log(1 + kap / 2) - lam   # tau_0 of the tail lemma
    print(f"{label} q={q}: E={E:.9f} int(G-lam)+={integ:.9f} C={C:.9f} lam={lam} B={B:.9f} "
          f"A_-={A:.9f} B-A={B - A:.6f} tail slope={tail1:.3f} tail value={tail0:.3f}")
    return B, A


if __name__ == '__main__':
    import os
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'certificates')
    c2 = json.load(open(os.path.join(base, 'general-construction-comparison-density.json')))
    c3 = json.load(open(os.path.join(base, 'band-construction-comparison-density.json')))
    I83 = -2113164137 / 10 ** 9
    I81 = -993544791 / 500000000
    for rec in c2:
        if rec['q'] in (83, 85, 127):
            run(rec, 7 / 6, 0.0, I83, -140 / 99, 'general')
    for rec in c3:
        run(rec, 49 / 40, 1 / 20, I81, -1847 / 1100, 'band')
