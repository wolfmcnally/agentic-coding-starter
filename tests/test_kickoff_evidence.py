"""Behavioral tests for run-scoped kickoff evidence."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "bin" / "kickoff-evidence"
TREE_ID = ROOT / "bin" / "kickoff-tree-id"
UV = shutil.which("uv")
assert UV is not None
sys.path.insert(0, str(ROOT / "lib"))
from agentic_starter.execution_telemetry import (  # noqa: E402
    attach_review_metrics,
    closed_span,
    closed_spans,
    finalize_trace,
    finish_span,
    start_span,
    start_trace,
)


def link_managed_interpreter(root: Path) -> None:
    """Give a synthetic engine root the managed interpreter a real one has.

    Repo tools run under `#!/usr/bin/env python3`, so an ambient interpreter
    older than 3.11 makes the shared guard re-exec under
    `<repository_root>/.venv/bin/python3`. A real engine root always has that
    venv; a fixture root without one models an engine that cannot exist, and
    the guard then refuses for want of an interpreter instead of proving
    anything about the tool. On a host whose `PATH` already leads with the
    managed venv the guard never fires and the gap stays invisible — Gate 9
    workers inherit the ambient `PATH`, which is where it surfaced.

    The symlink mirrors `tests/test_gate_contracts.py::_copy_gate_repository`;
    `.gitignore` keeps it out of the fixture's tracked content so candidate
    identity is unchanged.
    """
    managed = ROOT / ".venv"
    if managed.is_dir():
        (root / ".venv").symlink_to(managed.resolve(), target_is_directory=True)


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-b", "master"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "fixture@example.invalid"],
        cwd=root,
        check=True,
    )
    subprocess.run(["git", "config", "user.name", "Fixture"], cwd=root, check=True)
    # `.venv` without a trailing slash: the managed interpreter arrives as a
    # symlink, and a directory-only pattern would leave it tracked.
    (root / ".gitignore").write_text(".kickoff/\n.venv\n")
    link_managed_interpreter(root)
    (root / "projects").mkdir()
    (root / "policies").mkdir()
    (root / "CLAUDE.md").write_text("# Synthetic engine\n")
    (root / "phase.md").write_text("# Phase\n")
    (root / "policy.md").write_text("# Policy\n")
    (root / "candidate-partition.yaml").write_text(
        "schema: agentic.candidate-partition.v1\n"
        "active:\n"
        '  - "/candidate-partition.yaml"\n'
        '  - "/.gitignore"\n'
        '  - "/CLAUDE.md"\n'
        '  - "/phase.md"\n'
        '  - "/policy.md"\n'
        '  - "/code.py"\n'
        '  - "/tracked.txt"\n'
        '  - "/script"\n'
        '  - "/projects/**"\n'
        '  - "/policies/**"\n'
        '  - "/bin/**"\n'
        '  - "/lib/**"\n'
        '  - "/plan/**"\n'
        "bookkeeping:\n"
        '  - "/LOG*.md"\n'
        '  - "/EXECUTION_LOG.jsonl"\n'
        '  - "/plan/INDEX.md"\n'
        '  - "/lessons/**"\n'
        '  - "/lessons-archived/**"\n'
        '  - "/user-actions/**"\n'
        '  - "/user-actions-archived/**"\n'
    )

    (root / "code.py").write_text("VALUE = 1\n")
    (root / "bin").mkdir()
    (root / "bin" / "check").write_text("#!/bin/sh\nexit 0\n")
    (root / "bin" / "check").chmod(0o755)
    (root / "bin" / "check-catalogs").write_text("#!/bin/sh\nexit 0\n")
    (root / "bin" / "check-catalogs").chmod(0o755)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-m", "fixture"], cwd=root, check=True, capture_output=True)
    return root


def run(
    *arguments: str,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    executable = EVIDENCE
    if "--run-dir" in arguments and arguments[0] != "init":
        run_dir = Path(arguments[arguments.index("--run-dir") + 1])
        pinned = run_dir / "tools" / "kickoff-evidence"
        if pinned.is_file():
            executable = pinned
    return subprocess.run(
        [str(executable), *arguments],
        cwd=cwd or ROOT,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )


def open_role_dispatch(
    run_dir: Path,
    registration: Path,
    intelligence_span_id: str | None,
    *,
    dispatch_candidate: str | None = None,
) -> subprocess.CompletedProcess[str]:
    arguments = [
        "record-role-dispatch",
        "--run-dir",
        str(run_dir),
        "--registration",
        str(registration),
        "--state",
        "opened",
        "--idle-telemetry",
        "not-dispatched",
    ]
    if intelligence_span_id is not None:
        arguments.extend(["--intelligence-span-id", intelligence_span_id])
    if dispatch_candidate is not None:
        arguments.extend(["--dispatch-candidate", dispatch_candidate])
    return run(*arguments)


def initialize(
    repository: Path,
    run_dir: Path,
    *,
    review_lane: str = "full",
    evidence_lane: str = "full",
    follow_up_route: str = "direct-fix",
    authorities: tuple[str, ...] = ("phase.md::Acceptance", "policy.md"),
) -> str:
    receipt = run_dir.parent / f"{run_dir.name}-preflight.json"
    receipt.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "created_at": "2026-01-01T00:00:00+00:00",
                "config_sha256": hashlib.sha256((ROOT / "kickoff.yaml").read_bytes()).hexdigest(),
                "harness": "default",
                "targets": [],
            },
            sort_keys=True,
        )
        + "\n"
    )
    handle = start_trace(
        engine_root=repository,
        scope_root=repository,
        scope="engine",
        scope_id="engine",
        run_type="kickoff",
        operation="phase.1.1",
    )
    setup = start_span(
        engine_root=repository,
        trace_id=handle.trace_id,
        parent_span_id=handle.span_id,
        category="reconciliation",
        operation="orchestration.setup",
    )
    result = run(
        "init",
        "--run-dir",
        str(run_dir),
        "--root",
        str(repository),
        "--phase",
        "1.1",
        *[item for authority in authorities for item in ("--authority", authority)],
        "--telemetry-trace-id",
        handle.trace_id,
        "--telemetry-root-span-id",
        handle.span_id,
        "--initial-orchestration-span-id",
        setup.span_id,
        "--preflight-receipt",
        str(receipt),
        "--review-lane",
        review_lane,
        "--evidence-lane",
        evidence_lane,
        "--follow-up-route",
        follow_up_route,
    )
    assert result.returncode == 0, result.stderr
    manifest = run_dir.parent / f"{run_dir.name}-commands.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "commands": [
                    {
                        "operation": "gate.check-all",
                        "attempt": 1,
                        "final": True,
                        "argv": ["./bin/check", "all"],
                    },
                    {
                        "operation": "gate.focused",
                        "attempt": 1,
                        "final": False,
                        "argv": ["/usr/bin/true"],
                    },
                    {
                        "operation": "gate.check-all",
                        "attempt": 1,
                        "final": True,
                        "argv": ["/usr/bin/true"],
                    },
                ],
                "preflight_commands": [],
            },
            sort_keys=True,
        )
        + "\n"
    )
    activated = run(
        "activate-gate-manifest",
        "--run-dir",
        str(run_dir),
        "--manifest",
        str(manifest),
    )
    assert activated.returncode == 0, activated.stderr
    return result.stdout.strip()


def complete_orchestration(repository: Path, run_dir: Path) -> None:
    metadata = json.loads((run_dir / "run.json").read_text())
    trace_id = metadata["telemetry_trace_id"]
    root_span_id = metadata["telemetry_root_span_id"]
    finish_span(
        engine_root=repository,
        trace_id=trace_id,
        span_id=metadata["initial_orchestration_span_id"],
        outcome="success",
    )
    existing = closed_spans(
        engine_root=repository,
        trace_id=trace_id,
    )
    for operation in (
        "orchestration.planning",
        "orchestration.implementation",
        "orchestration.acceptance",
        "orchestration.close",
    ):
        if operation not in metadata["required_orchestration_operations"]:
            continue
        if any(
            span["operation"] == operation and span["outcome"] == "success" for span in existing
        ):
            continue
        stage = start_span(
            engine_root=repository,
            trace_id=trace_id,
            parent_span_id=root_span_id,
            category="reconciliation",
            operation=operation,
        )
        finish_span(
            engine_root=repository,
            trace_id=trace_id,
            span_id=stage.span_id,
            outcome="success",
        )
        existing.append(
            closed_span(
                engine_root=repository,
                trace_id=trace_id,
                span_id=stage.span_id,
            )
        )


def finding(
    finding_id: str,
    candidate: str,
    *,
    state: str = "open",
    classification: str = "initial",
    resolved_in: str | None = None,
) -> dict[str, object]:
    return {
        "id": finding_id,
        "severity": "high",
        "authority": "policy.md",
        "evidence": "Observed mismatch",
        "affected_paths": ["code.py"],
        "required_outcome": "Make the behavior exact",
        "introduced_in": candidate,
        "resolved_in": resolved_in,
        "state": state,
        "classification": classification,
        "disposition": None,
    }


def ingest(
    run_dir: Path,
    tmp_path: Path,
    findings: list[dict[str, object]],
    *,
    kind: str = "code",
    candidate: str | None = None,
    review_span_id: str | None = None,
) -> subprocess.CompletedProcess[str]:
    """Ingest findings for a test that is exercising something other than metrics.

    `--review-span-id` is required in production, but these cases have no
    dispatched review pass to name. They pass the explicit opt-out so the
    omission is recorded rather than silent -- which is the whole point of the
    flag. Tests that care about convergence metrics pass `review_span_id`.
    """
    input_path = tmp_path / "findings-input.json"
    input_path.write_text(json.dumps({"findings": findings}))
    expected_candidate = candidate or str(
        findings[0]["resolved_in"] or findings[0]["introduced_in"]
    )
    metrics_argv = (
        ["--review-span-id", review_span_id]
        if review_span_id
        else ["--no-review-span", "test fixture: no review pass was dispatched"]
    )
    return run(
        "ingest-findings",
        "--run-dir",
        str(run_dir),
        "--kind",
        kind,
        "--candidate",
        expected_candidate,
        "--input",
        str(input_path),
        *metrics_argv,
    )


def capture(repository: Path, run_dir: Path) -> str:
    result = run(
        "capture-change",
        "--run-dir",
        str(run_dir),
        "--risk-tag",
        "public-api",
        "--test",
        "./bin/test focused",
        "--unchanged",
        "policy.md",
        "--selection-reason",
        "Exercises the changed behavior",
        cwd=repository,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def tree_manifest_for_test(repository: Path) -> str:
    result = subprocess.run(
        [str(TREE_ID), "--root", str(repository), "--product", "--json"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)["candidate_id"]


def run_final_gate(run_dir: Path, candidate: str, artifact: Path | None = None):
    repository = Path(json.loads((run_dir / "run.json").read_text())["repository_root"])
    complete_orchestration(repository, run_dir)
    arguments = [
        "run-gate",
        "--run-dir",
        str(run_dir),
        "--candidate",
        candidate,
        "--operation",
        "gate.check-all",
        "--attempt",
        "1",
        "--selection-reason",
        "Authoritative acceptance close",
        "--warning-count",
        "0",
    ]
    if artifact is not None:
        arguments.extend(["--artifact", str(artifact)])
    arguments.extend(["--final", "--", "./bin/check", "all"])
    return run(
        *arguments,
        cwd=repository,
    )


def test_change_manifest_is_candidate_bound_and_detects_authority_drift(
    repository: Path, tmp_path: Path
) -> None:
    custody_dir = tmp_path / "custody"
    custody_dir.mkdir()
    custody_repository = custody_dir / "repo"
    shutil.copytree(repository, custody_repository)
    _assert_bookkeeping_review_custody(custody_repository, custody_dir)
    run_dir = tmp_path / "run"
    reviewed = initialize(repository, run_dir)
    assert len(reviewed) == 64
    assert json.loads((run_dir / "run.json").read_text())["phase"] == "1.1"
    authority = json.loads((run_dir / "authority.json").read_text())
    assert [item["path"] for item in authority["authorities"]] == [
        "phase.md",
        "policy.md",
    ]
    assert (run_dir / "reviewed-candidate.json").is_file()
    assert (run_dir / "findings.json").is_file()
    assert (run_dir / "gates.jsonl").is_file()

    active_digest = json.loads((run_dir / "gate-manifests.jsonl").read_text())["manifest_sha256"]
    original_manifest = json.loads((tmp_path / "run-commands.json").read_text())
    successor = tmp_path / "successor-commands.json"
    successor_document = dict(original_manifest)
    successor_document["commands"] = [
        {
            "operation": "gate.check-all",
            "attempt": 2,
            "final": True,
            "argv": ["./bin/check", "all"],
        }
    ]
    successor.write_text(json.dumps(successor_document, sort_keys=True) + "\n")
    refused = run(
        "activate-gate-manifest",
        "--run-dir",
        str(run_dir),
        "--manifest",
        str(successor),
    )
    assert refused.returncode != 0
    assert f"must pass --supersedes {active_digest}" in refused.stderr
    replaced = run(
        "activate-gate-manifest",
        "--run-dir",
        str(run_dir),
        "--manifest",
        str(successor),
        "--supersedes",
        active_digest,
    )
    assert replaced.returncode == 0, replaced.stderr

    (repository / "code.py").write_text("VALUE = 2\n")
    (repository / "new.py").write_text("NEW = True\n")
    candidate = capture(repository, run_dir)

    change = json.loads((run_dir / "change.json").read_text())
    assert change["reviewed_candidate_id"] == reviewed
    assert change["candidate_id"] == candidate
    assert [(item["path"], item["change"]) for item in change["changed_files"]] == [
        ("code.py", "modified"),
        ("new.py", "added"),
    ]
    assert change["risk_tags"] == ["public-api"]
    assert not change["rebase_required"]

    (repository / "policy.md").write_text("# Changed policy\n")
    capture(repository, run_dir)
    changed = json.loads((run_dir / "change.json").read_text())
    assert changed["rebase_required"]
    assert changed["authority_drift"][0]["path"] == "policy.md"


def test_finding_state_is_stable_validated_and_reopen_is_counted(
    repository: Path, tmp_path: Path
) -> None:
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    result = ingest(run_dir, tmp_path, [finding("CODE-F001", candidate)])
    assert result.returncode == 0, result.stderr

    addressed = finding("CODE-F001", candidate, state="addressed")
    result = ingest(run_dir, tmp_path, [addressed])
    assert result.returncode == 0, result.stderr

    verified = finding(
        "CODE-F001",
        candidate,
        state="verified",
        resolved_in=candidate,
    )
    assert ingest(run_dir, tmp_path, [verified]).returncode == 0
    closed = finding(
        "CODE-F001",
        candidate,
        state="closed",
        resolved_in=candidate,
    )
    assert ingest(run_dir, tmp_path, [closed]).returncode == 0
    reopened = finding(
        "CODE-F001",
        candidate,
        state="open",
        classification="newly-exposed-by-resolution",
    )
    assert ingest(run_dir, tmp_path, [reopened]).returncode == 0

    ledger = json.loads((run_dir / "findings.json").read_text())
    assert ledger["reopened_count"] == 1
    assert ledger["findings"][0]["state"] == "open"


def test_role_artifacts_feed_findings_and_change_metadata_without_reparsing(
    repository: Path, tmp_path: Path
) -> None:
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    review_artifact = tmp_path / "review.md"
    review_artifact.write_text(
        "## Finding Evidence\n```json\n"
        + json.dumps({"findings": [finding("CODE-F001", candidate)]})
        + "\n```\n\n## Verdict: REVISE\n"
    )

    review = run(
        "ingest-findings",
        "--run-dir",
        str(run_dir),
        "--kind",
        "code",
        "--candidate",
        candidate,
        "--no-review-span",
        "test fixture: no review pass was dispatched",
        "--artifact",
        str(review_artifact),
    )
    assert review.returncode == 0, review.stderr

    (repository / "code.py").write_text("VALUE = 2\n")
    coder_artifact = tmp_path / "coder.md"
    coder_artifact.write_text(
        "### Change Evidence\n```json\n"
        + json.dumps(
            {
                "risk_tags": ["public-api"],
                "selected_tests": ["./bin/test focused"],
                "selection_reason": "Exercises the public behavior",
                "intentionally_unchanged": ["policy.md"],
                "rebase_reasons": [],
                "failure_analysis": "",
                "falsifiers": [],
                "gate_status": {"focused": "green", "reason": ""},
            }
        )
        + "\n```\n"
    )
    change = run(
        "capture-change",
        "--run-dir",
        str(run_dir),
        "--metadata-artifact",
        str(coder_artifact),
    )
    assert change.returncode == 0, change.stderr
    manifest = json.loads((run_dir / "change.json").read_text())
    assert manifest["risk_tags"] == ["public-api"]
    assert manifest["selection_reason"] == "Exercises the public behavior"


def test_revision_round_requires_and_carries_failure_analysis(
    repository: Path, tmp_path: Path
) -> None:
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    (repository / "code.py").write_text("VALUE = 2\n")
    first_candidate = capture(repository, run_dir)
    marked = run(
        "mark-reviewed",
        "--run-dir",
        str(run_dir),
        "--expected-candidate",
        first_candidate,
        cwd=repository,
    )
    assert marked.returncode == 0, marked.stderr

    (repository / "code.py").write_text("VALUE = 3\n")
    without_analysis = run(
        "capture-change",
        "--run-dir",
        str(run_dir),
        "--risk-tag",
        "public-api",
        "--test",
        "./bin/test focused",
        "--selection-reason",
        "Exercises the revised behavior",
        cwd=repository,
    )
    assert without_analysis.returncode == 2
    assert "failure_analysis must be nonempty on a revision round" in without_analysis.stderr

    analysis = "Initial fix patched the symptom; the guard belonged one call earlier."
    with_analysis = run(
        "capture-change",
        "--run-dir",
        str(run_dir),
        "--risk-tag",
        "public-api",
        "--test",
        "./bin/test focused",
        "--selection-reason",
        "Exercises the revised behavior",
        "--failure-analysis",
        analysis,
        cwd=repository,
    )
    assert with_analysis.returncode == 0, with_analysis.stderr
    revised_candidate = with_analysis.stdout.strip()
    assert json.loads((run_dir / "change.json").read_text())["failure_analysis"] == analysis

    assert (
        ingest(
            run_dir,
            tmp_path,
            [finding("CODE-F001", revised_candidate)],
            candidate=revised_candidate,
        ).returncode
        == 0
    )
    output = tmp_path / "revision-packet.md"
    packet = run(
        "packet",
        "--run-dir",
        str(run_dir),
        "--kind",
        "code",
        "--output",
        str(output),
    )
    assert packet.returncode == 0, packet.stderr
    text = output.read_text()
    assert "## Failure analysis" in text
    assert analysis in text


@pytest.mark.parametrize("state", ["open", "addressed", "blocked-owner"])
def test_final_validation_rejects_blocking_findings(
    repository: Path,
    tmp_path: Path,
    state: str,
) -> None:
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    item = finding("CODE-F001", candidate, state=state)
    assert ingest(run_dir, tmp_path, [item]).returncode == 0
    assert run_final_gate(run_dir, candidate).returncode == 0
    complete_orchestration(repository, run_dir)

    result = run(
        "validate",
        "--run-dir",
        str(run_dir),
        "--level",
        "acceptance",
        "--required-final-command",
        "./bin/check all",
    )

    assert result.returncode == 2
    assert "phase-close findings remain unresolved: CODE-F001" in result.stderr


def test_validate_detects_corrupt_evidence(repository: Path, tmp_path: Path) -> None:
    _assert_failed_close_is_truthful_terminal_and_idempotent(repository, tmp_path)
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    valid = run("validate", "--run-dir", str(run_dir))
    assert valid.returncode == 0, valid.stderr
    assert "EVIDENCE VALID" in valid.stdout

    (run_dir / "findings.json").write_text("{broken")
    invalid = run("validate", "--run-dir", str(run_dir))
    assert invalid.returncode == 2
    assert "invalid JSON" in invalid.stderr


def _assert_failed_close_is_truthful_terminal_and_idempotent(
    repository: Path, tmp_path: Path
) -> None:
    run_dir = tmp_path / "failed-run"
    initialize(repository, run_dir, follow_up_route="full-cycle")
    status = run("status", "--run-dir", str(run_dir))
    assert status.returncode == 0, status.stderr
    observed = json.loads(status.stdout)
    assert observed["missing_acceptance_role_operations"]
    assert run("validate", "--run-dir", str(run_dir), "--level", "integrity").returncode == 0
    acceptance = run("validate", "--run-dir", str(run_dir), "--level", "acceptance")
    assert acceptance.returncode == 2
    assert "missing required initial role attempt" in acceptance.stderr

    metadata = json.loads((run_dir / "run.json").read_text())
    failure = {
        "affected_contract": "phase acceptance",
        "causal_generator": "run stopped before required roles completed",
        "execution_boundary": "role dispatch",
        "failed_operation": "phase.1.1",
        "novelty": "known",
        "park_id": "a" * 32,
        "phase": "1.1",
        "remaining_budget": 0,
        "resume_permitted": False,
        "resume_refusal_reason": "operator decision required",
        "self_resume_consumed": False,
        "terminal_condition": "run cannot accept",
        "trace_id": metadata["telemetry_trace_id"],
    }
    failure_path = tmp_path / "failed-close.json"
    failure_path.write_text(json.dumps(failure) + "\n")
    log_text = "## 2026-01-01 10:00 — PARK\n\nPhase 1.1 — failed\n"
    log_block = tmp_path / "failed-close.md"
    log_block.write_text(log_text)
    arguments = (
        "close",
        "--run-dir",
        str(run_dir),
        "--outcome",
        "failed",
        "--reason-code",
        "required-roles-missing",
        "--log-block",
        str(log_block),
        "--failure-record",
        str(failure_path),
    )
    first = run(*arguments)
    second = run(*arguments)
    assert first.returncode == second.returncode == 0, first.stderr + second.stderr
    assert (repository / "LOG.md").read_text().count(log_text) == 1
    rows = [
        json.loads(line)
        for line in (repository / ".kickoff" / "failure-signatures.jsonl").read_text().splitlines()
    ]
    assert rows == [failure]
    closure = json.loads((run_dir / "closure.json").read_text())
    assert closure["status"] == "complete" and closure["outcome"] == "failed"


def test_complete_synthetic_kickoff_cross_validates_roles_revision_and_gates(
    repository: Path, tmp_path: Path
) -> None:
    root = start_trace(
        engine_root=repository,
        scope_root=repository,
        scope="engine",
        scope_id="engine",
        run_type="kickoff",
        operation="phase.1.1",
    )
    setup = start_span(
        engine_root=repository,
        trace_id=root.trace_id,
        parent_span_id=root.span_id,
        category="reconciliation",
        operation="orchestration.setup",
    )
    run_dir = tmp_path / "run"
    receipt = tmp_path / "preflight.json"
    receipt.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "created_at": "2026-01-01T00:00:00+00:00",
                "config_sha256": hashlib.sha256((ROOT / "kickoff.yaml").read_bytes()).hexdigest(),
                "harness": "default",
                "targets": [],
            },
            sort_keys=True,
        )
        + "\n"
    )
    initialized = run(
        "init",
        "--run-dir",
        str(run_dir),
        "--root",
        str(repository),
        "--phase",
        "1.1",
        "--authority",
        "phase.md",
        "--telemetry-trace-id",
        root.trace_id,
        "--telemetry-root-span-id",
        root.span_id,
        "--initial-orchestration-span-id",
        setup.span_id,
        "--preflight-receipt",
        str(receipt),
        "--review-lane",
        "full",
        "--evidence-lane",
        "full",
        "--follow-up-route",
        "initial",
    )
    assert initialized.returncode == 0, initialized.stderr
    gate_manifest = tmp_path / "gate-manifest.json"
    gate_manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "commands": [
                    {
                        "operation": "gate.check-all",
                        "attempt": 1,
                        "final": True,
                        "argv": ["./bin/check", "all"],
                    },
                    {
                        "operation": "gate.focused",
                        "attempt": 1,
                        "final": False,
                        "argv": ["/usr/bin/true"],
                    },
                    {
                        "operation": "gate.check-all",
                        "attempt": 1,
                        "final": True,
                        "argv": ["/usr/bin/true"],
                    },
                ],
                "preflight_commands": [],
            },
            sort_keys=True,
        )
        + "\n"
    )
    activated = run(
        "activate-gate-manifest",
        "--run-dir",
        str(run_dir),
        "--manifest",
        str(gate_manifest),
    )
    assert activated.returncode == 0, activated.stderr

    def role_attempt(
        operation: str,
        role: str,
        harness: str,
        attempt: int,
        reason: str,
        outcome: str = "success",
        exit_code: int = 0,
        model: str | None = None,
        effort: str | None = None,
    ) -> None:
        handoff = run_dir / f"{operation}-{attempt}.json"
        arguments = [
            "register-role-attempt",
            "--run-dir",
            str(run_dir),
            "--operation",
            operation,
            "--attempt",
            str(attempt),
            "--role",
            role,
            "--harness",
            harness,
            "--reason",
            reason,
            "--output",
            str(handoff),
        ]
        if model:
            arguments.extend(["--model", model])
        if effort:
            arguments.extend(["--effort", effort])
        registered = run(*arguments)
        assert registered.returncode == 0, registered.stderr
        if harness in {"claude", "codex"}:
            executable = tmp_path / harness
            event = (
                '{"type":"result","result":"OK"}'
                if harness == "claude"
                else '{"type":"turn.completed"}'
            )
            artifact = tmp_path / f"{operation}-{attempt}-artifact.txt"
            populate = "" if harness == "claude" else f"printf '%s' 'CODEX' > {artifact}\n"
            executable.write_text(
                f"#!/bin/sh\nprintf '%s\\n' '{event}'\n{populate}exit {exit_code}\n"
            )
            executable.chmod(0o755)
            prompt = tmp_path / f"{operation}-{attempt}-prompt.md"
            prompt.write_text("Adopt your canonical persona and report.\n")
            artifact_flag = "--result-file" if harness == "claude" else "--required-output-file"
            watcher_arguments = [
                UV,
                "run",
                "--script",
                str(run_dir / "tools" / "kickoff-config"),
                "watch",
                "--role",
                role,
                "--venue",
                harness,
                "--model",
                model or harness,
                "--effort",
                effort or "default",
                "--phase",
                "1.1",
                "--prompt-file",
                str(prompt),
                artifact_flag,
                str(artifact),
                "--first-event-timeout",
                "2",
                "--idle-timeout",
                "2",
                "--hard-timeout",
                "2",
                "--telemetry-trace-id",
                root.trace_id,
                "--telemetry-parent-span-id",
                root.span_id,
                "--telemetry-operation",
                operation,
                "--telemetry-attempt",
                str(attempt),
                "--telemetry-role-registration",
                str(handoff),
            ]
            watched = subprocess.run(
                watcher_arguments,
                cwd=repository,
                env={
                    **os.environ,
                    f"KICKOFF_CLI_{harness.upper()}": str(executable),
                },
                capture_output=True,
                text=True,
                check=False,
            )
            assert watched.returncode == exit_code, watched.stderr
            return
        metadata = {"role": role, "harness": harness}
        if model:
            metadata["model"] = model
        if effort:
            metadata["effort"] = effort
        intelligence = start_span(
            engine_root=repository,
            trace_id=root.trace_id,
            parent_span_id=root.span_id,
            category="intelligence",
            operation=operation,
            attempt=attempt,
            **metadata,
        )
        opened = open_role_dispatch(run_dir, handoff, intelligence.span_id)
        assert opened.returncode == 0, opened.stderr
        wait = start_span(
            engine_root=repository,
            trace_id=root.trace_id,
            parent_span_id=intelligence.span_id,
            category="wait",
            operation=operation,
            attempt=attempt,
            **metadata,
        )
        finish_span(
            engine_root=repository,
            trace_id=root.trace_id,
            span_id=wait.span_id,
            outcome=outcome,
            exit_code=exit_code,
        )
        finish_span(
            engine_root=repository,
            trace_id=root.trace_id,
            span_id=intelligence.span_id,
            outcome=outcome,
            exit_code=exit_code,
        )
        dispatched = run(
            "record-role-dispatch",
            "--run-dir",
            str(run_dir),
            "--registration",
            str(handoff),
            "--state",
            "accepted",
            "--idle-telemetry",
            ("unavailable" if harness == "native" else "available"),
            "--intelligence-span-id",
            intelligence.span_id,
            "--wait-span-id",
            wait.span_id,
        )
        assert dispatched.returncode == 0, dispatched.stderr

    role_attempt(
        "role.plan",
        "planner",
        "claude",
        1,
        "initial",
        outcome="error",
        exit_code=1,
        model="opus",
        effort="high",
    )
    role_attempt(
        "role.plan",
        "planner",
        "claude",
        2,
        "revision",
        model="opus",
        effort="high",
    )
    role_attempt("role.plan-review", "reviewer", "native", 1, "initial")
    role_attempt("role.implement", "coder", "native", 1, "initial")
    role_attempt(
        "role.code-review",
        "critic",
        "codex",
        1,
        "initial",
        model="sol",
        effort="high",
    )
    dispatches = [
        dispatch
        for line in (run_dir / "role-dispatch.jsonl").read_text().splitlines()
        for dispatch in [json.loads(line)]
        if dispatch.get("state") != "opened"
    ]
    for dispatch in dispatches:
        if dispatch["operation"] in {"role.plan-review", "role.code-review"}:
            attach_review_metrics(
                engine_root=repository,
                trace_id=root.trace_id,
                span_id=dispatch["intelligence_span_id"],
                findings_reported=0,
                actionable_findings=0,
            )
    assert len(dispatches) == 5
    assert sum(item["idle_telemetry"] == "available" for item in dispatches) == 3
    assert sum(item["idle_telemetry"] == "unavailable" for item in dispatches) == 2
    candidate = tree_manifest_for_test(repository)
    focused = run(
        "run-gate",
        "--run-dir",
        str(run_dir),
        "--candidate",
        candidate,
        "--operation",
        "gate.focused",
        "--selection-reason",
        "focused proof",
        "--warning-count",
        "0",
        "--",
        "/usr/bin/true",
        cwd=repository,
    )
    assert focused.returncode == 0, focused.stderr
    complete_orchestration(repository, run_dir)
    artifact = tmp_path / "gate.txt"
    artifact.write_text("PASS\n")
    final = run(
        "run-gate",
        "--run-dir",
        str(run_dir),
        "--candidate",
        candidate,
        "--operation",
        "gate.check-all",
        "--selection-reason",
        "final proof",
        "--warning-count",
        "0",
        "--artifact",
        str(artifact),
        "--final",
        "--",
        "/usr/bin/true",
        cwd=repository,
    )
    assert final.returncode == 0, final.stderr
    gates = [json.loads(line) for line in (run_dir / "gates.jsonl").read_text().splitlines()]
    assert gates[-1]["artifact_sha256"] == hashlib.sha256(artifact.read_bytes()).hexdigest()
    assert gates[-1]["final"]
    validated = run(
        "validate",
        "--run-dir",
        str(run_dir),
        "--level",
        "acceptance",
        "--required-final-command",
        "/usr/bin/true",
    )
    assert validated.returncode == 0, validated.stderr
    finish_span(
        engine_root=repository,
        trace_id=root.trace_id,
        span_id=root.span_id,
        outcome="success",
    )
    finalize_trace(engine_root=repository, trace_id=root.trace_id)
    json_summary = run("timing-summary", "--run-dir", str(run_dir), "--format", "json")
    markdown = run("timing-summary", "--run-dir", str(run_dir), "--format", "markdown")
    assert json_summary.returncode == markdown.returncode == 0
    projection = json.loads(json_summary.stdout)
    assert projection["retry_ns"] > 0
    assert projection["failed_ns"] > 0
    for slow in projection["slowest_spans"]:
        assert slow["operation"] in markdown.stdout

    close_text = "## 2026-01-01 10:00 — END\n\nPhase 1.1 — accepted\n"
    close_block = tmp_path / "accepted-close.md"
    close_block.write_text(close_text)
    close_arguments = (
        "close",
        "--run-dir",
        str(run_dir),
        "--outcome",
        "accepted",
        "--reason-code",
        "all-gates-green",
        "--log-block",
        str(close_block),
        "--required-final-command",
        "/usr/bin/true",
    )
    closed = run(*close_arguments)
    repeated = run(*close_arguments)
    assert closed.returncode == repeated.returncode == 0, closed.stderr + repeated.stderr
    assert (repository / "LOG.md").read_text().count(close_text) == 1
    closure = json.loads((run_dir / "closure.json").read_text())
    assert closure["status"] == "complete" and closure["outcome"] == "accepted"

    (repository / "code.py").write_text("VALUE = 2\n")
    stale = run(
        "record-gate",
        "--run-dir",
        str(run_dir),
        "--candidate",
        candidate,
        "--selection-reason",
        "Final authoritative gate",
        "--exit-code",
        "0",
        "--warning-count",
        "0",
        "--",
        "./bin/check",
        "all",
    )
    assert stale.returncode == 2
    assert "candidate mismatch" in stale.stderr


REVIEWER_PERSONAS = (
    ".claude/agents/plan-reviewer.md",
    ".claude/agents/code-critic.md",
)


# --- The pre-finalization latch and the derived-metrics overlay ----------------
#
# Two halves of one contract. The latch refuses an unmeasured review pass while
# the trace is still open, which is the only window in which an honest re-ingest
# can repair it. The overlay is the sanctioned recovery for the residue the
# latch cannot reach: a pass that really succeeded, whose batch was structurally
# refused, discovered after the trace closed.


def review_artifact(path: Path, findings: list[dict[str, object]], **extra: object) -> Path:
    """A critic artifact in the markdown envelope the native venues emit."""
    document: dict[str, object] = {"verdict": "REVISE", "findings": findings, **extra}
    path.write_text(
        "## Finding Evidence\n```json\n" + json.dumps(document) + "\n```\n\n## Verdict: REVISE\n",
        encoding="utf-8",
    )
    return path


def ingest_artifact(
    run_dir: Path, candidate: str, artifact: Path, span_id: str
) -> subprocess.CompletedProcess[str]:
    return run(
        "ingest-findings",
        "--run-dir",
        str(run_dir),
        "--kind",
        "code",
        "--candidate",
        candidate,
        "--review-span-id",
        span_id,
        "--artifact",
        str(artifact),
    )


# --- Candidate drift under an in-flight dispatch ------------------------------
#
# `kickoff-tree-id` hashes nonignored untracked files, so any write by any
# session moves the candidate. The three acceptance checks below are exercised
# for independence on purpose: each of the first three tests constructs a drift
# that passes the other two checks and fails only its own, because a layered
# rule whose layers are never isolated is one check plus two decorations.


DRIFT_MARKERS = ("drift-partition:", "drift-reviewed-surface:", "drift-authority:")


def write_repo_file(repository: Path, relative: str, text: str) -> None:
    target = repository / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def dispatch_rows(run_dir: Path) -> list[dict[str, object]]:
    return [
        row
        for line in (run_dir / "role-dispatch.jsonl").read_text().splitlines()
        if line.strip()
        for row in [json.loads(line)]
        if row.get("state") != "opened"
    ]


def drifting_attempt(
    repository: Path,
    run_dir: Path,
    mutate,
    *,
    operation: str = "role.code-review",
    role: str = "critic",
    attempt: int = 1,
    accepted: bool = True,
    record_open_candidate: bool = True,
) -> tuple[str, str, str]:
    """One dispatch whose tree moved between dispatch-open and dispatch-return.

    Returns `(dispatch candidate, return candidate, intelligence span id)`.
    """
    metadata = json.loads((run_dir / "run.json").read_text())
    trace_id = metadata["telemetry_trace_id"]
    root_span_id = metadata["telemetry_root_span_id"]
    handoff = run_dir / f"{operation}-{attempt}.json"
    registered = run(
        "register-role-attempt",
        "--run-dir",
        str(run_dir),
        "--operation",
        operation,
        "--attempt",
        str(attempt),
        "--role",
        role,
        "--harness",
        "native",
        "--reason",
        "initial",
        "--output",
        str(handoff),
    )
    assert registered.returncode == 0, registered.stderr
    opened = run("current-candidate", "--run-dir", str(run_dir), "--reason", "dispatch")
    assert opened.returncode == 0, opened.stderr
    dispatch_candidate = opened.stdout.strip()
    intelligence = start_span(
        engine_root=repository,
        trace_id=trace_id,
        parent_span_id=root_span_id,
        category="intelligence",
        operation=operation,
        attempt=attempt,
        role=role,
        harness="native",
    )
    dispatch_opened = open_role_dispatch(
        run_dir,
        handoff,
        intelligence.span_id,
        dispatch_candidate=(dispatch_candidate if record_open_candidate else None),
    )
    assert dispatch_opened.returncode == 0, dispatch_opened.stderr
    wait = start_span(
        engine_root=repository,
        trace_id=trace_id,
        parent_span_id=intelligence.span_id,
        category="wait",
        operation=operation,
        attempt=attempt,
        role=role,
        harness="native",
    )
    mutate(repository)
    for span_id in (wait.span_id, intelligence.span_id):
        finish_span(
            engine_root=repository,
            trace_id=trace_id,
            span_id=span_id,
            outcome="success",
            exit_code=0,
        )
    arguments = [
        "record-role-dispatch",
        "--run-dir",
        str(run_dir),
        "--registration",
        str(handoff),
        "--state",
        "accepted" if accepted else "rejected",
        "--idle-telemetry",
        "unavailable" if accepted else "not-dispatched",
        "--intelligence-span-id",
        intelligence.span_id,
    ]
    if accepted:
        arguments.extend(["--wait-span-id", wait.span_id])
    dispatched = run(*arguments)
    assert dispatched.returncode == 0, dispatched.stderr
    row = [
        item
        for item in dispatch_rows(run_dir)
        if item["operation"] == operation and item["attempt"] == attempt
    ][0]
    return dispatch_candidate, str(row["return_candidate_id"]), intelligence.span_id


def add_lesson(repository: Path) -> None:
    write_repo_file(repository, "lessons/silent-guard-drift.md", "# Lesson\n")


def stale_batch(tmp_path: Path, dispatch: str, name: str = "critic.md") -> Path:
    """A critic batch stamped with the candidate the critic was dispatched at."""
    return review_artifact(
        tmp_path / name,
        [
            finding(
                "CODE-F002",
                dispatch,
                state="rejected-with-evidence",
                resolved_in=dispatch,
            )
        ],
    )


def _assert_bookkeeping_review_custody(repository: Path, tmp_path: Path) -> None:
    """Bookkeeping preserves review identity without an exception ledger."""
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    dispatch, returned, span_id = drifting_attempt(repository, run_dir, add_lesson)
    assert dispatch == returned
    assert not (run_dir / "candidate-drift.jsonl").exists()
    assert (
        ingest_artifact(run_dir, returned, stale_batch(tmp_path, dispatch), span_id).returncode == 0
    )
    assert run("validate", "--run-dir", str(run_dir)).returncode == 0
    assert "accept-candidate-drift" not in run("--help").stdout
    # The same pass cannot hide an active edit behind an old resolution stamp.
    (repository / "code.py").write_text("VALUE = 2\n")
    current = run(
        "current-candidate", "--run-dir", str(run_dir), "--reason", "active edit"
    ).stdout.strip()
    assert current != returned
    refused = ingest_artifact(run_dir, current, stale_batch(tmp_path, dispatch), span_id)
    assert refused.returncode == 2
    assert "resolved_in does not match" in refused.stderr
    # Even bookkeeping is protected when it is explicitly reviewed.
    captured = capture(repository, run_dir)
    assert captured == current
    reviewed = finding("CODE-F003", current, state="rejected-with-evidence", resolved_in=current)
    reviewed["affected_paths"] = ["lessons/silent-guard-drift.md"]
    assert ingest(run_dir, tmp_path, [reviewed], candidate=current).returncode == 0
    (repository / "lessons/silent-guard-drift.md").write_text("changed after review\n")
    protected = run("validate", "--run-dir", str(run_dir))
    assert protected.returncode == 2
    assert "reviewed bookkeeping changed" in protected.stderr

    marked = run("mark-reviewed", "--run-dir", str(run_dir), "--expected-candidate", current)
    assert marked.returncode == 2
    assert "reviewed bookkeeping changed" in marked.stderr

    # A gate that changes only bookkeeping still fails its full-tree custody check.
    (repository / "bin/check").write_text("#!/bin/sh\nprintf 'gate mutation\\n' >> LOG.md\n")
    gate_dir = tmp_path / "mutating-gate"
    gate_candidate = initialize(repository, gate_dir, evidence_lane="light")
    gate_result = run(
        "run-gate",
        "--run-dir",
        str(gate_dir),
        "--candidate",
        gate_candidate,
        "--operation",
        "gate.check-all",
        "--attempt",
        "1",
        "--final",
        "--selection-reason",
        "prove bookkeeping cannot hide gate mutation",
        "--warning-count",
        "0",
        "--",
        "./bin/check",
        "all",
    )
    assert gate_result.returncode == 2, gate_result.stderr
    gate_row = json.loads((gate_dir / "gates.jsonl").read_text())
    assert gate_row["candidate_id"] != gate_row["candidate_after_id"]
    assert gate_row["product_candidate_id"] == gate_row["product_candidate_after_id"]

    # Explicitly declared bookkeeping authority is independently protected.
    authority_dir = tmp_path / "bookkeeping-authority"
    initialize(repository, authority_dir, authorities=("phase.md", "LOG.md"))
    with (repository / "LOG.md").open("a") as log:
        log.write("changed declared authority\n")
    refused_authority = run("validate", "--run-dir", str(authority_dir))
    assert refused_authority.returncode == 2
    assert "reviewed bookkeeping changed" in refused_authority.stderr
