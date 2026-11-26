"""Exact rational certificates for the negative dilogarithm at -2/7.
The comparison measure lives on two rays of direction (21 +/- 20i)/29.
Only Python's standard library is used; no floating point enters assertions.
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
from math import factorial
from define_rational_intervals import add,mul,ex,logI,xlog,pmul,pdiv,peval,det,stirling

A=F(1,5); K=F(8,5); H=F(1); lam=-F(2,7)

def ordinary(cut=F(1,500)):
    points={cut,K}
    for a in [A,K,H,K-A]:
        points.update(a/j for j in range(1,int(a/cut)+1) if cut<a/j<K)
    total=F(0)
    points=sorted(points)
    for l,r in zip(points,points[1:]):
        x=(l+r)/2; qa=A//x; qc=K//x; qh=H//x
        ra=A-qa*x; rc=K-qc*x; rh=H-qh*x
        cuts=sorted({F(0),ra,rc,x});jet=[];raw=[]
        for lo,hi in zip(cuts,cuts[1:]):
            u=(lo+hi)/2; a=qa+int(u<ra); c=qc+int(u<rc); cap=hi-lo
            w=3*a-c-1
            jet.extend((w+2*j,cap) for j in range(qh+3))
            raw.extend((w+2*j+2*(a==0 and j==c-a-1),cap) for j in range(c-a))
        def pick(slots,raw=False):
            left=H;s=F(0)
            for w,cap in sorted(slots):
                if raw and w>=0:break
                d=min(left,cap);s+=w*d;left-=d
                if not left:break
            assert raw or not left
            return s
        norm=qc-3*qa-2*(x*qh*(qh-1)/2+qh*rh)
        total+=(r-l)*(norm+max(pick(jet),pick(raw,True)))
    return total-2*cut

# Rational interval for atan, with argument reduction.
D=10**15
def rounded(v):return F((v[0]*D)//1,D),F(-((-v[1]*D)//1),D)
def atanCore(x):
    assert abs(x)<=F(1,2)
    s=sum(((-1)**j*x**(2*j+1)/ (2*j+1) for j in range(20)),F(0))
    e=abs(x)**41/41
    return s-e,s+e
PI=rounded(add(mul(16,atanCore(F(1,5))),mul(-4,atanCore(F(1,239)))))
@lru_cache(None)
def atanI(x):
    if x<0:return mul(-1,atanI(-x))
    if x>1:return rounded(add(mul(F(1,2),PI),mul(-1,atanI(1/x))))
    if x>F(1,2):return rounded(add(mul(F(1,4),PI),atanCore((x-1)/(x+1))))
    return rounded(atanCore(x))

def argI(a,b):
    assert b>=0
    if a==0:return mul(F(1,2),PI)
    if a>0:return atanI(b/a)
    return add(PI,mul(-1,atanI(b/(-a))))

@lru_cache(None)
def clog(a,b):
    assert a or b
    return mul(F(1,2),logI(a*a+b*b)),argI(a,b)

# Re and Im of F(z)=z(log z-1) and G(z)=z²(log z/2-3/4).
@lru_cache(None)
def cf(a,b):
    if not (a or b):return ex(0),ex(0)
    l,t=clog(a,b);l=add(l,ex(-1))
    return add(mul(a,l),mul(-b,t)),add(mul(b,l),mul(a,t))
@lru_cache(None)
def cg(a,b):
    if not (a or b):return ex(0),ex(0)
    l,t=clog(a,b);l=add(mul(F(1,2),l),ex(-F(3,4)));t=mul(F(1,2),t)
    x=a*a-b*b;y=2*a*b
    return add(mul(x,l),mul(-y,t)),add(mul(y,l),mul(x,t))

# Each cell carries mass M_j/(2*100000) on EACH ray.
M=[13112,8416,7787,6951,6348,5833,5390,4997,4642,4318,4016,3734,3466,3210,2962,2721,2482,2244,2002,1751,1486,1185,869,78]
assert sum(M)==100000 and min(M)>=0
rho=[F(m,8000) for m in M]
a=[F(i,25) for i in range(len(M))];b=[u+F(1,25) for u in a]
c,s=F(21,29),F(20,29); C,S=F(41,841),F(840,841)
t=add(mul(c,logI(F(7,2))),mul(s,PI))

def Fsame(y,a,b):return add(cf(y-a,F(0))[0],mul(-1,cf(y-b,F(0))[0]))
def Fcross(y,a,b):return add(cf(C*y-a,S*y)[0],mul(-1,cf(C*y-b,S*y)[0]))
def U(y):return add(*(mul(d,add(Fsame(y,u,v),Fcross(y,u,v))) for d,u,v in zip(rho,a,b)))
def xlogC(a,b):return add(cf(a,b)[0],ex(a))
def V(y):return add(ex(K-3*A),mul(3,xlogC(c*y+A,s*y)),mul(-2,xlogC(c*y,s*y)),mul(-1,xlogC(c*y+K,s*y)),mul(-y,t))
def W(y):return add(V(y),mul(2,U(y)))

def Gcross(y,z):
    real,imag=cg(C*y-z,S*y)
    return add(mul(C,real),mul(S,imag))
def Gsame(y,z):return cg(y-z,F(0))[0]
def pair(fn,u,v,w,z):return add(fn(v,w),fn(u,z),mul(-1,fn(u,w)),mul(-1,fn(v,z)))
def energy_bound():
    # Each of the 2 same-ray and 2 opposite-ray pairs has the same energy.
    E=add(*(mul(2*di*dj,add(pair(Gsame,u,v,w,z),pair(Gcross,u,v,w,z)))
            for di,u,v in zip(rho,a,b) for dj,w,z in zip(rho,a,b)))
    # For y>=2, |cy+j|>=y, and |cy+j|<=y+j. Using the integral field,
    # V(y)<=3*A*log(y+A)-K*log y - t*y.  U(y)<=log(y+b[-1]).
    # The majorant decreases because 3*A/y+2/y < t at y>=2.
    Y=F(3); step=F(1,400)
    assert b[-1]<Y and (3*A+2)/Y<t[0]
    tail=add(mul(3*A,logI(Y+A)),mul(-K,logI(Y)),mul(-Y,t),mul(2,logI(Y+b[-1])))
    assert tail[1]<-4
    assert all(v/step==int(v/step) for v in [A,K,*a,*b,Y])
    # Pointwise interpolation error <= step/2 for each primitive F.
    # Same ray: touching the singularity gives step/e; otherwise <=step/8.
    # Cross ray: for y>=step or shift>=step, |eta*y-shift|>=S*step;
    # hence curvature <=1/(S*step).  The exceptional origin is exact up
    # to the same step/e bound.  External field is handled identically.
    jump=rho[0]+sum(abs(x-y) for x,y in zip(rho,rho[1:]))+rho[-1]
    coeff=6+4*jump
    error=coeff*step/2
    theta=max(W(step*j)[1] for j in range(int(Y/step)+1))+error
    # Tail bound has to be below the chosen theta, not merely -4.
    assert tail[1]<theta
    constant=add(xlog(K),mul(-3,xlog(A)),ex(F(3,2)-(K-3*A)))
    upper=add(constant,mul(-1,E),ex(theta))[1]
    return upper,E,theta,error

@lru_cache(None)
def mom(k):
    return sum(stirling(k,r)*factorial(r)*(lam/(1-lam) if r==0 else lam**r/(1-lam)**(r+1)) for r in range(k+1))
def local_moment(j,zero):
    if zero:
        num=[F(0)]*(j+1)+[F(1),F(2),F(1)];poles=range(2,9)
    else:
        num=[F(0)]*(j+2)+[F(1)];poles=range(1,8)
    den=[F(1)]
    for l in poles:den=pmul(den,[F(l),F(1)])
    q,_=pdiv(num,den);r=sum(k*q[k]*mom(k-1) for k in range(1,len(q)))
    for l in poles:
        d=F(1)
        for k in poles:
            if k!=l:d*=k-l
        r+=peval(num,-l)/d*lam**(-l)*sum(lam**k/F(k*k) for k in range(1,l+1))
    return r

def local_det(zero):
    a=[local_moment(j,zero) for j in range(9)]
    return det([[a[i+j] for j in range(5)] for i in range(5)])

if __name__=='__main__':
    a0=ordinary(); ar=add(ex(a0),mul(-(K-F(1,2)),logI(F(2))),mul(-(2-K+3*A)**2/4,mul(2,logI(F(3)))),mul(A+F(1,6),logI(F(7))))
    d1,d0=local_det(False),local_det(True);assert d1 and d0
    print('Local blocks:',d1,d0,flush=True)
    print('Ordinary lower bound:',float(a0),flush=True)
    print('Full arithmetic lower bound:',float(ar[0]),flush=True)
    ub,E,theta,error=energy_bound()
    print('Energy interval:',float(E[0]),float(E[1]),flush=True)
    print('Theta upper:',float(theta),'interpolation error:',float(error),flush=True)
    print('Analytic upper bound:',float(ub),flush=True)
    print('Margin:',float(ar[0]-ub),flush=True)
    assert ar[0]>-F(521323,1000000)
    assert ub<-F(526078,1000000)
    assert ar[0]-ub>F(1,250)
    print('All finite exact negative-argument certificates passed.',flush=True)
