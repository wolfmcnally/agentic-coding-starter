"""Behavioral tests for the lessons ledger tool (policies/lessons.md)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LESSONS = ROOT / "bin" / "lessons"

VALID_OPEN = """\
---
slug: {slug}
title: {title}
status: candidate
scope: {scope}
proposed_surface: policy
filed: 2026-08-01
source: kickoff
occurrences:
{occurrences}
---

Body of the lesson.
"""

VALID_ARCHIVED = """\
---
slug: silver-heron
title: An archived lesson
status: codified
scope: methodology
proposed_surface: policy
filed: 2026-07-01
source: sweep
occurrences:
  - date: 2026-07-01
    ref: "Phase 2 END"
closed: 2026-07-20
graduated_to: policies/example.md
---

Body.
"""


def occurrence_lines(count: int) -> str:
    return "\n".join(
        f'  - date: 2026-08-{index + 1:02d}\n    ref: "Phase {index + 1} END"'
        for index in range(count)
    )


def write_open_lesson(
    root: Path,
    slug: str = "amber-finch",
    *,
    scope: str = "methodology",
    occurrences: int = 1,
) -> Path:
    path = root / "lessons" / f"{slug}.md"
    path.write_text(
        VALID_OPEN.format(
            slug=slug,
            title=f"Lesson {slug}",
            scope=scope,
            occurrences=occurrence_lines(occurrences),
        )
    )
    return path


def run(*arguments: str, root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(LESSONS), "--root", str(root), *arguments],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


@pytest.fixture
def ledger(tmp_path: Path) -> Path:
    for name in ("lessons", "lessons-archived"):
        (tmp_path / name).mkdir()
        (tmp_path / name / ".gitkeep").write_text("")
    return tmp_path


def test_valid_open_and_archived_lessons_pass(ledger: Path) -> None:
    write_open_lesson(ledger)
    (ledger / "lessons-archived" / "silver-heron.md").write_text(VALID_ARCHIVED)

    result = run("validate", root=ledger)

    assert result.returncode == 0, result.stderr


def test_codified_lesson_requires_graduated_to(ledger: Path) -> None:
    text = VALID_ARCHIVED.replace("graduated_to: policies/example.md\n", "")
    (ledger / "lessons-archived" / "silver-heron.md").write_text(text)

    result = run("validate", root=ledger)

    assert result.returncode == 1
    assert "codified lesson missing graduated_to" in result.stderr


def test_candidates_applies_graduation_threshold_to_open_lessons_only(
    ledger: Path,
) -> None:
    write_open_lesson(ledger, "amber-finch", occurrences=3)
    write_open_lesson(ledger, "copper-vole", occurrences=2)
    (ledger / "lessons-archived" / "silver-heron.md").write_text(VALID_ARCHIVED)

    result = run("candidates", root=ledger)

    assert result.returncode == 0, result.stderr
    assert [line.split("\t")[0] for line in result.stdout.splitlines()] == ["amber-finch"]
