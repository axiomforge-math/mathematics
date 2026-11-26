"""Checker for the arithmetic rates and the final comparison of the rates (Table 2).

Exceptional-prime leading contributions and the final arithmetic (content) rate.

Rate (per unit^2, unit = n for 2/11, h for the others):
    rate = [int_delta^kappa B - 2 m delta]                       (ordinary primes, verify_profile_integrals.py)
           - (m kappa - m^2/2) log 2                              (p = 2: h largest pole indices)
           - f_P (m - d'/2)^2 log P                               (loss prime P, Newton exponent f_P)
           + e_G (m alpha + m^2/6) log G                          (gain prime G, e_G = v_G(1/lambda))
with d' = kappa - 3 alpha.  These leading coefficients are re-derived here from the
exact finite sums of Propositions 3.2, 3.3 and 3.5 of the manuscript (checked against the closed forms
by exact summation for several n), and the logs are Arb balls.

Checks
  * the inequalities used by the original programs, e.g. for 2/11 (n-scale)
        9/2 - 16 log 2 - (25/4) log 9 + (20/3) log 11 > -4.338,
    and the corresponding '>-1.33', '>-2/5', '>-0.521323';
  * the same with the exact profile value from verify_profile_integrals.py;
  * the final comparison arithmetic rate > analytic rate, using the certified analytic
    upper bounds of verify_comparison_bounds.py (read from
    outputs/comparison-bounds-*.json) and, separately, the thresholds of Table 2.

Usage: python verify_rate_comparison.py
       (needs outputs/profile-integrals.json and outputs/comparison-bounds-*.json)
"""

from __future__ import annotations

import json
from fractions import Fraction as Fr

from flint import arb

from define_parameters import CASES, OUT, A, Checks, arb_to_interval, check_exceptional_data, fmt, frac_str, upper_str


def LOG(x) -> arb:
    x = Fr(x)
    return arb(x.numerator).log() - arb(x.denominator).log()


def exact_sums(case, n: int):
    """The finite exceptional-prime sums at index n (without the -2hL terms)."""
    h, K, A_ = case.H * n, case.C * n, case.B * n
    # p = 2: sum of the h largest pole indices in (A, K]
    s2 = sum(range(K - h + 1, K + 1))
    # loss prime: f * sum_{i<h} (2i - (K-3A) + 1)_+
    sP = case.fP * sum(max(2 * i - (K - 3 * A_) + 1, 0) for i in range(h))
    # gain prime: e * sum_{k=0}^{h-2} (A + 1 + floor(k/3))
    sG = case.eG * sum(A_ + 1 + k // 3 for k in range(h - 1))
    return s2, sP, sG


def leading(case):
    m, al, ka = case.m, case.alpha, case.kappa
    dprime = ka - 3 * al
    return m * ka - m * m / 2, case.fP * (m - dprime / 2) ** 2, case.eG * (m * al + m * m / 6)


def main():
    chk = Checks("rate comparison")
    prof = json.loads((OUT / "profile-integrals.json").read_text())
    payload = {}
    for name, case in CASES.items():
        print(f"# case {name}")
        for msg in check_exceptional_data(case):
            chk.check(f"{name}: exceptional data", False, msg)
        chk.check(f"{name}: exceptional prime table consistent with lambda",
                  not check_exceptional_data(case), f"P={case.P} (f={case.fP}), G={case.G} (e={case.eG})")
        c2, cP, cG = leading(case)
        # compare the closed forms with the exact finite sums: sum/unit^2 -> leading coefficient
        ok = True
        for n in (50, 200, 800):
            u = n * case.scale
            s2, sP, sG = exact_sums(case, n)
            for s, c in ((s2, c2), (sP, cP), (sG, cG)):
                if abs(Fr(s, u * u) - c) > Fr(4 * case.H, u):  # O(1/u) discrepancy only
                    ok = False
        chk.check(f"{name}: leading coefficients match the finite sums (O(1/u) error)", ok,
                  f"2:{c2}  {case.P}:-{cP}  {case.G}:+{cG}")
        exc = -A(c2) * LOG(2) - A(cP) * LOG(case.P) + A(cG) * LOG(case.G)
        prof_exact = Fr(prof[name]["exact_minus_cut"])
        prof_mid = Fr(prof[name]["midpoint_minus_cut"])
        rate_exact = A(prof_exact) + exc
        print(f"  exceptional contribution = {fmt(exc, 16)}")
        print(f"  profile (exact) - cut     = {frac_str(prof_exact, 16)}")
        print(f"  arithmetic rate (exact profile) = {fmt(rate_exact, 16)}  "
              f"(reported {case.claims['content_rate_reported']})")
        lb = case.claims["content_rate_lower"]
        if name == "2/11":
            stated = A(Fr(9, 2)) - 16 * LOG(2) - A(Fr(25, 4)) * LOG(9) + A(Fr(20, 3)) * LOG(11)
            chk.check("2/11: n-scale bound 9/2 - 16log2 - (25/4)log9 + (20/3)log11 > -4.338",
                      stated > A(lb), fmt(stated, 14))
            chk.check("2/11: closed form equals the general exceptional formula",
                      abs(stated - (A(Fr(9, 2)) + exc)) < arb(10) ** -30)
        chk.check(f"{name}: arithmetic rate with the exact profile > {frac_str(lb, 6)}",
                  rate_exact > A(lb), fmt(rate_exact, 14))
        rate_mid = A(prof_mid) + exc
        chk.check(f"{name}: original chain: rate with the midpoint profile > {frac_str(lb, 6)}",
                  rate_mid > A(lb), fmt(rate_mid, 14))
        rate_lo = arb(rate_exact.lower())
        # final comparison
        ej = OUT / f"comparison-bounds-{case.slug}.json"
        res = {"exceptional": fmt(exc, 20), "rate_exact_profile": fmt(rate_exact, 20),
               "rate_lower_rational": str(arb_to_interval(rate_exact)[0])}
        if ej.exists():
            en = json.loads(ej.read_text())
            an_up = Fr(en["rhs_upper_rational"])
            margin = rate_lo - A(an_up)
            print(f"  certified analytic upper bound (ours) = {frac_str(an_up, 12)}  -> margin >= {upper_str(arb(margin.lower()), 8)}")
            chk.check(f"{name}: FINAL arithmetic rate > analytic rate (our certified bounds)",
                      rate_exact > A(an_up), f"margin {fmt(margin, 8)}")
            res["analytic_upper_ours"] = str(an_up)
            res["margin_ours"] = fmt(margin, 12)
            # the analytic method of the original programs, recomputed by verify_comparison_bounds.py
            ms = en.get("manuscript_method", {}).get("rhs") or en.get("rhs_ms")
            if ms:
                ms_up = A(Fr(arb_to_interval(arb(ms.split("+/-")[0].strip("[ ")) +
                                             arb(0, float(ms.split("+/-")[1].strip("] "))))[1]))
                m2 = rate_mid - ms_up
                print(f"  original chain (midpoint profile, original analytic method recomputed): "
                      f"margin {fmt(m2, 10)}")
                chk.check(f"{name}: original chain certified: midpoint rate > recomputed original analytic bound",
                          m2 > 0, fmt(m2, 10))
                res["margin_original_chain"] = fmt(m2, 12)
            # the same with the refined mesh 1/6000 (the margins quoted in the manuscript)
            ej6 = OUT / f"comparison-bounds-{case.slug}-mesh6000.json"
            if ej6.exists():
                an6 = Fr(json.loads(ej6.read_text())["rhs_upper_rational"])
                m6 = rate_lo - A(an6)
                print(f"  certified analytic upper bound, mesh 1/6000 = {frac_str(an6, 12)}  -> margin >= {upper_str(arb(m6.lower()), 8)}")
                chk.check(f"{name}: FINAL arithmetic rate > analytic rate (mesh 1/6000)", rate_exact > A(an6),
                          f"margin {fmt(m6, 8)}")
                res["analytic_upper_mesh6000"] = str(an6)
                res["margin_mesh6000"] = fmt(m6, 12)
        else:
            chk.check(f"{name}: certified analytic bound available", False, f"missing {ej.name}")
        chk.check(f"{name}: FINAL with the thresholds of Table 2 ({frac_str(lb, 6)} > {frac_str(case.claims['analytic_upper'], 6)})",
                  lb > case.claims["analytic_upper"])
        payload[name] = res
    chk.finish(OUT / "rate-comparison.json", payload)


if __name__ == "__main__":
    main()
