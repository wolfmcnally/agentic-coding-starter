"""Behavioral tests for run-scoped kickoff evidence."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "bin" / "kickoff-evidence"


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
    (root / ".gitignore").write_text(".kickoff/\n")
    (root / "phase.md").write_text("# Phase\n")
    (root / "policy.md").write_text("# Policy\n")
    (root / "code.py").write_text("VALUE = 1\n")
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-m", "fixture"], cwd=root, check=True, capture_output=True)
    return root


def run(
    *arguments: str,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(EVIDENCE), *arguments],
        cwd=cwd or ROOT,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )


def initialize(repository: Path, run_dir: Path) -> str:
    result = run(
        "init",
        "--run-dir",
        str(run_dir),
        "--root",
        str(repository),
        "--phase",
        "1.1",
        "--authority",
        "phase.md::Acceptance",
        "--authority",
        "policy.md",
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


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
) -> subprocess.CompletedProcess[str]:
    input_path = tmp_path / "findings-input.json"
    input_path.write_text(json.dumps({"findings": findings}))
    expected_candidate = candidate or str(
        findings[0]["resolved_in"] or findings[0]["introduced_in"]
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

    recorded = run(
        "record-gate",
        "--run-dir",
        str(run_dir),
        "--candidate",
        candidate,
        "--command",
        "./bin/check all",
        "--selection-reason",
        "Final authoritative gate",
        "--exit-code",
        "0",
        "--warning-count",
        "0",
        "--artifact",
        str(artifact),
        "--final",
    )
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
        "--command",
        "./bin/check all",
        "--selection-reason",
        "Final authoritative gate",
        "--exit-code",
        "0",
        "--warning-count",
        "0",
    )
    assert stale.returncode == 2
    assert "candidate mismatch" in stale.stderr


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


def test_validate_can_require_successful_named_final_gate(repository: Path, tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    candidate = initialize(repository, run_dir)

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

    recorded = run(
        "record-gate",
        "--run-dir",
        str(run_dir),
        "--candidate",
        candidate,
        "--command",
        "./bin/check all",
        "--selection-reason",
        "Authoritative acceptance close",
        "--exit-code",
        "0",
        "--warning-count",
        "0",
        "--final",
    )
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
