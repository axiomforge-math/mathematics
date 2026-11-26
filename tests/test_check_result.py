"""``check_result``: metadata, files, MSC, manuscript consistency and the publication gate."""

from __future__ import annotations

import os
import re

import pytest

from archive_factory import TITLE, make_result, result_toml
from conftest import abspath

REQUIRED = ["README.md", "result.toml", "CITATION.cff", "CHANGELOG.md", "paper/main.tex", "paper/main.pdf",
            "paper/references.bib", "lean/lean-toolchain", "lean/lakefile.toml", "lean/lake-manifest.json",
            "logs/README.md", "logs/ai-contributions.md"]


@pytest.fixture
def result(tmp_path):
    return make_result(tmp_path / "results")


def errors(afm, d, **kw):
    return afm.check_result(d, **kw).errors


def has(errs, needle):
    return any(needle in e for e in errs)


def set_toml(d, **kw):
    (d / "result.toml").write_text(result_toml(**kw))


def edit(path, old, new, count=1):
    text = path.read_text()
    assert old in text, f"{old!r} not in {path}"
    path.write_text(text.replace(old, new, count))


def test_valid_result_passes(afm, result):
    rep = afm.check_result(result)
    assert rep.errors == [] and rep.ok
    assert "[PASS]" in rep.render()


def test_required_files_list_is_complete(afm):
    assert afm.REQUIRED_FILES == REQUIRED


@pytest.mark.parametrize("rel", REQUIRED)
def test_missing_required_file(afm, result, rel):
    (result / rel).unlink()
    assert has(errors(afm, result), f"missing required file {rel}")


def test_invalid_toml(afm, result):
    (result / "result.toml").write_text('id = "AF-0001\n')
    errs = errors(afm, result)
    assert has(errs, "result.toml is not valid TOML")


@pytest.mark.parametrize("rid", ["AF-1", "af-0001", "AF-00001", "XX-0001", ""])
def test_invalid_id(afm, result, rid):
    set_toml(result, rid=rid)
    assert has(errors(afm, result), "invalid id")


def test_id_directory_mismatch(afm, result):
    set_toml(result, rid="AF-0002")
    errs = errors(afm, result)
    assert has(errs, "does not start with id AF-0002") and has(errs, "directory name must be '<id>-<slug>'")


def test_slug_directory_mismatch(afm, result):
    set_toml(result, slug="other-slug")
    assert has(errors(afm, result), "directory name must be '<id>-<slug>'")


@pytest.mark.parametrize("version", ["1.0", "v1.0.0", "1.0.0-rc1", "1.0.0.0", "one"])
def test_bad_version(afm, result, version):
    edit(result / "result.toml", 'version = "1.0.0"', f'version = "{version}"')
    assert has(errors(afm, result), "version must be MAJOR.MINOR.PATCH")


@pytest.mark.parametrize("field", ["title", "version", "date", "status", "summary", "template_version"])
def test_missing_fields(afm, result, field):
    text = (result / "result.toml").read_text()
    text = re.sub(rf"^{field} = .*\n", "", text, count=1, flags=re.M)
    (result / "result.toml").write_text(text)
    assert has(errors(afm, result), f"missing field {field!r}")


@pytest.mark.parametrize("status", ["draft", "Published", "candidate", "Preprint", "pre-print"])
def test_bad_status(afm, result, status):
    set_toml(result, status=status)
    assert has(errors(afm, result), "status must be 'published', 'preprint' or 'withdrawn'")


@pytest.mark.parametrize("primary,secondary,needle", [
    ("11j72", ["11Y60"], "malformed MSC2020 code '11j72'"),
    ("11J7", ["11Y60"], "malformed"),
    ("11J98", ["11Y60"], "does not exist"),
    ("11-XX", ["11Y60"], "section heading"),
    ("11Jxx", ["11Y60"], "section heading"),
    ("11J72", ["11J72"], "duplicate MSC2020 codes"),
    ("11J72", ["11Y60", "bad"], "malformed MSC2020 code 'bad'"),
])
def test_msc_codes(afm, result, primary, secondary, needle):
    set_toml(result, msc_primary=primary, msc_secondary=secondary)
    assert has(errors(afm, result), needle)


def test_msc_mismatch_with_subjclass(afm, result):
    set_toml(result, msc_secondary=["11J82"])
    errs = errors(afm, result)
    assert has(errs, "MSC codes differ between manuscript ['11J72', '11Y60'] and result.toml ['11J72', '11J82']")


def test_msc_mismatch_missing_secondary_in_manuscript(afm, result):
    edit(result / "paper" / "main.tex", "Secondary 11Y60", "Secondary")
    assert has(errors(afm, result), "MSC codes differ")


def test_subjclass_missing(afm, result):
    edit(result / "paper" / "main.tex", r"\subjclass[2020]", r"\keywords")
    assert has(errors(afm, result), "manuscript lacks \\subjclass[2020]")


def test_subjclass_only_in_a_comment(afm, result):
    """Regression: a commented-out \\subjclass satisfied the check."""
    edit(result / "paper" / "main.tex", r"\subjclass[2020]", r"% \subjclass[2020]")
    assert has(errors(afm, result), "manuscript lacks \\subjclass[2020]")


def test_title_mismatch(afm, result):
    edit(result / "result.toml", f'title = "{TITLE}"', 'title = "A different title"')
    assert has(errors(afm, result), "title does not appear verbatim")


def test_title_normalisation_ignores_braces_and_spacing(afm, tmp_path):
    d = make_result(tmp_path / "r", title="Irrationality of $\\zeta(3)$")
    edit(d / "result.toml", 'title = "Irrationality of $\\\\zeta(3)$"', 'title = "Irrationality   of {\\\\zeta(3)}"')
    assert not has(errors(afm, d), "title does not appear")


@pytest.mark.parametrize("disclosure,needle", [
    ("", "missing [disclosure] summary or ai_systems"),
    ('[disclosure]\nsummary = "x"\n', "missing [disclosure] summary or ai_systems"),
    ('[disclosure]\nai_systems = ["m"]\n', "missing [disclosure] summary or ai_systems"),
])
def test_missing_disclosure(afm, result, disclosure, needle):
    text = (result / "result.toml").read_text()
    text = re.sub(r"\[disclosure\]\n(.*\n){2}", disclosure, text)
    (result / "result.toml").write_text(text)
    assert has(errors(afm, result), needle)


def test_no_authors(afm, result):
    edit(result / "result.toml", 'authors = ["AxiomForge"]', "authors = []")
    assert has(errors(afm, result), "no authors")


def test_no_theorems(afm, result):
    text = (result / "result.toml").read_text()
    (result / "result.toml").write_text(text[:text.index("[[theorem]]")])
    assert has(errors(afm, result), "no [[theorem]] entries")


@pytest.mark.parametrize("field", ["key", "statement", "lean"])
def test_theorem_missing_field(afm, result, field):
    text = (result / "result.toml").read_text()
    head, tail = text.split("[[theorem]]")
    tail = re.sub(rf"^{field} = .*\n", "", tail, count=1, flags=re.M)
    (result / "result.toml").write_text(head + "[[theorem]]" + tail)
    assert has(errors(afm, result), f"missing {field!r}")


@pytest.mark.parametrize("name", ["Sample.main theorem", "1abc", "Sample.main_theorem;#eval 1", "a-b"])
def test_invalid_lean_name(afm, result, name):
    set_toml(result, lean=name)
    assert has(errors(afm, result), "invalid Lean name")


def test_duplicate_lean_name(afm, result):
    text = (result / "result.toml").read_text()
    second = text[text.index("[[theorem]]"):].replace('key = "thm:main"', 'key = "sec:introduction"')
    (result / "result.toml").write_text(text + "\n" + second)
    assert has(errors(afm, result), "duplicate Lean name")


@pytest.mark.parametrize("dim,value", [("proof", "done"), ("build", "green"), ("independent_review", "none")])
def test_verification_vocabulary(afm, result, dim, value):
    set_toml(result, verification={dim: value})
    assert has(errors(afm, result), f"verification.{dim}={value!r} not in")


def test_missing_verification_value(afm, result):
    edit(result / "result.toml", 'axioms = "standard"\n', "")
    assert has(errors(afm, result), "verification.axioms=None not in")


GATE_FAILURES = [("proof", "candidate"), ("proof", "sketch"), ("certificates", "pending"),
                 ("formalization", "partial"), ("formalization", "statement-only"), ("build", "failing"),
                 ("build", "not-run"), ("axioms", "not-run"), ("axioms", "failing"), ("statement_review", "pending"),
                 ("literature_review", "pending")]


@pytest.mark.parametrize("dim,value", GATE_FAILURES)
def test_publication_gate(afm, result, dim, value):
    set_toml(result, verification={dim: value})
    assert has(errors(afm, result), f"publication gate fails on {dim}={value!r}")


@pytest.mark.parametrize("dim,value", GATE_FAILURES[:3])
def test_gate_not_applied_to_withdrawn_or_when_disabled(afm, result, dim, value):
    set_toml(result, verification={dim: value})
    assert not has(errors(afm, result, require_gate=False), "publication gate")
    set_toml(result, verification={dim: value}, status="withdrawn")
    assert not has(errors(afm, result), "publication gate")


@pytest.mark.parametrize("value", ["pending", "ai-internal", "human"])
def test_independent_review_is_not_a_gate(afm, result, value):
    set_toml(result, verification={"independent_review": value})
    assert errors(afm, result) == []


def test_label_missing_in_manuscript(afm, result):
    edit(result / "paper" / "sections" / "introduction.tex", r"\label{thm:main}", r"\label{thm:other}")
    assert has(errors(afm, result), "label 'thm:main' not found in the manuscript")


def test_label_only_in_comment(afm, result):
    """Regression: a label inside a LaTeX comment satisfied the check."""
    edit(result / "paper" / "sections" / "introduction.tex", r"\label{thm:main}", r"% \label{thm:main}")
    assert has(errors(afm, result), "label 'thm:main' not found")


@pytest.mark.parametrize("text", ["TODO: finish", "FIXME", "XXX", "TBD", "???", "<<TITLE>>", "<<MSC PRIMARY>>"])
def test_placeholder_in_tex(afm, result, text):
    p = result / "paper" / "sections" / "introduction.tex"
    p.write_text(p.read_text() + f"\n{text}\n")
    assert has(errors(afm, result), "placeholder in paper/sections/introduction.tex:")


def test_placeholder_in_comment_line_is_ignored(afm, result):
    p = result / "paper" / "sections" / "introduction.tex"
    p.write_text(p.read_text() + "\n   % TODO later, <<TITLE>>\n")
    assert errors(afm, result) == []


@pytest.mark.parametrize("rel", ["README.md", "CITATION.cff", "CHANGELOG.md", "logs/ai-contributions.md"])
def test_unfilled_placeholder_in_other_files(afm, result, rel):
    p = result / rel
    p.write_text(p.read_text() + "\n<<SUMMARY>>\n")
    assert has(errors(afm, result), f"unfilled template placeholder in {rel}")


def test_placeholder_in_result_toml(afm, result):
    edit(result / "result.toml", 'summary = "A synthetic contribution."', 'summary = "<<SUMMARY>>"')
    assert has(errors(afm, result), "unfilled template placeholder in result.toml")


def test_forbidden_lean_construct_is_reported(afm, result):
    (result / "lean" / "Sample.lean").write_text("theorem bad : False := by sorry\n")
    assert has(errors(afm, result), "lean/Sample.lean: forbidden construct (sorry)")


def test_symlink_is_reported(afm, result):
    os.symlink(result / "README.md", result / "logs" / "link.md")
    assert has(errors(afm, result), "symbolic link not allowed: logs/link.md")


def test_absolute_path_is_reported(afm, result):
    p = result / "logs" / "README.md"
    p.write_text(p.read_text() + "\nbuilt in " + abspath("home", "someone", "work") + "\n")
    assert has(errors(afm, result), "logs/README.md: absolute local path")


def test_lakefile_path_dependency_is_reported(afm, result):
    lf = result / "lean" / "lakefile.toml"
    lf.write_text(lf.read_text() + '\n[[require]]\nname = "dep"\npath = "../dep"\n')
    assert has(errors(afm, result), "local path dependency")


def _theorem_as_table(text):
    head = text[:text.index("[[theorem]]")]
    return head + '[theorem]\nkey = "thm:main"\nlean = "Sample.main_theorem"\n'


def _disclosure_as_string(text):
    text = re.sub(r"\[disclosure\]\n(.*\n){2}", "", text)
    return text.replace('authors = ["AxiomForge"]', 'authors = ["AxiomForge"]\ndisclosure = "AI"')


@pytest.mark.parametrize("mutate,needle", [
    (lambda t: t.replace('id = "AF-0001"', "id = 1"), "invalid id 1"),
    (lambda t: t.replace('msc_primary = "11J72"', "msc_primary = 11"), "malformed MSC2020 code 11"),
    (lambda t: t.replace('msc_secondary = ["11Y60"]', 'msc_secondary = "11Y60"'), "msc_secondary must be a list"),
    (lambda t: t.replace('msc_secondary = ["11Y60"]', "msc_secondary = 5"), "msc_secondary must be a list"),
    (lambda t: re.sub(r'^title = .*$', "title = 3", t, count=1, flags=re.M), "field 'title' must be a string"),
    (lambda t: t.replace('lean = "Sample.main_theorem"', "lean = 42"), "invalid Lean name 42"),
    (_theorem_as_table, "[[theorem]] must be an array of tables"),
    (_disclosure_as_string, "missing [disclosure]"),
], ids=["id-int", "msc-int", "secondary-str", "secondary-int", "title-int", "lean-int", "theorem-table",
        "disclosure-str"])
def test_malformed_types_are_errors_not_crashes(afm, result, mutate, needle):
    """Adversarial metadata must yield errors, never a traceback."""
    p = result / "result.toml"
    p.write_text(mutate(p.read_text()))
    assert has(errors(afm, result), needle)


def test_malformed_verification_table(afm, result):
    edit(result / "result.toml", "[theorem.verification]\n", "verification = \"all good\"\n[unused]\n")
    errs = errors(afm, result)
    assert has(errs, "[theorem.verification] must be a table")


def test_report_render(afm):
    rep = afm.Report("demo")
    rep.error("e1")
    rep.warn("w1")
    rep.note("n1")
    assert rep.render() == "[FAIL] demo\n  error: e1\n  warning: w1\n  n1"
    assert not rep.ok
