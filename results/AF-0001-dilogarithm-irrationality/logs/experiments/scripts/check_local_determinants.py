"""Third computation of the eight local determinants (manuscript, Table 6 and Appendix A.3).

The moments are computed from Stirling numbers of the second kind, the local functional by
polynomial division and residues, and each 4x4 or 8x8 Hankel determinant through an
explicit factorisation M = L U that is checked entrywise. The determinants are compared
with the values printed in Table 6 of the manuscript.

This program accompanied the original candidate proof. It is reproduced here with two
changes: it compares with the values of Table 6 (instead of reading them from the draft
formal sources of the original research), and the guard below. It checks with assert
statements, so it refuses to run when assertions are disabled (python -O).
"""
import sys as _sys
if not __debug__:
    _sys.exit("assertions are disabled (python -O): this program refuses to run")
from fractions import Fraction as F
from functools import lru_cache
from math import prod, factorial

# Table 6 of the manuscript: (case, zero) -> determinant of the local Hankel matrix.
TABLE_5 = {
    ('TwoEleven', False): F(17828022563089333969, 1224440064),
    ('TwoEleven', True): F(12598972834814973210048467, 2295825120),
    ('TwoNine', False): F(3951366107675153857566158184061855291890957151, 50404062960731160576000000000000),
    ('TwoNine', True): F(75748065809620696385810762379349631101207641762772048941, 23344937339644196864000000000000),
    ('MinusTwoNine', False): F(1677163510311484581, 15488000),
    ('MinusTwoNine', True): F(16417954848664067036722569, 524733440),
    ('MinusTwoSeven', False): F(14067971871496713969085291850153, 1057916215296000000),
    ('MinusTwoSeven', True): F(17800469908791563702231968746821382359, 495898225920000000),
}
# An independent implementation of the local rational functional from
# polynomial division and residues, rather than the reciprocal-series code.
@lru_cache(None)
def stir(k,j):
    if k==0:return int(j==0)
    if j==0 or j>k:return 0
    return j*stir(k-1,j)+stir(k-1,j-1)
def mom(q,k):
    return sum(stir(k,j)*factorial(j)*(q/(1-q) if j==0 else q**j/(1-q)**(j+1)) for j in range(k+1))
def pmul(a,b):
    c=[F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):c[i+j]+=x*y
    return c
def peval(a,x):
    v=F(0)
    for z in reversed(a):v=v*x+z
    return v
def local(q,A,K,j,zero):
    if A==0:
        poles=list(range(1,K+1)) if zero else list(range(K))
        num=[F(0)]*(j+int(zero))+[F(1)]
    elif zero:
        poles=list(range(2,K+1)); num=[F(0)]*(j+1)+[F(1),F(2),F(1)]
    else:
        poles=list(range(1,K)); num=[F(0)]*(j+2)+[F(1)]
    den=[F(1)]
    for l in poles:den=pmul(den,[F(l),F(1)])
    rem=num.copy(); quotient=[F(0)]*max(1,len(num)-len(den)+1)
    while len(rem)>=len(den):
        i=len(rem)-len(den); c=rem[-1]/den[-1]; quotient[i]=c
        for j,v in enumerate(den):rem[i+j]-=c*v
        assert rem[-1]==0;rem.pop()
    res=sum(k*v*mom(q,k-1) for k,v in enumerate(quotient) if k)
    for l in poles:
        res+=peval(num,-l)/prod(F(k-l) for k in poles if k!=l)*q**(-l)*sum(q**k/F(k*k) for k in range(1,l+1))
    return res
cases=[('TwoEleven','twoEleven',F(2,11),1,6,4),('TwoNine','twoNine',F(2,9),0,9,8),('MinusTwoNine','minusTwoNine',F(-2,9),1,7,4),('MinusTwoSeven','minusTwoSeven',F(-2,7),1,8,5)]
logs=[]
def rat(v):
    if v.denominator==1:return str(v.numerator) if v>=0 else f'({v.numerator})'
    return f'({v.numerator}/{v.denominator})'
def mat(M):return '![\n    '+',\n    '.join('!['+', '.join(map(rat,row))+']' for row in M)+'\n  ]'
for name,case,q,A,K,H in cases:
    for zero in (False,True):
        s='zero' if zero else 'nonzero'; z=str(zero).lower()
        v=[local(q,A,K,j,zero) for j in range(2*H-1)]
        M=[[v[i+j] for j in range(H)] for i in range(H)]
        L=[[F(int(i==j)) for j in range(H)] for i in range(H)]
        U=[row.copy() for row in M]
        for k in range(H):
            assert U[k][k]!=0
            for i in range(k+1,H):
                L[i][k]=U[i][k]/U[k][k]
                for j in range(k,H):U[i][j]-=L[i][k]*U[k][j]
        assert all(sum(L[i][k]*U[k][j] for k in range(H))==M[i][j] for i in range(H) for j in range(H))
        assert all(L[i][j]==0 for i in range(H) for j in range(i+1,H))
        assert all(U[i][j]==0 for i in range(H) for j in range(i))
        d=prod(U[i][i] for i in range(H))
        # Compare with the value printed in Table 6 of the manuscript.
        assert d == TABLE_5[(name, zero)], (name, s, d)
        logs.append(f'{name} {s}: exact LU identity, both triangles, unit lower diagonal, determinant {d} verified')
print('\n'.join(logs))
