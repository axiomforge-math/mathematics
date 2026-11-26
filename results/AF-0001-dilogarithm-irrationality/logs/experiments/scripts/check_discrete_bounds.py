"""Finite slot bounds at ordinary primes versus the limiting profile and the exact data.

EXPLORATORY (Appendix C, item (c)). For index n and an ordinary prime p with
delta*u <= p <= K, p^2 > K (u = n for 2/11, u = h otherwise):
    discrete(p) = v_p(S^h/F) + max(jet(p), raw(p)),
where jet is the bound of Proposition 4.5 and raw the pole bound in the uncorrected form
of the original argument, computed by a grouped implementation (cross-checked against
check_valuation_bounds.py on small inputs). Part 1 compares with u*B(p/u)
(verify_profile_integrals.B_function), the content of Proposition 5.3 being
discrete(p) = u B(p/u) + O_delta(1), and reports
    max_p |discrete - uB|,   sum_p (discrete - uB) log p / u^2.
Part 2 (stored Q_n, see compute_hankel_polynomials.py): the actual Gauss valuations
v_p(Q_n) at ordinary primes versus
  * the jet bound (Proposition 4.5),
  * the corrected pole bound (Proposition 4.6: zero class with slots w_0 + 1 + 2j),
  * the uncorrected pole bound of the original argument (deficits are reported),
and sums weighted by log p / u^2. Exit status 1 if the jet bound or the corrected pole
bound fails for some (p, n).

Usage: python check_discrete_bounds.py CASE [n1 n2 ...]
"""

from __future__ import annotations

import json
import math
import sys
from collections import Counter
from fractions import Fraction as Fr
from pathlib import Path

sys.set_int_max_str_digits(0)

from define_parameters import CASES, OUT, Case  # noqa: E402
from verify_profile_integrals import B_function  # noqa: E402

from define_hankel_family import DATA_DIR, SLUG  # noqa: E402


def primes_upto(N):
    s = bytearray([1]) * (N + 1)
    s[0:2] = b"\x00\x00"
    for i in range(2, int(N ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(N + 1) if s[i]]


def class_counts(N: int, p: int) -> list[int]:
    """cnt[s] = #{1 <= l <= N : l = s mod p}."""
    q, r = divmod(N, p)
    cnt = [q] * p
    for s in range(1, r + 1):
        cnt[s] += 1
    return cnt


def vp_fact(N: int, p: int) -> int:
    v, q = 0, p
    while q <= N:
        v += N // q
        q *= p
    return v


def v_norm(h, K, A, p):
    return h * (vp_fact(K, p) - 3 * vp_fact(A, p)) - 2 * sum(vp_fact(i, p) for i in range(h))


def jet_bound(h, A, K, p):
    a, c = class_counts(A, p), class_counts(K, p)
    cnt = Counter(3 * a[s] - c[s] - 1 for s in range(p))
    wmin = min(cnt)
    left, total, v = h, 0, wmin
    while left > 0:
        k = sum(cw for w, cw in cnt.items() if w <= v and (v - w) % 2 == 0)
        d = min(k, left)
        total += d * v
        left -= d
        v += 1
    return total


def raw_bound(h, A, K, p):
    a, c = class_counts(A, p), class_counts(K, p)
    types = Counter((a[s], c[s]) for s in range(p))
    slots = Counter()
    for (aa, cc), mult in types.items():
        w = 3 * aa - cc - 1
        for j in range(cc - aa):
            wt = w + 2 * j + (2 if (aa == 0 and j == cc - aa - 1) else 0)
            if wt < 0:
                slots[wt] += mult
    left, total = h, 0
    for wt in sorted(slots):
        d = min(slots[wt], left)
        total += d * wt
        left -= d
        if left == 0:
            break
    return total


def pole_bound(h, A, K, p):
    """Corrected pole bound of Proposition 4.6: Sigma^-_h of the multiset
    w_s + 2j + 2[a_s = 0, j = c_s - a_s - 1]  (1 <= s < p, 0 <= j < c_s - a_s)  and
    w_0 + 1 + 2j  (0 <= j < c_0 - a_0)."""
    a, c = class_counts(A, p), class_counts(K, p)
    slots = Counter()
    w0 = 3 * a[0] - c[0] - 1
    for j in range(c[0] - a[0]):
        if w0 + 1 + 2 * j < 0:
            slots[w0 + 1 + 2 * j] += 1
    types = Counter((a[s], c[s]) for s in range(1, p))
    for (aa, cc), mult in types.items():
        w = 3 * aa - cc - 1
        for j in range(cc - aa):
            wt = w + 2 * j + (2 if (aa == 0 and j == cc - aa - 1) else 0)
            if wt < 0:
                slots[wt] += mult
    left, total = h, 0
    for wt in sorted(slots):
        d = min(slots[wt], left)
        total += d * wt
        left -= d
        if left == 0:
            break
    return total


def selftest():
    import check_valuation_bounds as pc  # the reference (ungrouped) implementation

    for (h, A, K) in [(8, 2, 12), (12, 3, 18), (16, 4, 28), (20, 4, 32), (24, 0, 27)]:
        for p in primes_upto(2 * K):
            if p < 5:
                continue
            assert jet_bound(h, A, K, p) == pc.jet_bound(h, A, K, p), (h, A, K, p)
            assert raw_bound(h, A, K, p) == pc.raw_bound(h, A, K, p), (h, A, K, p)
    print("selftest: grouped jet/raw bounds agree with check_valuation_bounds.py")


def part1(case: Case, n: int, B) -> dict:
    h, K, A = case.H * n, case.C * n, case.B * n
    u = n * case.scale
    excl = {2, case.P, case.G}
    rows = []
    for p in primes_upto(K):
        if p in excl or p * p <= K or Fr(p, u) < case.delta:
            continue
        disc = v_norm(h, K, A, p) + max(jet_bound(h, A, K, p), raw_bound(h, A, K, p))
        prof = u * B(Fr(p, u))
        rows.append((p, disc, prof))
    diffs = [float(d - pr) for _, d, pr in rows]
    s_disc = sum(d * math.log(p) for p, d, _ in rows) / u ** 2
    s_prof = sum(float(pr) * math.log(p) for p, _, pr in rows) / u ** 2
    worst = max(rows, key=lambda r: abs(r[1] - r[2]))
    return dict(n=n, u=u, nprimes=len(rows), max_abs_diff=max(abs(x) for x in diffs),
                worst_p=worst[0], worst_x=float(Fr(worst[0], u)), mean_diff=sum(diffs) / len(diffs),
                sum_disc=s_disc, sum_prof=s_prof)


def load_Q(case: Case):
    d = DATA_DIR / SLUG[case.name]
    for f in sorted(d.glob("Q_*.json")):
        try:
            data = json.loads(f.read_text())
        except Exception:
            continue
        coeffs = []
        for s in data["coefficients_ascending"]:
            if "/" in s:
                x, y = s.split("/")
                coeffs.append(Fr(int(x), int(y)))
            else:
                coeffs.append(Fr(int(s)))
        yield data["n"], coeffs


def vp_frac(x: Fr, p: int) -> int:
    a, b, v = abs(x.numerator), x.denominator, 0
    while a % p == 0:
        a //= p
        v += 1
    while b % p == 0:
        b //= p
        v -= 1
    return v


def part2(case: Case, B):
    out = []
    excl = {2, case.P, case.G}
    for n, coeffs in load_Q(case):
        h, K, A = case.H * n, case.C * n, case.B * n
        u = n * case.scale
        nz = [c for c in coeffs if c != 0]
        tot_act = tot_disc = tot_prof = 0.0
        viol_jet = []
        viol_raw = []
        viol_pole = []
        count = 0
        for p in primes_upto(K):
            if p in excl or p * p <= K:
                continue
            vQ = min(vp_frac(c, p) for c in nz)
            vn = v_norm(h, K, A, p)
            act = vQ + vn
            jb, rb = jet_bound(h, A, K, p), raw_bound(h, A, K, p)
            if vQ < jb:
                viol_jet.append((p, vQ, jb))
            if vQ < rb:
                viol_raw.append((p, rb - vQ))
            pb = pole_bound(h, A, K, p)
            if vQ < pb:
                viol_pole.append((p, vQ, pb))
            disc = vn + max(jb, rb)
            prof = float(u * B(Fr(p, u))) if Fr(p, u) >= case.delta else float("nan")
            lp = math.log(p)
            tot_act += act * lp
            tot_disc += disc * lp
            if prof == prof:
                tot_prof += prof * lp
            count += 1
        out.append(dict(n=n, primes=count, actual=tot_act / u ** 2, discrete_bound=tot_disc / u ** 2,
                        profile=tot_prof / u ** 2, jet_violations=viol_jet, pole_violations=viol_pole,
                        raw_deficits=viol_raw))
    return out


def main():
    name = sys.argv[1]
    case = CASES[name]
    ns = [int(x) for x in sys.argv[2:]] or [50, 100, 200, 400]
    selftest()
    B = B_function(case)
    print(f"# case {name}: part 1 (finite slot bounds vs u*B(p/u)), u = {case.unit}")
    print("   n     u  #p  max|disc-uB|  at x=p/u   mean(disc-uB)  sum disc*logp/u^2  sum uB*logp/u^2")
    res1 = []
    for n in ns:
        r = part1(case, n, B)
        res1.append(r)
        print(f"{n:5d} {r['u']:5d} {r['nprimes']:4d} {r['max_abs_diff']:10.2f}  {r['worst_x']:8.4f}"
              f"  {r['mean_diff']:10.3f}  {r['sum_disc']:14.6f}  {r['sum_prof']:14.6f}")
    print(f"# part 2 (cached Q_n): ordinary primes p^2 > K, all p <= K (no delta cut)")
    print("   n  #p   actual sum v_p log p/u^2   discrete bound   profile (p>=delta u)   "
          "jet violations; corrected pole-bound violations; uncorrected pole-bound deficits (p, raw - v_p(Q))")
    res2 = part2(case, B)
    for r in res2:
        print(f"{r['n']:4d} {r['primes']:4d}  {r['actual']:14.5f}  {r['discrete_bound']:14.5f}  {r['profile']:14.5f}"
              f"   {r['jet_violations'] if r['jet_violations'] else 'none'};"
              f" {r['pole_violations'] if r['pole_violations'] else 'none'};"
              f" {r['raw_deficits'] if r['raw_deficits'] else 'none'}")
    allraw = [d for r in res2 for (_, d) in r["raw_deficits"]]
    print(f"# uncorrected pole-bound deficits: {len(allraw)} (prime, n) pairs, max deficit {max(allraw) if allraw else 0}")
    njet = sum(len(r["jet_violations"]) for r in res2)
    npole = sum(len(r["pole_violations"]) for r in res2)
    print(f"# n checked: {[r['n'] for r in res2]}; jet-bound violations: {njet}; corrected pole-bound violations: {npole}")
    (OUT / f"discrete-bounds-{case.slug}.json").write_text(json.dumps(dict(part1=res1, part2=res2), indent=1, default=str))
    bad = [r for r in res2 if r["jet_violations"] or r["pole_violations"]]
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
