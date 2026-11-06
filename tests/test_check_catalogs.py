"""Behavioral tests for deterministic catalog fitness enforcement."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from structured_fixtures import completion, create_records, install_record_tools

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
    (root / "AGENTS.md").write_text(
        "# Instructions\n\n"
        "- [`example.md`](policies/example.md) — an example policy.\n"
        "- [`design.md`](briefs/design.md) — a design brief.\n" + ZONE_MARKERS,
        encoding="utf-8",
    )
    write_instruction_resources(root)
    install_record_tools(root)
    create_records(
        root,
        {
            "first-work-package": {"state": "next", "owner": "fixture-operator"},
            "second-work-package": {},
        },
    )
    (root / "plan/INDEX.md").write_text("# Plan context\n")
    (root / ".gitignore").write_text(".kickoff/\n__pycache__/\n.collaboration-views/\n")
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

    assert result.returncode == 0, (
        "CATALOG LOST PRIMARY CONSTITUTION: " + result.stdout + result.stderr
    )
    _assert_instruction_delivery(root)
    # The writer owns syntax and catalog placement; content and zone remain explicit.
    instructions = root / "AGENTS.md"
    instructions.write_text(
        instructions.read_text().replace(
            "<!-- METHODOLOGY_CONTRACT_START -->",
            "<!-- METHODOLOGY_CONTRACT_START -->\n## Methodology briefs\n",
        )
    )
    supplied = root / "document-input.json"
    supplied.write_text(
        json.dumps(
            {
                "path": "briefs/created.md",
                "title": "Created brief",
                "body": "Actual design.\n",
                "status": "draft",
                "scope": "A bounded design.",
            }
        )
    )
    command = [str(CHECKER), "--root", str(root)]
    written = subprocess.run(
        command + ["--create-input", str(supplied)], capture_output=True, text=True
    )
    document = root / "briefs/created.md"
    assert written.returncode == 0 and "status: draft" in document.read_text(), (
        "DOCUMENT SKELETON AUTHORING FAILED: " + written.stderr
    )
    before = document.read_bytes()
    escaped = root / "project/example.md"
    supplied.write_text(
        json.dumps(
            {
                "path": "docs/../project/example.md",
                "title": "Not docs",
                "body": "Outside the owning subtree.",
            }
        )
    )
    traversal = subprocess.run(
        command + ["--create-input", str(supplied)], capture_output=True, text=True
    )
    assert traversal.returncode != 0 and not escaped.exists(), (
        "DOCUMENT DESTINATION ESCAPED SUBTREE"
    )
    supplied.write_text(
        json.dumps(
            {
                "path": "briefs/created.md",
                "title": "Created brief",
                "body": "Actual design.\n",
                "status": "draft",
                "scope": "A bounded design.",
            }
        )
    )
    collision = subprocess.run(
        command + ["--create-input", str(supplied)], capture_output=True, text=True
    )
    assert collision.returncode != 0 and document.read_bytes() == before, (
        "DOCUMENT COLLISION OVERWROTE ORIGINAL"
    )
    supplied.write_text(
        json.dumps({"path": "briefs/created.md", "label": "Created", "zone": "methodology"})
    )
    original = instructions.read_bytes()
    registered = subprocess.run(
        command
        + [
            "--register-input",
            str(supplied),
            "--expect-sha256",
            hashlib.sha256(original).hexdigest(),
        ],
        capture_output=True,
        text=True,
    )
    assert (
        registered.returncode == 0 and "[Created](briefs/created.md)" in instructions.read_text()
    ), "CATALOG REGISTRATION FAILED: " + registered.stderr
    current = instructions.read_bytes()
    refused = subprocess.run(
        command + ["--register-input", str(supplied), "--expect-sha256", "0" * 64],
        capture_output=True,
        text=True,
    )
    assert refused.returncode != 0 and instructions.read_bytes() == current, (
        "CATALOG REFUSAL MUTATED CONSTITUTION"
    )


def _assert_instruction_delivery(root: Path) -> None:
    instructions = root / "AGENTS.md"
    entry = root / ".claude/skills/kickoff/SKILL.md"
    for path, ceiling in ((instructions, 20480), (entry, 10240)):
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
            assert "instructions\tAGENTS.md\tzone markers must" in result.stdout
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
        assert "instructions\tAGENTS.md\t" in result.stdout
    finally:
        instructions.write_text(original_root)
    restored = run(root)
    assert restored.returncode == 0, restored.stdout + restored.stderr


def test_structured_phase_order_and_events_are_checked_by_the_catalog(tmp_path: Path) -> None:
    root = fixture(tmp_path)
    second = root / "plan/phases/second-work-package.md"
    original = second.read_bytes()
    for before, after, diagnostic in (
        (b"depends_on: []", b"depends_on: [missing-work-package]", "unknown dependency"),
        (b"order: '2'", b"order: 'bad'", "invalid rational order"),
    ):
        assert before in original
        second.write_bytes(original.replace(before, after))
        refused = run(root)
        assert refused.returncode == 1 and diagnostic in refused.stdout, (
            "PHASE CATALOG ADMITTED " + diagnostic
        )
        second.write_bytes(original)
    assert run(root).returncode == 0
    event = next((root / "plan/events").glob("*.json"))
    row = json.loads(event.read_text())
    fork = {**row, "id": "a" * 32}
    (event.parent / (fork["id"] + ".json")).write_text(json.dumps(fork))
    refused = run(root)
    assert refused.returncode == 1 and "competing phase heads" in refused.stdout, (
        "PHASE CATALOG ADMITTED EVENT FORK"
    )


def test_a_phase_names_other_phases_by_id_and_a_path_is_refused(tmp_path: Path) -> None:
    root = fixture(tmp_path)
    path = root / "plan/phases/second-work-package.md"
    original = path.read_text()
    for key in ("depends_on", "informs"):
        path.write_text(
            original.replace(key + ": []", key + ": [plan/phases/first-work-package.md]")
        )
        refused = run(root)
        assert (
            refused.returncode == 1
            and ("unknown dependency" if key == "depends_on" else "unknown informed phase")
            in refused.stdout
        ), "PHASE CATALOG ADMITTED PATH AS " + key
    path.write_text(original.replace("depends_on: []", "depends_on: [first-work-package]"))
    assert run(root).returncode == 0


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
    # The one operator-directed research-to-runbook handoff is navigation only.
    write_tracked(root, "policies/multi-operator-migration.md", "# Migration runbook\n")
    brief = write_tracked(
        root,
        "briefs/multi-operator-collaboration.md",
        "# Research\n[Runbook](../policies/multi-operator-migration.md)\n",
    )
    instruction = root / "AGENTS.md"
    write_tracked(
        root,
        "AGENTS.md",
        instruction.read_text()
        + "\n[Migration](policies/multi-operator-migration.md)\n"
        + "[Research](briefs/multi-operator-collaboration.md)\n",
    )
    handed_off = run(root)
    assert handed_off.returncode == 0, "RUNBOOK HANDOFF REFUSED: " + handed_off.stdout
    brief.write_text("# Research\n[Other](../policies/example.md)\n")
    wrong_target = run(root)
    assert wrong_target.returncode == 1 and "citations" in wrong_target.stdout, (
        "RUNBOOK HANDOFF ALLOWED WRONG TARGET"
    )
    brief.write_text("# Research\n[Runbook](../policies/multi-operator-migration.md)\n")
    write_tracked(
        root,
        "briefs/design.md",
        "# Design\n[Other source](../policies/multi-operator-migration.md)\n",
    )
    wrong_source = run(root)
    assert wrong_source.returncode == 1 and "citations" in wrong_source.stdout, (
        "RUNBOOK HANDOFF ALLOWED WRONG SOURCE"
    )
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


def test_prospective_child_close_requires_real_parent_disposition(tmp_path: Path) -> None:
    root = fixture(tmp_path)
    create_records(
        root,
        {
            "active-parent-package": {"state": "in-progress", "order": "3"},
            "active-child-package": {
                "state": "in-progress",
                "order": "4",
                "parent": "active-parent-package",
            },
        },
    )
    proposal = completion(root, "active-child-package")
    target = root / ".kickoff/transition.json"
    target.parent.mkdir()
    target.write_text(json.dumps(proposal))
    refused = run(root, "--closing-phase", "active-child-package", "--ledger-file", str(target))
    assert refused.returncode == 1 and "last child requires" in refused.stdout, (
        "CHILD CLOSE STRANDED ACTIVE PARENT"
    )
    proposal["parent_continuation"] = "Parent has separately scoped integration work remaining"
    target.write_text(json.dumps(proposal))
    accepted = run(root, "--closing-phase", "active-child-package", "--ledger-file", str(target))
    assert accepted.returncode == 0, (
        "CHILD CLOSE LOST EXPLICIT REMAINING WORK: " + accepted.stdout + accepted.stderr
    )
    proposal["events"][0]["claim"] = "wrong-claim"
    target.write_text(json.dumps(proposal))
    refused = run(root, "--closing-phase", "active-child-package", "--ledger-file", str(target))
    assert refused.returncode == 1 and "changed owner or claim" in refused.stdout, (
        "CHILD CLOSE CHANGED OWNER CLAIM"
    )


def test_imported_links_use_exact_git_history_without_legacy_aliases(tmp_path: Path) -> None:
    import hashlib

    root = fixture(tmp_path)
    old_log = b"# Imported history\n\n[Original constitution](CLAUDE.md#hard-rules)\n"
    (root / "CLAUDE.md").write_text("# Instructions\n\n## Hard rules\nPreserve history.\n")
    (root / "LOG.md").write_bytes(old_log)
    archive = root / "lessons-archived/retained-observation.md"
    archive.parent.mkdir()
    archive.write_text("# Historical observation\n\n[Original](../CLAUDE.md#hard-rules)\n")
    subprocess.run(["git", "config", "user.name", "Fixture"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "fixture@example.invalid"], cwd=root, check=True)
    subprocess.run(
        ["git", "add", "--", "CLAUDE.md", "LOG.md", "lessons-archived"], cwd=root, check=True
    )
    subprocess.run(
        ["git", "commit", "-q", "-m", "Retained historical fixture"], cwd=root, check=True
    )
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root).decode().strip()
    (root / "CLAUDE.md").unlink()
    (root / "LOG.md").unlink()
    manifest_path = root / "collaboration/manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest.update(
        source_commit=commit,
        original_log_bytes=len(old_log),
        original_log_sha256=hashlib.sha256(old_log).hexdigest(),
    )
    manifest_path.write_text(json.dumps(manifest))
    entry = root / "log/entries" / ("1" * 32 + ".md")
    metadata = {
        "id": "1" * 32,
        "writer": "unattributed-import",
        "sequence": 1,
        "previous": None,
        "at": "import",
        "source_offset": 0,
        "body_sha256": hashlib.sha256(old_log).hexdigest(),
    }

    def publish(body: bytes) -> None:
        metadata["body_sha256"] = hashlib.sha256(body).hexdigest()
        entry.write_bytes(b"---\n" + json.dumps(metadata).encode() + b"\n---\n" + body)

    publish(old_log)
    subprocess.run(["git", "add", "--", "log", "collaboration"], cwd=root, check=True)
    positive = run(root)
    assert positive.returncode == 0, (
        "HISTORY LOST GIT LINK RESOLUTION: " + positive.stdout + positive.stderr
    )
    assert not (root / "CLAUDE.md").exists(), "HISTORY CREATED A LIVE LEGACY ALIAS"
    for bad, diagnostic in (
        ("0" * 40, "verified repository ancestor"),
        ("not-a-commit", "invalid historical source"),
    ):
        manifest_path.write_text(json.dumps({**manifest, "source_commit": bad}))
        refused = run(root)
        assert refused.returncode == 1 and diagnostic in refused.stdout, (
            "HISTORY UNVERIFIED SOURCE ADMITTED"
        )
    manifest_path.write_text(json.dumps(manifest))
    changed = old_log.replace(b"Original constitution", b"Altered historical assertion")
    publish(changed)
    manifest_path.write_text(
        json.dumps(
            {
                **manifest,
                "original_log_bytes": len(changed),
                "original_log_sha256": hashlib.sha256(changed).hexdigest(),
            }
        )
    )
    refused = run(root)
    assert refused.returncode == 1 and "differs from the declared Git source" in refused.stdout, (
        "HISTORY MUTATED IMPORT ADMITTED"
    )
    publish(old_log)
    manifest_path.write_text(json.dumps(manifest))
    archive.write_text(archive.read_text() + "\nNew post-import prose.\n")
    refused = run(root)
    assert refused.returncode == 1 and "missing target CLAUDE.md" in refused.stdout, (
        "HISTORY EDIT RETAINED IMPORT EXEMPTION"
    )
