"""Run the certificate checkers and the consistency checks.

Every command is run from this directory with the current Python interpreter; its standard
output and error are written to ../runs/<name>.txt, and a summary (command, exit status, time)
to ../runs/run-summary.txt. The exit status is 1 if any command fails.

Stages (see ../README.md for what each command establishes):

  certificates   profile integrals, the six margins with the shift check, the local
                 determinants (a few minutes)
  consistency    exact checks at small sizes (Appendix B); the longest take several minutes
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
OUT = HERE.parent / "runs"

# (a, q, sigma, t, c, nmax): rows of the theorem, h = t n up to 32 (larger sizes are slower).
ROWS = [
    (3, 131, 1, 6, 7, 5), (3, 257, -1, 4, 5, 8),
    (4, 995, 1, 4, 5, 8), (4, 995, -1, 4, 5, 8),
    (5, 829, 1, 4, 5, 8), (5, 1609, -1, 4, 5, 8),
    (8, 12061, 1, 4, 5, 8), (8, 12061, -1, 4, 5, 8),
    (9, 35, -1, 4, 5, 6), (12, 1001, 1, 4, 5, 6),   # extra tests: 9 | a and e = 2 with a0 = 3
]
# primes of the nonvanishing check: (a, q, sigma, t, c, p); h = t p
PRIMES = [(4, 995, 1, 4, 5, 13), (3, 257, -1, 4, 5, 13), (8, 12061, -1, 4, 5, 13)]


def tag(a: int, q: int, s: int) -> str:
    return f"a{a}-q{q}-{'plus' if s > 0 else 'minus'}"


def certificate_commands() -> list[list[tuple[str, list[str]]]]:
    return [[
        ("profile", ["profile.py", "k76", "k54"]),
        ("decay-ball-shift", ["decay_ball.py", "24000", "--shift"]),
        ("local-poly", ["local_poly.py"]),
    ]]


def consistency_commands() -> list[list[tuple[str, list[str]]]]:
    cmds = [("series-identity", ["series_identity.py"])]
    for a, q, s, t, c, n in ROWS:
        cmds.append((f"finite-bounds-{tag(a, q, s)}", ["finite_bounds.py", *map(str, (a, q, s, t, c, 1, n))]))
    for a, q, s, t, c, p in PRIMES:
        cmds.append((f"global-prime-index-{tag(a, q, s)}-p{p}", ["global_prime_index.py", *map(str, (a, q, s, t, c, p))]))
    return [cmds]


def run_one(name: str, argv: list[str]) -> tuple[str, int, float]:
    t0 = time.time()
    with open(OUT / f"{name}.txt", "w") as fh:
        r = subprocess.run([sys.executable, *argv], cwd=HERE, stdout=fh, stderr=subprocess.STDOUT)
    dt = time.time() - t0
    print(f"[{'PASS' if r.returncode == 0 else 'FAIL'}] {name} ({dt:.0f}s)", flush=True)
    return name, r.returncode, dt


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["certificates", "consistency", "all"])
    ap.add_argument("--jobs", type=int, default=4)
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    plan = []
    if args.stage in ("certificates", "all"):
        plan += certificate_commands()
    if args.stage in ("consistency", "all"):
        plan += consistency_commands()
    results = []
    for group in plan:
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            results += list(pool.map(lambda c: run_one(*c), group))
    with open(OUT / "run-summary.txt", "a") as fh:
        for name, code, dt in results:
            fh.write(f"{'PASS' if code == 0 else 'FAIL'}  exit={code}  {dt:8.0f}s  {name}\n")
    failed = [n for n, c, _ in results if c != 0]
    print(f"== {len(results) - len(failed)} passed, {len(failed)} failed" + (f": {failed}" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
