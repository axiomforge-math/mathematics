# Changelog

All changes to this contribution are recorded here. Versions follow
`MAJOR.MINOR.PATCH` as defined in the archive's publication policy
(`docs/publication-policy.md`); each version is tagged `af-0002-vMAJOR.MINOR.PATCH`.
Versions `0.x` are preprints; `1.0.0` is reserved for the first publication at level V4.

## [0.1.0] - 2026-11-26

### Added

- First preprint release: a complete written argument for the irrationality of
  ξ_k = ψ₁(k/5) − π²/2, k = 1, 2, 3, 4 (`thm:main`), with the original certificate programs,
  separately written checkers, exact tests of the separation identity and of the local bound,
  and a Lean development in preparation.

- Revision after a harsh AI-internal adversarial review of the manuscript (Claude Fable 5.2; see
  `logs/ai-contributions.md`): the review found no critical error, and all major findings were
  fixed. The description of earlier results was corrected; the claim that the alternating method
  fails was removed; the number and nature of the bad primes in the finite tests are now stated
  exactly; the claim that the profile dominates prime by prime was removed; proofs of the profile
  structure lemma (Lemma 4.13) and of a uniform-continuity lemma were added.

### Corrected

These corrections were made while the argument was reconstructed and reviewed, before this
first release; they are recorded for readers who know the original candidate proof.

- **Presentation of the separation identity** (Section 2). The proof now uses a cycle instead
  of a single contour for a general open set; the function Φ_g is shown to be independent of
  the cycle; the identity is stated multiplicatively, with no division by the alternating
  determinant; Corollary 2.7 is stated for an arbitrary common subset; the admissible cycle
  for F is made explicit (the circle with diameter [−1/10, N − 9/10]); the sign is +1 for
  increasing orderings (previously only ±); clashes of letters with ψ and with m = h/16 were
  removed.
- **Small primes (Corollary 4.3(c)).** An AI-internal adversarial review of the entrywise
  bounds found the proof of Lemma 4.2 correct but one point of Corollary 4.3 imprecise: part (c)
  now reads ≤ 2n log(5N) π(√(5N)) + 3n log den X, and its proof covers the primes p | den X with
  p > √(5N). The review reported exact checks with no violation in 10,640 comparisons. The
  final comparison of constants is unchanged.
- **Margin.** The original programs state a conservatively rounded margin of 0.000476 per h²;
  the certified margin used in the manuscript is 0.00075448 per h² (certified 0.00075448215…).

### Verification

- The original certificate programs were re-run and reproduce their logs exactly.
- Both certificates were recomputed by separately written checkers: 𝒜 is the same exact
  rational, 𝒟_alt ≥ 3.5101772515 and 𝒟_sep ≥ 3.5128848577 in ball arithmetic, margin
  ≥ 0.00075448 per h².
- The separation identity was checked exactly in 48 cases (h ≤ 64) and in the further tests
  of Remark 2.10; the local bound was tested up to h = 128 with no violation at non-bad primes.
- Lean: the package builds and the axiom audit of its 25 audited declarations reports only
  `propext`, `Classical.choice` and `Quot.sound`; the main theorem is proved in Lean only
  conditionally; its formalization is in preparation.
- All checks are AI-internal. No independent human review has taken place; the statement
  fidelity review is pending.
