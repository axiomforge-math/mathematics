"""Rational/fixed-point certificate. No floating-point calculations are used
for bounds; floats at the end only display certified rational bounds.
See proof note for error budgets and interpolation lemma.
"""

# This program is one of the original programs of the candidate proof. It is reproduced
# here unchanged except for its file name, the imports of its companion programs, the location of its data file,
# and this guard. It checks with assert statements, so it refuses to run when assertions
# are disabled (python -O); a failed check exits with status 1.
import sys as _sys
if not __debug__:
    _sys.exit("assertions are disabled (python -O): this program refuses to run")
from fractions import Fraction as F
from functools import lru_cache
from collections import defaultdict
import json
S=1<<100; E=1000000; B=10**14

def ceildiv(a,b):return -((-a)//b)
def add(a,b):return a[0]+b[0],a[1]+b[1]
def sub(a,b):return a[0]-b[0],a[1]-b[1]
def mul(a,b):return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]
def conj(a):return a[0],-a[1]
def norm(a):return a[0]*a[0]+a[1]*a[1]
def L1(a):return abs(a[0])+abs(a[1])
def atanh_series(u):
 q=u*u//S;w=u;t=0
 for j in range(64):t+=w//(2*j+1);w=w*q//S
 return 2*t
LOG2=atanh_series(S//3)
def lograt(x,y):
 assert x>0 and y>0
 k=x.bit_length()-y.bit_length()
 if k>=0:y<<=k
 else:x<<=-k
 if x<y:x*=2;k-=1
 assert y<=x<2*y and abs(k)<1000
 return k*LOG2+atanh_series((x-y)*S//(x+y))
def atan_series(u):
 q=u*u//S;w=u;t=0
 for j in range(64):t+=(-1 if j%2 else 1)*(w//(2*j+1));w=w*q//S
 return t
PI=16*atan_series(S//5)-4*atan_series(S//239)
def atan_small(y,x):
 assert 0<=y<=x and x>0
 if 2*y>x:return PI//4-atan_series((x-y)*S//(x+y))
 return atan_series(y*S//x)
def arg(x,y):
 if y<0:return -arg(x,-y)
 if x<0:return PI-arg(-x,y)
 if x==0:return PI//2 if y else 0
 if y>x:return PI//2-atan_small(x,y)
 return atan_small(y,x)
def logabs(x,y,d):return lograt(x*x+y*y,d*d)//2

def hre(x,y,d):
 if x==y==0:return 0
 return (x*logabs(x,y,d)-y*arg(x,y))//d

# Exact rational coordinates; D factor 2^16 permits dyadic bisection.
from pathlib import Path as _Path
data=json.load(open(_Path(__file__).resolve().parent.parent/'certificates'/'decay-trial-measure.json'));D=data['coordinate_denominator']*(1<<16);M=data['mass_denominator'];cv=lambda z:tuple(t*(1<<16) for t in z)
mu=[(cv(a),cv(b),F(m,M)) for a,b,m in data['segments']];verts=list(map(cv,data['vertices']));lam=F(17,16)
assert sum(m for a,b,m in mu)==lam and all(m>0 and a!=b for a,b,m in mu)
assert sorted(mu)==sorted((conj(a),conj(b),m) for a,b,m in mu)
nu=[((0,0),(D,0),F(1)),((D,0),(9*D//8,0),F(1,16))]
assert sum(m for a,b,m in nu)==lam
signed=mu+[(a,b,-m) for a,b,m in nu]
# Use cached exact scaled evaluations. E bounds elementary function errors;
# |u|_1 <= 10^6 is checked for every use. Hence each potential has error
# < 3*10^6 E/S < 1e-17. Weighted sum and flooring are budgeted by 1e-15.
def segpot(z,a,b):
 v=sub(b,a);w=norm(v);x,y=mul(sub(z,a),conj(v));assert abs(x)+abs(y)<=10**6*w
 return S-logabs(*v,D)-hre(x,y,w)+hre(x-w,y,w)
EPS=F(1,10**15)
@lru_cache(None)
def pot(z):
 v=sum((m*segpot(z,a,b) for a,b,m in signed),F(0))/S
 # We use (1-eps0)*pi |Im z| to reserve a positive tail factor.
 assert abs(z[1])<=2*D
 return v+F(999999,1000000)*F(PI,S)*F(abs(z[1]),D)

# Second derivative along any straight cell is a sum of endpoint simple poles.
co=defaultdict(lambda:[F(0),F(0)])
for a,b,m in signed:
 v=sub(b,a);w=norm(v);c=[m*D*v[0]/w,-m*D*v[1]/w]
 for j in range(2):co[a][j]+=c[j];co[b][j]-=c[j]
coef=[(z,ceildiv((abs(x)+abs(y)).numerator*B,(abs(x)+abs(y)).denominator)) for z,(x,y) in co.items() if x or y]

def err(a,b):
 l=L1(sub(a,b));xmin,xmax=sorted((a[0],b[0]));ymin,ymax=sorted((a[1],b[1]));s=0
 for z,w in coef:
  if z==a or z==b:s+=ceildiv(l*w,2*D)
  else:
   dx=max(xmin-z[0],z[0]-xmax,0);dy=max(ymin-z[1],z[1]-ymax,0);dist=max(dx,dy)
   if not dist:return None
   s+=ceildiv(l*l*w,8*D*dist)
 return s
# First split at all endpoints on each segment, then bisect as needed.
def cells(a,b,tol=F(1,50000)):
 v=sub(b,a);w=norm(v);points={a,b}
 for z,c in coef:
  d=sub(z,a);t=mul(d,conj(v))
  if t[1]==0 and 0<t[0]<w:points.add(z)
 points=sorted(points,key=lambda z:mul(sub(z,a),conj(v))[0]);stack=list(zip(points,points[1:]));result=[]
 while stack:
  a,b=stack.pop();e=err(a,b)
  if e is not None and F(e,B)<=tol:result.append((a,b,F(e,B)));continue
  assert (a[0]+b[0])%2==0 and (a[1]+b[1])%2==0,'increase dyadic denominator'
  mid=((a[0]+b[0])//2,(a[1]+b[1])//2);assert mid!=a and mid!=b
  stack.extend([(a,mid),(mid,b)])
 return result

# Pair-energy by mixed primitive of log z, choosing a half-plane branch for
# each difference parallelogram. The diagonal uses the exact self-energy.
def G2(z):
 # 2G = z^2(log z - 3/2), in scaled units S*D^2.
 if z==(0,0):return (0,0)
 return mul(mul(z,z),(logabs(*z,D)-3*S//2,arg(*z)))
def pair(a,b,c,d):
 if a==c and b==d:return F(3,2)-F(logabs(*sub(b,a),D),S), F(E,S)
 v=sub(b,a);w=sub(d,c);z=[sub(b,c),sub(a,d),sub(a,c),sub(b,d)]
 for rot in ((1,0),(-1,0),(0,1),(0,-1)):
  zs=[mul(t,rot) for t in z]
  if all(t[0]>=0 for t in zs):break
 else:raise AssertionError('intersecting segments')
 vw=mul(mul(v,rot),mul(w,rot));g=[G2(t) for t in zs];q=sub(add(g[0],g[1]),add(g[2],g[3]));value=-F(mul(q,conj(vw))[0],2*S*norm(vw))
 error=F(2*E*sum(norm(t) for t in zs)*L1(vw),2*S*norm(vw))
 return value,error

def energy(mu):
 a=b=F(0)
 for i,(u,v,m) in enumerate(mu):
  for j,(w,z,n) in enumerate(mu[:i+1]):
   f,e=pair(u,v,w,z);t=m*n*(1 if i==j else 2);a+=t*(f-e);b+=t*(f+e)
 return a,b

if __name__=='__main__':
 # The sign of the interpolating curve is chosen for an actual contour in
 # the left half plane; support of mu lies in these same edges or the atom interval.
 assert all(x<0 and y>=0 for x,y in verts) and verts[0][1]==0
 assert all(a[1]<b[1] for a,b in zip(verts,verts[1:]))
 assert all(L1(z)<=D for a,b,m in mu for z in (a,b))
 def lies(z,a,b):
  t=mul(sub(z,a),conj(sub(b,a)));return t[1]==0 and 0<=t[0]<=norm(sub(b,a))
 edges=list(zip(verts,verts[1:]));es=edges+[(conj(a),conj(b)) for a,b in edges]+[(verts[0],(0,0))]
 assert all(any(lies(a,u,v) and lies(b,u,v) for u,v in es) for a,b,m in mu)
 cc=[q for a,b in edges for q in cells(a,b)];print('contour cells',len(cc),flush=True)
 theta=min(min(pot(a),pot(b))-e-EPS for a,b,e in cc)-F(1,10**8)
 # For y>=last ordinate, U_mu-U_nu >= -lambda log(1+(|x|+1)/y)
 # >= -lambda (|x|+1)/y. This plus the field is increasing in y.
 x,y=verts[-1];assert F(999999,1000000)*F(PI-E,S)*F(y,D)-lam*F(abs(x)+D,y)>theta
 print('theta certified lower',float(theta),flush=True)
 ac=cells(verts[0],(0,0));J=F(0)
 for a,b,e in ac:
  u,v=sorted([pot(a)-theta-e-EPS,pot(b)-theta-e-EPS]);length=F(abs(a[0]-b[0]),D)
  if v<=0:J+=length*(u+v)/2
  elif u<0:J-=length*u*u/(2*(v-u))
 print('atom cells',len(ac),'J lower',float(J),flush=True)
 il,iu=energy(mu);nl,nuu=energy(nu)
 print('energy mu upper',float(iu),'node energy lower',float(nl),flush=True)
 decay=2*lam*theta+4*J-iu+nl
 gain=F(LOG2-E,S)/256
 # exact rational conclusions with intentionally rounded conservative bounds
 assert decay>=F(35099,10000),float(decay)
 assert gain>=F(2707,1000000)
 print('D_alternating lower',float(decay),'D_separated lower',float(decay+gain),flush=True)
 print('PASS: D_alternating >= 3.5099, separation gain >= 0.002707, D_separated >= 3.512607',flush=True)
