# Instructions for AI agents and contributors

This file is the canonical instruction set for every AI agent (Claude Code, Codex,
Gemini, Copilot, Cursor, Grok and others) and every person working in this repository.
`CLAUDE.md`, `GEMINI.md` and `.github/copilot-instructions.md` only point here.

This is the **public archive** of AxiomForge: everything committed here is published.

## Contents

1. [Absolute rules](#1-absolute-rules)
2. [Repository map](#2-repository-map)
3. [Structure of a contribution](#3-structure-of-a-contribution)
4. [`result.toml`](#4-resulttoml)
5. [The archive tool and its checks](#5-the-archive-tool-and-its-checks)
6. [Lean rules](#6-lean-rules)
7. [Manuscript rules](#7-manuscript-rules)
8. [Classification, disclosure and attribution](#8-classification-disclosure-and-attribution)
9. [Changing the repository](#9-changing-the-repository)

## 1. Absolute rules

1. **Public content only.** Never add, quote, link or allude to unpublished work, internal
   tooling, internal identifiers, local file-system paths, machine names, credentials or
   any material that is not itself part of this archive or a public source. Public
   documents describe only this archive, its policies and how to reproduce published
   results.
2. **Never weaken verification.** Do not relax a check in `scripts/afm.py`, the trust
   policy, a publication gate, or a status in `result.toml` to make something pass.
3. **Never upgrade a status without evidence.** A verification field in `result.toml`
   changes only when the corresponding check or review has actually been performed and
   its evidence is in the contribution.
4. **Never change a published statement silently.** Corrections follow
   [docs/publication-policy.md](docs/publication-policy.md).
5. **Self-containment.** A contribution never depends on another contribution, on
   repository-level files, or on anything outside its own directory (pinned public
   dependencies such as Mathlib excepted).
6. **No secrets.** Never read, print or commit `.env` or any credential.
7. **Commit and push only when the owners ask.** Never force-push; never rewrite
   published history.

## 2. Repository map

```text
mathematics/
├── README.md               overview for readers
├── AGENTS.md               this file (canonical instructions)
├── CLAUDE.md, GEMINI.md    pointers to this file
├── CONTRIBUTING.md         error reports, corrections, pull requests
├── CITATION.cff            citation of the archive as a whole
├── results/                one directory per published contribution (empty so far)
├── catalogue/              generated from results/*/result.toml; never edited by hand
├── templates/
│   ├── paper/              canonical amsart manuscript template
│   ├── result/             README.md, result.toml, CITATION.cff, CHANGELOG.md
│   └── logs/               scaffolding of a contribution's logs/ directory
├── docs/                   policies (verification, formalization, writing, publication,
│   │                       reproducibility, AI disclosure, naming, architecture)
│   └── manuscript-sample/  compiled specimen of the manuscript template
├── scripts/afm.py          archive tool (Python standard library only)
├── scripts/data/           official MSC2020 table used for validation
├── tests/                  test suite of the archive tool (pytest)
├── Makefile                shortcuts for scripts/afm.py (`make help`)
└── .github/                pull-request template and assistant instructions
```

No contribution has been published yet.

## 3. Structure of a contribution

```text
results/AF-NNNN-<slug>/
├── README.md          entry point: statements, status, how to reproduce
├── result.toml        authoritative metadata (section 4)
├── CITATION.cff
├── CHANGELOG.md
├── paper/             main.tex, preamble.tex, macros.tex, sections/, references.bib,
│                      latexmkrc, main.pdf (the committed PDF is built from the committed sources)
├── lean/              lean-toolchain, lakefile.toml, lake-manifest.json, sources
└── logs/              README.md, ai-contributions.md (required); timeline.md,
                       insights.md, obstructions.md, verification.md, attempts/,
                       experiments/ (scripts and certificates)
```

* Create a contribution by copying `templates/result/`, `templates/paper/` (into
  `paper/`) and `templates/logs/` (into `logs/`); templates are copied, never
  referenced. Record the template version in `result.toml` (`template_version`).
* Names follow [docs/naming-conventions.md](docs/naming-conventions.md): directory
  `AF-NNNN-<subject>-<property>`, Lake package `axiomforge-afNNNN`, Lean root module
  `AxiomForge.AFNNNN`, release tag `af-NNNN-vMAJOR.MINOR.PATCH`.
* Do not add files outside a contribution without a reason that concerns the whole
  archive (a policy, a template, the archive tool). Repository-level files never carry
  mathematics.

## 4. `result.toml`

`templates/result/result.toml` lists every field. `scripts/afm.py check` requires:

| Field | Requirement |
|---|---|
| `id` | `AF-NNNN`; the directory name is `<id>-<slug>` |
| `slug`, `title`, `version`, `date`, `status`, `summary`, `template_version` | non-empty; `version` is `MAJOR.MINOR.PATCH`; `status` is `published`, `preprint` or `withdrawn` |
| `title` | appears verbatim in the manuscript (ignoring braces, backslashes, `$` and case) |
| `msc_primary`, `msc_secondary` | existing MSC2020 classifications (not section headings), no duplicates, identical to the manuscript's `\subjclass[2020]` |
| `authors` | non-empty |
| `[disclosure]` | `summary` and `ai_systems` non-empty |
| `[[theorem]]` | at least one; each has `key` (the theorem's LaTeX `\label`), `statement`, `lean` (a unique, fully qualified declaration name; may be `""` only in a preprint whose `formalization` is not `complete`) and optionally `lean_conditional` (a list of declarations named `..._of_<hypotheses>`, built and axiom-audited, never accepted as `lean`) |
| `[theorem.verification]` | one value per dimension of the [verification policy](docs/verification-policy.md) |

For `status = "published"` every theorem must pass every gate: `proof = "complete"`,
`certificates` in {`not-applicable`, `reproduced`, `formally-checked`},
`formalization = "complete"`, `build = "passing"`, `axioms = "standard"`,
`statement_review = "checked"`, `literature_review = "checked"`.
`independent_review` (`pending`, `ai-internal`, `human`) is not a gate but must be
recorded as it actually is.

`status` takes three values:

* `published`: level V4, the gate above. The first published version is `1.0.0`.
* `preprint`: a complete written argument whose Lean development may be in preparation.
  Its main theorems are not established by the archive until V4. Every theorem must pass
  the preprint gate: `proof` in {`candidate`, `complete`}; `certificates` in
  {`not-applicable`, `reproduced`, `formally-checked`}; `formalization` in
  {`in-preparation`, `statement-only`, `partial`, `complete`};
  `build = "passing"` and `axioms = "standard"` whenever the theorem names a declaration
  to audit (`lean` or `lean_conditional`); `literature_review = "checked"`;
  `statement_review` in {`pending`, `checked`}; `independent_review` recorded honestly.
  `version` is `0.MINOR.PATCH`, and page 1 of the PDF must say "Preprint". A published
  contribution never returns to preprint.
* `withdrawn`: see [docs/publication-policy.md](docs/publication-policy.md).

The full rules are in the [preprint tier](docs/verification-policy.md#preprint-tier).

## 5. The archive tool and its checks

`scripts/afm.py` needs Python 3.11 or later and nothing else (`pdftotext`, `pdfinfo` and
`pdffonts` from poppler-utils enable the PDF layout checks). Exit status: 0 success,
1 check failure, 2 usage or environment error.

| Command | What it does |
|---|---|
| `python3 scripts/afm.py list` | list contributions |
| `python3 scripts/afm.py check [AF-NNNN ...]` | metadata, required files, publication gate, Lean source scan, self-containment, placeholders; no builds |
| `python3 scripts/afm.py lean AF-NNNN [--no-build]` | `lake exe cache get`, `lake build`, orphan-module check, `#print axioms` for every theorem in `result.toml` |
| `python3 scripts/afm.py paper AF-NNNN [--no-build]` | `latexmk`, log checks, PDF layout checks |
| `python3 scripts/afm.py verify AF-NNNN` | `check` + `lean` + `paper` |
| `python3 scripts/afm.py isolate AF-NNNN` | copies the contribution to a fresh temporary directory and runs `verify` there |
| `python3 scripts/afm.py catalogue [--check]` | regenerates `catalogue/*.md`; `--check` fails if they are stale |

The `Makefile` wraps these commands: `make check`, `make catalogue`,
`make catalogue-check`, and `make verify|isolate|lean|paper RESULT=AF-NNNN`
(`make help` lists them). `make test` runs the archive tool's test suite in `tests/`; it
needs a Python with pytest (`make test PYTHON=<interpreter>`). A change to
`scripts/afm.py` comes with tests and never weakens a check.

`check` reports an error for: a missing required file (`README.md`, `result.toml`,
`CITATION.cff`, `CHANGELOG.md`, `paper/main.tex`, `paper/main.pdf`,
`paper/references.bib`, `lean/lean-toolchain`, `lean/lakefile.toml`,
`lean/lake-manifest.json`, `logs/README.md`, `logs/ai-contributions.md`); any violation
of section 4 (commented-out LaTeX does not count); a forbidden Lean construct
(section 6); a symbolic link; a LaTeX `\input`, `\include`, `\includegraphics`,
`\bibliography` (or similar) whose target is absolute or lies outside the contribution;
an absolute local path in a text file; a Lake dependency given by local path, without a
pinned `rev`, or pinned to a moving branch (`main`, `master`, …); a `TODO`, `FIXME`,
`XXX`, `TBD`, `???` or `<<...>>` placeholder on a non-comment line of a `.tex` file; an
unfilled template placeholder `<<...>>` in a `.md`, `.toml`, `.cff`, `.bib` or `.txt`
file.

`paper` reports an error for: a failed build; undefined references or citations;
duplicate labels; missing files; an overfull box wider than 10pt (warning above 1pt);
a PDF whose page 1 lacks the abstract, the MSC classification or the short AI disclosure,
whose page 2 lacks the table of contents, whose introduction does not start after the
contents on a new page, which lacks the *AI-assisted research disclosure* section, or
which has a non-embedded font; and, for a preprint, a page 1 without the word
"Preprint".

## 6. Lean rules

Full policy: [docs/formalization-policy.md](docs/formalization-policy.md).

* **Trust policy.** `#print axioms` of every main theorem must report a subset of
  `propext`, `Classical.choice`, `Quot.sound`.
* **Forbidden in any Lean source** (comments excepted; the check is textual): `sorry`,
  `sorryAx`, `admit`, `axiom` declarations, `native_decide`, `implemented_by`, `extern`,
  `set_option debug.skipKernelTC`.
* Every `.lean` file must be imported, directly or transitively, by a library root of
  `lakefile.toml`; unused files fail the check.
* Pin the toolchain in `lean-toolchain` and every dependency by an exact commit `rev` in
  `lakefile.toml` (never a branch name); commit `lake-manifest.json`.
* A theorem that assumes unproved hypotheses is named after them (for example
  `..._of_estimates`) and is never listed as the formalization of a main theorem.
* `lake build` passing is not evidence of a proof; the axiom audit and the statement
  review are.

## 7. Manuscript rules

Full guide: [docs/mathematical-writing.md](docs/mathematical-writing.md). Specimen:
[docs/manuscript-sample/](docs/manuscript-sample/).

* Start from `templates/paper/`; keep `preamble.tex` (packages and series style, no
  mathematical notation) separate from `macros.tex` (the paper's own notation).
* Page architecture: title page (title, author, abstract, MSC2020, keywords, date,
  identifier, repository, short AI disclosure); table of contents on page 2; the
  introduction on a fresh page; body; appendices; then the unnumbered sections
  *Reproducibility and formal verification*, *Acknowledgements*, *AI-assisted research
  disclosure*; references.
* Every main theorem carries the `\label` recorded as its `key` in `result.toml`;
  labels follow `<kind>:<topic>`.
* Every bibliography entry is verified against the original source. Never invent a
  reference, a theorem number or a page.
* Commit `main.pdf` built from the committed sources.

## 8. Classification, disclosure and attribution

* **MSC2020 is mandatory**: `\subjclass[2020]{Primary …; Secondary …}` in the manuscript,
  the same codes in `result.toml`, validated against `scripts/data/msc2020.tsv`.
* **Author**: AxiomForge. Correspondence: axiomforge.math@gmail.com.
* **AI disclosure** follows [docs/ai-disclosure-policy.md](docs/ai-disclosure-policy.md):
  name each AI system and its role; state the human role and the review status exactly
  as they are; never present AI review as independent certification.
* Credit prior work precisely; reused machinery is cited and, if code, copied with its
  licence and provenance.

## 9. Changing the repository

* Policies, templates and the archive tool change only with a clear rationale; keep
  existing contributions valid (they own copies of their templates and never change when
  templates do).
* After any change to `results/`, run `python3 scripts/afm.py check` and
  `python3 scripts/afm.py catalogue --check`; regenerate the catalogue with
  `python3 scripts/afm.py catalogue` instead of editing it.
* Keep commits focused, with messages that say what changed and why. Never commit
  build outputs other than `paper/main.pdf` (see `.gitignore`).
* Use the pull-request template in `.github/pull_request_template.md`.
