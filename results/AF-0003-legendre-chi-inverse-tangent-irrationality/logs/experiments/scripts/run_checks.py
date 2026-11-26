"""Run the certificate checkers and the exploratory computations.

Every command is run from this directory with the current Python interpreter; its standard
output and error are written to ../outputs/<name>.txt, and a summary (command, exit status,
time) to ../outputs/run-summary.txt. The exit status is 1 if any command fails.

Stages (see ../README.md for what each command establishes):

  certificates   the checkers of the certificates (a few minutes)
  exploratory    exact consistency checks at small sizes (Appendix B); the 2-adic
                 valuations up to h = 72 take more than an hour
  all            both stages

Usage: python run_checks.py STAGE [--jobs N]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "outputs"
GEN = "../certificates/general-construction-comparison-density.json"
BAND = "../certificates/band-construction-comparison-density.json"
POLY = "../certificates/general-construction-local-polynomials.json"


def certificate_commands() -> list[list[tuple[str, list[str]]]]:
    """Groups of (name, argv); the groups run in order, the commands of a group in parallel."""
    return [[
        ("verify-profile-integrals", ["verify_profile_integrals.py", "k1", "k76", "band"]),
        ("verify-comparison-bounds-general-q83",
         ["verify_comparison_bounds.py", GEN, "83", "7", "6", "0", "1", "-2113164137", "1000000000", "-140", "99", "24000"]),
        ("verify-comparison-bounds-band-q81",
         ["verify_comparison_bounds.py", BAND, "81", "49", "40", "1", "20", "-993544791", "500000000", "-1847", "1100", "24000"]),
        ("verify-local-determinants-general", ["verify_local_determinants.py", POLY]),
        ("compute-local-blocks-band", ["compute_local_blocks.py", "band"]),
        ("estimate-comparison-bounds", ["estimate_comparison_bounds.py"]),
        ("bound-profile-integral", ["bound_profile_integral.py"]),
    ]]


def exploratory_commands() -> list[list[tuple[str, list[str]]]]:
    return [[
        ("check-series-identity", ["check_series_identity.py"]),
        ("check-finite-bounds-general-q83-plus", ["check_finite_bounds.py", "83", "1", "general", "1", "7"]),
        ("check-finite-bounds-general-q83-minus", ["check_finite_bounds.py", "83", "-1", "general", "1", "7"]),
        ("check-finite-bounds-band-q81-plus", ["check_finite_bounds.py", "81", "1", "band", "1", "1"]),
        ("check-finite-bounds-band-q81-minus", ["check_finite_bounds.py", "81", "-1", "band", "1", "1"]),
        ("check-prime-index-valuation-q83-minus-p17", ["check_prime_index_valuation.py", "83", "-1", "17"]),
        ("check-prime-index-valuation-q83-plus-p19", ["check_prime_index_valuation.py", "83", "1", "19"]),
        ("audit-small-sizes-general-q83-plus", ["audit_small_sizes.py", "83", "1", "general", "10"]),
        ("audit-small-sizes-general-q83-minus", ["audit_small_sizes.py", "83", "-1", "general", "7"]),
        ("audit-small-sizes-band-q81-plus", ["audit_small_sizes.py", "81", "1", "band", "1"]),
        ("audit-small-sizes-band-q81-minus", ["audit_small_sizes.py", "81", "-1", "band", "1"]),
        ("compute-two-adic-valuations", ["compute_two_adic_valuations.py", "1", "12"]),
        ("compute-two-adic-square", ["compute_two_adic_valuations.py", "--square", "83", "1",
                                     "8", "16", "24", "32", "40", "48", "56", "64"]),
    ]]


def run_one(name: str, argv: list[str]) -> tuple[str, int, float]:
    t0 = time.time()
    with open(OUT / f"{name}.txt", "w") as fh:
        r = subprocess.run([sys.executable, *argv], cwd=HERE, stdout=fh, stderr=subprocess.STDOUT)
    dt = time.time() - t0
    print(f"[{'PASS' if r.returncode == 0 else 'FAIL'}] {name} ({dt:.0f}s)", flush=True)
    return name, r.returncode, dt


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["certificates", "exploratory", "all"])
    ap.add_argument("--jobs", type=int, default=4)
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    plan = []
    if args.stage in ("certificates", "all"):
        plan += certificate_commands()
    if args.stage in ("exploratory", "all"):
        plan += exploratory_commands()
    results = []
    for group in plan:
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            results += list(pool.map(lambda c: run_one(*c), group))
    summary = OUT / "run-summary.txt"
    with open(summary, "a") as fh:
        for name, code, dt in results:
            fh.write(f"{'PASS' if code == 0 else 'FAIL'}  exit={code}  {dt:8.0f}s  {name}\n")
    failed = [n for n, c, _ in results if c != 0]
    print(f"== {len(results) - len(failed)} passed, {len(failed)} failed" + (f": {failed}" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
