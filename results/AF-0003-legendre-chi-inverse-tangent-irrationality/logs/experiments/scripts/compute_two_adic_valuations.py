"""2-adic Gauss valuation of T(X) for the general construction (q = 83, sigma = +1) against the
finite bound of the prime-2 theorem and its leading term -(140/99) h^2 (manuscript, Table of
Appendix B). Exact (python-flint); the sizes h = 66 and 72 take about half an hour each.
Exit status 1 if v_2^G(T) is below the finite bound for some n.

For the square construction (K = h, A = 0; manuscript, Appendix B, last table) the same
implementation is applied to (h, K, A) = (h, h, 0), in two normalisations, Delta(X) =
det[mu_X(phi u^{i+j})] (un-normalised) and T = S * Delta, against the finite bound of the prime-2
theorem and its limit -(13/11) h^2.

Usage: python compute_two_adic_valuations.py NMIN NMAX              (general construction, h = 6n)
       python compute_two_adic_valuations.py --square Q SIGMA H [H ...]   (square construction)
"""
import sys
import time

from check_finite_bounds import two_adic_bound, vS
from define_exact_arithmetic import gauss_valuation
from define_half_integer_pencils import Pencil, T_poly, det_affine, matrices


def square(q, sigma, sizes):
    P = Pencil(q, sigma, "square")
    print("h, v2(S), v2G(Delta), v2G(T), finite bound for T, -v2G(Delta)/h^2, -v2G(T)/h^2, -bound/h^2")
    failures = 0
    for h in sizes:
        t0 = time.time()
        A0, A1 = matrices(P, h)
        vD = gauss_valuation(det_affine(A0, A1), 2)
        s = vS(h, h, 0, 2)
        b = two_adic_bound(h, h, 0)
        ok = vD + s >= b
        failures += not ok
        print(f"h={h} v2(S)={s} v2G(Delta)={vD} v2G(T)={vD + s} bound={b} "
              f"lossDelta={-vD / h**2:.4f} lossT={-(vD + s) / h**2:.4f} lossBound={-b / h**2:.4f} "
              f"{'ok' if ok else 'FAIL'} [{time.time() - t0:.0f}s]", flush=True)
    print(f"== failures: {failures}")
    sys.exit(1 if failures else 0)


if len(sys.argv) > 1 and sys.argv[1] == "--square":
    square(int(sys.argv[2]), int(sys.argv[3]), [int(a) for a in sys.argv[4:]])

P = Pencil(83, 1, "general")
failures = 0
print("h, v2(T), finite bound, leading term -(140/99)h^2, v2/h^2")
for n in range(int(sys.argv[1]), int(sys.argv[2]) + 1):
    t0 = time.time()
    h, K, A = P.sizes(n)
    T = T_poly(P, n)
    v2 = gauss_valuation(T, 2)
    bound = two_adic_bound(h, K, A)
    failures += v2 < bound
    print(f"h={h} v2={v2} bound={bound} leading={-140 * h * h / 99:.1f} v2/h^2={v2 / h**2:.3f} [{time.time()-t0:.0f}s]",
          flush=True)
print(f"== failures: {failures}")
sys.exit(1 if failures else 0)
