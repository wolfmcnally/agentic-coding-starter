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


def test_more_than_one_next_marker_fails(tmp_path: Path) -> None:
    result = run(fixture(tmp_path, first="⬅️", second="⬅️"))

    assert result.returncode == 1
    assert "may carry at most one ⬅️ marker; found 2" in result.stdout


def test_idle_incomplete_ledger_requires_next_marker(tmp_path: Path) -> None:
    result = run(fixture(tmp_path, first="✅", second="⏳"))

    assert result.returncode == 1
    assert "idle incomplete phase table must carry exactly one ⬅️ marker" in result.stdout


def test_active_leaf_may_temporarily_have_no_next_marker(tmp_path: Path) -> None:
    result = run(fixture(tmp_path, first="🚧", second="⏳"))

    assert result.returncode == 0, result.stdout + result.stderr


def test_completed_project_may_have_no_next_marker(tmp_path: Path) -> None:
    result = run(fixture(tmp_path, first="✅", second="✅"))

    assert result.returncode == 0, result.stdout + result.stderr


def test_decomposed_parent_and_next_child_are_valid(tmp_path: Path) -> None:
    result = run(fixture(tmp_path, first="🚧", second="⬅️"))

    assert result.returncode == 0, result.stdout + result.stderr


def test_phase_row_must_have_exactly_one_recognized_marker(tmp_path: Path) -> None:
    doubled = run(fixture(tmp_path, first="🚧 ⬅️", second="⏳"))
    missing_root = fixture(tmp_path / "missing", first="", second="⏳")
    missing = run(missing_root)

    assert doubled.returncode == 1
    assert "phase row 1 must carry exactly one status marker; found 2" in doubled.stdout
    assert missing.returncode == 1
    assert "phase row 1 must carry exactly one status marker; found 0" in missing.stdout


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


def test_missing_phase_table_fails_closed(tmp_path: Path) -> None:
    root = fixture(tmp_path)
    (root / "plan" / "INDEX.md").write_text("# Plan\n\nNo table.\n", encoding="utf-8")

    result = run(root)

    assert result.returncode == 1
    assert "phase table has no data rows" in result.stdout


def test_valid_internal_links_and_explicit_exclusions_pass(tmp_path: Path) -> None:
    root = fixture(tmp_path)
    write_tracked(root, "docs/guide.md", "# Guide\n")
    write_tracked(
        root,
        "README.md",
        """\
[guide](docs/guide.md)
[guide section](docs/guide.md#usage)
[reference][guide-ref]
[anchor](#local)
[external](https://example.com/missing.md)
[email](mailto:test@example.com)
[placeholder](<target>/guide.md)
[embedded placeholder](phase-<id>.md)

[guide-ref]: docs/guide.md

```markdown
[fenced example](docs/missing.md)
```
""",
    )

    result = run(root)

    assert result.returncode == 0, result.stdout + result.stderr


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


def test_link_that_escapes_repository_is_reported(tmp_path: Path) -> None:
    root = fixture(tmp_path)
    write_tracked(root, "README.md", "[outside](../outside.md)\n")

    result = run(root)

    assert result.returncode == 1
    assert "links\tREADME.md\tline 1: link escapes repository" in result.stdout
