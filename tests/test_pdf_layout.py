"""PDF layout gate: synthetic PDFs (fast, poppler only) and real manuscripts compiled
from the template (``@pytest.mark.latex``)."""

from __future__ import annotations

import shutil
import subprocess

import pytest

from archive_factory import make_paper, make_pdf
from conftest import needs_pdftotext

TITLE_PAGE = ["A synthetic title", "Abstract. We prove things.", "2020 Mathematics Subject Classification. 11J72.",
              "Disclosure: AI-assisted research."]
CONTENTS = ["Contents", "1. Introduction 3", "References 4"]
BODY = ["1. Introduction", "", "Body text."]
BACK = ["AI-assisted research disclosure", "Details of the AI contribution."]


def layout(afm, tmp_path, pages):
    pdf = tmp_path / "main.pdf"
    pdf.write_bytes(make_pdf(pages))
    # Synthetic PDFs use a non-embedded base font: ignore that single, expected finding.
    return [e for e in afm.pdf_layout_problems(pdf) if not e.startswith("font not embedded")]


@needs_pdftotext
def test_good_layout(afm, tmp_path):
    assert layout(afm, tmp_path, [TITLE_PAGE, CONTENTS, BODY + BACK]) == []


@needs_pdftotext
def test_non_embedded_fonts_are_reported(afm, tmp_path):
    pdf = tmp_path / "main.pdf"
    pdf.write_bytes(make_pdf([TITLE_PAGE, CONTENTS, BODY + BACK]))
    if shutil.which("pdffonts") is None:
        pytest.skip("pdffonts not installed")
    assert "font not embedded: Helvetica" in afm.pdf_layout_problems(pdf)


@needs_pdftotext
def test_two_page_pdf_is_too_short(afm, tmp_path):
    """Regression: pdftotext ends every page with a form feed, so a two-page PDF was
    counted as three pages."""
    assert layout(afm, tmp_path, [TITLE_PAGE, CONTENTS]) == [
        "PDF has fewer than three pages (front matter, contents, body expected)"]


@needs_pdftotext
@pytest.mark.parametrize("pages,needle", [
    ([["A title", "2020 Mathematics Subject Classification", "AI-assisted"], CONTENTS, BODY + BACK],
     "page 1: abstract not found"),
    ([["A title", "Abstract.", "AI-assisted"], CONTENTS, BODY + BACK], "page 1: MSC classification not found"),
    ([["A title", "Abstract.", "MSC 11J72"], CONTENTS, BODY + BACK], "page 1: short AI disclosure not found"),
    ([TITLE_PAGE + ["1. Introduction"], CONTENTS, BODY + BACK], "page 1: introduction starts on the title page"),
    ([TITLE_PAGE, ["Summary"], BODY + BACK], "page 2: table of contents not found"),
    ([TITLE_PAGE, CONTENTS + BODY, ["More text"] + BACK],
     "introduction heading (section 1) not found on a page of its own after the contents"),
    ([TITLE_PAGE, BODY, ["More text"] + BACK], "introduction must start on a page after the table of contents"),
    ([TITLE_PAGE, CONTENTS, BODY], "detailed 'AI-assisted research disclosure' section not found"),
])
def test_layout_problems(afm, tmp_path, pages, needle):
    assert needle in layout(afm, tmp_path, pages)


@needs_pdftotext
def test_artificial_intelligence_wording_accepted(afm, tmp_path):
    title = ["T", "Abstract.", "MSC 11J72", "This work used artificial intelligence tools."]
    assert layout(afm, tmp_path, [title, CONTENTS, BODY + BACK]) == []


def test_missing_pdf(afm, tmp_path):
    assert afm.pdf_layout_problems(tmp_path / "main.pdf") == ["main.pdf missing"]


def test_layout_fails_closed_without_pdftotext(afm, tmp_path, monkeypatch):
    """Regression: without pdftotext the layout gate silently passed."""
    pdf = tmp_path / "main.pdf"
    pdf.write_bytes(make_pdf([TITLE_PAGE, CONTENTS, BODY + BACK]))
    monkeypatch.setattr(afm.shutil, "which", lambda name: None)
    out = afm.pdf_layout_problems(pdf)
    assert len(out) == 1 and "pdftotext not found" in out[0]


@needs_pdftotext
def test_unreadable_pdf(afm, tmp_path):
    pdf = tmp_path / "main.pdf"
    pdf.write_bytes(b"%PDF-1.4\nnot a pdf at all\n")
    out = afm.pdf_layout_problems(pdf)
    assert out and ("could not read" in out[0] or "fewer than three pages" in out[0])


# --------------------------------------------------------------------------- real manuscripts


def compile_paper(d, full: bool = True):
    """latexmk (all passes, bibliography) or, for layout-only checks, a single pdflatex pass:
    page breaks and the 'Contents' heading are already final after the first pass."""
    cmd = ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "main.tex"] if full else \
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"]
    r = subprocess.run(cmd, cwd=d, capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, r.stdout[-3000:]
    return d / "main.pdf"


@pytest.fixture(scope="module")
def good_paper(tmp_path_factory):
    if shutil.which("latexmk") is None:
        pytest.skip("latexmk not installed")
    d = make_paper(tmp_path_factory.mktemp("good") / "paper", filler_paragraphs=12)
    compile_paper(d)
    return d


@pytest.mark.latex
def test_template_manuscript_layout_passes(afm, good_paper):
    assert afm.pdf_layout_problems(good_paper / "main.pdf") == []


@pytest.mark.latex
def test_template_manuscript_paper_check_without_build(afm, good_paper):
    rep = afm.paper_check(good_paper, build=False)
    assert rep.errors == [], rep.render()


@pytest.mark.latex
def test_paper_check_builds_and_reads_the_log(afm, tmp_path):
    d = make_paper(tmp_path / "paper")
    p = d / "sections" / "introduction.tex"
    p.write_text(p.read_text() + "\nSee \\cref{thm:nowhere} and \\cite{ghost2020}.\n")
    rep = afm.paper_check(d, build=True)
    assert "latexmk: passing" in rep.notes
    assert any("undefined reference: thm:nowhere" in e for e in rep.errors) or \
        any("undefined references reported by LaTeX" in e for e in rep.errors)
    assert any("undefined citation: ghost2020" in e for e in rep.errors)


@pytest.mark.latex
def test_paper_check_reports_build_failure(afm, tmp_path):
    d = make_paper(tmp_path / "paper")
    p = d / "sections" / "introduction.tex"
    p.write_text(p.read_text() + "\n\\undefinedcontrolsequence\n")
    rep = afm.paper_check(d, build=True)
    assert rep.errors and rep.errors[0].startswith("latexmk failed")


@pytest.mark.latex
@pytest.mark.parametrize("variant,needles", [
    ("intro-on-title-page", ["page 1: introduction starts on the title page", "page 2: table of contents not found"]),
    ("no-contents", ["page 2: table of contents not found",
                     "introduction must start on a page after the table of contents"]),
    ("no-disclosure", ["detailed 'AI-assisted research disclosure' section not found",
                       "page 1: short AI disclosure not found"]),
])
def test_template_manuscript_bad_layouts(afm, tmp_path, variant, needles):
    d = make_paper(tmp_path / "paper", filler_paragraphs=12)
    main = d / "main.tex"
    text = main.read_text()
    if variant == "intro-on-title-page":
        text = text.replace("\\affrontmatter", "\\maketitle")
    elif variant == "no-contents":
        text = text.replace("\\affrontmatter", "\\maketitle\\afpublicationblock\\clearpage")
    else:
        text = text.replace("\\input{sections/disclosure}", "")
        text = text.replace("AI-assisted research; the detailed disclosure is at the end of the paper.",
                            "See the end of the paper.")
    main.write_text(text)
    out = afm.pdf_layout_problems(compile_paper(d, full=False))
    for needle in needles:
        assert needle in out, out


# --------------------------------------------------------------------------- table-of-contents spill (warning)


def spill_warnings(afm, tmp_path, pages):
    pdf = tmp_path / "main.pdf"
    pdf.write_bytes(make_pdf(pages))
    warnings: list[str] = []
    errors = [e for e in afm.pdf_layout_problems(pdf, warnings=warnings) if not e.startswith("font not embedded")]
    return errors, warnings


@needs_pdftotext
def test_toc_spilling_one_line_is_a_warning(afm, tmp_path):
    errors, warnings = spill_warnings(afm, tmp_path, [TITLE_PAGE, CONTENTS, ["References 9"], BODY + BACK])
    assert errors == []
    assert warnings == ["table of contents spills 1 lines onto page 3; tighten it so it fits on page 2"]


@needs_pdftotext
def test_toc_spill_ignores_the_running_head(afm, tmp_path):
    spill = ["SYNTHETIC STATEMENT                3", "Appendix A. Tail estimates 8", "References 9"]
    errors, warnings = spill_warnings(afm, tmp_path, [TITLE_PAGE, CONTENTS, spill, BODY + BACK])
    assert errors == [] and warnings == [
        "table of contents spills 2 lines onto page 3; tighten it so it fits on page 2"]


@needs_pdftotext
def test_toc_spill_before_the_heading_on_the_same_page(afm, tmp_path):
    errors, warnings = spill_warnings(afm, tmp_path, [TITLE_PAGE, CONTENTS, ["References 9"] + BODY + BACK])
    assert errors == [] and warnings == [
        "table of contents spills 1 lines onto page 3; tighten it so it fits on page 2"]


@needs_pdftotext
def test_long_toc_over_two_pages_is_not_a_spill(afm, tmp_path):
    long_toc = [f"{k}. Section number {k}   {k + 3}" for k in range(2, 14)]
    errors, warnings = spill_warnings(afm, tmp_path, [TITLE_PAGE, CONTENTS, long_toc, BODY + BACK])
    assert errors == [] and warnings == []


@needs_pdftotext
def test_toc_fitting_on_page_two_has_no_warning(afm, tmp_path):
    assert spill_warnings(afm, tmp_path, [TITLE_PAGE, CONTENTS, BODY + BACK]) == ([], [])


@needs_pdftotext
def test_spill_warning_reaches_the_paper_report(afm, tmp_path):
    d = tmp_path / "paper"
    d.mkdir()
    (d / "main.pdf").write_bytes(make_pdf([TITLE_PAGE, CONTENTS, ["References 9"], BODY + BACK]))
    rep = afm.paper_check(d, build=False)
    assert "table of contents spills 1 lines onto page 3; tighten it so it fits on page 2" in rep.warnings
    assert not any("spills" in e for e in rep.errors)


@pytest.mark.latex
def test_template_manuscript_has_no_toc_spill(afm, good_paper):
    warnings: list[str] = []
    afm.pdf_layout_problems(good_paper / "main.pdf", warnings=warnings)
    assert warnings == []


def test_specimen_has_no_toc_spill(afm):
    from conftest import REPO, HAVE_PDFTOTEXT
    pdf = REPO / "docs" / "manuscript-sample" / "main.pdf"
    if not (HAVE_PDFTOTEXT and pdf.is_file()):
        pytest.skip("specimen or pdftotext not available")
    warnings: list[str] = []
    assert afm.pdf_layout_problems(pdf, warnings=warnings) == [] and warnings == []
