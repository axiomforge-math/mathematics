#!/usr/bin/env python
"""Finite-h test of the two-layer polar valuation bound (Lemma 4.5, Proposition 4.8; Appendix A.4(b)).

For each h, k and odd prime p with p^2 > 5N, p != 5, p <= 5N, the exact (finite) version of the
argument predicts, for the alternating pencil P(X) = det Phi(X) (Gauss valuation, i.e. for every
p-integral X):

    -v_p(P) <= 2 R0 + rank_p(W) <= 2 R0 + q,

where for each residue fibre i mod p (nodes i + l p < N) the block A_i (entries W_l on common
digits, (V_l' - V_l)/(l' - l) otherwise) has rank R0_i, W is the first-digit pairing
det(B(y), B(z)) / (i' - i) of left/right null vectors across fibres (0 within a fibre) and q is
the line-count bound of Proposition 4.8.  The blocks are built from the polar digits of Section 4.2
with the actual
eps1 = [i >= p kappa + 1 - s], eps2 = [i >= (p+1)/2].  Primes where some block has F_p-rank
different from its Q-rank ("bad" primes) are reported separately (the argument excludes them).

The TRUE valuation is computed from the exact pencil (compute_separated_pencils.py).  We also
report the asymptotic profile prediction h * bound_kappa(p/h) of verify_arithmetic_constant.py.

Usage: python check_polar_bounds.py [--deletions] H1 [H2 ...]      (multiples of 16)
       --deletions also tests the deleted pencils I = {0} and I = {h-1}.
Exit status 1 if any non-bad prime violates -v_p(P) <= 2 R0 + rank_p(W).
"""

from __future__ import annotations

import math
import sys
import time

from flint import fmpq, fmpq_mat, nmod_mat

from define_exact_arithmetic import gauss_valuation, primes_upto
from compute_separated_pencils import node_sets, pencil_poly
import verify_arithmetic_constant as AP


def qmod(x: fmpq, p: int) -> int:
    num, den = int(x.p), int(x.q)
    assert den % p != 0
    return num * pow(den, -1, p) % p


def polar_values(kap: fmpq, L: int, e1: int, e2: int):
    half = fmpq(1, 2)
    V, W = [], []
    for l in range(L):
        V.append(sum((1 / (kap + a) for a in range(l + e1)), fmpq(0))
                 - sum((1 / (half + a) for a in range(l + e2)), fmpq(0)))
        W.append(-sum((1 / (kap + a) ** 2 for a in range(l + e1)), fmpq(0))
                 + sum((1 / (half + a) ** 2 for a in range(l + e2)), fmpq(0)))
    return V, W


def nullspace_p(rows, ncols, p):
    """Basis (list of lists mod p) of the right nullspace of a matrix given by rows."""
    if ncols == 0:
        return []
    if not rows:
        return [[int(i == j) for i in range(ncols)] for j in range(ncols)]
    M = nmod_mat(len(rows), ncols, [e for r in rows for e in r], p)
    X, nullity = M.nullspace()
    return [[int(X[i, j]) for i in range(ncols)] for j in range(nullity)]


def predict(h: int, k: int, p: int, removed=()):
    m = h // 16
    N = h + 2 * m
    R, Q = node_sets(h, "alternating")
    R = set(i for i in R if i not in removed)
    Q = set(j for j in Q if j not in removed)
    jj = k * pow(p, -1, 5) % 5
    kap = fmpq(jj, 5)
    i1 = (p * jj - k) // 5 + 1
    assert (p * jj - k) % 5 == 0
    i2 = (p + 1) // 2
    R0 = 0
    bad = False
    lefts, rights = [], []   # (fibre, moment vector mod p)
    for i in range(min(p, N)):
        L = (N - 1 - i) // p + 1
        e1, e2 = int(i >= i1), int(i >= i2)
        V, W = polar_values(kap, L, e1, e2)
        rows = [l for l in range(L) if i + l * p in R]
        cols = [l for l in range(L) if i + l * p in Q]
        Aq = [[W[a] if a == b else (V[b] - V[a]) / (b - a) for b in cols] for a in rows]
        Ap = [[qmod(e, p) for e in r] for r in Aq]
        if rows and cols:
            rq = fmpq_mat(len(rows), len(cols), [e for r in Aq for e in r]).rank()
            rp = nmod_mat(len(rows), len(cols), [e for r in Ap for e in r], p).rank()
        else:
            rq = rp = 0
        if rq != rp:
            bad = True
        R0 += rp
        Vp = [qmod(v, p) for v in V]
        for z in nullspace_p(Ap, len(cols), p):
            rights.append((i, (sum(z) % p, sum(zt * Vp[c] for zt, c in zip(z, cols)) % p)))
        At = [[Ap[a][b] for a in range(len(rows))] for b in range(len(cols))]
        for y in nullspace_p(At, len(rows), p):
            lefts.append((i, (sum(y) % p, sum(yt * Vp[r] for yt, r in zip(y, rows)) % p)))
    d = len(lefts)
    assert d == len(rights) == len(R) - R0
    if d:
        ent = []
        for i, By in lefts:
            for i2_, Bz in rights:
                if i == i2_:
                    ent.append(0)
                else:
                    ent.append((By[0] * Bz[1] - By[1] * Bz[0]) * pow((i2_ - i) % p, -1, p) % p)
        rW = nmod_mat(d, d, ent, p).rank()
    else:
        rW = 0

    # line-count bound q (moment lines in P^1(F_p); fibres with 2-dim image may host any line)
    def proj(v):
        x, y = v
        return ("inf",) if x == 0 else ("s", y * pow(x, -1, p) % p)

    def tally(vecs):
        by_fibre = {}
        for i, v in vecs:
            by_fibre.setdefault(i, []).append(v)
        nz, lines, two = 0, {}, 0
        for i, vs in by_fibre.items():
            nzv = [v for v in vs if v != (0, 0)]
            if not nzv:
                continue
            rk = nmod_mat(len(nzv), 2, [c for v in nzv for c in v], p).rank()
            nz += rk
            if rk == 1:
                L_ = proj(nzv[0])
                lines[L_] = lines.get(L_, 0) + 1
            else:
                two += 1
        return nz, lines, two

    a, la, ta = tally(lefts)
    b, lb, tb = tally(rights)
    q = min([a, b] + [a + b - la.get(L_, 0) - lb.get(L_, 0) - ta - tb for L_ in set(la) | set(lb)]
            + [a + b - ta - tb])
    return dict(R0=R0, d=d, rW=rW, q=q, bad=bad, kap=kap, n=len(R))


def main():
    args = sys.argv[1:]
    dels = "--deletions" in args
    hs = [int(t) for t in args if not t.startswith("--")] or [16, 32, 48, 64]
    viol = 0
    for h in hs:
        m = h // 16
        N = h + 2 * m
        for k, I in [(k, ()) for k in (1, 2, 3, 4)] + ([(k, I) for k in (1, 2, 3, 4) for I in ((0,), (h - 1,))] if dels else []):
            t0 = time.time()
            P = pencil_poly(k, h, "alternating", I)
            tot_true = tot_rW = tot_q = tot_prof = tot_2n = 0.0
            small = 0.0
            nbad = 0
            lines = []
            for p in primes_upto(5 * N):
                v = gauss_valuation(P, p)
                e_true = max(0, -int(v))
                if p in (2, 5) or p * p <= 5 * N:
                    small += e_true * math.log(p)
                    continue
                pr = predict(h, k, p, I)
                x = fmpq(p, h)
                if fmpq(1, 20) < x < AP.TOP:
                    prof = float(min(f(x) for f in AP.candidates(pr["kap"], x, "fixed"))) * h
                else:
                    prof = float("nan")
                e_rW = 2 * pr["R0"] + pr["rW"]
                e_q = 2 * pr["R0"] + pr["q"]
                if pr["bad"]:
                    nbad += 1
                elif e_true > e_rW:
                    viol += 1
                    print("VIOLATION h=%d k=%d I=%s p=%d: true %d > predicted %d" % (h, k, I, p, e_true, e_rW), flush=True)
                lg = math.log(p)
                tot_true += e_true * lg
                tot_rW += e_rW * lg
                tot_q += e_q * lg
                tot_2n += 2 * pr["n"] * lg
                if prof == prof:
                    tot_prof += prof * lg
                lines.append((p, e_true, e_rW, e_q, prof, pr["bad"]))
            print("h=%d k=%d I=%s [%.0fs]  primes p^2>5N: sum e*log p / h^2: true %.4f | 2R0+rank(W) %.4f | 2R0+q %.4f |"
                  " profile %.4f | crude 2n %.4f ; small primes (incl 2,5) true %.4f ; bad primes %d"
                  % (h, k, I, time.time() - t0, tot_true / h**2, tot_rW / h**2, tot_q / h**2, tot_prof / h**2,
                     tot_2n / h**2, small / h**2, nbad), flush=True)
            if I == () and (k == 1 or h == hs[-1]):
                print("   p: true / 2R0+rkW / 2R0+q / profile*h  : " +
                      " ".join("%d:%d/%d/%d/%.1f%s" % (p, a, b, c, d, "*" if bd else "") for p, a, b, c, d, bd in lines),
                      flush=True)
    print("violations:", viol)
    if viol:
        sys.exit(1)
    print("PASS: no violation of the finite two-layer bound at non-bad primes")


if __name__ == "__main__":
    main()
