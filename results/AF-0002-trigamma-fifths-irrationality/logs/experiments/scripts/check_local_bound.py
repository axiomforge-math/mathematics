"""Finite test of the two-layer local bound (manuscript, Appendix A.4(a)).

For h in the given list and k = 1..4, computes P_alt(1/7) exactly (no deletion) and compares
e_p(P_alt(1/7)) with the prediction 2*R0 + q of Proposition 4.8 at every prime p not in {5, 7}
with sqrt(5N) < p <= 5N.

Usage: python check_local_bound.py H1,H2,...      (for example 32,48,64,96)
Exit status 1 if some prime violates the bound.
"""
"""Compare the actual p-adic denominator exponent of P_alt(X) at X=1/7 with the
two-layer local bound 2R0+q (computed from rational block data) at finite h."""
import sys, time, math
sys.set_int_max_str_digits(0)
from fractions import Fraction as F
from collections import defaultdict
from flint import fmpq, fmpq_mat
from integrate_polar_profile import polar_data
from define_lowner_family import increments, node_sets

def vp(x, p):
    if x == 0: return None
    n, d = int(x.p), int(x.q); v = 0
    while n % p == 0: n//=p; v+=1
    while d % p == 0: d//=p; v-=1
    return v

def det_at(k, h, X):
    m=h//16; N=h+2*m; f,d=increments(k,N); R,Q=node_sets(h,'alternating'); n=len(R)
    A=fmpq_mat(n,n)
    for a,i in enumerate(R):
        for b,j in enumerate(Q):
            A[a,b]= X+d[i] if i==j else (f[j]-f[i])/(j-i)
    return A.det()

def local_bound(k,h,p):
    m=h//16; N=h+2*m; s=F(k,5)
    r=(k*pow(p,-1,5))%5; kap=F(r,5); j0=(r*p-k)//5
    R0=0; zl=0; zr=0; rows=defaultdict(int); cols=defaultdict(int)
    for i in range(p):
        total=len(range(i,N,p)); common=len(range(i,h,p))
        if total==0: continue
        arc=(int(i>j0), int(i>=(p+1)//2))
        parity=(i+common*p-h)%2
        rank,a,ll,b,lr=polar_data(kap,common,total,arc,parity)
        R0+=rank; zl+=a; zr+=b
        for L in ll: rows[L]+=1
        for L in lr: cols[L]+=1
    na=sum(rows.values()); nb=sum(cols.values())
    q=min([na,nb]+[na+nb-rows[L]-cols[L] for L in rows.keys()|cols.keys()])
    return 2*R0+q

X=fmpq(1,7)
violations = 0
for h in [int(a) for a in sys.argv[1].split(',')]:
    for k in (1,2,3,4):
        t0=time.time(); P=det_at(k,h,X); N=h+2*(h//16)
        bad=[]; tested=0; tot_e=0.0; tot_b=0.0; eq=0
        for p in range(11,5*N+1):
            if any(p%q==0 for q in range(2,int(p**.5)+1)) or p in (5,7) or p*p<=5*N: continue
            e=max(0,-vp(P,p)); bnd=local_bound(k,h,p); tested+=1
            if e>bnd: bad.append((p,e,bnd)); violations += 1
            tot_e+=e*math.log(p); tot_b+=bnd*math.log(p); eq+=(e==bnd)
        print(f"h={h} k={k}: primes tested {tested}, violations {bad}, equality at {eq}, sum e_p log p /h^2 = {tot_e/h**2:.4f}, sum bound log p /h^2 = {tot_b/h**2:.4f} [{time.time()-t0:.0f}s]", flush=True)
print(f'== violations: {violations}')
sys.exit(1 if violations else 0)
