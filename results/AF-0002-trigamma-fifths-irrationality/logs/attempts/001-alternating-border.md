# 001 · Interleaved border

| | |
|---|---|
| Dates | before 2026-11-25 |
| Outcome | SUPERSEDED |
| Leads to | Section 2 of the manuscript |

## Goal

Prove irrationality of ξ_k with Löwner determinants whose border rows and columns alternate.

## Method

Litsey's framework: two-layer p-adic bounds and a logarithmic-energy bound.

## Result

Falls short by about 0.0014 per h² (numerical estimate reported in the literature).

## Why it failed or what it taught

The separation of the border rows from the border columns gains exactly (log 2)/256 per h² at odd primes, which turns the sign of the comparison.

## Evidence

`experiments/scripts/check_separation_identity.py`, `experiments/outputs/check-separation-identity.txt`
