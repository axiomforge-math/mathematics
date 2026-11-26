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
| Exploration and conjectures | GPT-6.2 XHigh (web version) | proposed the two improvements and the traces to attack |
| Proof strategy and arguments | GPT-6.2 XHigh (web version) | produced the candidate proofs of the two estimates, the comparison densities and the first verification programs |
| Proof strategy and arguments | Claude Opus 5.5, Claude Fable 5.2 and Claude Sonnet 5.5 (Anthropic) | reconstructed the arguments, rewrote the proofs (one paragraph replaced), stated the four imported results explicitly |
| Computations and certificates | Claude Opus 5.5, Claude Fable 5.2 and Claude Sonnet 5.5 (Anthropic) | wrote the separately written checkers (`experiments/scripts/`) and ran every computation of `verification.md` |
| Error detection and internal review | Claude Fable 5.2 (Anthropic) | numeric audit, adversarial reading of the two new lemmas and dependency check of the imported results against the cited preprint; AI-internal, not independent |
| Manuscript preparation | Claude Opus 5.5, Claude Fable 5.2 and Claude Sonnet 5.5 (Anthropic) | drafted, revised and typeset the manuscript |
| Lean formalization | Claude Opus 5.5, Claude Fable 5.2 and Claude Sonnet 5.5 (Anthropic) | wrote the Lean package (definitions, units, criterion, margins, conditional final deduction) |
| Repository engineering | Claude Sonnet 5.5 (Anthropic) | prepared this package (scripts, logs, metadata, final checks) |

## Human contributions and responsibility

The AxiomForge owners chose the problems, directed the work, decided to release this
contribution as a preprint and approve its publication. No person has checked the mathematics.

The AxiomForge owners are responsible for every claim of this contribution. AI systems are not
authors; AxiomForge takes full responsibility for the content, including AI-assisted parts, and
for any errors. Errors can be reported to axiomforge.math@gmail.com; they are corrected openly
in a new version recorded in `../CHANGELOG.md`.

## Review status

`thm:main`: no independent human review (`independent_review = "ai-internal"`). The main theorem is conditional on four results of an unrefereed preprint, which no one has reproved. The review was carried out with Claude Fable 5.2 (Anthropic), a system of the same organisation as the one that reconstructed the proofs.
AI involvement, including AI review, is not independent certification.

## Corrections of AI-produced material

Errors found in the material produced during the original research, and how they were
repaired, are listed in `../CHANGELOG.md` and in `attempts/`.
