# Naming conventions

Names are permanent. A name that is chosen carefully once never has to be explained,
migrated or apologised for.

## General rules

1. **Describe the mathematics, not the process.** A name says *what* an object is, never
   *how* or *when* it was produced. Forbidden in names: `final`, `new`, `v2`, `fixed`,
   `UNVERIFIED`, `candidate`, `iteration4`, model names, session numbers, dates of AI
   runs. Status and history live in metadata and logs, not in file names.
2. **ASCII only, lower-case kebab-case** for directories and documents:
   `dilogarithm-irrationality`, `verification-policy.md`. No spaces, no `±`, no `^`, no
   uppercase except where a language convention requires it (below).
3. **Spell signs and fractions out** when a number appears in a name:
   `minus-two-sevenths`, `two-elevenths`, `k-over-five`. Never `-2_7`, `pm`, `2_11`.
4. **Stable identifiers are opaque and never reused.** Once allocated, an identifier
   keeps its meaning forever, even if the object is withdrawn or superseded.
5. **One concept, one name.** Do not alternate between synonyms (`cert`, `certificate`,
   `witness`) for the same kind of file.

## Public archive

| Object | Convention | Example |
|---|---|---|
| Result identifier | `AF-NNNN`, allocated sequentially at publication | `AF-0001` |
| Result directory | `results/AF-NNNN-<subject>-<property>/` | `results/AF-0001-dilogarithm-irrationality/` |
| Release tag | `af-NNNN-vMAJOR.MINOR.PATCH` | `af-0001-v1.0.0` |
| Lean package (Lake) | `axiomforge-afNNNN` | `axiomforge-af0001` |
| Lean library / root module | `AxiomForge.AFNNNN` | `AxiomForge.AF0001.MainTheorems` |
| Lean declarations | Mathlib style: `lowerCamelCase` for terms, `snake_case` for theorems | `irrational_dilog_two_elevenths` |
| Manuscript entry point | `paper/main.tex` → `paper/main.pdf` | |
| Manuscript sections | `paper/sections/<topic>.tex` (as in `templates/paper/`) | `paper/sections/arithmetic-estimates.tex` |
| Certificates | `logs/experiments/certificates/<target>-<quantity>.json` | `two-elevenths-arithmetic-profile.json` |
| Scripts | `logs/experiments/scripts/<verb>_<object>.py` (snake_case, a Python module) | `verify_arithmetic_profile.py` |
| Research attempt | `logs/attempts/NNN-<short-title>.md` | `logs/attempts/003-separated-border-nodes.md` |

Result slugs name the subject and the property: `dilogarithm-irrationality`,
`trigamma-fifths-irrationality`, `legendre-chi-inverse-tangent-irrationality`.

## Code

* Python: modules and functions `snake_case`, classes `CapWords`, constants `UPPER_CASE`.
* Lean: follow the Mathlib naming conventions
  (<https://leanprover-community.github.io/contribute/naming.html>).
* LaTeX labels: `<kind>:<topic>` with kinds `thm`, `prop`, `lem`, `cor`, `def`, `rem`,
  `sec`, `eq`, `app`, e.g. `\label{prop:prime-index-nonvanishing}`.
