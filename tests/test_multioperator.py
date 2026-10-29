"""The proposed migration is exercised through its actual CLI, never live adoption."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import uuid
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "bin/multioperator"


def run(*args: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(CLI), *map(str, args)],
        text=True,
        capture_output=True,
        env={**os.environ, "UV_OFFLINE": "1"},
        timeout=60,
    )


def result(command: subprocess.CompletedProcess[str]) -> None:
    assert command.returncode == 0, "MIGRATION VALID PATH REFUSED: " + command.stderr


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data))


def snapshot(root: Path) -> dict[str, bytes]:
    return {
        str(p.relative_to(root)): p.read_bytes()
        for p in root.rglob("*")
        if p.is_file()
        and not p.is_symlink()
        and not any(
            part in {".git", ".venv", "__pycache__", ".kickoff"}
            for part in p.relative_to(root).parts
        )
    }


def convert(tmp_path: Path, source: Path, phases: dict[str, str], **extra: object) -> Path:
    mapping = tmp_path / "mapping.json"
    retired = [
        "renumber-phases",
        "log-append",
        "log-relocate",
        "check-log",
        "check-log-prefix",
        "check-log-monotonic",
    ]
    recipe = {
        "bin/" + name: hashlib.sha256((source / "bin" / name).read_bytes()).hexdigest()
        for name in retired
        if (source / "bin" / name).is_file()
    }
    write_json(
        mapping,
        {
            "writer": "migration-author",
            "phases": phases,
            "retirements": recipe,
            "tool_replacements": {
                name: hashlib.sha256((source / name).read_bytes()).hexdigest()
                for name in (
                    "bin/multioperator",
                    "lib/agentic_starter/multioperator.py",
                    "lib/agentic_starter/multioperator_transition.py",
                )
                if (source / name).exists()
                and (source / name).read_bytes() != (ROOT / name).read_bytes()
            },
            **extra,
        },
    )
    output = tmp_path / "converted"
    result(run("rehearse", "--source", source, "--output", output, "--mapping", mapping))
    return output


def test_actual_starter_rehearsal_preserves_source_and_history(tmp_path: Path) -> None:
    """Use the real committed corpus, including its large historical log and symlinks."""
    source = tmp_path / "faithful-starter"
    # Old-format input comes from our Git provenance; it is not a live fallback.
    manifest = ROOT / "collaboration/manifest.json"
    commit = json.loads(manifest.read_text())["source_commit"] if manifest.exists() else "HEAD"
    archive = subprocess.check_output(["git", "archive", commit], cwd=ROOT)
    source.mkdir()
    import io
    import tarfile

    with tarfile.open(fileobj=io.BytesIO(archive)) as files:
        files.extractall(source, filter="data")
    subprocess.run(["git", "init", "-q", "-b", "master", str(source)], check=True)
    subprocess.run(
        ["git", "config", "user.email", "fixture@example.invalid"],
        cwd=source,
        check=True,
    )
    subprocess.run(["git", "config", "user.name", "Fixture"], cwd=source, check=True)
    paths = (
        subprocess.check_output(
            ["git", "ls-files", "--others", "--exclude-standard", "-z"], cwd=source
        )
        .decode()
        .split("\0")
    )
    subprocess.run(["git", "add", "--", *[p for p in paths if p]], cwd=source, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "Faithful pre-transition fixture"],
        cwd=source,
        check=True,
    )
    source_plan = snapshot(source / "plan")
    live_log = (source / "LOG.md").read_bytes()
    status = subprocess.check_output(["git", "status", "--porcelain"], cwd=source)
    original = subprocess.check_output(["git", "show", commit + ":LOG.md"], cwd=ROOT)
    output = convert(tmp_path, source, {"1": "starter-template-adoption"})
    wrong_recipe = json.loads((tmp_path / "mapping.json").read_text())
    wrong_recipe["retirements"]["bin/log-append"] = "0" * 64
    recipe_file = tmp_path / "wrong-recipe.json"
    write_json(recipe_file, wrong_recipe)
    wrong_destination = tmp_path / "wrong-preimage"
    wrong = run(
        "rehearse",
        "--source",
        source,
        "--output",
        wrong_destination,
        "--mapping",
        recipe_file,
    )
    assert (
        wrong.returncode == 2
        and "preimage mismatch" in wrong.stderr
        and not wrong_destination.exists()
    ), "MIGRATION RETIREMENT PREIMAGE NOT HELD"
    update_recipe = json.loads((tmp_path / "mapping.json").read_text())
    assert update_recipe["tool_replacements"]
    wrong_update = json.loads(json.dumps(update_recipe))
    wrong_update["tool_replacements"][next(iter(wrong_update["tool_replacements"]))] = "0" * 64
    update_file = tmp_path / "wrong-tool-preimage.json"
    write_json(update_file, wrong_update)
    update_destination = tmp_path / "wrong-tool-replacement"
    refused_update = run(
        "rehearse",
        "--source",
        source,
        "--output",
        update_destination,
        "--mapping",
        update_file,
    )
    assert (
        refused_update.returncode == 2
        and "replacement preimage required" in refused_update.stderr
        and not update_destination.exists()
    ), "MIGRATION TOOL REPLACEMENT IGNORED RECIPIENT PREIMAGE"
    assert (output / ".collaboration-views/LOG.md").read_bytes() == original, (
        "MIGRATION HISTORICAL BYTES LOST"
    )
    assert not (output / "LOG.md").exists() and not (output / "plan/phase-1.md").exists(), (
        "MIGRATION KEPT DUAL AUTHORITIES"
    )
    assert (output / "plan/phases/starter-template-adoption.md").is_file(), "MIGRATION PHASE LOST"
    assert (output / "AGENTS.md").is_file() and not (output / "AGENTS.md").is_symlink(), (
        "MIGRATION PRIMARY CONSTITUTION LOST"
    )
    assert not (output / "CLAUDE.md").exists(), "MIGRATION DUAL CONSTITUTIONS"
    assert "Hard rules" in (output / "AGENTS.md").read_text(), "MIGRATION CONSTITUTION CONTENT LOST"
    original_rules = (
        (source / "CLAUDE.md")
        .read_text()
        .split("## Hard rules", 1)[1]
        .split("<!-- PROJECT_CONTEXT_START -->", 1)[0]
    )
    target_rules = (
        (output / "AGENTS.md")
        .read_text()
        .split("## Hard rules", 1)[1]
        .split("<!-- PROJECT_CONTEXT_START -->", 1)[0]
    )
    assert target_rules == original_rules, "MIGRATION CONSTITUTION RULES CHANGED"
    assert (source / "AGENTS.md").is_symlink() and (source / "CLAUDE.md").is_file(), (
        "MIGRATION LIVE CONSTITUTION CHANGED"
    )
    retired = [
        "renumber-phases",
        "log-append",
        "log-relocate",
        "check-log",
        "check-log-prefix",
        "check-log-monotonic",
    ]
    assert all(not (output / "bin" / name).exists() for name in retired), (
        "MIGRATION OBSOLETE TOOL RETAINED"
    )
    assert not (output / "tests/test_renumber_phases.py").exists(), (
        "MIGRATION OBSOLETE TEST RETAINED"
    )
    assert (output / "lib/agentic_starter/log_blocks.py").is_file() and (
        output / "bin/normalize-final-newline"
    ).is_file(), "MIGRATION SHARED TOOL LOST"
    result(run("audit-retirement", "--root", output))
    bad_caller = output / "bin/dangling-caller"
    bad_caller.write_text("#!/bin/sh\n./bin/log-append\n")
    dangling = run("audit-retirement", "--root", output)
    assert dangling.returncode == 2 and "references remain" in dangling.stderr, (
        "MIGRATION DANGLING CALLER PASSED"
    )
    bad_caller.unlink()
    retirement = json.loads((output / "collaboration/retirement.json").read_text())
    assert set(retirement["inventory"]["obsolete"]) == {"bin/" + name for name in retired}, (
        "MIGRATION RETIREMENT INVENTORY LOST"
    )
    installed = subprocess.run(
        [str(output / "bin/multioperator"), "validate", "--root", str(output)],
        capture_output=True,
        text=True,
        env={**os.environ, "UV_OFFLINE": "1"},
        timeout=60,
    )
    result(installed)
    parity = subprocess.run(
        [str(output / "bin/check-harness-parity")],
        cwd=output,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert parity.returncode == 0, (
        "MIGRATION TARGET PARITY BROKEN: " + parity.stdout + parity.stderr
    )
    adapted_test = subprocess.run(
        [str(output / "bin/test"), "tests/test_log_control_plane.py"],
        cwd=output,
        capture_output=True,
        text=True,
        env={**os.environ, "UV_OFFLINE": "1"},
        timeout=90,
    )
    assert adapted_test.returncode == 0, (
        "MIGRATION SHARED NORMALIZATION PROOF LOST: " + adapted_test.stdout + adapted_test.stderr
    )
    parity_test = subprocess.run(
        [str(output / "bin/test"), "tests/test_mirror_parity.py"],
        cwd=output,
        capture_output=True,
        text=True,
        env={**os.environ, "UV_OFFLINE": "1"},
        timeout=90,
    )
    assert parity_test.returncode == 0, (
        "MIGRATION TARGET PARITY FIXTURE LOST: " + parity_test.stdout + parity_test.stderr
    )
    target_lint = subprocess.run(
        [str(output / "bin/check"), "lint"],
        cwd=output,
        capture_output=True,
        text=True,
        env={**os.environ, "UV_OFFLINE": "1"},
        timeout=90,
    )
    assert target_lint.returncode == 0, (
        "MIGRATION RETIREMENT BROKE LINT CALLER: " + target_lint.stdout + target_lint.stderr
    )
    migration_policy = (output / "policies/multi-operator-migration.md").read_text()
    assert "no top-level `CLAUDE.md` file or symlink" in migration_policy, (
        "MIGRATION CONFUSED PRIMARY CONSTITUTION WITH RETIRED ALIAS"
    )
    assert "project or ancestor `CLAUDE.md`" in migration_policy, (
        "MIGRATION REWROTE NATIVE PRECEDENCE FACT"
    )
    # No hook is installed: this calls the real replacement staged validator directly.
    for args in [
        ("init", "-b", "master"),
        ("add", "AGENTS.md", "plan", "log", "collaboration/manifest.json"),
        (
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.test",
            "commit",
            "-m",
            "Synthetic record baseline",
        ),
    ]:
        subprocess.run(["git", "-C", str(output), *args], check=True, capture_output=True)
    result(run("validate", "--root", output, "--staged"))
    frozen_event = next((output / "plan/events").glob("*.json"))
    original_event = frozen_event.read_bytes()
    wrong_event = json.loads(original_event)
    wrong_event["reason"] = "forged rewrite"
    frozen_event.write_text(json.dumps(wrong_event))
    subprocess.run(
        ["git", "-C", str(output), "add", str(frozen_event)],
        check=True,
        capture_output=True,
    )
    staged = run("validate", "--root", output, "--staged")
    assert staged.returncode == 2 and "immutable record rewrite" in staged.stderr, (
        "MIGRATION STAGED HISTORY REWRITE PASSED"
    )
    frozen_event.write_bytes(original_event)
    subprocess.run(
        ["git", "-C", str(output), "add", str(frozen_event)],
        check=True,
        capture_output=True,
    )
    result(run("validate", "--root", output, "--staged"))
    fresh_document = tmp_path / "fresh.md"
    fresh_document.write_text(
        "---\n"
        + yaml.safe_dump(
            {
                "id": "fresh-work-package",
                "title": "Fresh",
                "order": "100",
                "parent": None,
                "depends_on": [],
                "informs": [],
            }
        )
        + "---\n# Fresh\n"
    )
    result(run("add", "--root", output, "--document", fresh_document, "--writer", "fixture"))
    fresh = next(
        p
        for p in (output / "plan/events").glob("*.json")
        if json.loads(p.read_text())["phase"] == "fresh-work-package"
    )
    fresh_bytes = fresh.read_bytes()
    subprocess.run(["git", "-C", str(output), "add", "plan"], check=True, capture_output=True)
    result(run("validate", "--root", output, "--staged"))
    forged = json.loads(fresh_bytes)
    forged["state"] = "completed"
    fresh.write_text(json.dumps(forged))
    subprocess.run(["git", "-C", str(output), "add", str(fresh)], check=True, capture_output=True)
    fresh.write_bytes(fresh_bytes)
    rejected = run("validate", "--root", output, "--staged")
    assert rejected.returncode == 2 and "new completed genesis" in rejected.stderr, (
        "MIGRATION UNPROVED COMPLETED GENESIS ADMITTED: " + rejected.stderr
    )
    subprocess.run(["git", "-C", str(output), "add", str(fresh)], check=True, capture_output=True)
    result(run("validate", "--root", output, "--staged"))
    result(run("render", "--root", output))
    manifest = json.loads((output / "collaboration/manifest.json").read_text())
    assert manifest["adopted"] is False, "MIGRATION REHEARSAL CLAIMED ADOPTION"
    assert json.loads((output / "collaboration/adoption-blockers.json").read_text())["remaining"], (
        "MIGRATION CONCEALED ADAPTER GAPS"
    )
    assert (
        snapshot(source / "plan") == source_plan and (source / "LOG.md").read_bytes() == live_log
    ), "MIGRATION MUTATED LIVE STRUCTURE"
    assert subprocess.check_output(["git", "status", "--porcelain"], cwd=source) == status, (
        "MIGRATION MUTATED SOURCE CHECKOUT"
    )
    result(run("validate", "--root", output))
    result(run("render", "--root", output, "--check"))
    before = snapshot(output)
    collision = run(
        "rehearse",
        "--source",
        source,
        "--output",
        output,
        "--mapping",
        tmp_path / "mapping.json",
    )
    assert collision.returncode == 2 and "must be absent" in collision.stderr, (
        "MIGRATION OVERWROTE EXISTING DESTINATION"
    )
    assert snapshot(output) == before, "MIGRATION REFUSAL WROTE DESTINATION"


@pytest.fixture
def source(tmp_path: Path) -> Path:
    repo = tmp_path / "source"
    (repo / "plan").mkdir(parents=True)
    (repo / "plan/INDEX.md").write_text(
        "# Plan\n\n## Phase Table\n| Phase | Title | Status |\n|---|---|---|\n"
        "| [Phase 1](phase-1.md) | Parent | 🚧 |\n"
        "| [Phase 1.1](phase-1.1.md) | First | ✅ |\n"
        "| [Phase 1.2](phase-1.2.md) | Second | ⬅️ |\n\n"
        "## Notes\nDo not rewrite the dated meaning of Phase 1.\n"
    )
    for identifier, deps in [("1", []), ("1.1", []), ("1.2", ["1.1"])]:
        (repo / "plan" / ("phase-" + identifier + ".md")).write_text(
            "---\nid: "
            + json.dumps(identifier)
            + "\ntitle: Work\ndepends_on: "
            + json.dumps(deps)
            + "\ninforms: []\n---\n\n"
            "[Sibling](phase-1.1.md#goal) and [Brief](../briefs/example.md).\n"
        )
    (repo / "LOG.md").write_bytes(
        b"# Activity\n\n## 2026-01-01 01:00 \xe2\x80\x94 START\nOriginal Phase 1\n"
        b"```md\n## 1999-01-01 00:00 \xe2\x80\x94 quoted only\n```\n"
        b"## 2025-01-01 00:00 \xe2\x80\x94 correction\nOld clock preserved\n"
    )
    (repo / "CLAUDE.md").write_text("# Constitution\nPreserve this rule.\n")
    (repo / "AGENTS.md").symlink_to("CLAUDE.md")
    (repo / "README.md").write_text("[Plan](plan/phase-1.2.md) [History](LOG.md)\n")
    for args in [
        ("init", "-b", "master"),
        ("add", "AGENTS.md", "CLAUDE.md", "plan", "LOG.md", "README.md"),
        (
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.test",
            "commit",
            "-m",
            "Seed",
        ),
    ]:
        subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)
    return repo


MAPPING = {
    "1": "parent-work-package",
    "1.1": "first-work-package",
    "1.2": "second-work-package",
}


def checkpoint() -> dict[str, object]:
    return {
        "owners": {"1": "operator-a"},
        "active_checkpoints": {
            "1": {
                "terminal": True,
                "evidence": "retained checkpoint; original run stays closed",
            }
        },
    }


def test_transition_and_maintenance_refuse_false_state(tmp_path: Path, source: Path) -> None:
    mapping = tmp_path / "mapping.json"
    write_json(mapping, {"writer": "importer", "phases": MAPPING})
    out = tmp_path / "blocked"
    refused = run("rehearse", "--source", source, "--output", out, "--mapping", mapping)
    assert (
        refused.returncode == 2 and "terminal checkpoint" in refused.stderr and not out.exists()
    ), "MIGRATION ACTIVE CUTOVER NOT HELD"
    write_json(mapping, {"writer": "importer", "phases": {"1": "parent-work-package"}})
    refused = run("rehearse", "--source", source, "--output", out, "--mapping", mapping)
    assert refused.returncode == 2 and "cover every phase" in refused.stderr and not out.exists(), (
        "MIGRATION INCOMPLETE MAPPING ADMITTED"
    )
    output = convert(tmp_path, source, MAPPING, **checkpoint())
    assert (output / ".collaboration-views/LOG.md").read_bytes() == (
        source / "LOG.md"
    ).read_bytes(), "MIGRATION HISTORICAL BYTES LOST"
    phase = (output / "plan/phases/second-work-package.md").read_text()
    assert "- first-work-package" in phase and "parent: parent-work-package" in phase, (
        "MIGRATION IDENTITY EDGES LOST"
    )
    assert "(first-work-package.md#goal)" in phase and "(../../briefs/example.md)" in phase, (
        "MIGRATION LINK REWRITE WRONG"
    )
    assert "(plan/phases/second-work-package.md)" in (output / "README.md").read_text(), (
        "MIGRATION EXTERNAL LINK LOST"
    )
    heads = json.loads(run("validate", "--root", output).stdout)["heads"]
    original = snapshot(output)
    event = {
        "id": uuid.uuid4().hex,
        "phase": "second-work-package",
        "previous": heads["second-work-package"]["id"],
        "from": "next",
        "state": "in-progress",
        "owner": "operator-b",
        "writer": "operator-b",
        "reason": "explicit owner assignment",
        "claim": "external verified lease reference",
    }
    file = tmp_path / "event.json"
    for field, value, diagnostic in [
        ("previous", "0" * 32, "predecessor"),
        ("claim", "", "owner/claim"),
        ("state", "completed", "lifecycle"),
    ]:
        wrong = {**event, field: value}
        write_json(file, wrong)
        denied = run("event", "--root", output, "--file", file)
        assert denied.returncode == 2 and diagnostic in denied.stderr, (
            "MAINTENANCE REFUSAL GUARD MISSED: " + diagnostic + denied.stderr
        )
        assert snapshot(output) == original, "MAINTENANCE REFUSAL WROTE RECORDS"
    write_json(file, event)
    result(run("event", "--root", output, "--file", file))
    before = snapshot(output)
    replay = run("event", "--root", output, "--file", file)
    assert replay.returncode == 2 and snapshot(output) == before, "MAINTENANCE REPLAY WROTE RECORDS"
    # A second independently valid successor from the same predecessor is a real merge conflict.
    fork = {**event, "id": uuid.uuid4().hex, "owner": "operator-c"}
    (output / "plan/events" / (fork["id"] + ".json")).write_text(json.dumps(fork))
    denied = run("validate", "--root", output)
    assert denied.returncode == 2 and "competing phase heads" in denied.stderr, (
        "MAINTENANCE SILENTLY RESOLVED OWNERSHIP FORK"
    )
    (output / "plan/events" / (fork["id"] + ".json")).unlink()
    result(run("validate", "--root", output))
    selected = run(
        "select",
        "--root",
        output,
        "--owner",
        "operator-b",
        "--phase",
        "second-work-package",
    )
    result(selected)
    assert json.loads(selected.stdout)["phase"] == "second-work-package", (
        "SELECTION LOST EXACT PHASE"
    )
    wrong_owner = run(
        "select",
        "--root",
        output,
        "--owner",
        "operator-c",
        "--phase",
        "second-work-package",
    )
    assert wrong_owner.returncode == 2 and "another operator" in wrong_owner.stderr, (
        "SELECTION BORROWED OWNER CUSTODY"
    )
    automatic = run("select", "--root", output, "--owner", "operator-b")
    assert automatic.returncode == 2 and "no unique next" in automatic.stderr, (
        "SELECTION FABRICATED NEXT WORK"
    )
    from concurrent.futures import ThreadPoolExecutor

    proposals = []
    for index in range(2):
        proposal = {
            **event,
            "id": uuid.uuid4().hex,
            "previous": event["id"],
            "from": "in-progress",
            "reason": "Bounded concurrent fixture successor " + str(index),
        }
        target = tmp_path / ("successor-" + str(index) + ".json")
        write_json(target, proposal)
        proposals.append(target)
    with ThreadPoolExecutor(max_workers=2) as pool:
        attempts = list(
            pool.map(lambda path: run("event", "--root", output, "--file", path), proposals)
        )
    assert sorted(item.returncode for item in attempts) == [0, 2], (
        "CONCURRENT PHASE SUCCESSORS BOTH PUBLISHED"
    )
    result(run("validate", "--root", output))
    winner = json.loads(run("status", "--root", output).stdout)["heads"]["second-work-package"]
    event = winner
    # Actual distinct bodies at a common fixture time expose duplicate sequence allocation.
    bodies = []
    for index in range(2):
        target = tmp_path / ("parallel-" + str(index) + ".md")
        target.write_text("## Concurrent fixture\nBody " + str(index) + "\n")
        bodies.append(target)
    with ThreadPoolExecutor(max_workers=2) as pool:
        appends = list(
            pool.map(
                lambda path: run(
                    "append",
                    "--root",
                    output,
                    "--writer",
                    "concurrent-fixture",
                    "--body",
                    path,
                    "--at",
                    "2026-01-01T00:00:00Z",
                ),
                bodies,
            )
        )
    assert all(item.returncode == 0 for item in appends), (
        "CONCURRENT LOG APPEND REFUSED VALID INPUT"
    )
    validated = run("validate", "--root", output)
    assert validated.returncode == 0, "CONCURRENT LOG SEQUENCE FORKED"
    accepted_bytes = output / "qualification.json"
    accepted_bytes.write_text("Synthetic retained fixture; not native acceptance")
    completion = {
        **event,
        "id": uuid.uuid4().hex,
        "previous": event["id"],
        "from": "in-progress",
        "state": "completed",
    }
    for reference, diagnostic in [
        (None, "acceptance reference"),
        ({"path": "qualification.json", "sha256": "0" * 64}, "mutated"),
    ]:
        wrong = dict(completion)
        if reference is not None:
            wrong["acceptance"] = reference
        write_json(file, wrong)
        denied = run("event", "--root", output, "--file", file)
        assert denied.returncode == 2 and diagnostic in denied.stderr, (
            "MAINTENANCE FALSE COMPLETION ADMITTED: " + denied.stderr
        )
    completion["acceptance"] = {
        "path": "qualification.json",
        "sha256": hashlib.sha256(accepted_bytes.read_bytes()).hexdigest(),
    }
    write_json(file, completion)
    false_close = run("event", "--root", output, "--file", file)
    assert false_close.returncode == 2, "MAINTENANCE ARBITRARY ACCEPTANCE ADMITTED"
    assert not (output / "plan/events" / (completion["id"] + ".json")).exists()
    assert (
        json.loads(run("validate", "--root", output).stdout)["heads"]["second-work-package"][
            "state"
        ]
        == "in-progress"
    )
    parent_path = output / "plan/phases/parent-work-package.md"
    parent_original = parent_path.read_bytes()
    _, metadata, parent_body = parent_path.read_text().split("---\n", 2)
    parent_metadata = yaml.safe_load(metadata)
    parent_metadata["parent"] = "first-work-package"
    parent_path.write_text("---\n" + json.dumps(parent_metadata) + "\n---\n" + parent_body)
    cyclic = run("validate", "--root", output)
    assert cyclic.returncode == 2 and "graph cycle" in cyclic.stderr, "MAINTENANCE CYCLE PASSED"
    parent_path.write_bytes(parent_original)
    document = tmp_path / "new-phase.md"
    document.write_text(
        '---\nid: third-work-package\ntitle: Third\norder: "4"\nparent: null\n'
        "depends_on: [second-work-package]\ninforms: []\n---\nBody\n"
    )
    good_document = document.read_text()
    document.write_text(good_document.replace("[second-work-package]", "[absent-work-package]"))
    missing = run("add", "--root", output, "--document", document, "--writer", "operator-b")
    assert missing.returncode == 2 and "unknown dependency" in missing.stderr, (
        "MAINTENANCE UNKNOWN DEPENDENCY ADMITTED"
    )
    document.write_text(good_document)
    result(run("add", "--root", output, "--document", document, "--writer", "operator-b"))
    assert (output / "plan/phases/third-work-package.md").is_file(), "MAINTENANCE NEW PHASE LOST"
    result(run("order", "--root", output, "--phase", "third-work-package", "--value", "7/2"))
    ordered_metadata = yaml.safe_load(
        (output / "plan/phases/third-work-package.md").read_text().split("---\n", 2)[1]
    )
    assert ordered_metadata["order"] == "7/2", "MAINTENANCE EXACT ORDER LOST"
    before_order_refusal = snapshot(output)
    denied = run("order", "--root", output, "--phase", "third-work-package", "--value", "1/2")
    assert denied.returncode == 2 and "ordered after" in denied.stderr, (
        "MAINTENANCE ORDER VIOLATION ADMITTED"
    )
    assert snapshot(output) == before_order_refusal, "MAINTENANCE ORDER REFUSAL WROTE RECORDS"
    donor_state = (output / "collaboration/manifest.json").read_bytes()
    held = run(
        "transfer-preflight",
        "--entry",
        "teach",
        "--donor",
        output,
        "--recipient",
        source,
    )
    assert held.returncode == 2 and "has not migrated" in held.stderr, (
        "MIGRATION REHEARSAL DONOR ACCEPTED"
    )
    state = json.loads(donor_state)
    state["adopted"] = True
    (output / "collaboration/manifest.json").write_text(json.dumps(state))
    for entry in ("teach", "learn"):
        classified = run(
            "transfer-preflight",
            "--entry",
            entry,
            "--donor",
            output,
            "--recipient",
            source,
        )
        result(classified)
        route = json.loads(classified.stdout)
        assert (
            route["route"] == "migration-rehearsal"
            and route["mutation_authorized"] is False
            and route["adoption_verified"] is False
        ), "MIGRATION ROUTE GRANTED AUTHORITY"
    receiver = tmp_path / "adopted-receiver"
    shutil.copytree(output, receiver, symlinks=True)
    maintenance = run(
        "transfer-preflight",
        "--entry",
        "teach",
        "--donor",
        output,
        "--recipient",
        receiver,
    )
    result(maintenance)
    assert json.loads(maintenance.stdout)["route"] == "maintenance", "MIGRATION ADOPTED ROUTE WRONG"
    receiver_marker = receiver / "collaboration/manifest.json"
    receiver_state = json.loads(receiver_marker.read_text())
    receiver_state["adopted"] = False
    receiver_marker.write_text(json.dumps(receiver_state))
    pending = run(
        "transfer-preflight",
        "--entry",
        "learn",
        "--donor",
        output,
        "--recipient",
        receiver,
    )
    assert pending.returncode == 2 and "unresolved rehearsal" in pending.stderr, (
        "MIGRATION PENDING RECEIVER ACCEPTED"
    )
    marker = output / "collaboration/manifest.json"
    marker.write_text("{}")
    invalid = run(
        "transfer-preflight",
        "--entry",
        "teach",
        "--donor",
        output,
        "--recipient",
        source,
    )
    assert invalid.returncode == 2 and "malformed" in invalid.stderr, (
        "MIGRATION UNKNOWN DECLARATION DEFAULTED OK"
    )
    marker.write_bytes(donor_state)
    receiver_state["adopted"] = True
    receiver_marker.write_text(json.dumps(receiver_state))
    not_migrated = run(
        "transfer-preflight",
        "--entry",
        "learn",
        "--donor",
        source,
        "--recipient",
        receiver,
    )
    assert not_migrated.returncode == 2 and "has not migrated" in not_migrated.stderr, (
        "MIGRATION LEGACY DONOR ACCEPTED"
    )
    body = tmp_path / "body.md"
    body.write_text("## New maintenance entry\nExact bytes\n")
    bad_body = tmp_path / "bad-terminal.md"
    bad_body.write_text("## 2026-10-29 01:00 — END\nUnqualified terminal record\n")
    terminal = run("append", "--root", output, "--writer", "operator-b", "--body", bad_body)
    assert terminal.returncode == 2 and "Lessons" in terminal.stderr, (
        "MIGRATION TERMINAL WITNESS LOST"
    )
    result(
        run(
            "append",
            "--root",
            output,
            "--writer",
            "operator-b",
            "--body",
            body,
            "--at",
            "2026-10-29T01:00:00Z",
        )
    )
    denied = run(
        "append",
        "--root",
        output,
        "--writer",
        "operator-b",
        "--body",
        body,
        "--at",
        "2026-10-28T01:00:00Z",
    )
    assert denied.returncode == 2 and "clock moved backward" in denied.stderr, (
        "MAINTENANCE CLOCK REGRESSED"
    )
    stale = run("render", "--root", output, "--check")
    assert stale.returncode == 2 and "stale generated" in stale.stderr, (
        "MAINTENANCE STALE VIEW PASSED"
    )
    result(run("render", "--root", output))
    projected = (output / ".collaboration-views/LOG.md").read_bytes()
    prefix = (source / "LOG.md").read_bytes()
    first_body, second_body = [path.read_bytes() for path in bodies]
    assert projected in (
        prefix + first_body + second_body + body.read_bytes(),
        prefix + second_body + first_body + body.read_bytes(),
    ), "MAINTENANCE LOG PROJECTION WRONG"
    result(run("render", "--root", output, "--check"))
    entry = next(
        p for p in (output / "log/entries").glob("*.md") if b'"operator-b"' in p.read_bytes()
    )
    original_entry = entry.read_bytes()
    header, log_body = original_entry.split(b"\n---\n", 1)
    envelope = json.loads(header[4:])
    envelope["sequence"] = 2
    entry.write_bytes(b"---\n" + json.dumps(envelope).encode() + b"\n---\n" + log_body)
    gap = run("validate", "--root", output)
    assert gap.returncode == 2 and "sequence gap" in gap.stderr, "MAINTENANCE LOG GAP PASSED"
    entry.write_bytes(original_entry)
    entry.write_bytes(entry.read_bytes() + b"tamper")
    corrupted = run("validate", "--root", output)
    assert corrupted.returncode == 2 and "body digest" in corrupted.stderr, (
        "MAINTENANCE CORRUPTION PASSED"
    )


def test_constitution_version_gate_and_loading_limits(tmp_path: Path, monkeypatch) -> None:
    """Probe only a disposable executable's version, never a model or installed settings."""
    import sys

    monkeypatch.syspath_prepend(str(ROOT / "lib"))
    from agentic_starter import multioperator as migration
    from agentic_starter import multioperator_transition as transition

    binaries = tmp_path / "bin"
    binaries.mkdir()
    monkeypatch.setenv("PATH", str(binaries))
    absent = migration.claude_compatibility()
    assert absent["gate"] == "not-applicable" and absent["installed"] is None, "ABSENT CLAUDE GATED"
    executable = binaries / "claude"
    for output, exit_code, allowed in [
        ("2.1.289 (Claude Code)", 0, False),
        ("2.1.290 (Claude Code)", 0, True),
        ("2.1.291 (Claude Code)", 0, True),
        ("unknown", 0, False),
        ("2.1.290 (Claude Code)", 3, False),
    ]:
        executable.write_text(
            "#!"
            + sys.executable
            + "\nimport sys\nassert sys.argv[1:] == ['--version']\n"
            + "print("
            + repr(output)
            + ")\nsys.exit("
            + str(exit_code)
            + ")\n"
        )
        executable.chmod(0o755)
        if allowed:
            observed = migration.claude_compatibility()
            assert observed["gate"] == "passed" and observed["minimum"] == "2.1.290", (
                "VERSION FLOOR CHANGED"
            )
            assert observed["instruction_loading"] == "not-observed", (
                "VERSION MISLABELLED AS LOADING"
            )
        else:
            refused = False
            try:
                migration.claude_compatibility()
            except migration.Refusal:
                refused = True
            assert refused, "CLAUDE INVALID VERSION ADMITTED: " + output + ":" + str(exit_code)
    target = tmp_path / "target"
    (target / ".claude").mkdir(parents=True)
    local = target / ".claude/CLAUDE.md"
    local.write_text("local instructions must remain\n")
    warnings = migration.constitution_caveats(target)
    assert any(
        warning.startswith("Project-local instruction precedence") for warning in warnings
    ), "LOCAL LOADING CAVEAT HIDDEN"
    assert local.read_text() == "local instructions must remain\n", "LOCAL INSTRUCTIONS MUTATED"

    # The actual target transformer must also preserve local files, not just its warning probe.
    old = target / "CLAUDE.md"
    old.write_text("# Constitution\nKeep all rules.\n")
    primary = target / "AGENTS.md"
    primary.write_text("different owner rules\n")
    conflict = False
    try:
        transition.promote_constitution(target)
    except ValueError:
        conflict = True
    assert conflict and old.read_text() == "# Constitution\nKeep all rules.\n", (
        "CONSTITUTION CONFLICT OVERWRITTEN"
    )
    primary.unlink()
    primary.symlink_to("CLAUDE.md")
    local.write_text("Local instruction mentions CLAUDE.md verbatim.\n")
    transition.promote_constitution(target)
    assert local.read_text() == "Local instruction mentions CLAUDE.md verbatim.\n", (
        "LOCAL TRANSITION INSTRUCTIONS MUTATED"
    )
    assert primary.is_file() and not primary.is_symlink() and not old.exists(), (
        "CONSTITUTION PROMOTION INCOMPLETE"
    )
    assert primary.read_text() == "# Constitution\nKeep all rules.\n", (
        "CONSTITUTION ORIGINAL BODY LOST"
    )
