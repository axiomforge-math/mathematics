"""Rigorous ball-arithmetic (Arb) upper bound for the archimedean exponent
    B = C - E(rho) + lam + 2 int_alpha^1 (G - lam)_+ dx,
    G(x) = 2U(x) + x log W + 3 psi(x) - psi(x + kappa) - 2 psi(x - alpha),
for a step density rho on the mesh 1/mesh (masses m_i / M), and a rigorous lower bound
for the arithmetic constant A_-(q) (manuscript, Appendix A.2).  Written separately from the
fixed-point verifier that produced the certificate:
logarithms come from Arb; the cell bound uses
  sup_cell G <= max(G at the two endpoints) + sum_terms |c_j| dev_j,
  dev_j <= l^2/(8 dist) (singularity off the cell),  <= l/e (singularity at an endpoint),
for the chord deviation of each term c_j psi(x - a_j) (l = cell length).
Usage: verify_comparison_bounds.py DENSITY.json q kappa_num kappa_den alpha_num alpha_den I_num I_den f2_num f2_den L
(see ../README.md for the certified cases). Exit status 1 if a hypothesis of the certificate
fails (an assertion) or if B - A_-(q) < 0 cannot be certified.
"""
import json, sys
from fractions import Fraction as Fr
from flint import arb, ctx
ctx.prec = 160


def psi(t):  # t an arb (exact rational ball), psi(t) = t log|t| - t
    if t == 0:
        return arb(0)
    return t * abs(t).log() - t


def g2(t):  # double primitive of log|t|
    if t == 0:
        return arb(0)
    return t * t * abs(t).log() / 2 - 3 * t * t / 4


def q2a(x):
    x = Fr(x)
    return arb(x.numerator) / x.denominator


def main():
    data = json.load(open(sys.argv[1]))
    q = int(sys.argv[2])
    kap = Fr(int(sys.argv[3]), int(sys.argv[4])); alp = Fr(int(sys.argv[5]), int(sys.argv[6]))
    I = Fr(int(sys.argv[7]), int(sys.argv[8])); f2 = Fr(int(sys.argv[9]), int(sys.argv[10]))
    L = int(sys.argv[11])
    rec = next(r for r in data if r['q'] == q)
    mesh, M, ms = rec['mesh'], rec['mass_den'], rec['masses']
    lam = Fr(rec['theta_num'], rec['theta_den'])
    assert sum(ms) == M and all(0 <= m * mesh <= 2 * M for m in ms)
    assert L % mesh == 0 and (kap * L).denominator == 1 and (alp * L).denominator == 1
    assert all(m == 0 for i, m in enumerate(ms) if Fr(i, mesh) < alp)   # support in [alpha, 1]
    step = L // mesh
    # energy, exact cell formula
    s = Fr(1, mesh)
    E = arb(0)
    nz = [(i, m) for i, m in enumerate(ms) if m]
    cache = {}
    def G2(k):  # g2(k/mesh)
        if k not in cache:
            cache[k] = g2(q2a(Fr(k, mesh)))
        return cache[k]
    for i, a in nz:
        for j, b in nz:
            d = i - j
            E += (a * b) * (G2(d + 1) + G2(d - 1) - 2 * G2(d))
    E = E * (mesh * mesh) / (M * M)
    # potential as a sum of psi terms: coefficient dict on grid points j (psi(x - j/L))
    C = {}
    def add(j, c):
        C[j] = C.get(j, Fr(0)) + c
    for i, m in nz:
        add(i * step, Fr(2 * mesh * m, M)); add((i + 1) * step, -Fr(2 * mesh * m, M))
    add(0, Fr(3)); add(-int(kap * L), Fr(-1)); add(int(alp * L), Fr(-2))
    C = {j: c for j, c in C.items() if c}
    lW = (arb(4) / (q * q)).log()
    psitab = {}
    def P(d):  # psi(d/L)
        if d not in psitab:
            psitab[d] = psi(arb(d) / L)
        return psitab[d]
    k0 = int(alp * L)
    Gk = []
    for k in range(k0, L + 1):
        v = arb(k) / L * lW
        for j, c in C.items():
            v += q2a(c) * P(k - j)
        Gk.append(v)
    absC = {j: abs(c) for j, c in C.items()}
    total = arb(0)
    lam_a = q2a(lam)
    for idx, k in enumerate(range(k0, L)):
        dev = Fr(0)
        for j, c in absC.items():
            if j == k or j == k + 1:
                dev += c * Fr(10, 27 * L)   # l/e < 10 l / 27
            else:
                dist = min(abs(k - j), abs(k + 1 - j))
                dev += c / (8 * L * dist)
        up = max(Gk[idx].upper(), Gk[idx + 1].upper()) + q2a(dev).upper()
        diff = up - lam_a
        # (G - lam)_+ on the cell is at most max(upper end of the ball diff, 0); a ball that
        # straddles 0 must not be dropped, so only a certainly negative ball contributes 0.
        if not (diff < 0):
            u = diff.upper()
            if u > 0:
                total += u
    integral = 2 * total / L
    Cst = q2a(kap) * q2a(kap).log() - (2 * q2a(alp) * q2a(alp).log() if alp else 0) + q2a(Fr(3, 2) - kap + 2 * alp)
    Bup = (Cst - E + lam_a + integral).upper()
    # tail conditions of the tail lemma (x >= 1), the same for alpha = 0 and alpha > 0:
    #   tau_0 = log W - (kappa/2) log(1 + kappa/2) - lam < 0,   tau_1 = 1 + log W + kappa^2/4 < 0
    tau0 = lW - q2a(kap) / 2 * (1 + q2a(kap) / 2).log() - lam_a
    tau1 = lW + 1 + q2a(kap) ** 2 / 4
    assert tau0 < 0 and tau1 < 0, 'tail condition fails'
    d = kap - 2 * alp
    Alow = (q2a(I) + q2a(f2) * arb(2).log() + arb(q).log() / 3 - q2a((2 - d) ** 2 / 4) * arb(q * q + 4).log()).lower()
    print(f"q={q} L={L}: E in {E.str(12)}; C in {Cst.str(12)}; 2int(G-lam)+ <= {integral.upper().str(12)}")
    print(f"   tail: tau_0 <= {tau0.upper().str(8)} < 0, tau_1 <= {tau1.upper().str(8)} < 0")
    print(f"   B <= {Bup.str(12)};  A_-(q) >= {Alow.str(12)};  B - A_- <= {(Bup - Alow).upper().str(10)}")

    if not (Bup - Alow) < 0:
        print("FAIL: B - A_-(q) < 0 not certified")
        sys.exit(1)
    print("PASS: B - A_-(q) < 0 certified")


main()
