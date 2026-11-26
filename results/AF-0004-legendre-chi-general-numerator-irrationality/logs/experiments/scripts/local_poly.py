"""Local (residue-class) determinants L_{s,e}(Q) as polynomials, by exact interpolation.

Local functional over Q(Q): for a polynomial g, ell(g) = sum_{m>=0} Q^{-m} g'(m); on simple
poles ell(1/(z + j + 1/2)) = 4 sum_{l<j} Q^{j-l}/(2l+1)^2.  Block (s, e) of size t with c
poles: entries ell(z^{i+j} (z+1)^e / prod_{l=s}^{s+c-1}(z + l + 1/2)), 0 <= i, j < t.

For (t, c) = (6, 7) and (4, 5) and (s, e) = (0,0), (1,0), (1,1): evaluate the determinant
exactly at many rational Q (python-flint), interpolate (Q-1)^{4t} det, strip the powers of Q
and Q-1, compare with the stored primitive integer polynomial (../certificates/local_polynomials.json),
and check the strict domination  sum_{j>=1} |a_{d-j}/a_d| R^{-j} < 1  at R = 83^2/4 with
exact rationals.  Exit status 1 on any mismatch.  Does not import SymPy or the code that produced the candidate certificates.
"""
import json, os, sys
sys.set_int_max_str_digits(0)
from math import factorial
from flint import fmpq, fmpq_poly, fmpq_mat


def stirling2(n):
    S = [[0] * (n + 1) for _ in range(n + 1)]
    S[0][0] = 1
    for a in range(1, n + 1):
        for b in range(1, a + 1):
            S[a][b] = b * S[a - 1][b] + S[a - 1][b - 1]
    return S


def moments_at(v, rmax):
    """M_r(v) = sum_{m>=0} v^m m^r, r = 0..rmax (exact)."""
    S = stirling2(rmax)
    out = [1 / (1 - v)]
    for r in range(1, rmax + 1):
        out.append(sum(S[r][j] * factorial(j) * v ** j / (1 - v) ** (j + 1) for j in range(1, r + 1)))
    return out


def block_det(Qv, t, c, s, e):
    z = fmpq_poly([0, 1])
    D = fmpq_poly([1])
    poles = [fmpq(-(2 * l + 1), 2) for l in range(s, s + c)]
    for a in poles:
        D *= (z - a)
    dD = D.derivative()
    Nz = (z + 1) ** e
    tails = {l: 4 * sum((Qv ** (l - i) / fmpq((2 * i + 1) ** 2) for i in range(l)), fmpq(0))
             for l in range(s, s + c)}
    rmax = max(0, e + 2 * t - 2 - c)
    M = moments_at(1 / Qv, rmax + 1)
    vals = []
    for k in range(2 * t - 1):
        G = Nz * z ** k
        quo, _ = divmod(G, D)
        dq = quo.derivative()
        v = sum((dq[r] * M[r] for r in range(dq.degree() + 1)), fmpq(0)) if quo.degree() >= 1 else fmpq(0)
        for l, a in zip(range(s, s + c), poles):
            v += G(a) / dD(a) * tails[l]
        vals.append(v)
    Mx = fmpq_mat(t, t)
    for i in range(t):
        for j in range(t):
            Mx[i, j] = vals[i + j]
    return Mx.det()


def interpolate(xs, ys):
    coef = list(ys)
    n = len(xs)
    for j in range(1, n):
        for i in range(n - 1, j - 1, -1):
            coef[i] = (coef[i] - coef[i - 1]) / (xs[i] - xs[i - j])
    X = fmpq_poly([0, 1])
    poly = fmpq_poly([coef[-1]])
    for i in range(n - 2, -1, -1):
        poly = poly * (X - xs[i]) + coef[i]
    return poly


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    arch = json.load(open(os.path.join(here, '..', 'certificates', 'local_polynomials.json')))
    R = fmpq(83 ** 2, 4)
    ok = True
    for (t, c) in ((6, 7), (4, 5)):
        for (s, e) in ((0, 0), (1, 0), (1, 1)):
            pw = 4 * t
            npts = t * (s + c + 6) + pw + 8        # generous degree bound, verified below
            xs = [fmpq(k) for k in range(2, 2 + npts)]
            ys = [block_det(x, t, c, s, e) * (x - 1) ** pw for x in xs]
            P = interpolate(xs, ys)
            assert P.degree() < npts - 4, 'degree bound too small'
            for x in (fmpq(-7, 3), fmpq(1000), fmpq(-83 ** 2, 4), fmpq(131 ** 2, 9), fmpq(-12061 ** 2, 64)):
                assert P(x) == block_det(x, t, c, s, e) * (x - 1) ** pw
            Qp = fmpq_poly([0, 1]); a = b = 0
            while P(0) == 0:
                P = P // Qp; a += 1
            while P(1) == 0:
                P = P // (Qp - 1); b += 1
            coeffs = [P[k] for k in range(P.degree(), -1, -1)]
            rec = next(r for r in arch if r['t'] == t and r['c'] == c and r['shift'] == s and r['zero'] == bool(e))
            ac = [int(x) for x in rec['coefficients_desc']]
            r = fmpq(ac[0]) / coeffs[0]
            same = len(ac) == len(coeffs) and all(fmpq(x) == r * cc for x, cc in zip(ac, coeffs))
            ratio = sum((abs(cc / coeffs[0]) / R ** i for i, cc in enumerate(coeffs[1:], 1)), fmpq(0))
            cauchy = 1 + max(abs(cc / coeffs[0]) for cc in coeffs[1:])
            good = same and ratio < 1
            ok &= good
            print(f"(t,c)=({t},{c}) (s,e)=({s},{e}): (Q-1)^{pw} det = const Q^{a} (Q-1)^{b} P(Q), deg P = {P.degree()}, "
                  f"matches stored polynomial: {same}; domination ratio at 83^2/4 = {float(int(ratio.p)/int(ratio.q)):.6g} < 1: {ratio < 1}; "
                  f"Cauchy bound {float(int(cauchy.p)/int(cauchy.q)):.5g}", flush=True)
    print('ALL PASS' if ok else 'FAILURE')
    sys.exit(0 if ok else 1)


main()
