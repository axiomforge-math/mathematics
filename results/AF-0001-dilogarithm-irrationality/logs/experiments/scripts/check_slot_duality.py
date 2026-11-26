"""Check the new direct weak-duality certificates against the old greedy values.
All operations are exact rational arithmetic. This is not a Lean proof.
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
from math import lcm

CASES = {
    '2/11': (F(1), F(6), F(4), F(1,40)),
    '2/9': (F(0), F(9,8), F(1), F(1,500)),
    '-2/9': (F(1,4), F(7,4), F(1), F(1,500)),
    '-2/7': (F(1,5), F(8,5), F(1), F(1,500)),
}

def greedy(mass, slots, optional):
    left, total = mass, 0
    for w,c in sorted(slots):
        if optional and w>=0: break
        used=min(left,c); total+=used*w; left-=used
        if not left: break
    assert optional or left==0
    return total

def price(mass, slots, optional):
    left=mass
    for w,c in sorted(slots):
        if optional and w>=0: return 0
        if left<=c: return min(w,0) if optional else w
        left-=c
    return 0

def dual(mass,slots,t):
    return mass*t+sum(min(0,w-t)*c for w,c in slots)

def check(A,K,H,cut):
    points={cut,K}
    for a in (A,K,H,K-A):
        points.update(a/j for j in range(1,int(a/cut)+1) if cut<a/j<K)
    points=sorted(points); total=F(0)
    for l,r in zip(points,points[1:]):
        x=(l+r)/2; qa=A//x; qc=K//x; qh=H//x
        ra=A-qa*x;rc=K-qc*x;rh=H-qh*x
        cuts=sorted({F(0),ra,rc,x});jets=[];raw=[]
        den=lcm(H.denominator,*(v.denominator for v in cuts)); mass=int(H*den)
        for lo,hi in zip(cuts,cuts[1:]):
            u=(lo+hi)/2;a=qa+int(u<ra);c=qc+int(u<rc);cap=hi-lo
            cap=int(cap*den); w=3*a-c-1
            jets.extend((w+2*j,cap) for j in range(qh+3))
            raw.extend((w+2*j+2*int(a==0 and j==c-a-1),cap) for j in range(c-a))
        tj=min(price(mass,jets,False),min([0]+[w for w,_ in jets])+2*(qh+3))
        tr=min(price(mass,raw,True),0)
        jv=dual(mass,jets,tj);rv=dual(mass,raw,tr)
        assert jv==greedy(mass,jets,False), (l,r,jv,greedy(mass,jets,False))
        assert rv==greedy(mass,raw,True), (l,r,rv,greedy(mass,raw,True))
        norm=H*(qc-3*qa)-2*(x*qh*(qh-1)/2+qh*rh)
        total+=(r-l)*(norm+F(max(jv,rv),den))
    return len(points)-1,total-2*H*cut

if __name__=='__main__':
    for name,args in CASES.items():
        n,v=check(*args)
        print(f'{name}: {n} intervals; every dual value equals the previous greedy value exactly; lower bound {float(v):.16g}')
