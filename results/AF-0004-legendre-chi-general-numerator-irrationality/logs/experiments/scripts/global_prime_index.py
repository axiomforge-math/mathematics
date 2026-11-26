"""Usage: global_prime_index.py A Q SIGMA T C P

Global check of the prime-index reduction (Section 7): for h = T p, K = C p and r = 0 the
theorem predicts v_p(Delta(0)) = -p T (C + 2 - T) + T exactly, whenever p avoids the
exceptional primes and the three local determinants are p-adic units.  Exit status 1 if the
exact valuation differs."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pencil import Pencil, vp
a, q, sigma, t, c, p = (int(x) for x in sys.argv[1:7])
assert (2 * a * q * (q * q - sigma * a * a)) % p != 0 and p > 2 * c + 1
t0 = time.time()
A0, _ = Pencil(a, q, sigma, t, c).matrices(p)
d = A0.det()
pred = -p * t * (c + 2 - t) + t
ok = d != 0 and vp(d, p) == pred
print(f"a={a} q={q} sigma={sigma:+d} (t,c)=({t},{c}) p={p} h={t*p}: Delta(0) != 0: {d != 0}; "
      f"v_p = {vp(d, p) if d != 0 else None}; predicted {pred}; {'OK' if ok else 'MISMATCH'} [{time.time()-t0:.0f}s]", flush=True)
sys.exit(0 if ok else 1)
