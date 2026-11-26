"""End-to-end axiom audits of tiny Lake packages without Mathlib (``@pytest.mark.lean``).

One package with several theorems is built once per module; audits then run against it
without rebuilding. The orphan check needs a build of its own package.
"""

from __future__ import annotations

import subprocess

import pytest

from archive_factory import make_lean_package

pytestmark = pytest.mark.lean

AUDIT_LEAN = """/-! Synthetic theorems for the axiom audit. -/

namespace Audit

theorem clean : (2 : Nat) + 2 = 4 := rfl

theorem with_sorry : (2 : Nat) + 2 = 5 := by sorry

axiom bogus : False

theorem with_axiom : (1 : Nat) = 2 := bogus.elim

theorem with_classical (p : Prop) : p ∨ ¬p := Classical.em p

theorem with_propext (p q : Prop) (h : p ↔ q) : p = q := propext h

end Audit
"""


@pytest.fixture(scope="module")
def audit_pkg(tmp_path_factory):
    d = make_lean_package(tmp_path_factory.mktemp("lean") / "audit", {"Audit.lean": AUDIT_LEAN}, lib="Audit")
    r = subprocess.run(["lake", "build"], cwd=d, capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, r.stdout + r.stderr
    return d


def test_clean_theorem_has_no_axioms(afm, audit_pkg):
    rep = afm.lean_audit(audit_pkg, ["Audit.clean"], build=False)
    assert rep.ok and rep.notes == ["Audit.clean: axioms ['(none)']"]


def test_sorry_is_rejected(afm, audit_pkg):
    rep = afm.lean_audit(audit_pkg, ["Audit.with_sorry"], build=False)
    assert rep.errors == ["Audit.with_sorry: non-standard axioms ['sorryAx']"]


def test_custom_axiom_is_rejected(afm, audit_pkg):
    rep = afm.lean_audit(audit_pkg, ["Audit.with_axiom"], build=False)
    assert rep.errors == ["Audit.with_axiom: non-standard axioms ['Audit.bogus']"]


def test_standard_axioms_pass(afm, audit_pkg):
    rep = afm.lean_audit(audit_pkg, ["Audit.with_classical", "Audit.with_propext"], build=False)
    assert rep.ok, rep.render()
    assert "Audit.with_classical: axioms ['Classical.choice', 'Quot.sound', 'propext']" in rep.notes
    assert "Audit.with_propext: axioms ['propext']" in rep.notes


def test_missing_declaration_is_reported(afm, audit_pkg):
    rep = afm.lean_audit(audit_pkg, ["Audit.clean", "Audit.does_not_exist"], build=False)
    assert not rep.ok
    assert "Audit.does_not_exist" in rep.errors[0]


def test_mixed_verdicts(afm, audit_pkg):
    rep = afm.lean_audit(audit_pkg, ["Audit.clean", "Audit.with_sorry", "Audit.with_classical"], build=False)
    assert rep.errors == ["Audit.with_sorry: non-standard axioms ['sorryAx']"]
    assert len(rep.notes) == 2


def test_probe_file_is_cleaned_up(afm, audit_pkg):
    afm.lean_audit(audit_pkg, ["Audit.clean"], build=False)
    assert sorted(p.name for p in audit_pkg.glob("*.lean")) == ["Audit.lean"]


def test_source_scan_flags_the_same_package(afm, audit_pkg):
    out = afm.lean_source_problems(audit_pkg)
    assert any("(sorry)" in o for o in out) and any("(axiom declaration)" in o for o in out)


def test_build_and_orphan_module(afm, tmp_path):
    d = make_lean_package(tmp_path / "orphan", {
        "Sample.lean": "import Sample.Used\n",
        "Sample/Used.lean": "theorem Sample.used : True := trivial\n",
        "Sample/Forgotten.lean": "theorem Sample.forgotten : True := trivial\n",
    })
    rep = afm.lean_audit(d, ["Sample.used"], build=True)
    assert "lake build: passing" in rep.notes
    assert rep.errors == ["Lean module Sample.Forgotten is not imported by any library root"]


def test_build_failure_is_reported(afm, tmp_path):
    d = make_lean_package(tmp_path / "broken", {"Sample.lean": "theorem t : (1 : Nat) = 2 := rfl\n"})
    rep = afm.lean_audit(d, ["t"], build=True)
    assert rep.errors and rep.errors[0].startswith("lake build failed")


def test_module_system_package(afm, tmp_path):
    d = make_lean_package(tmp_path / "modsys", {
        "Sample.lean": "module\n\npublic import Sample.A\n",
        "Sample/A.lean": "module\n\npublic theorem Sample.a : True := trivial\n",
    })
    rep = afm.lean_audit(d, ["Sample.a"], build=True)
    assert rep.ok, rep.render()
