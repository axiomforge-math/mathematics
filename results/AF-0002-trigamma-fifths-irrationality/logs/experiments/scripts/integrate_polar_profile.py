"""Two-layer polar-rank bound. exact=True integrates the piecewise affine minimum
exactly; midpoint-only mode is an upper estimate. See PROOF.md.
"""

# This program is one of the original programs of the candidate proof. It is reproduced
# here unchanged except for its file name, the imports of its companion programs,
# and this guard. It checks with assert statements, so it refuses to run when assertions
# are disabled (python -O); a failed check exits with status 1.
import sys as _sys
if not __debug__:
    _sys.exit("assertions are disabled (python -O): this program refuses to run")
from fractions import Fraction as F
from functools import lru_cache
from collections import defaultdict
import sympy as S
from itertools import product

def nullspace(A,n):
    A=[r.copy() for r in A]; piv=[];m=len(A);i=0
    for j in range(n):
        k=next((k for k in range(i,m) if A[k][j]),None)
        if k is None:continue
        A[i],A[k]=A[k],A[i];v=A[i][j]
        A[i][j:]=[a/v for a in A[i][j:]]
        for k in range(i+1,m):
            v=A[k][j]
            if v:A[k][j:]=[a-v*b for a,b in zip(A[k][j:],A[i][j:])]
        piv.append(j);i+=1
        if i==m:break
    out=[]
    for j in range(n):
        if j in piv:continue
        v=[F(0)]*n;v[j]=F(1)
        for i,k in reversed(list(enumerate(piv))):v[k]=-sum((A[i][l]*v[l] for l in range(k+1,n) if v[l]),F(0))
        out.append(v)
    return out

@lru_cache(None)
def polar_data(kap, common,total,arc,parity):
    # arc = (indicator for fifth, indicator for half)
    shifts=(kap,F(1,2)); weights=(1,-1)
    V=[];W=[]
    for j in range(total):
        V.append(sum((w*sum((1/(s+k) for k in range(j+a)),F(0)) for s,w,a in zip(shifts,weights,arc)),F(0)))
        W.append(sum((-w*sum((1/(s+k)**2 for k in range(j+a)),F(0)) for s,w,a in zip(shifts,weights,arc)),F(0)))
    R=list(range(common))+[i for i in range(common,total) if (i-common+parity)%2==0]
    Q=list(range(common))+[i for i in range(common,total) if (i-common+parity)%2==1]
    raw=[[W[i] if i==j else (V[j]-V[i])/(j-i) for j in Q] for i in R]
    A=S.Matrix(len(R),len(Q),lambda i,j:raw[i][j])
    # Use single rational RREF per side rather than symbolic rank.
    nl=nullspace([[raw[i][j] for i in range(len(R))] for j in range(len(Q))],len(R)); nr=nullspace(raw,len(Q)); rank=len(Q)-len(nr)
    def lines(ns,ids):
        # Work in a basis adapted to the map onto the two moment coordinates.
        B=S.Matrix(2,len(ids),lambda i,j:1 if i==0 else V[ids[j]])
        moments=B*S.Matrix.hstack(*(S.Matrix(v) for v in ns)) if ns else S.zeros(2,0)
        cols=moments.columnspace(); nzero=len(ns)-len(cols)
        if len(cols)==2:return nzero,[('line',F(0)),('inf',)]
        if not cols:return nzero,[]
        x,y=cols[0];return nzero,[('line',F(y/x)) if x else ('inf',)]
    zl,ll=lines(nl,R);zr,lr=lines(nr,Q)
    assert rank+zl+len(ll)==len(R) and rank+zr+len(lr)==len(Q)
    return rank,zl,ll,zr,lr

def branches(c,kap,x):
    n=1+c/2; N=1+c; R0=1//x;N0=N//x
    cuts=sorted({F(0),x,1-R0*x,N-N0*x,kap*x,x/2})
    Rrank=F(0);zrow=F(0);zcol=F(0);rows=defaultdict(F);cols=defaultdict(F)
    for a,b in zip(cuts,cuts[1:]):
        mid=(a+b)/2; common=R0+int(mid<1-R0*x);total=N0+int(mid<N-N0*x)
        arc=(int(mid>kap*x),int(mid>x/2));cap=(b-a)/2
        for parity in (0,1):
            rank,zl,ll,zr,lr=polar_data(kap,common,total,arc,parity)
            Rrank+=rank*cap;zrow+=zl*cap;zcol+=zr*cap
            for l in ll:rows[l]+=cap
            for l in lr:cols[l]+=cap
    d=n-Rrank;nr=sum(rows.values());nc=sum(cols.values());assert nr+zrow==nc+zcol==d
    # rank of second layer <= matching number in complete bipartite graph
    # excluding proportional pairs; also all zero-moment directions vanish.
    candidates={"row":2*n-2*d+nr,"col":2*n-2*d+nc}
    for l in rows.keys()|cols.keys():candidates[l]=2*n-2*d+nr+nc-rows[l]-cols[l]
    assert min(candidates.values())>=0
    return candidates

def bound(c,kap,x):return min(branches(c,kap,x).values())

def exact_cell(c,kap,l,r):
    u=(2*l+r)/3;v=(l+2*r)/3;B=branches(c,kap,u);C=branches(c,kap,v);assert B.keys()==C.keys()
    lines=[(B[k]-(C[k]-B[k])*u/(v-u),(C[k]-B[k])/(v-u)) for k in B]
    cuts={l,r}
    for i,(a,b) in enumerate(lines):
        for e,f in lines[:i]:
            if b!=f:
                x=(e-a)/(b-f)
                if l<x<r:cuts.add(x)
    cuts=sorted(cuts);return sum((r-l)*min(a+b*(l+r)/2 for a,b in lines) for l,r in zip(cuts,cuts[1:]))

def integral(c,cut=F(1,100), details=False, exact=False):
    N=1+c;top=5*N;results=[]
    for kap in [F(j,5) for j in range(1,5)]:
        cuts={cut,top}
        for u in (F(1),N):
            for j in range(int(u/cut)+1):
                for z in (F(0),kap,F(1,2)):
                    if j+z and cut<u/(j+z)<top:cuts.add(u/(j+z))
        for j in range(1,int(c/cut)+1):
            if cut<c/j<top:cuts.add(c/j)
        cuts=sorted(cuts);a=F(0);per=[]
        for l,r in zip(cuts,cuts[1:]):
            e=bound(c,kap,(l+r)/2);a+=exact_cell(c,kap,l,r) if exact else e*(r-l);per.append((l,r,e))
        a+=(2+c)*cut
        results.append(a)
        if details:print('kap',kap,'integral',float(a),'intervals',len(per),flush=True)
    return sum(results)/4

if __name__=='__main__':
    import sys
    cut=F(sys.argv[1]) if len(sys.argv)>1 else F(1,50)
    for c in ([F(sys.argv[2])] if len(sys.argv)>2 else [F(1,8),F(1,10),F(3,20),F(1,6),F(1,5),F(1,4),F(0)]):
        print('c',c,'cut',cut,'Lambda',float(integral(c,cut,True)),flush=True)
