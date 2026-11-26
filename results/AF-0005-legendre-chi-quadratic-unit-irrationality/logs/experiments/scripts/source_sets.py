#!/usr/bin/env python3
"""Recompute the exceptional sets of [Krisman2026] from its own constants, and the list of
arguments that the present project adds.  Arb balls; exits non-zero on mismatch.

Inputs taken from the paper (cited, not recomputed): Phi_U <= -1.3592161834586374
(Theorem 5.3) and the ten certified values Phi(a) of Table 5.
Inputs from this project: the certified upper bounds of Phi at n = 14 and n = 27
(outputs/real-certificates.txt), rounded up.
"""
import sys

from flint import arb, ctx

ctx.prec = 200
PHI_U = arb("-1.3592161834586374")
TABLE5 = {59: "-2.730260", 61: "-2.746986", 67: "-2.794044", 91: "-2.947508", 95: "-2.969059",
          111: "-3.047021", 117: "-3.073383", 135: "-3.145029", 147: "-3.187657", 195: "-3.329068"}
OURS = {(14, 1): "-2.0046112", (14, -1): "-1.9993684", (27, 1): "-2.3373425", (27, -1): "-2.3359555"}
LOG_Z2 = (2 + arb(5).sqrt()).log()


def t(n, s):
    return ((arb(n) + arb(n * n + 4 * s).sqrt()) / 2).log()


def factor_odd(n):
    out, p = {}, 3
    while n % 2 == 0:
        n //= 2
    while n > 1:
        while n % p == 0:
            out[p] = out.get(p, 0) + 1
            n //= p
        p += 2
    return out


def nu2(n):
    v = 0
    while n % 2 == 0:
        n, v = n // 2, v + 1
    return v


def arith(n, refined):
    nu = nu2(n)
    if nu:
        c2 = abs(nu - 2)
    else:
        c2 = 1 if refined else 2
    tot = arb(4) / 3 + c2 * arb(2).log() / 4
    for p, e in factor_odd(n).items():
        tot += arb(e) * arb(p).log() / 4
        if not refined:
            tot += arb(p).log() / (4 * (p - 1))
    return tot


def sign(x, what):
    if x > 0:
        return 1
    if x < 0:
        return -1
    print("FAIL: undecided sign at", what)
    sys.exit(1)


def source_exceptions(s, lo, hi, direct):
    bad = []
    for n in range(lo, hi + 1):
        phi = PHI_U - (t(n, s) - LOG_Z2) / 2
        if n in direct:
            phi = arb(direct[n])
        if sign(phi + arith(n, False), (n, s)) > 0:
            bad.append(n)
    return bad


def main():
    ok = True
    # chi_2: the shift lemma needs z <= sqrt5 - 2, i.e. n >= 4; n = 1, 2, 3 are excluded a priori
    chi_shift = source_exceptions(1, 4, 20000, {})
    chi = source_exceptions(1, 4, 20000, TABLE5)
    chi_set = sorted([1, 2, 3] + chi)
    printed_chi = sorted([1, 3] + list(range(5, 58, 2)) + [63, 65, 69, 75, 77, 81, 85, 87, 93, 99, 105, 165]
                         + [2, 6, 10, 14, 18, 30])
    odd_shift = [n for n in chi_shift if n % 2]
    print(f"chi_2, source constants, shift lemma only: {len(odd_shift)} odd traces >= 5 with M >= 0 "
          f"(paper: 49, largest 195); largest {max(odd_shift)}")
    print(f"chi_2 exceptional set recomputed: {len(chi_set)} traces; equals printed set: {chi_set == printed_chi}")
    ok &= chi_set == printed_chi and len(odd_shift) == 49 and max(odd_shift) == 195
    # Ti_2: n >= 5 for the shift; n = 3, 4 excluded a priori
    ti = source_exceptions(-1, 5, 20000, {})
    ti_set = sorted([3, 4] + ti)
    printed_ti = sorted(list(range(3, 70, 2)) + [75, 77, 81, 85, 87, 91, 93, 95, 99, 105, 111, 117, 123, 135, 147, 165, 195]
                        + [4, 6, 10, 14, 18, 30])
    print(f"Ti_2 exceptional set recomputed: {len(ti_set)} traces; equals printed set: {ti_set == printed_ti}")
    ok &= ti_set == printed_ti
    ok &= len(printed_chi) == 47 and len(printed_ti) == 57

    def covered(n):
        return (n % 2 == 0 and n >= 14) or (n % 2 == 1 and n >= 27)

    for s, name, exc in ((1, "chi_2", printed_chi), (-1, "Ti_2", printed_ti)):
        new = [n for n in exc if covered(n)]
        left = [n for n in exc if not covered(n)]
        print(f"{name}: {len(new)} new traces: {new}")
        print(f"{name}: {len(left)} traces covered by neither: {left}")
        worst = None
        for n in new:
            n0 = 14 if n % 2 == 0 else 27
            m = arith(n, True) + arb(OURS[(n0, s)]) - (t(n, s) - t(n0, s)) / 2
            if not m < 0:
                print("FAIL: margin not negative at", n, s)
                ok = False
            ub = float((m.mid() + m.rad()).mid())
            if worst is None or ub > worst[1]:
                worst = (n, ub)
        print(f"{name}: every new trace has C(n) + Phi(n0) - (t(n) - t(n0))/2 < 0; largest value {worst[1]:.6f} at n = {worst[0]}")
    ok &= len([n for n in printed_chi if covered(n)]) == 31 and len([n for n in printed_ti if covered(n)]) == 42
    # uniform statement: margins for all n in the claimed range up to 20000
    for s in (1, -1):
        for n in range(14, 20001):
            if not covered(n):
                continue
            n0 = 14 if n % 2 == 0 else 27
            m = arith(n, True) + arb(OURS[(n0, s)]) - (t(n, s) - t(n0, s)) / 2
            if not m < 0:
                print("FAIL: range margin", n, s)
                ok = False
    print("margins negative for every covered n <= 20000, both signs (numerical confirmation of the monotonicity step)")
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
