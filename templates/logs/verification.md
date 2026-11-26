# Verification record

Every check performed on this contribution, with enough detail to repeat it. The status
values in `result.toml` must be supported by an entry here.

## Environment

| Component | Version |
|---|---|
| Lean toolchain | <<LEAN TOOLCHAIN>> |
| Mathlib | <<MATHLIB REV>> |
| TeX distribution | <<TEX VERSION>> |
| Python | <<PYTHON VERSION>> |

## Lean build and axiom audit

| Date | Command | Outcome |
|---|---|---|
| <<YYYY-MM-DD>> | `lake build` | <<OUTCOME>> |
| <<YYYY-MM-DD>> | `#print axioms <<LEAN NAME>>` | <<AXIOMS REPORTED>> |

## Certificates

| Certificate | SHA-256 | Checker command | Outcome |
|---|---|---|---|
| `experiments/certificates/<<FILE>>` | <<SHA256>> | `<<COMMAND>>` | <<OUTCOME>> |

## Reviews

| Date | Kind | Scope | Reviewer | Outcome |
|---|---|---|---|---|
| <<YYYY-MM-DD>> | <<STATEMENT FIDELITY OR MATHEMATICAL OR LITERATURE>> | <<SCOPE>> | <<WHO OR AI SYSTEM>> | <<OUTCOME AND OPEN ISSUES>> |

AI cross-checks are recorded as such and are not independent reviews.
