"""Two-layer polar bound and contour diagnostic for arbitrary finite block geometry.
C: list of intervals of total length 1; union [0,N). All endpoints rational.
Every endpoint and scale is chosen so that the discrete boundaries are even.
"""

# This program is one of the original programs of the candidate proof. It is reproduced
# here unchanged except for its file name, the imports of its companion programs,
# and this guard. It checks with assert statements, so it refuses to run when assertions
# are disabled (python -O); a failed check exits with status 1.
import sys as _sys
if not __debug__:
    _sys.exit("assertions are disabled (python -O): this program refuses to run")
from fractions import Fraction as F
from collections import defaultdict
from functools import lru_cache
from integrate_polar_profile import nullspace
import sympy as S

@lru_cache(None)
def polar(kap,R,Q,arc):
    shifts=(kap,F(1,2)); weights=(1,-1);total=max(R+Q,default=-1)+1
    V=[];W=[]
    for j in range(total):
        V.append(sum((w*sum((1/(s+k) for k in range(j+a)),F(0)) for s,w,a in zip(shifts,weights,arc)),F(0)))
        W.append(sum((-w*sum((1/(s+k)**2 for k in range(j+a)),F(0)) for s,w,a in zip(shifts,weights,arc)),F(0)))
    A=[[W[i] if i==j else (V[j]-V[i])/(j-i) for j in Q] for i in R]
    nr=nullspace(A,len(Q));nl=nullspace([[A[i][j] for i in range(len(R))] for j in range(len(Q))],len(R));rk=len(Q)-len(nr)
    def lines(ns,ids):
        mm=[(sum(z),sum((v*V[j] for v,j in zip(z,ids)),F(0))) for z in ns]
        ls=set(('line',y/x) if x else ('inf',) for x,y in mm if x or y)
        if len(ls)>1:return len(ns)-2,[('line',F(0)),('inf',)]
        return len(ns)-len(ls),list(ls)
    a,b=lines(nl,R);c,d=lines(nr,Q);return rk,a,b,c,d

def bound(C,N,kap,x):
    n=(N+1)/2;N0=N//x;endpoints={v for ab in C for v in ab}|{N}
    cuts=sorted({F(0),x,kap*x,x/2,*[z%x for z in endpoints]})
    rk=F(0);zr=F(0);zc=F(0);rows=defaultdict(F);cols=defaultdict(F)
    for a,b in zip(cuts,cuts[1:]):
        t=(a+b)/2;total=N0+int(t<N%x);common=set(j for j in range(total) if any(l<t+j*x<u for l,u in C))
        arc=(int(t>kap*x),int(t>x/2));cap=(b-a)/2
        for parity in (0,1):
            R=tuple(j for j in range(total) if j in common or (j+parity)%2==0)
            Q=tuple(j for j in range(total) if j in common or (j+parity)%2==1)
            r,az,al,bz,bl=polar(kap,R,Q,arc);rk+=r*cap;zr+=az*cap;zc+=bz*cap
            for l in al:rows[l]+=cap
            for l in bl:cols[l]+=cap
    d=n-rk;nr=sum(rows.values());nc=sum(cols.values());assert nr+zr==nc+zc==d
    rank2=min([nr,nc]+[nr+nc-rows[l]-cols[l] for l in rows.keys()|cols.keys()]);assert rank2>=0
    return 2*n-2*d+rank2

def integral(C,N,cut=F(1,20)):
    top=5*N;results=[];ends={v for ab in C for v in ab}|{N};diff={a-b for a in ends for b in ends if a>b}
    for kap in [F(j,5) for j in range(1,5)]:
        cuts={cut,top}
        for u in ends:
            if not u:continue
            for j in range(int(u/cut)+1):
                for z in (F(0),kap,F(1,2)):
                    if j+z and cut<u/(j+z)<top:cuts.add(u/(j+z))
        for u in diff:
            for j in range(1,int(u/cut)+1):
                if cut<u/j<top:cuts.add(u/j)
        cuts=sorted(cuts);a=(N+1)*cut
        for l,r in zip(cuts,cuts[1:]):a+=bound(C,N,kap,(l+r)/2)*(r-l)
        results.append(a)
    return sum(results)/4

def node_geometry(c,s):
    # single border interval [s,s+c], common on the complement
    return tuple(ab for ab in ((F(0),s),(s+c,1+c)) if ab[0]<ab[1]),1+c

if __name__=='__main__':
    c=F(1,8)
    from integrate_polar_profile import integral as old
    a=integral(*node_geometry(c,F(1)));assert a==old(c,F(1,20));print('old',float(a),flush=True)
    for s in [F(0),F(1,8),F(1,4),F(1,2),F(3,4),F(7,8)]:
        a=integral(*node_geometry(c,s));print('s',s,'Lambda upper',float(a),flush=True)
