# Experiments and certificates

<!-- Template version 1.0.0. Replace every <<...>> token. Delete this comment. -->

| Directory | Content |
|---|---|
| `scripts/` | programs, named `<verb>_<object>.py` (for example `verify_arithmetic_profile.py`) |
| `certificates/` | certificate files, named `<target>-<quantity>.json` |
| `outputs/` | recorded outputs of exploratory computations (optional) |

## Requirements

<<PYTHON VERSION AND PACKAGES WITH EXACT VERSIONS OR PYTHON STANDARD LIBRARY ONLY>>

## Certificates

Each certificate supports a named statement of the manuscript. Its checker is separate
from the program that generated it, uses exact or rigorous interval arithmetic, and exits
with a non-zero status on failure (no `assert`-only checks).

| Certificate | Supports | Checker | Command | Expected output |
|---|---|---|---|---|
| `certificates/<<FILE>>` | <<MANUSCRIPT LABEL>> | `scripts/<<CHECKER>>` | `python3 scripts/<<CHECKER>> certificates/<<FILE>>` | <<OUTPUT>> |

## Exploratory computations

Numerical evidence only: these computations guided the research and prove nothing.

| Script | Purpose | Command | Recorded output |
|---|---|---|---|
| `scripts/<<SCRIPT>>` | <<PURPOSE>> | `<<COMMAND>>` | `outputs/<<FILE>>` |
