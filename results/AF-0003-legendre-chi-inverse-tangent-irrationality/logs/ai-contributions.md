# AI contributions

The role of every AI system in this contribution, following the archive's AI disclosure policy
(`docs/ai-disclosure-policy.md`).

## Systems

| System | Provider | Version, interface or setting | Source of this identification |
|---|---|---|---|
| GPT-6.2 XHigh | OpenAI | web version, XHigh setting | as stated by the AxiomForge owners (not observed directly) |
| Claude Opus 5.5 | Anthropic | used through Claude Code | observed |
| Claude Fable 5.2 | Anthropic | used through Claude Code, separate sessions | observed |
| Claude Sonnet 5.5 | Anthropic | used through Claude Code | observed |

## Roles

| Phase | System | What it did |
|---|---|---|
| Exploration and conjectures | GPT-6.2 XHigh (web version) | chose the targets and the constructions, searched parameters numerically |
| Proof strategy and arguments | GPT-6.2 XHigh (web version) | produced the candidate proof(s) and the original certificate programs |
| Proof strategy and arguments | Claude Opus 5.5 (Anthropic) | reconstructed the argument as one manuscript, corrected the errors listed in `../CHANGELOG.md`, wrote the missing proofs |
| Computations and certificates | GPT-6.2 XHigh (web version) | wrote the original certificate programs (`experiments/scripts/certify_*.py` where present) |
| Computations and certificates | Claude Opus 5.5 (Anthropic) | wrote the separately written checkers and the exact audit programs, ran every computation of `verification.md` |
| Error detection and internal review | Claude Opus 5.5 (Anthropic) | audited the candidate argument and the certificates; this review is AI-internal, not independent |
| Manuscript preparation | Claude Opus 5.5 (Anthropic) | drafted and typeset the manuscript |
| Lean formalization | Claude Opus 5.5 (Anthropic) | wrote the Lean package (definitions, criterion, finite certificates, conditional final deduction) |
| Adversarial review | Claude Fable 5.2 (Anthropic) | reviewed the manuscript adversarially, in a separate session, and checked its statements against the cited sources; a harsh AI-internal review that found no critical error; all major findings were fixed; not an independent review |
| Revision after the review | Claude Fable 5.2 and Claude Sonnet 5.5 (Anthropic) | fixed the findings (statements, proofs, verifiers, reproducibility section) and updated the manuscript |
| Repository engineering | Claude Opus 5.5 and Claude Sonnet 5.5 (Anthropic) | prepared this package (scripts, logs, metadata, final checks) |

## Human contributions and responsibility

The AxiomForge owners chose the problems, directed the work, decided to release this
contribution as a preprint and approve its publication. No person has checked the mathematics.

The AxiomForge owners are responsible for every claim of this contribution. AI systems are not
authors; AxiomForge takes full responsibility for the content, including AI-assisted parts, and
for any errors. Errors can be reported to axiomforge.math@gmail.com; they are corrected openly
in a new version recorded in `../CHANGELOG.md`.

## Review status

`thm:main`: no independent human review (`independent_review = "ai-internal"`). The audits,
recomputations and the adversarial review were carried out with Claude Opus 5.5, Claude Fable 5.2 and Claude Sonnet 5.5 (Anthropic), all of them AI systems working within the same AI-driven process as the one that produced
the candidate material. AI involvement, including AI review, is not independent certification.

## Corrections of AI-produced material

Errors found in the material produced during the original research, and how they were
repaired, are listed under *Corrected* in `../CHANGELOG.md` and in `attempts/`.
