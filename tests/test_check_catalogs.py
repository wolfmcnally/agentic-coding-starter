"""Behavioral tests for deterministic catalog fitness enforcement."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "bin" / "check-catalogs"

INDEX = """\
# Plan

Status legend: ⏳ Not Started · ⬅️ Next (only one at a time) · 🚧 In Progress.

## Phase Table

| Phase | Title | Status |
|-------|-------|--------|
| Phase 1 | First | {first} |
| Phase 2 | Second | {second} |

`kickoff` flips `⬅️` → `🚧` on start.
"""


def run(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    checker = root / "bin" / "check-catalogs"
    return subprocess.run(
        [str(checker), *arguments],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


def fixture(tmp_path: Path, *, first: str = "⬅️", second: str = "⏳") -> Path:
    root = tmp_path / "repo"
    (root / "bin").mkdir(parents=True)
    shutil.copy2(CHECKER, root / "bin" / "check-catalogs")
    for directory in ("policies", "briefs"):
        (root / directory).mkdir()
    (root / "policies" / "example.md").write_text("# Policy: Example\n", encoding="utf-8")
    (root / "briefs" / "design.md").write_text("# Design\n", encoding="utf-8")
    (root / "CLAUDE.md").write_text(
        "# Instructions\n\n"
        "- [`example.md`](policies/example.md) — an example policy.\n"
        "- [`design.md`](briefs/design.md) — a design brief.\n",
        encoding="utf-8",
    )
    (root / "plan").mkdir()
    (root / "plan" / "INDEX.md").write_text(
        INDEX.format(first=first, second=second),
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-q", "-b", "master", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "add", "."], check=True)
    return root


def write_tracked(root: Path, relative: str, text: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", relative], check=True)
    return path


def test_tracked_markdown_deleted_from_worktree_is_not_read_as_a_source(
    tmp_path: Path,
) -> None:
    root = fixture(tmp_path)
    obsolete = write_tracked(root, "docs/obsolete.md", "# Obsolete\n")
    obsolete.unlink()

    result = run(root)

    assert result.returncode == 0, result.stdout + result.stderr
    _assert_child_close_requires_parent_close_or_another_drafted_child(tmp_path / "stranded-child")
    _assert_child_close_accepts_parent_close(tmp_path / "closed-parent")
    _assert_child_close_accepts_drafted_incomplete_sibling(tmp_path / "queued-sibling")


def test_missing_internal_inline_and_reference_links_are_reported(
    tmp_path: Path,
) -> None:
    root = fixture(tmp_path)
    write_tracked(
        root,
        "README.md",
        "[inline](docs/missing.md)\n\n[reference]: policies/absent.md\n",
    )

    result = run(root)

    assert result.returncode == 1
    assert "links\tREADME.md\tline 1: missing target docs/missing.md" in result.stdout
    assert "links\tREADME.md\tline 3: missing target policies/absent.md" in result.stdout


def test_the_citation_rule_is_directional_not_symmetric(tmp_path: Path) -> None:
    """A policy or a plan file may cite a brief; only the upward direction is barred."""
    root = fixture(tmp_path)
    write_tracked(
        root,
        "policies/example.md",
        "# Policy: Example\n\nRationale: [`design.md`](../briefs/design.md).\n",
    )
    write_tracked(
        root,
        "briefs/design.md",
        "# Design\n\nA sibling brief: [`design.md`](design.md), and `../policies/example.md`.\n",
    )

    result = run(root)

    assert result.returncode == 0, result.stdout + result.stderr


def _assert_child_close_requires_parent_close_or_another_drafted_child(tmp_path: Path) -> None:
    root = fixture(tmp_path, first="🚧", second="⏳")
    (root / "plan" / "INDEX.md").write_text(
        INDEX.format(first="🚧", second="⏳").replace(
            "| Phase 2 | Second | ⏳ |",
            "| Phase 1.1 | Child | ✅ |\n| Phase 2 | Second | ⏳ |",
        )
    )
    result = run(root, "--closing-phase", "1.1")
    assert result.returncode == 1
    assert "must close parent Phase 1 or leave it 🚧" in result.stdout


def _assert_child_close_accepts_parent_close(tmp_path: Path) -> None:
    root = fixture(tmp_path, first="✅", second="⬅️")
    (root / "plan" / "INDEX.md").write_text(
        INDEX.format(first="✅", second="⬅️").replace(
            "| Phase 2 | Second | ⬅️ |",
            "| Phase 1.1 | Child | ✅ |\n| Phase 2 | Second | ⬅️ |",
        )
    )
    result = run(root, "--closing-phase", "1.1")
    assert result.returncode == 0, result.stdout + result.stderr


def _assert_child_close_accepts_drafted_incomplete_sibling(tmp_path: Path) -> None:
    root = fixture(tmp_path, first="🚧", second="⏳")
    (root / "plan" / "phase-1.2.md").write_text("# Phase 1.2\n")
    (root / "plan" / "INDEX.md").write_text(
        INDEX.format(first="🚧", second="⏳").replace(
            "| Phase 2 | Second | ⏳ |",
            "| Phase 1.1 | Child one | ✅ |\n"
            "| Phase 1.2 | Child two | ⬅️ |\n"
            "| Phase 2 | Second | ⏳ |",
        )
    )
    result = run(root, "--closing-phase", "1.1")
    assert result.returncode == 0, result.stdout + result.stderr
