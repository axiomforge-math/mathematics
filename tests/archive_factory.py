"""Builders of synthetic contributions for the archive-tool tests.

Everything is generated in temporary directories: a contribution filled from the real
manuscript template in ``templates/paper``, a tiny Lean package and minimal PDF files.
"""

from __future__ import annotations

import json
import re
import shutil
import zlib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TEMPLATE = REPO / "templates" / "paper"

TITLE = "A synthetic irrationality statement"
INTRO = r"""\section{Introduction}\label{sec:introduction}

We prove the following statement, which is a synthetic example used to test the archive tool.

\begin{theorem}\label{thm:main}
Two plus two equals four.
\end{theorem}

The argument is classical~\cite{peano1889}. %s
"""
FILLER = ("This paragraph only fills space so that the body of the manuscript spans several pages, "
          "which the layout checks require. ") * 6


def fill_placeholders(text: str, values: dict[str, str]) -> str:
    for k, v in values.items():
        text = text.replace(f"<<{k}>>", v)
    return re.sub(r"<<[A-Z0-9 _-]+>>", "Synthetic filler text", text)


def paper_values(rid: str, slug: str, title: str, msc_primary: str, msc_secondary: list[str]) -> dict[str, str]:
    return {
        "SHORT TITLE": "Synthetic statement", "TITLE": title, "MSC PRIMARY": msc_primary,
        "MSC SECONDARY": ", ".join(msc_secondary), "KEYWORDS": "irrationality, synthetic example",
        "DATE": "25 November 2026", "AF-NNNN": rid, "VERSION": "1.0.0", "DIRECTORY": f"{rid}-{slug}",
        "SHORT AI DISCLOSURE": "AI-assisted research; the detailed disclosure is at the end of the paper.",
        "ABSTRACT": "We record a synthetic statement used to exercise the archive tool.",
        "ACKNOWLEDGEMENTS": "None.",
        "AI DISCLOSURE": "Synthetic disclosure: an AI system drafted this test document.",
        "REPRODUCIBILITY": "The Lean declaration \\texttt{Sample.main\\_theorem} is checked by Lean.",
    }


def make_paper(dest: Path, rid: str = "AF-0001", slug: str = "sample-result", title: str = TITLE,
               msc_primary: str = "11J72", msc_secondary=("11Y60",), filler_paragraphs: int = 0) -> Path:
    if not (TEMPLATE / "main.tex").is_file():
        raise RuntimeError("manuscript template not found")
    shutil.copytree(TEMPLATE, dest, ignore=shutil.ignore_patterns("README.md"))
    values = paper_values(rid, slug, title, msc_primary, list(msc_secondary))
    for f in dest.rglob("*.tex"):
        f.write_text(fill_placeholders(f.read_text(), values))
    intro = INTRO % ("\n\n".join([FILLER] * filler_paragraphs))
    (dest / "sections" / "introduction.tex").write_text(intro)
    bib = (dest / "references.bib").read_text()
    (dest / "references.bib").write_text(bib + "\n@book{peano1889,\n  author = {Peano, Giuseppe},\n"
                                                "  title = {Arithmetices principia},\n  year = {1889}\n}\n")
    (dest / "main.pdf").write_bytes(make_pdf([["Synthetic manuscript"]]))
    return dest


SAMPLE_LEAN = """/-!
# Sample

A synthetic formalization used by the test suite.
-/

namespace Sample

theorem main_theorem : (2 : Nat) + 2 = 4 := rfl

end Sample
"""


def make_lean_package(d: Path, files: dict[str, str] | None = None, lib: str = "Sample", extra_lakefile: str = "",
                      toolchain: str = "leanprover/lean4:v4.34.0-rc1") -> Path:
    d.mkdir(parents=True, exist_ok=True)
    (d / "lean-toolchain").write_text(toolchain + "\n")
    (d / "lakefile.toml").write_text(f'name = "{lib.lower()}"\ndefaultTargets = ["{lib}"]\n\n'
                                     f'[[lean_lib]]\nname = "{lib}"\n' + extra_lakefile)
    (d / "lake-manifest.json").write_text(json.dumps({"version": "1.1.0", "packagesDir": ".lake/packages",
                                                      "packages": [], "name": lib.lower(), "lakeDir": ".lake"},
                                                     indent=1) + "\n")
    for rel, text in (files if files is not None else {f"{lib}.lean": SAMPLE_LEAN}).items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    return d


def result_toml(rid="AF-0001", slug="sample-result", title=TITLE, status="published", msc_primary="11J72",
                msc_secondary=("11Y60",), lean="Sample.main_theorem", key="thm:main", verification=None,
                extra="", version="1.0.0", lean_conditional=None) -> str:
    ver = {"proof": "complete", "certificates": "not-applicable", "formalization": "complete", "build": "passing",
           "axioms": "standard", "statement_review": "checked", "independent_review": "ai-internal",
           "literature_review": "checked"}
    ver.update(verification or {})
    sec = ", ".join(json.dumps(c) for c in msc_secondary)
    cond = "" if lean_conditional is None else "lean_conditional = " + json.dumps(list(lean_conditional)) + "\n"
    return (f'id = "{rid}"\nslug = "{slug}"\ntitle = {json.dumps(title)}\nversion = "{version}"\ndate = 2026-11-25\n'
            f'status = "{status}"\nsummary = "A synthetic contribution."\ntemplate_version = "1.0.0"\n'
            f'msc_primary = {json.dumps(msc_primary)}\nmsc_secondary = [{sec}]\nauthors = ["AxiomForge"]\n{extra}\n'
            '[disclosure]\nsummary = "AI-assisted research; see logs/ai-contributions.md."\n'
            'ai_systems = ["Synthetic model"]\n\n'
            f'[[theorem]]\nkey = "{key}"\nstatement = "Two plus two equals four."\nlean = "{lean}"\n{cond}\n'
            "[theorem.verification]\n" + "\n".join(f'{k} = "{v}"' for k, v in ver.items()) + "\n")


def make_result(base: Path, rid: str = "AF-0001", slug: str = "sample-result", title: str = TITLE, **kw) -> Path:
    d = base / f"{rid}-{slug}"
    d.mkdir(parents=True)
    (d / "README.md").write_text(f"# {title}\n\nContribution {rid}.\n")
    (d / "result.toml").write_text(result_toml(rid, slug, title, **kw))
    (d / "CITATION.cff").write_text(f'cff-version: 1.2.0\ntitle: "{title}"\nmessage: "Synthetic."\n')
    version = kw.get("version", "1.0.0")
    (d / "CHANGELOG.md").write_text(f"# Changelog\n\n## [{version}] - 2026-11-25\n\n### Added\n\n- Initial version.\n")
    make_paper(d / "paper", rid, slug, title, kw.get("msc_primary", "11J72"), kw.get("msc_secondary", ("11Y60",)))
    make_lean_package(d / "lean")
    (d / "logs").mkdir()
    (d / "logs" / "README.md").write_text("# Logs\n\nSynthetic logs.\n")
    (d / "logs" / "ai-contributions.md").write_text("# AI contributions\n\nSynthetic.\n")
    return d


# --------------------------------------------------------------------------- PDF


def _esc(s: str) -> bytes:
    return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)").encode("latin-1")


def make_pdf(pages: list[list[str]], compress: bool = False) -> bytes:
    """A minimal valid PDF with one Helvetica text stream per page (readable by poppler)."""
    objs: dict[int, bytes] = {}
    page_ids = [4 + 2 * i for i in range(len(pages))]
    objs[1] = b"<< /Type /Catalog /Pages 2 0 R >>"
    objs[2] = b"<< /Type /Pages /Kids [" + b" ".join(b"%d 0 R" % p for p in page_ids) + b"] /Count %d >>" % len(pages)
    objs[3] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"
    for pid, lines in zip(page_ids, pages):
        content = b"BT /F1 11 Tf 14 TL 72 740 Td\n" + b"\n".join(b"(" + _esc(ln) + b") Tj T*" for ln in lines) + b"\nET"
        filt = b""
        if compress:
            content, filt = zlib.compress(content), b" /Filter /FlateDecode"
        objs[pid] = b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents %d 0 R" % (pid + 1) + \
            b" /Resources << /Font << /F1 3 0 R >> >> >>"
        objs[pid + 1] = b"<< /Length %d%s >>\nstream\n" % (len(content), filt) + content + b"\nendstream"
    out = bytearray(b"%PDF-1.4\n")
    offsets = {}
    for oid in sorted(objs):
        offsets[oid] = len(out)
        out += b"%d 0 obj\n" % oid + objs[oid] + b"\nendobj\n"
    size = max(objs) + 1
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % size
    out += b"".join(b"%010d 00000 n \n" % offsets[i] for i in range(1, size))
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (size, xref)
    return bytes(out)
