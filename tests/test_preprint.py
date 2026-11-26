"""The preprint tier: its gates, the 0.x version rule, `lean_conditional`, the page-1
label and the catalogue section. The published (V4) gate must not change."""

from __future__ import annotations

import os
import shutil
import subprocess

import pytest

from archive_factory import make_lean_package, make_pdf, make_result, result_toml
from conftest import needs_pdftotext

PREPRINT_OK = {"proof": "complete", "certificates": "reproduced", "formalization": "in-preparation",
               "build": "not-run", "axioms": "not-run", "statement_review": "pending",
               "independent_review": "ai-internal", "literature_review": "checked"}


def preprint(base, **kw):
    args = dict(status="preprint", version="0.1.0", lean="", verification=dict(PREPRINT_OK))
    ver = kw.pop("verification", {})
    args.update(kw)
    args["verification"].update(ver)
    return make_result(base, **args)


def errors(afm, d, **kw):
    return afm.check_result(d, **kw).errors


def has(errs, needle):
    return any(needle in e for e in errs)


def rewrite(d, **kw):
    """Rewrite result.toml with preprint defaults overridden by kw."""
    args = dict(status="preprint", version="0.1.0", lean="", verification=dict(PREPRINT_OK))
    ver = kw.pop("verification", {})
    args.update(kw)
    args["verification"].update(ver)
    (d / "result.toml").write_text(result_toml(**args))


# --------------------------------------------------------------------------- accepted


def test_preprint_accepted_when_the_gates_hold(afm, tmp_path):
    d = preprint(tmp_path / "results")
    assert errors(afm, d) == []


@pytest.mark.parametrize("ver", [
    {"proof": "candidate"},
    {"formalization": "statement-only"},
    {"formalization": "partial"},
    {"statement_review": "checked"},
    {"certificates": "not-applicable"},
    {"certificates": "formally-checked"},
    {"independent_review": "pending"},
    {"independent_review": "human"},
])
def test_preprint_accepted_variants(afm, tmp_path, ver):
    assert errors(afm, preprint(tmp_path / "results", verification=ver)) == []


def test_preprint_with_audited_main_theorem(afm, tmp_path):
    d = preprint(tmp_path / "results", lean="Sample.main_theorem",
                 verification={"formalization": "partial", "build": "passing", "axioms": "standard"})
    assert errors(afm, d) == []


def test_preprint_with_conditional_declarations(afm, tmp_path):
    d = preprint(tmp_path / "results", lean_conditional=["Sample.main_of_estimates", "Sample.bound_of_growth"],
                 verification={"build": "passing", "axioms": "standard"})
    assert errors(afm, d) == []


def test_preprint_with_complete_formalization(afm, tmp_path):
    d = preprint(tmp_path / "results", lean="Sample.main_theorem",
                 verification={"formalization": "complete", "build": "passing", "axioms": "standard"})
    assert errors(afm, d) == []


@pytest.mark.parametrize("version", ["0.1.0", "0.0.1", "0.12.3"])
def test_preprint_versions(afm, tmp_path, version):
    assert errors(afm, preprint(tmp_path / "results", version=version)) == []


# --------------------------------------------------------------------------- rejected


@pytest.mark.parametrize("ver,needle", [
    ({"certificates": "pending"}, "preprint gate fails on certificates='pending'"),
    ({"proof": "sketch"}, "preprint gate fails on proof='sketch'"),
    ({"proof": "none"}, "preprint gate fails on proof='none'"),
    ({"formalization": "none"}, "preprint gate fails on formalization='none'"),
    ({"literature_review": "pending"}, "preprint gate fails on literature_review='pending'"),
])
def test_preprint_gate_failures(afm, tmp_path, ver, needle):
    assert has(errors(afm, preprint(tmp_path / "results", verification=ver)), needle)


@pytest.mark.parametrize("version", ["1.0.0", "1.2.3", "2.0.0", "10.0.0"])
def test_preprint_version_must_be_zero_major(afm, tmp_path, version):
    errs = errors(afm, preprint(tmp_path / "results", version=version))
    assert has(errs, "a preprint's version must be 0.MINOR.PATCH")


@pytest.mark.parametrize("names,needle", [
    (["Sample.main_estimates"], "must be named after its hypotheses"),
    (["Sample.conditional"], "must be named after its hypotheses"),
    (["not a name"], "invalid Lean name 'not a name' in lean_conditional"),
])
def test_conditional_names(afm, tmp_path, names, needle):
    d = preprint(tmp_path / "results", lean_conditional=names, verification={"build": "passing", "axioms": "standard"})
    assert has(errors(afm, d), needle)


def test_conditional_list_must_be_a_list(afm, tmp_path):
    d = preprint(tmp_path / "results")
    (d / "result.toml").write_text((d / "result.toml").read_text().replace(
        'lean = ""\n', 'lean = ""\nlean_conditional = "Sample.x_of_y"\n'))
    assert has(errors(afm, d), "lean_conditional must be a list")


@pytest.mark.parametrize("ver,dim", [({"build": "not-run", "axioms": "standard"}, "build"),
                                     ({"build": "failing", "axioms": "standard"}, "build"),
                                     ({"build": "passing", "axioms": "not-run"}, "axioms"),
                                     ({"build": "passing", "axioms": "failing"}, "axioms")])
def test_declared_lean_must_build_and_pass_the_audit(afm, tmp_path, ver, dim):
    d = preprint(tmp_path / "results", lean_conditional=["Sample.main_of_estimates"], verification=ver)
    assert has(errors(afm, d), f"preprint gate fails on {dim}=")
    d2 = preprint(tmp_path / "other", lean="Sample.main_theorem", verification=dict(ver, formalization="partial"))
    assert has(errors(afm, d2), f"preprint gate fails on {dim}=")


def test_complete_formalization_needs_a_lean_name(afm, tmp_path):
    d = preprint(tmp_path / "results", verification={"formalization": "complete", "build": "passing",
                                                      "axioms": "standard"})
    assert has(errors(afm, d), "missing 'lean'")


def test_main_lean_name_cannot_be_a_conditional_declaration(afm, tmp_path):
    d = preprint(tmp_path / "results", lean="Sample.main_of_estimates", lean_conditional=["Sample.main_of_estimates"],
                 verification={"formalization": "partial", "build": "passing", "axioms": "standard"})
    assert has(errors(afm, d), "is a conditional declaration")


def test_published_result_cannot_return_to_preprint_changelog(afm, tmp_path):
    d = preprint(tmp_path / "results")
    (d / "CHANGELOG.md").write_text("# Changelog\n\n## [0.2.0] - 2027-01-01\n\n### Changed\n\n- x\n\n"
                                    "## [1.0.0] - 2026-12-01\n\n### Added\n\n- First publication.\n")
    assert has(errors(afm, d), "a published result cannot return to preprint")


def test_published_result_cannot_return_to_preprint_git_history(afm, tmp_path):
    if shutil.which("git") is None:
        pytest.skip("git not installed")
    repo = tmp_path / "archive"
    d = make_result(repo / "results")
    env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid")
    for args in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "publish"]):
        subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, env=env)
    rewrite(d)
    (d / "CHANGELOG.md").write_text("# Changelog\n\n## [0.1.0] - 2027-01-01\n\n### Changed\n\n- demoted\n")
    assert has(errors(afm, d), "the git history of result.toml contains status")


def test_preprint_in_a_fresh_repository_is_not_flagged(afm, tmp_path):
    if shutil.which("git") is None:
        pytest.skip("git not installed")
    repo = tmp_path / "archive"
    d = preprint(repo / "results")
    env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid")
    for args in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "preprint"]):
        subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, env=env)
    assert errors(afm, d) == []


# --------------------------------------------------------------------------- published gate unchanged


def test_published_still_rejects_an_empty_lean_name(afm, tmp_path):
    """Regression: the preprint exemption for `lean = ""` must not leak into `published`."""
    d = make_result(tmp_path / "results", lean="", verification={"formalization": "partial"})
    assert has(errors(afm, d), "theorem thm:main: missing 'lean'")
    d2 = make_result(tmp_path / "other", lean="")
    assert has(errors(afm, d2), "theorem thm:main: missing 'lean'")


def test_withdrawn_still_requires_a_lean_name(afm, tmp_path):
    d = make_result(tmp_path / "results", status="withdrawn", lean="")
    assert has(errors(afm, d), "missing 'lean'")


@pytest.mark.parametrize("ver,dim", [
    ({"formalization": "in-preparation"}, "formalization"),
    ({"formalization": "partial"}, "formalization"),
    ({"proof": "candidate"}, "proof"),
    ({"statement_review": "pending"}, "statement_review"),
    ({"build": "not-run"}, "build"),
    ({"axioms": "not-run"}, "axioms"),
])
def test_published_gate_is_unchanged(afm, tmp_path, ver, dim):
    d = make_result(tmp_path / "results", verification=ver)
    assert has(errors(afm, d), f"publication gate fails on {dim}=")


def test_published_gate_tables_are_unchanged(afm):
    assert afm.GATES == {
        "proof": {"complete"},
        "certificates": {"not-applicable", "reproduced", "formally-checked"},
        "formalization": {"complete"},
        "build": {"passing"},
        "axioms": {"standard"},
        "statement_review": {"checked"},
        "literature_review": {"checked"},
    }


def test_published_lean_cannot_be_a_conditional_declaration(afm, tmp_path):
    d = make_result(tmp_path / "results", lean="Sample.main_of_estimates", lean_conditional=["Sample.main_of_estimates"])
    assert has(errors(afm, d), "is a conditional declaration")


def test_published_versions_unchanged(afm, tmp_path):
    assert errors(afm, make_result(tmp_path / "results")) == []


# --------------------------------------------------------------------------- Lean names to audit


def test_theorem_names_include_conditional_declarations(afm, tmp_path):
    d = preprint(tmp_path / "results", lean="Sample.main_theorem", lean_conditional=["Sample.a_of_b", "Sample.c_of_d"],
                 verification={"formalization": "partial", "build": "passing", "axioms": "standard"})
    assert afm.theorem_names(d) == ["Sample.main_theorem", "Sample.a_of_b", "Sample.c_of_d"]
    assert afm.theorem_names(preprint(tmp_path / "x")) == []


def test_lean_report_for_preprint_without_declarations(afm, tmp_path):
    rep = afm.lean_report(preprint(tmp_path / "results"))
    assert rep.ok and rep.notes == ["preprint: no Lean declaration to audit yet (formalization in preparation)"]


@pytest.mark.lean
def test_lean_audit_of_conditional_declarations(afm, tmp_path):
    d = preprint(tmp_path / "results", lean_conditional=["Sample.main_of_estimates"],
                 verification={"build": "passing", "axioms": "standard"})
    shutil.rmtree(d / "lean")
    make_lean_package(d / "lean", {"Sample.lean": "namespace Sample\n\ntheorem main_of_estimates (P : Prop) "
                                                  "(h : P) : P := h\n\nend Sample\n"})
    rep = afm.lean_report(d)
    assert rep.ok, rep.render()
    assert "Sample.main_of_estimates: axioms ['(none)']" in rep.notes


# --------------------------------------------------------------------------- page 1 label


PAGES = [["A synthetic title", "Abstract.", "MSC 11J72", "AI-assisted research.", "Status: Preprint, version 0.1.0"],
         ["Contents"], ["1. Introduction", "AI-assisted research disclosure"]]


def layout(afm, tmp_path, pages, status):
    pdf = tmp_path / "main.pdf"
    pdf.write_bytes(make_pdf(pages))
    return [e for e in afm.pdf_layout_problems(pdf, status=status) if not e.startswith("font not embedded")]


@needs_pdftotext
def test_preprint_label_present(afm, tmp_path):
    assert layout(afm, tmp_path, PAGES, "preprint") == []


@needs_pdftotext
@pytest.mark.parametrize("word", ["PREPRINT", "preprint", "Preprint."])
def test_preprint_label_is_case_insensitive(afm, tmp_path, word):
    pages = [PAGES[0][:-1] + [f"Status: {word}"]] + PAGES[1:]
    assert layout(afm, tmp_path, pages, "preprint") == []


@needs_pdftotext
def test_preprint_label_missing(afm, tmp_path):
    pages = [PAGES[0][:-1]] + PAGES[1:]
    assert "page 1: the word 'Preprint' (status statement of a preprint) not found" in layout(
        afm, tmp_path, pages, "preprint")
    assert layout(afm, tmp_path, pages, "published") == []
    assert layout(afm, tmp_path, pages, None) == []


@needs_pdftotext
def test_preprint_label_only_on_page_one(afm, tmp_path):
    pages = [PAGES[0][:-1], ["Contents", "Preprint"], PAGES[2]]
    assert any("Preprint" in e for e in layout(afm, tmp_path, pages, "preprint"))


@needs_pdftotext
def test_preprint_page1_problems(afm, tmp_path):
    pdf = tmp_path / "main.pdf"
    pdf.write_bytes(make_pdf(PAGES))
    assert afm.preprint_page1_problems(pdf) == []
    pdf.write_bytes(make_pdf([PAGES[0][:-1]] + PAGES[1:]))
    assert afm.preprint_page1_problems(pdf) and "Preprint" in afm.preprint_page1_problems(pdf)[0]
    assert afm.preprint_page1_problems(tmp_path / "missing.pdf") == ["main.pdf missing"]


def test_preprint_page1_fails_closed_without_pdftotext(afm, tmp_path, monkeypatch):
    pdf = tmp_path / "main.pdf"
    pdf.write_bytes(make_pdf(PAGES))
    monkeypatch.setattr(afm.shutil, "which", lambda name: None)
    assert "cannot be checked" in afm.preprint_page1_problems(pdf)[0]


@pytest.mark.latex
def test_template_manuscript_preprint_label(afm, tmp_path):
    from archive_factory import make_paper
    d = make_paper(tmp_path / "paper", filler_paragraphs=8)
    main = d / "main.tex"
    r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], cwd=d,
                       capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, r.stdout[-2000:]
    assert "page 1: the word 'Preprint' (status statement of a preprint) not found" in afm.pdf_layout_problems(
        d / "main.pdf", status="preprint")
    main.write_text(main.read_text().replace("\\date{25 November 2026}", "\\date{Preprint, 25 November 2026}"))
    r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], cwd=d,
                       capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, r.stdout[-2000:]
    assert afm.pdf_layout_problems(d / "main.pdf", status="preprint") == []


# --------------------------------------------------------------------------- catalogue


def test_catalogue_lists_preprints_in_their_own_section(archive):
    make_result(archive.results, "AF-0001", "published-one", title="A published synthetic result")
    preprint(archive.results, rid="AF-0002", slug="preprint-one", title="A preprint synthetic result",
             lean_conditional=["Sample.main_of_estimates"], verification={"build": "passing", "axioms": "standard"})
    files = archive.afm.catalogue_files()
    res = files["results.md"]
    published, preprints = res.split("## Preprints (complete written arguments, not yet kernel-verified)")
    assert "AF-0001" in published and "AF-0002" not in published
    assert "AF-0002" in preprints and "AF-0001" not in preprints
    assert ("| [AF-0002](../results/AF-0002-preprint-one/README.md) | A preprint synthetic result | 11J72 | 0.1.0 | "
            "thm:main | complete | reproduced | in-preparation | passing | standard | pending | ai-internal | checked |"
            ) in preprints
    assert "not established by the archive until they reach level V4" in preprints
    assert "A preprint synthetic result (preprint)" in files["topics.md"]
    ver = files["verification.md"]
    assert "| AF-0002 | preprint | Two plus two equals four. | in preparation; conditional: `Sample.main_of_estimates` |" in ver


def test_catalogue_wording_with_only_preprints(archive):
    preprint(archive.results, rid="AF-0001", slug="only-preprint")
    res = archive.afm.catalogue_files()["results.md"]
    assert "No contribution has reached the published tier (level V4) yet." in res
    assert "No contribution has been published yet" not in res and "AF-0001" in res


def test_cli_check_and_catalogue_with_a_preprint(archive):
    preprint(archive.results, rid="AF-0001", slug="only-preprint")
    assert archive.run("check").returncode == 0
    assert archive.run("catalogue").returncode == 0
    assert archive.run("catalogue", "--check").returncode == 0
    assert "Preprints (complete written arguments" in (archive.catalogue / "results.md").read_text()
