"""Compute the exact polynomials Q_n(X) of the enlarged Hankel family (Appendix C).

Output: DATA_DIR/<case-slug>/Q_NNN.json (see define_hankel_family.py) with exact rational
coefficients as "p/q" strings, so that the analyses never recompute determinants. Existing
files are kept. The output is generated data and is not part of the archive; its SHA-256
digests are recorded in outputs/hankel-polynomials-sha256.txt.

Usage: python compute_hankel_polynomials.py CASE NMIN NMAX
"""

from __future__ import annotations

import json
import sys
import time

sys.set_int_max_str_digits(0)

from define_hankel_family import CASES, DATA_DIR, SLUG, det_poly, family_matrices  # noqa: E402


def main():
    cname, nmin, nmax = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    case = CASES[cname]
    d = DATA_DIR / SLUG[cname]
    d.mkdir(parents=True, exist_ok=True)
    for n in range(nmin, nmax + 1):
        f = d / f"Q_{n:03d}.json"
        if f.exists():
            continue
        t0 = time.time()
        A0, A1 = family_matrices(case, n)
        Q = det_poly(A0, A1)
        coeffs = [str(Q[k]) for k in range(Q.degree() + 1)]
        tmp = f.with_suffix(".tmp")
        tmp.write_text(json.dumps({"case": cname, "n": n, "H": case.H, "C": case.C, "B": case.B,
                                   "coefficients_ascending": coeffs}))
        tmp.replace(f)
        print(f"{cname} n={n} deg={Q.degree()} [{time.time() - t0:.1f}s]", flush=True)


if __name__ == "__main__":
    main()
