## Summary

<!-- What changes and why, in two or three sentences. -->

## Kind of change

- [ ] Correction or erratum to a published contribution (identifier and version: )
- [ ] New version of a published contribution (identifier, old → new version: )
- [ ] Policy or documentation
- [ ] Template
- [ ] Archive tool (`scripts/afm.py`)

## Checks

- [ ] `python3 scripts/afm.py check` passes
- [ ] `python3 scripts/afm.py catalogue --check` passes
- [ ] For a changed contribution: `python3 scripts/afm.py verify AF-NNNN` passes, and
      `CHANGELOG.md`, `version` in `result.toml` and `CITATION.cff` are updated
- [ ] No statement of a published theorem changes without a correction notice
      ([publication policy](../docs/publication-policy.md))
- [ ] Verification statuses in `result.toml` describe checks that were actually run
- [ ] AI involvement in this change is disclosed where the policy requires it
- [ ] Only public material: no references to unpublished work, internal tooling,
      local paths or credentials
