"""Checker for the comparison-measure bounds (analytic rates), in Arb ball arithmetic.

Manuscript: Proposition 7.7 (positive arguments), Proposition 8.4 (negative arguments),
Table 7 and Appendix A.4.

Positive arguments (2/11 in n-units, 2/9 in h-units), comparison measure on [0, inf):
    RHS = C_u - E + m*theta + 2 * int_0^inf (W(y) - theta)_+ dy,     W = V + 2U,
    V(y) = 3F(y+alpha) - 2F(y) - F(y+kappa) + (kappa - 3 alpha) - t y,  F(s) = s log|s|,
    t = log(1/|lambda|),  C_u = m kappa log kappa - 3 m alpha log alpha - m^2 log m
                                + 3m^2/2 - m(kappa - 3 alpha)
  (2/11: C_u = 24 log 6 - 16 log 4 + 12 in the n-scale, Remark 7.8; 2/9: C_* of Lemma 7.3).
Negative arguments (-2/9, -2/7), symmetric measure on the rays c y, conj(c) y:
    RHS = C_* - E + sup_{y>=0} (V_-(y) + 2 U_-(y)),                          (Prop. 8.4)
    V_-(y) = d + Re{3(cy+alpha)log(cy+alpha) - 2cy log(cy) - (cy+kappa)log(cy+kappa)} - T y,
    T = Re(c) t + Im(c) pi.

All potentials are written as finite sums of translates
    real   : coef * f(y - p),            f(s) = s log|s| - s
    complex: coef * Re Fc(alpha y + beta), Fc(z) = z (log z - 1)  (principal branch)
plus a linear term (the linear parts of V cancel exactly against the constant).

Rigorous cell bounds (method of this checker).  On a mesh cell [y0, y1] (all shifts mesh-aligned):
  * a real translate c f(y-p) is convex or concave on the cell (f'' = 1/s); we use its
    chord (convex) or its tangent at the cell midpoint (concave): an exact affine
    majorant;
  * a complex translate with beta = 0 equals Re(alpha) y log y + linear: same treatment;
  * any other complex translate: chord + (s^2/8) * max(0, sup_cell(-coef * phi'')),
    phi'' = Re(alpha^2 / (alpha y + beta)), the sup enclosed by Arb on the cell ball.
  Summing gives an affine majorant A of W on the cell up to an additive constant eps.
  Positive case:  int_cell (W - theta)_+ <= s * ((A(y0)+eps-theta)_+ + (A(y1)+eps-theta)_+)/2
                  (the positive part of an affine function is convex).
  Negative case:  sup_cell W <= max(A(y0), A(y1)) + eps.
  Tails beyond Y are handled by the monotone majorants of Appendix A.4, re-checked in Arb.

We also recompute the cruder bounds of Appendix A.4, used by the original programs -- BV/midpoint for 2/11,
trapezoid + L1 interpolation error for 2/9, mesh maximum + (6+4J)s/2 for the negative
cases -- to check the reported numbers.

Usage: python verify_comparison_bounds.py CASE [N]   (N = mesh cells per unit, default 2000)
"""

from __future__ import annotations

import sys
import time
from fractions import Fraction as Fr

from flint import acb, arb, ctx

from define_parameters import CASES, OUT, A, Checks, arb_to_interval, fmt, frac_str, upper_str

ctx.prec = 160

# ---------------------------------------------------------------------------
# Comparison-measure data: mass vectors of Table 8 of the manuscript (as used by the
# original programs named below), theta values of Appendix A.4
# ---------------------------------------------------------------------------
DATA = {
    "2/11": dict(  # certify_two_elevenths.py
        M=[1000, 557, 402, 325, 272, 233, 203, 178, 157, 139, 122, 107, 92, 78, 63, 48, 24],
        width=Fr(1, 2), dens_den=500, theta=Fr(-431, 50), Y=Fr(12), kind="positive"),
    "2/9": dict(  # certify_two_ninths.py
        M=[5000, 5000, 5000, 5000, 5000, 5000, 5000, 3819, 3235, 2875, 2603, 2389, 2213, 2065, 1937,
           1826, 1728, 1641, 1562, 1490, 1425, 1365, 1310, 1259, 1211, 1167, 1125, 1086, 1049, 1014,
           981, 950, 920, 891, 864, 837, 812, 788, 764, 742, 720, 699, 678, 659, 639, 620, 602, 584,
           567, 549, 533, 516, 500, 484, 468, 452, 437, 421, 406, 391, 376, 361, 346, 330, 315, 300,
           284, 268, 252, 235, 217, 199, 179, 158, 134, 107, 71],
        width=Fr(1, 40), dens_den=2500, theta=Fr(-3340, 1000), Y=Fr(4), kind="positive"),
    "-2/9": dict(  # certify_minus_two_ninths.py
        M=[9424, 5610, 5336, 4824, 4487, 4204, 3966, 3757, 3571, 3403, 3248, 3106, 2972, 2847, 2729,
           2616, 2508, 2405, 2305, 2208, 2114, 2023, 1933, 1844, 1757, 1671, 1585, 1499, 1413, 1326,
           1238, 1148, 1055, 958, 856, 744, 618, 477, 215],
        width=Fr(1, 40), dens_den=5000, c=(Fr(4, 5), Fr(3, 5)), Y=Fr(2), kind="negative"),
    "-2/7": dict(  # certify_minus_two_sevenths.py
        M=[13112, 8416, 7787, 6951, 6348, 5833, 5390, 4997, 4642, 4318, 4016, 3734, 3466, 3210, 2962,
           2721, 2482, 2244, 2002, 1751, 1486, 1185, 869, 78],
        width=Fr(1, 25), dens_den=8000, c=(Fr(21, 29), Fr(20, 29)), Y=Fr(3), kind="negative"),
}

PI = arb.pi()


def LOG(x) -> arb:
    x = Fr(x)
    return arb(x.numerator).log() - arb(x.denominator).log()


def xlogx(x: Fr) -> arb:
    x = Fr(x)
    return arb(0) if x == 0 else A(x) * LOG(abs(x))


def f_real(x: Fr) -> arb:  # f(s) = s log|s| - s
    return xlogx(x) - A(x)


def g_real(x: Fr) -> arb:  # g(s) = s^2/2 log|s| - 3 s^2/4
    x = Fr(x)
    return A(x * x / 2) * (LOG(abs(x)) if x != 0 else arb(0)) - A(Fr(3, 4) * x * x)


def clog(z: acb) -> acb:
    """Principal log; for an exact negative real z use log|z| + i pi explicitly."""
    if z.imag == 0 and z.real < 0:
        return acb((-z.real).log(), PI)
    return z.log()


def Fc(z: acb) -> acb:  # z (log z - 1), Fc(0) = 0
    if z == 0:
        return acb(0)
    return z * (clog(z) - 1)


def Gc(z: acb) -> acb:  # z^2 (log z / 2 - 3/4), Gc(0) = 0
    if z == 0:
        return acb(0)
    return z * z * (clog(z) / 2 - acb(3) / 4)


def AC(re: Fr, im: Fr) -> acb:
    return acb(A(re), A(im))


# ---------------------------------------------------------------------------
# Measures
# ---------------------------------------------------------------------------
def measure(case_name: str):
    d = DATA[case_name]
    M, w, den = d["M"], d["width"], d["dens_den"]
    rho = [Fr(mj, den) for mj in M]
    a = [j * w for j in range(len(M))]
    b = [x + w for x in a]
    jumps = []  # (position p_k, e_k = rho_k - rho_{k-1})
    prev = Fr(0)
    for k in range(len(M) + 1):
        cur = rho[k] if k < len(M) else Fr(0)
        if cur != prev:
            jumps.append((k * w, cur - prev))
        prev = cur
    return rho, a, b, jumps


# ---------------------------------------------------------------------------
# Energies
# ---------------------------------------------------------------------------
def energy_line(rho, a, b) -> arb:
    """E = int int log|x-y| for the density rho_j on [a_j,b_j] (one line)."""
    # cache g at all needed differences
    cache: dict[Fr, arb] = {}

    def g(x):
        if x not in cache:
            cache[x] = g_real(x)
        return cache[x]

    E = arb(0)
    for dj, aj, bj in zip(rho, a, b):
        for dk, ak, bk in zip(rho, a, b):
            I = g(bj - ak) + g(aj - bk) - g(aj - ak) - g(bj - bk)
            E += A(dj * dk) * I
    return E


def energy_rays(rho, a, b, eta: acb) -> arb:
    """E for the symmetric measure: density rho_j on [a_j,b_j] on EACH ray."""
    E_same = energy_line(rho, a, b)
    cache: dict[tuple, acb] = {}

    def G(y, s):
        key = (y, s)
        if key not in cache:
            cache[key] = Gc(eta * A(y) - A(s))
        return cache[key]

    Ec = acb(0)
    for dj, aj, bj in zip(rho, a, b):
        for dk, ak, bk in zip(rho, a, b):
            I = G(bj, ak) + G(aj, bk) - G(aj, ak) - G(bj, bk)
            Ec += A(dj * dk) * I
    E_cross = (Ec / eta).real
    return 2 * E_same + 2 * E_cross, E_same, E_cross


# ---------------------------------------------------------------------------
# Term lists for W
# ---------------------------------------------------------------------------
def terms_positive(case, jumps):
    """W = sum coef*f(y - p) - t*y ; returns (real_terms, slope_t)."""
    al, ka = case.alpha, case.kappa
    real = []
    if al == 0:
        real.append((Fr(1), Fr(0)))  # 3f(y) - 2f(y)
    else:
        real.append((Fr(3), -al))
        real.append((Fr(-2), Fr(0)))
    real.append((Fr(-1), -ka))
    for p, e in jumps:
        real.append((2 * e, p))
    return real


def terms_negative(case, jumps, c: acb, eta: acb):
    """W_- = sum coef*f(y-p) + sum coef*Re Fc(alpha*y + beta) - T*y."""
    al, ka = case.alpha, case.kappa
    real = [(2 * e, p) for p, e in jumps]
    cplx = [(Fr(3), c, A(al), al == 0), (Fr(-2), c, acb(0), True), (Fr(-1), c, A(ka), ka == 0)]
    for p, e in jumps:
        cplx.append((2 * e, eta, -A(p), p == 0))
    return real, cplx


# ---------------------------------------------------------------------------
# Cellwise affine majorants
# ---------------------------------------------------------------------------
class RealTermEvaluator:
    """f(y - p) on the grid 1/(2N): y = j/(2N), p = P/(2N)."""

    def __init__(self, N: int, jmax: int):
        self.N2 = 2 * N
        self.logN2 = arb(self.N2).log()
        self.logs = [arb(0)] + [arb(k).log() for k in range(1, jmax + 1)]

    def f(self, k: int) -> arb:  # f(k/(2N))
        if k == 0:
            return arb(0)
        v = arb(k) / self.N2
        return v * (self.logs[abs(k)] - self.logN2) - v

    def fprime(self, k: int) -> arb:  # log|k/(2N)|
        return self.logs[abs(k)] - self.logN2


def cell_majorants(real_terms, cplx_terms, slope: arb, N: int, Y: Fr):
    """For each cell i=[i/N,(i+1)/N] of [0,Y], return (U0, U1, eps): the affine majorant
    of W at the two ends (upper endpoints as arb) and the additive constant."""
    N2 = 2 * N
    ncell = int(Y * N)
    assert Fr(ncell, N) == Y
    # integer positions on the 1/(2N) grid
    rterms = []
    for coef, p in real_terms:
        P = p * N2
        assert P.denominator == 1 and int(P) % 2 == 0, "shift not mesh aligned"
        rterms.append((A(coef), coef, int(P)))
    jmax = 2 * ncell + 2 + max(abs(P) for _, _, P in rterms) + 2
    ev = RealTermEvaluator(N, jmax)
    # complex term values at mesh points
    cvals = []
    for coef, alpha, beta, beta_zero in cplx_terms:
        vals = []
        for i in range(ncell + 1):
            y = arb(i) / N
            vals.append(Fc(alpha * y + beta).real)
        cvals.append(vals)
    out = []
    s = arb(1) / N
    for i in range(ncell):
        j0, j1, jm = 2 * i, 2 * i + 2, 2 * i + 1
        y0, y1, ym = arb(j0) / N2, arb(j1) / N2, arb(jm) / N2
        U0 = -slope * y0
        U1 = -slope * y1
        eps = arb(0)
        for c_arb, coef, P in rterms:
            # sign of (y - p) on the cell
            if j0 >= P:
                sgn = 1
            elif j1 <= P:
                sgn = -1
            else:
                raise RuntimeError("cell straddles a singularity")
            convex = (coef > 0 and sgn > 0) or (coef < 0 and sgn < 0)
            if coef == 0:
                continue
            if convex:
                U0 += c_arb * ev.f(j0 - P)
                U1 += c_arb * ev.f(j1 - P)
            else:
                fm = ev.f(jm - P)
                dm = ev.fprime(jm - P)
                U0 += c_arb * (fm + dm * (y0 - ym))
                U1 += c_arb * (fm + dm * (y1 - ym))
        for (coef, alpha, beta, beta_zero), vals in zip(cplx_terms, cvals):
            c_arb = A(coef)
            if beta_zero:
                # Re Fc(alpha y) = Re(alpha) y log y + y Re(alpha(log alpha - 1)) ; Re(alpha)>0
                if coef * 1 > 0:  # convex (Re alpha > 0 is asserted below)
                    U0 += c_arb * vals[i]
                    U1 += c_arb * vals[i + 1]
                else:
                    zm = alpha * ym
                    fm = Fc(zm).real
                    dm = (alpha * clog(zm)).real
                    U0 += c_arb * (fm + dm * (y0 - ym))
                    U1 += c_arb * (fm + dm * (y1 - ym))
            else:
                U0 += c_arb * vals[i]
                U1 += c_arb * vals[i + 1]
                Yb = y0.union(y1)  # Arb hull: a ball containing the whole cell
                zb = alpha * Yb + beta
                phi2 = (alpha * alpha / zb).real
                neg = (-c_arb * phi2).upper()
                if neg > 0:
                    eps += arb(neg) * s * s / 8
                elif not (neg <= 0):
                    raise RuntimeError("could not bound second derivative")
        out.append((U0, U1, eps))
    return out


# ---------------------------------------------------------------------------
# Positive-case certificate
# ---------------------------------------------------------------------------
def positive(case, chk: Checks, N: int) -> dict:
    d = DATA[case.name]
    rho, a, b, jumps = measure(case.name)
    m, al, ka = case.m, case.alpha, case.kappa
    theta = d["theta"]
    th = A(theta)
    mass = sum(r * (y - x) for r, x, y in zip(rho, a, b))
    chk.check(f"{case.name}: comparison measure has mass m={m}", mass == m, f"mass={mass}")
    chk.check(f"{case.name}: density nonnegative", min(rho) >= 0)
    t = LOG(1 / abs(case.lam))
    dprime = ka - 3 * al
    C_u = (A(m * ka) * LOG(ka) - (A(3 * m * al) * LOG(al) if al else arb(0))
           - A(m * m) * LOG(m) + A(Fr(3, 2) * m * m) - A(m * dprime))
    if case.name == "2/11":
        C_ms = 24 * LOG(6) - 16 * LOG(4) + 12
        chk.check("2/11: C_u equals 24 log 6 - 16 log 4 + 12", (C_u - C_ms).contains(0) and
                  abs(C_u - C_ms) < arb(10) ** -40)
    E = energy_line(rho, a, b)
    print(f"  E = {fmt(E, 20)}")
    if "E_reported" in case.claims:
        chk.check(f"{case.name}: E agrees with reported {case.claims['E_reported']} to 1e-9",
                  abs(E - A(Fr(case.claims["E_reported"]))) < arb(10) ** -9)

    # ---- tail: W(y) < theta for y >= Y -------------------------------------------
    Y = d["Y"]
    supp = b[-1]
    chk.check(f"{case.name}: support [0,{supp}] inside [0,Y=]{Y}", supp < Y)

    def Vexact(y: Fr) -> arb:
        yA = A(y)
        val = 3 * xlogx(y + al) - 2 * xlogx(y) - xlogx(y + ka) + A(dprime) - t * yA
        return val

    maj_Y = Vexact(Y) + 2 * A(m) * LOG(Y)
    chk.check(f"{case.name}: tail majorant V(Y)+2m log Y < theta at Y={Y}", maj_Y < th,
              f"{fmt(maj_Y, 12)} vs theta={float(theta)}")
    # derivative of V(y) + 2m log y for y >= Y:
    #   3 log(1+al/y) - log(1+ka/y) + 2m/y - t <= (3 al + 2m)/y - t
    dbound = A((3 * al + 2 * m) / Y) - t
    chk.check(f"{case.name}: tail majorant decreasing on [Y,inf): (3a+2m)/Y - t < 0", dbound < 0,
              fmt(dbound, 10))

    # ---- cellwise rigorous upper bound for int_0^Y (W - theta)_+ ------------------
    t0 = time.time()
    real_terms = terms_positive(case, jumps)
    cells = cell_majorants(real_terms, [], t, N, Y)
    s = arb(1) / N
    pos = arb(0)
    maxW = None
    for U0, U1, eps in cells:
        e0 = (U0 + eps - th).upper()
        e1 = (U1 + eps - th).upper()
        e0 = arb(e0) if e0 > 0 else arb(0)
        e1 = arb(e1) if e1 > 0 else arb(0)
        pos += s * (e0 + e1) / 2
        hi = arb(max(U0.upper(), U1.upper()))
        maxW = hi if maxW is None else (hi if hi > maxW else maxW)
    pos_up = arb(pos.upper())
    print(f"  [our bound] int_0^Y (W-theta)_+ <= {upper_str(pos_up)}   (mesh 1/{N}, {time.time()-t0:.1f}s)")
    rhs = C_u - E + A(m) * th + 2 * pos_up
    rhs_up = arb(rhs.upper())
    print(f"  [our bound] RHS = C_u - E + m theta + 2 int(W-theta)_+ <= {upper_str(rhs_up)}")
    chk.check(f"{case.name}: certified RHS < claimed {frac_str(case.claims['analytic_upper'], 4)}",
              rhs_up < A(case.claims["analytic_upper"]), upper_str(rhs_up))

    # ---- recompute the manuscript's own (cruder) bound -----------------------------
    ms = manuscript_positive_bound(case, rho, a, b, jumps, t, th, E, C_u)
    return dict(E=E, C_u=C_u, pos_upper=pos_up, rhs_upper=rhs_up, ms=ms, t=t)


def W_point_real(real_terms, slope, y: Fr) -> arb:
    val = -slope * A(y)
    for coef, p in real_terms:
        val += A(coef) * f_real(y - p)
    return val


def manuscript_positive_bound(case, rho, a, b, jumps, t, th, E, C_u):
    real_terms = terms_positive(case, jumps)
    m = case.m
    out = {}
    if case.name == "2/11":
        # BV bound on [0,12] (Appendix A.4): TV(V) <= int |V'| with
        # |V'| <= 3log(1+1/y) + log(1+6/y) + t ; interval potentials: P(0)+P(12)-2P(mid)
        TV = 3 * (xlogx(13) - xlogx(12)) + (xlogx(18) - xlogx(12) - xlogx(6)) + 12 * t
        for r, x, y in zip(rho, a, b):
            def P(z):
                return f_real(z - x) - f_real(z - y)
            TV += 2 * A(r) * (P(Fr(0)) + P(Fr(12)) - 2 * P((x + y) / 2))
        step = Fr(1, 200)
        msum = arb(0)
        for j in range(2400):
            y = step * (j + Fr(1, 2))
            w = (W_point_real(real_terms, t, y) - th).upper()
            if w > 0:
                msum += arb(w)
        msum *= A(step)
        pen = msum + A(step) * TV / 2
        rhs = C_u - E + A(m) * th + 2 * pen
        print(f"  [manuscript method] TV <= {upper_str(TV, 10)}, midpoint sum = {upper_str(msum, 10)}, "
              f"penalty <= {upper_str(pen, 10)}, RHS <= {upper_str(rhs, 12)}")
        out = dict(TV=TV, midpoint_sum=msum, penalty=pen, rhs=rhs)
    elif case.name == "2/9":
        # trapezoid + L1 interpolation error (Appendix A.4), s = 1/400 on [0,4]
        step = Fr(1, 400)
        N = 1600
        harmonic = sum(Fr(1, j) for j in range(1, N + int(case.kappa / step) + 1))
        coef_norm = sum(abs(cf) for cf, _ in real_terms)
        err = A(coef_norm * step ** 2 * (Fr(1, 2) + harmonic / 6))
        samples = []
        for j in range(N + 1):
            w = (W_point_real(real_terms, t, step * j) - th).upper()
            samples.append(arb(w) if w > 0 else arb(0))
        trap = A(step) * (sum(samples[1:-1], arb(0)) + (samples[0] + samples[-1]) / 2)
        pen = trap + err
        rhs = C_u - E + A(m) * th + 2 * pen
        print(f"  [manuscript method] coefficient norm = {coef_norm}, L1 error <= {upper_str(err, 8)}, "
              f"trapezoid = {upper_str(trap, 10)}, RHS <= {upper_str(rhs, 16)}")
        out = dict(coef_norm=coef_norm, err=err, trapezoid=trap, penalty=pen, rhs=rhs)
    return out


# ---------------------------------------------------------------------------
# Negative-case certificate
# ---------------------------------------------------------------------------
def negative(case, chk: Checks, N: int) -> dict:
    d = DATA[case.name]
    rho, a, b, jumps = measure(case.name)
    al, ka = case.alpha, case.kappa
    cre, cim = d["c"]
    chk.check(f"{case.name}: |c| = 1", cre * cre + cim * cim == 1)
    c = AC(cre, cim)
    eta_re, eta_im = cre * cre - cim * cim, 2 * cre * cim
    eta = AC(eta_re, eta_im)
    chk.check(f"{case.name}: Re c > 0 and Re eta > 0 (convexity of the beta=0 terms)",
              cre > 0 and eta_re > 0, f"eta = {eta_re} + {eta_im} i")
    mass = 2 * sum(r * (y - x) for r, x, y in zip(rho, a, b))
    chk.check(f"{case.name}: comparison measure is a probability measure", mass == 1, f"{mass}")
    chk.check(f"{case.name}: density nonnegative", min(rho) >= 0)
    t = LOG(1 / abs(case.lam))
    T = A(cre) * t + A(cim) * PI
    dd = ka - 3 * al
    Cstar = A(ka) * LOG(ka) - A(3 * al) * LOG(al) + A(Fr(3, 2) - dd)
    E, E_same, E_cross = energy_rays(rho, a, b, eta)
    print(f"  E = {fmt(E, 20)}  (same-ray {fmt(E_same, 12)}, cross-ray {fmt(E_cross, 12)})")
    lo, hi = case.claims["E_reported"].strip("()").split(",")
    chk.check(f"{case.name}: E inside the reported enclosure {case.claims['E_reported']}",
              E > A(Fr(lo.strip())) and E < A(Fr(hi.strip())), fmt(E, 16))

    real_terms, cplx_terms = terms_negative(case, jumps, c, eta)
    Y = d["Y"]
    # ---- cellwise sup -----------------------------------------------------------
    t0 = time.time()
    cells = cell_majorants(real_terms, cplx_terms, T, N, Y)
    sup_up = None
    argmax = None
    for i, (U0, U1, eps) in enumerate(cells):
        hi = arb(max((U0 + eps).upper(), (U1 + eps).upper()))
        if sup_up is None or hi > sup_up:
            sup_up, argmax = hi, i
    print(f"  [our bound] sup_[0,{Y}] (V_-+2U_-) <= {upper_str(sup_up)}  near y = {float(Fr(argmax, N)):.4f}"
          f"  (mesh 1/{N}, {time.time()-t0:.1f}s)")

    def Wpoint(y: Fr) -> arb:
        yA = A(y)
        val = -T * yA
        for coef, p in real_terms:
            val += A(coef) * f_real(y - p)
        for coef, alpha, beta, _ in cplx_terms:
            val += A(coef) * Fc(alpha * yA + beta).real
        return val

    # a certified LOWER bound for the sup, from the value at the best mesh point
    i0 = argmax
    vals = [Wpoint(Fr(i0, N)), Wpoint(Fr(i0 + 1, N))]
    sup_low = arb(max(v.lower() for v in vals))
    print(f"  sup is >= {arb(sup_low).str(15, radius=False)} (value at a mesh point)")
    # ---- tail --------------------------------------------------------------------
    bstar = b[-1]
    chk.check(f"{case.name}: support within [0,Y]", bstar < Y)
    tail = A(3 * al) * LOG(Y + al) - A(ka) * LOG(Y) - T * A(Y) + 2 * LOG(Y + bstar)
    chk.check(f"{case.name}: tail majorant at Y={Y} below our sup bound", tail < sup_up,
              f"{fmt(tail, 10)}")
    chk.check(f"{case.name}: tail majorant decreasing: (3a+2)/Y < T", A((3 * al + 2) / Y) < T)
    theta = sup_up
    rhs = Cstar - E + theta
    rhs_up = arb(rhs.upper())
    print(f"  C_* = {fmt(Cstar, 16)}, T = {fmt(T, 16)}")
    print(f"  [our bound] RHS = C_* - E + sup <= {upper_str(rhs_up)}")
    chk.check(f"{case.name}: certified RHS < claimed {frac_str(case.claims['analytic_upper'], 6)}",
              rhs_up < A(case.claims["analytic_upper"]), upper_str(rhs_up))
    # ---- manuscript's own (cruder) bound: mesh max + (6+4J) s/2, s=1/400 ------------
    step = Fr(1, 400)
    J = rho[0] + sum(abs(x - y) for x, y in zip(rho, rho[1:])) + rho[-1]
    err = (6 + 4 * J) * step / 2
    mx = None
    for j in range(int(Y / step) + 1):
        v = Wpoint(step * j).upper()
        mx = v if mx is None or v > mx else mx
    theta_ms = arb(mx) + A(err)
    rhs_ms = Cstar - E + theta_ms
    print(f"  [manuscript method] J = {J}, error (6+4J)s/2 = {frac_str(err, 8)}, theta <= {upper_str(theta_ms)},"
          f" RHS <= {upper_str(rhs_ms)}")
    rep_theta = Fr(case.claims["theta_reported"])
    chk.check(f"{case.name}: manuscript-method theta reproduces reported {case.claims['theta_reported']} to 1e-9",
              abs(theta_ms - A(rep_theta)) < arb(10) ** -9, upper_str(theta_ms))
    return dict(E=E, Cstar=Cstar, T=T, sup_upper=sup_up, sup_lower=sup_low, rhs_upper=rhs_up,
                theta_ms=theta_ms, rhs_ms=rhs_ms, err_ms=err, J=J)


def main():
    name = sys.argv[1]
    N = int(sys.argv[2]) if len(sys.argv) > 2 else 2000
    case = CASES[name]
    chk = Checks(f"energy certificate {name}")
    print(f"# case {name}: kind={DATA[name]['kind']}  mesh 1/{N}  prec={ctx.prec}")
    if DATA[name]["kind"] == "positive":
        res = positive(case, chk, N)
        payload = {k: (fmt(v, 20) if isinstance(v, arb) else v) for k, v in res.items() if k != "ms"}
        payload["manuscript_method"] = {k: (fmt(v, 20) if isinstance(v, arb) else str(v))
                                        for k, v in res["ms"].items()}
    else:
        res = negative(case, chk, N)
        payload = {k: (fmt(v, 20) if isinstance(v, arb) else str(v)) for k, v in res.items()}
    payload["rhs_upper_rational"] = str(arb_to_interval(res["rhs_upper"])[1])
    payload["mesh"] = N
    suffix = "" if N == 2000 else f"-mesh{N}"
    chk.finish(OUT / f"comparison-bounds-{case.slug}{suffix}.json", payload)


if __name__ == "__main__":
    main()
