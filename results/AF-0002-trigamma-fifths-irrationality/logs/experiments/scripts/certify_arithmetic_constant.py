"""Exact rational integration, independent finite tests of the polar digit
formula and the power-of-two determinant normalization.
"""

# This program is one of the original programs of the candidate proof. It is reproduced
# here unchanged except for its file name, the imports of its companion programs,
# and this guard. It checks with assert statements, so it refuses to run when assertions
# are disabled (python -O); a failed check exits with status 1.
import sys as _sys
if not __debug__:
    _sys.exit("assertions are disabled (python -O): this program refuses to run")
from fractions import Fraction as F
from integrate_polar_profile import integral,polar_data
from integrate_separated_profile import integral as sep_integral
from math import prod
import sympy as S

def prefix(s,N):
 f=[F(0)];d=[F(0)]
 for j in range(N):
  a=j+s;b=j+F(1,2);f.append(f[-1]+1/a-1/b);d.append(d[-1]-1/a**2+1/b**2)
 return f,d

def matrix(f,d,R,Q,X):
 return [[X+d[i] if i==j else (f[j]-f[i])/ (j-i) for j in Q] for i in R]

def ratmod(x,power):
 x=F(x);return x.numerator*pow(x.denominator,-1,power)%power

def test_polar():
 count=0
 for h in (16,32,48,64):
  m=h//16;N=h+2*m;R=list(range(h+m));Q=list(range(h))+list(range(h+m,N))
  for p in (19,23,29,31,37,41,43,47,53):
   if p*p<=5*N:continue
   for k in (1,2,3,4):
    s=F(k,5);kap=F(k*pow(p,-1,5)%5,5);p1=int(p*kap+1-s);p2=(p+1)//2
    f,d=prefix(s,N);V=[];W=[]
    for j in range(N):
     i,l=j%p,j//p;eps=(i>=p1,i>=p2)
     V.append(sum((w*sum((1/(a+t) for t in range(l+e)),F(0)) for a,w,e in zip((kap,F(1,2)),(1,-1),eps)),F(0)))
     W.append(sum((-w*sum((1/(a+t)**2 for t in range(l+e)),F(0)) for a,w,e in zip((kap,F(1,2)),(1,-1),eps)),F(0)))
    A=matrix(f,d,R,Q,F(1,7))
    for u,i in enumerate(R):
     for v,j in enumerate(Q):
      L=p*p*A[u][v]
      if i==j:want=W[i]
      elif i%p==j%p:want=(V[j]-V[i])/((j-i)//p)
      else:want=p*(V[j]-V[i])/(j%p-i%p)
      assert ratmod(L-want,p*p)==0,(h,p,k,i,j)
      count+=1
 print('polar congruence checks:',count,flush=True)

def test_ratio():
 count=0
 for h,m in ((4,2),(6,3),(8,4)):
  N=h+2*m;R0=list(range(h))+list(range(h,N,2));Q0=list(range(h))+list(range(h+1,N,2));R1=list(range(h+m));Q1=list(range(h))+list(range(h+m,N))
  for k in (1,2,3,4):
   f,d=prefix(F(k,5),N)
   for I in ([],[0],[h-1]):
    cut=lambda T:[i for i in T if i not in I]
    for x in (F(1,7),F(2,3)):
     A=S.Matrix(matrix(f,d,cut(R0),cut(Q0),x)).det(method='domain-ge');B=S.Matrix(matrix(f,d,cut(R1),cut(Q1),x)).det(method='domain-ge');assert A==2**(m*(m-1))*B
     count+=1
 print('exact separated determinant identities:',count,flush=True)

if __name__=='__main__':
 test_polar();test_ratio()
 a=integral(F(1,8),F(1,20),True,True);b=sep_integral(F(1,8),1,F(1,20));assert a==b and a<F(3512131,10**6)
 print('arithmetic exact rational:',a,flush=True)
 print('PASS: Lambda < 3.512131',flush=True)
