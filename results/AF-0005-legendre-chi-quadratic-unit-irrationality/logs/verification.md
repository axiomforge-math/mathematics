# Verification record

Every check performed on this contribution, with enough detail to repeat it. The status values
in `result.toml` are supported by the entries below. All checks were run on 2026-11-26 with
Claude Sonnet 5.5 (Anthropic), from a fresh temporary copy of this package; the review was made
with Claude Fable 5.2 (Anthropic). They are AI-internal checks, not independent verification.

**Conditionality.** The main theorem is proved only assuming four results of an unrefereed
preprint of Krisman (Hexagon 2611.00265v1): K1 (Theorem 3.7), K2 (Proposition 4.2, for even n
only), K3 (Theorem 5.1, for even h >= 100) and K4 (Lemmas 6.1 and 8.6, for primes l >= 7 with
l not dividing n and l^2 not dividing the denominator). None of them is reproved or recomputed
here beyond the consistency checks below; the Lean development that preprint reports was neither
built nor audited.

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
| 2026-11-26 | `#print axioms AxiomForge.LegendreChi.irrational_unitValue_14_pos_of_estimates` | `[propext, Classical.choice, Quot.sound]` |
| 2026-11-26 | `#print axioms AxiomForge.LegendreChi.irrational_unitValue_14_neg_of_estimates` | `[propext, Classical.choice, Quot.sound]` |
| 2026-11-26 | `#print axioms AxiomForge.LegendreChi.irrational_unitValue_27_pos_of_estimates` | `[propext, Classical.choice, Quot.sound]` |
| 2026-11-26 | `#print axioms AxiomForge.LegendreChi.irrational_unitValue_27_neg_of_estimates` | `[propext, Classical.choice, Quot.sound]` |
| 2026-11-26 | `#print axioms AxiomForge.LegendreChi.irrational_legendreChi_neg_unit_of_estimates` | `[propext, Classical.choice, Quot.sound]` |
| 2026-11-26 | `#print axioms AxiomForge.LegendreChi.irrational_inverseTangentIntegral_neg_unit_of_estimates` | `[propext, Classical.choice, Quot.sound]` |
| 2026-11-26 | `#print axioms` on all 33 declarations of `lean/theorems.toml` | only `propext`, `Classical.choice`, `Quot.sound` (`lean/AXIOMS.txt`) |
| 2026-11-26 | source scan of `scripts/afm.py check` | no `sorry`, `admit`, `axiom`, `native_decide`, `implemented_by`, `extern` |

The conditional declarations above prove the main theorem only from explicitly stated hypotheses
(`PencilEstimates`; names ending in `_of_estimates`); they are not a formalization of it
(`formalization = "in-preparation"`).

## Manuscript

| Date | Command | Outcome |
|---|---|---|
| 2026-11-26 | `latexmk -pdf main.tex` (in `paper/`) | 21 pages; no overfull box, no undefined reference or citation; page 1 carries the abstract, the MSC, the keywords, the status row with the word *Preprint* and the short AI disclosure; page 2 the contents |

## Computations

Command: `python3 run_checks.py all` in `logs/experiments/scripts/` (each line below is one
command of `run_checks.py`; its full output is `logs/experiments/outputs/<name>.txt`, and
`logs/experiments/outputs/run-summary.txt` records exit statuses and times). PASS means exit
status 0. Certificate data and their SHA-256 digests: `logs/experiments/README.md`.

| Command (`run_checks.py` name) | Outcome (exit status, time) | Result (last lines of the output) |
|---|---|---|
| `real-certificates` (`real_certificates.py` on both density files, mesh 1/4000, 192 bits) | PASS (exit=0, 50s) | C(n) + Phi <= -0.011513537 (n=14, +), -0.006270772 (14, -), -0.076370841 (18, +), -0.073219674 (18, -), -0.206838107 (30, +), -0.205714097 (30, -), -0.006763214 (27, +), -0.005376191 (27, -); diagnostics C(n) + J >= +0.076201 (n=10, +), +0.086663 (10, -), +0.012824 (25, +), +0.014445 (25, -); PASS: 8 favourable comparisons (< -1/1000) and 4 diagnostic primal lower bounds (> 0) |
| `arithmetic-checks` | PASS (exit=0, 88s) | series identity at (14,+), (27,-), (7,+), (5,-), h = 6; parity-minor lemma: 4000 random minors, 560 attain the bound; odd-prime entry bounds: 10340 entries, 438 attain the bound; 2-adic regularisation: 1800 checks; exact exponents n_p(h) at or below the finite bounds (7) and (12); PASS: 16418 exact checks |
| `source-sets` | PASS (exit=0, 26s) | exceptional sets recomputed: 47 traces for chi_2 and 57 for Ti_2, equal to the printed sets; 31 new traces for chi_2 and 42 for Ti_2; 16 and 15 traces covered by neither; margins negative for every covered n <= 20000; PASS |

## Reviews

| Date | Kind | Scope | Reviewer | Outcome and open issues |
|---|---|---|---|---|
| 2026-11-26 | Mathematical (adversarial, AI-internal) | numeric audit of the certificates and of the arithmetic checks; adversarial reading of the two new lemmas; dependency check of the imported results against the cited preprint (read in full) | Claude Fable 5.2 (AI-internal) | a harsh review: the theorem is conditional on four imported results, now stated as hypotheses; the two new lemmas were read line by line and no gap was found, one unusable paragraph of the candidate proof was replaced; the certificates were confirmed (the original programs, read and rerun in a scratch copy, reproduce their logs; the separately written Arb code confirms all twelve values); hypotheses of the imported nonvanishing lemma and of the size estimate stated precisely; priority checked against the one available version of the cited preprint and its repository; not an independent review |
| 2026-11-26 | Literature and novelty | prior results on the target values; the cited preprint | Claude Fable 5.2 (AI-internal survey) | the cited preprint (Hexagon 2611.00265v1, the only version) was read; both improvements are stated there as unproved; no other source containing them was found. Limits: MathSciNet and Google Scholar not searched; the priority statement is relative to the sources read, not absolute |
| — | Statement fidelity (Lean against manuscript) | — | none yet | pending |
| — | Independent human review | — | none | pending; no person has reviewed the mathematics |

AI cross-checks are recorded as such and are not independent reviews.
