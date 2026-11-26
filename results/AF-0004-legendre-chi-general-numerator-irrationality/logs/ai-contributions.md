# AI contributions

The role of every AI system in this contribution, following the archive's AI disclosure policy
(`docs/ai-disclosure-policy.md`).

## Systems

| System | Provider | Version, interface or setting | Source of this identification |
|---|---|---|---|
| GPT-6.2 XHigh | OpenAI | web version, XHigh setting | as stated by the AxiomForge owners (not observed directly) |
| Claude Opus 5.5 | Anthropic | used through Claude Code | observed |
| Claude Fable 5.2 | Anthropic | used through Claude Code | observed |
| Claude Sonnet 5.5 | Anthropic | used through Claude Code | observed |

## Roles

| Phase | System | What it did |
|---|---|---|
| Exploration and conjectures | GPT-6.2 XHigh (web version) | chose the targets and the constructions, searched parameters numerically |
| Proof strategy and arguments | GPT-6.2 XHigh (web version) | produced the candidate proofs and the original certificate programs |
| Proof strategy and arguments | Claude Sonnet 5.5, Claude Fable 5.2, Claude Opus 5.5 (Anthropic) | reconstructed the arguments, rewrote the proofs, wrote the new arithmetic lemmas in full |
| Computations and certificates | Claude Sonnet 5.5, Claude Fable 5.2, Claude Opus 5.5 (Anthropic) | wrote the separately written checkers (`experiments/scripts/`) and ran every computation of `verification.md` |
| Error detection and internal review | Claude Sonnet 5.5 (Anthropic) | numeric audit and critical reading of the new arithmetic lemmas; AI-internal, not independent |
| Manuscript preparation | Claude Sonnet 5.5, Claude Fable 5.2, Claude Opus 5.5 (Anthropic) | drafted and typeset the manuscript |
| Lean formalization | Claude Sonnet 5.5, Claude Fable 5.2, Claude Opus 5.5 (Anthropic) | wrote the Lean package (definitions, criterion, margins, conditional final deduction) |
| Repository engineering | Claude Sonnet 5.5 (Anthropic) | prepared this package (scripts, logs, metadata, final checks) |

## Human contributions and responsibility

The AxiomForge owners chose the problems, directed the work, decided to release this
contribution as a preprint and approve its publication. No person has checked the mathematics.

The AxiomForge owners are responsible for every claim of this contribution. AI systems are not
authors; AxiomForge takes full responsibility for the content, including AI-assisted parts, and
for any errors. Errors can be reported to axiomforge.math@gmail.com; they are corrected openly
in a new version recorded in `../CHANGELOG.md`.

## Review status

`thm:main`: no independent human review (`independent_review = "ai-internal"`). The audit, the recomputations and the reading of the lemmas were carried out with Claude Sonnet 5.5, Claude Fable 5.2 and Claude Opus 5.5 (Anthropic), all AI systems working within the same AI-driven process as the one that produced the candidate material.
AI involvement, including AI review, is not independent certification.

## Corrections of AI-produced material

Errors found in the material produced during the original research, and how they were
repaired, are listed in `../CHANGELOG.md` and in `attempts/`.
