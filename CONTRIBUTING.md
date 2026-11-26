# Contributing

AxiomForge publishes its contributions in this archive after they meet the
[verification policy](docs/verification-policy.md). Readers help most by finding errors.

## Reporting an error

Open an issue at <https://github.com/axiomforge-math/mathematics/issues> or write to
axiomforge.math@gmail.com. Please give:

1. the identifier and version of the contribution (`AF-NNNN`, `vMAJOR.MINOR.PATCH`);
2. the exact location: manuscript section, theorem or equation number, page; Lean file
   and declaration; or log file;
3. what is wrong, and why: a counterexample, a gap in an argument, a misquoted
   reference, a mismatch between a Lean statement and the manuscript, a failing build;
4. how you checked it (commands, versions, environment), if computational.

Every substantiated report receives a public answer. Corrections and withdrawals follow
the [publication policy](docs/publication-policy.md); reporters are acknowledged in the
contribution's `CHANGELOG.md` unless they ask otherwise.

## Pull requests

Pull requests are welcome for:

* typographical and expository corrections to documentation;
* reproducibility fixes (for example a build that fails on a supported platform);
* improvements to `scripts/afm.py` that keep it dependent on the Python standard library
  only and never weaken a check.

A pull request that changes a published contribution must update its `CHANGELOG.md`,
the `version` in `result.toml` and its `CITATION.cff`, and pass
`python3 scripts/afm.py verify AF-NNNN`. Statements of published theorems are never
changed silently. Fill in the checklist of `.github/pull_request_template.md`.

New mathematical contributions are added by AxiomForge once they meet every gate. If you
have a result or an improvement to propose, open an issue first.

## Conventions

* Read [AGENTS.md](AGENTS.md) (the instructions for every agent and contributor),
  [docs/naming-conventions.md](docs/naming-conventions.md) and
  [docs/mathematical-writing.md](docs/mathematical-writing.md).
* Commit messages: an imperative summary line of at most 72 characters, then a body
  explaining what changed and why when this is not obvious.
* AI assistance in a contribution must be disclosed as described in the
  [AI disclosure policy](docs/ai-disclosure-policy.md).
* Do not commit secrets, local paths or build outputs (other than `paper/main.pdf`).
