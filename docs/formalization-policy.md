# Formalization policy

Every main theorem of a published contribution is formalized in Lean 4 and checked by
the Lean kernel against a pinned revision of Mathlib. This document states what that
means and how it is checked. The status vocabulary is defined in the
[verification policy](verification-policy.md).

## 1. The Lean package

Each contribution has an independent Lake package in `lean/`:

| File | Requirement |
|---|---|
| `lean-toolchain` | an exact Lean release, e.g. `leanprover/lean4:v4.x.y` |
| `lakefile.toml` | package `axiomforge-afNNNN`; library root module `AxiomForge.AFNNNN`; every dependency given by `scope` or `git` (never by local `path`) and pinned by `rev` to an exact commit (never a branch such as `main`) |
| `lake-manifest.json` | committed; resolves every dependency to an exact commit |
| sources | `AxiomForge/AFNNNN/*.lean`, each with a module docstring `/-! ... -/` |

A minimal `lakefile.toml`:

```toml
name = "axiomforge-af0001"
defaultTargets = ["AxiomForge"]

[leanOptions]
autoImplicit = false

[[require]]
name = "mathlib"
scope = "leanprover-community"
rev = "<full 40-character commit hash>"

[[lean_lib]]
name = "AxiomForge"
```

Different contributions may pin different toolchains and Mathlib revisions. A package
never imports another contribution; reused Lean code is copied with attribution.

## 2. Trust policy

A main theorem is **formally verified** only if all of the following hold.

1. **Kernel axioms.** `#print axioms <theorem>` reports a subset of `propext`,
   `Classical.choice`, `Quot.sound`. Anything else fails, in particular `sorryAx`,
   the axioms introduced by `native_decide` (such as `Lean.ofReduceBool`) and any
   declared axiom.
2. **No escape hatches in the sources.** No `sorry`, `sorryAx`, `admit`, `axiom`
   declaration, `native_decide`, `implemented_by`, `extern`, or
   `set_option debug.skipKernelTC`
   anywhere in the package (comments excepted), whether or not a main theorem uses it.
3. **Every file participates.** Each `.lean` source is imported, directly or
   transitively, by a library root, so that the build checks all of it.
4. **Statement fidelity.** A reviewer has compared the Lean statement with the
   manuscript's statement, definition by definition, and recorded
   `statement_review = "checked"`. Particular attention goes to coercions, division by
   zero conventions, natural-number subtraction, ranges of parameters, and definitions
   introduced by the package itself (which must be proved equivalent to the standard
   notion or be the standard Mathlib notion).
5. **Unconditional.** A theorem with unproved hypotheses (estimates, numerical facts,
   external results not in Mathlib) is not a formalization of the main theorem. Such
   theorems may exist as intermediate steps and are named after their hypotheses, for
   example `irrational_of_estimates`; the main theorem is the one with no such
   hypotheses.

## 3. Computations inside Lean

* Use kernel-checked tactics: `decide`, `norm_num`, `rfl`, `simp` with decidable
  arithmetic, `positivity`, `linarith`, `nlinarith`.
* `native_decide` and any other compiler-trusting mechanism are forbidden in published
  packages.
* A large numerical certificate is checked by a verified checker: the checker is a Lean
  function proved correct, and its run on the certificate is evaluated by the kernel.
  Only then may the certificate dimension be recorded as `formally-checked`.

## 4. Style

* Follow the Mathlib naming conventions and style guide (references below):
  `snake_case` theorem names describing the statement (`irrational_dilog_two_elevenths`),
  `lowerCamelCase` for definitions, `UpperCamelCase` for structures and types.
* `autoImplicit` is disabled. State universe and type parameters explicitly.
* Each file begins with a module docstring explaining its mathematical content and its
  place in the proof; each main theorem has a docstring quoting the manuscript statement
  and its label.
* Keep files below roughly 800 lines; split along mathematical boundaries.

## 5. Checking

```bash
cd results/AF-NNNN-<slug>/lean
lake exe cache get        # download the Mathlib build cache
lake build                # build every module
cd ../../..
python3 scripts/afm.py lean AF-NNNN   # build, orphan-module check, axiom audit
python3 scripts/afm.py check AF-NNNN  # includes the textual scan of section 2.2
```

`python3 scripts/afm.py lean` writes a temporary probe file that imports the library
roots and runs `#print axioms` for every `lean` name listed in `result.toml`; it fails if
a declaration is missing or depends on a non-standard axiom.

A passing `lake build` does not, on its own, show that anything was proved; only the
combination of build, axiom audit, source scan and statement review does.

## 6. References

* Mathlib naming conventions: <https://leanprover-community.github.io/contribute/naming.html>
* Mathlib style guide: <https://leanprover-community.github.io/contribute/style.html>
* Mathlib documentation style: <https://leanprover-community.github.io/contribute/doc.html>
* Using Mathlib as a dependency: <https://github.com/leanprover-community/mathlib4/wiki/Using-mathlib4-as-a-dependency>
* Lean reference manual: <https://lean-lang.org/doc/reference/latest/>
