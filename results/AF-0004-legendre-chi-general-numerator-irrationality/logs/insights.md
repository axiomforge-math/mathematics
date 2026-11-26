# Insights

The ideas that made the proof work. For each: the idea, why it works, where it is used in
the manuscript, and its limits. Scope: the ideas of this contribution only.

## Primes dividing the numerator

* **Idea.** At a prime p dividing a, each pole can be used only once in the rank-one expansion.
* **Mechanism.** The h dearest poles cost f h (2K − h), which gives the exact leading term −(2κ − 1) v_p(a) h².
* **Used in.** Section 4 (primes dividing a).
* **Scope and limits.** Finite checks are consistent (actual valuations about 1.2 to 1.47 f h² against 1.5 f h²).

## The prime 2 for odd a

* **Idea.** In bases of polynomials vanishing at the first and last poles each entry is a forward difference of a first-order recursion.
* **Mechanism.** The valuation of each entry is bounded directly; the dependence on v₂(q² − σa²) cancels against the contribution of 2 to the logarithm of q² − σa².
* **Used in.** Section 3.
* **Scope and limits.** O(h log h) terms are not explicit.

## The parity-minor bound for a = 4 and a = 8

* **Idea.** After rescaling, the poles are odd and the summation points even, and minors whose nodes share a parity are divisible by about 2^{t²}.
* **Mechanism.** Cauchy–Binet reduces the 2-adic valuation to a quadratic minimisation in the proportion x of pole terms (x = 27/28 for a = 4 at κ = 5/4, x = 1 for a = 8).
* **Used in.** Section 3.
* **Scope and limits.** The weakest link of the argument; finite checks only.

## One inequality for all larger denominators

* **Idea.** For q ≥ q₀ ≥ 2a the margin grows by at least (10/27) log(q/q₀).
* **Mechanism.** The size exponent improves by (1/2) log(q/q₀) and the arithmetic constant loses at most (8/3) D log(q/q₀) with D ≤ 25/144.
* **Used in.** Section 8.
* **Scope and limits.** Checked numerically at five larger denominators for each row.
