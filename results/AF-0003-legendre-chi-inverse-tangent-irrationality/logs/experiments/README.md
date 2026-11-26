# Experiments and certificates

| Directory | Content |
|---|---|
| `scripts/` | programs, named `<verb>_<object>.py` |
| `certificates/` | certificate data, named `<target>-<quantity>.json` |
| `outputs/` | recorded outputs of every command (`run-summary.txt`: exit status and time) |

## Requirements

Python 3.11 or later (the recorded runs used Python 3.12.3) and the packages of
`requirements.txt`: `python-flint==0.9.0`, `mpmath==1.3.0`. Install with
`python3 -m pip install -r requirements.txt`.

## Running

```bash
cd scripts
python3 run_checks.py all          # every command below; outputs go to ../outputs/
```

`run_checks.py` lists each command with its arguments; `python3 run_checks.py --help` shows
the stages. Every program exits with a non-zero status when a check fails. The programs
called *original* are the certificate programs that accompanied the original candidate
proof; the checkers (`verify_*.py`) were written separately from them, from the definitions
in the manuscript. Floating-point and fitted values are numerical evidence only.

## Programs

| Program | Content (first line of its documentation) | Kind |
|---|---|---|
| `scripts/audit_small_sizes.py` | Audit of the half-integer pencils at small sizes. | exact data at small sizes; evidence only |
| `scripts/bound_profile_integral.py` | Upper (one-sided trapezoid) bound for the exact profile integral, band geometry, and | upper bound (Section 9, not used in the proof) |
| `scripts/check_finite_bounds.py` | Usage: check_finite_bounds.py Q SIGMA {general|band} N0 N1 | exact or numerical check (exit 1 on failure); evidence only |
| `scripts/check_prime_index_valuation.py` | Usage: check_prime_index_valuation.py Q SIGMA P | exact or numerical check (exit 1 on failure); evidence only |
| `scripts/check_series_identity.py` | Direct check of mu_xi(phi u^s) = sum_{m>=1} w^m (phi u^s)'(m) for both constructions, | exact or numerical check (exit 1 on failure); evidence only |
| `scripts/compute_local_blocks.py` | Computation of the local (residue-class) Hankel blocks (manuscript, Section 7, Appendix A.3). | computation |
| `scripts/compute_two_adic_valuations.py` | 2-adic Gauss valuation of T(X) for the general construction (q = 83, sigma = +1) against the finite bound of the prime-2 theorem; with `--square Q SIGMA H ...`, the same for the square construction K = h, A = 0 (Appendix B, last table) | computation |
| `scripts/define_exact_arithmetic.py` | Exact arithmetic helpers: p-adic valuations, rational content, Gauss valuations, primes | support module |
| `scripts/define_half_integer_pencils.py` | Exact implementation of the half-integer pencils for chi_2(2/q), Ti_2(2/q). | support module |
| `scripts/estimate_comparison_bounds.py` | Independent floating-point recomputation of the archimedean bound | exploratory estimate (floating point or fits); proves nothing |
| `scripts/run_checks.py` | Run the certificate checkers and the exploratory computations. | runs everything |
| `scripts/verify_comparison_bounds.py` | Rigorous ball-arithmetic (Arb) upper bound for the archimedean exponent B and lower bound for A_-(q), including the tail conditions of Lemma 6.2 and the upper end of every cell not certainly negative | separately written checker (exact rationals / Arb balls; exit 1 on failure) |
| `scripts/verify_local_determinants.py` | 6x6 local determinants of the general construction as polynomials (manuscript, | separately written checker (exact rationals / Arb balls; exit 1 on failure) |
| `scripts/verify_profile_integrals.py` | Exact evaluation of the ordinary-prime slot profile B(x) and of its integral | separately written checker (exact rationals / Arb balls; exit 1 on failure) |

## Certificate data

| File | SHA-256 |
|---|---|
| `certificates/band-construction-comparison-density.json` | `66814ff32785de13223ffb637e485466dee6a0eb6449bbbf2585bde24c87b113` |
| `certificates/general-construction-comparison-density.json` | `fdaf68bb503b2a50f6c545ad14b26f1ac5e9d98ded01a9f2736380c4d2320f15` |
| `certificates/general-construction-local-polynomials.json` | `1f73ae29a0164324e9b93e27c6a5f5924bc5fb7482fe280509a439003bb9caa2` |
