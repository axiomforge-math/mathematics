"""Affinity of the profile candidates on every cell (manuscript, Appendix A.3).

For each kappa and each cell of the original exact integration (c = 1/8, cut 1/20), evaluate the
candidate functions of integrate_polar_profile.branches at three further points and compare them with the affine
function reconstructed from the points 1/3 and 2/3 of the cell, as the original program does.

Usage: python check_profile_affinity.py
Expected output: "cells 489 nonaffine/keys problems 0". Exit status 1 on any problem.
"""
import sys
from fractions import Fraction as F
from integrate_polar_profile import branches
c=F(1,8); cut=F(1,20); N=1+c; top=5*N
bad=0; cells=0; total=F(0)
for kap in [F(j,5) for j in range(1,5)]:
    cuts={cut,top}
    for u in (F(1),N):
        for j in range(int(u/cut)+1):
            for z in (F(0),kap,F(1,2)):
                if j+z and cut<u/(j+z)<top: cuts.add(u/(j+z))
    for j in range(1,int(c/cut)+1):
        if cut<c/j<top: cuts.add(c/j)
    cuts=sorted(cuts)
    for l,r in zip(cuts,cuts[1:]):
        cells+=1
        u=(2*l+r)/3; v=(l+2*r)/3
        B=branches(c,kap,u); C=branches(c,kap,v)
        for t in (F(1,11),F(1,2),F(9,10)):
            x=l+(r-l)*t; X=branches(c,kap,x)
            if X.keys()!=B.keys(): bad+=1; print('keys differ',kap,l,r,t); continue
            for key in B:
                pred=B[key]+(C[key]-B[key])*(x-u)/(v-u)
                if pred!=X[key]: bad+=1; print('nonaffine',kap,float(l),float(r),key)
print('cells',cells,'nonaffine/keys problems',bad)
sys.exit(1 if bad else 0)
