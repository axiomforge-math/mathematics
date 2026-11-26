"""Exact evaluation of the ordinary-prime slot profile B(x) and of its integral
(manuscript, Theorem 5.9 and Appendix A.1; usage: verify_profile_integrals.py k1 k76 band).

Parameters: kappa = K/h, alpha = A/h (numerator band 1..A with double zeros).
For x = p/h, classes are parametrised by t = k0/h in [0, x) (least pole index of the
class).  A class has
  c = floor(kappa/x) + [t < r_kappa]                     poles,
  n = floor(alpha/x) + [((x/2 - t) mod x) < r_alpha]       numerator roots (double),
  improved first pole iff t < x/2 and c > 0,
base weight w = 2n - c - 1.  Jet slots: w + 2j (j >= 0).  Raw slots: w + 2j (j < c),
the last one raised by 2 if improved.  J = min cost to fill mass exactly 1 with jet
slots, R = min cost to fill mass at most 1 with raw slots.  N = normalisation.
B = max(-2, N + max(J, R)).

The fill is computed by a threshold search on integer costs (closed forms), not by
materialising slot lists; this is a different implementation from the one that produced
the certificate. Exit status 1 if a rational lower bound used by the comparison fails.
"""
from fractions import Fraction as F
import sys


def floor(a):
    return a.numerator // a.denominator


def segments(kap, alp, x, tfix=None):
    """Return list of (cap, c, n, improved) for class types, using breakpoints in t."""
    qk = floor(kap / x); rk = kap - qk * x
    qa = floor(alp / x); ra = alp - qa * x
    cuts = {F(0), x, x / 2, rk}
    if alp:
        cuts.add((x / 2 - ra) % x)
    cuts = sorted(c for c in cuts if 0 <= c <= x)
    out = []
    for u, v in zip(cuts, cuts[1:]):
        if v == u:
            continue
        t = (u + v) / 2
        c = qk + (1 if t < rk else 0)
        n = qa + (1 if alp and ((x / 2 - t) % x) < ra else 0)
        imp = (t < x / 2) and c > 0
        out.append((v - u, c, n, imp))
    return out


def count_le(w, C, jmax=None):
    """#{j >= 0 (j < jmax if given) : w + 2j <= C}."""
    if C < w:
        return 0
    k = (C - w) // 2 + 1
    if jmax is not None:
        k = min(k, jmax)
    return k


def fill(slots, mass, only_negative):
    """slots: list of (cap, w, jmax, bump) meaning costs w+2j for j<jmax (jmax None = inf),
    with the last slot j=jmax-1 raised by bump.  Minimal cost of mass `mass`
    (exactly, or at most if only_negative)."""
    # expand the bumped last slot as a separate single slot
    simple = []
    singles = []
    for cap, w, jmax, bump in slots:
        if jmax is not None and bump and jmax > 0:
            simple.append((cap, w, jmax - 1))
            singles.append((cap, w + 2 * (jmax - 1) + bump))
        else:
            simple.append((cap, w, jmax))

    def cum(C):  # capacity and cost of all slots with cost <= C
        m = F(0); cost = F(0)
        for cap, w, jmax in simple:
            k = count_le(w, C, jmax)
            m += cap * k
            cost += cap * (k * w + k * (k - 1))
        for cap, s in singles:
            if s <= C:
                m += cap; cost += cap * s
        return m, cost

    if only_negative:
        m, cost = cum(-1)
        if m <= mass:
            return cost
    # smallest integer C with cum(C).mass >= mass
    lo = min([w for _, w, _ in simple] + [s for _, s in singles]) - 1
    hi = lo + 1
    while cum(hi)[0] < mass:
        hi = lo + 2 * (hi - lo)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if cum(mid)[0] >= mass:
            hi = mid
        else:
            lo = mid
    m0, c0 = cum(hi - 1)
    return c0 + hi * (mass - m0)


def B(kap, alp, x, segs=None):
    if segs is None:
        segs = segments(kap, alp, x)
    qh = floor(1 / x); qk = floor(kap / x); qa = floor(alp / x)
    N = qk - 2 * qa - 2 * qh + x * qh * (qh + 1)
    jets = [(cap, 2 * n - c - 1, None, 0) for cap, c, n, imp in segs]
    raws = [(cap, 2 * n - c - 1, c, 2 if imp else 0) for cap, c, n, imp in segs if c > 0]
    J = fill(jets, F(1), False)
    R = fill(raws, F(1), True) if raws else F(0)
    return max(F(-2), N + max(J, R)), N, J, R


def breakpoints(kap, alp, cut):
    top = max(F(1), 2 * kap)
    gens = [F(1), kap, 2 * kap]
    if alp:
        gens += [alp, 2 * alp, 2 * (kap + alp)]
    ends = {cut, top}
    for a in gens:
        j = 1
        while a / j > cut:
            if a / j < top:
                ends.add(a / j)
            j += 1
    return sorted(ends)


def integrate(kap, alp, cut=F(1, 2000), upper=False):
    ends = breakpoints(kap, alp, cut)
    tot = F(0); tot_up = F(0)
    for a, b in zip(ends, ends[1:]):
        mid = (a + b) / 2
        segs = segments(kap, alp, mid)
        v = B(kap, alp, mid)[0]
        tot += (b - a) * v
        if upper:
            # freeze class types at midpoint; capacities affine in x: rescale
            vals = []
            for xe in (a, b):
                vals.append(B_frozen(kap, alp, mid, xe))
            tot_up += (b - a) * (vals[0] + vals[1]) / 2
    return tot - 2 * cut, tot_up, len(ends) - 1


def B_frozen(kap, alp, xm, xe):
    """Profile at endpoint xe with floors and class order frozen at midpoint xm."""
    qh = floor(1 / xm); qk = floor(kap / xm); qa = floor(alp / xm)
    # cut points as affine functions of x with frozen floors
    rk = kap - qk * xe; ra = alp - qa * xe
    # ordering frozen from midpoint
    def pts(x, rk, ra):
        d = {'0': F(0), 'x': x, 'h': x / 2, 'rk': rk}
        if alp:
            d['ra'] = (x / 2 - ra) if (xm / 2 - (alp - qa * xm)) >= 0 else (x / 2 - ra + x)
        return d
    dm = pts(xm, kap - qk * xm, alp - qa * xm)
    de = pts(xe, rk, ra)
    order = sorted(dm, key=lambda k: dm[k])
    segs = []
    for k1, k2 in zip(order, order[1:]):
        if dm[k2] == dm[k1]:
            continue
        tm = (dm[k1] + dm[k2]) / 2
        c = qk + (1 if tm < dm['rk'] else 0)
        n = qa + (1 if alp and ((xm / 2 - tm) % xm) < (alp - qa * xm) else 0)
        imp = (tm < xm / 2) and c > 0
        cap = de[k2] - de[k1]
        segs.append((cap, c, n, imp))
    N = qk - 2 * qa - 2 * qh + xe * qh * (qh + 1)
    jets = [(cap, 2 * n - c - 1, None, 0) for cap, c, n, imp in segs]
    raws = [(cap, 2 * n - c - 1, c, 2 if imp else 0) for cap, c, n, imp in segs if c > 0]
    J = fill(jets, F(1), False)
    R = fill(raws, F(1), True) if raws else F(0)
    return max(F(-2), N + max(J, R))


if __name__ == '__main__':
    cases = {'k1': (F(1), F(0)), 'k76': (F(7, 6), F(0)), 'band': (F(49, 40), F(1, 20))}
    # Rational lower bounds used by the comparison certificates (Appendix A.1, A.2).
    stated = {'k76': F(-2113164137, 10**9), 'band': F(-993544791, 500000000)}
    which = [w for w in sys.argv[1:] if not w.startswith('--')] or list(cases)
    failures = 0
    for name in which:
        kap, alp = cases[name]
        I, Iup, n = integrate(kap, alp, upper=False)
        print(name, 'kappa', kap, 'alpha', alp, 'intervals', n, 'I_mid-2cut', float(I), flush=True)
        print(f"   exact midpoint sum minus 2 cut = {I.numerator}/{I.denominator}", flush=True)
        if name in stated:
            ok = I >= stated[name]
            failures += not ok
            print(f"   {'PASS' if ok else 'FAIL'}: I >= {stated[name]} = {float(stated[name])}", flush=True)
    sys.exit(1 if failures else 0)
