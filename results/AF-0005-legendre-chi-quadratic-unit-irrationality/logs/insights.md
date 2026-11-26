# Insights

The ideas that made the proof work. For each: the idea, why it works, where it is used in
the manuscript, and its limits. Scope: the ideas of this contribution only.

## No extra cost at odd primes dividing the trace

* **Idea.** At an odd prime p dividing n, bound the entries of the Hankel matrix directly, with loss −2L − e(i + j − K)₊.
* **Mechanism.** A Kummer-type count of the losses (binomial, pole index, pole tails) shows that no extra term beyond the one forced by v_p(n) remains; convexity handles the sum.
* **Used in.** Section 3.
* **Scope and limits.** Removes the term log p / (4(p − 1)) of the cited preprint; only O(h log h) is claimed beyond the leading term.

## Half the cost at the prime 2 for odd traces

* **Idea.** Regularise the functional by a finite 2-adic sum, then use a parity-minor lemma and Cauchy–Binet for arbitrary row subsets.
* **Mechanism.** 2 is inert, z and 1 − y are units, and the pole weights satisfy v₂(D′(x_k)) ≤ 2h; the factor 2 on the minors halves the cost, from (1/2) log 2 to (1/4) log 2.
* **Used in.** Section 4.
* **Scope and limits.** False by construction at even n; the even case is imported.

## Shift lemma and monotonicity

* **Idea.** A certificate at the first admissible trace of each parity extends to larger traces.
* **Mechanism.** The size exponent improves by half the logarithmic increase of t(n) while the arithmetic constant loses less.
* **Used in.** Section 6 and Section 7.
* **Scope and limits.** Confirmed numerically for every trace up to 20 000.
