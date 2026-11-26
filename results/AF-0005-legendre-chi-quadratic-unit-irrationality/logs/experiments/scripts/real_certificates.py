#!/usr/bin/env python3
"""Independent Arb verification of the dual certificates.

Written from the definitions, not from the original verifier.  Differences of method:
  * Arb ball arithmetic (python-flint) instead of 2^-100 fixed-point intervals;
  * the upper integral uses, on every mesh cell, the chord of each convex term and the
    midpoint tangent of each concave term (no curvature error term at all);
  * the positive part of the resulting affine majorant is integrated by the trapezoid
    upper bound (convexity).
Every comparison is a certified Arb comparison; the script exits non-zero on failure.

Usage: real_certificates.py <measures.json> <odd_trace_measures.json> [L]
"""
import json
import sys

from flint import arb, ctx

ctx.prec = 192


def fail(msg):
    print("FAIL:", msg, flush=True)
    sys.exit(1)


def check(cond, msg):
    # `cond` must be a certified truth (Arb comparisons return True only when certain).
    if not cond:
        fail(msg)


def trace_log(n, sigma):
    return ((arb(n) + arb(n * n + 4 * sigma).sqrt()) / 2).log()


def arithmetic_constant(n, refined=True):
    """C(n) = 4/3 + log(d)/4 + c(nu) log(2)/4 with n = 2^nu d.

    refined: c(0) = 1 and no extra odd-prime term (this project).
    not refined: the source's constants c(0) = 2 and the extra sum of log p/(4(p-1)).
    """
    nu, d = 0, n
    while d % 2 == 0:
        nu, d = nu + 1, d // 2
    c2 = abs(nu - 2) if nu else (1 if refined else 2)
    total = arb(4) / 3 + arb(d).log() / 4 + c2 * arb(2).log() / 4
    if not refined:
        m, p = d, 3
        while m > 1:
            if m % p == 0:
                total += arb(p).log() / (4 * (p - 1))
                while m % p == 0:
                    m //= p
            p += 2
    return total


def upper_ball(v):
    """A ball containing the upper endpoint of v."""
    return v.mid() + v.rad()


def positive_part_upper(v):
    if v < 0:
        return arb(0)
    return upper_ball(v)


def verify(cert, n, L):
    N, H, sc, sigma = cert["N"], cert["H"], cert["scale"], cert["sign"]
    lam = arb(cert["lambda"]) / sc
    # admissibility: exact integer checks
    check(len(H) == N and all(isinstance(v, int) and 0 <= v <= sc for v in H), "density range")
    check(2 * sum(H) == N * sc, "mass one")
    check((2 * L) % N == 0, "mesh alignment")
    step = 2 * L // N  # mesh points per density cell
    t = trace_log(n, sigma)
    check(arb(n) + arb(n * n + 4 * sigma).sqrt() >= 2 * (2 + arb(5).sqrt()), "z <= sqrt5 - 2")

    # ---- energy E(mu): exact double antiderivative g(u) = u^2 log|u|/2 - 3u^2/4
    w = arb(2) / N
    gtab = {}

    def g(m):  # g(m*w)
        if m == 0:
            return arb(0)
        m = abs(m)
        if m not in gtab:
            u = m * w
            gtab[m] = u * u * (u.log() / 2 - arb(3) / 4)
        return gtab[m]

    kern = [g(m + 1) + g(m - 1) - 2 * g(m) for m in range(N)]
    E = arb(0)
    for i in range(N):
        if H[i] == 0:
            continue
        E += H[i] * H[i] * kern[0]
        for j in range(i):
            if H[j]:
                E += 2 * H[i] * H[j] * kern[i - j]
    E = E / (arb(sc) * sc)

    # ---- F = 2U - t x - Psi = sum_j c_j f(x - j/L) - t x, f(u) = u log|u| - u
    coef = {}
    for i, v in enumerate(H):
        if v:
            coef[i * step] = coef.get(i * step, 0) + 2 * v
            coef[(i + 1) * step] = coef.get((i + 1) * step, 0) - 2 * v
    # Psi(x) = (f(x+1) - f(x-1))/2 enters with a minus sign; units of 1/sc, so use 2*sc denominators
    coef = {j: 2 * c for j, c in coef.items() if c}
    coef[-L] = coef.get(-L, 0) - sc
    coef[L] = coef.get(L, 0) + sc
    coef = {j: c for j, c in coef.items() if c}
    den = arb(2 * sc)
    nodes = sorted(coef)

    ftab, htab = {}, {}

    def f_int(m):  # f(m/L)
        if m == 0:
            return arb(0)
        if m not in ftab:
            u = arb(abs(m)) / L
            val = u * (u.log() - 1)
            ftab[m] = val if m > 0 else -val
        return ftab[m]

    def f_half(m):  # (f, f') at (2m+1)/(2L)
        if m not in htab:
            a = 2 * m + 1
            u = arb(abs(a)) / (2 * L)
            lg = u.log()
            val = u * (lg - 1)
            htab[m] = (val if a > 0 else -val, lg)
        return htab[m]

    half = arb(1) / (2 * L)
    total = arb(0)
    for k in range(4 * L):
        GL = -t * k / L * den
        GR = -t * (k + 1) / L * den
        for j in nodes:
            c = coef[j]
            m = k - j
            convex = (c > 0) == (m >= 0)
            if convex:  # chord through the endpoint values
                GL += c * f_int(m)
                GR += c * f_int(m + 1)
            else:  # tangent at the midpoint
                val, slope = f_half(m)
                GL += c * (val - slope * half)
                GR += c * (val + slope * half)
        total += positive_part_upper(GL / den - lam) + positive_part_upper(GR / den - lam)
    integral = total * half

    # ---- side conditions of [Krisman2026, Theorem 5.1]
    tail = 2 * arb(4).log() - arb(3).log() - 4 * t  # F(4) <= 2 log 4 - log 3 - 4t
    check(tail < lam - arb(113) / 100, "condition (i) at x = 4")
    check(arb(1) / 2 - t < -arb(94) / 100, "condition (i) slope")
    ccell = 2 * (arb(201) / 100).log() + 1 + t / 100 - lam

    phi = -E + lam + integral
    C = arithmetic_constant(n)
    gap = phi + C

    # ---- primal value J(mu) = E(mu) + int v_z dmu (diagnostic lower bound of any dual value)
    gt = {}

    def g_int(m):  # g(m/L)
        if m == 0:
            return arb(0)
        m = abs(m)
        if m not in gt:
            u = arb(m) / L
            gt[m] = u * u * (u.log() / 2 - arb(3) / 4)
        return gt[m]

    V = arb(0)
    for i, v in enumerate(H):
        if not v:
            continue
        l, r = i * step, (i + 1) * step
        psi_int = (g_int(r + L) - g_int(l + L) - g_int(r - L) + g_int(l - L)) / 2
        V += v * (-t * arb(r * r - l * l) / (2 * L * L) - psi_int)
    primal = E + V / sc + C
    return {"t": t, "C": C, "E": E, "integral": integral, "phi": phi, "gap": gap,
            "primal": primal, "ccell": ccell, "lam": lam}


def up(v, digits=9):
    return float(upper_ball(v).mid()) if True else None


def main():
    even = json.load(open(sys.argv[1]))
    odd = json.load(open(sys.argv[2]))
    L = int(sys.argv[3]) if len(sys.argv) > 3 else 4000
    print(f"mesh 1/{L}, Arb precision {ctx.prec} bits", flush=True)
    favourable = [(even["7,1"], 14), (even["7,-1"], 14), (even["9,1"], 18), (even["9,-1"], 18),
                  (even["15,1"], 30), (even["15,-1"], 30), (odd["27,1"], 27), (odd["27,-1"], 27)]
    diagnostic = [(even["5,1"], 10), (even["5,-1"], 10), (odd["25,1"], 25), (odd["25,-1"], 25)]
    for cert, n in favourable + diagnostic:
        r = verify(cert, n, L)
        print(f"n={n:3d} sigma={cert['sign']:+d} t={float(r['t'].mid()):.12f} C(n)={float(r['C'].mid()):.12f} "
              f"E={float(r['E'].mid()):.12f} int<={up(r['integral']):.12f} Phi<={up(r['phi']):.12f} "
              f"C+Phi<={up(r['gap']):.12f} C+J>={float((r['primal'].mid() - r['primal'].rad()).mid()):.12f} "
              f"ccell<={up(r['ccell']):.4f}", flush=True)
        if (cert, n) in favourable:
            check(r["gap"] < -arb(1) / 1000, f"favourable comparison at n={n}")
        else:
            check(r["primal"] > 0, f"diagnostic primal bound at n={n}")
    print("PASS: 8 favourable comparisons (< -1/1000) and 4 diagnostic primal lower bounds (> 0).")


if __name__ == "__main__":
    main()
