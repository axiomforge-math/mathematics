# Catalogue

Generated views of the archive. **Never edit these files by hand**: they are produced by
`python3 scripts/afm.py catalogue` (or `make catalogue`) from `results/*/result.toml`, and
`python3 scripts/afm.py catalogue --check` fails when they are stale.

| File | Content |
|---|---|
| [results.md](results.md) | every contribution: identifier, title, primary MSC2020 class, version, status |
| [topics.md](topics.md) | contributions grouped by MSC2020 class (primary and secondary) |
| [verification.md](verification.md) | every main theorem with its Lean declaration and verification status |

The authoritative record of a contribution is its own `result.toml`; the catalogue only
summarises it.
