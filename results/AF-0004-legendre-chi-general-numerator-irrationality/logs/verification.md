# Verification record

Every check performed on this contribution, with enough detail to repeat it. The status values
in `result.toml` are supported by the entries below. All checks were run on 2026-11-26 with
Claude Sonnet 5.5 (Anthropic), from a fresh temporary copy of this package; they are AI-internal
checks, not independent verification.

## Environment

| Component | Version |
|---|---|
| Lean toolchain | `leanprover/lean4:v4.34.0-rc1` |
| Mathlib | `f385f9fd18abed332ebcd3df239cb357e264aceb` |
| TeX distribution | TeX Live 2025 (pdfTeX 3.141592653-2.6-1.40.28) |
| Python | 3.12.3, with python-flint 0.9.0, mpmath 1.3.0 |
| Operating system | Ubuntu 24.04 (x86_64) |

## Lean build and axiom audit

| Date | Command | Outcome |
|---|---|---|
| 2026-11-26 | `lake build` (in `lean/`, Mathlib build cache of the pinned revision) | passing |
| 2026-11-26 | orphan-module check of `scripts/afm.py lean` | every `.lean` file is imported by the library root |
| 2026-11-26 | `#print axioms AxiomForge.LegendreChiGeneral.irrational_legendreChi_div_of_estimates` | `[propext, Classical.choice, Quot.sound]` |
| 2026-11-26 | `#print axioms AxiomForge.LegendreChiGeneral.irrational_inverseTangentIntegral_div_of_estimates` | `[propext, Classical.choice, Quot.sound]` |
| 2026-11-26 | `#print axioms AxiomForge.LegendreChiGeneral.irrational_legendreChi_neg_div_of_estimates` | `[propext, Classical.choice, Quot.sound]` |
| 2026-11-26 | `#print axioms AxiomForge.LegendreChiGeneral.irrational_inverseTangentIntegral_neg_div_of_estimates` | `[propext, Classical.choice, Quot.sound]` |
| 2026-11-26 | `#print axioms` on all 36 declarations of `lean/theorems.toml` | only `propext`, `Classical.choice`, `Quot.sound` (`lean/AXIOMS.txt`) |
| 2026-11-26 | source scan of `scripts/afm.py check` | no `sorry`, `admit`, `axiom`, `native_decide`, `implemented_by`, `extern` |

The four declarations above prove the main theorem only from explicitly stated hypotheses
(names ending in `_of_estimates`); they are not a formalization of it
(`formalization = "in-preparation"`).

## Manuscript

| Date | Command | Outcome |
|---|---|---|
| 2026-11-26 | `latexmk -pdf main.tex` (in `paper/`) | 36 pages; no overfull box, no undefined reference or citation; page 1 carries the abstract, the MSC, the keywords, the status row with the word *Preprint* and the short AI disclosure; page 2 the contents |

## Computations

Command: `python3 run_checks.py all` in `logs/experiments/scripts/` (each line below is one
command of `run_checks.py`; its full output is `logs/experiments/runs/<name>.txt`, and
`logs/experiments/runs/run-summary.txt` records exit statuses and times). PASS means exit
status 0. Certificate data and their SHA-256 digests: `logs/experiments/README.md`. The finite
checks were run here up to h = 32 (h = 24 for the two extra numerators); the sizes up to h = 56
mentioned in Appendix B of the manuscript, and the checks at the primes 17 (h = 68 and h = 102),
were not rerun in this package.

| Command (`run_checks.py` name) | Outcome (exit status, time) | Result (last lines of the output) |
|---|---|---|
| `profile` (`profile.py k76 k54`) | PASS (exit=0, 14s) | I(7/6) = -2.1131641365333835, floor = -2113164137/10^9, equals the stated certificate; I(5/4) = -2.3556398320231233, floor = -2355639833/10^9, equals the stated certificate; ALL PASS |
| `decay-ball-shift` (`decay_ball.py 24000 --shift`) | PASS (exit=0, 61s) | all six margins A - B certified above the required rational bounds (>= 0.013945786, 0.005113500, 0.001699724, 0.001300300, 0.000713481, 0.000758530 per h^2 for (a, q) = (3, 131), (3, 257), (4, 995), (5, 829), (5, 1609), (8, 12061)); for q + 2, q + 12, 2q + 1, 10q + 1, 1000q + 1 with the shifted lambda, B(q) <= B(q0) - log(q/q0)/2 + log(q/q0)/L and margin(q) >= margin(q0) + log(q/q0)/6 hold; ALL PASS |
| `local-poly` (`local_poly.py`) | PASS (exit=0, 1s) | the six local determinants equal the stored integer polynomials (degrees 16, 20, 20 and 6, 9, 9); domination ratios between 0.0004 and 0.0055 at |Q| = 83^2/4; Cauchy bounds 23.18, 136.72, 188.09 and 1.71, 9.37, 5.07, all below 189; ALL PASS |
| `series-identity` (`series_identity.py`) | PASS (exit=0, 4s) | maximum relative error between 1e-664 and 1e-677 for the six rows and both signs of a = 4, 8 |
| `finite-bounds-a3-q131-plus` (`finite_bounds.py`, n = 1 to the largest listed: a = 3, q = 131, sigma = +1, n = 5 (h = 30)) | PASS (exit=0, 11s) | failures=[] at every n; every prime dividing a, q or q^2 - sigma a^2 and the prime 2 tested against the finite form of its bound |
| `finite-bounds-a3-q257-minus` (`finite_bounds.py`, n = 1 to the largest listed: a = 3, q = 257, sigma = -1, n = 8 (h = 32)) | PASS (exit=0, 24s) | failures=[] at every n; every prime dividing a, q or q^2 - sigma a^2 and the prime 2 tested against the finite form of its bound |
| `finite-bounds-a4-q995-plus` (`finite_bounds.py`, n = 1 to the largest listed: a = 4, q = 995, sigma = +1, n = 8 (h = 32)) | PASS (exit=0, 31s) | failures=[] at every n; every prime dividing a, q or q^2 - sigma a^2 and the prime 2 tested against the finite form of its bound |
| `finite-bounds-a4-q995-minus` (`finite_bounds.py`, n = 1 to the largest listed: a = 4, q = 995, sigma = -1, n = 8 (h = 32)) | PASS (exit=0, 30s) | failures=[] at every n; every prime dividing a, q or q^2 - sigma a^2 and the prime 2 tested against the finite form of its bound |
| `finite-bounds-a5-q829-plus` (`finite_bounds.py`, n = 1 to the largest listed: a = 5, q = 829, sigma = +1, n = 8 (h = 32)) | PASS (exit=0, 34s) | failures=[] at every n; every prime dividing a, q or q^2 - sigma a^2 and the prime 2 tested against the finite form of its bound |
| `finite-bounds-a5-q1609-minus` (`finite_bounds.py`, n = 1 to the largest listed: a = 5, q = 1609, sigma = -1, n = 8 (h = 32)) | PASS (exit=0, 42s) | failures=[] at every n; every prime dividing a, q or q^2 - sigma a^2 and the prime 2 tested against the finite form of its bound |
| `finite-bounds-a8-q12061-plus` (`finite_bounds.py`, n = 1 to the largest listed: a = 8, q = 12061, sigma = +1, n = 8 (h = 32)) | PASS (exit=0, 78s) | failures=[] at every n; every prime dividing a, q or q^2 - sigma a^2 and the prime 2 tested against the finite form of its bound |
| `finite-bounds-a8-q12061-minus` (`finite_bounds.py`, n = 1 to the largest listed: a = 8, q = 12061, sigma = -1, n = 8 (h = 32)) | PASS (exit=0, 76s) | failures=[] at every n; every prime dividing a, q or q^2 - sigma a^2 and the prime 2 tested against the finite form of its bound |
| `finite-bounds-a9-q35-minus` (`finite_bounds.py`, n = 1 to the largest listed: extra: a = 9, q = 35, sigma = -1, n = 6 (h = 24)) | PASS (exit=0, 4s) | failures=[] at every n; every prime dividing a, q or q^2 - sigma a^2 and the prime 2 tested against the finite form of its bound |
| `finite-bounds-a12-q1001-plus` (`finite_bounds.py`, n = 1 to the largest listed: extra: a = 12, q = 1001, sigma = +1, n = 6 (h = 24)) | PASS (exit=0, 9s) | failures=[] at every n; every prime dividing a, q or q^2 - sigma a^2 and the prime 2 tested against the finite form of its bound |
| `global-prime-index-a4-q995-plus-p13`, `-a3-q257-minus-p13`, `-a8-q12061-minus-p13` (`global_prime_index.py`, h = 52) | PASS (exit=0, 4-5s each) | Delta(0) != 0 and v_13(Delta(0)) = -152 as predicted by -pt(gamma+2-t)+t, for all three |

## Reviews

| Date | Kind | Scope | Reviewer | Outcome and open issues |
|---|---|---|---|---|
| 2026-11-26 | Mathematical (numeric audit and critical reading, AI-internal) | the six margins, both profile integrals, the six local polynomials, the propagation to larger q, the finite consistency checks, and a line-by-line reading of the new arithmetic lemmas (numerator primes, 2-adic bounds for odd and even a, near-one primes, propagation in q) | Claude Sonnet 5.5 (AI-internal) | the archived exact verifiers were read and rerun in a scratch copy and reproduce their logs (24,960 exact entry-valuation checks, the six strict margins, both profile integrals, the six polynomials byte for byte); a separately written Arb code confirms all six margins; no mathematical gap was found; the parity-minor lemma for derivative columns is the weakest link (candidate); not checked: the ordinary primes at these numerators at finite sizes, literature theorem numbers inherited from the numerator-2 work, the constant q > 54 e^4 a^2 of the literature criterion (second hand); no status is upgraded beyond candidate; not an independent review |
| 2026-11-26 | Literature and novelty | prior results on the target values | Claude Sonnet 5.5 (AI-internal survey) | no explicit smaller thresholds for these numerators were found; the literature range q > 54 e^4 a^2 was not re-derived. Limits: MathSciNet and Google Scholar not searched; absence of evidence is "no proof found", not proof of absence |
| — | Statement fidelity (Lean against manuscript) | — | none yet | pending |
| — | Independent human review | — | none | pending; no person has reviewed the mathematics |

AI cross-checks are recorded as such and are not independent reviews.
