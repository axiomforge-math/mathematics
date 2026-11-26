#!/usr/bin/env python
"""Checker for the decay constant (manuscript, Proposition 5.10, Appendices B-D), in Arb:

    D = 2*lam*theta + 4*J - U + L,     lam = 17/16,

    nu   = Leb[0,1] + (1/2) Leb[1,9/8]              (node measure, mass lam)
    mu   = trial measure of ../certificates/decay-trial-measure.json (piecewise-uniform on segments, mass lam)
    V(z) = U^mu(z) - U^nu(z) + (1 - eps0) pi |Im z|,  eps0 = 1e-6,
    theta  = strict lower bound of V on the polygon Gamma (upper half + conjugate + vertical tails)
    J      = lower bound of int_{-r0}^0 min(V(x) - theta, 0) dx
    U >= I(mu),  L <= I(nu)   (logarithmic energies  I(m) = iint -log|z-w| dm dm).

Written from the mathematical definitions only, separately from the original program
certify_decay_constant.py:

* potentials: closed form of the potential of a uniform segment,
      U_[a,b](z) = 1 - log|w| - [x log|u| - (x-1) log|u-1| - y (arg u - arg(u-1))],
  w = b - a, u = (z-a)/w = x + i y  (principal arguments; the y-term is 0 when y = 0),
  evaluated with Arb at exact rational points;
* whole-cell enclosure: along a straight cell z(t) = z0 + t e (t in [0,1]) that contains
  no segment endpoint in its interior, V is C^2 and
      |V''(t)| <= |e|^2 sum_a |c_a| / |z(t) - a|,   c_a = sum_{segments with endpoint a} (+-) m/w,
  (from (U^m)'' = Re[e^2 sum m/w (1/(z-b) - 1/(z-a))]; the field is linear on cells).
  With |V''| <= C0 + C1/t + C2/(1-t), the Green-function bound gives
      |V - chord| <= C0/8 + (C1 + C2)/e    (max_t -t log t = 1/e);
* pair energies: mixed primitive Phi(Z) = Z^2 (Log(rZ)/2 - 3/4), Phi'' = Log(rZ), with a
  Gaussian-integer rotation r such that Re(rZ) >= 0 on the four corner differences
  (checked exactly), E = -Re[(Phi(b-c)+Phi(a-d)-Phi(a-c)-Phi(b-d))/(v w)] + log|r|;
  self-energy of a uniform segment of length l: 3/2 - log l;
* I(nu): closed form (computed with Arb);
* vertical tail: for Re z < 0, U^nu(z) <= -lam log|z| and U^mu(z) >= -lam log(|z| + R_mu), so
  V >= (1-eps0) pi y - lam R_mu / y on the tail, which is increasing in y.

All asserted inequalities use Arb lower/upper endpoints or exact rationals; the script exits
with status 1 if any check fails.

Usage: python verify_decay_constant.py ../certificates/decay-trial-measure.json [tol_contour] [tol_real]
"""

from __future__ import annotations

import json
import sys
import time
from collections import defaultdict

from flint import arb, acb, ctx, fmpq, fmpz

ctx.prec = 256
FAIL = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg, flush=True)
    if not cond:
        FAIL.append(msg)


# ---------------------------------------------------------------- exact complex helpers
def csub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def cadd(a, b):
    return (a[0] + b[0], a[1] + b[1])


def cmul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def cconj(a):
    return (a[0], -a[1])


def cnorm(a):
    return a[0] * a[0] + a[1] * a[1]


def cdiv(a, b):
    n = cnorm(b)
    t = cmul(a, cconj(b))
    return (t[0] / n, t[1] / n)


def arb_lower_q(x: arb) -> fmpq:
    """Exact rational <= every point of the ball x."""
    lo = x.lower()
    m, e = lo.man_exp()
    m, e = int(m), int(e)
    return fmpq(m * 2**e) if e >= 0 else fmpq(m, 2 ** (-e))


def arb_upper_q(x: arb) -> fmpq:
    hi = x.upper()
    m, e = hi.man_exp()
    m, e = int(m), int(e)
    return fmpq(m * 2**e) if e >= 0 else fmpq(m, 2 ** (-e))


def qsqrt_upper(q: fmpq) -> fmpq:
    return arb_upper_q(arb(q).sqrt())


def qsqrt_lower(q: fmpq) -> fmpq:
    if q == 0:
        return fmpq(0)
    return arb_lower_q(arb(q).sqrt())


# ---------------------------------------------------------------- data
def load(path):
    data = json.load(open(path))
    Dc = data["coordinate_denominator"]
    M = data["mass_denominator"]
    pt = lambda v: (fmpq(v[0], Dc), fmpq(v[1], Dc))
    verts = [pt(v) for v in data["vertices"]]
    mu = [(pt(a), pt(b), fmpq(m, M)) for a, b, m in data["segments"]]
    return verts, mu


LAM = fmpq(17, 16)
EPS0 = fmpq(1, 10**6)
NU = [((fmpq(0), fmpq(0)), (fmpq(1), fmpq(0)), fmpq(1)),
      ((fmpq(1), fmpq(0)), (fmpq(9, 8), fmpq(0)), fmpq(1, 16))]
PI = arb.pi()


# ---------------------------------------------------------------- potentials
def seg_pot(z, a, b):
    """Potential at the exact point z of the uniform PROBABILITY measure on [a,b]."""
    w = csub(b, a)
    x, y = cdiv(csub(z, a), w)
    r0 = x * x + y * y
    r1 = (x - 1) * (x - 1) + y * y
    T = arb(0)
    if r0 != 0:
        T += arb(x) * arb(r0).log() / 2
    if r1 != 0:
        T -= arb(x - 1) * arb(r1).log() / 2
    if y != 0:
        T -= arb(y) * (arb.atan2(arb(y), arb(x)) - arb.atan2(arb(y), arb(x - 1)))
    return 1 - arb(cnorm(w)).log() / 2 - T


class Field:
    def __init__(self, mu):
        self.signed = [(a, b, m) for a, b, m in mu] + [(a, b, -m) for a, b, m in NU]
        self.cache = {}
        coef = defaultdict(lambda: (fmpq(0), fmpq(0)))
        for a, b, m in self.signed:
            c = cdiv((m, fmpq(0)), csub(b, a))  # m / w
            coef[b] = cadd(coef[b], c)
            coef[a] = csub(coef[a], c)
        # |c_a| upper bounds (exact rationals)
        self.coef = [(p, qsqrt_upper(cnorm(c))) for p, c in coef.items() if cnorm(c) != 0]

    def V(self, z):
        if z in self.cache:
            return self.cache[z]
        v = arb(0)
        for a, b, m in self.signed:
            v += arb(m) * seg_pot(z, a, b)
        v += (1 - arb(EPS0)) * PI * arb(abs(z[1]))
        self.cache[z] = v
        return v

    def err(self, z0, z1):
        """Bound on max_t |V(z(t)) - chord(t)|, or None if an endpoint lies inside the cell."""
        e = csub(z1, z0)
        ee = cnorm(e)
        le = arb(ee).sqrt()
        C0 = arb(0)
        C12 = arb(0)
        for p, c in self.coef:
            if p == z0 or p == z1:
                C12 += le * arb(c)
                continue
            d = csub(p, z0)
            tau = cmul(d, cconj(e))[0] / ee
            if tau < 0:
                tau = fmpq(0)
            elif tau > 1:
                tau = fmpq(1)
            proj = (z0[0] + tau * e[0], z0[1] + tau * e[1])
            d2 = cnorm(csub(p, proj))
            if d2 == 0:
                return None
            C0 += arb(ee) * arb(c) / arb(d2).sqrt()
        return C0 / 8 + C12 / arb(1).exp()


def on_segment(p, a, b):
    d = csub(p, a)
    e = csub(b, a)
    t = cmul(d, cconj(e))
    return t[1] == 0 and 0 <= t[0] <= cnorm(e)


def cells(field, a, b, tol):
    pts = {a, b}
    for p, _ in field.coef:
        if on_segment(p, a, b):
            pts.add(p)
    e = csub(b, a)
    pts = sorted(pts, key=lambda p: cmul(csub(p, a), cconj(e))[0])
    stack = list(zip(pts, pts[1:]))
    out = []
    while stack:
        u, v = stack.pop()
        er = field.err(u, v)
        if er is not None and arb_upper_q(er) <= tol:
            out.append((u, v, er))
            continue
        mid = ((u[0] + v[0]) / 2, (u[1] + v[1]) / 2)
        stack.append((u, mid))
        stack.append((mid, v))
    return out


# ---------------------------------------------------------------- energies
ROTS = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1),
        (2, 1), (2, -1), (1, 2), (1, -2), (-2, 1), (-2, -1), (-1, 2), (-1, -2)]


def Phi(Z, r):
    if Z == (fmpq(0), fmpq(0)):
        return acb(0)
    Za = acb(arb(Z[0]), arb(Z[1]))
    rZ = cmul((fmpq(r[0]), fmpq(r[1])), Z)
    L = acb(arb(rZ[0]), arb(rZ[1])).log()
    return Za * Za * (L / 2 - acb(fmpq(3, 4)))


def pair_energy(S1, S2):
    """iint -log|z-w| for uniform probability measures on segments S1, S2 (disjoint interiors)."""
    a, b = S1
    c, d = S2
    if (a, b) == (c, d):
        return arb(fmpq(3, 2)) - arb(cnorm(csub(b, a))).log() / 2
    v = csub(b, a)
    w = csub(d, c)
    Zs = [csub(b, c), csub(a, d), csub(a, c), csub(b, d)]
    for r in ROTS:
        rq = (fmpq(r[0]), fmpq(r[1]))
        if all(cmul(rq, Z)[0] >= 0 for Z in Zs):
            break
    else:
        raise RuntimeError("no rotation found for pair %s %s" % (S1, S2))
    Q = Phi(Zs[0], r) + Phi(Zs[1], r) - Phi(Zs[2], r) - Phi(Zs[3], r)
    vw = cmul(v, w)
    val = -(Q / acb(arb(vw[0]), arb(vw[1]))).real
    return val + arb(r[0] * r[0] + r[1] * r[1]).log() / 2


def energy(meas):
    tot = arb(0)
    for i, (a, b, m) in enumerate(meas):
        tot += arb(m) * arb(m) * pair_energy((a, b), (a, b))
        for c, d, n in meas[:i]:
            tot += 2 * arb(m) * arb(n) * pair_energy((a, b), (c, d))
    return tot


def I_nu_closed():
    # I(nu) = 3/2 + (1/256)(3/2 + 3 log 2) - [(81/128) log(9/8) + (3/128) log 2 - 3/16]
    l2 = arb(2).log()
    return (arb(fmpq(3, 2)) + (arb(fmpq(3, 2)) + 3 * l2) / 256
            - (arb(fmpq(81, 128)) * arb(fmpq(9, 8)).log() + arb(fmpq(3, 128)) * l2 - arb(fmpq(3, 16))))


# ---------------------------------------------------------------- main
def main():
    path = sys.argv[1]
    tolc = fmpq(sys.argv[2]) if len(sys.argv) > 2 else fmpq(1, 10**5)
    tolr = fmpq(sys.argv[3]) if len(sys.argv) > 3 else fmpq(1, 10**5)
    t0 = time.time()
    verts, mu = load(path)
    print("vertices", len(verts), "segments", len(mu), "tol contour", tolc, "tol real", tolr, flush=True)

    # --- structural checks (exact)
    check(sum((m for _, _, m in mu), fmpq(0)) == LAM, "mass(mu) = 17/16 exactly")
    check(all(m > 0 and a != b for a, b, m in mu), "mu has positive masses on nondegenerate segments")
    key = lambda s: (s[0][0], s[0][1], s[1][0], s[1][1], s[2])
    check(sorted(mu, key=key) == sorted([(cconj(a), cconj(b), m) for a, b, m in mu], key=key),
          "mu is conjugation symmetric")
    check(verts[0][1] == 0 and verts[0][0] < 0, "Gamma crosses the real axis at -r0 < 0")
    check(all(v[0] < 0 and v[1] >= 0 for v in verts), "upper polygon in Re z < 0, Im z >= 0")
    check(all(verts[i][1] < verts[i + 1][1] for i in range(len(verts) - 1)), "Im strictly increasing along upper polygon")
    r0 = -verts[0][0]
    edges = list(zip(verts, verts[1:]))
    alledges = edges + [(cconj(a), cconj(b)) for a, b in edges] + [(verts[0], (fmpq(0), fmpq(0)))]
    check(all(any(on_segment(a, u, v) and on_segment(b, u, v) for u, v in alledges) for a, b, _ in mu),
          "every mu segment lies on an edge of Gamma or on [-r0,0]")
    Rmu2 = max(cnorm(p) for a, b, _ in mu for p in (a, b))
    Rmu = qsqrt_upper(Rmu2)
    print("r0 =", float(r0), " R_mu <=", float(Rmu), flush=True)

    field = Field(mu)

    # --- theta on the finite upper contour
    cc = []
    for a, b in edges:
        cc += cells(field, a, b, tolc)
    print("contour cells", len(cc), "[%.0fs]" % (time.time() - t0), flush=True)
    th = None
    argmin = None
    maxerr = arb(0)
    for u, v, er in cc:
        lo = arb_lower_q(field.V(u) - er)
        lo2 = arb_lower_q(field.V(v) - er)
        cand = min(lo, lo2)
        if th is None or cand < th:
            th, argmin = cand, (u, v)
    theta = th - fmpq(1, 10**9)  # strictness buffer
    print("theta (strict lower bound of V on finite contour) =", float(theta),
          "attained near", (float(argmin[0][0]), float(argmin[0][1])), flush=True)
    # max of V endpoint values minus theta: how flat is V on the contour?
    vals = sorted(float(field.V(u).mid()) for u, v, er in cc)
    print("V on contour cell endpoints: min %.9f  median %.9f  max %.9f" % (vals[0], vals[len(vals) // 2], vals[-1]), flush=True)

    # --- vertical tail
    xL, yL = verts[-1]
    tail_lo = (1 - arb(EPS0)) * PI * arb(yL) - arb(LAM) * arb(Rmu) / arb(yL)
    check(arb_lower_q(tail_lo) > theta, "tail: V >= (1-eps0) pi y - lam R_mu / y >= %.6f > theta on y >= %s"
          % (float(tail_lo.mid()), float(yL)))

    # --- J on [-r0, 0]
    rc = cells(field, verts[0], (fmpq(0), fmpq(0)), tolr)
    print("real cells", len(rc), "[%.0fs]" % (time.time() - t0), flush=True)
    J = fmpq(0)
    neg_len = fmpq(0)
    for u, v, er in rc:
        A = arb_lower_q(field.V(u) - er - arb(theta))
        B = arb_lower_q(field.V(v) - er - arb(theta))
        length = abs(v[0] - u[0])
        lo, hi = (A, B) if A <= B else (B, A)
        if hi <= 0:
            J += length * (lo + hi) / 2
            neg_len += length
        elif lo < 0:
            J -= length * lo * lo / (2 * (hi - lo))
            neg_len += length * (-lo) / (hi - lo)
    print("J lower =", float(J), " (measure of {chord-lower < theta} ~ %.5f of r0 = %.5f)" % (float(neg_len), float(r0)),
          flush=True)

    # --- energies
    Iv = I_nu_closed()
    Iv_check = energy(NU)
    check(Iv.overlaps(Iv_check), "I(nu) closed form agrees with segment-pair formula")
    L = arb_lower_q(Iv)
    print("I(nu) =", Iv, flush=True)
    Imu = energy(mu)
    U = arb_upper_q(Imu)
    print("I(mu) =", Imu, "[%.0fs]" % (time.time() - t0), flush=True)

    D = 2 * LAM * theta + 4 * J - U + L
    print("theta lower  =", float(theta))
    print("J lower      =", float(J))
    print("I(mu) upper  =", float(U))
    print("I(nu) lower  =", float(L))
    print("D_alt lower  =", float(D), " exact rational:", D, flush=True)
    check(D >= fmpq(35099, 10000), "D_alt >= 3.5099")
    gain = arb(2).log() / 256
    check(arb_lower_q(gain) >= fmpq(2707, 10**6), "log(2)/256 >= 0.002707")
    Dsep = D + arb_lower_q(gain)
    print("D_sep lower  =", float(Dsep), flush=True)
    check(Dsep >= fmpq(3512607, 10**6), "D_sep >= 3.512607")
    A = fmpq(304227995343501721142691896310988016794079029050925423,
             86622067750624596685118168422516024981216422248448000)
    print("margin D_sep - A >=", float(Dsep - A), flush=True)
    check(Dsep > A, "D_sep > A (claimed arithmetic integral)")
    print("total time %.0fs" % (time.time() - t0))
    if FAIL:
        print("CERTIFICATE FAILED:", FAIL)
        sys.exit(1)
    print("ALL DECAY CHECKS PASSED")


if __name__ == "__main__":
    main()
