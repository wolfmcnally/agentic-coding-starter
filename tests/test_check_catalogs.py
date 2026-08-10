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

| Phase | Title | Status |
|-------|-------|--------|
| Phase 1 | First | {first} |
| Phase 2 | Second | {second} |

`kickoff` flips `⬅️` → `🚧` on start.
"""


def run(root: Path) -> subprocess.CompletedProcess[str]:
    checker = root / "bin" / "check-catalogs"
    return subprocess.run(
        [str(checker)],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


def fixture(tmp_path: Path) -> Path:
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
    (root / "plan" / "INDEX.md").write_text(INDEX.format(first="⬅️", second="⏳"), encoding="utf-8")
    return root


def test_clean_fixture_passes(tmp_path: Path) -> None:
    result = run(fixture(tmp_path))

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == "CATALOGS OK\n"


def test_repository_catalogs_are_in_sync() -> None:
    result = run(ROOT)

    assert result.returncode == 0, result.stdout + result.stderr


def test_uncataloged_file_is_reported(tmp_path: Path) -> None:
    root = fixture(tmp_path)
    (root / "policies" / "orphan.md").write_text("# Policy: Orphan\n", encoding="utf-8")
    (root / "briefs" / "unlisted.md").write_text("# Unlisted\n", encoding="utf-8")

    result = run(root)

    assert result.returncode == 1
    assert "policies\tpolicies/orphan.md\tfile is not indexed" in result.stdout
    assert "briefs\tbriefs/unlisted.md\tfile is not indexed" in result.stdout


def test_dangling_catalog_reference_is_reported(tmp_path: Path) -> None:
    root = fixture(tmp_path)
    (root / "policies" / "example.md").unlink()

    result = run(root)

    assert result.returncode == 1
    assert "policies\tpolicies/example.md\tCLAUDE.md references a missing file" in result.stdout


def test_next_marker_count_must_be_exactly_one(tmp_path: Path) -> None:
    root = fixture(tmp_path)
    index = root / "plan" / "INDEX.md"

    index.write_text(INDEX.format(first="⬅️", second="⬅️"), encoding="utf-8")
    doubled = run(root)
    index.write_text(INDEX.format(first="✅", second="⏳"), encoding="utf-8")
    absent = run(root)

    assert doubled.returncode == 1
    assert "found 2" in doubled.stdout
    assert absent.returncode == 1
    assert "found 0" in absent.stdout


def test_legend_and_prose_markers_are_not_counted(tmp_path: Path) -> None:
    root = fixture(tmp_path)

    result = run(root)

    assert result.returncode == 0, result.stdout + result.stderr


def test_missing_index_fails_closed(tmp_path: Path) -> None:
    root = fixture(tmp_path)
    (root / "plan" / "INDEX.md").unlink()

    result = run(root)

    assert result.returncode == 1
    assert "plan\tplan/INDEX.md" in result.stdout
