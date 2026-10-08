"""Behavioral tests for bin/renumber-phases (opening a phase number for insertion)."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENUMBER = ROOT / "bin" / "renumber-phases"

INDEX = """\
# Plan

## Phase Dependency Graph

```mermaid
graph TD
    P1[Phase 1<br/>Done] --> P2[Phase 2<br/>Build]
    P2 --> P2_1[Phase 2.1<br/>Part]
    P2 --> P2_2[Phase 2.2<br/>Rest]
    P2 --> P3[Phase 3<br/>Ship]
```

## Phase Table

| Phase | Title | Status |
|---|---|---|
| [Phase 1](phase-1.md) | Done | ✅ |
| [Phase 2](phase-2.md) | Build | ⬅️ |
| [Phase 2.1](phase-2.1.md) | Part | ⏳ |
| [Phase 2.2](phase-2.2.md) | Rest | ⏳ |
| [Phase 3](phase-3.md) | Ship | ⏳ |

## Decomposition ledger (convention)

- **Deferred-work note, 2026-01-01.** Work found in Phase 2 was deferred to [Phase 3](phase-3.md).

## Cross-Cutting Concerns

None.
"""
PHASES = {
    "1": ("Done", "[]"),
    "2": ("Build", '["1"]'),
    "2.1": ("Part", '["2"]'),
    "2.2": ("Rest", '\n  - "2.1"'),
    "3": ("Ship", '["2", "2.2"]'),
}


def plan(root: Path) -> Path:
    (root / "plan").mkdir(parents=True)
    (root / "plan/INDEX.md").write_text(INDEX)
    for phase, (title, depends_on) in PHASES.items():
        (root / f"plan/phase-{phase}.md").write_text(
            f'---\nid: "{phase}"\ntitle: "{title}"\ndepends_on: {depends_on}\ninforms: []\n---\n\n'
            f"# Phase {phase} — {title}\n\nSee [Phase 2](phase-2.md); Phase 3 follows.\n"
        )
    return root


def run(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(RENUMBER), "--root", str(root), *arguments],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


def snapshot(root: Path) -> dict[str, bytes]:
    return {path.name: path.read_bytes() for path in sorted((root / "plan").iterdir())}


def test_inserting_a_phase_moves_every_later_upcoming_phase_and_its_references(
    tmp_path: Path,
) -> None:
    root = plan(tmp_path)
    result = run(root, "insert-before", "2", "--date", "2026-10-07", "--reason", "Review first.")
    assert result.returncode == 0, result.stderr
    names = sorted(path.name for path in (root / "plan").glob("phase-*.md"))
    assert names == ["phase-1.md", "phase-3.1.md", "phase-3.2.md", "phase-3.md", "phase-4.md"]
    # A moved file carries its new number in every structural place, and each link moves once.
    ship = (root / "plan/phase-4.md").read_text()
    assert 'id: "4"' in ship and 'depends_on: ["3", "3.2"]' in ship
    assert "# Phase 4 — Ship" in ship and "See [Phase 3](phase-3.md); Phase 3 follows." in ship
    assert '  - "3.1"' in (root / "plan/phase-3.2.md").read_text()
    # A phase that did not move still follows the ones that did.
    assert "See [Phase 3](phase-3.md)" in (root / "plan/phase-1.md").read_text()
    index = (root / "plan/INDEX.md").read_text()
    assert "| [Phase 1](phase-1.md) | Done | ✅ |" in index
    assert "| [Phase 3](phase-3.md) | Build | ⬅️ |" in index
    assert "| [Phase 3.2](phase-3.2.md) | Rest | ⏳ |" in index
    assert "| [Phase 4](phase-4.md) | Ship | ⏳ |" in index
    assert "P1[Phase 1<br/>Done] --> P3[Phase 3<br/>Build]" in index
    assert "P3 --> P3_2[Phase 3.2<br/>Rest]" in index and "P3 --> P4[Phase 4<br/>Ship]" in index
    # A dated note keeps its wording; only its link follows the renamed file.
    assert "Work found in Phase 2 was deferred to [Phase 3](phase-4.md)." in index
    assert "**Insertion / renumbering record, 2026-10-07.**" in index
    assert "2 → 3, 2.1 → 3.1, 2.2 → 3.2, 3 → 4" in index
    assert "'Phase 3' means the phase now numbered 4" in index and "Review first." in index
    assert index.index("renumbering record") < index.index("## Cross-Cutting Concerns")
    # Prose that names an old number is reported, not rewritten.
    assert "plan/INDEX.md:" in result.stdout and "plan/phase-4.md:" in result.stdout
    assert "Phase 2 -> Phase 3" in result.stdout


def test_inserting_a_sub_phase_moves_only_its_later_siblings(tmp_path: Path) -> None:
    root = plan(tmp_path)
    assert run(root, "insert-before", "2.2", "--date", "2026-10-07").returncode == 0
    names = sorted(path.name for path in (root / "plan").glob("phase-*.md"))
    assert names == ["phase-1.md", "phase-2.1.md", "phase-2.3.md", "phase-2.md", "phase-3.md"]
    assert 'depends_on: ["2", "2.3"]' in (root / "plan/phase-3.md").read_text()
    index = (root / "plan/INDEX.md").read_text()
    assert "| [Phase 2.3](phase-2.3.md) | Rest | ⏳ |" in index
    assert "| [Phase 3](phase-3.md) | Ship | ⏳ |" in index
    assert "P2 --> P2_3[Phase 2.3<br/>Rest]" in index


def test_a_started_phase_is_never_renumbered_and_a_refusal_writes_nothing(tmp_path: Path) -> None:
    root = plan(tmp_path)
    before = snapshot(root)
    refused = run(root, "insert-before", "1")
    assert refused.returncode == 1 and "Phase 1 is ✅" in refused.stderr
    assert "only phases that have not started are renumbered" in refused.stderr
    absent = run(root, "insert-before", "9")
    assert absent.returncode == 1 and "no phase is numbered 9" in absent.stderr
    # An in-progress child blocks moving its not-started parent.
    index = root / "plan/INDEX.md"
    index.write_text(index.read_text().replace("| Part | ⏳ |", "| Part | 🚧 |"))
    before["INDEX.md"] = index.read_bytes()
    child = run(root, "insert-before", "2")
    assert child.returncode == 1 and "Phase 2.1 is 🚧" in child.stderr
    assert snapshot(root) == before
