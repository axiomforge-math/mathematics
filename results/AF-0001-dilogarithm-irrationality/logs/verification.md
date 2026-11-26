# Verification record

Every check performed on this contribution, with enough detail to repeat it. The status values
in `result.toml` are supported by the entries below. The checks were run on 2026-11-25 and
2026-11-26 with Claude Opus 5.5 and Claude Sonnet 5.5 (Anthropic), from fresh temporary copies of
this package; they are AI-internal checks, not independent verification. The certificate and
exploratory stages of `run_checks.py` were rerun on 2026-11-26 for this revision of the manuscript
and all passed (the recorded outputs in `logs/experiments/outputs/` are those of the first run; later outputs differ only in timings); the exact computation of the polynomials Q_n (stage `exact-data`, about
one hour) was not rerun: its recorded outputs are those of 2026-11-25.

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
| 2026-11-26 | `#print axioms AxiomForge.Dilogarithm.irrational_dilog_two_elevenths_of_estimates` | `[propext, Classical.choice, Quot.sound]` |
| 2026-11-26 | `#print axioms AxiomForge.Dilogarithm.irrational_dilog_two_ninths_of_estimates` | `[propext, Classical.choice, Quot.sound]` |
| 2026-11-26 | `#print axioms AxiomForge.Dilogarithm.irrational_dilog_neg_two_ninths_of_estimates` | `[propext, Classical.choice, Quot.sound]` |
| 2026-11-26 | `#print axioms AxiomForge.Dilogarithm.irrational_dilog_neg_two_sevenths_of_estimates` | `[propext, Classical.choice, Quot.sound]` |
| 2026-11-26 | `#print axioms` on all 37 declarations of `lean/theorems.toml` | only `propext`, `Classical.choice`, `Quot.sound` (`lean/AXIOMS.txt`) |
| 2026-11-26 | source scan of `scripts/afm.py check` | no `sorry`, `admit`, `axiom`, `native_decide`, `implemented_by`, `extern` |

The four declarations above prove the main theorem only from explicitly stated hypotheses
(names ending in `_of_estimates`); they are not a formalization of it
(`formalization = "in-preparation"`).

## Manuscript

| Date | Command | Outcome |
|---|---|---|
| 2026-11-26 | `latexmk -pdf main.tex` (in `paper/`, after `latexmk -C`) | 45 pages; no overfull box, no undefined reference or citation; page 1 carries the abstract, the MSC, the keywords, the status row with the word *Preprint* and the short AI disclosure; page 2 the contents |

## Computations

Command: `python3 run_checks.py all` in `experiments/scripts/` (each line below is one
command of `run_checks.py`; its full output is `experiments/outputs/<name>.txt`, and
`experiments/outputs/run-summary.txt` records exit statuses and times). PASS means exit
status 0. Certificate data and their SHA-256 digests: `experiments/README.md`.

| Command (`run_checks.py` name) | Outcome (exit status, time) | Result (last lines of the output) |
|---|---|---|
| `check-local-determinants` | PASS (exit=0, 0s) | MinusTwoSeven zero: exact LU identity, both triangles, unit lower diagonal, determinant 17800469908791563702231968746821382359/495898225920000000 verified |
| `certify-two-elevenths` | PASS (exit=0, 11s) | All exact rational assertions passed. |
| `generate-local-gram-certificates` | PASS (exit=0, 15s) | wrote outputs/local-gram-certificates.json; failures: 0 |
| `check-slot-duality` | PASS (exit=0, 18s) | -2/7: 1799 intervals; every dual value equals the previous greedy value exactly; lower bound 0.07694503668343355 |
| `verify-comparison-bounds-two-elevenths` | PASS (exit=0, 8s) | == energy certificate 2/11: 8 passed, 0 failed == |
| `certify-two-ninths` | PASS (exit=0, 29s) | All finite exact certificates passed. |
| `verify-comparison-bounds-two-ninths` | PASS (exit=0, 11s) | == energy certificate 2/9: 6 passed, 0 failed == |
| `verify-comparison-bounds-two-elevenths-mesh6000` | PASS (exit=0, 24s) | == energy certificate 2/11: 8 passed, 0 failed == |
| `verify-comparison-bounds-minus-two-ninths` | PASS (exit=0, 11s) | == energy certificate -2/9: 10 passed, 0 failed == |
| `verify-comparison-bounds-minus-two-sevenths` | PASS (exit=0, 11s) | == energy certificate -2/7: 10 passed, 0 failed == |
| `verify-comparison-bounds-two-ninths-mesh6000` | PASS (exit=0, 28s) | == energy certificate 2/9: 6 passed, 0 failed == |
| `verify-comparison-bounds-minus-two-ninths-mesh6000` | PASS (exit=0, 25s) | == energy certificate -2/9: 10 passed, 0 failed == |
| `verify-comparison-bounds-minus-two-sevenths-mesh6000` | PASS (exit=0, 25s) | == energy certificate -2/7: 10 passed, 0 failed == |
| `certify-minus-two-ninths` | PASS (exit=0, 81s) | All finite exact negative-argument certificates passed. |
| `certify-minus-two-sevenths` | PASS (exit=0, 87s) | All finite exact negative-argument certificates passed. |
| `verify-profile-integrals` | PASS (exit=0, 285s) | == profile certificate: 13 passed, 0 failed == |
| `verify-rate-comparison` | PASS (exit=0, 0s) | == rate comparison: 34 passed, 0 failed == |
| `check-external-fields` | PASS (exit=0, 0s) | y=1.5: h=500: D=+0.01737 (D*h/log h=+1.40); h=5000: D=+0.00220 (D*h/log h=+1.29); h=50000: D=+0.00027 (D*h/log h=+1.23) |
| `check-series-identity` | PASS (exit=0, 2s) | == entries with relative difference above 1e-40: none |

## Reviews

| Date | Kind | Scope | Reviewer | Outcome and open issues |
|---|---|---|---|---|
| 2026-11-25 | Mathematical (internal audit) | the candidate argument and the certificates | Claude Opus 5.5 (AI-internal) | errors found and corrected (see `../CHANGELOG.md`; in particular the zero-class correction of the pole bound); the steps marked *candidate* in the manuscript are not verified; not an independent review |
| 2026-11-25 | Literature and novelty | prior results on the target values; bibliographic data | Claude Opus 5.5 (AI-internal survey) | sources read directly where possible (Hexagon, arXiv, Crossref, zbMATH Open, Zenodo, GitHub; full Hexagon catalogue); The Li₂ values: Litsey (Hexagon 2611.00848v1, Remark 8.1 and §1.1: no measure for Li₂(2/b), b ≤ 11, or Li₂(−2/b), b ≤ 9), Liu's Li2Rational, Tan–Zhang (arXiv:2611.01066), Rhin–Viola (2005, 2019), Viola–Zudilin (2018), Hata (1990, 1993). Outcome: no located source proves any of the four values irrational; Landen's identity gives one value of each pair. Limits: MathSciNet and Google Scholar not searched; some thresholds taken second-hand (marked in the manuscript); absence of evidence is "no proof found", not proof of absence |
| 2026-11-26 | Mathematical (adversarial, AI-internal) | the whole manuscript, its attributions and its description of the verification record | Claude Fable 5.2 (AI-internal) | a harsh review that found no critical error; all major findings were fixed (attributions to earlier work, the complete proof of Proposition 5.3, corrections of statements and of the description of the verification record); not an independent review |
| — | Statement fidelity (Lean against manuscript) | — | none yet | pending |
| — | Independent human review | — | none | pending; no person has reviewed the mathematics |

AI cross-checks are recorded as such and are not independent reviews.
