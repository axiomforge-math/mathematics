# Experiments and certificates

| Directory | Content |
|---|---|
| `scripts/` | programs |
| `certificates/` | certificate data: `comparison_densities.json` (the six step densities and λ) and `local_polynomials.json` (the six integer polynomials) |
| `runs/` | recorded outputs of every command (`run-summary.txt`: exit status and time) |

## Requirements

Python 3.11 or later (the recorded runs used Python 3.12.3) and the packages of
`requirements.txt`: `python-flint==0.9.0`, `mpmath==1.3.0`. Install with
`python3 -m pip install -r requirements.txt`.

## Running

```bash
cd scripts
python3 run_checks.py all          # every command below; outputs go to ../runs/
```

`run_checks.py` lists each command with its arguments. Every program exits with a non-zero status
when a check fails. All programs were written separately from the programs that produced the
candidate certificates and do not import their code. Finite checks support the estimates; they do not
prove them.

## Programs

| Program | Content | Kind |
|---|---|---|
| `scripts/pencil.py` | exact implementation of the functional, the determinant and T | support module |
| `scripts/profile.py` | exact ordinary-prime slot profile and its integrals for κ = 7/6, 5/4 | checker (exact rationals) |
| `scripts/decay_ball.py` | rigorous bounds for B and A and the six margins (Arb), with `--shift` for larger q | checker (Arb balls; exit 1 on failure) |
| `scripts/local_poly.py` | the six local determinants as polynomials against the stored ones, with the domination check | checker (exact; exit 1 on failure) |
| `scripts/series_identity.py` | the pole series against a direct sum (700 digits) | numerical check |
| `scripts/finite_bounds.py` | every local bound of Sections 3–5 against exact Gauss valuations at small sizes | exact consistency check; evidence only |
| `scripts/global_prime_index.py` | the prediction v_p(Δ(0)) = −pt(γ+2−t)+t at h = tp | exact consistency check |
| `scripts/run_checks.py` | runs everything | runs everything |

## Certificate data

| File | SHA-256 |
|---|---|
| `certificates/comparison_densities.json` | `19e3cbab6f95f639f2937780338a9a48c1481938073498e2db846bf61854c959` |
| `certificates/local_polynomials.json` | `8a208ae4b62b31f69c0f23c40adfd3e1e4e02560cf9f0c1c38b30316abaec91e` |
