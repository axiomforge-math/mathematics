# Publication policy

How contributions enter the archive, how they are versioned, corrected and withdrawn,
and how authorship, AI involvement and licensing are stated.

## 1. Publication

* A contribution is published when every main theorem satisfies every gate of the
  [verification policy](verification-policy.md) (level V4) and
  `python3 scripts/afm.py verify AF-NNNN` and `python3 scripts/afm.py isolate AF-NNNN`
  pass.
* Automated checks establish structure, builds and the axiom audit. They do not establish
  mathematical correctness, statement fidelity, exposition or novelty: those rest on the
  reviews recorded in `result.toml`, which state honestly who performed them.
* The publication commit adds the contribution's directory and regenerates the catalogue,
  and nothing else. It is tagged `af-NNNN-v1.0.0`.
* Before level V4 a contribution may be released as a **preprint** (`status =
  "preprint"`): a complete written argument with reproduced computations and a checked
  literature review, whose Lean development may still be in preparation. Its gates are
  those of the [preprint tier](verification-policy.md#preprint-tier). The archive does
  not establish a preprint's main theorems until the contribution reaches V4. A preprint
  says "Preprint" on page 1 of its manuscript and is listed in the catalogue section
  *Preprints (complete written arguments, not yet kernel-verified)*.

## 2. Identifiers

* Identifiers `AF-NNNN` are allocated sequentially at publication and are never reused,
  even after a withdrawal.
* The directory name `AF-NNNN-<subject>-<property>` is permanent; a later version keeps
  it even if the title changes.

## 3. Versioning

Each contribution is versioned independently, `MAJOR.MINOR.PATCH`, with a tag
`af-NNNN-vMAJOR.MINOR.PATCH` for every released version (preprint or published).

* **Preprints are versioned `0.MINOR.PATCH`**, starting at `0.1.0`. Within the 0.x
  series the table below applies with MINOR in the role of MAJOR (a changed main
  statement is a new MINOR version) and PATCH as usual.
* **`1.0.0` is reserved for the first publication at level V4**, the version at which
  every main theorem passes the publication gate. Later versions follow the table below.
* A published contribution never returns to preprint. `scripts/afm.py check` rejects a
  preprint whose `CHANGELOG.md`, or the history of its `result.toml`, records a published
  version. A published result found to be wrong is corrected or withdrawn (sections 4
  and 5).

| Change | Version |
|---|---|
| Typographical or expository correction; metadata; build fix; no change to any statement or proof | PATCH |
| Corrected or completed proof of an unchanged statement; new supporting material; stronger verification (for example a human review recorded) | MINOR |
| Change to the statement of a main theorem (weakened, strengthened or corrected); removal of a main theorem; withdrawal | MAJOR |

Every change, however small, gets a `CHANGELOG.md` entry under a new version. The
version and date are updated in `result.toml` and `CITATION.cff`, and `paper/main.pdf`
is rebuilt. Entries are listed newest first as `## [MAJOR.MINOR.PATCH] - YYYY-MM-DD`,
with the changes grouped under these categories (empty categories are omitted; see
`templates/result/CHANGELOG.md`):

| Category | Content |
|---|---|
| Corrected | errors fixed: what was wrong, its consequences, who reported it |
| Added | new results, proofs or supporting material |
| Generalized | a result extended, generalized or strengthened |
| Changed | other changes to statements, proofs, formalization or exposition |
| Literature | citations or attribution added or corrected |
| Verification | checks performed, certificates recomputed, review status changed |

### How "in preparation" progresses

A preprint's Lean development moves through the `formalization` values
`in-preparation`, `statement-only`, `partial`, `complete`. Each step is a new 0.x
version with a *Verification* entry stating what now compiles, which declarations are
audited (`lean`, `lean_conditional`) and the result of their axiom audit. Conditional
declarations (`..._of_<hypotheses>`) record progress but never count as the
formalization of a main theorem. When every main theorem passes every publication gate,
the contribution is released as version `1.0.0` with `status = "published"`.

## 4. Corrections

* An error is corrected openly. `CHANGELOG.md` describes what was wrong, what changed,
  who reported it and when.
* If a published statement was false or unproved, the README of the contribution carries
  a correction notice at the top, and the manuscript a dated note on its title page,
  until the next MAJOR version supersedes them.
* A different statement is never silently substituted for a published one. The earlier
  versions remain available through their tags.

## 5. Withdrawals

A contribution whose main result cannot be repaired is withdrawn:

* `status = "withdrawn"` in `result.toml`, with a `withdrawal` field giving the date and
  reason;
* a withdrawal notice at the top of its `README.md` and in `CHANGELOG.md`;
* the identifier, directory and history remain; the catalogue shows the status.

Partial results that survive are republished, if at all, as a new version or a new
contribution that cites the withdrawn one.

## 6. Authorship and attribution

* The author of every contribution is **AxiomForge**. Correspondence:
  axiomforge.math@gmail.com.
* AI systems are never listed as authors. Their roles are disclosed under the
  [AI disclosure policy](ai-disclosure-policy.md).
* Prior work is credited precisely: methods, constructions, lemmas and code that a
  contribution builds on are cited at the point of use. Code copied from another source
  keeps its licence notice and provenance.
* Persons who report errors or provide reviews are acknowledged with their consent.

## 7. Review status

The status of independent review is part of the published record
(`independent_review` = `pending`, `ai-internal` or `human` for each theorem) and is
repeated in the manuscript. A change of review status is a MINOR version.

## 8. Licensing

The licence of the archive and of its contributions is **to be decided by the owners**.
No `LICENSE` file exists yet, and none is implied. Third-party data redistributed in this
repository keeps its own licence (for example the MSC2020 table in `scripts/data/`, see
its README).
