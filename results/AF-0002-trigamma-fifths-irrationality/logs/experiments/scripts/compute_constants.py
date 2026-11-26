"""Closed form of I(nu), the separation gain, the margins and xi_k (mpmath, 60 digits), and the
accuracy of the fixed-point log 2 and pi of certify_decay_constant.py (manuscript, Lemma C.3,
Section 6.2, Appendix D.2). Floating point: orientation only, proves nothing.

Usage: python compute_constants.py
"""
import mpmath as mp
mp.mp.dps=60
c=mp.mpf(1)/8
G=lambda u: (u**2*mp.log(u)/2-3*u**2/4) if u>0 else mp.mpf(0)
Inu = mp.mpf(3)/2 + (c**2/4)*(mp.mpf(3)/2-mp.log(c)) - (G(1+c)-G(c)-G(1))
print('I(nu) exact', Inu)
print('log2/256', mp.log(2)/256)
A=mp.mpf(304227995343501721142691896310988016794079029050925423)/86622067750624596685118168422516024981216422248448000
print('A', A)
Dalt=mp.mpf('3.5101522752601806'); print('Dsep', Dalt+mp.log(2)/256, 'margin unrounded', Dalt+mp.log(2)/256-A)
print('rounded margin', mp.mpf('3.512607')-mp.mpf('3.512131'))
print('cot^2 pi/5', mp.cot(mp.pi/5)**2, 1+2/mp.sqrt(5))
for k in range(1,5):
    xi=mp.zeta(2,mp.mpf(k)/5)-mp.pi**2/2
    print('xi',k, xi)
print('psi1(1/2)-pi^2/2', mp.zeta(2,0.5)-mp.pi**2/2)
# fixed-point constants of certify_decay_constant.py
S=1<<100
def atanh_series(u):
    q=u*u//S;w=u;t=0
    for j in range(64):t+=w//(2*j+1);w=w*q//S
    return 2*t
def atan_series(u):
    q=u*u//S;w=u;t=0
    for j in range(64):t+=(-1 if j%2 else 1)*(w//(2*j+1));w=w*q//S
    return t
LOG2=atanh_series(S//3); PI=16*atan_series(S//5)-4*atan_series(S//239)
print('LOG2 err units', (mp.mpf(LOG2)-mp.log(2)*S), 'PI err units', mp.mpf(PI)-mp.pi*S)
