# AI disclosure policy

AxiomForge uses AI systems throughout its research. Readers are entitled to know exactly
how. This policy states what every contribution discloses, where, and in what terms.

## 1. Principles

1. **Complete.** Every AI system that contributed materially is named, with its role.
2. **Exact.** Systems are identified by provider, model, version and interface or
   setting when known. When a detail cannot be observed directly (for example the
   setting used in a past web session), it is reported as stated by the AxiomForge
   owners and marked as such.
3. **Not certification.** AI involvement, including AI review or cross-checking, is
   never presented as independent verification. The kernel check of the Lean proofs is
   reported as what it is: a mechanical check of the formal statements.
4. **Honest review status.** Whether an independent human review has taken place is
   stated plainly, per theorem; "pending" is a normal and acceptable status.
5. **Human responsibility.** The AxiomForge owners are responsible for every published
   claim, whatever tools produced it. AI systems are not authors and cannot take
   responsibility. Every manuscript ends its disclosure section with the fixed paragraph of
   the template (`templates/paper/sections/disclosure.tex`): AxiomForge takes full
   responsibility for the entire content, including every part produced with AI assistance,
   and for any errors; errors are reported to the correspondence address and corrected
   openly in a new version recorded in the contribution's changelog, with credit to the
   reporter. Taking responsibility is not a claim of verification: the review status is
   stated separately (item 4).

## 2. Where the disclosure appears

| Place | Content |
|---|---|
| Manuscript title page (`\afdisclosure{...}`) | one or two sentences: that AI systems were used and where the full disclosure is |
| Manuscript section *AI-assisted research disclosure* | the full account (section 3) |
| `logs/ai-contributions.md` | the same account, with the role of each system in each phase and the evidence trail |
| `result.toml`, `[disclosure]` | `summary` (one paragraph) and `ai_systems` (list of identified systems) |
| `README.md` of the contribution | one sentence and a link |

`python3 scripts/afm.py check` requires the `[disclosure]` fields, and
`python3 scripts/afm.py paper` requires the short disclosure on page 1 and the full
section.

## 3. What the full disclosure covers

For each AI system, which of the following it did, and how much:

* exploration: literature search, examples, conjectures;
* proof strategy and arguments: which proofs, lemmas or constructions originated with it;
* computations: code written, computations run, certificates generated;
* error detection and internal review;
* manuscript preparation: drafting, editing, typesetting;
* Lean formalization;
* repository engineering: tooling, checks, packaging.

And, for the people involved: what they did (direction, selection, checking, writing),
and the status of independent review (pending, AI-internal only, or human, with the
reviewer's consent to be named).

## 4. Wording

* Name systems precisely, for example "Claude Opus 5.5 (Anthropic), used through Claude
  Code". Do not write "an AI" or "a large language model" when the system is known.
* Use plain verbs: "proposed", "drafted", "computed", "checked", "formalized". Avoid
  wording that suggests understanding or endorsement ("the AI confirmed the proof is
  correct").
* When an argument produced by an AI system was later found wrong and repaired, say so
  in the logs.

## 5. Authorship

AI systems are not authors. The author of every contribution is AxiomForge (see the
[publication policy](publication-policy.md)).
