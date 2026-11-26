"""Run the certificate checkers and the exact consistency checks.

Every command is run from this directory with the current Python interpreter; its standard
output and error are written to ../outputs/<name>.txt, and a summary (command, exit status,
time) to ../outputs/run-summary.txt. The exit status is 1 if any command fails.

  python run_checks.py all [--jobs N]

The commands are:
  real-certificates   Arb verification of the dual certificates at n = 14, 18, 30, 27 (both signs),
                      with the primal diagnostics at n = 10, 25 (mesh 1/4000)
  arithmetic-checks   exact checks of the pencil, the entry bounds, the regularisation, the
                      parity minors and the exact exponents
  source-sets         the exceptional sets of the cited preprint and the list of new arguments
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
EVEN = "../certificates/even-trace-comparison-densities.json"
ODD = "../certificates/odd-trace-comparison-densities.json"

COMMANDS = [
    ("real-certificates", ["real_certificates.py", EVEN, ODD, "4000"]),
    ("arithmetic-checks", ["arithmetic_checks.py"]),
    ("source-sets", ["source_sets.py"]),
]


def run_one(name: str, argv: list[str]) -> tuple[str, int, float]:
    t0 = time.time()
    with open(OUT / f"{name}.txt", "w") as fh:
        r = subprocess.run([sys.executable, *argv], cwd=HERE, stdout=fh, stderr=subprocess.STDOUT)
    dt = time.time() - t0
    print(f"[{'PASS' if r.returncode == 0 else 'FAIL'}] {name} ({dt:.0f}s)", flush=True)
    return name, r.returncode, dt


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["all"])
    ap.add_argument("--jobs", type=int, default=3)
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        results = list(pool.map(lambda c: run_one(*c), COMMANDS))
    with open(OUT / "run-summary.txt", "a") as fh:
        for name, code, dt in results:
            fh.write(f"{'PASS' if code == 0 else 'FAIL'}  exit={code}  {dt:8.0f}s  {name}\n")
    failed = [n for n, c, _ in results if c != 0]
    print(f"== {len(results) - len(failed)} passed, {len(failed)} failed" + (f": {failed}" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
