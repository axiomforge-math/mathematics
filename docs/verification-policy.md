# Verification policy

AxiomForge never collapses "is it true?" into a single flag. Every advertised theorem
carries an independent status in each of the dimensions below, recorded in its
contribution's `result.toml`. A result is published (`status = "published"`) only when
every dimension marked **gate** is satisfied. A contribution below that level may appear
in the archive only as a clearly labelled preprint, under the separate gates of the
[preprint tier](#preprint-tier).

| Dimension | Field | Values | Gate |
|---|---|---|---|
| Conventional proof | `proof` | `none`, `sketch`, `candidate`, `complete` | `complete` |
| Computational certificates | `certificates` | `not-applicable`, `pending`, `reproduced`, `formally-checked` | `reproduced` or better |
| Lean formalization | `formalization` | `none`, `in-preparation`, `statement-only`, `partial`, `complete` | `complete` |
| Lean build | `build` | `not-run`, `failing`, `passing` | `passing` |
| Axiom audit | `axioms` | `not-run`, `failing`, `standard` | `standard` |
| Statement fidelity | `statement_review` | `pending`, `checked` | `checked` |
| Independent mathematical review | `independent_review` | `pending`, `ai-internal`, `human` | recorded honestly (not a gate) |
| Literature and novelty | `literature_review` | `pending`, `checked` | `checked` |

Definitions:

* **complete conventional proof** — the manuscript proves every advertised statement from
  cited external theorems whose statements and hypotheses have been checked against
  the original sources. No step is deferred to "future work", to the logs, or to Lean.
* **complete formalization** — the Lean theorem whose statement is recorded in
  `result.toml` compiles with no `sorry`, `admit`, project-specific `axiom`, or
  unverified hypothesis, and expresses the actual mathematical claim (checked by a
  human-readable statement review).
* **standard axioms** — `#print axioms` for every main theorem reports a subset of
  `propext`, `Classical.choice`, `Quot.sound`. Anything else, including `sorryAx`,
  `Lean.ofReduceBool` (from `native_decide`) or custom axioms, fails the gate.
* **ai-internal review** — cross-checking by AI systems. This is never described as
  independent human or external certification.

## Levels (summary)

For quick communication we also use the following summary levels. They are derived
from the dimensions above; they never replace them.

| Level | Meaning |
|---|---|
| V0 | Exploratory: ideas, conjectures, incomplete arguments |
| V1 | Candidate proof: an apparently complete argument awaiting verification |
| V2 | Audited manuscript: detailed internal mathematical audit performed |
| V3 | Formalized: main theorems and supporting proofs compile in Lean |
| V4 | Kernel-verified: V3 plus axiom audit and statement-fidelity review |
| V5 | Independently validated: V4 plus independent human review |

**Publication (`status = "published"`) requires V4 for every advertised main theorem.**
Below V4 a contribution may enter `results/` only as a preprint (next section), whose
main theorems the archive does not establish.

## Preprint tier

A preprint (`status = "preprint"`) releases a complete written argument whose Lean
development is still in preparation. It is a separate status with its own gates; it
does not relax the publication gate above, which is unchanged.

Gates, for every main theorem of a preprint:

| Dimension | Preprint gate |
|---|---|
| `proof` | `candidate` or `complete` |
| `certificates` | `not-applicable`, `reproduced` or `formally-checked`: every computation the argument relies on is reproduced |
| `formalization` | `in-preparation`, `statement-only`, `partial` or `complete` |
| `build`, `axioms` | `passing` and `standard` whenever the theorem names a Lean declaration to audit (`lean` or `lean_conditional`) |
| `statement_review` | `pending` or `checked` |
| `literature_review` | `checked` |
| `independent_review` | recorded honestly (not a gate) |

Further rules:

* `version` is `0.MINOR.PATCH`. Version `1.0.0` is reserved for the first publication at
  level V4. A contribution that has been published never returns to preprint.
* `lean` may be empty while `formalization` is not `complete`. A theorem may list
  `lean_conditional = ["Ns.main_of_estimates", ...]`: Lean declarations that prove the
  theorem from explicitly stated hypotheses. Their names contain `_of_` (they are named
  after their hypotheses); `python3 scripts/afm.py lean` builds them and audits their
  axioms. A conditional declaration is never accepted as the `lean` name of a theorem.
* Page 1 of the manuscript says "Preprint" next to its status statement (for example
  `\afversion{0.1.0, Preprint}` in the publication block); `afm paper` checks it.
* The catalogue lists preprints in a section of their own, *Preprints (complete written
  arguments, not yet kernel-verified)*, with every verification dimension.

What a preprint establishes, and what it does not:

* It establishes that a complete written argument, with reproduced computations and a
  checked literature review, has been released for public scrutiny under a permanent
  identifier, with an honest record of every verification dimension.
* It does **not** establish its main theorems: the archive does not vouch for a
  preprint's main theorem until the contribution reaches level V4 and is published.
  A conditional Lean declaration proves only its stated implication, never the
  unconditional theorem.

A preprint becomes a publication when every main theorem passes the publication gate.
That release is version `1.0.0`; the 0.x history remains in `CHANGELOG.md` and under
its tags (see the [publication policy](publication-policy.md)).

## What a successful build does not show

`lake build` succeeding does not show that a theorem was proved: a declaration may
depend on `sorryAx`, on `native_decide`, or may state something weaker than intended.
Verification therefore always combines (i) a build, (ii) an axiom audit of the named main
theorems, (iii) a check that every Lean file of the package participates in the build,
and (iv) a statement review by a mathematician-reader.

## Computational certificates

A certificate is a finite object together with a checker and a proof that acceptance by
the checker implies the mathematical statement used. Floating-point computations may
guide exploration, never prove. Python checks must not rely on `assert` (which can be
disabled); they must exit non-zero on failure. A certificate counts as
`formally-checked` only when its checker is proved correct in Lean and executed by the
kernel (`decide`, `norm_num`, `rfl`), not by `native_decide`.

## Corrections and withdrawals

Identifiers are never reused. A result found to be wrong keeps its identifier and
receives a prominent correction or withdrawal notice in its README, `result.toml`
(`status = "withdrawn"`) and `CHANGELOG.md`. A different statement is never silently
substituted for a published one.

## Related documents

[Formalization policy](formalization-policy.md) (Lean packages and the trust policy),
[reproducibility](reproducibility.md) (certificates and reproduction),
[publication policy](publication-policy.md) (versions, corrections, withdrawals),
[AI disclosure policy](ai-disclosure-policy.md).
