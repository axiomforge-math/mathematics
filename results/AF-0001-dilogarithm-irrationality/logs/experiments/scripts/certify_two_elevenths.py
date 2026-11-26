"""Exact rational certificates for the 6n-pole, 4n-dimensional Li_2(2/11) proof.
Python 3 standard library only. No floating point is used in any assertion.
The proof accompanying this file explains why these finite checks suffice.
"""

# This program is one of the original certificate programs of the candidate proof. It is
# reproduced here unchanged except for its file name, its imports of the companion
# programs, and this guard. It checks its inequalities with assert statements, so it
# refuses to run when assertions are disabled (python -O); a failed check exits with
# status 1.
import sys as _sys
if not __debug__:
    _sys.exit("assertions are disabled (python -O): this certificate program refuses to run")
from fractions import Fraction as F
from functools import lru_cache
from itertools import permutations
from math import factorial

# ---- 1. Arithmetic certificate --------------------------------------------
def ordinary_prime_bound(cut=F(1,40)):
    A,K,H=1,6,4
    points={cut,F(K)}
    # Floor breakpoints and the remainders' possible crossings.
    for a in [A,K,H,K-A]:
        points|={F(a,j) for j in range(1,int(a/cut)+1) if cut<F(a,j)<K}
    points=sorted(points)
    total=F(0)
    for l,r in zip(points,points[1:]):
        x=(l+r)/2
        qa=A//x; qc=K//x; qh=H//x
        ra=A-qa*x; rc=K-qc*x; rh=H-qh*x
        cuts=sorted(set([0,ra,rc,x]))
        slots=[]; raw=[]
        for lo,hi in zip(cuts,cuts[1:]):
            u=(lo+hi)/2
            a=qa+(u<ra); c=qc+(u<rc); f=hi-lo
            w=3*a-c-1
            slots.extend((w+2*j,f) for j in range(qh+3))
            raw.extend((w+2*j+2*(a==0 and j==c-a-1),f) for j in range(c-a))
        def pick(slots,allowzero=False):
            left=F(H); s=F(0)
            for w,f in sorted(slots):
                if allowzero and w>=0: break
                d=min(left,f); s+=d*w; left-=d
                if not left: break
            assert allowzero or not left
            return s
        norm=H*(qc-3*qa)-2*(x*qh*(qh-1)/2+qh*rh)
        val=norm+max(pick(slots),pick(raw,True))
        # The two slot costs are convex in the affine capacities on this
        # interval. Thus midpoint quadrature is a LOWER bound on the integral.
        total+=(r-l)*val
    return total-H*2*cut

# ---- 2. Rigorous logarithm enclosures and analytic certificate -------------
D=10**15

def core(q):
    assert 1<=q<=2
    r=(q-1)/(q+1); z=r; s=F(0)
    for k in range(20):
        s+=2*z/(2*k+1); z*=r*r
    return s,s+2*z/(41*(1-r*r))
L2=core(F(2))
@lru_cache(None)
def logI(q):
    q=F(q); assert q>0; k=0
    while q<1: q*=2; k-=1
    while q>2: q/=2; k+=1
    a,b=core(q)
    a+=k*(L2[0] if k>=0 else L2[1]); b+=k*(L2[1] if k>=0 else L2[0])
    return F((a*D)//1,D), F(-((-b*D)//1),D)

def add(*v): return sum(x[0] for x in v),sum(x[1] for x in v)
def mul(c,v): return (c*v[0],c*v[1]) if c>=0 else (c*v[1],c*v[0])
def ex(c): return F(c),F(c)
def xlog(x): return mul(x,logI(abs(x))) if x else ex(0)
def f(x): return add(xlog(x),ex(-x))
def g(x): return add(mul(x/2,xlog(x)),ex(-F(3,4)*x*x))

M=[1000,557,402,325,272,233,203,178,157,139,122,107,92,78,63,48,24]
assert sum(M)==4000 and min(M)>=0
rho=[F(m,500) for m in M]
A=[F(i,2) for i in range(len(M))]; B=[a+F(1,2) for a in A]
t=logI(F(11,2)); theta=-F(431,50)
def Lpair(y,a,b): return add(f(y-a),mul(-1,f(y-b)))
def pot(y): return add(*(mul(d,Lpair(y,a,b)) for d,a,b in zip(rho,A,B)))
def V(y): return add(mul(3,xlog(y+1)),mul(-2,xlog(y)),mul(-1,xlog(y+6)),ex(3),mul(-y,t))
def W(y): return add(V(y),mul(2,pot(y)))

def analytic_bound():
    # Tail: W(y) <= V(y)+8 log(y), decreasing with slope < -1/2 for y>=12.
    assert add(V(F(12)),mul(8,logI(F(12))))[1]<theta
    assert t[0]>F(17,12)
    # Energy of sigma, the signed logarithmic convention E=double integral log.
    E=add(*(mul(di*dj,add(g(b-c),g(a-d),mul(-1,g(a-c)),mul(-1,g(b-d))))
            for di,a,b in zip(rho,A,B) for dj,c,d in zip(rho,A,B)))
    # Upper bound on total variation of W, hence also of (W-theta)_+.
    T=add(mul(3,add(xlog(F(13)),mul(-1,xlog(F(12))))),
          add(xlog(F(18)),mul(-1,xlog(F(12))),mul(-1,xlog(F(6)))),mul(12,t),
          *(mul(2*r,add(Lpair(F(0),a,b),Lpair(F(12),a,b),mul(-2,Lpair((a+b)/2,a,b))))
            for r,a,b in zip(rho,A,B)))
    assert T[1]<101
    step=F(1,200); N=2400; s=F(0)
    for j in range(N):
        y=step*(F(j)+F(1,2)); s+=max(F(0),W(y)[1]-theta)*step
    # Midpoint error for a BV function <= step/2 times total variation.
    pen=s+step*T[1]/2
    C=add(mul(24,logI(F(6))),mul(-16,logI(F(4))),ex(12))
    upper=add(C,mul(-1,E),ex(4*theta),ex(2*pen))[1]
    assert upper < -F(49,10)
    return upper,E,T,pen

# ---- 3. Exact local 4x4 nonvanishing determinants --------------------------
lam=F(2,11)
def pmul(a,b):
    c=[F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): c[i+j]+=x*y
    return c

def pdiv(a,b):
    a=list(a);q=[F(0)]*max(1,len(a)-len(b)+1)
    while len(a)>=len(b):
        k=len(a)-len(b); z=a[-1]/b[-1];q[k]=z
        for i,x in enumerate(b): a[k+i]-=z*x
        assert a[-1]==0
        a.pop()
    return q,a

def peval(a,x):
    v=F(0)
    for z in reversed(a): v=v*x+z
    return v

@lru_cache(None)
def stirling(k,r):
    if k==0: return int(r==0)
    if r==0 or r>k: return 0
    return r*stirling(k-1,r)+stirling(k-1,r-1)
@lru_cache(None)
def mom(k):
    return sum(stirling(k,r)*factorial(r)*(lam/(1-lam) if r==0 else lam**r/(1-lam)**(r+1)) for r in range(k+1))

def loc_mom(j,zero):
    if zero:
        num=[F(0)]*(j+1)+[F(1),F(2),F(1)]
        poles=list(range(2,7))
    else:
        num=[F(0)]*(j+2)+[F(1)]
        poles=list(range(1,6))
    den=[F(1)]
    for l in poles: den=pmul(den,[F(l),F(1)])
    q,rem=pdiv(num,den)
    v=sum(k*q[k]*mom(k-1) for k in range(1,len(q)))
    for l in poles:
        d=F(1)
        for j2 in poles:
            if j2!=l:d*=j2-l
        residue=peval(num,-l)/d
        tau=sum(lam**k/F(k*k) for k in range(1,l+1))
        v+=residue*lam**(-l)*tau
    return v

def local_det(zero):
    v=[loc_mom(i,zero) for i in range(7)]; s=F(0)
    for p in permutations(range(4)):
        sign=(-1)**sum(p[i]>p[j] for i in range(4) for j in range(i+1,4))
        z=F(sign)
        for i,j in enumerate(p): z*=v[i+j]
        s+=z
    return s

if __name__=='__main__':
    a=ordinary_prime_bound()
    assert a>F(9,2)
    c=add(ex(F(9,2)),mul(F(20,3),logI(F(11))),mul(-16,logI(F(2))),mul(-F(25,4),logI(F(9))))
    assert c[0]>-F(2169,500)
    d0,d1=local_det(False),local_det(True)
    assert d0==F(17828022563089333969,1224440064)
    assert d1==F(12598972834814973210048467,2295825120)
    Bup,E,T,pen=analytic_bound()
    assert Bup<c[0]
    print('Ordinary-prime rate lower bound:',float(a))
    print('Total arithmetic rate lower bound:',float(c[0]))
    print('Local determinants:',d0,d1)
    print('Comparison measure energy:',float(E[0]))
    print('Total variation upper bound:',float(T[1]))
    print('Penalty integral upper bound:',float(pen))
    print('Analytic growth upper bound:',float(Bup))
    print('Positive certified margin:',float(c[0]-Bup))
    print('All exact rational assertions passed.')
