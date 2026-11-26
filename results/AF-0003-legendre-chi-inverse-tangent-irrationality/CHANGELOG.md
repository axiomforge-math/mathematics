# Changelog

All changes to this contribution are recorded here. Versions follow
`MAJOR.MINOR.PATCH` as defined in the archive's publication policy
(`docs/publication-policy.md`); each version is tagged `af-0003-vMAJOR.MINOR.PATCH`.
Versions `0.x` are preprints; `1.0.0` is reserved for the first publication at level V4.

## [0.1.0] - 2026-11-26

### Added

- First preprint release: a complete written argument for the irrationality of χ₂(2/q) and
  Ti₂(2/q) for every odd q ≥ 81, hence also at −2/q (`thm:main`), with separately written
  checkers for every certified number, exact consistency checks at small sizes and a Lean
  development in preparation.
- Full proofs of the ordinary-prime profile comparison (Proposition 5.7) and of the
  convexity on the breakpoint intervals (Lemma 5.8), which the original candidate arguments
  only sketched.

- Revision after a harsh AI-internal adversarial review (Claude Fable 5.2; see
  `logs/ai-contributions.md`): the review found no critical error and all major findings were fixed.
  The statements of the cited literature were checked against the cited preprint (statements only,
  not its proofs); the statements of the filling lemma (Lemma 5.6) and of the profile proposition
  (Proposition 5.7) were corrected; an unsupported claim of agreement with a numerical value was
  removed; Section 9 now describes limits of these estimates only; the reproducibility section was
  rewritten from the package.

### Corrected

- **Verifier of the archimedean bound.** The ball-arithmetic verifier (`verify_comparison_bounds.py`)
  dropped a cell whose enclosure straddled zero, and used a different form of the tail conditions
  for α = 0. It now adds the upper end of every cell that is not certainly negative and checks the two
  tail conditions of Lemma 6.2 in the same way for α = 0 and α > 0. The certified values are
  unchanged (B − A₋ ≤ −0.0068631 for q ≥ 83 and ≤ −0.0056790 for q = 81).

- **Valuation at p = 83.** An earlier record stated that v₈₃(T) = h²/3 at every computed size;
  exact data show that it falls slightly below h²/3 from h = 36 on (0.3326h² at h = 36,
  0.3219h² at h = 60), as allowed by the −O(h log h) term of Proposition 4.5. The manuscript
  states the corrected data.

### Verification

- The profile integrals, the comparison densities (B − A₋ ≤ −0.0068631 for q ≥ 83 and
  ≤ −0.0056790 for q = 81), the local determinants and the modular witnesses were recomputed by
  separately written checkers, with exact rationals and Arb ball arithmetic.
- The exact 2-adic data were extended to h = 72, and the square construction (K = h, A = 0) was
  computed exactly for h = 8, 16, …, 64 in both normalisations (last table of Appendix B); the finite local bounds, the series identity
  and the prime-index mechanism were checked on exact data at small sizes.
- Lean: the package builds and the axiom audit of its 29 audited declarations reports only
  `propext`, `Classical.choice` and `Quot.sound`; the main theorems are proved in Lean only
  conditionally; their formalization is in preparation.
- All checks are AI-internal. No independent human review has taken place; the statement
  fidelity review is pending.
