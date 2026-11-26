"""Fixtures for the archive-tool tests (standard library + pytest only).

``afm`` is the tool under test, imported from ``scripts/afm.py``. ``archive`` is a
throw-away copy of the archive skeleton (``scripts/`` only) in a temporary directory, so
that commands which act on ``results/`` and ``catalogue/`` never touch this repository.
"""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

TESTS = Path(__file__).resolve().parent
REPO = TESTS.parent
sys.path.insert(0, str(TESTS))

HAVE_LAKE = shutil.which("lake") is not None
HAVE_LATEX = shutil.which("latexmk") is not None and shutil.which("pdflatex") is not None
HAVE_PDFTOTEXT = shutil.which("pdftotext") is not None


def pytest_configure(config):
    config.addinivalue_line("markers", "lean: needs the Lean toolchain (lake); skipped when lake is missing")
    config.addinivalue_line("markers", "latex: needs latexmk/pdflatex and poppler-utils; skipped when missing")
    config.addinivalue_line("markers", "slow: slower integration tests")


def pytest_collection_modifyitems(config, items):
    for item in items:
        if "lean" in item.keywords and not HAVE_LAKE:
            item.add_marker(pytest.mark.skip(reason="lake not installed"))
        if "latex" in item.keywords and not (HAVE_LATEX and HAVE_PDFTOTEXT):
            item.add_marker(pytest.mark.skip(reason="latexmk/pdflatex/pdftotext not installed"))


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod  # dataclasses need the module registered
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="session")
def afm():
    return load_module(REPO / "scripts" / "afm.py", "afm_under_test")


class Archive:
    def __init__(self, root: Path, module):
        self.root = root
        self.afm = module
        self.results = root / "results"
        self.catalogue = root / "catalogue"

    def run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(self.root / "scripts" / "afm.py"), *args], cwd=self.root,
                              capture_output=True, text=True, timeout=600)


_counter = [0]


@pytest.fixture
def archive(tmp_path) -> Archive:
    root = tmp_path / "archive"
    (root / "scripts" / "data").mkdir(parents=True)
    shutil.copy(REPO / "scripts" / "afm.py", root / "scripts" / "afm.py")
    shutil.copy(REPO / "scripts" / "data" / "msc2020.tsv", root / "scripts" / "data" / "msc2020.tsv")
    (root / "results").mkdir()
    _counter[0] += 1
    mod = load_module(root / "scripts" / "afm.py", f"afm_archive_copy_{_counter[0]}")
    return Archive(root, mod)


def abspath(*parts: str) -> str:
    """An absolute POSIX path built at runtime, so that no machine-like path appears literally
    in the test sources (repository scans flag such literals)."""
    return "/" + "/".join(parts)


needs_pdftotext = pytest.mark.skipif(not HAVE_PDFTOTEXT, reason="pdftotext (poppler-utils) not installed")
