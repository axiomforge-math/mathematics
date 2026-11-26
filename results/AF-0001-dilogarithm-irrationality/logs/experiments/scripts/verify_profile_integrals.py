"""Checker for the profile integrals: exact value of  int_delta^kappa B(x) dx.

Manuscript: Definition 5.1, Proposition 5.6, Table 5 and Appendix A.2. Written from the
definitions of the manuscript, not from the original programs.

Units: x = p/u where u = n (2/11) or u = h (the other three values); see Remark 7.8.
With m = h/u, alpha = A/u, kappa = K/u:

    q_s = floor(s/x), r_s = s - q_s x            (s in {alpha, kappa, m})
    a(u) = q_alpha + [u < r_alpha],  c(u) = q_kappa + [u < r_kappa],  0 < u < x
    w(u) = 3a(u) - c(u) - 1
    jet slots   : weight w(u) + 2j, j >= 0, capacity du
    raw slots   : weight w(u) + 2j + 2[a(u)=0, j = c(u)-a(u)-1], 0 <= j < c(u)-a(u),
                  only negative weights, capacity du
    J(x) = min cost of jet mass exactly m;  R(x) = min cost of at most mass m of raw slots
    B(x) = m(q_kappa - 3 q_alpha) - 2(x q_m(q_m-1)/2 + q_m r_m) + max(J(x), R(x)).

Method (no quadrature, exact rationals):
  1. Partition (delta, kappa) at all points s/j, s in {m, alpha, kappa, kappa-alpha}:
     floors and the order of r_alpha, r_kappa are constant on each open piece, so slot
     weights are constant and capacities affine in x.
  2. On each piece J and R are continuous piecewise-affine (LP value with affine
     right-hand side).  Their breakpoints are the solutions of  S_k(x) = m, where S_k
     is the (affine) cumulative capacity of the k cheapest slots.  Between breakpoints
     both are affine; this is *verified* (value at the midpoint = mean of endpoint
     values, exactly).  The maximum of the two affine functions is integrated exactly
     (splitting at the crossing).
  3. The infinite jet list is truncated at q_m + 4 levels; exactness of the truncation
     is verified at every evaluation (the marginal used weight is <= the cheapest
     omitted weight).
  The result is the exact rational value of the integral.  We also compute the
  midpoint sum  sum (r-l) B(mid)  of the original programs and verify, piece by piece,
  that it is <= the exact integral (the convexity argument of Lemma A.1).

Usage: python verify_profile_integrals.py CASE   (CASE in 2/11, 2/9, -2/9, -2/7, or 'all')
"""

from __future__ import annotations

import sys
import time
from fractions import Fraction as Fr
from math import floor

from define_parameters import CASES, OUT, Case, Checks, frac_str

# an affine function of x is a pair (c0, c1) meaning c0 + c1 x


def aff_eval(f, x):
    return f[0] + f[1] * x


def partition(case: Case) -> list[Fr]:
    m, al, ka, de = case.m, case.alpha, case.kappa, case.delta
    pts = {de, ka}
    for s in {m, al, ka, ka - al}:
        if s <= 0:
            continue
        j = 1
        while s / j > de:
            if s / j < ka:
                pts.add(s / j)
            j += 1
    return sorted(pts)


def structure(case: Case, xm: Fr, at_point: bool = False):
    """Slot lists (weight, affine capacity) valid on the open piece containing xm.

    With at_point=True, xm may be a partition point: the floors are taken at xm itself
    and zero-length pieces are dropped (this is the exact discrete-limit value at xm)."""
    m, al, ka = case.m, case.alpha, case.kappa
    qa, qk, qm = floor(al / xm), floor(ka / xm), floor(m / xm)
    ra = (al, Fr(-qa))
    rk = (ka, Fr(-qk))
    marks = [(Fr(0), Fr(0)), ra, rk, (Fr(0), Fr(1))]
    marks.sort(key=lambda f: aff_eval(f, xm))
    types = []
    for lo, hi in zip(marks, marks[1:]):
        cap = (hi[0] - lo[0], hi[1] - lo[1])
        if cap == (0, 0):
            continue
        lo_v, hi_v = aff_eval(lo, xm), aff_eval(hi, xm)
        if hi_v <= lo_v:
            if at_point and hi_v == lo_v:
                continue
            raise RuntimeError("degenerate piece at a midpoint")
        u = (lo_v + hi_v) / 2
        a = qa + (1 if u < aff_eval(ra, xm) else 0)
        c = qk + (1 if u < aff_eval(rk, xm) else 0)
        types.append((a, c, cap))
    nlev = qm + 4
    jet = []
    raw = []
    for a, c, cap in types:
        w = 3 * a - c - 1
        for j in range(nlev):
            jet.append((w + 2 * j, cap))
        for j in range(c - a):
            wt = w + 2 * j + (2 if (a == 0 and j == c - a - 1) else 0)
            if wt < 0:
                raw.append((wt, cap))
    jet.sort(key=lambda s: s[0])
    raw.sort(key=lambda s: s[0])
    wmin = min(3 * a - c - 1 for a, c, _ in types)
    omitted_min = wmin + 2 * nlev
    norm = (m * (qk - 3 * qa) - 2 * m * qm, -Fr(2) * Fr(qm * (qm - 1), 2) + 2 * qm * qm)
    # norm(x) = m(qk-3qa) - 2( x qm(qm-1)/2 + qm (m - qm x) )
    return dict(qa=qa, qk=qk, qm=qm, types=types, jet=jet, raw=raw,
                omitted_min=omitted_min, norm=norm)


def greedy(slots, x, mass, exact_mass: bool):
    """Min cost of mass `mass` (exact_mass) or at most `mass` from sorted slots."""
    left = mass
    cost = Fr(0)
    marginal = None
    for w, cap in slots:
        cval = aff_eval(cap, x)
        if cval < 0:
            raise RuntimeError("negative capacity")
        d = cval if cval < left else left
        if d > 0:
            cost += w * d
            left -= d
            marginal = w
        if left == 0:
            break
    if exact_mass and left != 0:
        raise RuntimeError("jet mass not filled: truncation too short")
    return cost, marginal


def J_val(st, x, mass):
    v, marg = greedy(st["jet"], x, mass, True)
    if marg is not None and marg > st["omitted_min"]:
        raise RuntimeError("jet truncation not exact")
    return v


def R_val(st, x, mass):
    return greedy(st["raw"], x, mass, False)[0]


def B_val(st, x, mass):
    return aff_eval(st["norm"], x) + max(J_val(st, x, mass), R_val(st, x, mass))


# ---------------------------------------------------------------------------
# Second, separately written evaluator: closed form over integer weight thresholds.
# For a type t with jet weight w_t and capacity cap_t, the slots of weight <= v number
# N_t(v) = max(0, floor((v - w_t)/2) + 1)  (all levels j >= 0: no truncation), and
# for raw slots min(N_t(v), Jr_t) where Jr_t is the number of negative raw slots of t
# (a prefix, since raw weights increase with j).  C(v) = sum_t cap_t N_t(v) is affine
# in x for fixed v; J = cost(v*-1) + v*(m - C(v*-1)) with v* the first v, C(v) >= m.
# ---------------------------------------------------------------------------
def _types_w(st):
    out = []
    for a, c, cap in st["types"]:
        w = 3 * a - c - 1
        jr = 0
        for j in range(c - a):
            wt = w + 2 * j + (2 if (a == 0 and j == c - a - 1) else 0)
            if wt < 0:
                jr += 1
            else:
                break
        # sanity: negativity is a prefix
        for j in range(jr, c - a):
            wt = w + 2 * j + (2 if (a == 0 and j == c - a - 1) else 0)
            assert wt >= 0
        out.append((w, cap, jr))
    return out


def _N(v, w, lim=None):
    k = (v - w) // 2 + 1
    if k < 0:
        k = 0
    if lim is not None and k > lim:
        k = lim
    return k


def _C_cost(tw, v, x, raw):
    C = Fr(0)
    cost = Fr(0)
    for w, cap, jr in tw:
        k = _N(v, w, jr if raw else None)
        cv = aff_eval(cap, x)
        C += cv * k
        cost += cv * (k * w + k * (k - 1))
    return C, cost


def _C_aff(tw, v, raw):
    c0, c1 = Fr(0), Fr(0)
    for w, cap, jr in tw:
        k = _N(v, w, jr if raw else None)
        c0 += cap[0] * k
        c1 += cap[1] * k
    return c0, c1


def fast_J(tw, x, mass):
    """(value, marginal weight v*) of the jet LP (infinitely many levels)."""
    wmin = min(w for w, _, _ in tw)
    v = wmin + 2 * int(mass / x) - 8 if x > 0 else wmin
    v = max(v, wmin - 1)
    while _C_cost(tw, v, x, False)[0] >= mass and v >= wmin:
        v -= 4
    while True:
        C, _ = _C_cost(tw, v, x, False)
        if C >= mass:
            break
        v += 1
    Cp, costp = _C_cost(tw, v - 1, x, False)
    return costp + v * (mass - Cp), v


def fast_R(tw, x, mass):
    if not any(jr for _, _, jr in tw):
        return Fr(0), None
    wmin = min(w for w, _, jr in tw if jr)
    v = wmin
    while v < 0:
        C, _ = _C_cost(tw, v, x, True)
        if C >= mass:
            Cp, costp = _C_cost(tw, v - 1, x, True)
            return costp + v * (mass - Cp), v
        v += 1
    return _C_cost(tw, -1, x, True)[1], None


def fast_breakpoints(tw, mass, l, r, raw):
    if raw:
        if not any(jr for _, _, jr in tw):
            return set()
        vs = range(min(w for w, _, jr in tw if jr) - 1, 0)
    else:
        v_l = fast_J(tw, l, mass)[1]
        v_r = fast_J(tw, r, mass)[1]
        vs = range(min(v_l, v_r) - 2, max(v_l, v_r) + 3)
    out = set()
    for v in vs:
        c0, c1 = _C_aff(tw, v, raw)
        if c1 != 0:
            x = (mass - c0) / c1
            if l < x < r:
                out.add(x)
    return out


def profile_fast(case: Case, check_every: int = 0):
    """Same quantities as profile(), via the closed-form evaluator.  If check_every>0,
    every check_every-th interval is also integrated by the slot-sorting greedy and
    the two exact rationals are compared."""
    pts = partition(case)
    mass = case.m
    exact_total = Fr(0)
    mid_total = Fr(0)
    n_sub = 0
    nchecked = 0
    for idx, (l, r) in enumerate(zip(pts, pts[1:])):
        xm = (l + r) / 2
        st = structure(case, xm) if check_every and idx % check_every == 0 else _structure_types_only(case, xm)
        tw = _types_w(st)
        norm_m = aff_eval(st["norm"], xm)
        Bm = norm_m + max(fast_J(tw, xm, mass)[0], fast_R(tw, xm, mass)[0])
        mid_total += (r - l) * Bm
        bps = sorted({l, r} | fast_breakpoints(tw, mass, l, r, False) | fast_breakpoints(tw, mass, l, r, True))
        piece = Fr(0)
        for x0, x1 in zip(bps, bps[1:]):
            xc = (x0 + x1) / 2
            J0, J1, Jc = (fast_J(tw, z, mass)[0] for z in (x0, x1, xc))
            R0, R1, Rc = (fast_R(tw, z, mass)[0] for z in (x0, x1, xc))
            if 2 * Jc != J0 + J1 or 2 * Rc != R0 + R1:
                raise RuntimeError(f"non-affine sub-piece [{x0},{x1}] in case {case.name}")
            piece += int_max_affine(x0, x1, J0, J1, R0, R1)
            n_sub += 1
        piece += (r - l) * norm_m
        if piece < (r - l) * Bm:
            raise RuntimeError(f"midpoint value exceeds exact integral on [{l},{r}]")
        if check_every and idx % check_every == 0:
            # independent slow evaluation on this interval
            Bm_slow = B_val(st, xm, mass)
            bps2 = sorted({l, r} | lp_breakpoints(st["jet"], mass, l, r) | lp_breakpoints(st["raw"], mass, l, r))
            piece2 = Fr(0)
            for x0, x1 in zip(bps2, bps2[1:]):
                piece2 += int_max_affine(x0, x1, J_val(st, x0, mass), J_val(st, x1, mass),
                                         R_val(st, x0, mass), R_val(st, x1, mass))
            piece2 += (r - l) * norm_m
            if piece2 != piece or Bm_slow != Bm:
                raise RuntimeError(f"evaluators disagree on [{l},{r}]")
            nchecked += 1
        exact_total += piece
    cut = 2 * mass * case.delta
    return dict(intervals=len(pts) - 1, subpieces=n_sub, exact=exact_total,
                exact_minus_cut=exact_total - cut, midpoint=mid_total,
                midpoint_minus_cut=mid_total - cut, cut=cut, crosschecked_intervals=nchecked,
                jet_dominant_measure=Fr(-1), largest_convexity_gap=None)


def _structure_types_only(case: Case, xm: Fr):
    """structure() without building the (long) slot lists."""
    m, al, ka = case.m, case.alpha, case.kappa
    qa, qk, qm = floor(al / xm), floor(ka / xm), floor(m / xm)
    ra = (al, Fr(-qa))
    rk = (ka, Fr(-qk))
    marks = [(Fr(0), Fr(0)), ra, rk, (Fr(0), Fr(1))]
    marks.sort(key=lambda f: aff_eval(f, xm))
    types = []
    for lo, hi in zip(marks, marks[1:]):
        cap = (hi[0] - lo[0], hi[1] - lo[1])
        if cap == (0, 0):
            continue
        lo_v, hi_v = aff_eval(lo, xm), aff_eval(hi, xm)
        if hi_v <= lo_v:
            raise RuntimeError("degenerate piece at a midpoint")
        u = (lo_v + hi_v) / 2
        a = qa + (1 if u < aff_eval(ra, xm) else 0)
        c = qk + (1 if u < aff_eval(rk, xm) else 0)
        types.append((a, c, cap))
    norm = (m * (qk - 3 * qa) - 2 * m * qm, -Fr(2) * Fr(qm * (qm - 1), 2) + 2 * qm * qm)
    return dict(types=types, norm=norm)


def lp_breakpoints(slots, mass, l, r):
    out = set()
    s0, s1 = Fr(0), Fr(0)
    for _, cap in slots:
        s0 += cap[0]
        s1 += cap[1]
        if s1 != 0:
            x = (mass - s0) / s1
            if l < x < r:
                out.add(x)
    return out


def int_max_affine(x0, x1, f0, f1, g0, g1):
    """Exact integral over [x0,x1] of max(f,g) for affine f,g given endpoint values."""
    d0, d1 = f0 - g0, f1 - g1
    if (d0 >= 0 and d1 >= 0) or (d0 <= 0 and d1 <= 0):
        if d0 >= 0 and d1 >= 0:
            return (x1 - x0) * (f0 + f1) / 2
        return (x1 - x0) * (g0 + g1) / 2
    xs = x0 + (x1 - x0) * d0 / (d0 - d1)
    hs = f0 + (f1 - f0) * (xs - x0) / (x1 - x0)  # common value at the crossing
    left = (xs - x0) * ((f0 if d0 > 0 else g0) + hs) / 2
    right = (x1 - xs) * (hs + (f1 if d1 > 0 else g1)) / 2
    return left + right


def profile(case: Case, verbose: bool = False):
    pts = partition(case)
    mass = case.m
    exact_total = Fr(0)
    mid_total = Fr(0)
    n_sub = 0
    worst_gap = None
    jet_used_more = Fr(0)  # measure of x where J > R (diagnostic)
    for l, r in zip(pts, pts[1:]):
        xm = (l + r) / 2
        st = structure(case, xm)
        # midpoint value (lower sum of the original programs)
        Bm = B_val(st, xm, mass)
        mid_total += (r - l) * Bm
        # exact integral
        bps = sorted({l, r} | lp_breakpoints(st["jet"], mass, l, r) | lp_breakpoints(st["raw"], mass, l, r))
        piece = Fr(0)
        for x0, x1 in zip(bps, bps[1:]):
            xc = (x0 + x1) / 2
            J0, J1, Jc = J_val(st, x0, mass), J_val(st, x1, mass), J_val(st, xc, mass)
            R0, R1, Rc = R_val(st, x0, mass), R_val(st, x1, mass), R_val(st, xc, mass)
            if 2 * Jc != J0 + J1 or 2 * Rc != R0 + R1:
                raise RuntimeError(f"non-affine sub-piece [{x0},{x1}] in case {case.name}")
            piece += int_max_affine(x0, x1, J0, J1, R0, R1)
            if Jc > Rc:
                jet_used_more += x1 - x0
            n_sub += 1
        piece += (r - l) * aff_eval(st["norm"], xm)  # affine part integrates exactly
        exact_total += piece
        gap = piece - (r - l) * Bm
        if gap < 0:
            raise RuntimeError(f"midpoint value exceeds exact integral on [{l},{r}]")
        if worst_gap is None or gap > worst_gap[0]:
            worst_gap = (gap, l, r)
    cut = 2 * mass * case.delta
    return dict(
        intervals=len(pts) - 1,
        subpieces=n_sub,
        exact=exact_total,
        exact_minus_cut=exact_total - cut,
        midpoint=mid_total,
        midpoint_minus_cut=mid_total - cut,
        cut=cut,
        jet_dominant_measure=jet_used_more,
        largest_convexity_gap=worst_gap,
    )


def B_function(case: Case):
    """Return a callable x -> B(x) (exact rational), for cross-checks."""
    pts = partition(case)

    def B(x: Fr) -> Fr:
        """B evaluated with the floors at x itself (correct also at partition points)."""
        x = Fr(x)
        st = structure(case, x, at_point=True)
        return B_val(st, x, case.m)

    return B


def run(case: Case, chk: Checks) -> dict:
    t0 = time.time()
    every = 1 if case.name == "2/11" else 25
    res = profile_fast(case, check_every=every)
    dt = time.time() - t0
    print(f"# case {case.name} ({case.unit}-units): m={case.m} alpha={case.alpha} kappa={case.kappa} "
          f"delta={case.delta}  [{dt:.1f}s]")
    print(f"  intervals={res['intervals']} affine sub-pieces={res['subpieces']}; "
          f"{res['crosschecked_intervals']} intervals re-integrated by the slot-sorting greedy (identical)")
    print(f"  exact  int B - 2 m delta = {frac_str(res['exact_minus_cut'], 16)}")
    print(f"  midpoint sum - 2 m delta = {frac_str(res['midpoint_minus_cut'], 16)}"
          f"   (original program printed {case.claims['profile_minus_cut_reported']})")
    rep = Fr(case.claims["profile_minus_cut_reported"])
    # the reported decimal is the midpoint sum printed as a float (~16 digits)
    chk.check(f"{case.name}: midpoint sum reproduces the reported value to 1e-12",
              abs(res["midpoint_minus_cut"] - rep) < Fr(1, 10**12),
              f"|diff| = {float(abs(res['midpoint_minus_cut'] - rep)):.3e}")
    chk.check(f"{case.name}: midpoint sum <= exact integral (convexity lower bound)",
              res["midpoint"] <= res["exact"])
    chk.check(f"{case.name}: two separately written evaluators agree on {res['crosschecked_intervals']} intervals",
              res["crosschecked_intervals"] > 0)
    if "profile_minus_cut_lower" in case.claims:
        lb = case.claims["profile_minus_cut_lower"]
        chk.check(f"{case.name}: claimed inequality int B - cut > {lb}",
                  res["midpoint_minus_cut"] > lb and res["exact_minus_cut"] > lb,
                  f"exact {frac_str(res['exact_minus_cut'], 12)}")
    return res


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    names = list(CASES) if which == "all" else [which]
    chk = Checks("profile certificate")
    payload = {}
    for nm in names:
        res = run(CASES[nm], chk)
        payload[nm] = {
            "exact_int_B": str(res["exact"]),
            "exact_minus_cut": str(res["exact_minus_cut"]),
            "exact_minus_cut_decimal": frac_str(res["exact_minus_cut"], 20),
            "midpoint_minus_cut": str(res["midpoint_minus_cut"]),
            "midpoint_minus_cut_decimal": frac_str(res["midpoint_minus_cut"], 20),
            "cut": str(res["cut"]),
            "intervals": res["intervals"],
            "subpieces": res["subpieces"],
            "crosschecked_intervals": res["crosschecked_intervals"],
        }
    tag = "" if which == "all" else "-" + CASES[which].slug
    chk.finish(OUT / f"profile-integrals{tag}.json", payload)


if __name__ == "__main__":
    main()
