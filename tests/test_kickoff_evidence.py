"""Behavioral tests for run-scoped kickoff evidence."""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import runpy
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
    (root / "code.py").write_text("VALUE = 1\n")
    (root / "bin").mkdir()
    (root / "bin" / "check").write_text("#!/bin/sh\nexit 0\n")
    (root / "bin" / "check").chmod(0o755)
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


def lineage_of(run_dir: Path) -> list[str]:
    return [
        json.loads(line)["candidate_id"]
        for line in (run_dir / "lineage.jsonl").read_text().splitlines()
        if line.strip()
    ]


def initialize(
    repository: Path,
    run_dir: Path,
    *,
    review_lane: str = "full",
    evidence_lane: str = "full",
    follow_up_route: str = "direct-fix",
    authorities: tuple[str, ...] = ("phase.md::Acceptance", "policy.md"),
) -> str:
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
        "--review-lane",
        review_lane,
        "--evidence-lane",
        evidence_lane,
        "--follow-up-route",
        follow_up_route,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def native_accepted_attempt(
    repository: Path,
    run_dir: Path,
    operation: str,
    role: str,
    attempt: int,
    *,
    reason: str = "initial",
) -> str:
    """Register, span, and record one accepted native role attempt.

    Returns the intelligence span id so review attempts can attach
    convergence metrics afterwards.
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
        reason,
        "--output",
        str(handoff),
    )
    assert registered.returncode == 0, registered.stderr
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
    opened = open_role_dispatch(run_dir, handoff, intelligence.span_id)
    assert opened.returncode == 0, opened.stderr
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
    finish_span(
        engine_root=repository,
        trace_id=trace_id,
        span_id=wait.span_id,
        outcome="success",
        exit_code=0,
    )
    finish_span(
        engine_root=repository,
        trace_id=trace_id,
        span_id=intelligence.span_id,
        outcome="success",
        exit_code=0,
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
        "unavailable",
        "--intelligence-span-id",
        intelligence.span_id,
        "--wait-span-id",
        wait.span_id,
    )
    assert dispatched.returncode == 0, dispatched.stderr
    return intelligence.span_id


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
        [str(TREE_ID), "--root", str(repository), "--json"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)["candidate_id"]


def run_final_gate(run_dir: Path, candidate: str, artifact: Path | None = None):
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
        *arguments, cwd=Path(json.loads((run_dir / "run.json").read_text())["repository_root"])
    )


def test_init_creates_complete_run_scoped_evidence(repository: Path, tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)

    assert len(candidate) == 64
    assert json.loads((run_dir / "run.json").read_text())["phase"] == "1.1"
    authority = json.loads((run_dir / "authority.json").read_text())
    assert [item["path"] for item in authority["authorities"]] == [
        "phase.md",
        "policy.md",
    ]
    assert (run_dir / "reviewed-candidate.json").is_file()
    assert (run_dir / "findings.json").is_file()
    assert (run_dir / "gates.jsonl").is_file()


def test_init_refuses_reused_nonempty_run_directory(repository: Path, tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "stale").write_text("old")

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
        "--authority",
        "phase.md",
        "--telemetry-trace-id",
        handle.trace_id,
        "--telemetry-root-span-id",
        handle.span_id,
        "--initial-orchestration-span-id",
        setup.span_id,
        "--review-lane",
        "full",
        "--evidence-lane",
        "full",
        "--follow-up-route",
        "direct-fix",
    )

    assert result.returncode == 2
    assert "not empty" in result.stderr


def test_change_manifest_is_candidate_bound_and_detects_authority_drift(
    repository: Path, tmp_path: Path
) -> None:
    run_dir = tmp_path / "run"
    reviewed = initialize(repository, run_dir)
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


def test_finding_ingestion_attaches_review_convergence_metrics(
    repository: Path, tmp_path: Path
) -> None:
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    metadata = json.loads((run_dir / "run.json").read_text())
    registration = run_dir / "review.json"
    registered = run(
        "register-role-attempt",
        "--run-dir",
        str(run_dir),
        "--operation",
        "role.plan-review",
        "--attempt",
        "1",
        "--role",
        "reviewer",
        "--harness",
        "native",
        "--reason",
        "initial",
        "--output",
        str(registration),
    )
    assert registered.returncode == 0, registered.stderr
    review = start_span(
        engine_root=repository,
        trace_id=metadata["telemetry_trace_id"],
        parent_span_id=metadata["telemetry_root_span_id"],
        category="intelligence",
        operation="role.plan-review",
        role="reviewer",
        harness="native",
    )
    opened = open_role_dispatch(run_dir, registration, review.span_id)
    assert opened.returncode == 0, opened.stderr
    wait = start_span(
        engine_root=repository,
        trace_id=metadata["telemetry_trace_id"],
        parent_span_id=review.span_id,
        category="wait",
        operation="role.plan-review",
        role="reviewer",
        harness="native",
    )
    finish_span(
        engine_root=repository,
        trace_id=metadata["telemetry_trace_id"],
        span_id=wait.span_id,
        outcome="success",
        exit_code=0,
    )
    finish_span(
        engine_root=repository,
        trace_id=metadata["telemetry_trace_id"],
        span_id=review.span_id,
        outcome="success",
        exit_code=0,
    )
    dispatched = run(
        "record-role-dispatch",
        "--run-dir",
        str(run_dir),
        "--registration",
        str(registration),
        "--state",
        "accepted",
        "--idle-telemetry",
        "unavailable",
        "--intelligence-span-id",
        review.span_id,
        "--wait-span-id",
        wait.span_id,
    )
    assert dispatched.returncode == 0, dispatched.stderr
    evidence = tmp_path / "plan-findings.json"
    evidence.write_text(
        json.dumps({"findings": [finding("PLAN-F001", candidate)]}),
        encoding="utf-8",
    )
    ingested = run(
        "ingest-findings",
        "--run-dir",
        str(run_dir),
        "--kind",
        "plan",
        "--candidate",
        candidate,
        "--review-span-id",
        review.span_id,
        "--input",
        str(evidence),
    )
    assert ingested.returncode == 0, ingested.stderr
    measured = closed_span(
        engine_root=repository,
        trace_id=metadata["telemetry_trace_id"],
        span_id=review.span_id,
    )
    assert measured["findings_reported"] == 1
    assert measured["actionable_findings"] == 1


def test_finding_rejects_invalid_transition_and_identity_change(
    repository: Path, tmp_path: Path
) -> None:
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    assert ingest(run_dir, tmp_path, [finding("CODE-F001", candidate)]).returncode == 0

    invalid = finding(
        "CODE-F001",
        candidate,
        state="closed",
        resolved_in=candidate,
    )
    transition = ingest(run_dir, tmp_path, [invalid])
    assert transition.returncode == 2
    assert "invalid transition" in transition.stderr

    changed = finding("CODE-F001", candidate)
    changed["required_outcome"] = "A different outcome"
    identity = ingest(run_dir, tmp_path, [changed])
    assert identity.returncode == 2
    assert "immutable field" in identity.stderr


def test_finding_that_stays_actionable_keeps_its_evidence(repository: Path, tmp_path: Path) -> None:
    """One id carrying a new objection each round is several findings wearing one label."""
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    assert ingest(run_dir, tmp_path, [finding("CODE-F001", candidate)]).returncode == 0

    re_aimed = finding("CODE-F001", candidate)
    re_aimed["evidence"] = "A different defect in the same area"
    re_aimed["disposition"] = "Partially addressed"
    refused = ingest(run_dir, tmp_path, [re_aimed])
    assert refused.returncode == 2
    assert "substitutes evidence while it remains actionable" in refused.stderr
    journal = json.loads((run_dir / "ingest-log.jsonl").read_text().splitlines()[-1])
    assert journal["refusal_codes"] == ["evidence-substituted"]

    # Progress notes belong in `disposition`; the objection itself is stable.
    noted = finding("CODE-F001", candidate)
    noted["disposition"] = "Partially addressed: the wrapper exists, its failure contract does not"
    assert ingest(run_dir, tmp_path, [noted]).returncode == 0

    # Resolving it may restate what was verified: the finding is no longer actionable.
    resolved = finding("CODE-F001", candidate, state="addressed")
    assert ingest(run_dir, tmp_path, [resolved]).returncode == 0
    verified = finding("CODE-F001", candidate, state="verified", resolved_in=candidate)
    verified["evidence"] = "Verified resolved: the guard now precedes the mutation"
    assert ingest(run_dir, tmp_path, [verified]).returncode == 0, verified

    # A further defect gets its own id, classified by how it surfaced.
    further = finding("CODE-F002", candidate, classification="newly-exposed-by-resolution")
    assert ingest(run_dir, tmp_path, [further]).returncode == 0


def test_change_metadata_carries_falsifiers_and_gate_status(
    repository: Path, tmp_path: Path
) -> None:
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    assert ingest(run_dir, tmp_path, [finding("CODE-F001", candidate)]).returncode == 0
    (repository / "code.py").write_text("VALUE = 2\n")

    def artifact(metadata: dict[str, object]) -> Path:
        path = tmp_path / "coder.md"
        path.write_text("### Change Evidence\n```json\n" + json.dumps(metadata) + "\n```\n")
        return path

    base: dict[str, object] = {
        "risk_tags": ["public-api"],
        "selected_tests": ["./bin/test focused"],
        "selection_reason": "Exercises the public behavior",
        "intentionally_unchanged": [],
        "rebase_reasons": [],
        "failure_analysis": "",
    }
    # The old six-field shape is refused: both new fields are required.
    refused = run(
        "capture-change", "--run-dir", str(run_dir), "--metadata-artifact", str(artifact(base))
    )
    assert refused.returncode == 2
    assert "must contain exactly" in refused.stderr

    silent = dict(base, falsifiers=[], gate_status={"focused": "not-run", "reason": ""})
    refused = run(
        "capture-change", "--run-dir", str(run_dir), "--metadata-artifact", str(artifact(silent))
    )
    assert refused.returncode == 2
    assert "reason must be nonempty when focused is not-run" in refused.stderr

    malformed = dict(
        base,
        falsifiers=[{"test": "tests/test_x.py::test_y"}],
        gate_status={"focused": "green", "reason": ""},
    )
    refused = run(
        "capture-change", "--run-dir", str(run_dir), "--metadata-artifact", str(artifact(malformed))
    )
    assert refused.returncode == 2
    assert "falsifiers[0] must be an object with exactly test, mutation" in refused.stderr

    good = dict(
        base,
        falsifiers=[{"test": "tests/test_x.py::test_y", "mutation": "drop the guard at :12"}],
        gate_status={"focused": "not-run", "reason": "sandbox cannot reach the uv cache"},
    )
    accepted = run(
        "capture-change", "--run-dir", str(run_dir), "--metadata-artifact", str(artifact(good))
    )
    assert accepted.returncode == 0, accepted.stderr
    change = json.loads((run_dir / "change.json").read_text())
    assert change["falsifiers"] == good["falsifiers"]
    assert change["gate_status"] == good["gate_status"]

    output = tmp_path / "packet.md"
    packet = run("packet", "--run-dir", str(run_dir), "--kind", "code", "--output", str(output))
    assert packet.returncode == 0, packet.stderr
    text = output.read_text()
    assert "Focused gate: not-run (sandbox cannot reach the uv cache)" in text
    assert "tests/test_x.py::test_y ← drop the guard at :12" in text


def test_placeholder_evidence_and_suspected_blocking_are_refused(
    repository: Path, tmp_path: Path
) -> None:
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    placeholder = finding("CODE-F001", candidate)
    placeholder["evidence"] = "Carried forward unchanged. This pass did not re-examine it."
    refused = ingest(run_dir, tmp_path, [placeholder])
    assert refused.returncode == 2
    assert "carry-forward placeholder" in refused.stderr

    suspected = finding("CODE-F002", candidate)
    suspected["severity"] = "blocking"
    suspected["evidence"] = "SUSPECTED, NOT CONFIRMED: the symlink case needs shell access."
    refused = ingest(run_dir, tmp_path, [suspected])
    assert refused.returncode == 2
    assert "SUSPECTED and cannot be blocking" in refused.stderr

    suspected["severity"] = "medium"
    assert ingest(run_dir, tmp_path, [suspected]).returncode == 0


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


def test_malformed_role_artifact_is_rejected(repository: Path, tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    malformed = tmp_path / "critic.md"
    malformed.write_text("## Finding Evidence\nnot a fenced JSON block\n")
    result = run(
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
        str(malformed),
    )
    assert result.returncode == 2
    assert "block found" in result.stderr
    assert "malformed" in result.stderr


def test_role_artifact_allows_blank_line_before_json_fence(
    repository: Path, tmp_path: Path
) -> None:
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    artifact = tmp_path / "review.md"
    artifact.write_text(
        "## Finding Evidence\n\n```json\n"
        + json.dumps({"findings": [finding("CODE-F001", candidate)]})
        + "\n```\n"
    )

    result = run(
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
        str(artifact),
    )

    assert result.returncode == 0, result.stderr


def test_structured_artifact_is_ingested_without_a_markdown_envelope(
    repository: Path, tmp_path: Path
) -> None:
    """A schema-constrained venue returns JSON, so there is no envelope to find.

    Accepting both shapes here is what keeps the orchestrator from branching on
    venue — which would put the invocation shape back in the caller's hands, the
    thing CH-13 removed.
    """
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    artifact = tmp_path / "review.json"
    artifact.write_text(
        json.dumps(
            {
                "verdict": "REVISE",
                "summary": "One blocking issue.",
                "findings": [finding("CODE-F001", candidate)],
            }
        )
    )

    result = run(
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
        str(artifact),
    )

    assert result.returncode == 0, result.stderr


def test_structured_artifact_still_gets_the_fenced_readers_diagnostic(
    repository: Path, tmp_path: Path
) -> None:
    """A JSON artifact that is not a findings document is not silently accepted."""
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    artifact = tmp_path / "review.json"
    artifact.write_text(json.dumps({"verdict": "APPROVED"}))

    result = run(
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
        str(artifact),
    )

    assert result.returncode != 0
    assert "Finding Evidence" in result.stderr


def test_role_artifact_diagnostic_distinguishes_missing_block(
    repository: Path, tmp_path: Path
) -> None:
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    artifact = tmp_path / "review.md"
    artifact.write_text("## Verdict: REVISE\n")

    result = run(
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
        str(artifact),
    )

    assert result.returncode == 2
    assert "no ## Finding Evidence fenced JSON block found" in result.stderr


def test_finding_batch_reports_every_invalid_finding(repository: Path, tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    invalid_severity = finding("CODE-F001", candidate)
    invalid_severity["severity"] = "catastrophic"
    invalid_state = finding("CODE-F002", candidate)
    invalid_state["state"] = "done"
    invalid_state["classification"] = "regression"
    wrong_namespace = finding("PLAN-F003", candidate)

    result = ingest(
        run_dir,
        tmp_path,
        [invalid_severity, invalid_state, wrong_namespace],
        candidate=candidate,
    )

    assert result.returncode == 2
    assert "CODE-F001 field severity is invalid: catastrophic" in result.stderr
    assert "CODE-F002 field state is invalid: done" in result.stderr
    assert "CODE-F002 field classification is invalid: regression" in result.stderr
    assert "PLAN-F003 field id must use the CODE-FNNN namespace" in result.stderr
    assert json.loads((run_dir / "findings.json").read_text())["findings"] == []


@pytest.mark.parametrize(
    ("field", "alias", "canonical"),
    [
        ("severity", "major", "high"),
        ("severity", "critical", "blocking"),
        ("severity", "minor", "low"),
        ("severity", "info", "nit"),
        ("state", "resolved", "verified"),
        ("state", "fixed", "verified"),
    ],
)
def test_finding_alias_is_normalized_with_notice(
    repository: Path,
    tmp_path: Path,
    field: str,
    alias: str,
    canonical: str,
) -> None:
    run_dir = tmp_path / f"run-{field}-{alias}"
    candidate = initialize(repository, run_dir)
    item = finding("CODE-F001", candidate)
    item[field] = alias
    if field == "state":
        item["resolved_in"] = candidate

    result = ingest(run_dir, tmp_path, [item], candidate=candidate)

    assert result.returncode == 0, result.stderr
    assert f"normalized CODE-F001 field {field}: {alias} -> {canonical}" in result.stderr
    stored = json.loads((run_dir / "findings.json").read_text())["findings"][0]
    assert stored[field] == canonical


def test_packet_is_deterministic_projection_with_explicit_omissions(
    repository: Path, tmp_path: Path
) -> None:
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    (repository / "code.py").write_text("VALUE = 2\n")
    candidate = capture(repository, run_dir)
    assert (
        ingest(
            run_dir,
            tmp_path,
            [
                finding("CODE-F001", candidate),
                finding(
                    "CODE-F002",
                    candidate,
                    state="closed",
                    resolved_in=candidate,
                ),
            ],
            candidate=candidate,
        ).returncode
        == 0
    )
    output = tmp_path / "packet.md"

    result = run(
        "packet",
        "--run-dir",
        str(run_dir),
        "--kind",
        "code",
        "--output",
        str(output),
    )

    assert result.returncode == 0, result.stderr
    text = output.read_text()
    assert "CODE-F001" in text
    assert "CODE-F002" not in text
    assert "code.py" in text
    assert "Omission rules" in text
    packet_record = json.loads((run_dir / "packets.jsonl").read_text())
    assert packet_record["bytes"] == len(text.encode())
    assert packet_record["candidate_id"] == candidate
    assert "## Failure analysis" in text
    assert "None (initial implementation)." in text


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


def test_plan_packet_contains_exact_plan_delta(repository: Path, tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    plan = tmp_path / "plan.md"
    plan.write_text("# Plan\n\n- First\n")
    first = run(
        "capture-plan",
        "--run-dir",
        str(run_dir),
        "--plan",
        str(plan),
    )
    assert first.returncode == 0, first.stderr
    reviewed = run(
        "mark-plan-reviewed",
        "--run-dir",
        str(run_dir),
        "--plan",
        str(plan),
        "--expected-plan",
        first.stdout.strip(),
    )
    assert reviewed.returncode == 0, reviewed.stderr

    plan.write_text("# Plan\n\n- First\n- Second\n")
    second = run(
        "capture-plan",
        "--run-dir",
        str(run_dir),
        "--plan",
        str(plan),
    )
    assert second.returncode == 0, second.stderr
    output = tmp_path / "plan-packet.md"
    packet = run(
        "packet",
        "--run-dir",
        str(run_dir),
        "--kind",
        "plan",
        "--output",
        str(output),
    )

    assert packet.returncode == 0, packet.stderr
    text = output.read_text()
    assert "Causal plan change" in text
    assert "+- Second" in text
    assert first.stdout.strip() in text
    assert second.stdout.strip() in text


def test_gate_record_rejects_stale_candidate_and_hashes_artifact(
    repository: Path, tmp_path: Path
) -> None:
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    artifact = tmp_path / "gate.txt"
    artifact.write_text("PASS\n")

    recorded = run_final_gate(run_dir, candidate, artifact)
    assert recorded.returncode == 0, recorded.stderr
    gate = json.loads((run_dir / "gates.jsonl").read_text())
    assert gate["artifact_sha256"]
    assert gate["final"]

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


def test_record_gate_round_trips_multiword_argv_through_validate(
    repository: Path, tmp_path: Path
) -> None:
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir, evidence_lane="light")

    recorded = run(
        "record-gate",
        "--run-dir",
        str(run_dir),
        "--candidate",
        candidate,
        "--selection-reason",
        "Imported venue-fallback gate",
        "--exit-code",
        "0",
        "--warning-count",
        "0",
        "--",
        "./bin/test",
        "tests/test_check.py",
        "-q",
    )

    assert recorded.returncode == 0, recorded.stderr
    gate = json.loads((run_dir / "gates.jsonl").read_text())
    assert gate["argv"] == ["./bin/test", "tests/test_check.py", "-q"]
    assert gate["command"] == "./bin/test tests/test_check.py -q"
    validated = run("validate", "--run-dir", str(run_dir))
    assert validated.returncode == 0, validated.stderr


def test_legacy_record_gate_row_is_readable_and_refused_precisely(
    repository: Path, tmp_path: Path
) -> None:
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir, evidence_lane="light")
    metadata = json.loads((run_dir / "run.json").read_text())
    command = "./bin/test tests/test_check.py -q"
    legacy = {
        "schema_version": 3,
        "recorded_at": "2026-08-16T00:00:00+00:00",
        "candidate_id": candidate,
        "candidate_after_id": candidate,
        "argv": [command],
        "command": command,
        "operation": "gate.imported",
        "attempt": 1,
        "selection_reason": "Legacy imported gate",
        "exit_code": 0,
        "outcome": "success",
        "warning_count": 0,
        "artifact_sha256": None,
        "final": False,
        "telemetry_trace_id": metadata["telemetry_trace_id"],
        "telemetry_span_id": None,
        "duration_ns": None,
        "telemetry_complete": False,
    }
    (run_dir / "gates.jsonl").write_text(json.dumps(legacy) + "\n")

    validated = run("validate", "--run-dir", str(run_dir))

    assert validated.returncode == 2
    assert "gates.jsonl line 1 has non-canonical argv" in validated.stderr
    assert repr([command]) in validated.stderr
    assert "legacy record-gate encoding" in validated.stderr


def test_findings_reject_wrong_namespace_and_noncurrent_candidate(
    repository: Path, tmp_path: Path
) -> None:
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)

    wrong_namespace = ingest(
        run_dir,
        tmp_path,
        [finding("PLAN-F001", candidate)],
        kind="code",
    )
    assert wrong_namespace.returncode == 2
    assert "CODE-FNNN namespace" in wrong_namespace.stderr

    (repository / "code.py").write_text("VALUE = 2\n")
    stale = ingest(
        run_dir,
        tmp_path,
        [finding("CODE-F001", candidate)],
        candidate=candidate,
    )
    assert stale.returncode == 2
    assert "candidate mismatch" in stale.stderr


def test_evidence_paths_cannot_escape_repository(repository: Path, tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    escaped_finding = finding("CODE-F001", candidate)
    escaped_finding["affected_paths"] = ["../outside"]

    finding_result = ingest(run_dir, tmp_path, [escaped_finding])
    assert finding_result.returncode == 2
    assert "repository-relative paths" in finding_result.stderr

    (repository / "code.py").write_text("VALUE = 2\n")
    metadata = tmp_path / "change.json"
    metadata.write_text(
        json.dumps(
            {
                "risk_tags": [],
                "selected_tests": ["./bin/test focused"],
                "selection_reason": "Exercises the change",
                "intentionally_unchanged": ["../outside"],
                "rebase_reasons": [],
                "failure_analysis": "",
                "falsifiers": [],
                "gate_status": {"focused": "green", "reason": ""},
            }
        )
    )
    change_result = run(
        "capture-change",
        "--run-dir",
        str(run_dir),
        "--metadata",
        str(metadata),
    )
    assert change_result.returncode == 2
    assert "repository-relative paths" in change_result.stderr


def test_pre_dispatch_rejected_attempt_validates_with_an_error_127_span(
    repository: Path, tmp_path: Path
) -> None:
    """A rejected attempt is recordable, and only in the correct shape.

    An attempt the watcher refuses before launch still consumed a registration,
    so validation still demands exactly one closed intelligence span for it --
    closed as error 127, with no wait span, because nothing was ever waited on.
    Recording the rejection with no span at all is NOT a valid shape and must
    stay refused: correctness belongs at write time, not forgiveness at read
    time. Observed in Phase 26.9.2, where a span-less rejected dispatch made the
    whole run unvalidatable and could not be repaired afterwards, because the
    terminal amendment is append-only.
    """
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    metadata = json.loads((run_dir / "run.json").read_text())
    trace_id = metadata["telemetry_trace_id"]
    root_span_id = metadata["telemetry_root_span_id"]

    registration = run_dir / "rejected-reviewer-1.json"
    registered = run(
        "register-role-attempt",
        "--run-dir",
        str(run_dir),
        "--operation",
        "role.plan-review",
        "--attempt",
        "1",
        "--role",
        "reviewer",
        "--harness",
        "codex",
        "--model",
        "sol",
        "--effort",
        "high",
        "--reason",
        "initial",
        "--output",
        str(registration),
    )
    assert registered.returncode == 0, registered.stderr

    # The shape that must stay refused: a rejection with no span to point at.
    spanless = run(
        "record-role-dispatch",
        "--run-dir",
        str(run_dir),
        "--registration",
        str(registration),
        "--state",
        "rejected",
        "--idle-telemetry",
        "not-dispatched",
    )
    assert spanless.returncode != 0
    assert "intelligence span" in (spanless.stdout + spanless.stderr)

    # The correct shape: error-127 intelligence span closed at rejection time.
    intelligence = start_span(
        engine_root=repository,
        trace_id=trace_id,
        parent_span_id=root_span_id,
        category="intelligence",
        operation="role.plan-review",
        attempt=1,
        role="reviewer",
        harness="codex",
        model="sol",
        effort="high",
    )
    opened = open_role_dispatch(run_dir, registration, intelligence.span_id)
    assert opened.returncode == 0, opened.stderr
    finish_span(
        engine_root=repository,
        trace_id=trace_id,
        span_id=intelligence.span_id,
        outcome="error",
        exit_code=127,
    )
    dispatched = run(
        "record-role-dispatch",
        "--run-dir",
        str(run_dir),
        "--registration",
        str(registration),
        "--state",
        "rejected",
        "--idle-telemetry",
        "not-dispatched",
        "--intelligence-span-id",
        intelligence.span_id,
    )
    assert dispatched.returncode == 0, dispatched.stderr

    complete_orchestration(repository, run_dir)
    validated = run("validate", "--run-dir", str(run_dir))
    assert validated.returncode == 0, validated.stdout + validated.stderr


def test_validate_can_require_successful_named_final_gate(repository: Path, tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    complete_orchestration(repository, run_dir)

    absent = run(
        "validate",
        "--run-dir",
        str(run_dir),
        "--require-final",
        "--required-final-command",
        "./bin/check all",
    )
    assert absent.returncode == 2
    assert "no successful final gate" in absent.stderr

    recorded = run_final_gate(run_dir, candidate)
    assert recorded.returncode == 0, recorded.stderr
    valid = run(
        "validate",
        "--run-dir",
        str(run_dir),
        "--require-final",
        "--required-final-command",
        "./bin/check all",
    )
    assert valid.returncode == 0, valid.stderr


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
        "--require-final",
        "--required-final-command",
        "./bin/check all",
    )

    assert result.returncode == 2
    assert "phase-close findings remain unresolved: CODE-F001" in result.stderr


def test_validate_detects_corrupt_evidence(repository: Path, tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    valid = run("validate", "--run-dir", str(run_dir))
    assert valid.returncode == 0, valid.stderr
    assert "EVIDENCE VALID" in valid.stdout

    (run_dir / "findings.json").write_text("{broken")
    invalid = run("validate", "--run-dir", str(run_dir))
    assert invalid.returncode == 2
    assert "invalid JSON" in invalid.stderr


def test_validate_recomputes_candidate_manifest_identity(repository: Path, tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    reviewed_path = run_dir / "reviewed-candidate.json"
    reviewed = json.loads(reviewed_path.read_text())
    reviewed["entries"][0]["content_sha256"] = "0" * 64
    reviewed_path.write_text(json.dumps(reviewed))

    result = run("validate", "--run-dir", str(run_dir))

    assert result.returncode == 2
    assert "identifier does not match" in result.stderr


def test_validate_rejects_malformed_change_manifest(repository: Path, tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    (repository / "code.py").write_text("VALUE = 2\n")
    capture(repository, run_dir)
    change_path = run_dir / "change.json"
    change = json.loads(change_path.read_text())
    change["selected_tests"] = {"not": "an array"}
    change_path.write_text(json.dumps(change))

    result = run("validate", "--run-dir", str(run_dir))

    assert result.returncode == 2
    assert "change selected_tests must be a string array" in result.stderr


def test_role_registration_spans_and_finalized_timing_summary(
    repository: Path, tmp_path: Path
) -> None:
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    metadata = json.loads((run_dir / "run.json").read_text())
    handoff = run_dir / "role.json"
    registered = run(
        "register-role-attempt",
        "--run-dir",
        str(run_dir),
        "--operation",
        "role.implement",
        "--attempt",
        "1",
        "--role",
        "coder",
        "--harness",
        "native",
        "--reason",
        "initial",
        "--output",
        str(handoff),
    )
    assert registered.returncode == 0, registered.stderr
    intelligence = start_span(
        engine_root=repository,
        trace_id=metadata["telemetry_trace_id"],
        parent_span_id=metadata["telemetry_root_span_id"],
        category="intelligence",
        operation="role.implement",
        role="coder",
        harness="native",
    )
    opened = open_role_dispatch(run_dir, handoff, intelligence.span_id)
    assert opened.returncode == 0, opened.stderr
    wait = start_span(
        engine_root=repository,
        trace_id=metadata["telemetry_trace_id"],
        parent_span_id=intelligence.span_id,
        category="wait",
        operation="role.implement",
        role="coder",
        harness="native",
    )
    finish_span(
        engine_root=repository,
        trace_id=metadata["telemetry_trace_id"],
        span_id=wait.span_id,
        outcome="success",
        exit_code=0,
    )
    finish_span(
        engine_root=repository,
        trace_id=metadata["telemetry_trace_id"],
        span_id=intelligence.span_id,
        outcome="success",
        exit_code=0,
    )
    dispatch = run(
        "record-role-dispatch",
        "--run-dir",
        str(run_dir),
        "--registration",
        str(handoff),
        "--state",
        "accepted",
        "--idle-telemetry",
        "unavailable",
        "--intelligence-span-id",
        intelligence.span_id,
        "--wait-span-id",
        wait.span_id,
    )
    assert dispatch.returncode == 0, dispatch.stderr
    assert run("validate", "--run-dir", str(run_dir)).returncode == 0
    complete_orchestration(repository, run_dir)
    finish_span(
        engine_root=repository,
        trace_id=metadata["telemetry_trace_id"],
        span_id=metadata["telemetry_root_span_id"],
        outcome="success",
    )
    finalize_trace(engine_root=repository, trace_id=metadata["telemetry_trace_id"])
    summary = run("timing-summary", "--run-dir", str(run_dir), "--format", "json")
    assert summary.returncode == 0, summary.stderr
    projection = json.loads(summary.stdout)
    assert projection["trace_id"] == metadata["telemetry_trace_id"]
    assert projection["intelligence_ns"] >= projection["wait_ns"]
    markdown = run("timing-summary", "--run-dir", str(run_dir), "--format", "markdown")
    assert markdown.returncode == 0, markdown.stderr
    slow = projection["slowest_spans"][0]
    assert slow["operation"] in markdown.stdout
    assert slow["category"] in markdown.stdout
    assert f"attempt {slow['attempt']}" in markdown.stdout
    assert slow["outcome"] in markdown.stdout
    assert f"{slow['duration_ns']} ns" in markdown.stdout


def test_wait_metadata_drift_is_rejected(repository: Path, tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    metadata = json.loads((run_dir / "run.json").read_text())
    handoff = run_dir / "role.json"
    assert (
        run(
            "register-role-attempt",
            "--run-dir",
            str(run_dir),
            "--operation",
            "role.implement",
            "--attempt",
            "1",
            "--role",
            "coder",
            "--harness",
            "native",
            "--reason",
            "initial",
            "--output",
            str(handoff),
        ).returncode
        == 0
    )
    intelligence = start_span(
        engine_root=repository,
        trace_id=metadata["telemetry_trace_id"],
        parent_span_id=metadata["telemetry_root_span_id"],
        category="intelligence",
        operation="role.implement",
        role="coder",
        harness="native",
    )
    opened = open_role_dispatch(run_dir, handoff, intelligence.span_id)
    assert opened.returncode == 0, opened.stderr
    wait = start_span(
        engine_root=repository,
        trace_id=metadata["telemetry_trace_id"],
        parent_span_id=intelligence.span_id,
        category="wait",
        operation="role.implement",
        role="coder",
        harness="claude",
    )
    finish_span(
        engine_root=repository,
        trace_id=metadata["telemetry_trace_id"],
        span_id=wait.span_id,
        outcome="success",
        exit_code=0,
    )
    finish_span(
        engine_root=repository,
        trace_id=metadata["telemetry_trace_id"],
        span_id=intelligence.span_id,
        outcome="success",
        exit_code=0,
    )
    result = run(
        "record-role-dispatch",
        "--run-dir",
        str(run_dir),
        "--registration",
        str(handoff),
        "--state",
        "accepted",
        "--idle-telemetry",
        "unavailable",
        "--intelligence-span-id",
        intelligence.span_id,
        "--wait-span-id",
        wait.span_id,
    )
    assert result.returncode == 2
    assert (
        "wait span harness does not match registration: span='claude', registration='native'"
    ) in result.stderr
    rows = [
        json.loads(line)
        for line in (run_dir / "role-dispatch.jsonl").read_text().splitlines()
        if line.strip()
    ]
    assert len(rows) == 1 and rows[0]["state"] == "opened"


def test_pinned_tool_bundle_survives_live_tool_replacement(
    repository: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    live = tmp_path / "live"
    (live / "bin").mkdir(parents=True)
    (live / "lib" / "agentic_starter").mkdir(parents=True)
    for name in (
        "kickoff-evidence",
        "kickoff-tree-id",
        "execution-telemetry",
        "kickoff-config",
    ):
        shutil.copy2(ROOT / "bin" / name, live / "bin" / name)
    shutil.copy2(ROOT / "kickoff.yaml", live / "kickoff.yaml")
    for name in (
        "__init__.py",
        "execution_telemetry.py",
        "execution_dashboard.py",
        "finding_schema.py",
    ):
        shutil.copy2(
            ROOT / "lib" / "agentic_starter" / name, live / "lib" / "agentic_starter" / name
        )
    spool = tmp_path / "spool"
    monkeypatch.setenv("AGENTIC_STARTER_EXECUTION_TELEMETRY_DIR", str(spool))
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
    environment = os.environ.copy()
    initialized = subprocess.run(
        [
            str(live / "bin" / "kickoff-evidence"),
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
            "--review-lane",
            "full",
            "--evidence-lane",
            "full",
            "--follow-up-route",
            "direct-fix",
        ],
        cwd=repository,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert initialized.returncode == 0, initialized.stderr
    pinned_evidence = run_dir / "tools" / "kickoff-evidence"
    pinned_telemetry = run_dir / "tools" / "execution-telemetry"
    for target in (
        live / "bin" / "kickoff-evidence",
        live / "bin" / "kickoff-tree-id",
        live / "bin" / "execution-telemetry",
        live / "bin" / "kickoff-config",
        live / "lib" / "agentic_starter" / "execution_telemetry.py",
        live / "lib" / "agentic_starter" / "execution_dashboard.py",
    ):
        target.write_text("#!/bin/sh\nexit 91\n")
        target.chmod(0o755)
    (live / "kickoff.yaml").write_text("invalid: live config replaced\n")
    registration = run_dir / "external-role.json"
    registered = subprocess.run(
        [
            str(pinned_evidence),
            "register-role-attempt",
            "--run-dir",
            str(run_dir),
            "--operation",
            "role.plan-review",
            "--attempt",
            "1",
            "--role",
            "reviewer",
            "--harness",
            "claude",
            "--model",
            "opus",
            "--effort",
            "high",
            "--reason",
            "initial",
            "--output",
            str(registration),
        ],
        cwd=repository,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert registered.returncode == 0, registered.stderr
    fake_claude = tmp_path / "claude"
    fake_claude.write_text('#!/bin/sh\nprintf \'%s\\n\' \'{"type":"result","result":"PINNED"}\'\n')
    fake_claude.chmod(0o755)
    prompt = tmp_path / "reviewer-prompt.md"
    prompt.write_text("Adopt policies/personas/plan-reviewer.md and report.\n")
    # The pinned manager builds its own invocation; only the binary is stubbed.
    watched = subprocess.run(
        [
            UV,
            "run",
            "--script",
            str(run_dir / "tools" / "kickoff-config"),
            "watch",
            "--role",
            "reviewer",
            "--venue",
            "claude",
            "--model",
            "opus",
            "--effort",
            "high",
            "--phase",
            "1.1",
            "--prompt-file",
            str(prompt),
            "--result-file",
            str(tmp_path / "reviewer-verdict.md"),
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
            "role.plan-review",
            "--telemetry-attempt",
            "1",
            "--telemetry-role-registration",
            str(registration),
        ],
        cwd=repository,
        env={**environment, "KICKOFF_CLI_CLAUDE": str(fake_claude)},
        capture_output=True,
        text=True,
        check=False,
    )
    assert watched.returncode == 0, watched.stderr
    dispatch = json.loads((run_dir / "role-dispatch.jsonl").read_text().splitlines()[-1])
    assert dispatch["accepted"] is True
    assert dispatch["idle_telemetry"] == "available"
    plan = tmp_path / "plan.md"
    plan.write_text("# Approved plan\n")
    captured_plan = subprocess.run(
        [
            str(pinned_evidence),
            "capture-plan",
            "--run-dir",
            str(run_dir),
            "--plan",
            str(plan),
        ],
        cwd=repository,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert captured_plan.returncode == 0, captured_plan.stderr
    reviewed_plan = subprocess.run(
        [
            str(pinned_evidence),
            "mark-plan-reviewed",
            "--run-dir",
            str(run_dir),
            "--plan",
            str(plan),
            "--expected-plan",
            captured_plan.stdout.strip(),
        ],
        cwd=repository,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert reviewed_plan.returncode == 0, reviewed_plan.stderr
    (repository / "code.py").write_text("VALUE = 2\n")
    captured = subprocess.run(
        [
            str(pinned_evidence),
            "capture-change",
            "--run-dir",
            str(run_dir),
            "--selection-reason",
            "self-hosting regression",
        ],
        cwd=repository,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert captured.returncode == 0, captured.stderr
    reviewed = subprocess.run(
        [
            str(pinned_evidence),
            "mark-reviewed",
            "--run-dir",
            str(run_dir),
            "--expected-candidate",
            captured.stdout.strip(),
        ],
        cwd=repository,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert reviewed.returncode == 0, reviewed.stderr
    gated = subprocess.run(
        [
            str(pinned_evidence),
            "run-gate",
            "--run-dir",
            str(run_dir),
            "--candidate",
            captured.stdout.strip(),
            "--operation",
            "gate.check-all",
            "--selection-reason",
            "self-hosting gate",
            "--warning-count",
            "0",
            "--final",
            "--",
            "/usr/bin/true",
        ],
        cwd=repository,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert gated.returncode == 0, gated.stderr
    review_dispatch = json.loads((run_dir / "role-dispatch.jsonl").read_text().splitlines()[-1])
    attach_review_metrics(
        engine_root=repository,
        trace_id=root.trace_id,
        span_id=review_dispatch["intelligence_span_id"],
        findings_reported=0,
        actionable_findings=0,
    )
    complete_orchestration(repository, run_dir)
    validated = subprocess.run(
        [
            str(pinned_evidence),
            "validate",
            "--run-dir",
            str(run_dir),
            "--require-final",
            "--required-final-command",
            "/usr/bin/true",
        ],
        cwd=repository,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert validated.returncode == 0, validated.stderr
    for arguments in (
        (
            "finish",
            "--repo-root",
            str(repository),
            "--trace-id",
            root.trace_id,
            "--span-id",
            root.span_id,
            "--outcome",
            "success",
        ),
        ("finalize", "--repo-root", str(repository), "--trace-id", root.trace_id),
    ):
        result = subprocess.run(
            [str(pinned_telemetry), *arguments],
            cwd=repository,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
    report = subprocess.run(
        [
            str(pinned_evidence),
            "timing-summary",
            "--run-dir",
            str(run_dir),
            "--format",
            "markdown",
        ],
        cwd=repository,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert report.returncode == 0, report.stderr
    assert "Execution timing" in report.stdout


def test_zero_exit_candidate_changing_gate_is_recorded_and_rejected(
    repository: Path, tmp_path: Path
) -> None:
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    mutator = tmp_path / "mutate.sh"
    mutator.write_text(f"#!/bin/sh\nprintf 'VALUE = 9\\n' > {repository / 'code.py'}\nexit 0\n")
    mutator.chmod(0o755)
    result = run(
        "run-gate",
        "--run-dir",
        str(run_dir),
        "--candidate",
        candidate,
        "--operation",
        "gate.focused",
        "--selection-reason",
        "mutation proof",
        "--warning-count",
        "0",
        "--",
        str(mutator),
        cwd=repository,
    )
    assert result.returncode == 2
    gate = json.loads((run_dir / "gates.jsonl").read_text())
    assert gate["exit_code"] == 0
    assert gate["candidate_after_id"] != gate["candidate_id"]


def test_fabricated_or_foreign_gate_span_cannot_validate(repository: Path, tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    assert (
        run(
            "run-gate",
            "--run-dir",
            str(run_dir),
            "--candidate",
            candidate,
            "--operation",
            "gate.focused",
            "--selection-reason",
            "focused",
            "--warning-count",
            "0",
            "--",
            "/usr/bin/true",
            cwd=repository,
        ).returncode
        == 0
    )
    gates_path = run_dir / "gates.jsonl"
    gate = json.loads(gates_path.read_text())
    gate["telemetry_span_id"] = "ffffffffffff4fff8fffffffffffffff"
    gates_path.write_text(json.dumps(gate, separators=(",", ":")) + "\n")
    result = run("validate", "--run-dir", str(run_dir))
    assert result.returncode == 2
    assert "span_id does not identify" in result.stderr


def test_unregistered_closed_gate_span_blocks_validation_and_timing(
    repository: Path, tmp_path: Path
) -> None:
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    metadata = json.loads((run_dir / "run.json").read_text())
    extra = start_span(
        engine_root=repository,
        trace_id=metadata["telemetry_trace_id"],
        parent_span_id=metadata["telemetry_root_span_id"],
        category="gate",
        operation="gate.fabricated",
    )
    finish_span(
        engine_root=repository,
        trace_id=metadata["telemetry_trace_id"],
        span_id=extra.span_id,
        outcome="success",
        exit_code=0,
    )
    rejected = run("validate", "--run-dir", str(run_dir))
    assert rejected.returncode == 2
    assert "unregistered=" in rejected.stderr
    complete_orchestration(repository, run_dir)
    finish_span(
        engine_root=repository,
        trace_id=metadata["telemetry_trace_id"],
        span_id=metadata["telemetry_root_span_id"],
        outcome="success",
    )
    finalize_trace(engine_root=repository, trace_id=metadata["telemetry_trace_id"])
    summary = run("timing-summary", "--run-dir", str(run_dir), "--format", "json")
    assert summary.returncode == 2
    assert "unregistered=" in summary.stderr


def test_timing_summary_refuses_unfinalized_trace(repository: Path, tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    result = run("timing-summary", "--run-dir", str(run_dir), "--format", "json")
    assert result.returncode == 2
    assert "not durably finalized" in result.stderr


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
        "--review-lane",
        "full",
        "--evidence-lane",
        "full",
        "--follow-up-route",
        "initial",
    )
    assert initialized.returncode == 0, initialized.stderr

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
        "--final",
        "--",
        "/usr/bin/true",
        cwd=repository,
    )
    assert final.returncode == 0, final.stderr
    complete_orchestration(repository, run_dir)
    validated = run(
        "validate",
        "--run-dir",
        str(run_dir),
        "--require-final",
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


@pytest.mark.parametrize(
    ("accepted", "outcome", "exit_code"),
    [
        (False, "error", 127),
        (True, "error", 1),
        (True, "cancelled", 143),
    ],
)
def test_native_dispatch_topologies_preserve_truthful_outcomes(
    repository: Path,
    tmp_path: Path,
    accepted: bool,
    outcome: str,
    exit_code: int,
) -> None:
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    metadata = json.loads((run_dir / "run.json").read_text())
    handoff = run_dir / "native.json"
    assert (
        run(
            "register-role-attempt",
            "--run-dir",
            str(run_dir),
            "--operation",
            "role.implement",
            "--attempt",
            "1",
            "--role",
            "coder",
            "--harness",
            "native",
            "--reason",
            "initial",
            "--output",
            str(handoff),
        ).returncode
        == 0
    )
    intelligence = start_span(
        engine_root=repository,
        trace_id=metadata["telemetry_trace_id"],
        parent_span_id=metadata["telemetry_root_span_id"],
        category="intelligence",
        operation="role.implement",
        role="coder",
        harness="native",
    )
    opened = open_role_dispatch(run_dir, handoff, intelligence.span_id)
    assert opened.returncode == 0, opened.stderr
    wait = None
    if accepted:
        wait = start_span(
            engine_root=repository,
            trace_id=metadata["telemetry_trace_id"],
            parent_span_id=intelligence.span_id,
            category="wait",
            operation="role.implement",
            role="coder",
            harness="native",
        )
        finish_span(
            engine_root=repository,
            trace_id=metadata["telemetry_trace_id"],
            span_id=wait.span_id,
            outcome=outcome,
            exit_code=exit_code,
        )
    finish_span(
        engine_root=repository,
        trace_id=metadata["telemetry_trace_id"],
        span_id=intelligence.span_id,
        outcome=outcome,
        exit_code=exit_code,
    )
    dispatch_arguments = [
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
    if wait:
        dispatch_arguments.extend(["--wait-span-id", wait.span_id])
    assert run(*dispatch_arguments).returncode == 0
    validated = run("validate", "--run-dir", str(run_dir))
    assert validated.returncode == 0, validated.stderr


REVIEWER_PERSONAS = (
    ".claude/agents/plan-reviewer.md",
    ".claude/agents/code-critic.md",
)


def _persona_vocabulary(text: str, field: str) -> set[str]:
    """Parse `- `<field>`: `a`, `b`, ...` including its wrapped continuation lines."""
    lines = text.splitlines()
    start = next(index for index, line in enumerate(lines) if line.startswith(f"- `{field}`:"))
    block = [lines[start]]
    for line in lines[start + 1 :]:
        if line.startswith("- ") or not line.strip():
            break
        block.append(line)
    return set(re.findall(r"`([a-z][a-z-]*)`", " ".join(block)[len(f"- `{field}`:") :]))


def exported_schema(kind: str = "code") -> dict[str, object]:
    """The schema as the venue boundary receives it, via the tool's own export."""
    result = subprocess.run(
        [str(EVIDENCE), "schema", "--kind", kind],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def schema_enum(document: dict, field: str) -> set[str]:
    return set(document["properties"]["findings"]["items"]["properties"][field]["enum"])


@pytest.mark.parametrize("persona", REVIEWER_PERSONAS)
@pytest.mark.parametrize("field", ("severity", "state", "classification"))
def test_reviewer_persona_vocabularies_match_the_exported_schema(persona: str, field: str) -> None:
    """One source, reached the same way the venue reaches it.

    CH-12: the personas and the validator drifted silently, and an invented
    `major` severity discarded a whole review batch after the reviewing agent
    had exited. This used to compare the personas against the validator's
    in-process constants. Now it compares them against the *exported schema* —
    the identical artifact that constrains generation at the venue boundary — so
    the prose a reviewer reads, the enum a schema-constrained venue enforces, and
    the set the validator checks are provably the same list, and no test-only
    linkage stands between them.
    """
    documented = _persona_vocabulary((ROOT / persona).read_text(encoding="utf-8"), field)
    kind = "plan" if "plan-reviewer" in persona else "code"
    expected = schema_enum(exported_schema(kind), field)
    assert documented == expected, (
        f"{persona} documents {field} as {sorted(documented)} but the exported "
        f"{kind} schema enumerates {sorted(expected)}"
    )


class TestExportedSchema:
    """The schema is derived from the validator's sets, not restated beside them.

    Theme correction 2 in `briefs/kickoff-cross-harness-defects.md` asked for one
    source of truth for the reviewer vocabularies. A test that compared two
    hand-maintained lists was the interim form; deriving the schema from the sets
    the validator itself checks is the durable one, because there is no longer a
    second list to drift.
    """

    @pytest.mark.parametrize("kind", ("plan", "code"))
    def test_enums_come_from_the_validators_own_sets(self, kind: str) -> None:
        namespace = runpy.run_path(str(EVIDENCE), run_name="schema_source_test")
        document = exported_schema(kind)
        for field, constant in (
            ("severity", "SEVERITIES"),
            ("state", "STATES"),
            ("classification", "CLASSIFICATIONS"),
        ):
            assert schema_enum(document, field) == set(namespace[constant])

    def test_the_token_that_cost_a_review_is_not_expressible(self) -> None:
        """CH-12's `major` discarded five findings after a $8.67 critique."""
        assert "major" not in schema_enum(exported_schema(), "severity")
        assert "blocking" in schema_enum(exported_schema(), "severity")

    def test_the_transition_that_cost_a_review_is_still_a_state(self) -> None:
        """`verified` is legal as a value; only the *transition* to it is gated.

        CH-10 is a protocol gap, not an encoding one — a schema cannot fix it,
        and pretending otherwise by dropping `verified` from the enum would make
        the reviewer unable to report what it actually determined.
        """
        assert "verified" in schema_enum(exported_schema(), "state")

    @pytest.mark.parametrize("kind,prefix", (("plan", "PLAN"), ("code", "CODE")))
    def test_the_id_prefix_is_kind_specific(self, kind: str, prefix: str) -> None:
        document = exported_schema(kind)
        described = document["properties"]["findings"]["items"]["properties"]["id"]
        assert described["description"].startswith(f"{prefix}-F")

    def test_the_verdict_travels_inside_the_document(self) -> None:
        """Structured output leaves no markdown to carry a `## Verdict:` header.

        A schema constraining only the findings array would silently drop the
        orchestration contract that header exists to satisfy.
        """
        document = exported_schema()
        assert document["properties"]["verdict"]["enum"] == ["APPROVED", "REVISE"]
        assert set(document["required"]) == {"verdict", "summary", "findings"}

    def test_it_stays_inside_the_strict_structured_output_subset(self) -> None:
        """Both vendors accept a narrow schema dialect; exceed it and dispatch fails.

        Optionality is expressed as a nullable type with the key still required —
        strict mode has no other spelling for it — and no `pattern`/`minLength`
        appears anywhere, because those constraints live with the validator that
        still runs after the fact.
        """
        document = exported_schema()
        item = document["properties"]["findings"]["items"]
        assert item["additionalProperties"] is False
        assert document["additionalProperties"] is False
        assert set(item["required"]) == set(item["properties"])
        for field in ("resolved_in", "disposition"):
            assert item["properties"][field]["type"] == ["string", "null"]
        rendered = json.dumps(document)
        assert "pattern" not in rendered
        assert "minLength" not in rendered

    def test_export_is_byte_stable(self) -> None:
        """A schema that reorders between runs churns every artifact that pins it."""
        first = subprocess.run(
            [str(EVIDENCE), "schema", "--kind", "code"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        second = subprocess.run(
            [str(EVIDENCE), "schema", "--kind", "code"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert first.stdout == second.stdout
        assert first.stdout.strip()

    def test_every_validated_field_is_in_the_schema(self, tmp_path: Path) -> None:
        """Derivation is only single-source if it covers what the validator reads.

        A field the validator requires but the schema omits is a field a
        constrained venue cannot emit — the failure would land at ingestion, after
        the session is gone, which is precisely what this work removes.
        """
        namespace = runpy.run_path(str(EVIDENCE), run_name="schema_field_test")
        described = set(exported_schema()["properties"]["findings"]["items"]["properties"])
        source = ast.parse((ROOT / "bin" / "kickoff-evidence").read_text())
        validator = next(
            node
            for node in ast.walk(source)
            if isinstance(node, ast.FunctionDef) and node.name == "validate_finding"
        )
        read_fields = {
            node.args[0].value
            for node in ast.walk(validator)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "text_field"
            and node.args
            and isinstance(node.args[0], ast.Constant)
        }
        assert read_fields, "no validated text fields discovered"
        assert read_fields <= described, sorted(read_fields - described)
        assert {"affected_paths", "introduced_in", "resolved_in"} <= described
        assert namespace["FINDING_ID"].pattern


class TestCandidateLineage:
    """A run's candidate changes for reasons unrelated to the code under review.

    CH-8: `init` prints a candidate, and the next two orchestration steps — the
    `plan/INDEX.md` marker flip and the START log block — change it, because both
    are tracked files. An orchestrator that carried the init-time value into role
    prompts handed every role a value that was stale by construction; the
    reviewer stamped what it was given, and all seven of its findings were
    rejected. The tree was `c2e36624…`; the roles were told `7c9eb28c…`.
    """

    def test_init_seeds_the_lineage_with_the_initial_candidate(
        self, repository: Path, tmp_path: Path
    ) -> None:
        run_dir = tmp_path / "run"
        candidate = initialize(repository, run_dir)
        records = [
            json.loads(line)
            for line in (run_dir / "lineage.jsonl").read_text().splitlines()
            if line.strip()
        ]
        assert [item["candidate_id"] for item in records] == [candidate]
        assert records[0]["reason"] == "init"

    def test_current_candidate_recomputes_and_records(
        self, repository: Path, tmp_path: Path
    ) -> None:
        """This is the helper that exists so nobody caches the init-time value."""
        run_dir = tmp_path / "run"
        initial = initialize(repository, run_dir)
        (repository / "plan-index.md").write_text("marker flipped\n")

        result = run("current-candidate", "--run-dir", str(run_dir), "--reason", "step-3")

        assert result.returncode == 0, result.stderr
        recomputed = result.stdout.strip()
        assert recomputed != initial, "the tree changed, so the candidate must too"
        assert "candidate advanced" in result.stderr
        assert lineage_of(run_dir) == [initial, recomputed]

    def test_recording_the_same_candidate_twice_is_not_a_new_entry(
        self, repository: Path, tmp_path: Path
    ) -> None:
        run_dir = tmp_path / "run"
        initial = initialize(repository, run_dir)

        first = run("current-candidate", "--run-dir", str(run_dir))
        second = run("current-candidate", "--run-dir", str(run_dir))

        assert first.stdout.strip() == second.stdout.strip() == initial
        assert lineage_of(run_dir) == [initial]
        assert "candidate advanced" not in second.stderr

    def test_a_finding_stamped_with_an_earlier_recorded_candidate_is_accepted(
        self, repository: Path, tmp_path: Path
    ) -> None:
        """The whole point: an honest id must not be rejected for bookkeeping.

        The reviewer was dispatched against the candidate the orchestrator gave
        it and stamped that id. By the time its findings are ingested the tree
        has moved on. Refusing them discards correct work over a value the
        reviewer had no way to influence.
        """
        run_dir = tmp_path / "run"
        reviewed = initialize(repository, run_dir)
        (repository / "log.md").write_text("START block\n")
        current = run("current-candidate", "--run-dir", str(run_dir)).stdout.strip()
        assert current != reviewed
        artifact = tmp_path / "review.json"
        artifact.write_text(json.dumps({"findings": [finding("CODE-F001", reviewed)]}))

        result = run(
            "ingest-findings",
            "--run-dir",
            str(run_dir),
            "--kind",
            "code",
            "--candidate",
            current,
            "--no-review-span",
            "test fixture: no review pass was dispatched",
            "--artifact",
            str(artifact),
        )

        assert result.returncode == 0, result.stderr

    def test_a_candidate_the_run_never_recorded_is_still_refused(
        self, repository: Path, tmp_path: Path
    ) -> None:
        """Lineage acceptance widens the set; it does not open it.

        An `introduced_in` naming a tree this run never saw is not an
        orchestrator bookkeeping artifact — it is a finding bound to nothing.
        """
        run_dir = tmp_path / "run"
        candidate = initialize(repository, run_dir)
        artifact = tmp_path / "review.json"
        artifact.write_text(json.dumps({"findings": [finding("CODE-F001", "b" * 64)]}))

        result = run(
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
            str(artifact),
        )

        assert result.returncode != 0
        assert "is not a candidate this run recorded" in result.stderr

    def test_capture_change_and_mark_reviewed_extend_the_lineage(
        self, repository: Path, tmp_path: Path
    ) -> None:
        """Lineage is the run's own history, not a list anyone maintains."""
        run_dir = tmp_path / "run"
        initial = initialize(repository, run_dir)
        plan = tmp_path / "plan.md"
        plan.write_text("# Approved plan\n")
        captured = run("capture-plan", "--run-dir", str(run_dir), "--plan", str(plan))
        assert captured.returncode == 0, captured.stderr
        assert (
            run(
                "mark-plan-reviewed",
                "--run-dir",
                str(run_dir),
                "--plan",
                str(plan),
                "--expected-plan",
                captured.stdout.strip(),
            ).returncode
            == 0
        )
        (repository / "code.py").write_text("VALUE = 99\n")
        changed = run(
            "capture-change",
            "--run-dir",
            str(run_dir),
            "--selection-reason",
            "lineage regression",
        )
        assert changed.returncode == 0, changed.stderr

        lineage = lineage_of(run_dir)
        assert lineage[0] == initial
        assert changed.stdout.strip() in lineage
        assert len(set(lineage)) == len(lineage), "lineage must not repeat a candidate"


def test_handoff_refusal_names_the_directory_it_wants(repository: Path, tmp_path: Path) -> None:
    """CH-6: the constraint is right; the diagnostic was not actionable.

    Keeping role artifacts beside prompts and event streams in a scratch dir is
    the natural reading, so it fails on first use — and a message that says only
    "must be inside its run directory" leaves the reader to guess which one.
    """
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    outside = tmp_path / "scratch" / "role.json"
    outside.parent.mkdir(parents=True)

    result = run(
        "register-role-attempt",
        "--run-dir",
        str(run_dir),
        "--operation",
        "role.plan",
        "--attempt",
        "1",
        "--role",
        "planner",
        "--harness",
        "claude",
        "--reason",
        "initial",
        "--output",
        str(outside),
    )

    assert result.returncode != 0
    assert str(run_dir.resolve()) in result.stderr
    assert str(outside.resolve()) in result.stderr


class TestPinnedTreeIdRoot:
    """CH-9: a pinned copy must identify the repository, not its own bundle."""

    def _pinned(self, tmp_path: Path, repository_root: str | None) -> Path:
        bundle = tmp_path / "run" / "tools"
        (bundle / "lib").mkdir(parents=True)
        shutil.copy2(ROOT / "bin" / "kickoff-tree-id", bundle / "kickoff-tree-id")
        if repository_root is not None:
            (bundle.parent / "run.json").write_text(
                json.dumps({"repository_root": repository_root})
            )
        return bundle / "kickoff-tree-id"

    def test_it_resolves_the_root_the_run_recorded(self, tmp_path: Path) -> None:
        """`--root` was required on every pinned call and `/kickoff` never said so."""
        pinned = self._pinned(tmp_path, str(ROOT))

        result = subprocess.run(
            [sys.executable, str(pinned)],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0, result.stderr
        expected = subprocess.run(
            [sys.executable, str(ROOT / "bin" / "kickoff-tree-id"), "--root", str(ROOT)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.stdout.strip() == expected.stdout.strip()

    def test_a_non_repository_root_is_a_diagnostic_not_a_traceback(self, tmp_path: Path) -> None:
        """It died with a raw CalledProcessError, which names no remedy."""
        pinned = self._pinned(tmp_path, None)

        result = subprocess.run(
            [sys.executable, str(pinned)],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 2
        assert "is not a git repository" in result.stderr
        assert "--root" in result.stderr
        assert "Traceback" not in result.stderr


class TestEmittedReviewSchemaLoadsInBothVenues:
    """The schema is generated once and consumed by two different validators."""

    def emitted(self, kind: str) -> dict:
        result = run("schema", "--kind", kind)
        assert result.returncode == 0, result.stderr
        return json.loads(result.stdout)

    @pytest.mark.parametrize("kind", ("plan", "code"))
    def test_the_schema_declares_no_meta_schema(self, kind: str) -> None:
        """Claude's `--json-schema` rejects a `$schema` it cannot resolve.

        Measured: the draft 2020-12 URI made every Claude-venue review die in
        0.6 s with `no schema with key or ref "..."`, before the model ran. The
        key constrains nothing either vendor reads.
        """
        document = self.emitted(kind)
        assert "$schema" not in document
        assert "$schema" not in json.dumps(document["properties"])

    @pytest.mark.parametrize("kind", ("plan", "code"))
    def test_the_schema_compiles_under_the_codex_dialect(self, kind: str) -> None:
        """The document stays inside the strict structured-output subset."""
        document = self.emitted(kind)
        assert document["type"] == "object"
        assert document["additionalProperties"] is False
        assert set(document["required"]) == {"verdict", "summary", "findings"}
        assert document["properties"]["verdict"]["enum"] == ["APPROVED", "REVISE"]
        finding = document["properties"]["findings"]["items"]
        assert finding["type"] == "object"
        assert finding["additionalProperties"] is False
        assert set(finding["required"]) == set(finding["properties"])

    @pytest.mark.parametrize("kind", ("plan", "code"))
    def test_the_schema_stays_inside_the_strict_structured_output_subset(self, kind: str) -> None:
        """What both vendors accept, not merely what is valid JSON Schema."""
        document = self.emitted(kind)
        forbidden = {"pattern", "minLength", "maxLength", "format", "$ref", "$defs"}
        seen: list[str] = []

        def walk(node: object) -> None:
            if isinstance(node, dict):
                seen.extend(key for key in node if key in forbidden)
                if node.get("type") == "object":
                    assert node.get("additionalProperties") is False
                    assert set(node.get("required", [])) == set(node["properties"])
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for value in node:
                    walk(value)

        walk(document)
        assert seen == [], f"unsupported keywords for strict mode: {sorted(set(seen))}"

    def test_both_venues_are_handed_the_same_document(self, tmp_path: Path) -> None:
        """One generator, so a venue fix cannot drift into a second copy."""
        sys.path.insert(0, str(ROOT / "lib"))
        from agentic_starter.finding_schema import schema_json

        assert json.loads(schema_json("code")) == self.emitted("code")
        assert json.loads(schema_json("plan")) == self.emitted("plan")


def test_a_reviewer_may_reject_a_finding_it_previously_marked_addressed(
    repository: Path, tmp_path: Path
) -> None:
    """`addressed -> rejected-with-evidence` is a real review outcome.

    An implementer answers a finding with a counter-argument rather than a
    change; the reviewer agrees. Without this edge the only route to a truthful
    terminal state ran backwards through `open`.
    """
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    finding = {
        "id": "PLAN-F001",
        "severity": "blocking",
        "authority": "plan/phase-1.1.md",
        "evidence": "the plan asserts a precedent that does not exist",
        "affected_paths": ["plan/phase-1.1.md"],
        "required_outcome": "cite a real precedent or drop the claim",
        "introduced_in": candidate,
        "resolved_in": None,
        "state": "open",
        "classification": "initial",
        "disposition": None,
    }
    batch = tmp_path / "findings.json"

    def ingest(state: str, resolved: str | None) -> subprocess.CompletedProcess[str]:
        entry = dict(finding, state=state, resolved_in=resolved)
        batch.write_text(json.dumps({"findings": [entry]}))
        return run(
            "ingest-findings",
            "--run-dir",
            str(run_dir),
            "--kind",
            "plan",
            "--candidate",
            candidate,
            "--no-review-span",
            "test fixture: no review pass was dispatched",
            "--input",
            str(batch),
        )

    assert ingest("open", None).returncode == 0
    assert ingest("addressed", None).returncode == 0
    rejected = ingest("rejected-with-evidence", candidate)
    assert rejected.returncode == 0, rejected.stderr
    ledger = json.loads((run_dir / "findings.json").read_text())
    assert ledger["findings"][0]["state"] == "rejected-with-evidence"


def test_a_native_registration_emits_the_exact_span_recipe(
    repository: Path, tmp_path: Path
) -> None:
    """The pair must not be hand-built; a missing --model is unrecoverable."""
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    handoff = run_dir / "native.json"
    registered = run(
        "register-role-attempt",
        "--run-dir",
        str(run_dir),
        "--operation",
        "role.code-review",
        "--attempt",
        "1",
        "--role",
        "critic",
        "--harness",
        "native",
        "--model",
        "opus",
        "--effort",
        "xhigh",
        "--reason",
        "fallback",
        "--output",
        str(handoff),
    )
    assert registered.returncode == 0, registered.stderr
    recipe_path = Path(f"{handoff}.span-recipe.json")
    assert recipe_path.is_file(), registered.stdout
    assert str(recipe_path) in registered.stdout

    recipe = json.loads(recipe_path.read_text())
    metadata = json.loads((run_dir / "run.json").read_text())
    for category, argv in (("intelligence", recipe["intelligence"]), ("wait", recipe["wait"])):
        assert argv[1:3] == ["bin/execution-telemetry", "start"]
        assert argv[argv.index("--category") + 1] == category
        assert argv[argv.index("--operation") + 1] == "role.code-review"
        assert argv[argv.index("--attempt") + 1] == "1"
        # Both spans carry routing metadata, because validation joins each of
        # them against the registration field by field.
        assert argv[argv.index("--model") + 1] == "opus"
        assert argv[argv.index("--effort") + 1] == "xhigh"
        assert argv[argv.index("--role") + 1] == "critic"
        assert argv[argv.index("--harness") + 1] == "native"
    intelligence = recipe["intelligence"]
    assert (
        intelligence[intelligence.index("--parent-span-id") + 1]
        == metadata["telemetry_root_span_id"]
    )
    wait = recipe["wait"]
    assert wait[wait.index("--parent-span-id") + 1] == "<INTELLIGENCE_SPAN_ID>"

    resolved = run(
        "span-recipe",
        "--run-dir",
        str(run_dir),
        "--registration",
        str(handoff),
        "--intelligence-span-id",
        "a" * 32,
    )
    assert resolved.returncode == 0, resolved.stderr
    substituted = json.loads(resolved.stdout)["wait"]
    assert substituted[substituted.index("--parent-span-id") + 1] == "a" * 32
    assert "<INTELLIGENCE_SPAN_ID>" not in substituted


def test_a_delegated_registration_emits_no_span_recipe(repository: Path, tmp_path: Path) -> None:
    """`kickoff-config watch` builds those spans itself; a recipe would mislead."""
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    handoff = run_dir / "delegated.json"
    assert (
        run(
            "register-role-attempt",
            "--run-dir",
            str(run_dir),
            "--operation",
            "role.plan",
            "--attempt",
            "1",
            "--role",
            "planner",
            "--harness",
            "claude",
            "--model",
            "opus",
            "--reason",
            "initial",
            "--output",
            str(handoff),
        ).returncode
        == 0
    )
    assert not Path(f"{handoff}.span-recipe.json").exists()
    refused = run("span-recipe", "--run-dir", str(run_dir), "--registration", str(handoff))
    assert refused.returncode == 2
    assert "only for native role attempts" in refused.stderr


def broken_native_wait_join(
    repository: Path, run_dir: Path, *, omit_metadata: bool
) -> tuple[str, str]:
    """Reproduce the CH-14 native-path residue: a wait span opened without
    routing metadata, closed, and therefore unrepairable.

    Returns the intelligence and wait span ids.
    """
    metadata = json.loads((run_dir / "run.json").read_text())
    trace_id = metadata["telemetry_trace_id"]
    root_span_id = metadata["telemetry_root_span_id"]
    handoff = run_dir / "critic.json"
    assert (
        run(
            "register-role-attempt",
            "--run-dir",
            str(run_dir),
            "--operation",
            "role.code-review",
            "--attempt",
            "1",
            "--role",
            "critic",
            "--harness",
            "native",
            "--model",
            "opus",
            "--effort",
            "xhigh",
            "--reason",
            "fallback",
            "--output",
            str(handoff),
        ).returncode
        == 0
    )
    routing = {"role": "critic", "harness": "native", "model": "opus", "effort": "xhigh"}
    intelligence = start_span(
        engine_root=repository,
        trace_id=trace_id,
        parent_span_id=root_span_id,
        category="intelligence",
        operation="role.code-review",
        attempt=1,
        **routing,
    )
    opened = open_role_dispatch(run_dir, handoff, intelligence.span_id)
    assert opened.returncode == 0, opened.stderr
    wait_routing = {"role": "critic", "harness": "native"} if omit_metadata else routing
    wait = start_span(
        engine_root=repository,
        trace_id=trace_id,
        parent_span_id=intelligence.span_id,
        category="wait",
        operation="role.code-review",
        attempt=1,
        **wait_routing,
    )
    finish_span(
        engine_root=repository,
        trace_id=trace_id,
        span_id=wait.span_id,
        outcome="success",
        exit_code=0,
    )
    finish_span(
        engine_root=repository,
        trace_id=trace_id,
        span_id=intelligence.span_id,
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
        "accepted",
        "--idle-telemetry",
        "unavailable",
        "--intelligence-span-id",
        intelligence.span_id,
    ]
    if not omit_metadata:
        arguments.extend(["--wait-span-id", wait.span_id])
    recorded = run(*arguments)
    assert recorded.returncode == 0, recorded.stderr
    return intelligence.span_id, wait.span_id


def test_an_undeclared_broken_wait_join_still_refuses(repository: Path, tmp_path: Path) -> None:
    """The degradation is opt-in. Silence is not a pass."""
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    broken_native_wait_join(repository, run_dir, omit_metadata=True)
    validated = run("validate", "--run-dir", str(run_dir))
    assert validated.returncode == 2
    assert "dispatch and wait span ids do not agree" in validated.stderr


def test_a_declared_broken_wait_join_degrades_visibly(repository: Path, tmp_path: Path) -> None:
    """A defect owned in writing keeps the phase closable and stays legible.

    A validator that can only refuse converts one honest slip into a phase that
    can never close; the record is what keeps that from becoming a way to wave
    problems through.
    """
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    intelligence_span_id, wait_span_id = broken_native_wait_join(
        repository, run_dir, omit_metadata=True
    )
    declared = run(
        "record-telemetry-incomplete",
        "--run-dir",
        str(run_dir),
        "--operation",
        "role.code-review",
        "--attempt",
        "1",
        "--span-id",
        wait_span_id,
        "--missing-field",
        "model",
        "--missing-field",
        "effort",
        "--cause",
        "native wait span opened without routing metadata",
    )
    assert declared.returncode == 0, declared.stderr
    metadata = json.loads((run_dir / "run.json").read_text())
    attach_review_metrics(
        engine_root=repository,
        trace_id=metadata["telemetry_trace_id"],
        span_id=intelligence_span_id,
        findings_reported=0,
        actionable_findings=0,
    )
    validated = run("validate", "--run-dir", str(run_dir))
    assert validated.returncode == 0, validated.stderr

    complete_orchestration(repository, run_dir)
    finish_span(
        engine_root=repository,
        trace_id=metadata["telemetry_trace_id"],
        span_id=metadata["telemetry_root_span_id"],
        outcome="success",
    )
    finalize_trace(engine_root=repository, trace_id=metadata["telemetry_trace_id"])
    summary = run("timing-summary", "--run-dir", str(run_dir), "--format", "json")
    assert summary.returncode == 0, summary.stderr
    incomplete = json.loads(summary.stdout)["telemetry_incomplete"]
    assert len(incomplete) == 1
    assert incomplete[0]["operation"] == "role.code-review"
    assert incomplete[0]["attempt"] == 1
    assert incomplete[0]["span_id"] == wait_span_id
    assert incomplete[0]["missing_fields"] == ["effort", "model"]

    markdown = run("timing-summary", "--run-dir", str(run_dir), "--format", "markdown")
    assert markdown.returncode == 0, markdown.stderr
    # The operator reading the summary must see the gap, not infer it.
    assert "Telemetry-incomplete role attempts" in markdown.stdout
    assert wait_span_id in markdown.stdout
    assert "`model`" in markdown.stdout and "`effort`" in markdown.stdout
    assert "native wait span opened without routing metadata" in markdown.stdout


def test_a_declaration_cannot_excuse_a_wait_span_that_is_simply_absent(
    repository: Path, tmp_path: Path
) -> None:
    """Degradation covers a malformed span, never a missing one."""
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    metadata = json.loads((run_dir / "run.json").read_text())
    handoff = run_dir / "critic.json"
    assert (
        run(
            "register-role-attempt",
            "--run-dir",
            str(run_dir),
            "--operation",
            "role.code-review",
            "--attempt",
            "1",
            "--role",
            "critic",
            "--harness",
            "native",
            "--reason",
            "fallback",
            "--output",
            str(handoff),
        ).returncode
        == 0
    )
    intelligence = start_span(
        engine_root=repository,
        trace_id=metadata["telemetry_trace_id"],
        parent_span_id=metadata["telemetry_root_span_id"],
        category="intelligence",
        operation="role.code-review",
        attempt=1,
        role="critic",
        harness="native",
    )
    opened = open_role_dispatch(run_dir, handoff, intelligence.span_id)
    assert opened.returncode == 0, opened.stderr
    finish_span(
        engine_root=repository,
        trace_id=metadata["telemetry_trace_id"],
        span_id=intelligence.span_id,
        outcome="success",
        exit_code=0,
    )
    assert (
        run(
            "record-role-dispatch",
            "--run-dir",
            str(run_dir),
            "--registration",
            str(handoff),
            "--state",
            "accepted",
            "--idle-telemetry",
            "unavailable",
            "--intelligence-span-id",
            intelligence.span_id,
        ).returncode
        == 0
    )
    assert (
        run(
            "record-telemetry-incomplete",
            "--run-dir",
            str(run_dir),
            "--operation",
            "role.code-review",
            "--attempt",
            "1",
            "--span-id",
            "b" * 32,
            "--missing-field",
            "model",
            "--cause",
            "claiming a span nobody opened",
        ).returncode
        == 0
    )
    validated = run("validate", "--run-dir", str(run_dir))
    assert validated.returncode == 2
    assert "lacks one closed nested wait span" in validated.stderr


def test_a_declaration_must_name_the_span_the_trace_actually_carries(
    repository: Path, tmp_path: Path
) -> None:
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    broken_native_wait_join(repository, run_dir, omit_metadata=True)
    assert (
        run(
            "record-telemetry-incomplete",
            "--run-dir",
            str(run_dir),
            "--operation",
            "role.code-review",
            "--attempt",
            "1",
            "--span-id",
            "c" * 32,
            "--missing-field",
            "model",
            "--cause",
            "wrong span id",
        ).returncode
        == 0
    )
    validated = run("validate", "--run-dir", str(run_dir))
    assert validated.returncode == 2
    assert "names a span the trace does not carry" in validated.stderr


def test_a_declaration_does_not_excuse_defects_it_did_not_name(
    repository: Path, tmp_path: Path
) -> None:
    """Declaring `model` must not quietly wave `effort` through as well."""
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    _, wait_span_id = broken_native_wait_join(repository, run_dir, omit_metadata=True)
    assert (
        run(
            "record-telemetry-incomplete",
            "--run-dir",
            str(run_dir),
            "--operation",
            "role.code-review",
            "--attempt",
            "1",
            "--span-id",
            wait_span_id,
            "--missing-field",
            "model",
            "--cause",
            "only half the truth",
        ).returncode
        == 0
    )
    validated = run("validate", "--run-dir", str(run_dir))
    assert validated.returncode == 2
    assert "wait span effort does not match registration" in validated.stderr


def test_a_declaration_cannot_excuse_a_field_that_is_actually_correct(
    repository: Path, tmp_path: Path
) -> None:
    """A record that excuses nothing real is a record covering something up."""
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    _, wait_span_id = broken_native_wait_join(repository, run_dir, omit_metadata=False)
    assert (
        run(
            "record-telemetry-incomplete",
            "--run-dir",
            str(run_dir),
            "--operation",
            "role.code-review",
            "--attempt",
            "1",
            "--span-id",
            wait_span_id,
            "--missing-field",
            "model",
            "--cause",
            "nothing is actually wrong here",
        ).returncode
        == 0
    )
    validated = run("validate", "--run-dir", str(run_dir))
    assert validated.returncode == 2
    assert "which the wait span records correctly" in validated.stderr


def test_a_declaration_for_an_unregistered_attempt_refuses(
    repository: Path, tmp_path: Path
) -> None:
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    broken_native_wait_join(repository, run_dir, omit_metadata=False)
    assert (
        run(
            "record-telemetry-incomplete",
            "--run-dir",
            str(run_dir),
            "--operation",
            "role.plan",
            "--attempt",
            "7",
            "--span-id",
            "d" * 32,
            "--missing-field",
            "model",
            "--cause",
            "no such attempt",
        ).returncode
        == 0
    )
    validated = run("validate", "--run-dir", str(run_dir))
    assert validated.returncode == 2
    assert "unregistered attempts" in validated.stderr


def test_repinning_lets_an_active_run_adopt_a_repaired_tool(
    repository: Path, tmp_path: Path
) -> None:
    """The bundle protects a run from the tree; re-pinning is the way back.

    The snapshot exists so an active run survives the tree changing underneath
    it. That guarantee inverts when the change is a repair the run needs, so
    the crossing is explicit and prints both digests rather than being a silent
    overwrite.
    """
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    before = json.loads((run_dir / "run.json").read_text())["tool_bundle"]
    pinned = run_dir / "tools" / "kickoff-evidence"
    original = pinned.read_bytes()

    pinned.write_bytes(original + b"\n# drift\n")
    drifted = run("validate", "--run-dir", str(run_dir))
    assert drifted.returncode == 2
    assert "pinned tool changed" in drifted.stderr

    repinned = subprocess.run(
        [str(EVIDENCE), "repin-tools", "--run-dir", str(run_dir)],
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    assert repinned.returncode == 0, repinned.stderr
    after = json.loads((run_dir / "run.json").read_text())["tool_bundle"]
    assert before["manifest_sha256"] in repinned.stdout
    assert after["manifest_sha256"] in repinned.stdout
    assert pinned.read_bytes() == EVIDENCE.read_bytes()
    assert run("validate", "--run-dir", str(run_dir)).returncode == 0


def review_dispatch_with_outcome(
    repository: Path, run_dir: Path, outcome: str, exit_code: int
) -> str:
    """A native review attempt closed with the given outcome. Returns its span id."""
    metadata = json.loads((run_dir / "run.json").read_text())
    trace_id = metadata["telemetry_trace_id"]
    handoff = run_dir / "reviewer.json"
    assert (
        run(
            "register-role-attempt",
            "--run-dir",
            str(run_dir),
            "--operation",
            "role.code-review",
            "--attempt",
            "1",
            "--role",
            "critic",
            "--harness",
            "native",
            "--reason",
            "initial",
            "--output",
            str(handoff),
        ).returncode
        == 0
    )
    routing = {"role": "critic", "harness": "native"}
    intelligence = start_span(
        engine_root=repository,
        trace_id=trace_id,
        parent_span_id=metadata["telemetry_root_span_id"],
        category="intelligence",
        operation="role.code-review",
        attempt=1,
        **routing,
    )
    opened = open_role_dispatch(run_dir, handoff, intelligence.span_id)
    assert opened.returncode == 0, opened.stderr
    wait = start_span(
        engine_root=repository,
        trace_id=trace_id,
        parent_span_id=intelligence.span_id,
        category="wait",
        operation="role.code-review",
        attempt=1,
        **routing,
    )
    for span_id in (wait.span_id, intelligence.span_id):
        finish_span(
            engine_root=repository,
            trace_id=trace_id,
            span_id=span_id,
            outcome=outcome,
            exit_code=exit_code,
        )
    assert (
        run(
            "record-role-dispatch",
            "--run-dir",
            str(run_dir),
            "--registration",
            str(handoff),
            "--state",
            "accepted",
            "--idle-telemetry",
            "unavailable",
            "--intelligence-span-id",
            intelligence.span_id,
            "--wait-span-id",
            wait.span_id,
        ).returncode
        == 0
    )
    return intelligence.span_id


def finalize_for_summary(repository: Path, run_dir: Path) -> None:
    complete_orchestration(repository, run_dir)
    metadata = json.loads((run_dir / "run.json").read_text())
    finish_span(
        engine_root=repository,
        trace_id=metadata["telemetry_trace_id"],
        span_id=metadata["telemetry_root_span_id"],
        outcome="success",
    )
    finalize_trace(engine_root=repository, trace_id=metadata["telemetry_trace_id"])


def test_a_failed_review_dispatch_needs_no_convergence_metrics(
    repository: Path, tmp_path: Path
) -> None:
    """A venue failure produced no pass, so it has no findings to count.

    Requiring the integers anyway would make an upstream failure permanently
    unclosable instead of merely recorded — the attempt keeps its own truthful
    error outcome in the trace either way.
    """
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    review_dispatch_with_outcome(repository, run_dir, "error", 1)
    finalize_for_summary(repository, run_dir)
    summary = run("timing-summary", "--run-dir", str(run_dir), "--format", "json")
    assert summary.returncode == 0, summary.stderr


def test_a_successful_review_dispatch_still_requires_convergence_metrics(
    repository: Path, tmp_path: Path
) -> None:
    """The exemption is scoped to failure; a real pass must still be measured."""
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    span_id = review_dispatch_with_outcome(repository, run_dir, "success", 0)
    # Metrics attach before finalization, so the refusal is proved on a second
    # run that reaches the same point without them.
    unmeasured_dir = tmp_path / "unmeasured"
    initialize(repository, unmeasured_dir)
    review_dispatch_with_outcome(repository, unmeasured_dir, "success", 0)
    finalize_for_summary(repository, unmeasured_dir)
    refused = run("timing-summary", "--run-dir", str(unmeasured_dir), "--format", "json")
    assert refused.returncode == 2
    assert "lacks convergence metrics" in refused.stderr

    metadata = json.loads((run_dir / "run.json").read_text())
    attach_review_metrics(
        engine_root=repository,
        trace_id=metadata["telemetry_trace_id"],
        span_id=span_id,
        findings_reported=3,
        actionable_findings=1,
    )
    finalize_for_summary(repository, run_dir)
    accepted = run("timing-summary", "--run-dir", str(run_dir), "--format", "json")
    assert accepted.returncode == 0, accepted.stderr


def test_a_nested_gate_span_needs_no_evidence_row(repository: Path, tmp_path: Path) -> None:
    """`bin/check` opens a gate span per sub-gate beneath its own gate span.

    Those children are the observed command's instrumentation, not gates the
    orchestrator ran, so they carry no `run-gate` row. Requiring one made a
    complete acceptance close fail with every sub-gate reported unregistered.
    """
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    # Open the child the way bin/check does: from inside the observed command,
    # using the AGENTIC_STARTER_EXECUTION_* context run-gate exports to it.
    nesting = tmp_path / "nested-gate.sh"
    nesting.write_text(
        "#!/bin/sh\n"
        f'span=$("{sys.executable}" "{ROOT / "bin" / "execution-telemetry"}" start'
        ' --trace-id "$AGENTIC_STARTER_EXECUTION_TRACE_ID"'
        ' --parent-span-id "$AGENTIC_STARTER_EXECUTION_PARENT_SPAN_ID"'
        " --category gate --operation gate.check.lint"
        ' | sed -n \'s/.*"span_id":"\\([0-9a-f]*\\)".*/\\1/p\')\n'
        f'"{sys.executable}" "{ROOT / "bin" / "execution-telemetry"}" finish'
        ' --trace-id "$AGENTIC_STARTER_EXECUTION_TRACE_ID" --span-id "$span"'
        " --outcome success --exit-code 0\n"
    )
    nesting.chmod(0o755)
    executed = run(
        "run-gate",
        "--run-dir",
        str(run_dir),
        "--candidate",
        candidate,
        "--operation",
        "gate.check-all",
        "--selection-reason",
        "final",
        "--warning-count",
        "0",
        "--final",
        "--",
        str(nesting),
        cwd=repository,
    )
    assert executed.returncode == 0, executed.stderr
    metadata = json.loads((run_dir / "run.json").read_text())
    nested = [
        span
        for span in closed_spans(engine_root=repository, trace_id=metadata["telemetry_trace_id"])
        if span["operation"] == "gate.check.lint"
    ]
    assert len(nested) == 1, "the observed command must have opened its own gate span"
    assert nested[0]["parent_span_id"] != metadata["telemetry_root_span_id"]
    finalize_for_summary(repository, run_dir)
    summary = run("timing-summary", "--run-dir", str(run_dir), "--format", "json")
    assert summary.returncode == 0, summary.stderr


def test_an_orchestrator_gate_span_without_evidence_still_refuses(
    repository: Path, tmp_path: Path
) -> None:
    """The exemption is parentage-scoped: a root-child gate must be recorded."""
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    assert (
        run(
            "run-gate",
            "--run-dir",
            str(run_dir),
            "--candidate",
            candidate,
            "--operation",
            "gate.check-all",
            "--selection-reason",
            "final",
            "--warning-count",
            "0",
            "--final",
            "--",
            "/usr/bin/true",
            cwd=repository,
        ).returncode
        == 0
    )
    metadata = json.loads((run_dir / "run.json").read_text())
    orphan = start_span(
        engine_root=repository,
        trace_id=metadata["telemetry_trace_id"],
        parent_span_id=metadata["telemetry_root_span_id"],
        category="gate",
        operation="gate.unrecorded",
    )
    finish_span(
        engine_root=repository,
        trace_id=metadata["telemetry_trace_id"],
        span_id=orphan.span_id,
        outcome="success",
        exit_code=0,
    )
    finalize_for_summary(repository, run_dir)
    refused = run("timing-summary", "--run-dir", str(run_dir), "--format", "json")
    assert refused.returncode == 2
    assert "unregistered=" + orphan.span_id in refused.stderr


def test_absent_gate_artifact_records_the_gate_instead_of_orphaning_its_span(
    repository: Path, tmp_path: Path
) -> None:
    """A gate whose artifact never appeared must still be recorded.

    `run_observed` opens and closes the gate span before the artifact is
    inspected. Raising on an absent artifact therefore stranded a closed,
    root-parented gate span with no evidence row -- and `validate` refuses on
    exactly that, with no supported repair (`record-gate` writes
    `telemetry_span_id: None`, so it cannot adopt the span). Observed in a
    derived project's acceptance close: a passing `./bin/check all` gate named
    an artifact its script had not yet written, which made the run's evidence
    bundle permanently unvalidatable.
    """
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    missing = tmp_path / "never-written.txt"
    result = run(
        "run-gate",
        "--run-dir",
        str(run_dir),
        "--candidate",
        candidate,
        "--operation",
        "gate.focused",
        "--selection-reason",
        "artifact absent after a clean run",
        "--warning-count",
        "0",
        "--artifact",
        str(missing),
        "--",
        "/usr/bin/true",
        cwd=repository,
    )
    assert result.returncode == 0, result.stderr
    assert "gate artifact absent" in result.stderr
    gate = json.loads((run_dir / "gates.jsonl").read_text())
    assert gate["exit_code"] == 0
    assert gate["artifact_sha256"] is None
    assert gate["telemetry_span_id"] is not None
    # The whole point: the bundle still validates, so the span is not orphaned.
    assert run("validate", "--run-dir", str(run_dir)).returncode == 0


def test_unusable_gate_artifact_path_is_refused_before_the_command_runs(
    repository: Path, tmp_path: Path
) -> None:
    """An artifact precondition must fail before a span exists, not after."""
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    marker = tmp_path / "command-ran.txt"
    toucher = tmp_path / "touch.sh"
    toucher.write_text(f"#!/bin/sh\nprintf 'ran\\n' > {marker}\nexit 0\n")
    toucher.chmod(0o755)
    result = run(
        "run-gate",
        "--run-dir",
        str(run_dir),
        "--candidate",
        candidate,
        "--operation",
        "gate.focused",
        "--selection-reason",
        "artifact directory does not exist",
        "--warning-count",
        "0",
        "--artifact",
        str(tmp_path / "no-such-dir" / "artifact.txt"),
        "--",
        str(toucher),
        cwd=repository,
    )
    assert result.returncode == 2
    assert "gate artifact directory does not exist" in result.stderr
    assert not marker.exists(), "the command must not run when the precondition fails"
    assert not (run_dir / "gates.jsonl").read_text().strip()
    assert run("validate", "--run-dir", str(run_dir)).returncode == 0


def test_ingest_findings_refuses_when_the_review_span_is_omitted(
    repository: Path, tmp_path: Path
) -> None:
    """An omitted --review-span-id is unrepairable, so it must fail closed.

    Convergence metrics attach to the review pass's own intelligence span, and a
    span is immutable once its trace is finalized. A derived project once
    omitted the flag on every call; by the time `timing-summary` refused, the
    trace was finalized and the only way to attach the metrics late would have
    been to re-ingest earlier artifacts, driving `verified -> open` and
    reopening resolved findings to satisfy a validator. The lesson belongs in
    the machinery, not in LOG.md.
    """
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    evidence = tmp_path / "findings.json"
    evidence.write_text(json.dumps({"findings": [finding("CODE-F001", candidate)]}))

    result = run(
        "ingest-findings",
        "--run-dir",
        str(run_dir),
        "--kind",
        "code",
        "--candidate",
        candidate,
        "--input",
        str(evidence),
    )

    assert result.returncode == 2
    assert "requires --review-span-id" in result.stderr
    assert "finalized trace cannot be repaired" in result.stderr
    assert "--no-review-span" in result.stderr
    # `init` creates the ledger, so the proof is that it is still empty: a
    # refused ingest must not half-write the findings it declined to accept.
    assert json.loads((run_dir / "findings.json").read_text())["findings"] == []
    assert not (run_dir / "review-metrics-omitted.jsonl").exists()


def test_explicit_opt_out_records_the_omission_instead_of_hiding_it(
    repository: Path, tmp_path: Path
) -> None:
    """The escape hatch exists for non-review ingests, and it is never silent.

    An orchestrator-authored state transition -- recording that a plan revision
    addressed its findings, for instance -- has no dispatched review pass and so
    no intelligence span to carry metrics. That ingest is legitimate; what is
    not legitimate is letting it look like a measured review pass.
    """
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    evidence = tmp_path / "findings.json"
    evidence.write_text(json.dumps({"findings": [finding("CODE-F001", candidate)]}))

    result = run(
        "ingest-findings",
        "--run-dir",
        str(run_dir),
        "--kind",
        "code",
        "--candidate",
        candidate,
        "--no-review-span",
        "orchestrator-authored addressed transition; no review pass dispatched",
        "--input",
        str(evidence),
    )

    assert result.returncode == 0, result.stderr
    assert "WITHOUT review convergence metrics" in result.stderr
    omissions = [
        json.loads(line)
        for line in (run_dir / "review-metrics-omitted.jsonl").read_text().splitlines()
        if line.strip()
    ]
    assert len(omissions) == 1
    assert omissions[0]["kind"] == "code"
    assert omissions[0]["candidate_id"] == candidate
    assert omissions[0]["findings_reported"] == 1
    assert "orchestrator-authored" in omissions[0]["reason"]
    assert json.loads((run_dir / "findings.json").read_text())["findings"][0]["id"] == "CODE-F001"


def test_the_two_review_span_flags_are_mutually_exclusive(repository: Path, tmp_path: Path) -> None:
    """Naming a span and disclaiming one at once is incoherent, not a preference."""
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    evidence = tmp_path / "findings.json"
    evidence.write_text(json.dumps({"findings": [finding("CODE-F001", candidate)]}))

    result = run(
        "ingest-findings",
        "--run-dir",
        str(run_dir),
        "--kind",
        "code",
        "--candidate",
        candidate,
        "--review-span-id",
        "f" * 32,
        "--no-review-span",
        "cannot be both",
        "--input",
        str(evidence),
    )

    assert result.returncode == 2
    assert "mutually exclusive" in result.stderr


def test_the_opt_out_reason_cannot_be_blank(repository: Path, tmp_path: Path) -> None:
    """An unexplained omission is the silence the flag exists to prevent."""
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    evidence = tmp_path / "findings.json"
    evidence.write_text(json.dumps({"findings": [finding("CODE-F001", candidate)]}))

    result = run(
        "ingest-findings",
        "--run-dir",
        str(run_dir),
        "--kind",
        "code",
        "--candidate",
        candidate,
        "--no-review-span",
        "   ",
        "--input",
        str(evidence),
    )

    assert result.returncode == 2
    assert "nonempty reason" in result.stderr


def open_setup_span(repository: Path) -> tuple:
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
    return handle, setup


def lane_init(
    repository: Path,
    run_dir: Path,
    *,
    review_lane: str,
    evidence_lane: str | None,
    route: str,
) -> subprocess.CompletedProcess[str]:
    handle, setup = open_setup_span(repository)
    arguments = [
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
        handle.trace_id,
        "--telemetry-root-span-id",
        handle.span_id,
        "--initial-orchestration-span-id",
        setup.span_id,
        "--review-lane",
        review_lane,
        "--follow-up-route",
        route,
    ]
    if evidence_lane is not None:
        arguments[-2:-2] = ["--evidence-lane", evidence_lane]
    return run(*arguments)


def test_init_requires_an_evidence_lane(repository: Path, tmp_path: Path) -> None:
    result = lane_init(
        repository,
        tmp_path / "run",
        review_lane="full",
        evidence_lane=None,
        route="initial",
    )

    assert result.returncode == 2
    assert "--evidence-lane" in result.stderr


def test_one_shot_lane_derives_role_and_stage_requirements(
    repository: Path, tmp_path: Path
) -> None:
    run_dir = tmp_path / "run"
    result = lane_init(
        repository,
        run_dir,
        review_lane="one-shot",
        evidence_lane="full",
        route="initial",
    )

    assert result.returncode == 0, result.stderr
    metadata = json.loads((run_dir / "run.json").read_text())
    assert metadata["review_lane"] == "one-shot"
    assert metadata["evidence_lane"] == "full"
    assert metadata["required_initial_role_operations"] == [
        "role.code-review",
        "role.implement",
    ]
    assert "orchestration.planning" not in metadata["required_orchestration_operations"]


def test_one_shot_is_not_a_frontmatter_evidence_lane(repository: Path, tmp_path: Path) -> None:
    result = lane_init(
        repository,
        tmp_path / "run",
        review_lane="full",
        evidence_lane="one-shot",
        route="initial",
    )

    assert result.returncode == 2


def test_light_evidence_lane_demotes_missing_role_requirement(
    repository: Path, tmp_path: Path
) -> None:
    light_dir = tmp_path / "light-run"
    initialized = lane_init(
        repository,
        light_dir,
        review_lane="full",
        evidence_lane="light",
        route="initial",
    )
    assert initialized.returncode == 0, initialized.stderr

    result = run("validate", "--run-dir", str(light_dir))

    assert result.returncode == 0, result.stderr


def test_full_evidence_lane_still_requires_initial_roles(repository: Path, tmp_path: Path) -> None:
    full_dir = tmp_path / "full-run"
    initialized = lane_init(
        repository,
        full_dir,
        review_lane="full",
        evidence_lane="full",
        route="initial",
    )
    assert initialized.returncode == 0, initialized.stderr

    result = run("validate", "--run-dir", str(full_dir))

    assert result.returncode == 2
    assert "missing required initial role attempt" in result.stderr


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


def journal_of(run_dir: Path) -> list[dict[str, object]]:
    path = run_dir / "ingest-log.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def derived_records(run_dir: Path) -> list[dict[str, object]]:
    path = run_dir / "derived-metrics.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def derive(
    run_dir: Path,
    *,
    attempt: int,
    span_id: str,
    refusal_class: str,
    artifact: Path,
    corroborating: Path | None = None,
    id_map: tuple[str, ...] = (),
    cause: str = "the critic pass ran; its batch was structurally refused",
) -> subprocess.CompletedProcess[str]:
    arguments = [
        "attach-derived-metrics",
        "--run-dir",
        str(run_dir),
        "--operation",
        "role.code-review",
        "--attempt",
        str(attempt),
        "--span-id",
        span_id,
        "--refusal-class",
        refusal_class,
        "--refused-artifact",
        str(artifact),
    ]
    if corroborating is not None:
        arguments.extend(["--corroborating-artifact", str(corroborating)])
    for entry in id_map:
        arguments.extend(["--id-map", entry])
    arguments.extend(["--cause", cause])
    return run(*arguments)


def stale_resolution(
    repository: Path,
    tmp_path: Path,
    run_dir: Path,
    *,
    seed: list[dict[str, object]] | None = None,
    batch: list[dict[str, object]] | None = None,
    attempt: int = 1,
    name: str = "critic-review.md",
) -> tuple[str, str, Path]:
    """A successful critic pass whose batch was refused on a stale `resolved_in`.

    Returns the candidate, the review span id, and the refused artifact.
    """
    candidate = initialize(repository, run_dir)
    if seed:
        assert ingest(run_dir, tmp_path, seed, candidate=candidate).returncode == 0
    span_id = native_accepted_attempt(repository, run_dir, "role.code-review", "critic", attempt)
    findings = batch or [
        finding("CODE-F002", candidate, resolved_in="0" * 64),
        finding("CODE-F003", candidate),
    ]
    artifact = review_artifact(tmp_path / name, findings)
    refused = ingest_artifact(run_dir, candidate, artifact, span_id)
    assert refused.returncode == 2, refused.stdout
    assert "resolved_in does not match" in refused.stderr
    return candidate, span_id, artifact


def test_an_unmeasured_review_pass_refuses_at_validate_before_finalization(
    repository: Path, tmp_path: Path
) -> None:
    """The latch. A repair exists only while the trace is open.

    `validate` used to check review metrics only under `--require-final`, so a
    run passed validation all night with unmeasured passes and discovered the
    gap at `timing-summary`, after finalization, when the only "repair" left
    was re-ingesting earlier artifacts and driving `verified -> open`.
    """
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    span_id = native_accepted_attempt(repository, run_dir, "role.code-review", "critic", 1)

    validated = run("validate", "--run-dir", str(run_dir))

    assert validated.returncode == 2, "validate accepted a run with an unmeasured review pass"
    assert "review passes lack convergence metrics" in validated.stderr
    assert "role.code-review#1" in validated.stderr
    assert span_id in validated.stderr
    # The refusal has to name the repair, and the window it is available in.
    assert "--review-span-id" in validated.stderr
    assert "attach-derived-metrics" in validated.stderr


def test_the_latch_leaves_a_measured_pass_alone(repository: Path, tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    span_id = native_accepted_attempt(repository, run_dir, "role.code-review", "critic", 1)
    artifact = review_artifact(tmp_path / "critic.md", [finding("CODE-F001", candidate)])
    assert ingest_artifact(run_dir, candidate, artifact, span_id).returncode == 0

    assert run("validate", "--run-dir", str(run_dir)).returncode == 0


def test_the_latch_keeps_the_failed_dispatch_exemption(repository: Path, tmp_path: Path) -> None:
    """A venue failure produced no pass, so the latch has nothing to demand."""
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    review_dispatch_with_outcome(repository, run_dir, "error", 1)

    assert run("validate", "--run-dir", str(run_dir)).returncode == 0


def test_the_light_evidence_lane_is_untouched_by_the_latch(
    repository: Path, tmp_path: Path
) -> None:
    """Light-lane metrics ride `review-metrics-omitted.jsonl`, not the span."""
    run_dir = tmp_path / "run"
    initialize(repository, run_dir, evidence_lane="light")
    native_accepted_attempt(repository, run_dir, "role.code-review", "critic", 1)

    assert run("validate", "--run-dir", str(run_dir)).returncode == 0


def test_a_refused_ingest_is_journaled_with_its_typed_codes(
    repository: Path, tmp_path: Path
) -> None:
    """The journal is what makes a refusal a machine-checkable fact later."""
    run_dir = tmp_path / "run"
    candidate, span_id, artifact = stale_resolution(repository, tmp_path, run_dir)

    rows = journal_of(run_dir)
    assert len(rows) == 1
    row = rows[0]
    assert row["outcome"] == "refused"
    assert row["kind"] == "code"
    assert row["refusal_codes"] == ["resolved-in-not-current"]
    assert row["review_span_id"] == span_id
    assert row["candidate_id"] == candidate
    assert row["findings_reported"] == 2
    assert row["actionable_findings"] is None
    assert "resolved_in does not match" in row["refusal_detail"]
    assert row["artifact_sha256"] == hashlib.sha256(artifact.read_bytes()).hexdigest()
    # Captured before any mutation, and the refusal really left the ledger alone.
    assert row["ledger_before"] == {}
    assert json.loads((run_dir / "findings.json").read_text())["findings"] == []


def test_an_accepted_ingest_is_journaled_after_the_merge_lands(
    repository: Path, tmp_path: Path
) -> None:
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    span_id = native_accepted_attempt(repository, run_dir, "role.code-review", "critic", 1)
    artifact = review_artifact(
        tmp_path / "critic.md",
        [finding("CODE-F001", candidate), finding("CODE-F002", candidate)],
    )
    assert ingest_artifact(run_dir, candidate, artifact, span_id).returncode == 0

    rows = journal_of(run_dir)
    assert len(rows) == 1
    assert rows[0]["outcome"] == "accepted"
    assert rows[0]["refusal_codes"] == []
    assert rows[0]["refusal_detail"] is None
    assert rows[0]["findings_reported"] == 2
    assert rows[0]["actionable_findings"] == 2
    assert rows[0]["ledger_before"] == {}
    # The row is written after `findings.json`, so it can never claim a merge
    # that did not land.
    assert len(json.loads((run_dir / "findings.json").read_text())["findings"]) == 2


def test_an_orchestrator_error_is_never_journaled(repository: Path, tmp_path: Path) -> None:
    """The journal describes review batches, not malformed invocations."""
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    span_id = native_accepted_attempt(repository, run_dir, "role.code-review", "critic", 1)
    artifact = review_artifact(tmp_path / "critic.md", [finding("CODE-F001", candidate)])

    mismatched = run(
        "ingest-findings",
        "--run-dir",
        str(run_dir),
        "--kind",
        "code",
        "--candidate",
        "e" * 64,
        "--review-span-id",
        span_id,
        "--artifact",
        str(artifact),
    )
    assert mismatched.returncode == 2
    assert "candidate mismatch" in mismatched.stderr

    conflicting = run(
        "ingest-findings",
        "--run-dir",
        str(run_dir),
        "--kind",
        "code",
        "--candidate",
        candidate,
        "--review-span-id",
        span_id,
        "--no-review-span",
        "both at once",
        "--artifact",
        str(artifact),
    )
    assert conflicting.returncode == 2
    assert "mutually exclusive" in conflicting.stderr

    assert journal_of(run_dir) == []

    # ...while a refusal about the batch's own content does land, so the absence
    # above is a boundary rather than a journal that never writes anything.
    stale = review_artifact(
        tmp_path / "stale.md",
        [finding("CODE-F002", candidate, resolved_in="0" * 64)],
    )
    assert ingest_artifact(run_dir, candidate, stale, span_id).returncode == 2
    assert [row["refusal_codes"] for row in journal_of(run_dir)] == [["resolved-in-not-current"]]


def test_repeated_refused_ingests_append_rather_than_refuse(
    repository: Path, tmp_path: Path
) -> None:
    """A deliberate divergence from `record-telemetry-incomplete`.

    Re-ingesting a refused batch is the normal recovery, so repeated rows for
    one artifact are the expected shape rather than a duplicate-key defect.
    """
    run_dir = tmp_path / "run"
    candidate, span_id, artifact = stale_resolution(repository, tmp_path, run_dir)

    again = ingest_artifact(run_dir, candidate, artifact, span_id)
    assert again.returncode == 2

    rows = journal_of(run_dir)
    assert len(rows) == 2
    assert {row["artifact_sha256"] for row in rows} == {rows[0]["artifact_sha256"]}


def test_a_derivation_counts_the_whole_ledger_not_only_its_own_batch(
    repository: Path, tmp_path: Path
) -> None:
    """The regression the policy names: pre-existing actionable entries count.

    `ingest-findings` computes `actionable_findings` over the *whole merged
    ledger*, namespace-filtered. A by-hand rule that counted only the batch's
    own non-merging findings would answer 2 here; the ledger already holds one
    `open` entry the batch never mentions, so the answer is 3.
    """
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    assert (
        ingest(run_dir, tmp_path, [finding("CODE-F001", candidate)], candidate=candidate).returncode
        == 0
    )
    span_id = native_accepted_attempt(repository, run_dir, "role.code-review", "critic", 1)
    artifact = review_artifact(
        tmp_path / "critic.md",
        [
            finding("CODE-F002", candidate, resolved_in="0" * 64),
            finding("CODE-F003", candidate),
        ],
    )
    assert ingest_artifact(run_dir, candidate, artifact, span_id).returncode == 2
    assert journal_of(run_dir)[-1]["ledger_before"] == {"CODE-F001": "open"}

    derived = derive(
        run_dir,
        attempt=1,
        span_id=span_id,
        refusal_class="resolved-in-not-current-candidate",
        artifact=artifact,
    )

    assert derived.returncode == 0, derived.stderr
    assert "findings_reported=2" in derived.stdout
    assert "actionable_findings=3" in derived.stdout, (
        "the derived count dropped the base term: a pre-existing open "
        "ledger entry the batch never mentioned was not counted"
    )
    record = derived_records(run_dir)[0]
    assert record["findings_reported"] == 2
    assert record["actionable_findings"] == 3


def test_a_derivation_never_attaches_to_the_span(repository: Path, tmp_path: Path) -> None:
    """The record is an overlay. Laundering it onto the span is the failure mode.

    `attach_review_metrics` refuses on a finalized trace, which is exactly where
    this gap bites, and a derived number written onto a span its ingest never
    produced would be indistinguishable from a measured one.
    """
    run_dir = tmp_path / "run"
    _, span_id, artifact = stale_resolution(repository, tmp_path, run_dir)
    assert (
        derive(
            run_dir,
            attempt=1,
            span_id=span_id,
            refusal_class="resolved-in-not-current-candidate",
            artifact=artifact,
        ).returncode
        == 0
    )

    metadata = json.loads((run_dir / "run.json").read_text())
    span = closed_span(
        engine_root=repository,
        trace_id=metadata["telemetry_trace_id"],
        span_id=span_id,
    )
    assert "findings_reported" not in span
    assert "actionable_findings" not in span
    assert run("validate", "--run-dir", str(run_dir)).returncode == 0


def test_a_derivation_refuses_when_the_ingest_was_never_attempted(
    repository: Path, tmp_path: Path
) -> None:
    """A derivation stands on a recorded refusal, never on an account of one."""
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    span_id = native_accepted_attempt(repository, run_dir, "role.code-review", "critic", 1)
    artifact = review_artifact(
        tmp_path / "critic.md", [finding("CODE-F002", candidate, resolved_in="0" * 64)]
    )

    derived = derive(
        run_dir,
        attempt=1,
        span_id=span_id,
        refusal_class="resolved-in-not-current-candidate",
        artifact=artifact,
    )

    assert derived.returncode == 2
    assert "no refused ingest of this artifact is recorded" in derived.stderr
    assert derived_records(run_dir) == []


def test_a_derivation_refuses_a_batch_that_carried_another_defect(
    repository: Path, tmp_path: Path
) -> None:
    """Extra codes refuse: a batch with a substance defect was not a pass."""
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    span_id = native_accepted_attempt(repository, run_dir, "role.code-review", "critic", 1)
    broken = finding("CODE-F002", candidate, resolved_in="0" * 64)
    broken["severity"] = "catastrophic"
    artifact = review_artifact(tmp_path / "critic.md", [broken])
    assert ingest_artifact(run_dir, candidate, artifact, span_id).returncode == 2
    assert sorted(journal_of(run_dir)[-1]["refusal_codes"]) == ["severity-invalid"]

    derived = derive(
        run_dir,
        attempt=1,
        span_id=span_id,
        refusal_class="resolved-in-not-current-candidate",
        artifact=artifact,
    )

    assert derived.returncode == 2
    assert "does not match the declared class" in derived.stderr
    assert "severity-invalid" in derived.stderr


def test_a_derivation_refuses_a_refusal_recorded_against_another_span(
    repository: Path, tmp_path: Path
) -> None:
    """One refused artifact is evidence about the pass whose ingest named it."""
    run_dir = tmp_path / "run"
    _, span_id, artifact = stale_resolution(repository, tmp_path, run_dir)
    other = native_accepted_attempt(repository, run_dir, "role.code-review", "critic", 2)

    derived = derive(
        run_dir,
        attempt=2,
        span_id=other,
        refusal_class="resolved-in-not-current-candidate",
        artifact=artifact,
    )

    assert derived.returncode == 2, "a refusal recorded against another span backed this derivation"
    assert "names a different review span" in derived.stderr
    assert span_id != other


def test_a_derivation_refuses_when_the_span_already_carries_metrics(
    repository: Path, tmp_path: Path
) -> None:
    """A pass whose ingest did land has nothing to derive."""
    run_dir = tmp_path / "run"
    candidate, span_id, artifact = stale_resolution(repository, tmp_path, run_dir)
    corrected = review_artifact(
        tmp_path / "critic-2.md",
        [finding("CODE-F002", candidate), finding("CODE-F003", candidate)],
    )
    assert ingest_artifact(run_dir, candidate, corrected, span_id).returncode == 0

    derived = derive(
        run_dir,
        attempt=1,
        span_id=span_id,
        refusal_class="resolved-in-not-current-candidate",
        artifact=artifact,
    )

    assert derived.returncode == 2
    assert "already carries convergence metrics" in derived.stderr


def test_a_duplicate_derivation_refuses(repository: Path, tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    _, span_id, artifact = stale_resolution(repository, tmp_path, run_dir)
    first = derive(
        run_dir,
        attempt=1,
        span_id=span_id,
        refusal_class="resolved-in-not-current-candidate",
        artifact=artifact,
    )
    assert first.returncode == 0, first.stderr

    second = derive(
        run_dir,
        attempt=1,
        span_id=span_id,
        refusal_class="resolved-in-not-current-candidate",
        artifact=artifact,
    )

    assert second.returncode == 2
    assert "duplicate derived-metrics record" in second.stderr


def malformed_id_run(repository: Path, tmp_path: Path, run_dir: Path) -> tuple[str, str, Path]:
    """A critic pass whose batch was refused for malformed finding ids."""
    candidate = initialize(repository, run_dir)
    span_id = native_accepted_attempt(repository, run_dir, "role.code-review", "critic", 1)
    artifact = review_artifact(
        tmp_path / "critic.md",
        [finding("CODE-F1", candidate), finding("CODE-F2", candidate)],
    )
    refused = ingest_artifact(run_dir, candidate, artifact, span_id)
    assert refused.returncode == 2
    assert sorted(journal_of(run_dir)[-1]["refusal_codes"]) == ["id-format"]
    return candidate, span_id, artifact


def test_an_id_format_derivation_requires_a_total_injective_bijection(
    repository: Path, tmp_path: Path
) -> None:
    run_dir = tmp_path / "run"
    _, span_id, artifact = malformed_id_run(repository, tmp_path, run_dir)

    missing = derive(
        run_dir,
        attempt=1,
        span_id=span_id,
        refusal_class="finding-id-format",
        artifact=artifact,
    )
    assert missing.returncode == 2
    assert "--id-map is required" in missing.stderr

    partial = derive(
        run_dir,
        attempt=1,
        span_id=span_id,
        refusal_class="finding-id-format",
        artifact=artifact,
        id_map=("CODE-F1=CODE-F011",),
    )
    assert partial.returncode == 2
    assert "must name exactly the artifact's malformed finding ids" in partial.stderr

    collapsing = derive(
        run_dir,
        attempt=1,
        span_id=span_id,
        refusal_class="finding-id-format",
        artifact=artifact,
        id_map=("CODE-F1=CODE-F011", "CODE-F2=CODE-F011"),
    )
    assert collapsing.returncode == 2
    assert "must be injective" in collapsing.stderr

    wrong_namespace = derive(
        run_dir,
        attempt=1,
        span_id=span_id,
        refusal_class="finding-id-format",
        artifact=artifact,
        id_map=("CODE-F1=PLAN-F011", "CODE-F2=CODE-F012"),
    )
    assert wrong_namespace.returncode == 2
    assert "must use the CODE-FNNN namespace" in wrong_namespace.stderr

    accepted = derive(
        run_dir,
        attempt=1,
        span_id=span_id,
        refusal_class="finding-id-format",
        artifact=artifact,
        id_map=("CODE-F1=CODE-F011", "CODE-F2=CODE-F012"),
    )
    assert accepted.returncode == 0, accepted.stderr
    assert "actionable_findings=2" in accepted.stdout
    assert len(derived_records(run_dir)) == 1


def test_an_id_map_is_refused_for_a_class_that_renames_nothing(
    repository: Path, tmp_path: Path
) -> None:
    run_dir = tmp_path / "run"
    _, span_id, artifact = stale_resolution(repository, tmp_path, run_dir)

    derived = derive(
        run_dir,
        attempt=1,
        span_id=span_id,
        refusal_class="resolved-in-not-current-candidate",
        artifact=artifact,
        id_map=("CODE-F002=CODE-F009",),
    )

    assert derived.returncode == 2
    assert "applies only to refusal class finding-id-format" in derived.stderr


def corroborated_id_format_run(
    repository: Path, tmp_path: Path, run_dir: Path
) -> tuple[str, str, Path, Path]:
    """A refused id-format batch plus the corrected batch that really ingested."""
    candidate, span_id, artifact = malformed_id_run(repository, tmp_path, run_dir)
    second = native_accepted_attempt(repository, run_dir, "role.code-review", "critic", 2)
    corrected = review_artifact(
        tmp_path / "critic-2.md",
        [finding("CODE-F011", candidate), finding("CODE-F012", candidate)],
    )
    assert ingest_artifact(run_dir, candidate, corrected, second).returncode == 0
    return candidate, span_id, artifact, corrected


def test_a_corroborated_derivation_verifies_batch_identity(
    repository: Path, tmp_path: Path
) -> None:
    run_dir = tmp_path / "run"
    _, span_id, artifact, corrected = corroborated_id_format_run(repository, tmp_path, run_dir)

    derived = derive(
        run_dir,
        attempt=1,
        span_id=span_id,
        refusal_class="finding-id-format",
        artifact=artifact,
        corroborating=corrected,
        id_map=("CODE-F1=CODE-F011", "CODE-F2=CODE-F012"),
    )

    assert derived.returncode == 0, derived.stderr
    assert derived_records(run_dir)[0]["corroborating_artifact_sha256"] is not None


def test_a_bijection_is_refused_when_a_non_id_field_differs(
    repository: Path, tmp_path: Path
) -> None:
    """The only permitted delta is the one the declared class names."""
    run_dir = tmp_path / "run"
    candidate, span_id, artifact = malformed_id_run(repository, tmp_path, run_dir)
    second = native_accepted_attempt(repository, run_dir, "role.code-review", "critic", 2)
    divergent = finding("CODE-F011", candidate)
    divergent["severity"] = "low"
    corrected = review_artifact(
        tmp_path / "critic-2.md", [divergent, finding("CODE-F012", candidate)]
    )
    assert ingest_artifact(run_dir, candidate, corrected, second).returncode == 0

    derived = derive(
        run_dir,
        attempt=1,
        span_id=span_id,
        refusal_class="finding-id-format",
        artifact=artifact,
        corroborating=corrected,
        id_map=("CODE-F1=CODE-F011", "CODE-F2=CODE-F012"),
    )

    assert derived.returncode == 2, (
        "a corroborating artifact with a different severity was accepted"
    )
    assert "field severity, which the declared refusal class does not permit" in (derived.stderr)
    assert derived_records(run_dir) == []


def test_a_corroborating_source_cannot_support_two_derivations(
    repository: Path, tmp_path: Path
) -> None:
    """One measured pass corroborates one derived pass, never a fan-out."""
    run_dir = tmp_path / "run"
    candidate, span_id, artifact, corrected = corroborated_id_format_run(
        repository, tmp_path, run_dir
    )
    assert (
        derive(
            run_dir,
            attempt=1,
            span_id=span_id,
            refusal_class="finding-id-format",
            artifact=artifact,
            corroborating=corrected,
            id_map=("CODE-F1=CODE-F011", "CODE-F2=CODE-F012"),
        ).returncode
        == 0
    )
    third = native_accepted_attempt(repository, run_dir, "role.code-review", "critic", 3)
    other = review_artifact(
        tmp_path / "critic-3.md",
        [finding("CODE-F3", candidate), finding("CODE-F4", candidate)],
    )
    assert ingest_artifact(run_dir, candidate, other, third).returncode == 2

    derived = derive(
        run_dir,
        attempt=3,
        span_id=third,
        refusal_class="finding-id-format",
        artifact=other,
        corroborating=corrected,
        id_map=("CODE-F3=CODE-F011", "CODE-F4=CODE-F012"),
    )

    assert derived.returncode == 2, "one corroborating artifact supported a second derivation"
    assert "already supports another derivation" in derived.stderr


def test_a_corroborating_source_without_native_metrics_refuses(
    repository: Path, tmp_path: Path
) -> None:
    """No chaining: a source that was never measured corroborates nothing."""
    run_dir = tmp_path / "run"
    candidate, span_id, artifact = malformed_id_run(repository, tmp_path, run_dir)
    unmeasured = review_artifact(
        tmp_path / "critic-2.md",
        [finding("CODE-F011", candidate), finding("CODE-F012", candidate)],
    )
    # Ingested as an orchestrator-authored transition, so no span ever measured it.
    assert (
        run(
            "ingest-findings",
            "--run-dir",
            str(run_dir),
            "--kind",
            "code",
            "--candidate",
            candidate,
            "--no-review-span",
            "orchestrator-authored",
            "--artifact",
            str(unmeasured),
        ).returncode
        == 0
    )

    derived = derive(
        run_dir,
        attempt=1,
        span_id=span_id,
        refusal_class="finding-id-format",
        artifact=artifact,
        corroborating=unmeasured,
        id_map=("CODE-F1=CODE-F011", "CODE-F2=CODE-F012"),
    )

    assert derived.returncode == 2, "an artifact that was never measured corroborated a derivation"
    assert "attached to its own review span" in derived.stderr


def test_a_tampered_derived_record_fails_recomputation(repository: Path, tmp_path: Path) -> None:
    """The recomputation is what makes this a measurement, not an assertion.

    Without it the ledger would be another write-only record with no reader
    anywhere that could contradict it.
    """
    run_dir = tmp_path / "run"
    _, span_id, artifact = stale_resolution(repository, tmp_path, run_dir)
    assert (
        derive(
            run_dir,
            attempt=1,
            span_id=span_id,
            refusal_class="resolved-in-not-current-candidate",
            artifact=artifact,
        ).returncode
        == 0
    )
    assert run("validate", "--run-dir", str(run_dir)).returncode == 0

    record = derived_records(run_dir)[0]
    record["actionable_findings"] = 0
    (run_dir / "derived-metrics.jsonl").write_text(
        json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n"
    )

    validated = run("validate", "--run-dir", str(run_dir))
    assert validated.returncode == 2, "validate accepted derived integers that do not recompute"
    assert "do not recompute" in validated.stderr


def test_a_derived_record_cannot_outlive_its_artifact(repository: Path, tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    _, span_id, artifact = stale_resolution(repository, tmp_path, run_dir)
    assert (
        derive(
            run_dir,
            attempt=1,
            span_id=span_id,
            refusal_class="resolved-in-not-current-candidate",
            artifact=artifact,
        ).returncode
        == 0
    )
    stored = next((run_dir / "derived-artifacts").iterdir())
    stored.write_text("{}\n")

    validated = run("validate", "--run-dir", str(run_dir))
    assert validated.returncode == 2
    assert "absent or altered" in validated.stderr


def test_a_derived_record_for_an_attempt_that_needs_none_refuses(
    repository: Path, tmp_path: Path
) -> None:
    """Mirrors the telemetry declaration naming an unregistered attempt."""
    run_dir = tmp_path / "run"
    _, span_id, artifact = stale_resolution(repository, tmp_path, run_dir)
    assert (
        derive(
            run_dir,
            attempt=1,
            span_id=span_id,
            refusal_class="resolved-in-not-current-candidate",
            artifact=artifact,
        ).returncode
        == 0
    )
    record = derived_records(run_dir)[0]
    record["attempt"] = 9
    (run_dir / "derived-metrics.jsonl").write_text(
        json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n"
    )

    validated = run("validate", "--run-dir", str(run_dir))
    assert validated.returncode == 2
    assert "not unmeasured review passes" in validated.stderr


def test_a_derived_pass_closes_the_run_and_is_visible_in_both_summaries(
    repository: Path, tmp_path: Path
) -> None:
    """The whole point: the overlay works identically after finalization."""
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    assert (
        ingest(run_dir, tmp_path, [finding("CODE-F001", candidate)], candidate=candidate).returncode
        == 0
    )
    span_id = native_accepted_attempt(repository, run_dir, "role.code-review", "critic", 1)
    artifact = review_artifact(
        tmp_path / "critic.md",
        [
            finding("CODE-F002", candidate, resolved_in="0" * 64),
            finding("CODE-F003", candidate),
        ],
    )
    assert ingest_artifact(run_dir, candidate, artifact, span_id).returncode == 2
    assert (
        derive(
            run_dir,
            attempt=1,
            span_id=span_id,
            refusal_class="resolved-in-not-current-candidate",
            artifact=artifact,
            cause="ingest refusal was chained behind a backgrounded dispatch",
        ).returncode
        == 0
    )
    finalize_for_summary(repository, run_dir)

    summary = run("timing-summary", "--run-dir", str(run_dir), "--format", "json")
    assert summary.returncode == 0, summary.stderr
    projected = json.loads(summary.stdout)["derived_review_metrics"]
    assert len(projected) == 1
    assert projected[0]["operation"] == "role.code-review"
    assert projected[0]["attempt"] == 1
    assert projected[0]["span_id"] == span_id
    assert projected[0]["refusal_class"] == "resolved-in-not-current-candidate"
    assert projected[0]["findings_reported"] == 2
    assert projected[0]["actionable_findings"] == 3
    assert projected[0]["corroborated"] is False

    markdown = run("timing-summary", "--run-dir", str(run_dir), "--format", "markdown")
    assert markdown.returncode == 0, markdown.stderr
    assert "Derived review convergence metrics" in markdown.stdout
    assert span_id in markdown.stdout
    assert "`resolved-in-not-current-candidate`" in markdown.stdout
    assert "actionable_findings 3" in markdown.stdout
    assert "ingest refusal was chained behind a backgrounded dispatch" in markdown.stdout
    # The reader must see that these were recomputed, not measured.
    assert "recomputed from the refused artifact" in markdown.stdout


def test_an_unmeasured_pass_with_no_derivation_still_refuses_at_summary(
    repository: Path, tmp_path: Path
) -> None:
    """The overlay is opt-in and evidence-bound. Silence is still not a pass."""
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    native_accepted_attempt(repository, run_dir, "role.code-review", "critic", 1)
    finalize_for_summary(repository, run_dir)

    refused = run("timing-summary", "--run-dir", str(run_dir), "--format", "json")

    assert refused.returncode == 2
    assert "lacks convergence metrics" in refused.stderr
    assert "attach-derived-metrics" in refused.stderr


def test_a_derivation_refuses_a_batch_that_trips_a_rule_outside_its_class(
    repository: Path, tmp_path: Path
) -> None:
    """Suppressing one rule is not suppressing the rest.

    A `finding-id-format` batch never reaches the relationship loop at all — its
    findings fail `validate_finding` before they get there — so the namespace,
    lineage, `resolved_in`, and transition rules have never run on them. The
    replay is where they run, and it is the load-bearing claim of the whole
    id-format path: without it a mapped id could land on a terminal ledger entry
    and be counted as if the ingest had accepted it.
    """
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    # A terminal entry: `superseded` accepts no transition but itself.
    assert (
        ingest(
            run_dir,
            tmp_path,
            [finding("CODE-F011", candidate, state="superseded", resolved_in=candidate)],
            candidate=candidate,
        ).returncode
        == 0
    )
    span_id = native_accepted_attempt(repository, run_dir, "role.code-review", "critic", 1)
    artifact = review_artifact(tmp_path / "critic.md", [finding("CODE-F1", candidate)])
    assert ingest_artifact(run_dir, candidate, artifact, span_id).returncode == 2
    assert sorted(journal_of(run_dir)[-1]["refusal_codes"]) == ["id-format"]
    assert journal_of(run_dir)[-1]["ledger_before"] == {"CODE-F011": "superseded"}

    derived = derive(
        run_dir,
        attempt=1,
        span_id=span_id,
        refusal_class="finding-id-format",
        artifact=artifact,
        id_map=("CODE-F1=CODE-F011",),
    )

    assert derived.returncode == 2, (
        "a batch tripping a rule outside the declared class was derived anyway"
    )
    assert "fails rules the declared class does not cover" in derived.stderr
    assert "invalid transition: superseded -> open" in derived.stderr
    assert derived_records(run_dir) == []


def test_a_derivation_refuses_an_attempt_that_was_never_dispatched(
    repository: Path, tmp_path: Path
) -> None:
    """The verb binds its own attempt, rather than leaving it to the reader.

    `derived-metrics.jsonl` is append-only, so a record accepted with a wrong
    `--attempt` would pass at write time and then refuse every later `validate`
    and `timing-summary` permanently, with no verb to withdraw it. The refusal
    has to land before the record exists.
    """
    run_dir = tmp_path / "run"
    _, span_id, artifact = stale_resolution(repository, tmp_path, run_dir)

    derived = derive(
        run_dir,
        attempt=7,
        span_id=span_id,
        refusal_class="resolved-in-not-current-candidate",
        artifact=artifact,
    )

    assert derived.returncode == 2, (
        "a derivation was recorded for an attempt this run never dispatched"
    )
    assert "no accepted review dispatch is recorded" in derived.stderr
    assert derived_records(run_dir) == []
    # And the run is still closable, which is the point of refusing early.
    assert run("validate", "--run-dir", str(run_dir)).returncode == 2
    assert (
        "review passes lack convergence metrics"
        in run("validate", "--run-dir", str(run_dir)).stderr
    )


def test_a_derivation_refuses_a_span_the_dispatch_does_not_name(
    repository: Path, tmp_path: Path
) -> None:
    run_dir = tmp_path / "run"
    _, span_id, artifact = stale_resolution(repository, tmp_path, run_dir)
    other = native_accepted_attempt(repository, run_dir, "role.code-review", "critic", 2)

    derived = derive(
        run_dir,
        attempt=1,
        span_id=other,
        refusal_class="resolved-in-not-current-candidate",
        artifact=artifact,
    )

    assert derived.returncode == 2, (
        "a derivation named an attempt and a span that belong to different passes"
    )
    assert "not the declared" in derived.stderr
    assert span_id != other


def test_an_honest_re_ingest_after_a_derivation_supersedes_it(
    repository: Path, tmp_path: Path
) -> None:
    """The more honest path must not be the one that deadlocks.

    Deriving before finalization and then re-ingesting the pass properly used to
    strand the derived record as an orphan and refuse the run forever. The real
    measurement wins; the record is retained, reported as superseded, and the
    run still closes.
    """
    run_dir = tmp_path / "run"
    candidate, span_id, artifact = stale_resolution(repository, tmp_path, run_dir)
    assert (
        derive(
            run_dir,
            attempt=1,
            span_id=span_id,
            refusal_class="resolved-in-not-current-candidate",
            artifact=artifact,
        ).returncode
        == 0
    )
    assert run("validate", "--run-dir", str(run_dir)).returncode == 0

    corrected = review_artifact(
        tmp_path / "critic-2.md",
        [finding("CODE-F002", candidate), finding("CODE-F003", candidate)],
    )
    assert ingest_artifact(run_dir, candidate, corrected, span_id).returncode == 0

    validated = run("validate", "--run-dir", str(run_dir))
    assert validated.returncode == 0, "an honest re-ingest after a derivation deadlocked the run"

    finalize_for_summary(repository, run_dir)
    summary = run("timing-summary", "--run-dir", str(run_dir), "--format", "json")
    assert summary.returncode == 0, summary.stderr
    projected = json.loads(summary.stdout)["derived_review_metrics"]
    assert len(projected) == 1
    assert projected[0]["superseded"] is True
    # The span's own measurement is what is reported, not the derivation's.
    metadata = json.loads((run_dir / "run.json").read_text())
    span = closed_span(
        engine_root=repository,
        trace_id=metadata["telemetry_trace_id"],
        span_id=span_id,
    )
    assert projected[0]["findings_reported"] == span["findings_reported"]
    assert projected[0]["actionable_findings"] == span["actionable_findings"]

    markdown = run("timing-summary", "--run-dir", str(run_dir), "--format", "markdown")
    assert markdown.returncode == 0, markdown.stderr
    assert "superseded by a later ingest" in markdown.stdout
    assert "retained only for the trail" in markdown.stdout


def test_a_superseded_derivation_still_needs_the_evidence_it_publishes(
    repository: Path, tmp_path: Path
) -> None:
    """Relaxing recomputation does not relax what the entry stands on.

    A superseded record reports the span's integers, so its own two are read by
    nothing — but `timing-summary` goes on publishing its refusal class and its
    cause, and after supersession nothing else in the run references
    `derived-artifacts/`. That makes those artifacts the first thing a cleanup
    removes, and without this floor the removal would be silent while the entry
    kept being printed.
    """
    run_dir = tmp_path / "run"
    candidate, span_id, artifact = stale_resolution(repository, tmp_path, run_dir)
    assert (
        derive(
            run_dir,
            attempt=1,
            span_id=span_id,
            refusal_class="resolved-in-not-current-candidate",
            artifact=artifact,
        ).returncode
        == 0
    )
    corrected = review_artifact(
        tmp_path / "critic-2.md",
        [finding("CODE-F002", candidate), finding("CODE-F003", candidate)],
    )
    assert ingest_artifact(run_dir, candidate, corrected, span_id).returncode == 0
    # Superseded and closable, before the artifact goes missing.
    assert run("validate", "--run-dir", str(run_dir)).returncode == 0

    stored = next((run_dir / "derived-artifacts").iterdir())
    stored.write_text("{}\n")

    validated = run("validate", "--run-dir", str(run_dir))
    assert validated.returncode == 2, (
        "a superseded entry kept publishing a refusal class its artifact no longer backs"
    )
    assert "absent or altered" in validated.stderr

    finalize_for_summary(repository, run_dir)
    summary = run("timing-summary", "--run-dir", str(run_dir), "--format", "json")
    assert summary.returncode == 2
    assert "absent or altered" in summary.stderr


def test_a_superseded_derivation_still_needs_its_pinned_journal_row(
    repository: Path, tmp_path: Path
) -> None:
    """The other half of the same floor: the refusal it names must still exist."""
    run_dir = tmp_path / "run"
    candidate, span_id, artifact = stale_resolution(repository, tmp_path, run_dir)
    assert (
        derive(
            run_dir,
            attempt=1,
            span_id=span_id,
            refusal_class="resolved-in-not-current-candidate",
            artifact=artifact,
        ).returncode
        == 0
    )
    corrected = review_artifact(
        tmp_path / "critic-2.md",
        [finding("CODE-F002", candidate), finding("CODE-F003", candidate)],
    )
    assert ingest_artifact(run_dir, candidate, corrected, span_id).returncode == 0
    assert run("validate", "--run-dir", str(run_dir)).returncode == 0

    kept = [
        line
        for line in (run_dir / "ingest-log.jsonl").read_text().splitlines()
        if line.strip() and json.loads(line)["outcome"] != "refused"
    ]
    (run_dir / "ingest-log.jsonl").write_text("\n".join(kept) + "\n")

    validated = run("validate", "--run-dir", str(run_dir))
    assert validated.returncode == 2, (
        "a superseded entry kept publishing a refusal the journal no longer records"
    )
    assert "no unique refused ingest" in validated.stderr


# --- Candidate drift under an in-flight dispatch ------------------------------
#
# `kickoff-tree-id` hashes nonignored untracked files, so any write by any
# session moves the candidate. The three acceptance checks below are exercised
# for independence on purpose: each of the first three tests constructs a drift
# that passes the other two checks and fails only its own, because a layered
# rule whose layers are never isolated is one check plus two decorations.


DRIFT_MARKERS = ("drift-partition:", "drift-reviewed-surface:", "drift-authority:")


def install_drift_policy(repository: Path) -> None:
    """Give the fixture the real policy file that owns the partition vocabulary.

    The block in `policies/orchestration-evidence.md` is the single source of
    truth, so the tests read the shipped vocabulary rather than a paraphrase of
    it that could agree with a wrong implementation.
    """
    destination = repository / "policies" / "orchestration-evidence.md"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes((ROOT / "policies" / "orchestration-evidence.md").read_bytes())


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


def drift_records(run_dir: Path) -> list[dict[str, object]]:
    path = run_dir / "candidate-drift.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


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


def accept_drift(
    run_dir: Path,
    *,
    operation: str = "role.code-review",
    attempt: int = 1,
    cause: str = "a concurrent supervision session appended a lesson mid-dispatch",
) -> subprocess.CompletedProcess[str]:
    return run(
        "accept-candidate-drift",
        "--run-dir",
        str(run_dir),
        "--operation",
        operation,
        "--attempt",
        str(attempt),
        "--cause",
        cause,
    )


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


def sole_marker(text: str) -> set[str]:
    return {marker for marker in DRIFT_MARKERS if marker in text}


def test_the_partition_check_alone_refuses_a_path_it_cannot_place(
    repository: Path, tmp_path: Path
) -> None:
    """Check 1 in isolation: `bin/` is nothing the bookkeeping touches.

    Nothing is captured, so no reviewed surface exists, and the drifted path is
    not a declared authority — checks 2 and 3 have nothing to say about it. Only
    the partition can refuse this drift, and an unplaceable path must fail
    closed rather than default to disjoint.
    """
    install_drift_policy(repository)
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)

    def mutate(root: Path) -> None:
        write_repo_file(root, "bin/tool.py", "VALUE = 2\n")

    drifting_attempt(repository, run_dir, mutate)

    refused = accept_drift(run_dir)

    assert refused.returncode == 2, "an unplaceable drifted path was accepted"
    assert sole_marker(refused.stderr) == {"drift-partition:"}, refused.stderr
    assert "bin/tool.py" in refused.stderr
    assert drift_records(run_dir) == []


def test_the_reviewed_surface_check_alone_refuses_a_path_a_finding_names(
    repository: Path, tmp_path: Path
) -> None:
    """Check 2 in isolation, via `affected_paths`.

    `lessons/` is squarely inside the inert partition and is not a declared
    authority, so checks 1 and 3 pass. A ledger finding names the very path that
    drifted, which makes the drift part of what the review was about.
    """
    install_drift_policy(repository)
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    named = dict(finding("CODE-F001", candidate))
    named["affected_paths"] = ["lessons/silent-guard-drift.md"]
    assert ingest(run_dir, tmp_path, [named], candidate=candidate).returncode == 0

    drifting_attempt(repository, run_dir, add_lesson)

    refused = accept_drift(run_dir)

    assert refused.returncode == 2, (
        "a drift the review's own findings point at was accepted as disjoint"
    )
    assert sole_marker(refused.stderr) == {"drift-reviewed-surface:"}, refused.stderr
    assert "CODE-F001" in refused.stderr
    assert drift_records(run_dir) == []


def test_the_reviewed_surface_check_alone_refuses_a_captured_change_path(
    repository: Path, tmp_path: Path
) -> None:
    """The other half of check 2: `change.json`'s own `changed_files`."""
    install_drift_policy(repository)
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    add_lesson(repository)
    capture(repository, run_dir)
    assert "lessons/silent-guard-drift.md" in {
        item["path"] for item in json.loads((run_dir / "change.json").read_text())["changed_files"]
    }

    def mutate(root: Path) -> None:
        write_repo_file(root, "lessons/silent-guard-drift.md", "# Lesson, revised\n")

    drifting_attempt(repository, run_dir, mutate)

    refused = accept_drift(run_dir)

    assert refused.returncode == 2, (
        "a drift inside the captured change surface was accepted as disjoint"
    )
    assert sole_marker(refused.stderr) == {"drift-reviewed-surface:"}, refused.stderr
    assert drift_records(run_dir) == []


def test_the_authority_check_alone_refuses_a_drifted_authority_in_the_inert_set(
    repository: Path, tmp_path: Path
) -> None:
    """Check 3 in isolation — the sharp edge, and why `plan/` cannot be one class.

    `plan/INDEX.md` is inert bookkeeping and sits in the partition, so check 1
    passes; nothing is captured and no finding names it, so check 2 passes. But
    it is a *declared authority* of this very review, which is exactly the case
    a path partition inverts on. Only the authority check can refuse it.
    """
    install_drift_policy(repository)
    write_repo_file(repository, "plan/INDEX.md", "| 1 | ready |\n")
    run_dir = tmp_path / "run"
    initialize(
        repository,
        run_dir,
        authorities=("phase.md::Acceptance", "plan/INDEX.md"),
    )

    def mutate(root: Path) -> None:
        write_repo_file(root, "plan/INDEX.md", "| 1 | done |\n")

    drifting_attempt(repository, run_dir, mutate)

    refused = accept_drift(run_dir)

    assert refused.returncode == 2, (
        "a declared authority drifted under the review and was waved through "
        "because its path prefix is inert bookkeeping"
    )
    assert sole_marker(refused.stderr) == {"drift-authority:"}, refused.stderr
    assert "plan/INDEX.md" in refused.stderr
    assert drift_records(run_dir) == []


def test_a_proven_disjoint_drift_is_accepted_and_recorded(repository: Path, tmp_path: Path) -> None:
    """All three checks pass: a concurrent session's lesson file mid-dispatch."""
    install_drift_policy(repository)
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)

    dispatch, returned, span_id = drifting_attempt(repository, run_dir, add_lesson)

    accepted = accept_drift(run_dir)

    assert accepted.returncode == 0, accepted.stderr
    record = drift_records(run_dir)[0]
    assert record["operation"] == "role.code-review"
    assert record["attempt"] == 1
    assert record["dispatch_candidate_id"] == dispatch
    assert record["return_candidate_id"] == returned
    assert dispatch != returned
    assert record["drifted_paths"] == ["lessons/silent-guard-drift.md"]
    assert record["cause"].startswith("a concurrent supervision session")
    assert (
        ingest_artifact(run_dir, returned, stale_batch(tmp_path, dispatch), span_id).returncode == 0
    )
    assert run("validate", "--run-dir", str(run_dir)).returncode == 0


def test_an_accepted_drift_lets_the_stale_resolution_ingest(
    repository: Path, tmp_path: Path
) -> None:
    """The refusal this mechanism exists for, and the only one it relaxes.

    The critic honestly stamped the candidate it was dispatched against; the
    tree then moved under it. Rewriting `resolved_in` to the ingesting candidate
    would record that a reviewer verified a tree it never saw, so the batch is
    admitted only once the drift between the two is proven disjoint.
    """
    install_drift_policy(repository)
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    dispatch, returned, span_id = drifting_attempt(repository, run_dir, add_lesson)
    artifact = review_artifact(
        tmp_path / "critic.md",
        [
            finding(
                "CODE-F002",
                dispatch,
                state="rejected-with-evidence",
                resolved_in=dispatch,
            )
        ],
    )

    before = ingest_artifact(run_dir, returned, artifact, span_id)
    assert before.returncode == 2, "a stale resolution was admitted with no record"
    assert "resolved_in does not match" in before.stderr

    assert accept_drift(run_dir).returncode == 0
    after = ingest_artifact(run_dir, returned, artifact, span_id)

    assert after.returncode == 0, after.stderr
    ledger = json.loads((run_dir / "findings.json").read_text())["findings"]
    assert [item["resolved_in"] for item in ledger] == [dispatch]
    assert run("validate", "--run-dir", str(run_dir)).returncode == 0


def test_drift_acceptance_is_bound_to_the_reviews_own_dispatch(
    repository: Path, tmp_path: Path
) -> None:
    """A record for one pass does not launder another pass's stale resolution."""
    install_drift_policy(repository)
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    dispatch, returned, _ = drifting_attempt(repository, run_dir, add_lesson)
    assert accept_drift(run_dir).returncode == 0
    other = native_accepted_attempt(repository, run_dir, "role.code-review", "critic", 2)
    artifact = review_artifact(
        tmp_path / "critic-2.md",
        [
            finding(
                "CODE-F003",
                dispatch,
                state="rejected-with-evidence",
                resolved_in=dispatch,
            )
        ],
    )

    refused = ingest_artifact(run_dir, returned, artifact, other)

    assert refused.returncode == 2, (
        "one pass's drift record admitted another pass's stale resolution"
    )
    assert "resolved_in does not match" in refused.stderr


def test_an_ingest_beyond_the_recorded_return_candidate_still_refuses(
    repository: Path, tmp_path: Path
) -> None:
    """The record spans exactly one dispatch, and later movement is unclassified."""
    install_drift_policy(repository)
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    dispatch, _, span_id = drifting_attempt(repository, run_dir, add_lesson)
    assert accept_drift(run_dir).returncode == 0
    write_repo_file(repository, "lessons/second.md", "# Another\n")
    moved = run("current-candidate", "--run-dir", str(run_dir), "--reason", "ingest")
    assert moved.returncode == 0
    artifact = review_artifact(
        tmp_path / "critic.md",
        [
            finding(
                "CODE-F002",
                dispatch,
                state="rejected-with-evidence",
                resolved_in=dispatch,
            )
        ],
    )

    refused = ingest_artifact(run_dir, moved.stdout.strip(), artifact, span_id)

    assert refused.returncode == 2, (
        "a drift record was stretched across movement it never classified"
    )
    assert "resolved_in does not match" in refused.stderr


def test_a_drift_record_requires_both_stored_manifests(repository: Path, tmp_path: Path) -> None:
    """Without the manifests the drift is unclassifiable, never assumed disjoint.

    Only `candidate.json` and `reviewed-candidate.json` were ever persisted
    before the store existed, both overwritten in place, so at the moment a
    batch was refused the manifest the role saw was already gone.
    """
    install_drift_policy(repository)
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    dispatch, _, _ = drifting_attempt(repository, run_dir, add_lesson)
    (run_dir / "candidates" / f"{dispatch}.json").unlink()

    refused = accept_drift(run_dir)

    assert refused.returncode == 2, "an unclassifiable drift defaulted to disjoint"
    assert "no stored candidate manifest" in refused.stderr
    assert drift_records(run_dir) == []


def test_the_candidate_store_is_content_addressed_and_write_once(
    repository: Path, tmp_path: Path
) -> None:
    install_drift_policy(repository)
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)
    stored = run_dir / "candidates" / f"{candidate}.json"
    assert json.loads(stored.read_text())["candidate_id"] == candidate
    before = stored.read_bytes()

    # The same candidate observed again deduplicates rather than rewriting.
    assert (
        run("current-candidate", "--run-dir", str(run_dir), "--reason", "dispatch").returncode == 0
    )
    assert stored.read_bytes() == before

    add_lesson(repository)
    moved = run("current-candidate", "--run-dir", str(run_dir), "--reason", "dispatch")
    assert moved.returncode == 0
    assert (run_dir / "candidates" / f"{moved.stdout.strip()}.json").is_file()
    assert sorted(lineage_of(run_dir)) == sorted(
        path.stem for path in (run_dir / "candidates").iterdir()
    )


def test_a_tampered_drift_record_fails_recomputation(repository: Path, tmp_path: Path) -> None:
    """The recomputation is what makes the classification a measurement."""
    install_drift_policy(repository)
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    dispatch, returned, span_id = drifting_attempt(repository, run_dir, add_lesson)
    assert accept_drift(run_dir).returncode == 0
    assert (
        ingest_artifact(run_dir, returned, stale_batch(tmp_path, dispatch), span_id).returncode == 0
    )
    assert run("validate", "--run-dir", str(run_dir)).returncode == 0

    record = drift_records(run_dir)[0]
    record["drifted_paths"] = []
    (run_dir / "candidate-drift.jsonl").write_text(
        json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n"
    )

    validated = run("validate", "--run-dir", str(run_dir))

    assert validated.returncode == 2, (
        "validate trusted a recorded drift path set instead of re-deriving it"
    )
    assert "do not recompute" in validated.stderr


def test_validate_re_runs_the_classification_it_published(repository: Path, tmp_path: Path) -> None:
    """A record accepted under one ledger is re-checked against the ledger now.

    A finding ingested after the acceptance can bring the drifted path into the
    reviewed surface, and the entry must stop being published on the strength of
    a classification that no longer holds.
    """
    install_drift_policy(repository)
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    dispatch, returned, span_id = drifting_attempt(repository, run_dir, add_lesson)
    assert accept_drift(run_dir).returncode == 0
    assert (
        ingest_artifact(run_dir, returned, stale_batch(tmp_path, dispatch), span_id).returncode == 0
    )
    assert run("validate", "--run-dir", str(run_dir)).returncode == 0

    named = dict(finding("CODE-F009", returned))
    named["affected_paths"] = ["lessons/silent-guard-drift.md"]
    assert ingest(run_dir, tmp_path, [named], candidate=returned).returncode == 0

    validated = run("validate", "--run-dir", str(run_dir))

    assert validated.returncode == 2, (
        "an accepted drift kept being published after the reviewed surface grew to cover it"
    )
    assert "drift-reviewed-surface:" in validated.stderr


def test_a_drift_record_binds_an_accepted_dispatch(repository: Path, tmp_path: Path) -> None:
    """Append-only means the reader's refusal has no undo, so the verb checks."""
    install_drift_policy(repository)
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    drifting_attempt(repository, run_dir, add_lesson)

    never = accept_drift(run_dir, attempt=4)

    assert never.returncode == 2, "a drift record was written for a dispatch this run never made"
    assert "no accepted role dispatch is recorded" in never.stderr
    assert drift_records(run_dir) == []


def test_a_rejected_dispatch_cannot_carry_a_drift_record(repository: Path, tmp_path: Path) -> None:
    install_drift_policy(repository)
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    drifting_attempt(repository, run_dir, add_lesson, accepted=False)

    refused = accept_drift(run_dir)

    assert refused.returncode == 2
    assert "no accepted role dispatch is recorded" in refused.stderr
    assert drift_records(run_dir) == []


def test_a_dispatch_with_no_recorded_open_candidate_has_no_recovery(
    repository: Path, tmp_path: Path
) -> None:
    """The freeze convention's executable half: unrecorded is unreconstructible.

    Nothing forces `--dispatch-candidate`, because the delegated watcher records
    the topology and cannot know it. What is enforced is that its absence costs
    the recovery outright rather than being silently filled in later.
    """
    install_drift_policy(repository)
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    drifting_attempt(repository, run_dir, add_lesson, record_open_candidate=False)
    assert dispatch_rows(run_dir)[0]["dispatch_candidate_id"] is None

    refused = accept_drift(run_dir)

    assert refused.returncode == 2, (
        "a drift was classified for a dispatch that recorded no open candidate"
    )
    assert "records no dispatch-open candidate" in refused.stderr
    assert drift_records(run_dir) == []


def test_a_dispatch_that_did_not_move_the_tree_has_no_drift(
    repository: Path, tmp_path: Path
) -> None:
    install_drift_policy(repository)
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    dispatch, returned, _ = drifting_attempt(repository, run_dir, lambda root: None)
    assert dispatch == returned

    refused = accept_drift(run_dir)

    assert refused.returncode == 2
    assert "did not move" in refused.stderr
    assert drift_records(run_dir) == []


def test_a_duplicate_drift_record_refuses(repository: Path, tmp_path: Path) -> None:
    install_drift_policy(repository)
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    drifting_attempt(repository, run_dir, add_lesson)
    assert accept_drift(run_dir).returncode == 0

    again = accept_drift(run_dir)

    assert again.returncode == 2
    assert "duplicate candidate-drift record" in again.stderr
    assert len(drift_records(run_dir)) == 1


def test_a_drift_record_requires_a_cause(repository: Path, tmp_path: Path) -> None:
    install_drift_policy(repository)
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    drifting_attempt(repository, run_dir, add_lesson)

    refused = accept_drift(run_dir, cause="   ")

    assert refused.returncode == 2
    assert "requires its cause" in refused.stderr
    assert drift_records(run_dir) == []


def test_accepted_drift_is_published_in_both_summary_formats(
    repository: Path, tmp_path: Path
) -> None:
    """A run that accepted a review of a tree the ingest did not hold says so."""
    install_drift_policy(repository)
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    dispatch, returned, span_id = drifting_attempt(repository, run_dir, add_lesson)
    artifact = review_artifact(
        tmp_path / "critic.md",
        [
            finding(
                "CODE-F002",
                dispatch,
                state="rejected-with-evidence",
                resolved_in=dispatch,
            )
        ],
    )
    assert (
        accept_drift(
            run_dir, cause="a supervision session appended a lesson mid-dispatch"
        ).returncode
        == 0
    )
    assert ingest_artifact(run_dir, returned, artifact, span_id).returncode == 0
    finalize_for_summary(repository, run_dir)

    summary = run("timing-summary", "--run-dir", str(run_dir), "--format", "json")
    assert summary.returncode == 0, summary.stderr
    projected = json.loads(summary.stdout)["candidate_drift"]
    assert len(projected) == 1
    assert projected[0]["operation"] == "role.code-review"
    assert projected[0]["attempt"] == 1
    assert projected[0]["dispatch_candidate_id"] == dispatch
    assert projected[0]["return_candidate_id"] == returned
    assert projected[0]["drifted_paths"] == ["lessons/silent-guard-drift.md"]

    markdown = run("timing-summary", "--run-dir", str(run_dir), "--format", "markdown")
    assert markdown.returncode == 0, markdown.stderr
    assert "Accepted candidate drift" in markdown.stdout
    assert "lessons/silent-guard-drift.md" in markdown.stdout
    assert "a supervision session appended a lesson mid-dispatch" in markdown.stdout
    assert dispatch[:12] in markdown.stdout


def test_accepted_drift_does_not_relax_the_final_seal(repository: Path, tmp_path: Path) -> None:
    """The seal is lane- and drift-independent.

    A gate whose candidates differ measured a tree other than the one being
    accepted, and an accepted drift record buys exactly nothing here.
    """
    install_drift_policy(repository)
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    dispatch, returned, span_id = drifting_attempt(repository, run_dir, add_lesson)
    artifact = review_artifact(
        tmp_path / "critic.md",
        [
            finding(
                "CODE-F002",
                dispatch,
                state="rejected-with-evidence",
                resolved_in=dispatch,
            )
        ],
    )
    assert accept_drift(run_dir).returncode == 0
    assert ingest_artifact(run_dir, returned, artifact, span_id).returncode == 0
    complete_orchestration(repository, run_dir)
    assert run_final_gate(run_dir, returned).returncode == 0
    assert (
        run(
            "validate",
            "--run-dir",
            str(run_dir),
            "--require-final",
            "--required-final-command",
            "./bin/check all",
        ).returncode
        == 0
    )

    # One more inert-set write, and the seal refuses even though the very same
    # partition was proven disjoint minutes ago.
    write_repo_file(repository, "lessons/later.md", "# Later\n")

    sealed = run(
        "validate",
        "--run-dir",
        str(run_dir),
        "--require-final",
        "--required-final-command",
        "./bin/check all",
    )

    assert sealed.returncode == 2, (
        "an accepted drift classification was allowed to stand in for the "
        "candidate-bound final gate"
    )
    assert "no successful final gate" in sealed.stderr


def test_a_dispatch_records_both_candidates(repository: Path, tmp_path: Path) -> None:
    """The detection half: a moved candidate is visible at the seam."""
    install_drift_policy(repository)
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)

    dispatch, returned, _ = drifting_attempt(repository, run_dir, add_lesson)

    row = dispatch_rows(run_dir)[0]
    assert row["dispatch_candidate_id"] == dispatch
    assert row["return_candidate_id"] == returned
    assert dispatch != returned
    assert dispatch in lineage_of(run_dir)
    assert returned in lineage_of(run_dir)


def test_a_dispatch_candidate_outside_the_lineage_refuses(repository: Path, tmp_path: Path) -> None:
    """A candidate this run never observed is not an anchor for anything."""
    install_drift_policy(repository)
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    handoff = run_dir / "critic.json"
    assert (
        run(
            "register-role-attempt",
            "--run-dir",
            str(run_dir),
            "--operation",
            "role.code-review",
            "--attempt",
            "1",
            "--role",
            "critic",
            "--harness",
            "native",
            "--reason",
            "initial",
            "--output",
            str(handoff),
        ).returncode
        == 0
    )
    metadata = json.loads((run_dir / "run.json").read_text())
    intelligence = start_span(
        engine_root=repository,
        trace_id=metadata["telemetry_trace_id"],
        parent_span_id=metadata["telemetry_root_span_id"],
        category="intelligence",
        operation="role.code-review",
        attempt=1,
        role="critic",
        harness="native",
    )
    finish_span(
        engine_root=repository,
        trace_id=metadata["telemetry_trace_id"],
        span_id=intelligence.span_id,
        outcome="success",
        exit_code=0,
    )

    refused = run(
        "record-role-dispatch",
        "--run-dir",
        str(run_dir),
        "--registration",
        str(handoff),
        "--state",
        "accepted",
        "--idle-telemetry",
        "unavailable",
        "--intelligence-span-id",
        intelligence.span_id,
        "--dispatch-candidate",
        "b" * 64,
    )

    assert refused.returncode == 2
    assert "is not a candidate this run recorded" in refused.stderr
    assert dispatch_rows(run_dir) == []


# --- The vocabulary's own fail-closed behaviour --------------------------------
#
# Sourcing the partition from a policy document rather than restating it in
# code is only safe if the tool refuses when the document does not parse. Every
# branch below is reachable: a `return DEFAULT_ENTRIES` in place of the
# absent-block raise would pass the entire drift suite without these tests.


def rewrite_drift_policy(repository: Path, transform) -> None:
    """Edit the fixture's copy of the policy that owns the vocabulary."""
    target = repository / "policies" / "orchestration-evidence.md"
    target.write_text(transform(target.read_text(encoding="utf-8")), encoding="utf-8")


def drop_vocabulary_block(text: str) -> str:
    start = text.index("```yaml\n# kickoff-evidence drift partitions")
    end = text.index("```", text.index("\n", start)) + 3
    return text[:start] + text[end:]


def vocabulary_block(text: str) -> str:
    start = text.index("```yaml\n# kickoff-evidence drift partitions")
    end = text.index("```", text.index("\n", start)) + 3
    return text[start:end]


def drifted_run_awaiting_classification(repository: Path, tmp_path: Path) -> Path:
    """A run with one recorded, unclassified inert-set drift ready to accept."""
    install_drift_policy(repository)
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    drifting_attempt(repository, run_dir, add_lesson)
    return run_dir


def test_an_absent_vocabulary_block_refuses(repository: Path, tmp_path: Path) -> None:
    """No block, no classification. The document is the contract or nothing is."""
    run_dir = drifted_run_awaiting_classification(repository, tmp_path)
    rewrite_drift_policy(repository, drop_vocabulary_block)

    refused = accept_drift(run_dir)

    assert refused.returncode == 2, (
        "a drift was classified against a vocabulary the policy no longer carries"
    )
    assert "carries 0" in refused.stderr
    assert "drift partitions" in refused.stderr
    assert drift_records(run_dir) == []


def test_a_duplicated_vocabulary_block_refuses(repository: Path, tmp_path: Path) -> None:
    """Exactly one, as this file's fenced-JSON reader already demands.

    Silently taking the first would make which block governs depend on document
    order, in a document that documents its own block format.
    """
    run_dir = drifted_run_awaiting_classification(repository, tmp_path)
    rewrite_drift_policy(repository, lambda text: text + "\n" + vocabulary_block(text) + "\n")

    refused = accept_drift(run_dir)

    assert refused.returncode == 2, "a second vocabulary block was resolved silently to the first"
    assert "carries 2" in refused.stderr
    assert drift_records(run_dir) == []


def test_an_unparseable_vocabulary_line_refuses(repository: Path, tmp_path: Path) -> None:
    """A dropped list marker is a silently smaller inert set, so it is an error."""
    run_dir = drifted_run_awaiting_classification(repository, tmp_path)
    rewrite_drift_policy(repository, lambda text: text.replace("  - lessons/\n", "  lessons/\n", 1))

    refused = accept_drift(run_dir)

    assert refused.returncode == 2, "an unparseable vocabulary line was skipped instead of refusing"
    assert "unparseable drift partition line" in refused.stderr
    assert drift_records(run_dir) == []


def test_an_empty_inert_set_refuses(repository: Path, tmp_path: Path) -> None:
    """An empty set would refuse every drift — correct, but for the wrong reason.

    It has to be distinguishable from a vocabulary that genuinely places
    nothing, or a truncated policy reads as a very strict one.
    """
    run_dir = drifted_run_awaiting_classification(repository, tmp_path)
    rewrite_drift_policy(
        repository,
        lambda text: text.replace(
            vocabulary_block(text),
            "```yaml\n# kickoff-evidence drift partitions\ninert:\n```",
        ),
    )

    refused = accept_drift(run_dir)

    assert refused.returncode == 2
    assert "inert set is empty" in refused.stderr
    assert drift_records(run_dir) == []


def test_a_single_component_entry_never_matches_a_nested_path(
    repository: Path, tmp_path: Path
) -> None:
    """`*` never crosses a `/`, which is the whole safety of the `LOG*.md` entry.

    A naive `fnmatch(path, entry)` matches `LOGS/notes/x.md` against `LOG*.md`,
    because `*` there spans separators — so a directory whose name merely starts
    with `LOG` would become inert, along with everything under it. The shipped
    vocabulary is used verbatim; only the path is contrived.
    """
    install_drift_policy(repository)
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)

    def mutate(root: Path) -> None:
        write_repo_file(root, "LOGS/notes/x.md", "# Not a root log\n")

    drifting_attempt(repository, run_dir, mutate)

    refused = accept_drift(run_dir)

    assert refused.returncode == 2, (
        "a nested path was placed in the inert set by a single-component entry, "
        "so `*` crossed a `/`"
    )
    assert sole_marker(refused.stderr) == {"drift-partition:"}, refused.stderr
    assert "LOGS/notes/x.md" in refused.stderr
    assert drift_records(run_dir) == []


def test_the_root_log_entry_still_matches_what_it_is_for(repository: Path, tmp_path: Path) -> None:
    """The other side of the same rule: `LOG*.md` does place the root log."""
    install_drift_policy(repository)
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)

    def mutate(root: Path) -> None:
        write_repo_file(root, "LOG.md", "# START\n")

    drifting_attempt(repository, run_dir, mutate)

    accepted = accept_drift(run_dir)

    assert accepted.returncode == 0, accepted.stderr
    assert drift_records(run_dir)[0]["drifted_paths"] == ["LOG.md"]


def test_a_poisoned_drift_record_refuses_at_ingest_too(repository: Path, tmp_path: Path) -> None:
    """Both readers apply the dispatch check, not just the gate at the end."""
    install_drift_policy(repository)
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    dispatch, returned, span_id = drifting_attempt(repository, run_dir, add_lesson)
    assert accept_drift(run_dir).returncode == 0

    record = drift_records(run_dir)[0]
    record["dispatch_candidate_id"] = "c" * 64
    (run_dir / "candidate-drift.jsonl").write_text(
        json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n"
    )

    refused = ingest_artifact(run_dir, returned, stale_batch(tmp_path, dispatch), span_id)

    assert refused.returncode == 2, (
        "a poisoned drift record was consulted at ingest without the check validate applies to it"
    )
    assert "does not describe the accepted dispatch it names" in refused.stderr
    assert journal_of(run_dir) == []


def test_a_stale_classification_refusal_names_its_recovery(
    repository: Path, tmp_path: Path
) -> None:
    """Append-only means there is no withdrawal verb, so say what to do instead."""
    install_drift_policy(repository)
    run_dir = tmp_path / "run"
    initialize(repository, run_dir)
    dispatch, returned, span_id = drifting_attempt(repository, run_dir, add_lesson)
    assert accept_drift(run_dir).returncode == 0
    assert (
        ingest_artifact(run_dir, returned, stale_batch(tmp_path, dispatch), span_id).returncode == 0
    )
    named = dict(finding("CODE-F009", returned))
    named["affected_paths"] = ["lessons/silent-guard-drift.md"]
    assert ingest(run_dir, tmp_path, [named], candidate=returned).returncode == 0

    validated = run("validate", "--run-dir", str(run_dir))

    assert validated.returncode == 2
    assert "cannot be withdrawn" in validated.stderr
    assert "fresh evidence run" in validated.stderr
