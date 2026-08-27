"""Behavioral tests for bin/check-plan-delivery."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "bin" / "check-plan-delivery"

PLAN = """# Implementation Plan: Example

## Definitions Read

| Identifier | Defined at | Kind |
|---|---|---|
| `existing_helper` | `lib/widgets.py:1` | read |
| `frobnicate_widget` | new — `lib/frob.py` | introduced |
| `Frobnicator.spin` | new — `lib/frob.py` | introduced |

## File Changes

### New Files
- **Path**: `lib/frob.py`
- **Path**: `tests/test_frob.py`

## Testing Strategy
- **Unit tests**: `tests/test_frob.py::test_frobnicates`, `test_spin_is_idempotent`
- Existing coverage: `tests/test_widgets.py::test_existing_helper`

## Build Gate Sequence

```bash
./bin/test tests/test_frob.py
```
"""


def repository(tmp_path: Path, *, delivered: bool) -> Path:
    root = tmp_path / "repo"
    (root / "lib").mkdir(parents=True)
    (root / "tests").mkdir()
    (root / "lib" / "widgets.py").write_text("def existing_helper():\n    return 1\n")
    (root / "tests" / "test_widgets.py").write_text(
        "def test_existing_helper():\n    assert True\n"
    )
    if delivered:
        (root / "lib" / "frob.py").write_text(
            "def frobnicate_widget():\n    return 2\n\n\n"
            "class Frobnicator:\n    def spin(self):\n        return 3\n"
        )
        (root / "tests" / "test_frob.py").write_text(
            "def test_frobnicates():\n    assert True\n\n\n"
            "def test_spin_is_idempotent():\n    assert True\n"
        )
    subprocess.run(["git", "init", "-q", "-b", "master", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "add", "."], check=True)
    return root


def run(root: Path, plan: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(CHECKER), "--plan", str(plan), "--root", str(root), *extra],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def write(tmp_path: Path, name: str, text: str) -> Path:
    path = tmp_path / name
    path.write_text(text)
    return path


def test_undeclared_narrowing_still_fails_with_a_report(tmp_path: Path) -> None:
    root = repository(tmp_path, delivered=True)
    (root / "lib" / "frob.py").write_text("def frobnicate_widget():\n    return 2\n")
    subprocess.run(["git", "-C", str(root), "add", "."], check=True)
    report = write(tmp_path, "coder.md", "### Notes\n- nothing to declare\n")
    result = run(root, write(tmp_path, "plan.md", PLAN), "--deviations", str(report))
    assert result.returncode == 1
    assert "ERROR\tintroduced-missing" in result.stdout
