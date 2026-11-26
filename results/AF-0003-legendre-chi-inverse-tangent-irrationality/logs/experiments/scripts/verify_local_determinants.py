"""6x6 local determinants of the general construction as polynomials (manuscript,
Proposition 7.2 and Appendix A.3): interpolate (Q-1)^24 det L_{s,e}(Q) exactly from values at
integer Q (flint), strip powers of Q and Q-1, compare with the integer polynomials of
../certificates/general-construction-local-polynomials.json (computed symbolically when the
certificate was produced), and bound the roots: exactly by Cauchy's bound
1 + max |p_i / p_deg|, and numerically by computing all roots (mpmath).

Usage: python verify_local_determinants.py ../certificates/general-construction-local-polynomials.json
Exit status 1 if a polynomial differs or if a Cauchy bound is not below 189.
"""
import sys, json
sys.set_int_max_str_digits(0)
from flint import fmpq, fmpq_poly
import mpmath as mp
from compute_local_blocks import block_det
from define_half_integer_pencils import interpolate
arch = json.load(open(sys.argv[1]))
failures = 0
for idx, (s, e) in enumerate(((0, 0), (1, 0), (1, 1))):
    xs = [fmpq(k) for k in range(2, 2 + 90)]
    ys = [block_det(x, 6, 7, s, fmpq_poly([1]), e) * (x - 1) ** 24 for x in xs]
    P = interpolate(xs, ys)
    # verify at extra points
    for x in (fmpq(-7, 3), fmpq(1000), fmpq(-83 ** 2, 4)):
        assert P(x) == block_det(x, 6, 7, s, fmpq_poly([1]), e) * (x - 1) ** 24
    a = 0
    Qp = fmpq_poly([0, 1])
    while P(0) == 0:
        P = P // Qp; a += 1
    b = 0
    while P(1) == 0:
        P = P // (Qp - 1); b += 1
    coeffs = [P[k] for k in range(P.degree(), -1, -1)]
    ac = [int(x) for x in arch[idx]['coefficients_desc']]
    r = fmpq(ac[0]) / coeffs[0]
    same = len(ac) == len(coeffs) and all(fmpq(x) == r * c for x, c in zip(ac, coeffs))
    cauchy = 1 + max(abs(c / coeffs[0]) for c in coeffs[1:])
    failures += (not same) or not (cauchy < 189)
    mp.mp.dps = 60
    roots = mp.polyroots([mp.mpf(int(c.p)) / int(c.q) for c in coeffs], maxsteps=500, extraprec=500)
    rmax = max(abs(z) for z in roots)
    print(f"(s,e)=({s},{e}): (Q-1)^24 det = Q^{a} (Q-1)^{b} P(Q), deg P = {P.degree()}, "
          f"archived match up to scalar: {same} (archived powers {arch[idx]['power_Q']},{arch[idx]['power_Q_minus_1']}); "
          f"max |root of P| = {mp.nstr(rmax, 8)}; Cauchy bound = {float(cauchy):.4f} (< 189: {cauchy < 189})  vs 83^2/4 = {83**2/4}")
print(f"== {'PASS' if not failures else 'FAIL'}: {failures} failures")
sys.exit(1 if failures else 0)
