"""Exact arithmetic helper functions shared by the certificates."""
from fractions import Fraction as F
from functools import lru_cache
from math import factorial

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

