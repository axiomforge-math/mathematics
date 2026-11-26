"""Irreducibility over Q of the exact polynomials Q_n(X) (Appendix C, item (b)).

An irreducible Q_n of degree >= 2 has no rational root, so Q_n(r) != 0 for every rational r
at that n. This is numerical evidence consistent with Theorem 1.6; it is not used in the
proof. Exact factorisation with FLINT. Exit status 1 if a computed Q_n is reducible or has
degree different from h.

Usage: python check_irreducibility.py CASE [CASE ...]
"""

import sys

from define_hankel_family import CASES, load_polynomials

failures = []
for cname in sys.argv[1:]:
    verdicts = []
    for n, Q in load_polynomials(cname):
        h = CASES[cname].H * n
        _c, factors = Q.factor()
        degs = sorted(f.degree() for f, _e in factors)
        ok = len(degs) == 1 and factors[0][1] == 1 and Q.degree() == h
        verdicts.append(f"{n}:{'irreducible' if ok else degs}")
        if not ok:
            failures.append((cname, n, degs, Q.degree(), h))
    print(f"{cname}: " + " ".join(verdicts), flush=True)
print(f"== reducible or wrong degree: {failures if failures else 'none'}")
sys.exit(1 if failures else 0)
