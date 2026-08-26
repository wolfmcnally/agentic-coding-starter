"""Behavioral tests for bin/check-plan-concreteness."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "bin" / "check-plan-concreteness"

SCRIPT = """#!/usr/bin/env python3
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--run-dir")
parser.add_argument("--fuzz")
"""

MODULE = '''"""Widgets."""


class Mode:
    FAST_PATH = "fast"


def document_identity_key(document):
    return document.provenance.records  # TODO: bind the key
'''


def repository(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "bin").mkdir(parents=True)
    (root / "lib").mkdir()
    (root / "bin" / "tool").write_text(SCRIPT)
    (root / "bin" / "tool").chmod(0o755)
    (root / "bin" / "test").write_text('#!/usr/bin/env bash\npytest "$@"\n')
    (root / "bin" / "test").chmod(0o755)
    (root / "lib" / "widgets.py").write_text(MODULE)
    (root / "policies").mkdir()
    (root / "policies" / "example.md").write_text("# Example\n")
    subprocess.run(["git", "init", "-q", "-b", "master", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "add", "."], check=True)
    return root


def run(root: Path, plan: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(CHECKER), "--plan", str(plan), "--root", str(root)],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


GOOD_PLAN = """# Implementation Plan: Example

## Definitions Read

| Identifier | Defined at | Kind |
|---|---|---|
| `Mode.FAST_PATH` | `lib/widgets.py:5` | read |
| `document_identity_key` | `lib/widgets.py` | read |
| `frobnicate_widget` | new — `lib/frob.py` | introduced |

## Surfaces Touched
- `lib/widgets.py` — extend `document_identity_key`
- `policies/example.md` — cite

## File Changes

### New Files
- **Path**: `lib/frob.py`
- **Key types / functions / classes / exports**: `frobnicate_widget`

## Build Gate Sequence

```bash
./bin/tool --run-dir /tmp/run --fuzz=0
./bin/test tests/test_frob.py -k frob
```
"""


def write_plan(tmp_path: Path, text: str) -> Path:
    plan = tmp_path / "plan.md"
    plan.write_text(text)
    return plan


def test_concrete_plan_passes(tmp_path: Path) -> None:
    root = repository(tmp_path)
    result = run(root, write_plan(tmp_path, GOOD_PLAN))
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == "PLAN CONCRETENESS PASS"


def test_missing_definitions_table_refuses(tmp_path: Path) -> None:
    root = repository(tmp_path)
    text = GOOD_PLAN.replace("## Definitions Read", "## Things I Looked At")
    result = run(root, write_plan(tmp_path, text))
    assert result.returncode == 1
    assert "definitions-missing" in result.stdout


def test_unread_identifier_refuses_and_declared_new_passes(tmp_path: Path) -> None:
    root = repository(tmp_path)
    text = GOOD_PLAN.replace(
        "- `policies/example.md` — cite",
        "- `policies/example.md` — cite; use `Mode.FAST` and `provision_json`",
    )
    result = run(root, write_plan(tmp_path, text))
    assert result.returncode == 1
    assert "identifier-unread\t" in result.stdout
    assert "`Mode.FAST`" in result.stdout
    assert "`provision_json`" in result.stdout
    # `frobnicate_widget` is cited in the plan but declared new, so it is fine.
    assert "frobnicate_widget" not in result.stdout


def test_definition_row_is_verified_against_its_file(tmp_path: Path) -> None:
    root = repository(tmp_path)
    text = GOOD_PLAN.replace("`lib/widgets.py:5`", "`lib/widgets.py:2`").replace(
        "| `document_identity_key` | `lib/widgets.py` | read |",
        "| `document_identity_key` | `lib/absent.py` | read |",
    )
    result = run(root, write_plan(tmp_path, text))
    assert result.returncode == 1
    assert "definition-line-mismatch" in result.stdout
    assert "definition-file-missing" in result.stdout


def test_missing_path_refuses_unless_declared_new(tmp_path: Path) -> None:
    root = repository(tmp_path)
    text = GOOD_PLAN.replace("- `policies/example.md` — cite", "- `policies/absent.md` — cite")
    result = run(root, write_plan(tmp_path, text))
    assert result.returncode == 1
    assert "path-missing\t" in result.stdout and "policies/absent.md" in result.stdout
    # `lib/frob.py` is a declared new file and never reported.
    assert "lib/frob.py" not in result.stdout


def test_commands_that_cannot_run_refuse(tmp_path: Path) -> None:
    root = repository(tmp_path)
    candidate = "a" * 64
    text = GOOD_PLAN.replace(
        "./bin/tool --run-dir /tmp/run --fuzz=0",
        "./bin/tool --run-dir <run> --only=phase\n"
        f"./bin/absent --x\n./bin/tool --expected-candidate {candidate}",
    )
    result = run(root, write_plan(tmp_path, text))
    assert result.returncode == 1
    rows = result.stdout.splitlines()
    assert any("command-placeholder" in row and "<run>" in row for row in rows)
    assert any("command-flag-unknown" in row and "--only" in row for row in rows)
    assert any("command-script-missing" in row and "./bin/absent" in row for row in rows)
    assert any("command-candidate-pinned" in row for row in rows)
    # Shell pass-through wrappers are not flag-checked: `-k` reaches pytest.
    assert not any("./bin/test" in row for row in rows)


def test_node_ids_and_line_ranges_resolve_to_members(tmp_path: Path) -> None:
    root = repository(tmp_path)
    text = GOOD_PLAN.replace(
        "- `policies/example.md` — cite",
        "- `policies/example.md` — cite; extend `lib/widgets.py::document_identity_key`,\n"
        "  `lib/widgets.py:4–5`, and `lib/widgets.py::absent_helper`; add\n"
        "  `tests/test_frob.py::test_frobnicates` (new test file below)",
    ).replace(
        "- **Path**: `lib/frob.py`", "- **Path**: `lib/frob.py`\n- **Path**: `tests/test_frob.py`"
    )
    result = run(root, write_plan(tmp_path, text))
    assert result.returncode == 1, result.stdout
    rows = result.stdout.splitlines()
    assert len(rows) == 1 and "member-missing" in rows[0] and "absent_helper" in rows[0], rows


def test_help_is_an_implicit_argparse_flag(tmp_path: Path) -> None:
    root = repository(tmp_path)
    text = GOOD_PLAN.replace("./bin/tool --run-dir /tmp/run --fuzz=0", "./bin/tool --help")
    result = run(root, write_plan(tmp_path, text))
    assert result.returncode == 0, result.stdout


def test_deferrals_refuse(tmp_path: Path) -> None:
    root = repository(tmp_path)
    text = GOOD_PLAN + (
        "\n## Architecture Decisions\n"
        "- Verify the provenance field name before coding.\n"
        "- Run `./bin/tool` or equivalent.\n"
        "- Threshold TBD.\n"
    )
    result = run(root, write_plan(tmp_path, text))
    assert result.returncode == 1
    deferrals = [row for row in result.stdout.splitlines() if row.startswith("ERROR\tdeferral")]
    assert len(deferrals) == 3, result.stdout


def test_words_inside_code_spans_are_not_deferrals(tmp_path: Path) -> None:
    root = repository(tmp_path)
    text = GOOD_PLAN + "\n- Remove every `TODO` marker from `lib/widgets.py`.\n"
    result = run(root, write_plan(tmp_path, text))
    assert result.returncode == 0, result.stdout


def test_missing_plan_is_a_usage_error(tmp_path: Path) -> None:
    root = repository(tmp_path)
    result = run(root, tmp_path / "nope.md")
    assert result.returncode == 2
    assert "cannot read plan" in result.stderr
