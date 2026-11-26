# Experiments and certificates

| Directory | Content |
|---|---|
| `scripts/` | programs, named `<verb>_<object>.py` |
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
| `scripts/certify_minus_two_ninths.py` | Exact rational certificates for the negative dilogarithm at -2/9. | original certificate program (assertions; refuses python -O) |
| `scripts/certify_minus_two_sevenths.py` | Exact rational certificates for the negative dilogarithm at -2/7. | original certificate program (assertions; refuses python -O) |
| `scripts/certify_two_elevenths.py` | Exact rational certificates for the 6n-pole, 4n-dimensional Li_2(2/11) proof. | original certificate program (assertions; refuses python -O) |
| `scripts/certify_two_ninths.py` | Exact finite checks for a candidate Li_2(2/9) Hankel family. | original certificate program (assertions; refuses python -O) |
| `scripts/check_discrete_bounds.py` | Finite slot bounds at ordinary primes versus the limiting profile and the exact data. | exact or numerical check (exit 1 on failure); evidence only |
| `scripts/check_exceptional_primes.py` | EXPLORATORY: the exceptional and small-prime finite bounds versus the exact Q_n. | exact or numerical check (exit 1 on failure); evidence only |
| `scripts/check_external_fields.py` | EXPLORATORY (floating point, mpmath): do the closed-form external fields used by the | exact or numerical check (exit 1 on failure); evidence only |
| `scripts/check_irreducibility.py` | Irreducibility over Q of the exact polynomials Q_n(X) (Appendix C, item (b)). | exact or numerical check (exit 1 on failure); evidence only |
| `scripts/check_local_determinants.py` | Third computation of the eight local determinants (manuscript, Table 6 and Appendix A.3). | original program (assertions; refuses python -O) |
| `scripts/check_series_identity.py` | Lemma 2.2 on sample entries (Appendix C, item (a)): Lambda_xi(W x^s) computed from the | exact or numerical check (exit 1 on failure); evidence only |
| `scripts/check_slot_duality.py` | Check the new direct weak-duality certificates against the old greedy values. | original program (assertions; refuses python -O) |
| `scripts/check_valuation_bounds.py` | Compare the actual Gauss valuations of Q_n at ordinary primes with the finite slot | exact or numerical check (exit 1 on failure); evidence only |
| `scripts/compute_bound_sequence.py` | EXPLORATORY: the finite-n sum of the per-prime lower bounds of Sections 3 and 4. | computation |
| `scripts/compute_hankel_polynomials.py` | Compute the exact polynomials Q_n(X) of the enlarged Hankel family (Appendix C). | computation |
| `scripts/define_hankel_family.py` | Exact implementation of the enlarged Hankel family for Li_2(lambda) (manuscript, Section 2). | support module |
| `scripts/define_parameters.py` | Shared definitions of the checkers ``verify_*.py`` (separately written recomputation). | support module |
| `scripts/define_rational_intervals.py` | Exact arithmetic helper functions shared by the certificates. | support module |
| `scripts/estimate_family_rates.py` | EXPLORATORY: finite-n content and value of the exact polynomials Q_n (Appendix C). | exploratory estimate (fits); proves nothing |
| `scripts/generate_local_gram_certificates.py` | Local Gram determinants det H_0, det H_1 and the Lean certificate modules (lean/.../LocalGram). | generator of the Lean certificate modules |
| `scripts/run_checks.py` | Run the certificate programs, the checkers and the exploratory computations. | runs everything |
| `scripts/verify_comparison_bounds.py` | Checker for the comparison-measure bounds (analytic rates), in Arb ball arithmetic. | separately written checker (exact rationals / Arb balls; exit 1 on failure) |
| `scripts/verify_profile_integrals.py` | Checker for the profile integrals: exact value of  int_delta^kappa B(x) dx. | separately written checker (exact rationals / Arb balls; exit 1 on failure) |
| `scripts/verify_rate_comparison.py` | Checker for the arithmetic rates and the final comparison of the rates (Table 2). | separately written checker (exact rationals / Arb balls; exit 1 on failure) |

## Generated data

`run_checks.py exact-data` writes the exact polynomials Q_n of Appendix C to `data/` (not part
of the archive; recomputed in about one hour on four cores). Their SHA-256 digests are
recorded in `outputs/hankel-polynomials-sha256.txt`; the computation is deterministic, so a
rerun reproduces them byte for byte. The certificate stage needs no generated data.
