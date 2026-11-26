"""Run the certificate programs, the checkers and the exploratory computations.

Every command is run from this directory with the current Python interpreter; its standard
output and error are written to ../outputs/<name>.txt, and a summary (command, exit status,
time) to ../outputs/run-summary.txt. The exit status is 1 if any command fails.

Stages (see ../README.md for what each command establishes):

  certificates   original certificate programs and the separately written checkers
                 (about 15 minutes on one core)
  exact-data     compute the exact polynomials Q_n in the ranges of Appendix C (about one
                 hour on four cores), record their SHA-256 digests, then run the
                 exploratory checks that use them
  exploratory    the exploratory checks that need no stored polynomial
  all            the three stages above

Usage: python run_checks.py STAGE [--jobs N]
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "outputs"
CASES = {"2/11": "two-elevenths", "2/9": "two-ninths", "-2/9": "minus-two-ninths", "-2/7": "minus-two-sevenths"}
# Ranges of n of Appendix C.
NMAX = {"2/11": 19, "2/9": 11, "-2/9": 19, "-2/7": 16}


def certificate_commands() -> list[list[tuple[str, list[str]]]]:
    """Groups of (name, argv); the groups run in order, the commands of a group in parallel."""
    first = [
        ("certify-two-elevenths", ["certify_two_elevenths.py"]),
        ("certify-two-ninths", ["certify_two_ninths.py"]),
        ("certify-minus-two-ninths", ["certify_minus_two_ninths.py"]),
        ("certify-minus-two-sevenths", ["certify_minus_two_sevenths.py"]),
        ("check-local-determinants", ["check_local_determinants.py"]),
        ("generate-local-gram-certificates", ["generate_local_gram_certificates.py"]),
        ("check-slot-duality", ["check_slot_duality.py"]),
        ("verify-profile-integrals", ["verify_profile_integrals.py", "all"]),
    ]
    for case, slug in CASES.items():
        first.append((f"verify-comparison-bounds-{slug}", ["verify_comparison_bounds.py", case, "2000"]))
        first.append((f"verify-comparison-bounds-{slug}-mesh6000", ["verify_comparison_bounds.py", case, "6000"]))
    return [first, [("verify-rate-comparison", ["verify_rate_comparison.py"])]]


def exploratory_commands() -> list[list[tuple[str, list[str]]]]:
    return [[("check-external-fields", ["check_external_fields.py"]),
             ("check-series-identity", ["check_series_identity.py"])]]


def exact_data_commands() -> list[list[tuple[str, list[str]]]]:
    compute = [(f"compute-hankel-polynomials-{slug}", ["compute_hankel_polynomials.py", case, "1", str(NMAX[case])])
               for case, slug in CASES.items()]
    analyse = [("check-exceptional-primes", ["check_exceptional_primes.py"]),
               ("estimate-family-rates", ["estimate_family_rates.py"]),
               ("check-irreducibility", ["check_irreducibility.py", *CASES])]
    for case, slug in CASES.items():
        analyse.append((f"check-discrete-bounds-{slug}", ["check_discrete_bounds.py", case, "25", "50", "100", "200"]))
        analyse.append((f"compute-bound-sequence-{slug}",
                        ["compute_bound_sequence.py", case, "10", "30", "100", "300", "1000"]))
    return [compute, analyse]


def run_one(name: str, argv: list[str]) -> tuple[str, int, float]:
    t0 = time.time()
    with open(OUT / f"{name}.txt", "w") as fh:
        r = subprocess.run([sys.executable, *argv], cwd=HERE, stdout=fh, stderr=subprocess.STDOUT)
    dt = time.time() - t0
    print(f"[{'PASS' if r.returncode == 0 else 'FAIL'}] {name} ({dt:.0f}s)", flush=True)
    return name, r.returncode, dt


def record_digests() -> None:
    from define_hankel_family import DATA_DIR  # noqa: PLC0415

    lines = []
    for slug in CASES.values():
        for f in sorted((DATA_DIR / slug).glob("Q_*.json")):
            lines.append(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {slug}/{f.name}")
    (OUT / "hankel-polynomials-sha256.txt").write_text("\n".join(lines) + "\n")
    print(f"recorded {len(lines)} SHA-256 digests", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["certificates", "exact-data", "exploratory", "all"])
    ap.add_argument("--jobs", type=int, default=4)
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    plan = []
    if args.stage in ("certificates", "all"):
        plan += certificate_commands()
    if args.stage in ("exploratory", "all"):
        plan += exploratory_commands()
    if args.stage in ("exact-data", "all"):
        data = exact_data_commands()
        plan += [data[0], "digests", data[1]]
    results = []
    for group in plan:
        if group == "digests":
            record_digests()
            continue
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
