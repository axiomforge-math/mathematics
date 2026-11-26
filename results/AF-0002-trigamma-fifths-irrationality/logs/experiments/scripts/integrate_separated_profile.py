"""Exact local-rank integration for piecewise constant row/column roles.
Geometry common [0,1), border [1,1+c), rows first c/2 then columns.
General parameter: q blocks, each block split R then C; q=1 fully separated.
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
from compute_polar_geometry import polar

def setup(c,q):
    w=c/(2*q)
    return [(F(0),F(1),'B')]+[(1+j*w,1+(j+1)*w,'R' if j%2==0 else 'C') for j in range(2*q)]

def branches(G,kap,x):
    N=G[-1][1]; n=(N+1)/2; N0=N//x; ends={u for a,b,r in G for u in (a,b)}
    cuts=sorted({F(0),x,kap*x,x/2,*[u%x for u in ends]})
    rk=F(0);rows=defaultdict(F);cols=defaultdict(F)
    for a,b in zip(cuts,cuts[1:]):
        t=(a+b)/2;count=N0+int(t<N%x)
        roles=[next(role for l,u,role in G if l<t+j*x<u) for j in range(count)]
        R=tuple(j for j,role in enumerate(roles) if role in ('B','R'));Q=tuple(j for j,role in enumerate(roles) if role in ('B','C'))
        v,zr,ls,zc,rs=polar(kap,R,Q,(int(t>kap*x),int(t>x/2))); cap=b-a;rk+=cap*v
        for l in ls:rows[l]+=cap
        for l in rs:cols[l]+=cap
    d=n-rk;nr=sum(rows.values());nc=sum(cols.values());base=2*n-2*d
    return {**{'row':base+nr,'col':base+nc},**{l:base+nr+nc-rows[l]-cols[l] for l in rows.keys()|cols.keys()}}

def cell(G,k,l,r):
    u=(2*l+r)/3;v=(l+2*r)/3;A=branches(G,k,u);B=branches(G,k,v);assert A.keys()==B.keys()
    lines=[(A[j]-(B[j]-A[j])*u/(v-u),(B[j]-A[j])/(v-u)) for j in A]
    cuts={l,r}
    for i,(a,b) in enumerate(lines):
        for e,f in lines[:i]:
            if b!=f:
                x=(e-a)/(b-f)
                if l<x<r:cuts.add(x)
    cuts=sorted(cuts)
    return sum((r-l)*min(a+b*(l+r)/2 for a,b in lines) for l,r in zip(cuts,cuts[1:]))

def integral(c,q,cut=F(1,20),verbose=False):
    G=setup(c,q);ends={u for a,b,role in G for u in (a,b)};N=1+c;top=5*N;diff={a-b for a in ends for b in ends if a>b};out=[]
    for k in [F(j,5) for j in range(1,5)]:
        cuts={cut,top}
        for t in diff:
            for j in range(1,int(t/cut)+1):
                if cut<t/j<top:cuts.add(t/j)
        for u in ends:
            for z in (k,F(1,2)):
                for j in range(int(u/cut)+1):
                    if cut<u/(j+z)<top:cuts.add(u/(j+z))
        cuts=sorted(cuts);a=(2+c)*cut
        for l,r in zip(cuts,cuts[1:]):a+=cell(G,k,l,r)
        out.append(a)
        if verbose:print('k',k,'integral',float(a),flush=True)
    return sum(out)/4

if __name__=='__main__':
    import sys
    c=F(sys.argv[1]) if len(sys.argv)>1 else F(1,8);q=int(sys.argv[2]) if len(sys.argv)>2 else 1;cut=F(sys.argv[3]) if len(sys.argv)>3 else F(1,20)
    a=integral(c,q,cut,True);print('c',c,'q',q,'cut',cut,'Lambda',float(a),'exact',a,flush=True)
