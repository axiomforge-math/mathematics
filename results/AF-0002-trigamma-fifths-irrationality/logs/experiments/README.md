# Experiments and certificates

| Directory | Content |
|---|---|
| `scripts/` | programs, named `<verb>_<object>.py` |
| `certificates/` | certificate data, named `<target>-<quantity>.json` |
| `outputs/` | recorded outputs of every command (`run-summary.txt`: exit status and time) |

## Requirements

Python 3.11 or later (the recorded runs used Python 3.12.3) and the packages of
`requirements.txt`: `python-flint==0.9.0`, `mpmath==1.3.0`, `sympy==1.14.0`. Install with
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
| `scripts/certify_arithmetic_constant.py` | Exact rational integration, independent finite tests of the polar digit | original certificate program (assertions; refuses python -O) |
| `scripts/certify_decay_constant.py` | Rational/fixed-point certificate. No floating-point calculations are used | original certificate program (assertions; refuses python -O) |
| `scripts/check_local_bound.py` | Finite test of the two-layer local bound (manuscript, Appendix A.4(a)). | exact or numerical check (exit 1 on failure); evidence only |
| `scripts/check_polar_bounds.py` | Finite-h test of the two-layer polar valuation bound (Lemma 4.5, Proposition 4.8; Appendix A.4(b)). | exact or numerical check (exit 1 on failure); evidence only |
| `scripts/check_profile_affinity.py` | Affinity of the profile candidates on every cell (manuscript, Appendix A.3). | exact or numerical check (exit 1 on failure); evidence only |
| `scripts/check_separation_case.py` | Exact separation identity for h = 64 and given k and deletions (manuscript, Remark 2.10). | exact or numerical check (exit 1 on failure); evidence only |
| `scripts/check_separation_identity.py` | Audit of the separated-border identity and its 2-adic consequences. | exact or numerical check (exit 1 on failure); evidence only |
| `scripts/check_separation_signs.py` | Exact tests of the separation identity beyond the 48 cases of check_separation_identity.py. | exact or numerical check (exit 1 on failure); evidence only |
| `scripts/compute_constants.py` | Closed form of I(nu), the separation gain, the margins and xi_k (mpmath, 60 digits), and the | computation |
| `scripts/compute_polar_geometry.py` | Two-layer polar bound and contour diagnostic for arbitrary finite block geometry. | support module |
| `scripts/compute_separated_pencils.py` | Fast exact Löwner pencils P_I(X) = det(Phi(X)) via a Schur complement and a characteristic polynomial. | computation |
| `scripts/define_exact_arithmetic.py` | Exact arithmetic helpers: p-adic valuations, rational content, Gauss valuations, primes | support module |
| `scripts/define_lowner_family.py` | Independent exact implementation of the Löwner pencils for psi_1(k/5) - pi^2/2. | support module |
| `scripts/estimate_finite_rates.py` | Exploratory (NOT a certificate): finite-h trends of the separated pencil P_sep(X). | exploratory estimate (floating point or fits); proves nothing |
| `scripts/find_rational_roots.py` | Rational roots of the separated Löwner pencil P_sep(X) (Remark 3.6; numerical evidence only). | exact factorisation; evidence only |
| `scripts/integrate_polar_profile.py` | Two-layer polar-rank bound. exact=True integrates the piecewise affine minimum | support module |
| `scripts/integrate_separated_profile.py` | Exact local-rank integration for piecewise constant row/column roles. | support module |
| `scripts/run_checks.py` | Run the original certificate programs, the checkers and the exploratory computations. | runs everything |
| `scripts/verify_arithmetic_constant.py` | Checker for the arithmetic constant A (manuscript, Definition 4.12, Proposition 4.13, Appendix A). | separately written checker (exact rationals / Arb balls; exit 1 on failure) |
| `scripts/verify_decay_constant.py` | Checker for the decay constant (manuscript, Proposition 5.10, Appendices B-D), in Arb: | separately written checker (exact rationals / Arb balls; exit 1 on failure) |

## Certificate data

| File | SHA-256 |
|---|---|
| `certificates/decay-trial-measure.json` | `a4da00b3a51e1d414b8f1bf30a1a59d9f3334f27d35c6e5acf3e4b520a1c499c` |
