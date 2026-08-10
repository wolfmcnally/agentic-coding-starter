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


def test_empty_ledger_validates_clean(ledger: Path) -> None:
    result = run("validate", root=ledger)

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "LESSONS OK"


def test_missing_directory_fails_closed(tmp_path: Path) -> None:
    (tmp_path / "lessons").mkdir()

    result = run("validate", root=tmp_path)

    assert result.returncode == 1
    assert "missing directory: lessons-archived/" in result.stderr


def test_valid_open_and_archived_lessons_pass(ledger: Path) -> None:
    write_open_lesson(ledger)
    (ledger / "lessons-archived" / "silver-heron.md").write_text(VALID_ARCHIVED)

    result = run("validate", root=ledger)

    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("status: codified", "status 'codified' invalid here"),
        ("scope: global", "scope must be one of"),
        ("proposed_surface: vibes", "proposed_surface must be one of"),
        ("source: rumor", "source must be one of"),
        ("filed: yesterday", "filed is not an ISO date"),
    ],
)
def test_invalid_enum_values_are_rejected(ledger: Path, mutation: str, message: str) -> None:
    path = write_open_lesson(ledger)
    original_line = {
        "status": "status: candidate",
        "scope": "scope: methodology",
        "proposed_surface": "proposed_surface: policy",
        "source": "source: kickoff",
        "filed": "filed: 2026-08-01",
    }[mutation.split(":")[0]]
    path.write_text(path.read_text().replace(original_line, mutation))

    result = run("validate", root=ledger)

    assert result.returncode == 1
    assert message in result.stderr


def test_unknown_and_missing_keys_are_rejected(ledger: Path) -> None:
    path = write_open_lesson(ledger)
    text = path.read_text()
    path.write_text(text.replace("source: kickoff", "source: kickoff\npriority: high"))
    unknown = run("validate", root=ledger)
    path.write_text(text.replace("source: kickoff\n", ""))
    missing = run("validate", root=ledger)

    assert unknown.returncode == 1
    assert "unknown frontmatter keys: ['priority']" in unknown.stderr
    assert missing.returncode == 1
    assert "missing frontmatter keys: ['source']" in missing.stderr


def test_slug_must_match_filename_and_shape(ledger: Path) -> None:
    path = write_open_lesson(ledger)
    renamed = path.with_name("other-name.md")
    path.rename(renamed)
    mismatched = run("validate", root=ledger)
    renamed.rename(ledger / "lessons" / "notaslug.md")
    malformed = run("validate", root=ledger)

    assert mismatched.returncode == 1
    assert "does not match filename" in mismatched.stderr
    assert malformed.returncode == 1
    assert "filename must be a two-word slug" in malformed.stderr


def test_slug_collision_across_directories_is_rejected(ledger: Path) -> None:
    write_open_lesson(ledger, "silver-heron")
    (ledger / "lessons-archived" / "silver-heron.md").write_text(VALID_ARCHIVED)

    result = run("validate", root=ledger)

    assert result.returncode == 1
    assert "slug collides with" in result.stderr


def test_open_lesson_must_not_carry_closure_keys(ledger: Path) -> None:
    path = write_open_lesson(ledger)
    path.write_text(
        path.read_text().replace("source: kickoff", "source: kickoff\nclosed: 2026-08-05")
    )

    result = run("validate", root=ledger)

    assert result.returncode == 1
    assert "open lesson must not carry closed" in result.stderr


def test_codified_lesson_requires_graduated_to(ledger: Path) -> None:
    text = VALID_ARCHIVED.replace("graduated_to: policies/example.md\n", "")
    (ledger / "lessons-archived" / "silver-heron.md").write_text(text)

    result = run("validate", root=ledger)

    assert result.returncode == 1
    assert "codified lesson missing graduated_to" in result.stderr


def test_malformed_occurrences_are_rejected(ledger: Path) -> None:
    path = write_open_lesson(ledger)
    path.write_text(path.read_text().replace('    ref: "Phase 1 END"\n', ""))

    result = run("validate", root=ledger)

    assert result.returncode == 1
    assert "occurrence 1 must be a mapping with exactly" in result.stderr


def test_list_filters_by_scope_and_status(ledger: Path) -> None:
    write_open_lesson(ledger, "amber-finch", scope="methodology")
    write_open_lesson(ledger, "copper-vole", scope="local")
    (ledger / "lessons-archived" / "silver-heron.md").write_text(VALID_ARCHIVED)

    everything = run("list", root=ledger)
    methodology = run("list", "--scope", "methodology", root=ledger)
    codified = run("list", "--status", "codified", root=ledger)

    assert everything.returncode == 0
    assert [line.split("\t")[0] for line in everything.stdout.splitlines()] == [
        "amber-finch",
        "copper-vole",
        "silver-heron",
    ]
    assert [line.split("\t")[0] for line in methodology.stdout.splitlines()] == [
        "amber-finch",
        "silver-heron",
    ]
    assert [line.split("\t")[0] for line in codified.stdout.splitlines()] == ["silver-heron"]


def test_candidates_applies_graduation_threshold_to_open_lessons_only(ledger: Path) -> None:
    write_open_lesson(ledger, "amber-finch", occurrences=3)
    write_open_lesson(ledger, "copper-vole", occurrences=2)
    (ledger / "lessons-archived" / "silver-heron.md").write_text(VALID_ARCHIVED)

    result = run("candidates", root=ledger)

    assert result.returncode == 0, result.stderr
    assert [line.split("\t")[0] for line in result.stdout.splitlines()] == ["amber-finch"]


def test_queries_fail_closed_on_invalid_ledger(ledger: Path) -> None:
    path = write_open_lesson(ledger)
    path.write_text(path.read_text().replace("status: candidate", "status: nonsense"))

    listing = run("list", root=ledger)
    candidates = run("candidates", root=ledger)

    assert listing.returncode == 1
    assert candidates.returncode == 1
    assert listing.stdout == ""


def test_repo_ledger_validates_clean() -> None:
    result = run("validate", root=ROOT)

    assert result.returncode == 0, result.stderr
