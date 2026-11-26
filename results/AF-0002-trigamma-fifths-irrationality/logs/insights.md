# Insights

The ideas that made the proof work. For each: the idea, why it works, where it is used in
the manuscript, and its limits. Scope: the ideas of this contribution only.

## Separate the border rows from the border columns

* **Idea.** Put all border rows before all border columns instead of interleaving them.
* **Mechanism.** By an Andréief–Cauchy factorization the separated determinant is the alternating one divided by exactly 2^{m(m−1)}; odd-prime valuations are unchanged and the entrywise bound controls the prime 2 at cost O(h log h), a net gain of (log 2)/256 per h².
* **Used in.** Proposition 2.6, Corollaries 2.7–2.8.
* **Scope and limits.** The gain is small; the final margin is thin.

## Two-layer polar bound

* **Idea.** Denominators are bounded by the ranks of residue-class blocks and a first-digit pairing across classes.
* **Mechanism.** The finite prediction 2R₀ + q is attained at almost every prime in the exact tests.
* **Used in.** Lemma 4.5, Proposition 4.8.
* **Scope and limits.** p₀ not computed.
