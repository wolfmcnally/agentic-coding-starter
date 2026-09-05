"""Behavioral tests for deterministic catalog fitness enforcement."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "bin" / "check-catalogs"

RESOURCES = (
    "preflight.md",
    "dispatch.md",
    "planning.md",
    "implementation.md",
    "acceptance.md",
    "close.md",
    "recovery.md",
)
ZONE_MARKERS = (
    "<!-- PROJECT_CONTEXT_START -->\n"
    "<!-- PROJECT_CONTEXT_END -->\n"
    "<!-- METHODOLOGY_CONTRACT_START -->\n"
    "<!-- METHODOLOGY_CONTRACT_END -->\n"
)


def write_instruction_resources(root: Path) -> None:
    """Independently construct the declared table, without copying the checker."""
    skill = root / ".claude/skills/kickoff"
    skill.mkdir(parents=True, exist_ok=True)
    (skill / "SKILL.md").write_text(
        "# Kickoff\n\n"
        "| Execution condition | Direct resource | Load requirement |\n"
        "|---|---|---|\n"
        + "".join(
            f"| Enter {name.removesuffix('.md')} | [{name}]({name}) | Read before this stage. |\n"
            for name in RESOURCES
        ),
        encoding="utf-8",
    )
    for name in RESOURCES:
        (skill / name).write_text(f"# {name}\n\n[Entry](SKILL.md)\n", encoding="utf-8")


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
        "- [`design.md`](briefs/design.md) — a design brief.\n" + ZONE_MARKERS,
        encoding="utf-8",
    )
    write_instruction_resources(root)
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
    _assert_instruction_delivery(root)
    _assert_phase_entry_ledgers(root)
    _assert_child_close_requires_parent_close_or_another_drafted_child(tmp_path / "stranded-child")
    _assert_child_close_accepts_parent_close(tmp_path / "closed-parent")
    _assert_child_close_accepts_drafted_incomplete_sibling(tmp_path / "queued-sibling")


def _assert_instruction_delivery(root: Path) -> None:
    instructions = root / "CLAUDE.md"
    entry = root / ".claude/skills/kickoff/SKILL.md"
    for path, ceiling in ((instructions, 16384), (entry, 8192)):
        original = path.read_bytes()
        # Include multibyte prose and CRLF: the budget counts stored UTF-8 bytes.
        padding = ceiling - len(original) - len("\r\né".encode())
        boundary = original + "\r\né".encode() + b"x" * padding
        try:
            path.write_bytes(boundary)
            accepted = run(root)
            assert accepted.returncode == 0, accepted.stdout + accepted.stderr
            path.write_bytes(boundary + b"x")
            refused = run(root)
            assert refused.returncode == 1
            assert f"UTF-8 size {ceiling + 1} exceeds {ceiling} bytes" in refused.stdout
        finally:
            path.write_bytes(original)

    original_root = instructions.read_text()
    markers = ZONE_MARKERS.splitlines()
    for changed, diagnostic in (
        (original_root.replace(markers[0], "PROJECT_CONTEXT_START"), "exactly once"),
        (original_root + markers[0], "exactly once"),
        (
            original_root.replace(ZONE_MARKERS, "\n".join(reversed(markers)) + "\n"),
            "declared order",
        ),
    ):
        try:
            instructions.write_text(changed)
            result = run(root)
            assert result.returncode == 1
            assert "instructions\tCLAUDE.md\tzone markers must" in result.stdout
            assert diagnostic in result.stdout
        finally:
            instructions.write_text(original_root)

    original_entry = entry.read_text()
    first_row = next(line for line in original_entry.splitlines() if "](preflight.md)" in line)
    for malformed in (
        "<!--\n" + original_entry + "-->\n",
        original_entry.replace("Execution condition", "Unrelated condition"),
        original_entry.replace("|---|---|---|", "|---|---|"),
        original_entry.replace(first_row, first_row + "\n" + first_row),
        original_entry.replace("Enter preflight", ""),
        original_entry.replace("[preflight.md](preflight.md)", "[preflight.md][resource]")
        + "\n[resource]: preflight.md\n",
    ):
        try:
            entry.write_text(malformed)
            result = run(root)
            assert result.returncode == 1
            assert "preflight.md: expected one operative row" in result.stdout
        finally:
            entry.write_text(original_entry)
    for name in RESOURCES:
        resource = entry.parent / name
        body = resource.read_bytes()
        try:
            resource.unlink()
            missing = run(root)
            assert missing.returncode == 1
            assert f"kickoff/{name}\trequired resource is unreadable" in missing.stdout
            resource.mkdir()
            try:
                not_a_file = run(root)
                assert not_a_file.returncode == 1
                assert f"kickoff/{name}\trequired resource is unreadable" in not_a_file.stdout
            finally:
                resource.rmdir()
            resource.write_bytes(b"\xff")
            unreadable = run(root)
            assert unreadable.returncode == 1
            assert f"kickoff/{name}\trequired resource is unreadable" in unreadable.stdout
        finally:
            resource.write_bytes(body)

        row = next(line for line in original_entry.splitlines() if f"]({name})" in line)
        absent = original_entry.replace(row + "\n", "")
        # Other resources retain their loading phrases in every wrong control.
        replacements = (
            "",
            "> " + row + "\n",
            "```markdown\n" + row + "\n```\n",
            "`" + row + "`\n",
            f"[Navigation]({name})\nRead before this stage.\n",
            row.replace(f"]({name})", "](indirect.md)") + "\n",
            row.replace(f"]({name})", "](missing.md)") + "\n",
        )
        indirect = entry.parent / "indirect.md"
        indirect.write_text(f"[Resource]({name})\n")
        try:
            for replacement in replacements:
                entry.write_text(absent + replacement)
                result = run(root)
                assert result.returncode == 1
                assert f"{name}: expected one operative row" in result.stdout
            for requirement in (
                "",
                "Do not read before this stage.",
                "Read after this stage.",
                "`Read before this stage.`",
                '"Read before this stage."',
            ):
                entry.write_text(
                    original_entry.replace(row, row.replace("Read before this stage.", requirement))
                )
                result = run(root)
                assert result.returncode == 1
                assert f"{name}: row must declare Read before use" in result.stdout
        finally:
            entry.write_text(original_entry)
            indirect.unlink()

    try:
        entry.unlink()
        result = run(root)
        assert result.returncode == 1
        assert "kickoff/SKILL.md\trequired entry is unreadable" in result.stdout
    finally:
        entry.write_text(original_entry)
    try:
        instructions.unlink()
        result = run(root)
        assert result.returncode == 1
        assert "instructions\tCLAUDE.md\t" in result.stdout
    finally:
        instructions.write_text(original_root)
    restored = run(root)
    assert restored.returncode == 0, restored.stdout + restored.stderr


def _assert_phase_entry_ledgers(root: Path) -> None:
    index = root / "plan/INDEX.md"
    original = index.read_bytes()
    try:
        for first, second, diagnostic in (
            ("⬅️", "⏳", None),  # Coherent major work needs no child files.
            ("🚧", "⏳", None),  # Valid active ledger; selection remains explicit.
            ("✅", "✅", None),
            ("⏳", "⏳", "idle incomplete phase table"),
            ("⬅️", "⬅️", "may carry at most one"),
            ("🚧 ✅", "⏳", "exactly one status marker"),
            ("", "⬅️", "exactly one status marker"),
        ):
            index.write_text(INDEX.format(first=first, second=second))
            result = run(root, "--closing-phase", "1")
            if diagnostic is None:
                assert result.returncode == 0, result.stdout + result.stderr
            else:
                assert result.returncode == 1
                assert diagnostic in result.stdout
    finally:
        index.write_bytes(original)


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
