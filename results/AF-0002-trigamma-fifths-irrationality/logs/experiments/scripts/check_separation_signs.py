"""Exact tests of the separation identity beyond the 48 cases of check_separation_identity.py.

Manuscript, Remark 2.10. Exact rational arithmetic (python-flint); pseudo-random choices use a
fixed seed, so the run is deterministic.

  Test A  (Proposition 2.6 for a generic function, Lemma 2.4): F(z) = 1/(z+1/3) - 2/(z+7/4)
          + z^5 + 3z^2. For 40 random multisets of 2 to 9 positive rationals (a random subset
          doubled, the single nodes split evenly) and 6 random partitions of each into rows R
          and columns Q, in random order, the ratio det L(R, Q) / (Delta(R) Delta(Q)) depends
          only on the multiset.
  Test B  (the same for the trigamma function): increments f_i, d_i of Section 2.1 on the
          integers [0, 22); 12 random multisets for each k = 1..4, 5 partitions each; the
          polynomial P_{R,Q}(X) / (Delta(R) Delta(Q)) depends only on the multiset.
  Test C1 (sign +1): h = 16, 32, 48, k = 1..4, I in {(), (0,), (h-1,)} and two random
          deletions I with 2 <= |I| <= 4: P_sep,I = 2^{-m(m-1)} P_alt,I exactly and
          P_alt,I != 0 (60 cases).
  Test C2 (all border splits): h = 32, 48, k = 1, 4, I = {3}: for every m-subset B_R of the
          border B (rows B_R, columns B_Q = B \\ B_R), P_{C+B_R, C+B_Q} =
          P_alt * Delta(B_R) Delta(B_Q) / (Delta(E) Delta(O)), E and O the alternating border
          rows and columns (2 x (6 + 20) = 52 splits).

Here Delta(S) = prod_{a<b} (s_b - s_a) in the given order, and L(R, Q) is the Loewner matrix:
(F(q) - F(r))/(q - r) for r != q and F'(r) for r = q. Exit status 1 if any test fails.

Usage: python check_separation_signs.py
"""

from __future__ import annotations

import itertools
import random
import sys
import time

from flint import fmpq, fmpq_mat

from define_exact_arithmetic import interpolate
from define_lowner_family import increments

sys.set_int_max_str_digits(0)
FAILURES: list[str] = []


def check(ok: bool, what: str) -> None:
    if not ok:
        FAILURES.append(what)
        print(f"[FAIL] {what}", flush=True)


def delta(nodes) -> fmpq:
    out = fmpq(1)
    for a in range(len(nodes)):
        for b in range(a + 1, len(nodes)):
            out *= fmpq(nodes[b]) - fmpq(nodes[a])
    return out


def loewner_det(F, dF, R, Q) -> fmpq:
    n = len(R)
    M = fmpq_mat(n, n)
    for a, r in enumerate(R):
        for b, q in enumerate(Q):
            M[a, b] = dF(r) if r == q else (F(q) - F(r)) / (q - r)
    return M.det()


def random_partition(rng, multiset):
    """Doubled nodes go to both sides; single nodes are split evenly; random orders."""
    doubled = [x for x in set(multiset) if multiset.count(x) == 2]
    singles = [x for x in multiset if multiset.count(x) == 1]
    rng.shuffle(singles)
    half = len(singles) // 2
    R = doubled + singles[:half]
    Q = doubled + singles[half:]
    rng.shuffle(R)
    rng.shuffle(Q)
    return R, Q


def random_multiset(rng, size, draw):
    pts = set()
    while len(pts) < size:
        pts.add(draw())
    pts = sorted(pts)
    doubled = rng.sample(pts, rng.randint(1, len(pts)))
    singles = [x for x in pts if x not in doubled]
    if len(singles) % 2:  # an even number of single nodes keeps |R| = |Q|
        doubled.append(singles.pop())
    return sorted(doubled * 2 + singles)


def test_a(rng) -> None:
    def F(z):
        z = fmpq(z)
        return 1 / (z + fmpq(1, 3)) - 2 / (z + fmpq(7, 4)) + z**5 + 3 * z**2

    def dF(z):
        z = fmpq(z)
        return -1 / (z + fmpq(1, 3)) ** 2 + 2 / (z + fmpq(7, 4)) ** 2 + 5 * z**4 + 6 * z

    cases = nonzero = 0
    for _ in range(40):
        ms = random_multiset(rng, rng.randint(2, 9), lambda: fmpq(rng.randint(1, 60), rng.randint(1, 7)))
        ratios = set()
        for _ in range(6):
            R, Q = random_partition(rng, ms)
            ratios.add(loewner_det(F, dF, R, Q) / (delta(R) * delta(Q)))
            cases += 1
        check(len(ratios) == 1, f"Test A: ratio not invariant for multiset {ms}")
        nonzero += next(iter(ratios)) != 0
    print(f"Test A: {cases} partitions of 40 multisets; ratio invariant in every multiset; "
          f"nonzero for {nonzero} multisets", flush=True)


def pencil_poly(f, d, R, Q):
    """det of the pencil with entries X + d_i (i = j) and (f_j - f_i)/(j - i) otherwise."""
    common = sum(1 for r in R if r in Q)
    n = len(R)
    xs = [fmpq(t) for t in range(common + 1)]
    vals = []
    for x in xs:
        M = fmpq_mat(n, n)
        for a, r in enumerate(R):
            for b, q in enumerate(Q):
                M[a, b] = x + d[r] if r == q else (f[q] - f[r]) / (q - r)
        vals.append(M.det())
    return interpolate(xs, vals)


def test_b(rng) -> None:
    pencils = raw_variable = 0
    for k in (1, 2, 3, 4):
        f, d = increments(k, 22)
        for _ in range(12):
            ms = random_multiset(rng, rng.randint(3, 8), lambda: rng.randrange(0, 22))
            normalised, raw = set(), set()
            for _ in range(5):
                R, Q = random_partition(rng, ms)
                P = pencil_poly(f, d, R, Q)
                raw.add(str(P))
                normalised.add(str(P / (delta(R) * delta(Q))))
                pencils += 1
            check(len(normalised) == 1, f"Test B: k={k} normalised pencil not invariant for {ms}")
            raw_variable += len(raw) > 1
    print(f"Test B: {pencils} pencils (k = 1..4, 12 multisets x 5 partitions); normalised pencil invariant "
          f"in every multiset; raw pencil not invariant in {raw_variable} of 48 multisets (control)", flush=True)


def layout(h, kind, removed=()):
    m = h // 16
    C = list(range(h))
    if kind == "alternating":
        R, Q = C + [h + 2 * r for r in range(m)], C + [h + 2 * r + 1 for r in range(m)]
    else:
        R, Q = list(range(h + m)), C + list(range(h + m, h + 2 * m))
    return [i for i in R if i not in removed], [j for j in Q if j not in removed]


def test_c1(rng) -> None:
    count = 0
    for h in (16, 32, 48):
        m = h // 16
        deletions = [(), (0,), (h - 1,)] + [tuple(sorted(rng.sample(range(h), rng.randint(2, 4)))) for _ in range(2)]
        for k in (1, 2, 3, 4):
            f, d = increments(k, h + 2 * m)
            for removed in deletions:
                Ps = pencil_poly(f, d, *layout(h, "separated", removed))
                Pa = pencil_poly(f, d, *layout(h, "alternating", removed))
                check(Pa != 0 and Ps * 2 ** (m * (m - 1)) == Pa,
                      f"Test C1: h={h} k={k} I={removed}")
                count += 1
    print(f"Test C1: {count} cases (h = 16, 32, 48; k = 1..4; 5 deletions each): "
          f"P_sep,I = 2^(-m(m-1)) P_alt,I exactly, P_alt,I != 0", flush=True)


def test_c2() -> None:
    count = 0
    for h in (32, 48):
        m = h // 16
        C = [i for i in range(h) if i != 3]
        B = list(range(h, h + 2 * m))
        E = [h + 2 * r for r in range(m)]
        O = [h + 2 * r + 1 for r in range(m)]
        for k in (1, 4):
            f, d = increments(k, h + 2 * m)
            Pa = pencil_poly(f, d, C + E, C + O)
            for BR in itertools.combinations(B, m):
                BQ = [b for b in B if b not in BR]
                P = pencil_poly(f, d, C + list(BR), C + BQ)
                check(P == Pa * (delta(BR) * delta(BQ) / (delta(E) * delta(O))),
                      f"Test C2: h={h} k={k} split {BR}")
                count += 1
    print(f"Test C2: {count} border splits (h = 32, 48; k = 1, 4; I = {{3}}): "
          f"P = P_alt Delta(B_R) Delta(B_Q) / (Delta(E) Delta(O)) exactly", flush=True)


def main() -> int:
    rng = random.Random(20261125)
    for test in (lambda: test_a(rng), lambda: test_b(rng), lambda: test_c1(rng), test_c2):
        t0 = time.time()
        test()
        print(f"   [{time.time() - t0:.0f}s]", flush=True)
    print(f"== failures: {len(FAILURES)}")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
