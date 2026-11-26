# Obstructions

Approaches that failed, and precisely why. Scope: approaches to the main theorem of this
contribution that were tried or that the literature reports as failing.

## The original Hankel family at these values

* **Approach.** Tang's family (H, B, C) = (2, 1, 4), as used in Litsey's preprint.
* **Obstruction.** According to Litsey's Remark 8.1 the margin of that construction is non-positive at 2/11 and −2/9 for every choice of his parameter; values with b ≤ 11 are outside his ranges.
* **Evidence.** Literature survey (see `verification.md`); not re-derived here.
* **Status.** Reported from the literature.

## Pole bound with uniform slot weights

* **Approach.** Giving the zero residue class the same pole weights as the other classes.
* **Obstruction.** The pole l = p gains +1, not +2; the bound fails by exactly one unit, e.g. λ = 2/11, n = 6, p = 19, 23, 29, 31.
* **Evidence.** `experiments/outputs/check-discrete-bounds-*.txt` (uncorrected deficits)
* **Status.** Refuted by exact computation; corrected in Proposition 4.6.
