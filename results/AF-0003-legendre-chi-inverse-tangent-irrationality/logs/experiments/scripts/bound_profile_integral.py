"""Upper (one-sided trapezoid) bound for the exact profile integral, band geometry, and
the small-x bound B <= 1 on (0, delta) (manuscript, Section 9; not used in the proof).
Uses the frozen-type evaluation of verify_profile_integrals.py.

Usage: python bound_profile_integral.py"""
import sys
from fractions import Fraction as F
from verify_profile_integrals import breakpoints, B_frozen
kap, alp, cut = F(49, 40), F(1, 20), F(1, 2000)
ends = breakpoints(kap, alp, cut)
up = F(0)
for a, b in zip(ends, ends[1:]):
    m = (a + b) / 2
    up += (b - a) * (B_frozen(kap, alp, m, a) + B_frozen(kap, alp, m, b)) / 2
print('trapezoid upper on [delta, 2kappa]:', float(up), ' plus delta for (0,delta):', float(up + cut))
