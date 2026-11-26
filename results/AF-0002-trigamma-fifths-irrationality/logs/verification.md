# Verification record

Every check performed on this contribution, with enough detail to repeat it. The status values
in `result.toml` are supported by the entries below. The checks were run on 2026-11-25 and
2026-11-26 with Claude Opus 5.5 and Claude Sonnet 5.5 (Anthropic), from fresh temporary copies of
this package; they are AI-internal checks, not independent verification. The five certificate
commands and `compute-constants` were rerun on 2026-11-26 for this revision of the manuscript and
gave the same results up to timings (outputs and `run-summary.txt` updated).

## Environment

| Component | Version |
|---|---|
| Lean toolchain | `leanprover/lean4:v4.34.0-rc1` |
| Mathlib | `f385f9fd18abed332ebcd3df239cb357e264aceb` |
| TeX distribution | TeX Live 2025 (pdfTeX 3.141592653-2.6-1.40.28) |
| Python | 3.12.3, with python-flint 0.9.0, mpmath 1.3.0, SymPy 1.14.0 |
| Operating system | Ubuntu 24.04 (x86_64) |

## Lean build and axiom audit

| Date | Command | Outcome |
|---|---|---|
| 2026-11-26 | `lake build` (in `lean/`, Mathlib build cache of the pinned revision) | passing |
| 2026-11-26 | orphan-module check of `scripts/afm.py lean` | every `.lean` file is imported by the library root |
| 2026-11-26 | `#print axioms AxiomForge.Trigamma.irrational_xi_one_of_estimates` | `[propext, Classical.choice, Quot.sound]` |
| 2026-11-26 | `#print axioms AxiomForge.Trigamma.irrational_xi_two_of_estimates` | `[propext, Classical.choice, Quot.sound]` |
| 2026-11-26 | `#print axioms AxiomForge.Trigamma.irrational_xi_three_of_estimates` | `[propext, Classical.choice, Quot.sound]` |
| 2026-11-26 | `#print axioms AxiomForge.Trigamma.irrational_xi_four_of_estimates` | `[propext, Classical.choice, Quot.sound]` |
| 2026-11-26 | `#print axioms` on all 25 declarations of `lean/theorems.toml` | only `propext`, `Classical.choice`, `Quot.sound` (`lean/AXIOMS.txt`) |
| 2026-11-26 | source scan of `scripts/afm.py check` | no `sorry`, `admit`, `axiom`, `native_decide`, `implemented_by`, `extern` |

The four declarations above prove the main theorem only from explicitly stated hypotheses
(names ending in `_of_estimates`); they are not a formalization of it
(`formalization = "in-preparation"`).

## Manuscript

| Date | Command | Outcome |
|---|---|---|
| 2026-11-26 | `latexmk -pdf main.tex` (in `paper/`, after `latexmk -C`) | 42 pages; no overfull box, no undefined reference or citation; page 1 carries the abstract, the MSC, the keywords, the status row with the word *Preprint* and the short AI disclosure; page 2 the contents |

## Computations

Command: `python3 run_checks.py all` in `experiments/scripts/` (each line below is one
command of `run_checks.py`; its full output is `experiments/outputs/<name>.txt`, and
`experiments/outputs/run-summary.txt` records exit statuses and times). PASS means exit
status 0. Certificate data and their SHA-256 digests: `experiments/README.md`.

| Command (`run_checks.py` name) | Outcome (exit status, time) | Result (last lines of the output) |
|---|---|---|
| `certify-arithmetic-constant` | PASS (exit=0, 95s) | PASS: Lambda < 3.512131 |
| `certify-decay-constant` | PASS (exit=0, 85s) | PASS: D_alternating >= 3.5099, separation gain >= 0.002707, D_separated >= 3.512607 |
| `verify-arithmetic-constant` | PASS (exit=0, 6s) | PASS A < 3.512131 (mode optimal) |
| `verify-decay-constant` | PASS (exit=0, 102s) | ALL DECAY CHECKS PASSED |
| `check-profile-affinity` | PASS (exit=0, 53s) | cells 489 nonaffine/keys problems 0 |
| `compute-constants` | PASS (exit=0, 1s) | LOG2 err units -26.2468172880027886040701599669690092679294359294512503215932 PI err units -8.21495367825316516651126243786210552925959180737013775501845 |
| `check-separation-identity` | PASS (exit=0, 2383s) | == failures: 0 |
| `check-separation-signs` | PASS (exit=0, 1415s) | == failures: 0 |
| `check-polar-bounds` | PASS (exit=0, 2295s) | violations: 0; PASS: no violation of the finite two-layer bound at non-bad primes |
| `check-polar-bounds-deletions` | PASS (exit=0, 54s) | violations: 0; PASS: no violation of the finite two-layer bound at non-bad primes |
| `check-local-bound` | PASS (exit=0, 29s) | h=96 k=4: primes tested 90, violations [], equality at 88, sum e_p log p /h^2 = 2.6957, sum bound log p /h^2 = 2.6983 [6s]; == violations: 0 |
| `find-rational-roots` | PASS (exit=0, 50s) | h=48 k=4 deg=48 rational roots: none [13.1s] |
| `estimate-finite-rates` | PASS (exit=0, 1310s) | 96 4 / 3.41500 2.69567 0.71933 / -3.45147 / -0.03646 / -0.03646   [186s] |

## Reviews

| Date | Kind | Scope | Reviewer | Outcome and open issues |
|---|---|---|---|---|
| 2026-11-25 | Mathematical (internal audit) | the candidate argument and the certificates | Claude Opus 5.5 (AI-internal) | errors found and corrected (see `../CHANGELOG.md`); the steps marked *candidate* in the manuscript are not verified; not an independent review |
| 2026-11-25 | Literature and novelty | prior results on the target values; bibliographic data | Claude Opus 5.5 (AI-internal survey) | sources read directly where possible (Hexagon, arXiv, Crossref, zbMATH Open, Zenodo, GitHub; full Hexagon catalogue); Litsey (Hexagon 2610.00401v3: ψ₁(k/5) − π²/6 treated, ψ₁(k/5) − π²/2 listed in §12.1 as not reached, gap ≈ −0.0014 per h²), Calegari–Dimitrov–Tang (arXiv:2408.15403, ψ₁(n/6)), the Hexagon catalogue, arXiv and Zenodo searches. Outcome: no located source proves the irrationality of any individual ξ_k; ξ_k + ξ_{5−k} is an algebraic multiple of π². Limits: MathSciNet and Google Scholar not searched; some thresholds taken second-hand (marked in the manuscript); absence of evidence is "no proof found", not proof of absence |
| 2026-11-25 | Mathematical (adversarial, AI-internal) | separation identity, Proposition 2.6 and Corollaries 2.7-2.8 | Claude Opus 5.5 | proof found correct; presentation fixes applied (see `../CHANGELOG.md`); tests reproduced by `check_separation_signs.py` except the ball-arithmetic check of the cofactor signs |
| 2026-11-26 | Mathematical (adversarial, AI-internal) | entrywise bounds, Lemma 4.2 and Corollary 4.3 | Claude Opus 5.5 | proof found correct; Corollary 4.3(c) made precise; exact checks reported with no violation in 10,640 comparisons (programs not part of this package) |
| 2026-11-26 | Mathematical (adversarial, AI-internal) | the whole manuscript, its description of earlier results and its finite tests | Claude Fable 5.2 (AI-internal) | a harsh review that found no critical error and no failing step of the chain of estimates; all major findings were fixed (description of earlier results, a claim about the alternating method removed, the number and nature of the bad primes in the finite tests stated exactly, a claim about the profile removed, proofs of two lemmas added); not an independent review |
| — | Statement fidelity (Lean against manuscript) | — | none yet | pending |
| — | Independent human review | — | none | pending; no person has reviewed the mathematics |

AI cross-checks are recorded as such and are not independent reviews.
