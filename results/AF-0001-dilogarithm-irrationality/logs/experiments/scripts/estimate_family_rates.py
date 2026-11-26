"""EXPLORATORY: finite-n content and value of the exact polynomials Q_n (Appendix C).

For each stored n (see compute_hankel_polynomials.py; exact rational coefficients):
    Qt_n = S^h/F * Q_n,  c = cont(Qt_n) (exact positive rational),  P_n = Qt_n / c in Z[X]
    c_n = log c / u^2,   d_n = log|Qt_n(xi)| / u^2,   e_n = log|P_n(xi)| / u^2 = d_n - c_n
(u = n for 2/11, u = h = H n otherwise, the scales of the certificates; Remark 7.8).
log c is an Arb ball of an exact rational; P_n(xi) is enclosed with Arb (xi = Li_2(lambda)
by Arb's certified polylog, precision increased until the ball excludes 0), so every
finite-n number printed is rigorous.  The *fits* (least squares in floating point) of
    r_n ~ a + b log(n)/n + c/n
are extrapolations, NOT certificates.  They are compared with the claimed limits:
    liminf c_n > content lower bound,   limsup d_n < analytic upper bound.
The same quantities normalised by h^2 at the largest stored n are printed for Table 9, and
for 2/9 the fits d ~ c0 + c1 log(h)/h + c2/h of log|Qt_n(xi)|/h^2 over n >= 3, 5, 7 that are
quoted in Appendix C.

Usage: python estimate_family_rates.py [CASE ...]
"""

from __future__ import annotations

import json
import math
import sys
from fractions import Fraction as Fr
from pathlib import Path

sys.set_int_max_str_digits(0)

from flint import acb, arb, arb_poly, ctx, fmpq, fmpq_poly, fmpz  # noqa: E402

from define_parameters import CASES, OUT, Case, frac_str  # noqa: E402

from define_hankel_family import CASES as FAMILY, load_polynomials  # noqa: E402


def load(case: Case):
    yield from load_polynomials(case.name)


def normalization(case: Case, n: int) -> fmpq:
    h, K, A = case.H * n, case.C * n, case.B * n
    S = fmpq(math.factorial(K), math.factorial(A) ** 3)
    F = fmpz(1)
    for i in range(h):
        F *= fmpz(math.factorial(i)) ** 2
    return S ** h / F


def content(P: fmpq_poly) -> fmpq:
    num, den = fmpz(0), fmpz(1)
    for k in range(P.degree() + 1):
        c = P[k]
        if c != 0:
            num = num.gcd(c.p)
            den = den.lcm(c.q)
    return fmpq(num, den)


def log_abs_P_at_xi(P: fmpq_poly, lam: Fr) -> arb:
    coeffs = [int(P[k].p) for k in range(P.degree() + 1)]  # P is integral
    assert all(P[k].q == 1 for k in range(P.degree() + 1))
    maxbits = max(abs(c).bit_length() for c in coeffs)
    prec = maxbits + 256
    while True:
        ctx.prec = prec
        xi = acb(arb(lam.numerator) / lam.denominator).polylog(2).real
        val = arb_poly(coeffs)(xi)
        if not val.contains(0):
            lg = abs(val).log()
            if lg.rad() < 1e-8:
                ctx.prec = 256
                return lg
        prec *= 2


def fit(ns, ys):
    """least squares y ~ a + b log(n)/n + c/n (floating point, exploratory)."""
    import mpmath as mp

    X = mp.matrix([[1.0, math.log(n) / n, 1.0 / n] for n in ns])
    y = mp.matrix(list(ys))
    coef = mp.lu_solve(X.T * X, X.T * y)
    return [float(coef[i]) for i in range(3)]


def analyse(case: Case, cert: dict):
    rows = []
    for n, Q in load(case):
        u = n * case.scale
        Qt = Q * normalization(case, n)
        c = content(Qt)
        P = Qt / c
        lp = log_abs_P_at_xi(P, case.lam)
        ctx.prec = 256
        lc = arb(fmpz(c.p)).log() - arb(fmpz(c.q)).log()
        rows.append(dict(n=n, u=u, deg=Q.degree(), c=float((lc / u**2).mid()), d=float(((lc + lp) / u**2).mid()),
                         e=float((lp / u**2).mid()), lc=lc.str(12), lp=lp.str(12)))
    print(f"# case {case.name} ({case.unit}-units)  claimed: content rate > {cert['arith']},"
          f" decay rate < {cert['anal']}")
    print("   n    u  deg   c_n=log cont/u^2   d_n=log|Qt(xi)|/u^2   e_n=log|P(xi)|/u^2")
    for r in rows:
        print(f"{r['n']:4d} {r['u']:4d} {r['deg']:4d}   {r['c']:14.5f}   {r['d']:14.5f}   {r['e']:14.5f}")
    out = dict(rows=rows)
    good = [r for r in rows if r["n"] >= max(4, rows[-1]["n"] // 3)] if rows else []
    if len(good) >= 5:
        ns = [r["n"] for r in good]
        for key in ("c", "d", "e"):
            a, b, cc = fit(ns, [r[key] for r in good])
            out[f"fit_{key}"] = (a, b, cc)
            print(f"  fit {key}_n ~ {a:+.4f} {b:+.4f} log n/n {cc:+.4f}/n   (n = {ns[0]}..{ns[-1]})  -> limit {a:+.4f}")
        print(f"  claimed limits: content >= {cert['arith']} (certified, ours: {cert['arith_ours']}),"
              f" decay <= {cert['anal']} (certified, ours: {cert['anal_ours']})")
    return out


def table8(case: Case, rows: list) -> dict:
    """Last row normalised by h^2 (Table 9) and, for 2/9, the fits of Appendix C."""
    if not rows:
        return {}
    k = (case.H // case.scale) ** 2  # h^2 = k u^2
    r = rows[-1]
    h = case.H * r["n"]
    out = dict(n=r["n"], h=h, content_h2=r["c"] / k, value_h2=r["d"] / k, primitive_h2=r["e"] / k)
    print(f"  h^2-normalised row: n={r['n']} h={h}  log cont/h^2 = {out['content_h2']:.4f}  "
          f"log|Qt(xi)|/h^2 = {out['value_h2']:.4f}  log|P(xi)|/h^2 = {out['primitive_h2']:.4f}")
    if case.name == "2/9":
        import mpmath as mp
        fits = {}
        for nmin in (3, 5, 7):
            sel = [x for x in rows if x["n"] >= nmin]
            hs = [case.H * x["n"] for x in sel]
            X = mp.matrix([[1.0, math.log(hh) / hh, 1.0 / hh] for hh in hs])
            y = mp.matrix([x["d"] / k for x in sel])
            coef = mp.lu_solve(X.T * X, X.T * y)
            fits[nmin] = float(coef[0])
            print(f"  fit log|Qt(xi)|/h^2 ~ c0 + c1 log h/h + c2/h over n >= {nmin}: limit c0 = {float(coef[0]):+.4f}")
        out["fits_value_h2"] = fits
    return out


def main():
    names = sys.argv[1:] or list(CASES)
    rc = OUT / "rate-comparison.json"
    cr = json.loads(rc.read_text()) if rc.exists() else {}
    allout = {}
    for nm in names:
        case = CASES[nm]
        info = cr.get(nm, {})
        cert = dict(arith=case.claims["content_rate_reported"], anal=case.claims["analytic_reported"],
                    arith_ours=info.get("rate_exact_profile", "?"),
                    anal_ours=(frac_str(Fr(info["analytic_upper_ours"]), 10) if "analytic_upper_ours" in info else "?"))
        allout[nm] = analyse(case, cert)
        allout[nm]["table8"] = table8(case, allout[nm]["rows"])
    (OUT / "family-rates.json").write_text(json.dumps(allout, indent=1, default=str))


if __name__ == "__main__":
    main()
