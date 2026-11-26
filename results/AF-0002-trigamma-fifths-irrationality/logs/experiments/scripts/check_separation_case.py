"""Exact separation identity for h = 64 and given k and deletions (manuscript, Remark 2.10).

Runs single cases of check_separation_identity.py at h = 64 (for example the last case,
k = 4, I = {63}). Deletions are given as colon-separated indices, cases separated by commas.

Usage: python check_separation_case.py 4 63          (k = 4, I = {63})
Exit status 1 if the identity or the equality of odd-prime valuations fails.
"""
import sys, time
sys.set_int_max_str_digits(0)
from flint import fmpq
from define_exact_arithmetic import gauss_valuation, primes_upto
from define_lowner_family import det_pencil, pencil
h=64; m=4; N=h+2*m
failures=0
for k in [int(a) for a in sys.argv[1].split(',')]:
    for removed in [tuple(int(x) for x in r.split(':') if x) for r in sys.argv[2].split(',')]:
        t0=time.time()
        A0s,A1s,cs=pencil(k,h,'separated',removed); A0a,A1a,ca=pencil(k,h,'alternating',removed)
        Ps=det_pencil(A0s,A1s,cs); Pa=det_pencil(A0a,A1a,ca)
        ok = (Ps*fmpq(2**(m*(m-1))) == Pa)
        odd = all(gauss_valuation(Ps,p)==gauss_valuation(Pa,p) for p in primes_upto(5*N+10) if p>2)
        print(f"h={h} k={k} I={removed}: P_alt == 2^{m*(m-1)} P_sep exactly: {ok}; odd-prime valuations equal: {odd}; v2 sep {gauss_valuation(Ps,2)} alt {gauss_valuation(Pa,2)} [{time.time()-t0:.0f}s]", flush=True)
        failures += (not ok) or (not odd)
sys.exit(1 if failures else 0)
