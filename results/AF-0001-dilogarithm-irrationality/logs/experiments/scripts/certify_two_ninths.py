"""Exact finite checks for a candidate Li_2(2/9) Hankel family.
The certificates support a candidate irrationality proof; the general mathematical lemmas must also hold. Standard library only.
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

kappa=F(9,8)
lam=F(2,9)

def ordinary(cut=F(1,500)):
    H=F(1); K=kappa
    points={cut,K}
    for a in [H,K]:
        points.update(a/j for j in range(1,int(a/cut)+1) if cut<a/j<K)
    points=sorted(points); total=F(0)
    for l,r in zip(points,points[1:]):
        x=(l+r)/2; qc=K//x; qh=H//x
        rc=K-qc*x; rh=H-qh*x
        jet=[];raw=[]
        for c,cap in [(qc,x-rc),(qc+1,rc)]:
            if not cap:continue
            w=-c-1
            jet.extend((w+2*j,cap) for j in range(qh+3))
            raw.extend((w+2*j+2*(j==c-1),cap) for j in range(c))
        def pick(slots,raw=False):
            left=H; s=F(0)
            for w,cap in sorted(slots):
                if raw and w>=0:break
                d=min(left,cap);s+=w*d;left-=d
                if not left:break
            assert raw or not left
            return s
        norm=H*qc-2*(x*qh*(qh-1)/2+qh*rh)
        total+=(r-l)*(norm+max(pick(jet),pick(raw,True)))
    return total-2*cut

# Outward rounded interval arithmetic for real logs.
D=10**15

def core(q):
    assert 1<=q<=2
    r=(q-1)/(q+1);z=r;s=F(0)
    for i in range(20):
        s+=2*z/(2*i+1);z*=r*r
    return s,s+2*z/(41*(1-r*r))
L2=core(F(2))
@lru_cache(None)
def logI(q):
    q=F(q);assert q>0;k=0
    while q<1:q*=2;k-=1
    while q>2:q/=2;k+=1
    a,b=core(q);a+=k*(L2[0] if k>=0 else L2[1]);b+=k*(L2[1] if k>=0 else L2[0])
    return F((a*D)//1,D),F(-((-b*D)//1),D)
def add(*v):return sum(x[0] for x in v),sum(x[1] for x in v)
def mul(c,v):return (c*v[0],c*v[1]) if c>=0 else (c*v[1],c*v[0])
def ex(c):return F(c),F(c)
def xlog(x):return mul(x,logI(abs(x))) if x else ex(0)
def f(x):return add(xlog(x),ex(-x))
def g(x):return add(mul(x/2,xlog(x)),ex(-F(3,4)*x*x))

# A positive comparison measure of mass one, with mesh 1/40.
M=[5000,5000,5000,5000,5000,5000,5000,3819,3235,2875,2603,2389,2213,2065,1937,1826,1728,1641,1562,1490,1425,1365,1310,1259,1211,1167,1125,1086,1049,1014,981,950,920,891,864,837,812,788,764,742,720,699,678,659,639,620,602,584,567,549,533,516,500,484,468,452,437,421,406,391,376,361,346,330,315,300,284,268,252,235,217,199,179,158,134,107,71]
assert sum(M)==100000 and min(M)>=0
rho=[F(m,2500) for m in M]
A=[F(i,40) for i in range(len(M))];B=[a+F(1,40) for a in A]
t=logI(F(9,2));theta=-F(3340,1000)
def Lpair(y,a,b):return add(f(y-a),mul(-1,f(y-b)))
def pot(y):return add(*(mul(d,Lpair(y,a,b)) for d,a,b in zip(rho,A,B)))
def V(y):return add(xlog(y),mul(-1,xlog(y+kappa)),ex(kappa),mul(-y,t))
def W(y):return add(V(y),mul(2,pot(y)))

def energy_bound():
    Y=F(4)
    # W<=V+2 log(y) after the support, and this majorant decreases for y>=4.
    assert B[-1]<Y and t[0]>F(1,2)
    assert add(V(Y),mul(2,logI(Y)))[1]<theta
    E=add(*(mul(di*dj,add(g(b-c),g(a-d),mul(-1,g(a-c)),mul(-1,g(b-d)))) for di,a,b in zip(rho,A,B) for dj,c,d in zip(rho,A,B)))
    # On mesh intervals the linear-interpolation L1 error of f(y-a)
    # is <= s^2(1/2 + H_N/6) when a is on the mesh.  All shifts
    # are on the mesh, including the shift -kappa (outside [0,Y]).
    step=F(1,400);N=int(Y/step)
    assert all(v/step==int(v/step) for v in [kappa,*A,*B])
    coefficient_norm=2+2*(rho[0]+sum(abs(x-y) for x,y in zip(rho,rho[1:]))+rho[-1])
    assert coefficient_norm==10
    harmonic=sum(F(1,j) for j in range(1,N+int(kappa/step)+1))
    error=coefficient_norm*step**2*(F(1,2)+harmonic/6)
    samples=[max(F(0),W(step*j)[1]-theta) for j in range(N+1)]
    pen=step*(sum(samples[1:-1])+(samples[0]+samples[-1])/2)+error
    TV=ex(error)

    C=add(xlog(kappa),ex(F(3,2)-kappa))
    upper=add(C,mul(-1,E),ex(theta),ex(2*pen))[1]
    return upper,E,TV,pen

# Exact local block determinants for the prime-index nonvanishing argument.
def pmul(a,b):
    c=[F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):c[i+j]+=x*y
    return c
def pdiv(a,b):
    a=list(a);q=[F(0)]*max(1,len(a)-len(b)+1)
    while len(a)>=len(b):
        k=len(a)-len(b);z=a[-1]/b[-1];q[k]=z
        for i,x in enumerate(b):a[k+i]-=z*x
        assert not a[-1];a.pop()
    return q,a
def peval(a,x):
    v=F(0)
    for z in reversed(a):v=v*x+z
    return v
@lru_cache(None)
def stirling(k,r):
    if k==0:return int(r==0)
    if r==0 or r>k:return 0
    return r*stirling(k-1,r)+stirling(k-1,r-1)
@lru_cache(None)
def mom(k):
    return sum(stirling(k,r)*factorial(r)*(lam/(1-lam) if r==0 else lam**r/(1-lam)**(r+1)) for r in range(k+1))

def local_moment(j,zero):
    num=[F(0)]*(j+int(zero))+[F(1)]
    poles=range(1,10) if zero else range(9)
    den=[F(1)]
    for l in poles:den=pmul(den,[F(l),F(1)])
    q,_=pdiv(num,den);s=sum(k*q[k]*mom(k-1) for k in range(1,len(q)))
    for l in poles:
        d=F(1)
        for k in poles:
            if k!=l:d*=k-l
        c=peval(num,-l)/d
        s+=c*lam**(-l)*sum(lam**k/F(k*k) for k in range(1,l+1))
    return s

def det(a):
    a=[list(r) for r in a];d=F(1);n=len(a)
    for j in range(n):
        i=next((i for i in range(j,n) if a[i][j]),None)
        if i is None:return F(0)
        if i!=j:a[i],a[j]=a[j],a[i];d=-d
        v=a[j][j];d*=v
        for i in range(j+1,n):
            r=a[i][j]/v
            for k in range(j+1,n):a[i][k]-=r*a[j][k]
    return d

def local_det(zero):
    a=[local_moment(j,zero) for j in range(15)]
    return det([[a[i+j] for j in range(8)] for i in range(8)])

if __name__=='__main__':
    a=ordinary();ari=add(ex(a),mul(-(kappa-F(1,2)),logI(F(2))),mul(-(2-kappa)**2/4,logI(F(7))),mul(F(1,6),logI(F(9))))
    d1,d0=local_det(False),local_det(True)
    assert d1 and d0
    print('Local blocks:',d1,d0,flush=True)
    print('Ordinary-prime lower bound:',float(a),flush=True)
    print('Full arithmetic lower bound:',float(ari[0]),flush=True)
    Bup,E,err,pen=energy_bound()
    print('Analytic upper bound:',float(Bup),flush=True)
    print('Interpolation error bound:',float(err[1]),flush=True)
    print('Margin:',float(ari[0]-Bup),flush=True)
    assert ari[0]>-F(133,100)
    assert Bup<-F(134,100)
    assert ari[0]-Bup>F(1,100)
    print('All finite exact certificates passed.',flush=True)
