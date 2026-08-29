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


def run(root: Path, plan: Path, *prior_plans: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            str(CHECKER),
            "--plan",
            str(plan),
            "--root",
            str(root),
            *[item for prior in prior_plans for item in ("--prior-plan", str(prior))],
        ],
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


def sized_plan(lines: int) -> str:
    base = GOOD_PLAN.splitlines()
    notes = [f"Evidence note {index}." for index in range(lines - len(base))]
    return "\n".join([*base, *notes]) + "\n"


def _assert_refuses_oversized_plan(tmp_path: Path) -> None:
    root = repository(tmp_path)
    result = run(root, write_plan(tmp_path, sized_plan(601)))
    assert result.returncode == 1
    assert "plan-size" in result.stdout
    assert "601 lines" in result.stdout


def _assert_refuses_more_than_one_third_growth(tmp_path: Path) -> None:
    root = repository(tmp_path)
    prior = tmp_path / "prior.md"
    prior.write_text(sized_plan(300))
    current = write_plan(tmp_path, sized_plan(401))
    result = run(root, current, prior)
    assert result.returncode == 1
    assert "grew from 300 to 401 lines" in result.stdout


def _assert_refuses_second_growth_event(tmp_path: Path) -> None:
    root = repository(tmp_path)
    first = tmp_path / "first.md"
    second = tmp_path / "second.md"
    first.write_text(sized_plan(300))
    second.write_text(sized_plan(320))
    current = write_plan(tmp_path, sized_plan(330))
    result = run(root, current, first, second)
    assert result.returncode == 1
    assert "2 growth events" in result.stdout


def _assert_one_bounded_growth_event_passes(tmp_path: Path) -> None:
    root = repository(tmp_path)
    prior = tmp_path / "prior.md"
    prior.write_text(sized_plan(300))
    result = run(root, write_plan(tmp_path, sized_plan(330)), prior)
    assert result.returncode == 0, result.stdout


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
    _assert_refuses_oversized_plan(tmp_path / "oversized")
    _assert_refuses_more_than_one_third_growth(tmp_path / "large-growth")
    _assert_refuses_second_growth_event(tmp_path / "second-growth")
    _assert_one_bounded_growth_event_passes(tmp_path / "bounded-growth")


def test_node_ids_and_line_ranges_resolve_to_members(tmp_path: Path) -> None:
    root = repository(tmp_path)
    text = GOOD_PLAN.replace(
        "- `policies/example.md` — cite",
        "- `policies/example.md` — cite; extend `lib/widgets.py::document_identity_key`,\n"
        "  `lib/widgets.py:4–5`, and `lib/widgets.py::absent_helper`; add\n"
        "  `tests/test_frob.py::test_frobnicates` (new test file below)",
    ).replace(
        "- **Path**: `lib/frob.py`",
        "- **Path**: `lib/frob.py`\n- **Path**: `tests/test_frob.py`",
    )
    result = run(root, write_plan(tmp_path, text))
    assert result.returncode == 1, result.stdout
    rows = result.stdout.splitlines()
    assert len(rows) == 1 and "member-missing" in rows[0] and "absent_helper" in rows[0], rows
