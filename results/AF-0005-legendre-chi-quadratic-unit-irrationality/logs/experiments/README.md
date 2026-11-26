# Experiments and certificates

| Directory | Content |
|---|---|
| `scripts/` | programs |
| `certificates/` | the step densities (`even-trace-comparison-densities.json`, `odd-trace-comparison-densities.json`) |
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

All programs were written separately from the programs that produced the candidate certificates
and do not import their code. Every program exits with a non-zero status when a check fails. The
imported results of the cited preprint are not recomputed beyond the consistency checks listed in
`verification.md`.

## Programs

| Program | Content | Kind |
|---|---|---|
| `scripts/real_certificates.py` | Arb verification of the dual certificates at n = 14, 18, 30, 27 (both signs) and the primal diagnostics at n = 10, 25 | checker (Arb balls; exit 1 on failure) |
| `scripts/arithmetic_checks.py` | exact checks of the pencil, the entry bounds, the finite regularisation, the parity minors and the exact exponents | exact checks (exit 1 on failure) |
| `scripts/source_sets.py` | exceptional sets of the cited preprint from its own constants; the list of new arguments | Arb check (exit 1 on mismatch) |
| `scripts/run_checks.py` | runs everything | runs everything |

## Certificate data

| File | SHA-256 |
|---|---|
| `certificates/even-trace-comparison-densities.json` | `3cc2ff8218866df4c7ace311ddf4d594d9ab7883d87d8720ce1bfd6616e6f6a0` |
| `certificates/odd-trace-comparison-densities.json` | `71ac567222f361dcdd0a86913d48615f548b010d40b3e683c35fdb66300f3ade` |
