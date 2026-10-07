from __future__ import annotations

import json
import shlex
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "lib"))

import agentic_starter.mutation as mutation  # noqa: E402

CALC = (
    "def at_least(value, floor):\n"
    "    return value >= floor\n"
    "\n\n"
    "def label(value):\n"
    "    if value > 10:\n"
    '        return "big"\n'
    '    return "small"\n'
)
# The first proof never tries the boundary, so a fault there survives; the second does.
TESTS = (
    "import sys\n"
    'sys.path.insert(0, "lib")\n'
    "from calc import at_least, label\n"
    "\n\n"
    "def test_at_least():\n"
    "    assert at_least(5, 1)\n"
    "\n\n"
    "def test_label():\n"
    '    assert label(11) == "big" and label(10) == "small"\n'
)


def _repo(root: Path, declared: dict[str, object], *, tests: str = TESTS) -> Path:
    """A small repository with the real mutation tool behind a one-line test wrapper."""
    files = {
        "lib/calc.py": CALC,
        "tests/test_calc.py": tests,
        "bin/test": f'#!/bin/sh\nexec {shlex.quote(sys.executable)} -m pytest "$@"\n',
        "tests/proof-estate.yaml": json.dumps(
            {
                "mutation": declared,
                "families": [
                    {
                        "id": "calc",
                        "kind": "pytest",
                        "selectors": ["tests/test_calc.py"],
                        "covers": ["lib/calc.py"],
                        "source_paths": ["tests/test_calc.py"],
                    }
                ],
            }
        ),
    }
    for name, text in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text)
    (root / "bin/test").chmod(0o755)
    for arguments in (
        ("init", "-q", "-b", "master"),
        ("config", "user.email", "fixture@example.invalid"),
        ("config", "user.name", "Fixture"),
        ("add", "-A"),
        ("commit", "-qm", "base"),
    ):
        subprocess.run(["git", *arguments], cwd=root, check=True, capture_output=True)
    return root


MEASURED = {"tool": "cosmic-ray", "paths": ["lib/*.py"], "budget_seconds": 120}


def test_a_survey_reports_the_faults_tests_miss_on_the_changed_lines(
    tmp_path: Path,
) -> None:
    root = _repo(tmp_path, MEASURED)
    source = root / "lib/calc.py"
    source.write_text(CALC.replace("return value >= floor", "return not value < floor"))
    changed = source.read_bytes()

    observed = mutation.survey(root, changed_from="HEAD")

    assert (observed["state"], observed["files"]) == ("measured", ["lib/calc.py"])
    # Only the changed line is challenged, and the weak proof lets a fault on it live.
    assert observed["survivors"] and {row["line"] for row in observed["survivors"]} == {2}
    assert all(row["path"] == "lib/calc.py" and row["change"] for row in observed["survivors"])
    assert observed["generated"] == observed["killed"] + observed["survived"]
    # The fault was planted in a copy: the candidate file is untouched.
    assert source.read_bytes() == changed
    # A path filter narrows the scope; a pattern that matches nothing surveys nothing.
    assert mutation.survey(root, changed_from="HEAD", only=["lib/other*"])["files"] == []
    assert mutation.survey(root, changed_from="HEAD", only=["lib/calc.py"])["files"] == [
        "lib/calc.py"
    ]
    whole = mutation.survey(root, changed_from=None)
    assert whole["generated"] > observed["generated"] and whole["killed"] > 0


def test_a_repository_with_no_tool_reports_unmeasured_and_never_measured(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    reason = "No mutation tool is maintained for this language."
    root = _repo(tmp_path / "declared", {"tool": None, "reason": reason})
    assert mutation.survey(root, changed_from=None) == {
        "state": "unmeasured",
        "tool": None,
        "scope": {"all": True},
        "reason": reason,
    }
    assert mutation.main(["--root", str(root), "--all"]) == 0
    assert "MUTATE UNMEASURED" in capsys.readouterr().err
    silent = _repo(tmp_path / "silent", {"tool": None, "reason": " "})
    with pytest.raises(mutation.MutationError, match="must say why no mutation tool"):
        mutation.survey(silent, changed_from=None)


def test_a_survey_that_cannot_be_taken_fails_and_an_unfinished_one_is_partial(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # Tests that fail before any fault is planted cannot judge one.
    broken = _repo(tmp_path / "broken", MEASURED, tests=TESTS.replace("at_least(5, 1)", "False"))
    with pytest.raises(mutation.MutationError, match="tests fail before any fault is planted"):
        mutation.survey(broken, changed_from=None)
    assert mutation.main(["--root", str(broken), "--all"]) == 1
    assert "MUTATE ERROR" in capsys.readouterr().err
    # A budget that runs out reports what it did not finish, not a clean result.
    hurried = _repo(tmp_path / "hurried", {**MEASURED, "budget_seconds": 0.001})
    observed = mutation.survey(hurried, changed_from=None)
    assert (observed["state"], observed["unfinished"]) == ("partial", ["lib/calc.py"])
    assert observed["survivors"] == []
