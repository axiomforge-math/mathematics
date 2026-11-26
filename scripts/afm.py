#!/usr/bin/env python3
"""afm — AxiomForge Mathematics archive tool.

Discovers, checks, verifies and catalogues the self-contained contributions in
``results/``. It is a convenience: every contribution documents its own reproduction
commands and never needs this tool.

Commands (see ``afm.py <command> --help``):
  list                      list contributions
  check [RESULT...]         validate metadata, files and the publication gate (no builds)
  lean RESULT               build the Lean package and audit the axioms of its main theorems
  paper RESULT              compile the manuscript and check the log and the PDF layout
  verify RESULT             check + lean + paper
  isolate RESULT            copy the contribution to a fresh temporary directory and verify it there
  catalogue [--check]       (re)generate catalogue/*.md from result.toml files

Only the Python standard library is required (Python >= 3.11). PDF layout checks use
``pdftotext``/``pdfinfo``/``pdffonts`` (poppler-utils) when available.

Exit status: 0 success, 1 check failure, 2 usage or environment error.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
CATALOGUE = ROOT / "catalogue"

ID_RE = re.compile(r"^AF-\d{4}$")
DIR_RE = re.compile(r"^AF-\d{4}-[a-z0-9]+(-[a-z0-9]+)*$")
MSC_RE = re.compile(r"^\d\d[A-Z-]\d\d$|^\d\d-XX$|^\d\d[A-Z]xx$")
LEAN_NAME_RE = re.compile(r"^[A-Za-z_][\w'.]*$")
STANDARD_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
MSC_DATA = Path(__file__).resolve().parent / "data" / "msc2020.tsv"


def msc_table() -> dict[str, str]:
    """Official MSC2020 codes (see scripts/data/README.md for provenance and licence)."""
    table = {}
    for line in MSC_DATA.read_text(encoding="utf-8").splitlines()[1:]:
        cols = [c.strip('"') for c in line.split("\t")]
        if len(cols) >= 2:
            table[cols[0]] = cols[1]
    return table

STATUSES = ("published", "preprint", "withdrawn")
# Publication gate (status = "published", level V4). Unchanged by the preprint tier.
GATES = {
    "proof": {"complete"},
    "certificates": {"not-applicable", "reproduced", "formally-checked"},
    "formalization": {"complete"},
    "build": {"passing"},
    "axioms": {"standard"},
    "statement_review": {"checked"},
    "literature_review": {"checked"},
}
# Preprint gate (status = "preprint"): a complete written argument with reproduced
# certificates and checked literature; the Lean development may still be in preparation.
PREPRINT_GATES = {
    "proof": {"candidate", "complete"},
    "certificates": {"not-applicable", "reproduced", "formally-checked"},
    "formalization": {"in-preparation", "statement-only", "partial", "complete"},
    "statement_review": {"pending", "checked"},
    "literature_review": {"checked"},
}
# Added to the preprint gate for a theorem that declares something for Lean to audit
# (a `lean` name or `lean_conditional` names).
PREPRINT_AUDIT_GATES = {"build": {"passing"}, "axioms": {"standard"}}
PREPRINT_VERSION_RE = re.compile(r"^0\.\d+\.\d+$")
CHANGELOG_VERSION_RE = re.compile(r"^##\s*\[?v?(\d+)\.(\d+)\.(\d+)\]?", re.M)
ALLOWED = {
    "proof": {"none", "sketch", "candidate", "complete"},
    "certificates": {"not-applicable", "pending", "reproduced", "formally-checked"},
    "formalization": {"none", "in-preparation", "statement-only", "partial", "complete"},
    "build": {"not-run", "failing", "passing"},
    "axioms": {"not-run", "failing", "standard"},
    "statement_review": {"pending", "checked"},
    "independent_review": {"pending", "ai-internal", "human"},
    "literature_review": {"pending", "checked"},
}
REQUIRED_FILES = [
    "README.md",
    "result.toml",
    "CITATION.cff",
    "CHANGELOG.md",
    "paper/main.tex",
    "paper/main.pdf",
    "paper/references.bib",
    "lean/lean-toolchain",
    "lean/lakefile.toml",
    "lean/lake-manifest.json",
    "logs/README.md",
    "logs/ai-contributions.md",
]
FORBIDDEN_LEAN = [
    (re.compile(r"\bsorry\b"), "sorry"),
    (re.compile(r"\bsorryAx\b"), "sorryAx"),
    (re.compile(r"\badmit\b"), "admit"),
    # `axiom` after any declaration modifiers or attributes (visibility, noncomputable,
    # unsafe, @[simp], ...), not only at the start of a line.
    (re.compile(r"(?<![\w.'])axiom\s+[^\s:]"), "axiom declaration"),
    (re.compile(r"\bnative_decide\b"), "native_decide"),
    (re.compile(r"\bimplemented_by\b"), "implemented_by"),
    (re.compile(r"\bextern\b"), "extern"),
    (re.compile(r"set_option\s+debug\.skipKernelTC"), "kernel check disabled"),
]
PLACEHOLDERS = re.compile(r"\b(TODO|FIXME|XXX|TBD)\b|\?\?\?|<<[A-Z0-9 -]+>>")
TEMPLATE_PLACEHOLDER = re.compile(r"<<[A-Z0-9 _-]+>>")


# --------------------------------------------------------------------------- reporting


@dataclass
class Report:
    name: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def note(self, msg: str) -> None:
        self.notes.append(msg)

    @property
    def ok(self) -> bool:
        return not self.errors

    def render(self) -> str:
        lines = [f"[{'PASS' if self.ok else 'FAIL'}] {self.name}"]
        lines += [f"  error: {e}" for e in self.errors]
        lines += [f"  warning: {w}" for w in self.warnings]
        lines += [f"  {n}" for n in self.notes]
        return "\n".join(lines)


def run(cmd: list[str], cwd: Path, timeout: int = 7200, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env)


# --------------------------------------------------------------------------- discovery


def result_dirs() -> list[Path]:
    if not RESULTS.is_dir():
        return []
    return sorted(p for p in RESULTS.iterdir() if p.is_dir() and DIR_RE.match(p.name))


def resolve(name: str) -> Path:
    p = Path(name)
    if p.is_dir() and (p / "result.toml").exists():
        return p.resolve()
    for d in result_dirs():
        if d.name == name or d.name.startswith(name + "-"):
            return d
    raise SystemExit(f"afm: no contribution matching {name!r}")


def load_meta(d: Path) -> dict:
    with open(d / "result.toml", "rb") as fh:
        return tomllib.load(fh)


# --------------------------------------------------------------------------- check


def check_result(d: Path, require_gate: bool = True) -> Report:
    rep = Report(f"check {d.name}")
    for rel in REQUIRED_FILES:
        if not (d / rel).exists():
            rep.error(f"missing required file {rel}")
    if not (d / "result.toml").exists():
        return rep
    try:
        meta = load_meta(d)
    except tomllib.TOMLDecodeError as exc:
        rep.error(f"result.toml is not valid TOML: {exc}")
        return rep

    rid = meta.get("id", "")
    if not isinstance(rid, str) or not ID_RE.match(rid):
        rep.error(f"invalid id {rid!r}")
    elif not d.name.startswith(rid + "-"):
        rep.error(f"directory {d.name} does not start with id {rid}")
    if d.name != f"{rid}-{meta.get('slug', '')}":
        rep.error("directory name must be '<id>-<slug>'")
    for key in ("title", "version", "date", "status", "summary", "template_version"):
        if not meta.get(key):
            rep.error(f"missing field {key!r}")
    for key in ("title", "summary", "slug"):
        if key in meta and not isinstance(meta[key], str):
            rep.error(f"field {key!r} must be a string")
    status = meta.get("status")
    if status not in STATUSES:
        rep.error("status must be 'published', 'preprint' or 'withdrawn'")
    if not re.match(r"^\d+\.\d+\.\d+$", str(meta.get("version", ""))):
        rep.error("version must be MAJOR.MINOR.PATCH")
    elif status == "preprint" and not PREPRINT_VERSION_RE.match(str(meta["version"])):
        rep.error(f"a preprint's version must be 0.MINOR.PATCH, not {meta['version']} "
                  "(1.0.0 is reserved for the first publication at level V4)")
    if status == "preprint":
        reason = published_history(d)
        if reason:
            rep.error(f"this contribution was published ({reason}); a published result cannot return to preprint")
    secondary = meta.get("msc_secondary", [])
    if not isinstance(secondary, list):
        rep.error("msc_secondary must be a list of MSC2020 codes")
        secondary = []
    msc = [meta.get("msc_primary", "")] + list(secondary)
    table = msc_table()
    for code in msc:
        if not isinstance(code, str) or not MSC_RE.fullmatch(code):
            rep.error(f"malformed MSC2020 code {code!r}")
        elif code not in table:
            rep.error(f"MSC2020 code {code!r} does not exist in the official table")
        elif code.endswith("-XX") or code.endswith("xx"):
            rep.error(f"MSC2020 code {code!r} is a section heading, not a classification")
    msc = [c for c in msc if isinstance(c, str)]
    if len(set(msc)) != len(msc):
        rep.error("duplicate MSC2020 codes")
    # LaTeX comments are not part of the manuscript: a commented-out \subjclass, title or
    # \label must not satisfy the checks below.
    manuscript = "\n".join(strip_tex_comments(p.read_text(errors="replace"))
                           for p in sorted((d / "paper").rglob("*.tex"))) if (d / "paper").is_dir() else ""
    m = re.search(r"\\subjclass\[2020\]\{([^}]*)\}", manuscript)
    if not m:
        rep.error("manuscript lacks \\subjclass[2020]{...}")
    else:
        codes = re.findall(r"\d\d[A-Z-]\d\d", m.group(1))
        if set(codes) != set(msc):
            rep.error(f"MSC codes differ between manuscript {sorted(codes)} and result.toml {sorted(msc)}")
    title = meta.get("title")
    if manuscript and isinstance(title, str) and title and _norm(title) not in _norm(manuscript):
        rep.error("result.toml title does not appear verbatim in the manuscript")
    if not meta.get("authors"):
        rep.error("no authors")
    disc = meta.get("disclosure", {})
    if not isinstance(disc, dict):
        disc = {}
    if not disc.get("summary") or not disc.get("ai_systems"):
        rep.error("missing [disclosure] summary or ai_systems")

    theorems = meta.get("theorem", [])
    if not isinstance(theorems, list):
        rep.error("[[theorem]] must be an array of tables")
        theorems = []
    if not theorems:
        rep.error("no [[theorem]] entries")
    lean_names = set()
    conditional_names: set[str] = set()
    main_names: list[tuple[str, str]] = []
    for i, th in enumerate(theorems):
        if not isinstance(th, dict):
            rep.error(f"theorem #{i}: not a table")
            continue
        tag = th.get("key", f"#{i}")
        ver = th.get("verification", {})
        if not isinstance(ver, dict):
            rep.error(f"theorem {tag}: [theorem.verification] must be a table")
            ver = {}
        for key in ("key", "statement", "lean"):
            if not th.get(key):
                # Only a preprint whose formalization is not complete may leave `lean` empty.
                if key == "lean" and status == "preprint" and ver.get("formalization") != "complete":
                    continue
                rep.error(f"theorem {tag}: missing {key!r}")
        lean = th.get("lean")
        if lean and not (isinstance(lean, str) and LEAN_NAME_RE.match(lean)):
            rep.error(f"theorem {tag}: invalid Lean name {lean!r}")
        if isinstance(lean, str) and lean in lean_names:
            rep.error(f"theorem {tag}: duplicate Lean name")
        if isinstance(lean, str) and lean:
            lean_names.add(lean)
            main_names.append((tag, lean))
        conditional = th.get("lean_conditional", [])
        if not isinstance(conditional, list) or not all(isinstance(c, str) for c in conditional):
            rep.error(f"theorem {tag}: lean_conditional must be a list of Lean declaration names")
            conditional = []
        for c in conditional:
            if not LEAN_NAME_RE.match(c):
                rep.error(f"theorem {tag}: invalid Lean name {c!r} in lean_conditional")
            elif "_of_" not in c:
                rep.error(f"theorem {tag}: conditional declaration {c!r} must be named after its hypotheses "
                          "(its name contains '_of_')")
        conditional_names.update(conditional)
        declares = bool(lean) or bool(conditional)
        for dim, allowed in ALLOWED.items():
            val = ver.get(dim)
            if val not in allowed:
                rep.error(f"theorem {tag}: verification.{dim}={val!r} not in {sorted(allowed)}")
            elif require_gate and status == "published" and dim in GATES and val not in GATES[dim]:
                rep.error(f"theorem {tag}: publication gate fails on {dim}={val!r}")
            elif require_gate and status == "preprint":
                gate = PREPRINT_GATES.get(dim) or (PREPRINT_AUDIT_GATES.get(dim) if declares else None)
                if gate and val not in gate:
                    rep.error(f"theorem {tag}: preprint gate fails on {dim}={val!r}")
        if th.get("key") and (d / "paper").is_dir():
            if f"\\label{{{th['key']}}}" not in manuscript:
                rep.error(f"theorem {tag}: label {th['key']!r} not found in the manuscript")

    for tag, lean in main_names:
        if lean in conditional_names:  # a conditional declaration never stands for a main theorem
            rep.error(f"theorem {tag}: lean = {lean!r} is a conditional declaration (lean_conditional)")
    rep.errors += lean_source_problems(d / "lean")
    rep.errors += isolation_problems(d)
    for tex in sorted((d / "paper").rglob("*.tex")) if (d / "paper").is_dir() else []:
        for no, line in enumerate(tex.read_text(errors="replace").splitlines(), 1):
            if not line.lstrip().startswith("%") and PLACEHOLDERS.search(line):
                rep.error(f"placeholder in {tex.relative_to(d)}:{no}")
    # Unfilled template placeholders anywhere else in the public text files.
    for f in sorted(d.rglob("*")):
        if f.suffix in {".md", ".toml", ".cff", ".bib", ".txt"} and f.is_file() and not f.is_symlink() \
                and ".lake" not in f.relative_to(d).parts:
            for no, line in enumerate(f.read_text(errors="replace").splitlines(), 1):
                if TEMPLATE_PLACEHOLDER.search(line):
                    rep.error(f"unfilled template placeholder in {f.relative_to(d)}:{no}")
    return rep


def published_history(d: Path) -> str | None:
    """Evidence that a contribution has been published: a version 1.0.0 or later in its
    CHANGELOG.md, or `status = "published"` in the git history of its result.toml.
    Returns a short description of the evidence, or None."""
    changelog = d / "CHANGELOG.md"
    if changelog.is_file():
        for m in CHANGELOG_VERSION_RE.finditer(changelog.read_text(errors="replace")):
            if int(m.group(1)) >= 1:
                return f"CHANGELOG.md records version {m.group(1)}.{m.group(2)}.{m.group(3)}"
    # Only an archive working tree (results/<dir>) has a meaningful history: there, a commit
    # with status = "published" is a publication.
    if d.parent.name == "results" and shutil.which("git") and (d / "result.toml").is_file():
        try:
            r = run(["git", "log", "--format=", "-p", "--", "result.toml"], d, timeout=120)
        except (OSError, subprocess.SubprocessError):
            return None
        if r.returncode == 0 and re.search(r'^[-+]\s*status\s*=\s*"published"', r.stdout, re.M):
            return 'the git history of result.toml contains status = "published"'
    return None


def strip_tex_comments(text: str) -> str:
    return re.sub(r"(?<!\\)%.*", "", text)


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[{}\\$]", "", text)).strip().lower()


def lean_source_problems(lean_dir: Path) -> list[str]:
    out = []
    if not lean_dir.is_dir():
        return out
    for f in sorted(lean_dir.rglob("*.lean")):
        if ".lake" in f.relative_to(lean_dir).parts or f.is_symlink():
            continue
        text = strip_lean_comments(f.read_text(errors="replace"))
        for rx, what in FORBIDDEN_LEAN:
            if rx.search(text):
                out.append(f"{f.relative_to(lean_dir.parent)}: forbidden construct ({what})")
    return out


def strip_lean_comments(text: str) -> str:
    """Remove Lean comments with a small lexer: block comments nest (``/- /- -/ -/``),
    ``--`` inside a string literal is not a comment, and ``/-`` inside a line comment does
    not open a block comment. String literals are kept (a forbidden word inside a string
    is reported, which errs on the safe side)."""
    out: list[str] = []
    i, n, depth = 0, len(text), 0
    while i < n:
        two = text[i:i + 2]
        if depth:
            if two == "/-":
                depth, i = depth + 1, i + 2
            elif two == "-/":
                depth, i = depth - 1, i + 2
            else:
                if text[i] == "\n":
                    out.append("\n")  # keep line numbers stable
                i += 1
        elif two == "/-":
            depth, i = 1, i + 2
        elif two == "--":
            j = text.find("\n", i)
            i = n if j < 0 else j
        elif text[i] == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            out.append(text[i:j + 1])
            i = j + 1
        elif text[i] == "'" and i + 2 < n and (text[i + 2] == "'" or text[i + 1] == "\\") and \
                (i == 0 or not (text[i - 1].isalnum() or text[i - 1] in "_'.!?")):
            j = text.find("'", i + 2 if text[i + 1] == "\\" else i + 1)  # character literal such as '"'
            j = i + 2 if j < 0 else j
            out.append(text[i:j + 1])
            i = j + 1
        else:
            out.append(text[i])
            i += 1
    return "".join(out)


TEXT_SUFFIXES = {".tex", ".lean", ".py", ".toml", ".md", ".bib", ".cff", ".json", ".txt", ".sty", ".cls", ".bst",
                 ".sh", ".cfg", ".yml", ".yaml", ".csv", ".tsv", ".svg"}
LOCAL_PATH = re.compile(r"(?<![\w.])/(home|media|Users|mnt|tmp|root|Volumes)/|/var/folders/"
                        r"|\b[A-Za-z]:\\(Users|Documents and Settings)\\")
TEX_INCLUDE = re.compile(r"\\(?:input|include|includegraphics|bibliography|addbibresource|subfile|import)"
                         r"\*?(?:\[[^\]]*\])?\{([^}]*)\}")
MOVING_REVS = {"main", "master", "HEAD", "dev", "develop", "nightly", "stable", "latest"}


def isolation_problems(d: Path) -> list[str]:
    """Self-containment: no symlinks, no references outside the contribution."""
    out = []
    root = d.resolve()
    for p in sorted(d.rglob("*")):
        if ".lake" in p.relative_to(d).parts:
            continue
        if p.is_symlink():
            out.append(f"symbolic link not allowed: {p.relative_to(d)}")
            continue  # never read through a link
        if p.suffix.lower() in TEXT_SUFFIXES and p.is_file():
            text = p.read_text(errors="replace")
            if p.suffix == ".tex":
                for group in TEX_INCLUDE.findall(strip_tex_comments(text)):
                    for target in (x.strip() for x in group.split(",")):
                        # LaTeX resolves relative paths from the build directory (paper/).
                        if target.startswith(("/", "~")) or not (d / "paper" / target).resolve().is_relative_to(root):
                            out.append(f"{p.relative_to(d)}: LaTeX reference outside the contribution ({target})")
            if LOCAL_PATH.search(text):
                out.append(f"{p.relative_to(d)}: absolute local path")
    lake = d / "lean" / "lakefile.toml"
    if lake.exists() and not lake.is_symlink():
        try:
            conf = tomllib.loads(lake.read_text())
        except tomllib.TOMLDecodeError as exc:
            return out + [f"lean/lakefile.toml is not valid TOML: {exc}"]
        for req in conf.get("require", []):
            if not isinstance(req, dict):
                out.append("lean/lakefile.toml: malformed [[require]] entry")
            elif "path" in req:
                out.append(f"lean/lakefile.toml: local path dependency {req['path']!r}")
            elif "git" not in req and "scope" not in req:
                out.append(f"lean/lakefile.toml: dependency {req.get('name')} is not pinned to a git source")
            elif not req.get("rev"):
                out.append(f"lean/lakefile.toml: dependency {req.get('name')} has no pinned rev")
            elif req["rev"] in MOVING_REVS:
                out.append(f"lean/lakefile.toml: dependency {req.get('name')} follows the moving branch {req['rev']!r}")
    return out


# --------------------------------------------------------------------------- lean


def lean_audit(lean_dir: Path, theorems: list[str], build: bool = True, fetch_cache: bool = True) -> Report:
    """Build a Lake package and audit the transitive axioms of the given declarations."""
    rep = Report(f"lean {lean_dir}")
    if shutil.which("lake") is None:
        rep.error("lake not found (install elan: https://github.com/leanprover/elan)")
        return rep
    if build:
        if fetch_cache and "mathlib" in (lean_dir / "lakefile.toml").read_text():
            r = run(["lake", "exe", "cache", "get"], lean_dir)
            if r.returncode != 0:
                rep.warn("`lake exe cache get` failed; building from source")
        r = run(["lake", "build"], lean_dir)
        if r.returncode != 0:
            rep.error("lake build failed:\n" + tail(r.stdout + r.stderr, 40))
            return rep
        rep.note("lake build: passing")
        rep.errors += orphan_modules(lean_dir)
    if not theorems:
        rep.error("no main theorems to audit")
        return rep
    bad = [t for t in theorems if not isinstance(t, str) or not LEAN_NAME_RE.match(t)]
    if bad:  # names are spliced into a Lean file: never let one inject commands
        rep.error(f"invalid Lean declaration names: {bad!r}")
        return rep
    roots = lake_roots(lean_dir)
    probe = "\n".join([f"import {m}" for m in roots] + [""] + [f"#print axioms {t}" for t in theorems])
    with tempfile.NamedTemporaryFile("w", suffix=".lean", dir=lean_dir, delete=False) as fh:
        fh.write(probe)
        probe_path = Path(fh.name)
    try:
        r = run(["lake", "env", "lean", probe_path.name], lean_dir)
    finally:
        probe_path.unlink(missing_ok=True)
    text = r.stdout + r.stderr
    if r.returncode != 0 and "error" in text:
        rep.error("axiom probe failed:\n" + tail(text, 30))
        return rep
    found = parse_axiom_report(text, theorems)
    for t in theorems:
        if t not in found:
            rep.error(f"{t}: no axiom report (declaration missing?)")
            continue
        extra = found[t] - STANDARD_AXIOMS
        if extra:
            rep.error(f"{t}: non-standard axioms {sorted(extra)}")
        else:
            rep.note(f"{t}: axioms {sorted(found[t]) or ['(none)']}")
    return rep


def parse_axiom_report(text: str, theorems: list[str]) -> dict[str, set[str]]:
    found: dict[str, set[str]] = {}
    for t in theorems:
        short = re.escape(t)
        m = re.search(rf"'{short}' depends on axioms: \[(.*?)\]", text, re.S)
        if m:
            found[t] = {a.strip() for a in m.group(1).replace("\n", " ").split(",") if a.strip()}
        elif re.search(rf"'{short}' does not depend on any axioms", text):
            found[t] = set()
    return found


def lake_roots(lean_dir: Path) -> list[str]:
    conf = tomllib.loads((lean_dir / "lakefile.toml").read_text())
    roots = []
    for lib in conf.get("lean_lib", []):
        roots += lib.get("roots", [lib["name"]])
    return roots


# `import M`, and the module-system forms `public import M`, `meta import M`, `import all M`.
IMPORT_RE = re.compile(r"^[ \t]*(?:public[ \t]+)?(?:meta[ \t]+)?import[ \t]+(?:all[ \t]+)?([\w.'«»]+)",
                       re.M)


def orphan_modules(lean_dir: Path) -> list[str]:
    """Every .lean source must be imported (transitively) by a library root."""
    roots = lake_roots(lean_dir)
    sources = {}
    for f in lean_dir.rglob("*.lean"):
        if ".lake" in f.relative_to(lean_dir).parts or f.name == "lakefile.lean":
            continue
        mod = ".".join(f.relative_to(lean_dir).with_suffix("").parts)
        sources[mod] = f
    seen, stack = set(), [r for r in roots if r in sources]
    while stack:
        mod = stack.pop()
        if mod in seen:
            continue
        seen.add(mod)
        for imp in IMPORT_RE.findall(strip_lean_comments(sources[mod].read_text(errors="replace"))):
            if imp in sources:
                stack.append(imp)
    return [f"Lean module {m} is not imported by any library root" for m in sorted(set(sources) - seen)]


def tail(text: str, n: int) -> str:
    return "\n".join(text.strip().splitlines()[-n:])


# --------------------------------------------------------------------------- paper


def paper_check(paper_dir: Path, build: bool = True, status: str | None = None) -> Report:
    rep = Report(f"paper {paper_dir}")
    main = paper_dir / "main.tex"
    if build:
        if shutil.which("latexmk") is None:
            rep.error("latexmk not found (install a TeX distribution, e.g. TeX Live)")
            return rep
        r = run(["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], paper_dir)
        if r.returncode != 0:
            rep.error("latexmk failed:\n" + tail(r.stdout, 30))
            return rep
        rep.note("latexmk: passing")
    log = paper_dir / "main.log"
    if log.exists():
        text = log.read_text(errors="replace")
        for pat, what in [
            (r"LaTeX Warning: Reference `([^']+)' on page", "undefined reference"),
            (r"LaTeX Warning: Citation `([^']+)' on page", "undefined citation"),
            (r"LaTeX Warning: Label `([^']+)' multiply defined", "duplicate label"),
            (r"! LaTeX Error: File `([^']+)' not found", "missing file"),
        ]:
            for m in sorted(set(re.findall(pat, text))):
                rep.error(f"{what}: {m}")
        if "There were undefined references" in text:
            rep.error("undefined references reported by LaTeX")
        for m in re.findall(r"Overfull \\hbox \((\d+\.\d+)pt too wide\)", text):
            if float(m) > 10.0:
                rep.error(f"overfull hbox {m}pt (> 10pt)")
            elif float(m) > 1.0:
                rep.warn(f"overfull hbox {m}pt")
    rep.errors += pdf_layout_problems(paper_dir / "main.pdf", status=status, warnings=rep.warnings)
    return rep


def preprint_label_problems(page1: str) -> list[str]:
    """A preprint says so on its title page, next to its status statement."""
    if re.search(r"\bpreprint\b", page1, re.I):
        return []
    return ["page 1: the word 'Preprint' (status statement of a preprint) not found"]


def preprint_page1_problems(pdf: Path) -> list[str]:
    """Page-1 check of a preprint on its own (fails closed without pdftotext)."""
    pdf = pdf.resolve()
    if not pdf.exists():
        return ["main.pdf missing"]
    if shutil.which("pdftotext") is None:
        return ["pdftotext not found (install poppler-utils): the preprint label cannot be checked"]
    r = run(["pdftotext", "-layout", "-f", "1", "-l", "1", str(pdf), "-"], pdf.parent)
    if r.returncode != 0:
        return ["pdftotext could not read main.pdf: " + tail(r.stderr, 3)]
    return preprint_label_problems(r.stdout)


TOC_SPILL_LIMIT = 10  # a continuation shorter than this is a spill worth tightening


def toc_spill_lines(pages: list[str], body_start: int, heading: re.Pattern) -> int:
    """Non-empty text lines of the table of contents that continue past page 2, i.e. on
    pages 3 .. body_start before the "1. Introduction" heading. A first line without
    lower-case letters is the running head (set in capitals) and is not counted."""
    count = 0
    for i in range(2, body_start + 1):
        lines = [ln for ln in pages[i].splitlines() if ln.strip()]
        if lines and not re.search(r"[a-z]", lines[0]):
            lines = lines[1:]
        if i == body_start:
            lines = lines[:next((k for k, ln in enumerate(lines) if heading.match(ln)), len(lines))]
        count += len(lines)
    return count


def pdf_layout_problems(pdf: Path, status: str | None = None, warnings: list[str] | None = None) -> list[str]:
    """Front matter on page 1, contents from page 2, introduction on a fresh page,
    all fonts embedded, disclosure and MSC present; for a preprint, the word "Preprint"
    on page 1. Returns the errors; layout warnings (a table of contents spilling a few
    lines past page 2) are appended to ``warnings`` when a list is given."""
    pdf = pdf.resolve()
    out: list[str] = []
    if not pdf.exists():
        return ["main.pdf missing"]
    if shutil.which("pdftotext") is None:  # fail closed: an unchecked layout is not a passing layout
        return ["pdftotext not found (install poppler-utils): the PDF layout cannot be checked"]
    r = run(["pdftotext", "-layout", str(pdf), "-"], pdf.parent)
    if r.returncode != 0:
        return ["pdftotext could not read main.pdf: " + tail(r.stderr, 3)]
    pages = r.stdout.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()  # pdftotext ends every page, including the last, with a form feed
    if len(pages) < 3:
        return ["PDF has fewer than three pages (front matter, contents, body expected)"]
    p1, p2 = pages[0], pages[1]
    if "Abstract" not in p1 and "ABSTRACT" not in p1:
        out.append("page 1: abstract not found")
    if not re.search(r"Mathematics Subject Classification|MSC", p1):
        out.append("page 1: MSC classification not found")
    if not re.search(r"artificial intelligence|AI-assisted", p1, re.I):
        out.append("page 1: short AI disclosure not found")
    if re.search(r"^\s*1\.\s+Introduction", p1, re.M | re.I):
        out.append("page 1: introduction starts on the title page")
    if status == "preprint":
        out += preprint_label_problems(p1)
    if not re.search(r"Contents", p2):
        out.append("page 2: table of contents not found")
    heading = re.compile(r"^\s*1\.\s+Introduction\s*$", re.M | re.I)
    body_start = next((i for i, pg in enumerate(pages) if i >= 1 and "Contents" not in pg and heading.search(pg)), None)
    if body_start is None:
        out.append("introduction heading (section 1) not found on a page of its own after the contents")
    elif body_start < 2:
        out.append("introduction must start on a page after the table of contents")
    elif warnings is not None:
        spill = toc_spill_lines(pages, body_start, heading)
        if 0 < spill < TOC_SPILL_LIMIT:
            warnings.append(f"table of contents spills {spill} lines onto page 3; tighten it so it fits on page 2")
    full = "\n".join(pages)
    if not re.search(r"AI-assisted research disclosure", full, re.I):
        out.append("detailed 'AI-assisted research disclosure' section not found")
    if shutil.which("pdffonts"):
        fonts = run(["pdffonts", str(pdf)], pdf.parent).stdout.splitlines()[2:]
        for line in fonts:
            cols = line.split()
            if len(cols) >= 5 and "no" in cols[-5:-4]:
                out.append(f"font not embedded: {cols[0]}")
    return out


# --------------------------------------------------------------------------- catalogue


PREPRINT_SECTION = "Preprints (complete written arguments, not yet kernel-verified)"
VERIFICATION_DIMENSIONS = ["proof", "certificates", "formalization", "build", "axioms", "statement_review",
                           "independent_review", "literature_review"]


def _cell(value) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def catalogue_files() -> dict[str, str]:
    metas = [(d, load_meta(d)) for d in result_dirs()]
    head = "<!-- Generated by scripts/afm.py catalogue from results/*/result.toml. Do not edit. -->\n\n"
    none_yet = "No contribution has been released yet."

    def link(d, m):
        return f"[{m['id']}](../results/{d.name}/README.md)"

    published = [(d, m) for d, m in metas if m.get("status") != "preprint"]
    preprints = [(d, m) for d, m in metas if m.get("status") == "preprint"]
    results = head + "# Results\n\n"
    if not metas:
        results += none_yet + "\n"
    else:
        results += "## Published results (level V4)\n\n"
        if published:
            results += "| Identifier | Title | MSC2020 | Version | Status |\n|---|---|---|---|---|\n" + "\n".join(
                f"| {link(d, m)} | {_cell(m['title'])} | {m['msc_primary']} | {m['version']} | {m['status']} |"
                for d, m in published) + "\n"
        else:
            results += "No contribution has reached the published tier (level V4) yet.\n"
        results += f"\n## {PREPRINT_SECTION}\n\n"
        if preprints:
            results += ("A preprint's main theorems are not established by the archive until they reach level V4; "
                        "see the verification policy.\n\n")
            results += ("| Identifier | Title | MSC2020 | Version | Theorem | "
                        + " | ".join(dim.replace("_", " ").capitalize() for dim in VERIFICATION_DIMENSIONS) + " |\n|"
                        + "---|" * (5 + len(VERIFICATION_DIMENSIONS)) + "\n")
            for d, m in preprints:
                for th in m.get("theorem", []):
                    v = th.get("verification", {})
                    results += (f"| {link(d, m)} | {_cell(m['title'])} | {m['msc_primary']} | {m['version']} | "
                                f"{_cell(th.get('key', ''))} | "
                                + " | ".join(_cell(v.get(dim)) for dim in VERIFICATION_DIMENSIONS) + " |\n")
        else:
            results += "No preprint.\n"
    by_msc: dict[str, list[str]] = {}
    for d, m in metas:
        mark = " (preprint)" if m.get("status") == "preprint" else ""
        for code in [m["msc_primary"]] + list(m.get("msc_secondary", [])):
            by_msc.setdefault(code, []).append(f"{link(d, m)} {m['title']}{mark}")
    topics = head + "# Results by MSC2020 class\n\n" + ("\n".join(
        f"## {code}\n\n" + "\n".join(f"- {x}" for x in sorted(items)) + "\n" for code, items in sorted(by_msc.items()))
        if by_msc else none_yet + "\n")
    vrows = []
    for d, m in metas:
        for th in m.get("theorem", []):
            v = th.get("verification", {})
            decl = f"`{th['lean']}`" if th.get("lean") else "in preparation"
            if th.get("lean_conditional"):
                decl += "; conditional: " + ", ".join(f"`{c}`" for c in th["lean_conditional"])
            vrows.append(f"| {m['id']} | {m['status']} | {_cell(th['statement'])} | {decl} | {v.get('proof')} | "
                         f"{v.get('formalization')} | {v.get('axioms')} | {v.get('independent_review')} |")
    verification = head + "# Verification status\n\n" + (
        "| Result | Status | Theorem | Lean declaration | Proof | Formalization | Axioms | Independent review |\n"
        "|---|---|---|---|---|---|---|---|\n" + "\n".join(vrows) if vrows else none_yet) + "\n"
    return {"results.md": results, "topics.md": topics, "verification.md": verification}


def cmd_catalogue(args) -> int:
    files = catalogue_files()
    stale = []
    for name, text in files.items():
        path = CATALOGUE / name
        if args.check:
            if not path.exists() or path.read_text() != text:
                stale.append(name)
        else:
            CATALOGUE.mkdir(exist_ok=True)
            path.write_text(text)
    if args.check and stale:
        print("stale catalogue files: " + ", ".join(stale) + " (run `make catalogue`)")
        return 1
    print("catalogue up to date" if args.check else f"wrote {len(files)} catalogue files")
    return 0


# --------------------------------------------------------------------------- commands


def cmd_list(args) -> int:
    for d in result_dirs():
        m = load_meta(d)
        print(f"{m['id']}  v{m['version']:<7} {m['status']:<10} {m['title']}")
    if not result_dirs():
        print("no contributions yet")
    return 0


def cmd_check(args) -> int:
    dirs = [resolve(n) for n in args.results] if args.results else result_dirs()
    reports = [check_result(d) for d in dirs]
    for r in reports:
        print(r.render())
    return 0 if all(r.ok for r in reports) else 1


def theorem_names(d: Path) -> list[str]:
    """Every declaration to audit: the `lean` name of each theorem (when given) and its
    `lean_conditional` declarations."""
    names: list[str] = []
    for t in load_meta(d).get("theorem", []):
        for name in ([t.get("lean")] if t.get("lean") else []) + list(t.get("lean_conditional", [])):
            if name not in names:
                names.append(name)
    return names


def lean_report(d: Path, build: bool = True) -> Report:
    names = theorem_names(d)
    if not names and load_meta(d).get("status") == "preprint":
        rep = Report(f"lean {d / 'lean'}")
        rep.note("preprint: no Lean declaration to audit yet (formalization in preparation)")
        return rep
    return lean_audit(d / "lean", names, build=build)


def cmd_lean(args) -> int:
    d = resolve(args.result)
    rep = lean_report(d, build=not args.no_build)
    print(rep.render())
    return 0 if rep.ok else 1


def cmd_paper(args) -> int:
    d = resolve(args.result)
    rep = paper_check(d / "paper", build=not args.no_build, status=load_meta(d).get("status"))
    print(rep.render())
    return 0 if rep.ok else 1


def verify_dir(d: Path) -> list[Report]:
    reps = [check_result(d)]
    reps.append(lean_report(d))
    reps.append(paper_check(d / "paper", status=load_meta(d).get("status")))
    return reps


def cmd_verify(args) -> int:
    reps = verify_dir(resolve(args.result))
    for r in reps:
        print(r.render())
    return 0 if all(r.ok for r in reps) else 1


def cmd_isolate(args) -> int:
    src = resolve(args.result)
    with tempfile.TemporaryDirectory(prefix="afm-isolation-") as tmp:
        dst = Path(tmp) / src.name
        shutil.copytree(src, dst, symlinks=True, ignore=shutil.ignore_patterns(".lake", "*.aux", "*.log", "*.fls",
                                                                                "*.fdb_latexmk", "*.out", "*.toc"))
        print(f"isolated copy: {dst}")
        reps = verify_dir(dst)
        for r in reps:
            print(r.render())
        return 0 if all(r.ok for r in reps) else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="afm", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list").set_defaults(func=cmd_list)
    p = sub.add_parser("check")
    p.add_argument("results", nargs="*")
    p.set_defaults(func=cmd_check)
    for name, func in (("lean", cmd_lean), ("paper", cmd_paper)):
        p = sub.add_parser(name)
        p.add_argument("result")
        p.add_argument("--no-build", action="store_true")
        p.set_defaults(func=func)
    for name, func in (("verify", cmd_verify), ("isolate", cmd_isolate)):
        p = sub.add_parser(name)
        p.add_argument("result")
        p.set_defaults(func=func)
    p = sub.add_parser("catalogue")
    p.add_argument("--check", action="store_true")
    p.set_defaults(func=cmd_catalogue)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
