"""Usage: check_prime_index_valuation.py Q SIGMA P

Global check of the prime-index reduction: for h = 6p, K = 7p and X0 = 0 the theory
predicts v_p(Delta(0)) = -18p + 6 exactly whenever p avoids the exceptional primes and the
three local determinants are p-units (manuscript, Appendix B). Uses the exact implementation
define_half_integer_pencils.py. Exit status 1 unless Delta(0) != 0 and v_p = -18p + 6."""
import sys, time
sys.set_int_max_str_digits(0)
import os
from flint import fmpq_mat
from define_half_integer_pencils import Pencil, matrices
q, sigma, p = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
t0 = time.time()
A0, A1 = matrices(Pencil(q, sigma, 'general'), p)
print('matrices built', time.time()-t0, flush=True)
d = A0.det()
num, den = int(d.p), int(d.q)
def v(a, p):
    k = 0
    while a % p == 0:
        a //= p; k += 1
    return k
print(f"q={q} sigma={sigma} p={p} h={6*p}: Delta(0) != 0: {d != 0}; v_p = {v(num,p)-v(den,p)}; predicted {-18*p+6}; time {time.time()-t0:.1f}s", flush=True)
sys.exit(0 if d != 0 and v(num, p) - v(den, p) == -18 * p + 6 else 1)
