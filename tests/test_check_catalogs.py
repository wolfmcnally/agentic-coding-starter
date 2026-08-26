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


def test_tracked_markdown_deleted_from_worktree_is_not_read_as_a_source(
    tmp_path: Path,
) -> None:
    root = fixture(tmp_path)
    obsolete = write_tracked(root, "docs/obsolete.md", "# Obsolete\n")
    obsolete.unlink()

    result = run(root)

    assert result.returncode == 0, result.stdout + result.stderr


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
    write_tracked(root, "docs/guide.md", "# Guide\n\n## Usage\n")
    write_tracked(
        root,
        "README.md",
        """\
# Readme

## Local

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


def test_link_quoted_in_an_inline_code_span_is_exempt(tmp_path: Path) -> None:
    """A backtick-quoted link is a quoted edit target, not a live link.

    Quoting the exact sentence another file should contain is the ordinary way
    a plan specifies an edit; resolving that quotation from the quoting file's
    directory forced precise quotes to be degraded into prose.
    """
    root = fixture(tmp_path)
    write_tracked(root, "docs/guide.md", "# Guide\n")
    write_tracked(
        root,
        "README.md",
        "Add the line `- [`x.md`](briefs/x.md) — an x brief.` to that catalog.\n"
        "Quoted `[missing](docs/absent.md)` plus a real [guide](docs/guide.md).\n"
        "A double-backtick span: ``[also quoted](docs/also-absent.md)``.\n",
    )

    result = run(root)

    assert result.returncode == 0, result.stdout + result.stderr


def test_real_missing_link_beside_a_code_span_is_still_reported(tmp_path: Path) -> None:
    root = fixture(tmp_path)
    write_tracked(
        root,
        "README.md",
        "Quoted `[fine](docs/absent.md)` but [broken](docs/broken.md) is live.\n",
    )

    result = run(root)

    assert result.returncode == 1
    assert "links\tREADME.md\tline 1: missing target docs/broken.md" in result.stdout
    assert "docs/absent.md" not in result.stdout


def test_missing_cross_file_anchor_is_reported(tmp_path: Path) -> None:
    """A link can resolve to a real file and still land nowhere.

    Validating only the path half of a compound reference reports on the half
    it checked in language that sounds like it covered the whole thing.
    """
    root = fixture(tmp_path)
    write_tracked(root, "docs/guide.md", "# Guide\n\n## Usage\n")
    write_tracked(root, "README.md", "[renamed section](docs/guide.md#getting-started)\n")

    result = run(root)

    assert result.returncode == 1
    assert "links\tREADME.md\tline 1: missing anchor #getting-started in docs/guide.md" in (
        result.stdout
    )


def test_missing_same_document_anchor_is_reported(tmp_path: Path) -> None:
    root = fixture(tmp_path)
    write_tracked(root, "README.md", "# Readme\n\n## Usage\n\n[jump](#instalation)\n")

    result = run(root)

    assert result.returncode == 1
    assert "links\tREADME.md\tline 5: missing anchor #instalation in README.md" in result.stdout


def test_anchor_slugs_survive_markup_punctuation_and_repetition(tmp_path: Path) -> None:
    """Anchors come from rendered heading text, not the raw source line."""
    root = fixture(tmp_path)
    write_tracked(
        root,
        "docs/guide.md",
        "# Guide\n\n"
        "## The `kickoff` skill — what it does\n\n"
        '## "Authorization stands for the scope specified"\n\n'
        "## Notes\n\n"
        "## Notes\n\n"
        "## A [linked](https://example.com) heading\n",
    )
    write_tracked(
        root,
        "README.md",
        "[a](docs/guide.md#the-kickoff-skill--what-it-does)\n"
        "[b](docs/guide.md#authorization-stands-for-the-scope-specified)\n"
        "[c](docs/guide.md#notes)\n"
        "[d](docs/guide.md#notes-1)\n"
        "[e](docs/guide.md#a-linked-heading)\n",
    )

    result = run(root)

    assert result.returncode == 0, result.stdout + result.stderr


def test_headings_inside_a_fenced_block_do_not_define_anchors(tmp_path: Path) -> None:
    root = fixture(tmp_path)
    write_tracked(root, "docs/guide.md", "# Guide\n\n```markdown\n## Quoted\n```\n")
    write_tracked(root, "README.md", "[quoted](docs/guide.md#quoted)\n")

    result = run(root)

    assert result.returncode == 1
    assert "links\tREADME.md\tline 1: missing anchor #quoted in docs/guide.md" in result.stdout


def test_fragment_into_a_non_markdown_target_is_skipped(tmp_path: Path) -> None:
    """A declared blind spot: only Markdown has a derivable anchor set."""
    root = fixture(tmp_path)
    write_tracked(root, "bin/tool.py", "print('hello')\n")
    write_tracked(root, "README.md", "[a line](bin/tool.py#L1)\n")

    result = run(root)

    assert result.returncode == 0, result.stdout + result.stderr


def test_brief_citing_a_policy_or_a_plan_file_is_reported(tmp_path: Path) -> None:
    """A brief never cites a policy or a plan file.

    The thinking predates the rule derived from it; inverting the citation
    direction means neither document can be read on its own.
    """
    root = fixture(tmp_path)
    write_tracked(
        root,
        "briefs/design.md",
        "# Design\n\nPer [`example.md`](../policies/example.md).\n\n"
        "See [plan](../plan/INDEX.md).\n",
    )

    result = run(root)

    assert result.returncode == 1
    assert "citations\tbriefs/design.md\tline 3: brief cites policies/example.md" in result.stdout
    assert "citations\tbriefs/design.md\tline 5: brief cites plan/INDEX.md" in result.stdout


def test_brief_citing_a_policy_that_does_not_exist_is_still_a_direction_failure(
    tmp_path: Path,
) -> None:
    """Direction is judged before existence — a dangling cite inverts order too."""
    root = fixture(tmp_path)
    write_tracked(root, "briefs/design.md", "# Design\n\nPer [absent](../policies/absent.md).\n")

    result = run(root)

    assert result.returncode == 1
    assert "citations\tbriefs/design.md\tline 3: brief cites policies/absent.md" in result.stdout


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


def test_phase_frontmatter_status_field_is_rejected(tmp_path: Path) -> None:
    root = fixture(tmp_path)
    write_tracked(
        root,
        "plan/phase-1.md",
        "---\ntitle: First\nstatus: in progress\n---\n\n# Phase 1\n",
    )

    result = run(root)

    assert result.returncode == 1
    assert (
        "plan\tplan/phase-1.md\tline 3: frontmatter must not carry a status field" in result.stdout
    )


def test_phase_body_status_declaration_is_rejected(tmp_path: Path) -> None:
    root = fixture(tmp_path)
    write_tracked(
        root,
        "plan/phase-1.md",
        "---\ntitle: First\n---\n\n# Phase 1\n\nStatus: ✅\n\n**Status**: In Progress\n",
    )

    result = run(root)

    assert result.returncode == 1
    assert (
        "plan\tplan/phase-1.md\tline 7: status declaration outside plan/INDEX.md's phase table"
        in result.stdout
    )
    assert (
        "plan\tplan/phase-1.md\tline 9: status declaration outside plan/INDEX.md's phase table"
        in result.stdout
    )


def test_narrative_status_mentions_in_phase_files_are_fine(tmp_path: Path) -> None:
    """Only declarations create a second source of truth; prose mentions don't."""
    root = fixture(tmp_path)
    write_tracked(
        root,
        "plan/phase-1.md",
        "---\ntitle: First\n---\n\n# Phase 1\n\n"
        "When this phase closes, `kickoff` flips 🚧 → ✅ in the index.\n"
        "The quoted form `status: ✅` is how the defect looked in the wild.\n"
        "```\nstatus: in progress\n```\n",
    )

    result = run(root)

    assert result.returncode == 0, result.stdout + result.stderr
