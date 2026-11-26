# Verification record

Every check performed on this contribution, with enough detail to repeat it. The status values
in `result.toml` are supported by the entries below. The checks were run on 2026-11-25 and 2026-11-26
(the dates are given per entry) with Claude Opus 5.5 and Claude Sonnet 5.5 (Anthropic), from fresh
temporary copies of this package; they are AI-internal checks, not independent verification.
The computations marked 2026-11-26 were rerun for this revision of the manuscript.

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
| 2026-11-26 | `#print axioms AxiomForge.LegendreChi.irrational_legendreChi_two_div_of_estimates` | `[propext, Classical.choice, Quot.sound]` |
| 2026-11-26 | `#print axioms AxiomForge.LegendreChi.irrational_inverseTangentIntegral_two_div_of_estimates` | `[propext, Classical.choice, Quot.sound]` |
| 2026-11-26 | `#print axioms AxiomForge.LegendreChi.irrational_legendreChi_neg_two_div_of_estimates` | `[propext, Classical.choice, Quot.sound]` |
| 2026-11-26 | `#print axioms AxiomForge.LegendreChi.irrational_inverseTangentIntegral_neg_two_div_of_estimates` | `[propext, Classical.choice, Quot.sound]` |
| 2026-11-26 | `#print axioms` on all 29 declarations of `lean/theorems.toml` | only `propext`, `Classical.choice`, `Quot.sound` (`lean/AXIOMS.txt`) |
| 2026-11-26 | source scan of `scripts/afm.py check` | no `sorry`, `admit`, `axiom`, `native_decide`, `implemented_by`, `extern` |

The four declarations above prove the main theorem only from explicitly stated hypotheses
(names ending in `_of_estimates`); they are not a formalization of it
(`formalization = "in-preparation"`).

## Manuscript

| Date | Command | Outcome |
|---|---|---|
| 2026-11-26 | `latexmk -pdf main.tex` (in `paper/`, after `latexmk -C`) | 37 pages; no overfull box, no undefined reference or citation; page 1 carries the abstract, the MSC, the keywords, the status row with the word *Preprint* and the short AI disclosure; page 2 the contents |

## Computations

Command: `python3 run_checks.py all` in `experiments/scripts/` (each line below is one
command of `run_checks.py`; its full output is `experiments/outputs/<name>.txt`, and
`experiments/outputs/run-summary.txt` records exit statuses and times). PASS means exit
status 0. Certificate data and their SHA-256 digests: `experiments/README.md`.

| Command (`run_checks.py` name) | Outcome (exit status, time) | Result (last lines of the output) |
|---|---|---|
| `verify-profile-integrals` | PASS (exit=0, 109s) | PASS: I >= -2113164137/1000000000 = -2.113164137; PASS: I >= -993544791/500000000 = -1.987089582 |
| `verify-comparison-bounds-general-q83` (2026-11-26, repaired verifier) | PASS (exit=0, 30s) | q=83: B <= -3.16170896366, A_- >= -3.15484583292, B - A_- <= -0.006863130746; tail: tau_0 < 0, tau_1 < 0; PASS: B - A_-(q) < 0 certified |
| `verify-comparison-bounds-band-q81` (2026-11-26, repaired verifier) | PASS (exit=0, 33s) | q=81: B <= -3.37417611701, A_- >= -3.36849705145, B - A_- <= -0.005679065551; tail: tau_0 < 0, tau_1 < 0; PASS: B - A_-(q) < 0 certified |
| `verify-local-determinants-general` | PASS (exit=0, 6s) | == PASS: 0 failures |
| `compute-local-blocks-band` | PASS (exit=0, 11s) | == PASS: six nonzero determinants, residues mod 191 as expected |
| `estimate-comparison-bounds` | PASS (exit=0, 103s) | band q=79: E=-2.111531211 int(G-lam)+=0.594231452 C=0.923175761 lam=-7.5821309 B=-3.358961023 A_-=-3.367265987 B-A=0.008305 tail slope=-5.977 tail value=-0.063 |
| `bound-profile-integral` | PASS (exit=0, 110s) | trapezoid upper on [delta, 2kappa]: -1.985656684672533  plus delta for (0,delta): -1.9851566846725328 |
| `check-series-identity` | PASS (exit=0, 45s) | == PASS |
| `check-finite-bounds-general-q83-plus` | PASS (exit=0, 170s) | n=7 h=42 K=49 A=0: failures=[] ; p=2[2] v=-2328 bound=-2358; p=3[Y] v=-1360 bound=-1560; p=5[Y] v=-422 bound=-558; p=17[Y] v=-367 bound=-390; p=41[macro] v=-25 ; == failures: 0 |
| `check-finite-bounds-general-q83-minus` | PASS (exit=0, 188s) | n=7 h=42 K=49 A=0: failures=[] ; p=2[2] v=-2328 bound=-2358; p=41[macro] v=-25 bound=-26; p=43[macro] v=-19 bound=-20; p=61[Y] v=-343 bound=-390; p=83/q: v=574 ; == failures: 0 |
| `check-finite-bounds-band-q81-plus` | PASS (exit=0, 90s) | n=1 h=40 K=49 A=2: failures=[] ; p=2[2] v=-2441 bound=-2462; p=3/q: v=2106 v/(f h^2)=0.3291; p=41[macro] v=-25 bound=-26; p=79[Y] v=-325 bound=-386; p=83[Y] v=-; == failures: 0 |
| `check-finite-bounds-band-q81-minus` | PASS (exit=0, 81s) | n=1 h=40 K=49 A=2: failures=[] ; p=2[2] v=-2441 bound=-2462; p=3/q: v=2106 v/(f h^2)=0.3291; p=5[Y] v=-378 bound=-546; p=13[Y] v=-344 bound=-386; p=41[macro] v=; == failures: 0 |
| `check-prime-index-valuation-q83-minus-p17` | PASS (exit=0, 196s) | q=83 sigma=-1 p=17 h=102: Delta(0) != 0: True; v_p = -300; predicted -300; time 195.2s |
| `check-prime-index-valuation-q83-plus-p19` | PASS (exit=0, 268s) | q=83 sigma=1 p=19 h=114: Delta(0) != 0: True; v_p = -336; predicted -336; time 267.0s |
| `audit-small-sizes-general-q83-plus` | PASS (exit=0, 1165s) | n=10 h=60 K=70 A=0 deg=60 v2=-4816 v2/h^2=-1.3378 vq={83: (1159, 0.3219)} log cont/h^2=-2.8052 log/T(xi)//h^2=-3.1181 log/prim(xi)//h^2=-0.3129 [514.6s] |
| `audit-small-sizes-general-q83-minus` | PASS (exit=0, 232s) | n=7 h=42 K=49 A=0 deg=42 v2=-2328 v2/h^2=-1.3197 vq={83: (574, 0.3254)} log cont/h^2=-2.7622 log/T(xi)//h^2=-3.1133 log/prim(xi)//h^2=-0.3511 [164.7s] |
| `audit-small-sizes-band-q81-plus` | PASS (exit=0, 87s) | n=1 h=40 K=49 A=2 deg=40 v2=-2441 v2/h^2=-1.5256 vq={3: (2106, 1.3162)} log cont/h^2=-2.9776 log/T(xi)//h^2=-3.3766 log/prim(xi)//h^2=-0.3990 [86.5s] |
| `audit-small-sizes-band-q81-minus` | PASS (exit=0, 108s) | n=1 h=40 K=49 A=2 deg=40 v2=-2441 v2/h^2=-1.5256 vq={3: (2106, 1.3162)} log cont/h^2=-2.9279 log/T(xi)//h^2=-3.3791 log/prim(xi)//h^2=-0.4512 [107.3s] |
| `compute-two-adic-valuations` | PASS (exit=0, 2515s) | == failures: 0 |
| `compute-two-adic-square` (2026-11-26; `compute_two_adic_valuations.py --square 83 1 8 16 24 32 40 48 56 64`) | PASS (exit=0, 430s) | exact values of the last table of Appendix B for K = h, A = 0, q = 83, sigma = 1: v2G(Delta) = -66, -287, -663, -1188, -1882, -2700, -3685, -4816 and v2G(T) = -42, -223, -583, -1028, -1722, -2492, -3485, -4432 at h = 8, ..., 64, each at or above the finite bound (-48, ..., -4484); == failures: 0 |
| `verify_comparison_bounds.py` on the general density at q = 81 (2026-11-26; Section 9 of the manuscript; not in `run_checks.py` because it is expected to fail) | exit=1 as expected (output `verify-comparison-bounds-general-q81-upper-bound.txt`) | B - A_- <= +0.005331535681: this density does not certify q = 81 for the general construction |

## Reviews

| Date | Kind | Scope | Reviewer | Outcome and open issues |
|---|---|---|---|---|
| 2026-11-25 | Mathematical (internal audit) | the candidate argument and the certificates | Claude Opus 5.5 (AI-internal) | errors found and corrected (see `../CHANGELOG.md`); the steps marked *candidate* in the manuscript are not verified; not an independent review |
| 2026-11-25 | Literature and novelty | prior results on the target values; bibliographic data | Claude Opus 5.5 (AI-internal survey) | sources read directly where possible (Hexagon, arXiv, Crossref, zbMATH Open, Zenodo, GitHub; full Hexagon catalogue); Krisman (Hexagon 2611.00432v2: χ₂(2/q) for odd q ≥ 175; his §12 estimate), David–Hirata-Kohno–Kawashima (Acta Arith. 2022, threshold as specialised by Krisman), Hata (1990, as reported by Krisman). Outcome: no located source proves χ₂(2/q) irrational for odd 81 ≤ q ≤ 173, or gives an explicit odd q for Ti₂(2/q). Limits: MathSciNet and Google Scholar not searched; some thresholds taken second-hand (marked in the manuscript); absence of evidence is "no proof found", not proof of absence |
| 2026-11-26 | Mathematical (adversarial, AI-internal) | the whole manuscript, its literature statements and its verifier | Claude Fable 5.2 (AI-internal) | a harsh review that found no critical error; all major findings were fixed: literature statements checked against the cited preprint (statements only), statements of the filling lemma and the profile proposition corrected, an unsupported claim removed, the ball-arithmetic verifier repaired (cells whose enclosure straddles zero, tail conditions), reproducibility section rewritten; the revision was made with Claude Sonnet 5.5; not an independent review |
| — | Statement fidelity (Lean against manuscript) | — | none yet | pending |
| — | Independent human review | — | none | pending; no person has reviewed the mathematics |

AI cross-checks are recorded as such and are not independent reviews.
