"""Independent observations and primary decisions, without approval semantics."""

from __future__ import annotations

import fcntl
import hashlib
import json
from pathlib import Path
from typing import Any


class AdvisoryError(ValueError):
    """Incomplete or contradictory advisory evidence."""


def read(path: Path, default: Any = None) -> Any:
    if not path.exists() and default is not None:
        return default
    return json.loads(path.read_text())


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def check_report(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != {"summary", "findings"}:
        raise AdvisoryError("advice requires summary/findings, never a verdict")
    if not isinstance(value["summary"], str) or not isinstance(value["findings"], list):
        raise AdvisoryError("invalid advisory report")
    seen = set()
    for item in value["findings"]:
        if not isinstance(item, dict) or set(item) != {
            "id",
            "severity",
            "affected_paths",
            "evidence",
            "consequence",
            "suggestion",
        }:
            raise AdvisoryError("advisory finding has unknown or missing fields")
        for key in ("id", "evidence", "consequence", "suggestion"):
            if not isinstance(item[key], str) or not item[key].strip():
                raise AdvisoryError(f"advisory {key} must be nonempty")
        if item["id"] in seen:
            raise AdvisoryError("duplicate advisory finding")
        seen.add(item["id"])
        if item["severity"] not in {
            "critical",
            "high",
            "medium",
            "low",
            "informational",
        }:
            raise AdvisoryError("invalid advisory severity; blocking is not advisory")
        if not isinstance(item["affected_paths"], list) or any(
            not isinstance(p, str) or not p or Path(p).is_absolute() or ".." in Path(p).parts
            for p in item["affected_paths"]
        ):
            raise AdvisoryError("advisory paths must be repository-relative")
    return value


def budget_path(root: Path, phase: str) -> Path:
    return (
        root
        / ".kickoff"
        / "advice-budgets"
        / (hashlib.sha256(phase.encode()).hexdigest() + ".jsonl")
    )


def start(
    root: Path, phase: str, run_dir: Path, operation: str, attempt: int, cause: str
) -> dict[str, Any]:
    """Claim a launch atomically across continuations, before candidate transmission."""
    file = budget_path(root, phase)
    file.parent.mkdir(parents=True, exist_ok=True)
    with file.open("a+") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        handle.seek(0)
        records = active_launches([json.loads(line) for line in handle if line.strip()])
        matching = [r for r in records if r["operation"] == operation]
        if any(r["run"] == str(run_dir.resolve()) and r["attempt"] == attempt for r in matching):
            raise AdvisoryError("advisory invocation already launched; resume is another pass")
        if len(matching) >= 2:
            raise AdvisoryError("maximum two advisory passes per stage across continuations")
        if matching and not cause.strip():
            raise AdvisoryError("second advisory pass requires a recorded cause")
        row = {
            "run": str(run_dir.resolve()),
            "operation": operation,
            "attempt": attempt,
            "pass": len(matching) + 1,
            "cause": cause,
        }
        handle.write(json.dumps(row, sort_keys=True) + "\n")
        handle.flush()
        return row


def active_launches(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cancelled = {digest(r["not_started"]) for r in records if "not_started" in r}
    return [r for r in records if "not_started" not in r and digest(r) not in cancelled]


def cancel_unstarted(root: Path, phase: str, claim: dict[str, Any]) -> None:
    """Only the watcher calls this after Popen fails to create any child."""
    with budget_path(root, phase).open("a+") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        handle.seek(0)
        rows = active_launches([json.loads(line) for line in handle if line.strip()])
        if claim not in rows:
            raise AdvisoryError("unstarted advisory claim is missing")
        handle.write(json.dumps({"not_started": claim}, sort_keys=True) + "\n")
        handle.flush()


def launches(root: Path, phase: str) -> list[dict[str, Any]]:
    file = budget_path(root, phase)
    if not file.exists():
        return []
    return active_launches(
        [json.loads(line) for line in file.read_text().splitlines() if line.strip()]
    )


def validate_decision(
    decision: Any, reports: list[dict[str, Any]], candidate: str, required: set[str]
) -> None:
    if not isinstance(decision, dict) or set(decision) != {
        "candidate_id",
        "delta_assessment",
        "requirements_checked",
        "dispositions",
        "reports_sha256",
    }:
        raise AdvisoryError("primary decision has unknown or missing fields")
    if decision["candidate_id"] != candidate or decision["reports_sha256"] != digest(reports):
        raise AdvisoryError("primary acceptance is stale for the candidate or advice")
    for key in ("delta_assessment", "requirements_checked"):
        if not isinstance(decision[key], str) or not decision[key].strip():
            raise AdvisoryError(f"primary acceptance requires {key}")
    if required - {r["kind"] for r in reports}:
        raise AdvisoryError("required independent advisory report is missing")
    expected = {}
    for row in reports:
        check_report(row["report"])
        for finding in row["report"]["findings"]:
            expected[row["report_id"] + ":" + finding["id"]] = finding
    dispositions = decision["dispositions"]
    if not isinstance(dispositions, list):
        raise AdvisoryError("primary dispositions must be a list")
    seen = set()
    for item in dispositions:
        if not isinstance(item, dict) or set(item) != {
            "finding",
            "action",
            "reason",
            "verification",
        }:
            raise AdvisoryError("invalid primary disposition shape")
        key = item["finding"]
        if (
            key not in expected
            or key in seen
            or item["action"] not in {"adopt", "decline", "defer"}
        ):
            raise AdvisoryError("invalid or duplicate primary disposition")
        seen.add(key)
        if not isinstance(item["reason"], str) or not isinstance(item["verification"], str):
            raise AdvisoryError("disposition evidence must be text")
        if (
            expected[key]["severity"] in {"critical", "high", "medium"}
            and not item["reason"].strip()
        ):
            raise AdvisoryError("material advice requires a primary rationale")
        if item["action"] == "adopt" and not item["verification"].strip():
            raise AdvisoryError("adopted correction requires verification")
    material = {
        key for key, f in expected.items() if f["severity"] in {"critical", "high", "medium"}
    }
    if material - seen:
        raise AdvisoryError("material advice lacks primary disposition")
