"""Computation of the local (residue-class) Hankel blocks (manuscript, Section 7, Appendix A.3).

Usage: python compute_local_blocks.py band     (the six band determinants at q = 81;
exit status 1 unless all six are nonzero and their residues modulo 191 are 171, 138, 106
for sigma = 1 and 47, 24, 90 for sigma = -1, as computed modulo 191 when the certificate was
produced)
       python compute_local_blocks.py general  (sample values of the general 6x6 blocks)

Local functional (over Q(Q)):  for a polynomial g,  ell(g) = sum_{m>=0} Q^{-m} g'(m)
(rational in Q via Eulerian/Stirling moments, m = 0 term included); on simple poles
ell(1/(z + j + 1/2)) = 4 sum_{l<j} Q^{j-l}/(2l+1)^2.
Block (s, e) of size t with c poles and numerator N(z):
  entries ell( z^{i+j} N(z) (z+1)^e / prod_{l=s}^{s+c-1} (z + l + 1/2) ), 0 <= i, j < t.
General construction: t=6, c=7, N=1.  Band construction (q=81): t=40, c=49, N=z^2(z-1)^2.
"""
import sys
sys.set_int_max_str_digits(0)
from math import factorial
from flint import fmpq, fmpq_poly, fmpq_mat, fmpz, nmod_mat, nmod


def stirling2(n):
    S = [[0] * (n + 1) for _ in range(n + 1)]
    S[0][0] = 1
    for a in range(1, n + 1):
        for b in range(1, a + 1):
            S[a][b] = b * S[a - 1][b] + S[a - 1][b - 1]
    return S


def moments_at(v, rmax):
    """M_r(v) = sum_{m>=0} v^m m^r as exact rationals, r = 0..rmax."""
    S = stirling2(rmax)
    out = [1 / (1 - v)]
    for r in range(1, rmax + 1):
        out.append(sum(S[r][j] * factorial(j) * v ** j / (1 - v) ** (j + 1) for j in range(1, r + 1)))
    return out


def hankel_values(Qv, t, c, s, num, e):
    """Return the 2t-1 values ell(z^k N (z+1)^e / D) at a rational Q value."""
    z = fmpq_poly([0, 1])
    D = fmpq_poly([1])
    poles = [fmpq(-(2 * l + 1), 2) for l in range(s, s + c)]
    for a in poles:
        D *= (z - a)
    dD = D.derivative()
    Nz = num * (z + 1) ** e
    tails = {}
    for l in range(s, s + c):
        tails[l] = 4 * sum((Qv ** (l - i) / fmpq((2 * i + 1) ** 2) for i in range(l)), fmpq(0))
    rmax = max(0, Nz.degree() + 2 * t - 2 - c)
    M = moments_at(1 / Qv, rmax + 1)
    vals = []
    for k in range(2 * t - 1):
        G = Nz * z ** k
        quo, rem = divmod(G, D)
        dq = quo.derivative()
        v = sum((dq[r] * M[r] for r in range(dq.degree() + 1)), fmpq(0)) if quo.degree() >= 1 else fmpq(0)
        for l, a in zip(range(s, s + c), poles):
            v += G(a) / dD(a) * tails[l]
        vals.append(v)
    return vals


def block_det(Qv, t, c, s, num, e):
    vals = hankel_values(Qv, t, c, s, num, e)
    Mx = fmpq_mat(t, t)
    for i in range(t):
        for j in range(t):
            Mx[i, j] = vals[i + j]
    return Mx.det()


def vp(x, p):
    if x == 0:
        return None
    a, b, v = int(x.p), int(x.q), 0
    while a % p == 0:
        a //= p; v += 1
    while b % p == 0:
        b //= p; v -= 1
    return v


if __name__ == '__main__':
    z = fmpq_poly([0, 1])
    mode = sys.argv[1]
    if mode == 'band':
        expected = {1: [171, 138, 106], -1: [47, 24, 90]}
        failures = 0
        for sigma in (1, -1):
            Qv = fmpq(sigma * 81 ** 2, 4)
            out = []
            for (s, e) in ((0, 0), (1, 0), (1, 1)):
                d = block_det(Qv, 40, 49, s, z ** 2 * (z - 1) ** 2, e)
                r191 = (int(d.p) * pow(int(d.q), -1, 191)) % 191 if d != 0 else 0
                out.append((s, e, d != 0, len(str(abs(int(d.p)))), r191))
            print('q=81 sigma', sigma, out, flush=True)
            failures += not all(o[2] for o in out) or [o[4] for o in out] != expected[sigma]
        print(f"== {'PASS' if not failures else 'FAIL'}: six nonzero determinants, residues mod 191 as expected")
        sys.exit(1 if failures else 0)
    elif mode == 'general':
        # evaluate the 6x6 determinants at sample points; report sign/nonvanishing
        for q in (83, 85, 101, 125, 175, 1001):
            for sigma in (1, -1):
                Qv = fmpq(sigma * q * q, 4)
                ds = [block_det(Qv, 6, 7, s, fmpq_poly([1]), e) for (s, e) in ((0, 0), (1, 0), (1, 1))]
                print(q, sigma, [float(d) for d in ds])
