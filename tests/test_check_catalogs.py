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
    obsolete = write_tracked(root, "notes/obsolete.md", "# Obsolete\n")
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
        "[inline](notes/missing.md)\n\n[reference]: policies/absent.md\n",
    )

    result = run(root)

    assert result.returncode == 1
    assert "links\tREADME.md\tline 1: missing target notes/missing.md" in result.stdout
    assert "links\tREADME.md\tline 3: missing target policies/absent.md" in result.stdout
    _assert_a_docs_catalog_row_linking_a_missing_file_is_reported(tmp_path / "docs-missing")
    _assert_every_pinned_document_is_linked_from_the_docs_catalog(tmp_path / "docs-catalog")


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
    _assert_briefs_and_policies_may_cite_a_pinned_document(tmp_path / "cite-docs")
    _assert_a_pinned_document_never_links_outside_docs(tmp_path / "docs-outbound")


DOCS_CATALOG_HEADER = (
    "# docs\n\n| Document | Source | As of | Retrieved | Basis | Pinned for |\n"
    "|---|---|---|---|---|---|\n"
)


def _assert_every_pinned_document_is_linked_from_the_docs_catalog(tmp_path: Path) -> None:
    root = fixture(tmp_path)
    write_tracked(root, "docs/vendor-spec-v2.md", "# Vendor spec v2\n")
    write_tracked(root, "docs/rfc-0000/index.txt", "RFC 0000\n")

    missing_catalog = run(root)

    assert missing_catalog.returncode == 1
    assert (
        "docs\tdocs/README.md\tcatalog is missing while docs/ holds 2 entries"
        in missing_catalog.stdout
    )

    write_tracked(
        root,
        "docs/README.md",
        DOCS_CATALOG_HEADER
        + "| [`vendor-spec-v2.md`](vendor-spec-v2.md) | https://example.invalid/spec"
        " | v2 | 2026-01-01 | CC BY 4.0 | briefs/design.md |\n",
    )

    orphan = run(root)

    assert orphan.returncode == 1
    assert "docs\tdocs/rfc-0000\tentry is not linked from any docs/README.md catalog row" in (
        orphan.stdout
    )
    assert "vendor-spec-v2.md" not in orphan.stdout

    write_tracked(
        root,
        "docs/README.md",
        DOCS_CATALOG_HEADER
        + "| [`vendor-spec-v2.md`](vendor-spec-v2.md) | https://example.invalid/spec"
        " | v2 | 2026-01-01 | CC BY 4.0 | briefs/design.md |\n"
        "| [`rfc-0000/`](rfc-0000/index.txt) | https://example.invalid/rfc"
        " | 2020-01-01 | 2026-01-01 | public standard | excerpt; policies/example.md |\n",
    )

    complete = run(root)

    assert complete.returncode == 0, complete.stdout + complete.stderr


def _assert_a_docs_catalog_row_linking_a_missing_file_is_reported(tmp_path: Path) -> None:
    root = fixture(tmp_path)
    write_tracked(
        root,
        "docs/README.md",
        DOCS_CATALOG_HEADER
        + "| [`gone.md`](gone.md) | https://example.invalid | - | 2026-01-01 | MIT | - |\n",
    )

    result = run(root)

    assert result.returncode == 1
    assert "links\tdocs/README.md\tline 5: missing target docs/gone.md" in result.stdout


def _assert_a_pinned_document_never_links_outside_docs(tmp_path: Path) -> None:
    root = fixture(tmp_path)
    write_tracked(
        root,
        "docs/README.md",
        DOCS_CATALOG_HEADER
        + "| [`vendor-spec-v2.md`](vendor-spec-v2.md) | https://example.invalid/spec"
        " | v2 | 2026-01-01 | CC BY 4.0 | briefs/design.md |\n"
        "\nGoverned by [`policies/example.md`](../policies/example.md).\n",
    )
    write_tracked(
        root,
        "docs/vendor-spec-v2.md",
        "# Vendor spec v2\n\n"
        "See [the design](../briefs/design.md) and [section](#vendor-spec-v2).\n",
    )

    result = run(root)

    assert result.returncode == 1
    assert (
        "docs\tdocs/vendor-spec-v2.md\tline 3: pinned document links outside docs/ "
        "(../briefs/design.md); third-party material never references the project"
    ) in result.stdout
    assert "docs/README.md" not in result.stdout


def _assert_briefs_and_policies_may_cite_a_pinned_document(tmp_path: Path) -> None:
    root = fixture(tmp_path)
    write_tracked(
        root,
        "docs/README.md",
        DOCS_CATALOG_HEADER
        + "| [`vendor-spec-v2.md`](vendor-spec-v2.md) | https://example.invalid/spec"
        " | v2 | 2026-01-01 | CC BY 4.0 | briefs/design.md |\n",
    )
    write_tracked(root, "docs/vendor-spec-v2.md", "# Vendor spec v2\n\n## Limits\n")
    write_tracked(
        root,
        "briefs/design.md",
        "# Design\n\nPer [the spec](../docs/vendor-spec-v2.md#limits).\n",
    )
    write_tracked(
        root,
        "policies/example.md",
        "# Policy: Example\n\nBound by [the spec](../docs/vendor-spec-v2.md).\n",
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
