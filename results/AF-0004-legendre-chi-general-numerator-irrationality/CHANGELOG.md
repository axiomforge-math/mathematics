# Changelog

All changes to this contribution are recorded here. Versions follow
`MAJOR.MINOR.PATCH` as defined in the archive's publication policy
(`docs/publication-policy.md`); each version is tagged `af-0004-vMAJOR.MINOR.PATCH`.
Versions `0.x` are preprints; `1.0.0` is reserved for the first publication at level V4.

## [0.1.0] - 2026-11-26

### Added

- First preprint release: a complete written argument for the irrationality of χ₂(a/q) and Ti₂(a/q)
  (and at −a/q) for the numerators a = 3, 4, 5, 8 and the thresholds of `thm:main`, with separately
  written checkers for every certified number, exact consistency checks at small sizes and a Lean
  development in preparation.
- Three arithmetic estimates absent for the numerator 2: the bound at the primes dividing a, the bound
  at the prime 2 for odd a, and the parity-minor bound at 2 for a = 4 and a = 8.
- A single inequality (a shift lemma and a monotonicity computation) that carries each threshold to
  all larger denominators.

### Corrected

- **Tail condition.** The tail condition used by the verifiers (1 + log W < 0, log W < λ) is stronger
  than needed in the original candidate material and is the one used in the manuscript.
- **Nonvanishing range.** The manuscript requires q ≥ 14a for the nonvanishing at prime indices (the
  candidate material used q/a ≥ 83/2); both hold for the six rows.

### Verification

- The profile integrals, the six threshold margins (certified with Arb ball arithmetic: at least 0.013945786, 0.005113500, 0.001699724, 0.001300300, 0.000713481 and 0.000758530 per h² for (a, q) = (3, 131), (3, 257), (4, 995), (5, 829), (5, 1609), (8, 12061)), the
  propagation of the margin to larger q and the six local determinants were recomputed by separately
  written programs; the exact polynomials T were computed for all six rows (and for two extra
  numerators) up to h = 32–56 and no finite bound failed.
- A numeric audit and a line-by-line reading of the new arithmetic lemmas (Claude Sonnet 5.5, AI-internal)
  found no mathematical gap; every step stays *candidate*.
- Lean: the package builds and the axiom audit of its 36 audited declarations reports only `propext`,
  `Classical.choice` and `Quot.sound`; the main theorems are proved in Lean only conditionally; their
  formalization is in preparation.
- All checks are AI-internal. No independent human review has taken place; the statement fidelity
  review is pending.
