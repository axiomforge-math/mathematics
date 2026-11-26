"""Rational roots of the separated Löwner pencil P_sep(X) (Remark 3.6; numerical evidence only).

If P_sep has no rational root, then P_sep(X0) != 0 for every rational X0 without any
deletion — stronger than the 'one deletion suffices' statement used by the proof.
Exact: FLINT factorisation over Q.

Usage: python find_rational_roots.py HMAX"""
import sys
import time

from define_lowner_family import det_pencil, pencil

hmax = int(sys.argv[1])
for h in range(16, hmax + 1, 16):
    for k in (1, 2, 3, 4):
        t0 = time.time()
        A0, A1, c = pencil(k, h, "separated")
        P = det_pencil(A0, A1, c)
        _content, factors = P.factor()
        roots = [-(f[0] / f[1]) for f, e in factors if f.degree() == 1]
        print(f"h={h} k={k} deg={P.degree()} rational roots: {roots if roots else 'none'} [{time.time() - t0:.1f}s]",
              flush=True)
