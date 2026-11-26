"""Static Lean source checks: forbidden constructs inside and outside comments, and the
comment lexer (nested block comments, strings, character literals)."""

from __future__ import annotations

import pytest


def problems(afm, tmp_path, source: str, name: str = "Main.lean"):
    lean = tmp_path / "lean"
    (lean / "Pkg").mkdir(parents=True, exist_ok=True)
    (lean / "Pkg" / name).write_text(source)
    return afm.lean_source_problems(lean)


FORBIDDEN = [
    ("theorem t : False := by sorry", "sorry"),
    ("theorem t : False := sorry", "sorry"),
    ("theorem t : False := sorryAx False false", "sorryAx"),
    ("theorem t : False := by admit", "admit"),
    ("axiom bad : False", "axiom declaration"),
    ("protected axiom bad : False", "axiom declaration"),
    ("noncomputable axiom choice' : Nat", "axiom declaration"),
    ("@[simp] axiom bad : 1 = 2", "axiom declaration"),
    ("/-- doc -/ axiom bad : False", "axiom declaration"),
    ("  axiom   indented : False", "axiom declaration"),
    ("theorem t : 2 + 2 = 4 := by native_decide", "native_decide"),
    ("@[implemented_by foo] def bar : Nat := 0", "implemented_by"),
    ('@[extern "c_fn"] opaque f : Nat → Nat', "extern"),
    ("set_option debug.skipKernelTC true", "kernel check disabled"),
]


@pytest.mark.parametrize("source,what", FORBIDDEN)
def test_forbidden_constructs_in_code(afm, tmp_path, source, what):
    out = problems(afm, tmp_path, source + "\n")
    assert any(f"forbidden construct ({what})" in p for p in out), out
    assert all(p.startswith("lean/Pkg/Main.lean:") for p in out)


@pytest.mark.parametrize("source,_what", FORBIDDEN)
def test_forbidden_words_inside_comments_are_ignored(afm, tmp_path, source, _what):
    text = f"-- {source}\n/- {source} -/\n/-- {source} -/\n/-! {source} -/\ntheorem ok : True := trivial\n"
    assert problems(afm, tmp_path, text) == []


@pytest.mark.parametrize("source", [
    "theorem sorry_free : True := trivial",
    "theorem admits_nothing : True := trivial",
    "def my_axiom := 1",
    "theorem uses_axioms : True := trivial  -- mentions axioms",
    "#print axioms Foo.bar",
    "theorem axiomatic : True := trivial",
    "def nativeDecideLike := 3",
])
def test_identifiers_containing_forbidden_words_are_fine(afm, tmp_path, source):
    assert problems(afm, tmp_path, source + "\n") == []


def test_nested_block_comment(afm, tmp_path):
    text = "/- outer /- inner -/ still comment: sorry -/\ntheorem ok : True := trivial\n"
    assert problems(afm, tmp_path, text) == []


def test_code_after_nested_comment_is_scanned(afm, tmp_path):
    text = "/- outer /- inner -/ comment -/\ntheorem bad : False := sorry\n"
    assert any("sorry" in p for p in problems(afm, tmp_path, text))


def test_block_opener_inside_line_comment_does_not_hide_code(afm, tmp_path):
    """Regression: `-- see /-` opened a (regex) block comment that swallowed real code
    up to the next `-/`, hiding the sorry below."""
    text = "-- note: /- unbalanced\ntheorem bad : False := sorry\n-- -/\n"
    assert any("sorry" in p for p in problems(afm, tmp_path, text))


def test_line_comment_marker_inside_string_does_not_hide_code(afm, tmp_path):
    """Regression: `--` inside a string literal truncated the rest of the line."""
    text = 'def s : String := "--"; theorem bad : False := sorry\n'
    assert any("sorry" in p for p in problems(afm, tmp_path, text))


def test_block_marker_inside_string_does_not_hide_code(afm, tmp_path):
    text = 'def s : String := "/-"\ntheorem bad : False := sorry\ndef e : String := "-/"\n'
    assert any("sorry" in p for p in problems(afm, tmp_path, text))


def test_char_literal_quote_does_not_open_a_string(afm, tmp_path):
    text = "def c : Char := '\"'\ntheorem bad : False := sorry\ndef d : Char := '\"'\n"
    assert any("sorry" in p for p in problems(afm, tmp_path, text))


def test_primed_identifiers_are_not_char_literals(afm, tmp_path):
    text = "theorem h' : True := trivial\ntheorem h'' : True := by sorry\n"
    assert any("sorry" in p for p in problems(afm, tmp_path, text))


def test_forbidden_word_in_string_is_reported_conservatively(afm, tmp_path):
    assert any("sorry" in p for p in problems(afm, tmp_path, 'def msg : String := "sorry"\n'))


def test_lake_directory_is_ignored(afm, tmp_path):
    lean = tmp_path / "lean"
    (lean / ".lake" / "packages" / "dep").mkdir(parents=True)
    (lean / ".lake" / "packages" / "dep" / "Bad.lean").write_text("axiom bad : False\n")
    assert afm.lean_source_problems(lean) == []


def test_missing_lean_directory(afm, tmp_path):
    assert afm.lean_source_problems(tmp_path / "nope") == []


@pytest.mark.parametrize("text,expected", [
    ("a /- x -/ b", "a  b"),
    ("a /- x /- y -/ z -/ b", "a  b"),
    ("x -- comment\ny", "x \ny"),
    ('"--" -- c', '"--" '),
    ('"esc \\" -- still string" -- c', '"esc \\" -- still string" '),
    ("/-- doc -/ theorem t", " theorem t"),
    ("/- multi\nline\n-/ x", "\n\n x"),
])
def test_strip_lean_comments(afm, text, expected):
    assert afm.strip_lean_comments(text) == expected


def test_strip_lean_comments_keeps_line_count(afm):
    text = "a\n/- b\nc\n-/\nd -- e\nf\n"
    assert afm.strip_lean_comments(text).count("\n") == text.count("\n")


def test_unterminated_block_comment_swallows_rest(afm):
    assert afm.strip_lean_comments("ok /- never closed sorry") == "ok "
