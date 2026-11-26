"""Self-containment of a contribution: symbolic links, absolute paths, LaTeX references
outside the contribution, and Lake dependencies."""

from __future__ import annotations

import os

import pytest

from archive_factory import make_result
from conftest import abspath


@pytest.fixture
def result(tmp_path):
    return make_result(tmp_path / "results")


def iso(afm, d):
    return afm.isolation_problems(d)


def test_clean_result_is_isolated(afm, result):
    assert iso(afm, result) == []


def test_symlink_to_file_and_directory(afm, result, tmp_path):
    secret = tmp_path / "outside.txt"
    secret.write_text(abspath("home", "someone", "notes") + "\n")
    os.symlink(secret, result / "logs" / "notes.md")
    os.symlink(tmp_path, result / "paper" / "figures")
    out = iso(afm, result)
    assert "symbolic link not allowed: logs/notes.md" in out
    assert "symbolic link not allowed: paper/figures" in out
    # The link target is never read: its absolute path must not be reported as content.
    assert not any("absolute local path" in o for o in out)


def test_dangling_symlink(afm, result):
    os.symlink("/nonexistent/target", result / "README-link.md")
    assert "symbolic link not allowed: README-link.md" in iso(afm, result)


@pytest.mark.parametrize("path", [abspath("home", "user", "x"), abspath("media", "disk", "x"),
                                  abspath("Users", "someone", "x"), abspath("mnt", "data", "x"),
                                  abspath("tmp", "build", "x"), abspath("root", "x"), abspath("Volumes", "External", "x"),
                                  abspath("var", "folders", "ab", "T", "x"), "C:\\Users\\someone\\x"])
@pytest.mark.parametrize("rel", ["README.md", "paper/main.tex", "lean/Sample.lean", "lean/lake-manifest.json",
                                 "logs/build.txt", "CITATION.cff"])
def test_absolute_local_paths(afm, result, path, rel):
    p = result / rel
    p.write_text((p.read_text() if p.exists() else "") + f"\nsee {path}\n")
    assert f"{rel}: absolute local path" in iso(afm, result)


@pytest.mark.parametrize("text", ["https://example.org/home/page", "see docs/home/x", "file.home/x"])
def test_urls_and_relative_paths_are_not_local_paths(afm, result, text):
    p = result / "README.md"
    p.write_text(p.read_text() + f"\n{text}\n")
    assert iso(afm, result) == []


@pytest.mark.parametrize("command", [
    r"\input{../../outside}", r"\include{../../../x}", r"\includegraphics[width=3cm]{../../fig.png}",
    r"\bibliography{../../refs}", r"\input{/abs/file}", r"\input{~/file}", r"\addbibresource{../../x.bib}",
    r"\bibliography{references,../../other}",
])
def test_latex_references_outside_the_contribution(afm, result, command):
    p = result / "paper" / "sections" / "introduction.tex"
    p.write_text(p.read_text() + "\n" + command + "\n")
    assert any("LaTeX reference outside the contribution" in o for o in iso(afm, result))


@pytest.mark.parametrize("command", [r"\input{sections/introduction}", r"\includegraphics{figures/plot.pdf}",
                                     r"\input{../lean/statement}", r"% \input{../../commented}"])
def test_latex_references_inside_are_fine(afm, result, command):
    p = result / "paper" / "sections" / "introduction.tex"
    p.write_text(p.read_text() + "\n" + command + "\n")
    assert iso(afm, result) == []


@pytest.mark.parametrize("require,needle", [
    ('[[require]]\nname = "dep"\npath = "../dep"\n', "local path dependency '../dep'"),
    ('[[require]]\nname = "dep"\n', "dependency dep is not pinned to a git source"),
    ('[[require]]\nname = "dep"\ngit = "https://example.org/dep.git"\n', "dependency dep has no pinned rev"),
    ('[[require]]\nname = "dep"\ngit = "https://example.org/dep.git"\nrev = "main"\n', "moving branch 'main'"),
    ('[[require]]\nname = "dep"\ngit = "https://example.org/dep.git"\nrev = "master"\n', "moving branch 'master'"),
    ('[[require]]\nname = "mathlib"\nscope = "leanprover-community"\n', "dependency mathlib has no pinned rev"),
])
def test_lakefile_dependencies(afm, result, require, needle):
    lf = result / "lean" / "lakefile.toml"
    lf.write_text(lf.read_text() + "\n" + require)
    assert any(needle in o for o in iso(afm, result)), iso(afm, result)


@pytest.mark.parametrize("rev", ["v4.34.0", "0123456789abcdef0123456789abcdef01234567"])
def test_pinned_dependencies_are_fine(afm, result, rev):
    lf = result / "lean" / "lakefile.toml"
    lf.write_text(lf.read_text() + f'\n[[require]]\nname = "dep"\ngit = "https://example.org/dep.git"\nrev = "{rev}"\n')
    assert iso(afm, result) == []


def test_invalid_lakefile_is_an_error_not_a_crash(afm, result):
    (result / "lean" / "lakefile.toml").write_text("name = \n[[lean_lib\n")
    out = iso(afm, result)
    assert any("lakefile.toml is not valid TOML" in o for o in out)
    assert not afm.check_result(result).ok


def test_lake_build_directory_is_ignored(afm, result):
    build = result / "lean" / ".lake" / "build"
    build.mkdir(parents=True)
    (build / "trace.json").write_text('{"path": "%s"}' % abspath("home", "someone", ".elan"))
    assert iso(afm, result) == []
