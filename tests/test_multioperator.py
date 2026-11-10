"""Portable synthetic migration and current-record contracts; no donor history required."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
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


def assert_rehearsal_contract(tmp_path: Path, source: Path, mapping: dict[str, str]) -> None:
    """One receiving contract, exercised against synthetic and real historical input."""
    source_plan = snapshot(source / "plan")
    live_log = (source / "LOG.md").read_bytes()
    status = subprocess.check_output(["git", "status", "--porcelain"], cwd=source)
    original = live_log
    output = convert(tmp_path, source, mapping)
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
    assert (output / ("plan/phases/" + mapping["1"] + ".md")).is_file(), "MIGRATION PHASE LOST"
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


def test_portable_rehearsal_preserves_source_and_guards(tmp_path: Path) -> None:
    source = tmp_path / "portable-source"
    for directory in (
        "plan",
        "bin",
        "tests",
        "project",
        "policies",
        ".claude/skills/probe",
        ".claude/agents",
        ".agents/skills",
        ".codex/agents",
    ):
        (source / directory).mkdir(parents=True, exist_ok=True)
    (source / "plan/INDEX.md").write_text(
        "# Plan\n\n## Phase Table\n| Phase | Status |\n|---|---|\n| [Phase 1](phase-1.md) | ⬅️ |\n"
    )
    (source / "plan/phase-1.md").write_text(
        '---\nid: "1"\ntitle: Synthetic\ndepends_on: []\ninforms: []\n---\n# Synthetic\n'
    )
    (source / "CLAUDE.md").write_text(
        "# Constitution\n## Hard rules\nPreserve this rule.\n<!-- PROJECT_CONTEXT_START -->\n"
    )
    (source / "AGENTS.md").symlink_to("CLAUDE.md")
    (source / "LOG.md").write_text("# Exact synthetic history\n")
    (source / "README.md").write_text("[Plan](plan/phase-1.md)\n")
    shutil.copytree(
        ROOT / "lib/agentic_starter",
        source / "lib/agentic_starter",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    for name in ("multioperator", "check-harness-parity", "normalize-final-newline"):
        shutil.copy2(ROOT / "bin" / name, source / "bin" / name)
    # A genuine differing, approved input tool exercises exact replacement preimages.
    migration_tool = source / "bin/multioperator"
    migration_tool.write_text(migration_tool.read_text() + "\n# Synthetic prior revision\n")
    normalizer = source / "bin/normalize-final-newline"
    normalizer.write_text(
        normalizer.read_text().replace(
            'ALLOWED = {Path("EXECUTION_LOG.jsonl")}',
            'ALLOWED = {Path("LOG.md"), Path("EXECUTION_LOG.jsonl"), Path("plan/INDEX.md")}',
        )
    )
    for name in (
        "renumber-phases",
        "log-append",
        "log-relocate",
        "check-log",
        "check-log-prefix",
        "check-log-monotonic",
    ):
        path = source / "bin" / name
        path.write_text("#!/bin/sh\nexit 0\n")
        path.chmod(0o755)
    (source / "tests/test_renumber_phases.py").write_text("# Synthetic retired contract\n")
    (source / "tests/test_log_control_plane.py").write_text(
        "# Converted to the retained shared normalizer proof\n"
    )
    for name, command in (("python", '"$@"'), ("test", '-m pytest "$@"')):
        path = source / "bin" / name
        path.write_text("#!/bin/sh\nexec " + repr(sys.executable) + " " + command + "\n")
        path.chmod(0o755)
    check = source / "bin/check"
    check.write_text(
        '#!/bin/sh\nset -eu\ntest "$1" = lint\n# test-governance check-l'
        "og check-log-prefix check-log-monotonic kickoff-command-zero"
        "\n# log-append log-relocate normalize-final-newline\n# run_gat"
        "e policy-log ./bin/check-log\nexec "
        + repr(sys.executable)
        + " -m ruff check --config project/pyproject.toml lib tests bin"
        "/check-harness-parity bin/normalize-final-newline ../bin/che"
        "ck-log ../bin/check-log-prefix ../bin/check-log-monotonic\n"
    )
    check.chmod(0o755)
    (source / "project/pyproject.toml").write_text(
        '[tool.ruff]\nline-length = 100\ntarget-version = "py311"\n[tool'
        '.ruff.lint]\nselect = ["E", "F", "I"]\n'
    )
    (source / ".claude/skills/probe/SKILL.md").write_text("# Probe\n")
    (source / ".agents/skills/probe").symlink_to("../../.claude/skills/probe")
    (source / ".claude/agents/phase-coder.md").write_text(
        "---\nname: phase-coder\ndescription: Fixture role\n---\n# Coder\n"
    )
    (source / ".codex/agents/phase-coder.toml").write_text(
        'name = "phase-coder"\ndescription = "Fixture role"\ndeveloper_'
        'instructions = "Read .claude/agents/phase-coder.md in this r'
        'epo and follow it."\n'
    )
    (source / "tests/test_mirror_parity.py").write_text("""import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_converted_checker_and_fixture(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_text("Rule")
    (tmp_path / "AGENTS.md").symlink_to("CLAUDE.md")
    checker = ROOT / "bin/check-harness-parity"
    assert subprocess.run([str(checker)], capture_output=True).returncode == 0
    mirror = ROOT / ".agents/skills/probe"
    mirror.unlink()
    mirror.write_text("Not a mirror")
    try:
        assert subprocess.run([str(checker)], capture_output=True).returncode == 1
    finally:
        mirror.unlink()
        mirror.symlink_to("../../.claude/skills/probe")
""")
    shutil.copy2(
        ROOT / "policies/multi-operator-migration.md",
        source / "policies/multi-operator-migration.md",
    )
    for args in (
        ("init", "-q", "-b", "master"),
        (
            "add",
            "AGENTS.md",
            "CLAUDE.md",
            "LOG.md",
            "README.md",
            "plan",
            "bin",
            "lib",
            "tests",
            "project",
            "policies",
            ".claude",
            ".agents",
            ".codex",
        ),
        (
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.test",
            "commit",
            "-q",
            "-m",
            "Synthetic pre-transition input",
        ),
    ):
        subprocess.run(["git", *args], cwd=source, check=True, capture_output=True)
    assert_rehearsal_contract(tmp_path, source, {"1": "portable-work-package"})


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
    original_logs = snapshot(output / "log/entries")
    refusals = []
    for kind in ("END", "PARK"):
        for answer in ("", "Lessons: substantive prose\n"):
            bad_body.write_text(f"## 2026-10-29 01:00 — {kind}\n{answer}")
            rejected_bytes = bad_body.read_bytes()
            terminal = run("append", "--root", output, "--writer", "operator-b", "--body", bad_body)
            refusals.append(
                terminal.returncode == 2
                and "Lessons" in terminal.stderr
                and bad_body.read_bytes() == rejected_bytes
                and snapshot(output / "log/entries") == original_logs
            )
    assert all(refusals), "TERMINAL REFUSAL LOST OR IMMUTABLE LOG BYTES CHANGED"

    content = tmp_path / "terminal.json"
    fields = {
        "title": "END (correction)",
        "body": (
            "Correction bookkeeping\n\nBuild status:\n- Focused checks passed\n\nRemaining:\n- None"
        ),
        "lessons": ["Require structural composition at the publication boundary."],
    }
    write_json(content, fields)
    prepared = tmp_path / "prepared.md"
    result(
        run(
            "compose-terminal",
            "--content",
            content,
            "--output",
            prepared,
            "--at",
            "2026-10-29T01:00:00Z",
        )
    )
    expected = (
        "## 2026-10-29 01:00 — END (correction)\n\nCorrection bookkeeping\n\n"
        "Build status:\n- Focused checks passed\n\nRemaining:\n- None\n\n"
        "Lessons:\n- Require structural composition at the publication boundary.\n"
    ).encode()
    assert prepared.read_bytes() == expected, "TERMINAL COMPOSITION CHANGED MEANING OR FORMAT"
    result(
        run(
            "append-terminal",
            "--root",
            output,
            "--writer",
            "operator-c",
            "--content",
            content,
            "--at",
            "2026-10-29T01:00:00Z",
        )
    )
    published = snapshot(output / "log/entries")
    added = set(published) - set(original_logs)
    assert len(added) == 1 and published[added.pop()].split(b"\n---\n", 1)[1] == expected, (
        "TERMINAL COMPOSER DID NOT USE IMMUTABLE DESTINATION"
    )
    # Compose collisions and malformed substantive input never overwrite records.
    collision = run("compose-terminal", "--content", content, "--output", prepared)
    failures = [collision.returncode == 2 and prepared.read_bytes() == expected]
    for malformed in (
        {key: value for key, value in fields.items() if key != "lessons"},
        {**fields, "lessons": []},
        {**fields, "body": "Lessons: inline substitute"},
        {**fields, "body": "## 2026-10-29 01:01 — END\nInjected record"},
    ):
        write_json(content, malformed)
        refused = run(
            "append-terminal",
            "--root",
            output,
            "--writer",
            "operator-c",
            "--content",
            content,
        )
        failures.append(refused.returncode == 2 and snapshot(output / "log/entries") == published)
    assert all(failures), "TERMINAL COMPOSER INFERRED LESSONS OR MUTATED ON REFUSAL"
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
        prefix + first_body + second_body + body.read_bytes() + expected,
        prefix + second_body + first_body + body.read_bytes() + expected,
        prefix + first_body + second_body + expected + body.read_bytes(),
        prefix + second_body + first_body + expected + body.read_bytes(),
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


def test_transfer_equivalence_for_existing_product(tmp_path: Path) -> None:
    """Admission: a missing receiver class and reversed source eligibility escaped old proofs.

    One bounded CLI table checks both entry labels, both source directions and precise
    partial-layout refusals. Snapshots independently guard against assessment writes.
    """
    from structured_fixtures import create_records

    adopted = tmp_path / "adopted"
    adopted.mkdir()
    (adopted / "AGENTS.md").write_text("# Synthetic constitution\n")
    create_records(adopted, {})
    product = tmp_path / "product"
    product.mkdir()
    (product / "pyproject.toml").write_text('[project]\nname = "sample-product"\n')
    (product / "src/sample_product").mkdir(parents=True)
    (product / "src/sample_product/__init__.py").write_text('"""Existing product."""\n')
    (product / "plan").mkdir()
    (product / "plan/README.md").write_text("# Historical narrative roadmap\n")
    for number in range(1, 7):
        (product / f"plan/{number:02d}-narrative.md").write_text(f"# Historical plan {number}\n")
    prose_source = tmp_path / "prose-source"
    prose_source.mkdir()
    (prose_source / "README.md").write_text("# A selected documentation capability\n")
    before = snapshot(tmp_path)
    observed = []
    for donor, recipient, intent, expected in (
        (adopted, product, "methodology", "retrofit-rehearsal"),
        (product, adopted, "capability", "capability-learning"),
        (prose_source, adopted, "capability", "capability-learning"),
        (adopted, product, "capability", "capability-learning"),
        (adopted, adopted, "methodology", "same checkout"),
        (product, adopted, "methodology", "has not migrated"),
    ):
        answers = []
        for entry in ("teach", "learn"):
            response = run(
                "transfer-preflight",
                "--entry",
                entry,
                "--intent",
                intent,
                "--donor",
                donor,
                "--recipient",
                recipient,
            )
            if response.returncode == 0:
                value = json.loads(response.stdout)
                value.pop("entry")
                answers.append(value)
                observed.append(
                    value["route"] == expected
                    and not value["mutation_authorized"]
                    and not value["adoption_verified"]
                )
            else:
                answers.append(response.stderr)
                observed.append(response.returncode == 2 and expected in response.stderr)
        observed.append(answers[0] == answers[1])
    observed.append(snapshot(tmp_path) == before)
    for marker, message in (
        ("plan/events", "partial collaboration"),
        ("plan/INDEX.md", "partial/unsupported"),
        ("LOG.md", "partial/unsupported"),
        ("kickoff.yaml", "partial methodology"),
        ("AGENTS.md", "constitution requires owner"),
        ("collaboration/manifest.json", "malformed"),
    ):
        target = product / marker
        target.parent.mkdir(parents=True, exist_ok=True)
        if marker == "plan/events":
            target.mkdir()
        else:
            target.write_text("{}")
        frozen = snapshot(product)
        for entry in ("teach", "learn"):
            response = run(
                "transfer-preflight",
                "--entry",
                entry,
                "--donor",
                adopted,
                "--recipient",
                product,
            )
            observed.append(
                response.returncode == 2
                and message in response.stderr
                and snapshot(product) == frozen
            )
        if target.is_dir():
            target.rmdir()
        else:
            target.unlink()
        if marker.startswith("collaboration/"):
            target.parent.rmdir()
    unknown = tmp_path / "unknown"
    unknown.mkdir()
    (unknown / "README.md").write_text("Unclassified records\n")
    response = run(
        "transfer-preflight",
        "--entry",
        "teach",
        "--donor",
        adopted,
        "--recipient",
        unknown,
    )
    observed.append(response.returncode == 2 and "unsupported existing-project" in response.stderr)
    assert all(observed), "TRANSFER EQUIVALENCE OR REFUSAL CONTRACT LOST: " + repr(observed)


def test_retrofit_rehearsal_preserves_narrative_history(tmp_path: Path) -> None:
    """Admission: canonical conversion cannot consume existing narrative-only product history.

    One committed tiny product and three refusing recipes exercise the real archive/CLI
    boundary. No network, dependency provisioning or live receiving checkout is used.
    """
    source = tmp_path / "source"
    source.mkdir()
    (source / "pyproject.toml").write_text('[project]\nname = "sample-product"\n')
    (source / "plan").mkdir()
    for number in range(1, 7):
        (source / f"plan/{number:02d}-narrative.md").write_text(f"# Historical plan {number}\n")
    (source / "plan/README.md").write_text("# Original roadmap\n")
    for args in (
        ("init", "-b", "master"),
        ("add", "pyproject.toml", "plan"),
        (
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.test",
            "commit",
            "-m",
            "Synthetic existing product",
        ),
    ):
        subprocess.run(["git", "-C", str(source), *args], check=True, capture_output=True)
    head = subprocess.check_output(
        ["git", "-C", str(source), "rev-parse", "HEAD"], text=True
    ).strip()
    original = snapshot(source)
    recipe = dict(
        mode="retrofit",
        source_commit=head,
        writer="fixture-operator",
        constitution="# Reviewed receiving constitution\n",
        historical_plans={
            name: hashlib.sha256(body).hexdigest()
            for name, body in original.items()
            if name.startswith("plan/")
        },
    )
    recipe_file = tmp_path / "recipe.json"
    write_json(recipe_file, recipe)
    # Unique dirty work must stay in place and never masquerade as committed rehearsal input.
    (source / "plan/01-narrative.md").write_text("Unique unsettled work\n")
    dirty = snapshot(source)
    output = tmp_path / "rehearsal"
    response = run("rehearse", "--source", source, "--mapping", recipe_file, "--output", output)
    observed = [response.returncode == 0]
    if response.returncode == 0:
        retained = snapshot(output)
        observed += [
            all(retained.get(name) == body for name, body in original.items()),
            not (output / "LOG.md").exists(),
            not list((output / "plan/events").glob("*.json")),
            not list((output / "plan/phases").glob("*.md")),
            not list((output / "log/entries").glob("*.md")),
        ]
        state = json.loads(run("validate", "--root", output).stdout)
        observed.append(
            state["adopted"] is False
            and state["phases"] == state["events"] == state["log_entries"] == 0
        )
        observed.append(run("render", "--root", output, "--check").returncode == 0)
        for args in (
            ("init", "-b", "master"),
            ("add", "AGENTS.md", "plan", "log", "collaboration/manifest.json"),
        ):
            subprocess.run(["git", "-C", str(output), *args], check=True, capture_output=True)
        observed.append(run("validate", "--root", output, "--staged").returncode == 0)
        (output / "plan/01-narrative.md").write_text("Lost history\n")
        subprocess.run(
            ["git", "-C", str(output), "add", "plan/01-narrative.md"],
            check=True,
            capture_output=True,
        )
        (output / "plan/01-narrative.md").write_bytes(original["plan/01-narrative.md"])
        refused = run("validate", "--root", output, "--staged")
        observed.append(
            refused.returncode == 2 and "historical plan missing or mutated" in refused.stderr
        )
        (output / "plan/01-narrative.md").write_text("Lost history\n")
        refused = run("validate", "--root", output)
        observed.append(
            refused.returncode == 2 and "historical plan missing or mutated" in refused.stderr
        )
        occupied = snapshot(output)
        refused = run("rehearse", "--source", source, "--mapping", recipe_file, "--output", output)
        observed.append(
            refused.returncode == 2
            and "output must be absent" in refused.stderr
            and snapshot(output) == occupied
        )
    for change, message in (
        ({"source_commit": "unbound"}, "exact committed source"),
        ({"historical_plans": {}}, "inventory/preimage mismatch"),
        ({"constitution": ""}, "reviewed constitution"),
    ):
        write_json(recipe_file, {**recipe, **change})
        absent = tmp_path / ("refused-" + next(iter(change)))
        refused = run("rehearse", "--source", source, "--mapping", recipe_file, "--output", absent)
        observed.append(
            refused.returncode == 2 and message in refused.stderr and not absent.exists()
        )
    observed.append(snapshot(source) == dirty)
    assert all(observed), "RETROFIT HISTORY OR REFUSAL CONTRACT LOST: " + repr(observed)


def test_absent_retained_evidence_is_reported_while_altered_evidence_refuses(
    tmp_path: Path,
) -> None:
    """Admission: a clean clone could not pass the gate, yet tampering must still refuse.

    A hand-built historical completion gives validation real retained bytes to re-verify.
    The oracle is the validator's own exit status and reported list for three states of
    the same file: intact, altered and absent.
    """
    from structured_fixtures import create_records

    def sha(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    root = tmp_path / "held"
    root.mkdir()
    (root / "AGENTS.md").write_text("# Synthetic constitution\n")
    (root / "EXECUTION_LOG.jsonl").write_bytes(b"")
    name = "kept-work-package"
    opened = create_records(root, {name: {"state": "in-progress"}})[name]
    retained = root / ".kickoff/runs/fixture/gates.jsonl"
    retained.parent.mkdir(parents=True)
    retained.write_text("{}\n")
    retained_name = retained.relative_to(root).as_posix()
    body = (
        "## 2026-01-01 00:00 — END " + name + "\n\nSynthetic historical close.\n\n"
        "Lessons:\n- none\n"
    ).encode()
    bound = {
        "phase": name,
        "outcome": "accepted",
        "phase_custody": {
            "id": opened["id"],
            "owner": opened["owner"],
            "claim": opened["claim"],
        },
        "qualification": {
            "schema": "agentic.phase-qualification.v1",
            "files": {retained_name: sha(retained.read_bytes())},
            "budget_prefix": None,
            "execution_prefix": {"path": "EXECUTION_LOG.jsonl", "bytes": 0, "sha256": sha(b"")},
        },
        "log_sha256": sha(body),
    }
    closure_id = sha(json.dumps(bound, sort_keys=True, separators=(",", ":")).encode())
    closure = retained.parent / "closure.json"
    closure.write_text(json.dumps({**bound, "closure_id": closure_id, "status": "complete"}))
    log_id = uuid.uuid5(uuid.NAMESPACE_URL, "log:" + opened["owner"] + ":" + closure_id).hex
    envelope = {
        "at": "2026-01-01T00:00:00+00:00",
        "body_sha256": sha(body),
        "id": log_id,
        "previous": None,
        "sequence": 1,
        "writer": opened["owner"],
    }
    (root / "log/entries" / (log_id + ".md")).write_bytes(
        b"---\n" + json.dumps(envelope).encode() + b"\n---\n" + body
    )
    completed = {
        **opened,
        "id": uuid.uuid4().hex,
        "previous": opened["id"],
        "from": "in-progress",
        "state": "completed",
        "reason": "Synthetic historical completion",
        "acceptance": {
            "path": closure.relative_to(root).as_posix(),
            "sha256": sha(closure.read_bytes()),
        },
    }
    write_json(root / "plan/events" / (completed["id"] + ".json"), completed)

    intact = run("validate", "--root", root)
    assert intact.returncode == 0, "VALID RETAINED EVIDENCE REFUSED: " + intact.stderr
    original = retained.read_bytes()
    retained.write_text("altered\n")
    altered = run("validate", "--root", root)
    retained.write_bytes(original)
    retained.unlink()
    absent = run("validate", "--root", root)
    shutil.rmtree(root / ".kickoff")
    cloned = run("validate", "--root", root)
    assert (
        json.loads(intact.stdout)["evidence_not_held"] == []
        and altered.returncode == 2
        and "missing or mutated" in altered.stderr
        and absent.returncode == 0
        and json.loads(absent.stdout)["evidence_not_held"] == [retained_name]
        and "EVIDENCE NOT HELD 1" in absent.stderr
        and cloned.returncode == 0
        and json.loads(cloned.stdout)["evidence_not_held"] == [completed["acceptance"]["path"]]
    ), (
        "RETAINED EVIDENCE ABSENCE REFUSED OR ALTERATION PASSED: "
        + altered.stderr
        + absent.stderr
        + cloned.stderr
    )


def test_methodology_close_cannot_bypass_the_lessons_contract(tmp_path: Path) -> None:
    """Admission: closes written under a bare methodology heading carried no Lessons.

    The append boundary is exercised directly: a scope record and a composed terminal
    record are admitted, while a close under any non-terminal methodology heading refuses
    and leaves the log bytes unchanged.
    """
    from structured_fixtures import create_records

    root = tmp_path / "records"
    root.mkdir()
    (root / "AGENTS.md").write_text("# Synthetic constitution\n")
    create_records(root, {"open-work-package": {"state": "next"}})
    body = tmp_path / "body.md"

    def append(heading: str, tail: str = "Body.\n") -> subprocess.CompletedProcess[str]:
        body.write_text(f"## 2026-11-10 01:00 — {heading}\n\n{tail}")
        return run(
            "append", "--root", root, "--writer", "operator-a", "--body", body,
            "--at", "2026-11-10T01:00:00Z",
        )  # fmt: skip

    scope = append("METHODOLOGY SCOPE")
    before = snapshot(root / "log/entries")
    bypasses = [append("METHODOLOGY"), append("METHODOLOGY CLOSE gate work")]
    unchanged = snapshot(root / "log/entries") == before
    terminal = append("END — METHODOLOGY gate work", "Done.\n\nLessons:\n- none\n")
    assert (
        scope.returncode == 0
        and all(item.returncode == 2 and "append-terminal" in item.stderr for item in bypasses)
        and unchanged
        and terminal.returncode == 0
    ), "METHODOLOGY CLOSE BYPASSED LESSONS OR VALID RECORD REFUSED: " + "".join(
        item.stderr for item in (scope, *bypasses, terminal)
    )


def test_preflight_lists_source_releases_the_recipient_has_not_recorded(tmp_path: Path) -> None:
    """Admission: no recipient could say which source release it held.

    Real preflight runs compare a recorded baseline with the source's declared releases;
    an absent record claims nothing, and a malformed one refuses instead of hiding a gap.
    """
    from structured_fixtures import create_records

    roots = []
    for name in ("source", "recipient"):
        root = tmp_path / name
        root.mkdir()
        (root / "AGENTS.md").write_text("# Synthetic constitution\n")
        create_records(root, {})
        roots.append(root)
    source, recipient = roots
    (source / "RELEASES.md").write_text(
        "# Releases\n\n## 1.1.0 — 2026-11-10\n\n## 1.0.2 — 2026-11-10\n\n## 1.0.1 — 2026-11-10\n"
    )
    record = recipient / "collaboration/methodology-provenance.json"

    def preflight() -> subprocess.CompletedProcess[str]:
        return run(
            "transfer-preflight", "--entry", "teach", "--donor", source, "--recipient", recipient
        )  # fmt: skip

    unrecorded = preflight()
    write_json(
        record,
        {
            "schema": "agentic.methodology-provenance.v1",
            "source": "synthetic-source",
            "release": "1.0.2",
            "revision": "a" * 40,
            "recorded": "2026-11-10",
            "capabilities": ["gate-report-mode"],
        },
    )
    recorded = preflight()
    record.write_text('{"release": "1.1.0"}')
    malformed = preflight()
    assert (
        unrecorded.returncode == 0
        and json.loads(unrecorded.stdout)["recipient_provenance"] is None
        and json.loads(unrecorded.stdout)["releases_not_recorded"] == ["1.0.1", "1.0.2", "1.1.0"]
        and recorded.returncode == 0
        and json.loads(recorded.stdout)["releases_not_recorded"] == ["1.1.0"]
        and malformed.returncode == 2
        and "provenance" in malformed.stderr
    ), "RELEASE GAP MISREPORTED OR MALFORMED PROVENANCE ACCEPTED: " + "".join(
        item.stderr for item in (unrecorded, recorded, malformed)
    )


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", *args],
        cwd=root, check=True, capture_output=True, text=True,
    ).stdout.strip()  # fmt: skip


def test_adoption_is_the_only_manifest_change_after_cutover(tmp_path: Path) -> None:
    """Admission: a cutover committed undeclared could never record its owner's adoption.

    The real commands run against a committed conversion: the declaration refuses while
    the plan index still carries the rehearsal banner, then becomes the one manifest
    change the staged validator admits; any other field change still refuses.
    """
    from structured_fixtures import create_records

    root = tmp_path / "records"
    (root / "collaboration").mkdir(parents=True)
    (root / "AGENTS.md").write_text("# Synthetic constitution\n")
    manifest = root / "collaboration/manifest.json"
    write_json(
        manifest,
        {
            "format": "starter.multioperator.v1",
            "adopted": False,
            "original_log_bytes": 0,
            "original_log_sha256": hashlib.sha256(b"").hexdigest(),
        },
    )
    create_records(root, {"open-work-package": {"state": "next"}})
    index = root / "plan/INDEX.md"
    index.write_text("# Proposed plan discovery — REHEARSAL ONLY\n\nContext.\n")
    _git(root, "init", "-q", "-b", "master")
    _git(root, "add", ".")
    _git(root, "commit", "-q", "-m", "cutover")

    unreviewed = run("adopt", "--root", root)
    index.write_text("# Plan discovery\n\nContext.\n")
    declared = run("adopt", "--root", root)
    _git(root, "add", "collaboration/manifest.json")
    admitted = run("validate", "--root", root, "--staged")
    adopted = manifest.read_bytes()
    manifest.write_bytes(adopted.replace(b'"original_log_bytes": 0', b'"original_log_bytes": 1'))
    _git(root, "add", "collaboration/manifest.json")
    widened = run("validate", "--root", root, "--staged")
    manifest.write_bytes(adopted)
    _git(root, "add", "collaboration/manifest.json")
    _git(root, "commit", "-q", "-m", "adopt")
    repeated = run("adopt", "--root", root)
    assert (
        unreviewed.returncode == 2
        and "rehearsal banner" in unreviewed.stderr
        and declared.returncode == 0
        and json.loads(adopted)["adopted"] is True
        and admitted.returncode == 0
        and widened.returncode == 2
        and "immutable record rewrite" in widened.stderr
        and repeated.returncode == 2
        and "already declared" in repeated.stderr
    ), "ADOPTION DECLARATION REFUSED OR WIDENED: " + "".join(
        item.stderr for item in (unreviewed, declared, admitted, widened, repeated)
    )


def test_transfer_ancestry_names_the_nearest_revision_and_recipient_lines(tmp_path: Path) -> None:
    """Admission: merging against one assumed base silently dropped content a recipient never had.

    A recipient that took an early donor revision and added a line of its own must be
    reported against that early revision, with its own line named, so later donor
    additions merge in instead of reading as recipient deletions.
    """
    donor, recipient = tmp_path / "donor", tmp_path / "recipient"
    revisions = {}
    donor.mkdir()
    _git(donor, "init", "-q", "-b", "master")
    for name, tracked, behind in (
        ("early", "a\nb\nc\n", "x\n"),
        ("middle", "a\nb2\nc\nd\n", "x\ny\n"),
        ("late", "a\nb3\nc\nd\ne\n", "x\ny\nz\n"),
    ):
        (donor / "tracked.txt").write_text(tracked)
        (donor / "behind.txt").write_text(behind)
        (donor / "same.txt").write_text("unchanged\n")
        _git(donor, "add", ".")
        _git(donor, "commit", "-q", "-m", name)
        revisions[name] = _git(donor, "rev-parse", "HEAD")
    recipient.mkdir()
    _git(recipient, "init", "-q", "-b", "master")
    (recipient / "tracked.txt").write_text("a\nb\nmine\nc\n")
    (recipient / "behind.txt").write_text("x\ny\n")
    (recipient / "same.txt").write_text("unchanged\n")
    _git(recipient, "add", ".")
    _git(recipient, "commit", "-q", "-m", "recipient")

    report = run("transfer-ancestry", "--donor", donor, "--recipient", recipient)
    result(report)
    files = {item["path"]: item for item in json.loads(report.stdout)["files"]}
    assert (
        set(files) == {"tracked.txt", "behind.txt"}
        and files["tracked.txt"]["ancestor"] == revisions["early"]
        and files["tracked.txt"]["recipient_own_lines"] == ["mine"]
        and files["tracked.txt"]["state"] == "edited"
        and files["behind.txt"]["state"] == "behind"
        and files["behind.txt"]["ancestor"] == revisions["middle"]
        and files["behind.txt"]["recipient_own_lines"] == []
    ), "TRANSFER ANCESTRY MISREAD THE RECIPIENT: " + report.stdout
