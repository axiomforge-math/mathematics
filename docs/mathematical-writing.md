# Mathematical writing

How AxiomForge manuscripts are written and laid out. The canonical template is
[`templates/paper/`](../templates/paper/); a compiled specimen is in
[`manuscript-sample/`](manuscript-sample/). The archive tool enforces the mechanical
parts (section 6); the rest is the responsibility of the authors and reviewers.

## 1. Principles

1. **The manuscript is the proof.** It proves every advertised statement from cited
   external results. No step is deferred to the Lean code, to the logs, to "a computer
   check" without a stated certificate, or to future work.
2. **State exactly what is proved.** Hypotheses, ranges of parameters, constants and
   quantifiers are explicit. A conditional result is labelled as such in its statement.
3. **Separate the established from the heuristic.** Numerical evidence, heuristics and
   conjectures are labelled as remarks, never mixed into proofs.
4. **Write for a mathematician outside the subfield.** Define every non-standard notion
   before use; recall standard ones with a reference.

## 2. Structure

| Part | Content |
|---|---|
| Title page | title, author (AxiomForge), abstract, MSC2020, keywords, date, identifier, repository, short AI disclosure |
| Contents | table of contents, on page 2 |
| 1. Introduction | on a fresh page: the main theorem within its first page; what was known (with references); what is new; the idea of the proof; the plan of the paper |
| Body | definitions, auxiliary results, proofs, in logical order |
| Appendices | computations, certificates and routine verifications that would interrupt the argument |
| Reproducibility and formal verification | unnumbered: Lean declarations of the main theorems, toolchain and Mathlib revision, axiom audit, commands reproducing every certificate |
| Acknowledgements | unnumbered |
| AI-assisted research disclosure | unnumbered: see the [AI disclosure policy](ai-disclosure-policy.md) |
| References | `amsplain`, from `references.bib` |

The template provides the commands that produce this layout: `\affrontmatter` (title page,
publication block, contents, page breaks) and `\afbacksection` (unnumbered back-matter
sections).

## 3. Statements and proofs

* Use the environments of the preamble: `theorem`, `proposition`, `lemma`, `corollary`
  (sharing one counter, numbered within sections), `definition`, `example`, `remark`.
* Every main theorem has a `\label` that is recorded as its `key` in `result.toml`, and
  the manuscript names the Lean declaration that formalizes it.
* Begin each proof by saying what it proves when this is not the immediately preceding
  statement. End it with the proof's actual conclusion, not with a computation.
* Quote external theorems with their exact hypotheses, the precise source (author,
  title, theorem number, page) and, when the statement is adapted, the adaptation.
* Numerical constants that matter for the argument are exact rationals or rigorous
  enclosures, with a pointer to the certificate that establishes them.

## 4. Notation and macros

* `preamble.tex` fixes the typographic identity of the series (packages, page geometry,
  theorem environments, publication metadata). It defines no mathematical notation and is
  not edited for a single paper except to add a package the paper needs.
* `macros.tex` holds the paper's own notation. Define a macro only when it materially
  simplifies the exposition or guarantees consistency; name it after the object
  (`\Li`, not `\myfunc`).
* Fix each symbol once. Do not reuse a letter for two objects in the same section.
* Use `\coloneqq` for definitions, `\lvert…\rvert` and `\lVert…\rVert` for absolute
  values and norms, `\operatorname` for named operators.

## 5. Cross-references and citations

* Labels follow `<kind>:<topic>` with kinds `thm`, `prop`, `lem`, `cor`, `def`, `rem`,
  `sec`, `eq`, `app` (for example `\label{prop:prime-index-nonvanishing}`).
* Refer with `\cref`/`\Cref` (cleveref), equations with `\eqref` or `\cref`.
* Every entry of `references.bib` is verified against the original source: authors,
  title, venue, year, volume, pages, DOI or arXiv identifier. Never invent or
  reconstruct bibliographic data from memory.
* Cite preprints as preprints, with their identifier and version.

## 6. Mechanical requirements (checked)

`python3 scripts/afm.py check` and `python3 scripts/afm.py paper AF-NNNN` enforce:

* `\subjclass[2020]{Primary …; Secondary …}` with the same codes as `result.toml`;
* the title of `result.toml` appears verbatim in the manuscript;
* every theorem `key` of `result.toml` is a `\label` of the manuscript;
* no placeholder (`TODO`, `FIXME`, `XXX`, `TBD`, `???`, `<<...>>`) outside comment lines;
* no `\input`, `\include`, `\includegraphics` or `\bibliography` outside the contribution;
* a clean build: no undefined reference or citation, no duplicate label, no missing file,
  no overfull box wider than 10pt;
* the page architecture of section 2 (abstract, MSC and short AI disclosure on page 1,
  contents on page 2, introduction on a later page, the disclosure section present) and
  embedded fonts.

## 7. Style

* Prefer short declarative sentences. Avoid "clearly", "obviously" and "it is easy to
  see" unless the step really is immediate; otherwise give the step.
* Do not begin a sentence with a symbol. Punctuate displayed formulas as part of the
  sentence.
* Avoid promotional language ("groundbreaking", "powerful new method"). State what is new
  and let the mathematics speak.
* Spelling: consistent within a manuscript; the series uses Oxford spelling
  (-ize endings, "catalogue", "behaviour").

## 8. References

* N. J. Higham, *Handbook of Writing for the Mathematical Sciences*, 3rd ed., SIAM, 2020.
* P. R. Halmos, "How to write mathematics", *L'Enseignement Mathématique* 16 (1970).
* AMS Author Resource Center: <https://www.ams.org/publications/authors/authors>.
* The `amsart` class (amscls): <https://ctan.org/pkg/amscls>; cleveref:
  <https://ctan.org/pkg/cleveref>; mathtools: <https://ctan.org/pkg/mathtools>.
* MSC2020: <https://msc2020.org/>.
