"""Parsing of ``#print axioms`` output, Lake library roots and orphan modules (no Lean needed)."""

from __future__ import annotations

import pytest

from archive_factory import make_lean_package

REPORT = """'Sample.clean' does not depend on any axioms
'Sample.classical' depends on axioms: [propext, Classical.choice, Quot.sound]
'Sample.cheat' depends on axioms: [sorryAx]
'Sample.long' depends on axioms: [propext,
 Classical.choice,
 Quot.sound,
 Sample.myAxiom]
'clean' does not depend on any axioms
"""


def test_parse_axiom_report(afm):
    found = afm.parse_axiom_report(REPORT, ["Sample.clean", "Sample.classical", "Sample.cheat", "Sample.long",
                                            "Sample.missing"])
    assert found["Sample.clean"] == set()
    assert found["Sample.classical"] == {"propext", "Classical.choice", "Quot.sound"}
    assert found["Sample.cheat"] == {"sorryAx"}
    assert found["Sample.long"] == {"propext", "Classical.choice", "Quot.sound", "Sample.myAxiom"}
    assert "Sample.missing" not in found


def test_parse_axiom_report_matches_exact_names(afm):
    """'clean' must not pick up the report of 'Sample.clean' (and vice versa)."""
    text = "'Sample.clean' depends on axioms: [sorryAx]\n"
    assert afm.parse_axiom_report(text, ["clean"]) == {}
    assert afm.parse_axiom_report(REPORT, ["clean"]) == {"clean": set()}


def test_parse_axiom_report_regex_metacharacters_in_names(afm):
    text = "'Foo.bar'' depends on axioms: [propext]\n'Fooxbar' depends on axioms: [sorryAx]\n"
    assert afm.parse_axiom_report(text, ["Foo.bar'"]) == {"Foo.bar'": {"propext"}}
    assert afm.parse_axiom_report(text, ["Foo.bar"]) == {}


def test_standard_axioms(afm):
    assert afm.STANDARD_AXIOMS == {"propext", "Classical.choice", "Quot.sound"}


def test_lake_roots(afm, tmp_path):
    d = make_lean_package(tmp_path / "p", lib="Alpha")
    assert afm.lake_roots(d) == ["Alpha"]
    (d / "lakefile.toml").write_text('name = "x"\n[[lean_lib]]\nname = "A"\nroots = ["A.One", "A.Two"]\n'
                                     '[[lean_lib]]\nname = "B"\n')
    assert afm.lake_roots(d) == ["A.One", "A.Two", "B"]


def test_no_orphans(afm, tmp_path):
    d = make_lean_package(tmp_path / "p", {"Sample.lean": "import Sample.A\nimport Sample.B\n",
                                            "Sample/A.lean": "import Sample.C\ntheorem a : True := trivial\n",
                                            "Sample/B.lean": "theorem b : True := trivial\n",
                                            "Sample/C.lean": "theorem c : True := trivial\n"})
    assert afm.orphan_modules(d) == []


def test_orphan_module_reported(afm, tmp_path):
    d = make_lean_package(tmp_path / "p", {"Sample.lean": "import Sample.A\n",
                                            "Sample/A.lean": "theorem a : True := trivial\n",
                                            "Sample/Forgotten.lean": "theorem f : True := trivial\n",
                                            "Sample/Deep/Also.lean": "theorem g : True := trivial\n"})
    assert afm.orphan_modules(d) == ["Lean module Sample.Deep.Also is not imported by any library root",
                                     "Lean module Sample.Forgotten is not imported by any library root"]


def test_import_in_comment_does_not_count(afm, tmp_path):
    d = make_lean_package(tmp_path / "p", {"Sample.lean": "-- import Sample.A\n/-\nimport Sample.B\n-/\n",
                                            "Sample/A.lean": "", "Sample/B.lean": ""})
    assert len(afm.orphan_modules(d)) == 2


@pytest.mark.parametrize("header", ["module\n\npublic import Sample.A\n", "module\nimport all Sample.A\n",
                                    "module\npublic meta import Sample.A\n", "  import Sample.A\n"])
def test_module_system_imports_are_followed(afm, tmp_path, header):
    """Regression: `public import` (Lean module system) was not recognised, so every module
    imported that way was reported as an orphan."""
    d = make_lean_package(tmp_path / "p", {"Sample.lean": header, "Sample/A.lean": "module\n"})
    assert afm.orphan_modules(d) == []


def test_import_cycle_terminates(afm, tmp_path):
    d = make_lean_package(tmp_path / "p", {"Sample.lean": "import Sample.A\n", "Sample/A.lean": "import Sample.B\n",
                                            "Sample/B.lean": "import Sample.A\n"})
    assert afm.orphan_modules(d) == []


def test_external_imports_and_lake_dir_ignored(afm, tmp_path):
    d = make_lean_package(tmp_path / "p", {"Sample.lean": "import Mathlib.Tactic\nimport Sample.A\n",
                                            "Sample/A.lean": "", ".lake/packages/m/Mathlib.lean": ""})
    assert afm.orphan_modules(d) == []


def test_lakefile_lean_is_not_a_module(afm, tmp_path):
    d = make_lean_package(tmp_path / "p", {"Sample.lean": "", "lakefile.lean": "import Lake\n"})
    assert afm.orphan_modules(d) == []


def test_lean_audit_without_theorems(afm, tmp_path, monkeypatch):
    d = make_lean_package(tmp_path / "p")
    monkeypatch.setattr(afm.shutil, "which", lambda name: "/usr/bin/" + name)
    rep = afm.lean_audit(d, [], build=False)
    assert rep.errors == ["no main theorems to audit"]


@pytest.mark.parametrize("name", ["Sample.t\n#eval IO.println 1", "a b", "x;y", ""])
def test_lean_audit_rejects_injected_names(afm, tmp_path, monkeypatch, name):
    """Theorem names are spliced into a Lean file; a crafted name must never inject commands."""
    d = make_lean_package(tmp_path / "p")
    calls = []
    monkeypatch.setattr(afm.shutil, "which", lambda n: "/usr/bin/" + n)
    monkeypatch.setattr(afm, "run", lambda *a, **k: calls.append(a) or None)
    rep = afm.lean_audit(d, [name], build=False)
    assert any("invalid Lean declaration names" in e for e in rep.errors)
    assert calls == []


def test_lean_audit_without_lake(afm, tmp_path, monkeypatch):
    monkeypatch.setattr(afm.shutil, "which", lambda name: None)
    rep = afm.lean_audit(make_lean_package(tmp_path / "p"), ["Sample.main_theorem"])
    assert rep.errors and "lake not found" in rep.errors[0]


class _Proc:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr


@pytest.mark.parametrize("output,ok,needle", [
    ("'Sample.main_theorem' does not depend on any axioms\n", True, "axioms ['(none)']"),
    ("'Sample.main_theorem' depends on axioms: [propext, Quot.sound]\n", True, "axioms ['Quot.sound', 'propext']"),
    ("'Sample.main_theorem' depends on axioms: [sorryAx]\n", False, "non-standard axioms ['sorryAx']"),
    ("'Sample.main_theorem' depends on axioms: [propext, Sample.bad]\n", False, "non-standard axioms ['Sample.bad']"),
    ("", False, "no axiom report (declaration missing?)"),
])
def test_lean_audit_verdict_from_probe_output(afm, tmp_path, monkeypatch, output, ok, needle):
    d = make_lean_package(tmp_path / "p")
    monkeypatch.setattr(afm.shutil, "which", lambda n: "/usr/bin/" + n)
    monkeypatch.setattr(afm, "run", lambda cmd, cwd, **k: _Proc(0, output))
    rep = afm.lean_audit(d, ["Sample.main_theorem"], build=False)
    assert rep.ok is ok
    assert any(needle in x for x in rep.errors + rep.notes), (rep.errors, rep.notes)
    assert not list(d.glob("tmp*.lean")), "the probe file must be removed"


def test_lean_audit_probe_failure(afm, tmp_path, monkeypatch):
    d = make_lean_package(tmp_path / "p")
    monkeypatch.setattr(afm.shutil, "which", lambda n: "/usr/bin/" + n)
    monkeypatch.setattr(afm, "run", lambda cmd, cwd, **k: _Proc(1, "", "probe.lean:2:14: error: Unknown constant `X`"))
    rep = afm.lean_audit(d, ["X"], build=False)
    assert rep.errors and rep.errors[0].startswith("axiom probe failed") and "Unknown constant" in rep.errors[0]


def test_lean_audit_build_failure(afm, tmp_path, monkeypatch):
    d = make_lean_package(tmp_path / "p")
    monkeypatch.setattr(afm.shutil, "which", lambda n: "/usr/bin/" + n)
    monkeypatch.setattr(afm, "run", lambda cmd, cwd, **k: _Proc(1, "error: Sample.lean:3: type mismatch"))
    rep = afm.lean_audit(d, ["Sample.main_theorem"], build=True)
    assert rep.errors[0].startswith("lake build failed") and "type mismatch" in rep.errors[0]


def test_lean_audit_runs_cache_get_only_for_mathlib(afm, tmp_path, monkeypatch):
    calls = []

    def fake(cmd, cwd, **k):
        calls.append(cmd)
        return _Proc(0, "'Sample.main_theorem' does not depend on any axioms\n")
    monkeypatch.setattr(afm.shutil, "which", lambda n: "/usr/bin/" + n)
    monkeypatch.setattr(afm, "run", fake)
    d = make_lean_package(tmp_path / "p")
    afm.lean_audit(d, ["Sample.main_theorem"], build=True)
    assert ["lake", "exe", "cache", "get"] not in calls and ["lake", "build"] in calls
    calls.clear()
    d2 = make_lean_package(tmp_path / "q", extra_lakefile='\n[[require]]\nname = "mathlib"\nscope = "x"\nrev = "v1"\n')
    afm.lean_audit(d2, ["Sample.main_theorem"], build=True)
    assert calls[0] == ["lake", "exe", "cache", "get"]
