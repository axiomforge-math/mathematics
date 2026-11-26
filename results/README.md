# Results

One directory per published contribution, named `AF-NNNN-<subject>-<property>`
(for example `AF-0001-dilogarithm-irrationality`). Identifiers are allocated
sequentially at publication and never reused.

**No contribution has been published yet.**

Each directory is self-contained: it can be copied anywhere and reproduced with the
commands in its own `README.md`, without anything else from this repository.

| File or directory | Role |
|---|---|
| `README.md` | statements, verification status, reproduction commands |
| `result.toml` | authoritative metadata (read by `scripts/afm.py` and the catalogue) |
| `CITATION.cff`, `CHANGELOG.md` | citation metadata, version history |
| `paper/` | manuscript sources and `main.pdf` |
| `lean/` | independent Lake package |
| `logs/` | curated research history, experiments and certificates |

Structure and rules: [AGENTS.md](../AGENTS.md#3-structure-of-a-contribution),
[docs/architecture.md](../docs/architecture.md). Verification gate:
[docs/verification-policy.md](../docs/verification-policy.md). Reproduction:
[docs/reproducibility.md](../docs/reproducibility.md). Templates:
[templates/result/](../templates/result/), [templates/paper/](../templates/paper/),
[templates/logs/](../templates/logs/).

Check every contribution with `python3 scripts/afm.py check`, one contribution fully
with `python3 scripts/afm.py verify AF-NNNN` (run from the repository root).
