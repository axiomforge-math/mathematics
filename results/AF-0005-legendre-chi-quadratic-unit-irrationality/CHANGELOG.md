# Changelog

All changes to this contribution are recorded here. Versions follow
`MAJOR.MINOR.PATCH` as defined in the archive's publication policy
(`docs/publication-policy.md`); each version is tagged `af-0005-vMAJOR.MINOR.PATCH`.
Versions `0.x` are preprints; `1.0.0` is reserved for the first publication at level V4.

## [0.1.0] - 2026-11-26

### Added

- First preprint release: **assuming four results of an unrefereed preprint of Krisman** (K1 Theorem 3.7,
  K2 Proposition 4.2, K3 Theorem 5.1 for even h ≥ 100, K4 Lemmas 6.1 and 8.6 for ℓ ≥ 7, ℓ ∤ n, ℓ² ∤ b, K2 only for even n; stated, not reproved), a complete written argument
  that T_σ(n) (χ₂ or Ti₂ at the unit z = 2/(n + √(n² + 4σ))) is irrational for both signs, every even n ≥ 14 and every
  odd n ≥ 27 (`thm:main`); this covers 31 of the 47 traces excluded for χ₂ and 42 of the 57 excluded for Ti₂.
- Proofs of the two improvements that the cited preprint names and does not prove: no cost at an odd prime
  dividing n beyond the one forced by the valuation of n, and half of the proved cost at the prime 2 for odd n.
- Four new certificates for the size estimate (n = 14, 27, both signs), a shift lemma and a monotonicity step for
  larger traces, separately written checkers, and a Lean development in preparation.

### Corrected

- **Finite regularisation.** One paragraph of the candidate proof of the bound at the prime 2 was unusable and was
  replaced by a complete argument (Eulerian polynomials; the difference has valuation at least L − v₂(c)), confirmed
  on exact data.
- **Hypotheses of the imported nonvanishing lemma.** The candidate material stated it with ℓ ∤ b; the manuscript requires
  ℓ ≥ 7, ℓ ∤ n and ℓ² ∤ b, as in the cited preprint, and h ≥ 100 for the size estimate.
- **Reading of a remark.** The cited preprint's remark expects n = 14 to need a better 2-adic constant in addition to
  direct certificates; the recomputation shows that the improved constant together with a direct certificate suffices.

### Verification

- The size certificates were recomputed by a separately written Arb implementation (all twelve values of the
  original verifier confirmed; margins C(n) + Φ ≤ −0.0115, −0.0063 at n = 14 and −0.0068, −0.0054 at n = 27 per h²);
  16 418 exact arithmetic checks pass (series identity, entry bounds, regularisation, parity minors, exact exponents n_p(h));
  the exceptional sets of the cited preprint were recomputed (31 and 42 new traces).
- A harsh AI-internal review (Claude Fable 5.2: numeric audit, adversarial reading of the two new lemmas, dependency check)
  found that the theorem is conditional on the four imported results (stated explicitly), found no gap in the new lemmas,
  and led to the fixes above; it is not independent.
- Lean: the package builds and the axiom audit of its 33 audited declarations reports only `propext`,
  `Classical.choice` and `Quot.sound`; the main theorems are proved in Lean only conditionally; their
  formalization is in preparation.
- All checks are AI-internal. No independent human review has taken place; the statement
  fidelity review is pending.
