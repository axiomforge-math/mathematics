"""Run the original certificate programs, the checkers and the exploratory computations.

Every command is run from this directory with the current Python interpreter; its standard
output and error are written to ../outputs/<name>.txt, and a summary (command, exit status,
time) to ../outputs/run-summary.txt. The exit status is 1 if any command fails.

Stages (see ../README.md for what each command establishes):

  certificates   original certificate programs and the separately written checkers
                 (about 10 minutes)
  exploratory    exact finite tests of the separation identity, the local bounds and the
                 nonvanishing (about 1.5 hours on four cores)
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
TRIAL = "../certificates/decay-trial-measure.json"


def certificate_commands() -> list[list[tuple[str, list[str]]]]:
    """Groups of (name, argv); the groups run in order, the commands of a group in parallel."""
    return [[
        ("certify-arithmetic-constant", ["certify_arithmetic_constant.py"]),
        ("certify-decay-constant", ["certify_decay_constant.py"]),
        ("verify-arithmetic-constant", ["verify_arithmetic_constant.py", "both"]),
        ("verify-decay-constant", ["verify_decay_constant.py", TRIAL, "1/1000000", "1/1000000"]),
        ("check-profile-affinity", ["check_profile_affinity.py"]),
        ("compute-constants", ["compute_constants.py"]),
    ]]


def exploratory_commands() -> list[list[tuple[str, list[str]]]]:
    return [[
        ("check-separation-identity", ["check_separation_identity.py", "64"]),
        ("check-separation-signs", ["check_separation_signs.py"]),
        ("check-polar-bounds", ["check_polar_bounds.py", "16", "32", "48", "64", "80", "96", "128"]),
        ("check-polar-bounds-deletions", ["check_polar_bounds.py", "--deletions", "32", "48"]),
        ("check-local-bound", ["check_local_bound.py", "32,48,64,96"]),
        ("find-rational-roots", ["find_rational_roots.py", "48"]),
        ("estimate-finite-rates", ["estimate_finite_rates.py", "16", "32", "48", "64", "80", "96"]),
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
