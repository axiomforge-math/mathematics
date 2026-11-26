# Lean package template

Copy this directory to `results/AF-NNNN-<slug>/lean/` and replace `NNNN` by the four digits
of the identifier everywhere: in `lakefile.toml` (`name`, `defaultTargets`, `lean_lib`), in
`lake-manifest.json` (`name`), in the file names `AxiomForge/AFNNNN.lean` and
`AxiomForge/AFNNNN/`, and in the module and namespace names inside the sources.

| File | Content |
|---|---|
| `lean-toolchain` | the exact Lean release |
| `lakefile.toml` | package `axiomforge-afNNNN`, library root `AxiomForge.AFNNNN`, Mathlib pinned to an exact commit |
| `lake-manifest.json` | Mathlib and its dependencies resolved to exact commits |
| `AxiomForge/AFNNNN.lean` | library root: imports every module of the package |
| `AxiomForge/AFNNNN/*.lean` | sources, each starting with a module docstring `/-! … -/` |

The pinned versions are `leanprover/lean4:v4.34.0-rc1` and Mathlib
`f385f9fd18abed332ebcd3df239cb357e264aceb`. A contribution may pin other versions; then
update `lean-toolchain`, the `rev` in `lakefile.toml`, and regenerate the manifest with
`lake update`.

## Build

```bash
lake exe cache get    # download the Mathlib build cache for the pinned revision
lake build            # build every module of the package
```

## Axiom audit

Compile a probe file outside the package with `lake env lean`:

```lean
import AxiomForge.AFNNNN

#print axioms AxiomForge.AFNNNN.some_theorem
```

Every main theorem must depend only on `propext`, `Classical.choice` and `Quot.sound`.
See `docs/formalization-policy.md` for the full trust policy (no `sorry`, `admit`,
`axiom`, `native_decide`, `implemented_by`, `extern`; every file imported by the root).
