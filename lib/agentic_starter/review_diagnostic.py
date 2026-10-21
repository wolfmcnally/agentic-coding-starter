"""Finite, nonprivate native lifecycle qualification; never a product review lane."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agentic_starter import test_runner, workflow  # noqa: E402

FIXTURE = (
    "Review this synthetic function only: def identity(value): return value. "
    "Reply DIAGNOSTIC_READY."
)
HOOK_SHA256 = "9ae3e48647204c2ff35937c11fafc97a4a09e3efa8507c0976a1e1a6c61d0f1c"
OPERATIONS = ("startup", "compact", "resume")
TOTAL_SECONDS = 600


class DiagnosticError(ValueError):
    """A refused diagnostic, not failed product acceptance."""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(target: Path, value: object) -> None:
    # The enclosing exclusive run lock serializes writers. Never truncate history.
    with target.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, sort_keys=True)
        stream.write("\n")
    target.chmod(0o600)


def append(target: Path, value: object) -> None:
    with target.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, sort_keys=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def prepare(run: Path, *, authority: str) -> None:
    """Create real diagnostic metadata, without borrowing a phase or its budget."""
    if not authority.strip():
        raise DiagnosticError("an attributable diagnostic authority reference is required")
    run = run.absolute()
    if run != run.resolve() or run.exists():
        raise DiagnosticError("diagnostic destination must be new and canonical")
    run.mkdir(mode=0o700)
    native_id = workflow.review_session_id(None)
    trace_id = "diagnostic-" + workflow.review_session_id(None)
    record = {
        "schema_version": 3,
        "role": "critic",
        "operation": "role.code-review",
        "harness": "claude",
        "model": "fable",
        "effort": "high",
        "attempt": 1,
        "candidate_id": digest(FIXTURE.encode()),
        "telemetry_trace_id": trace_id,
        "telemetry_root_span_id": "root-" + native_id,
    }
    write_json(run / "code-registration.json", record)
    append(run / "role-attempts.jsonl", record)
    (run / "fixture.txt").write_text(FIXTURE, encoding="utf-8")
    (run / "fixture.txt").chmod(0o600)
    (run / "workspace").mkdir(mode=0o700)
    write_json(
        run / "diagnostic.json",
        {
            "schema_version": 1,
            "purpose": "native-binding-diagnostic",
            "authority": authority,
            "session_id": native_id,
            "trace_id": trace_id,
            "fixture_sha256": digest(FIXTURE.encode()),
            "registration_sha256": digest((run / "code-registration.json").read_bytes()),
            "created_at": time.time(),
            "deadline": time.time() + TOTAL_SECONDS,
            "boot_monotonic": time.monotonic(),
            "producer_sha256": digest(Path(__file__).read_bytes()),
        },
    )
    append(run / "events.jsonl", {"event": "prepared", "trace_id": trace_id})


def validate(run: Path) -> dict:
    run = run.absolute()
    workflow.review_path(run / "code-registration.json")
    document = json.loads((run / "diagnostic.json").read_text())
    record, registration_digest = workflow.review_registration(run / "code-registration.json")
    if (
        document["purpose"] != "native-binding-diagnostic"
        or record.get("candidate_id") != digest(FIXTURE.encode())
        or record["telemetry_trace_id"] != document["trace_id"]
        or registration_digest != document["registration_sha256"]
        or document["fixture_sha256"] != digest(FIXTURE.encode())
        or (run / "fixture.txt").read_bytes() != FIXTURE.encode()
        or document["producer_sha256"] != digest(Path(__file__).read_bytes())
    ):
        raise DiagnosticError("diagnostic seal mismatch")
    workflow.review_session_id(document["session_id"])
    remaining = min(
        document["deadline"] - time.time(),
        TOTAL_SECONDS - (time.monotonic() - document["boot_monotonic"]),
    )
    if not 0 < remaining <= TOTAL_SECONDS or time.monotonic() < document["boot_monotonic"]:
        raise DiagnosticError("diagnostic deadline expired or boot continuity lost")
    document["remaining"] = remaining
    return document


def context_profile(settings: Path, hook: Path) -> dict:
    """Inventory configuration without inventing runtime observations or gates.

    Ambient MCP/plugins are permitted. Availability, connection, enrollment,
    assignment-scoped messages and unrelated context are different properties;
    inspecting settings establishes only the first. No installed settings change.
    """
    if digest(hook.read_bytes()) != HOOK_SHA256:
        raise DiagnosticError("installed continuation hook differs from qualified bytes")
    document = json.loads(settings.read_text())
    configured_hooks = []
    for event, groups in document.get("hooks", {}).items():
        for group in groups:
            for entry in group.get("hooks", []):
                configured_hooks.append(
                    {
                        "event": event,
                        "matcher": group.get("matcher"),
                        "configuration_sha256": digest(json.dumps(entry, sort_keys=True).encode()),
                    }
                )
    # Do not print config values, infer a connection from a catalog, or require
    # a new bus-nonparticipant architecture as a precondition for every review.
    return {
        "state": "INSPECTION-ONLY",
        "configured_availability": {
            "enabled_plugin_entries": sum(
                bool(value) for value in document.get("enabledPlugins", {}).values()
            ),
            "mcp_entries_in_this_document": len(document.get("mcpServers", {})),
            "configured_hooks": configured_hooks,
        },
        "runtime_evidence": {
            name: {"state": "NOT-OBSERVED", "evidence": []}
            for name in (
                "connection_startup",
                "identity_enrollment",
                "assignment_scoped_messaging",
                "unrelated_context_delivery",
            )
        },
        "settings_sha256": digest(settings.read_bytes()),
        "hook_sha256": HOOK_SHA256,
        "remaining_evidence": [
            "current fresh candidate-bound registration and native launch contract",
            "independent initial review context and actual delivered context evidence",
            "actual native startup, compact and exact-session resume observations",
        ],
    }


def local_settings(run: Path, hook: Path) -> dict:
    """Add an observer only; preserve ambient MCP/plugins and security settings."""
    observer = [
        sys.executable,
        str(Path(__file__).resolve()),
        "observe",
        "--run-dir",
        str(run),
        "--hook",
        str(hook),
    ]
    import shlex

    return {
        "hooks": {
            "SessionStart": [
                {
                    "matcher": "startup|compact|resume",
                    "hooks": [
                        {
                            "type": "command",
                            "command": shlex.join(observer),
                            "timeout": 10,
                        }
                    ],
                }
            ]
        },
    }


def observe(run: Path, hook: Path, event: dict) -> None:
    """Observe a native event; never read a packet or synthesize a lifecycle event."""
    document = validate(run)
    binding = json.loads(os.environ.get("CONTINUATION_REVIEW_BINDING", "null"))
    if not isinstance(binding, dict) or any(
        [
            event.get("hook_event_name") != "SessionStart",
            event.get("source") not in OPERATIONS,
            event.get("session_id") != document["session_id"],
            event.get("cwd") != str(run / "workspace"),
            binding.get("session_id") != document["session_id"],
            binding.get("cwd") != event.get("cwd"),
            binding.get("process_session_id") != os.getsid(0),
            binding.get("registration_sha256") != document["registration_sha256"],
            binding.get("registration_path") != str(run / "code-registration.json"),
            not binding.get("issued_at", float("inf"))
            <= time.time()
            < binding.get("expires_at", 0),
        ]
    ):
        raise DiagnosticError("native event does not match diagnostic binding")
    if digest(hook.read_bytes()) != HOOK_SHA256:
        raise DiagnosticError("hook changed before native observation")
    # This is an additive diagnostic observer invoking the installed guard on the
    # actual native event. The ordinary compact hook remains installed and active.
    result = subprocess.run(
        [sys.executable, str(hook), "claude"],
        input=json.dumps(event),
        text=True,
        capture_output=True,
        timeout=8,
        check=False,
    )
    append(
        run / "observations.jsonl",
        {
            "source": event["source"],
            "session_id": event["session_id"],
            "cwd": event["cwd"],
            "process_session_id": os.getsid(0),
            "registration_sha256": document["registration_sha256"],
            "hook_sha256": HOOK_SHA256,
            "exit_code": result.returncode,
            "empty_stdout": result.stdout == "",
            "empty_stderr": result.stderr == "",
        },
    )
    if result.returncode or result.stdout or result.stderr:
        raise DiagnosticError("installed guard did not return silent success")


def launch(run: Path, *, settings: Path, hook: Path) -> None:
    """Inspection is not a verified native registration/launch contract.

    Deliberately no force/receipt/skip flag: a hand-authored approval receipt or
    absent hooks cannot turn incomplete evidence into permission to send data.
    """
    with (run / ".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        validate(run)
        if (run / "launch-claimed.json").exists():
            raise DiagnosticError("diagnostic launch already claimed; replay refused")
        profile = context_profile(settings, hook)
        append(run / "events.jsonl", {"event": "prelaunch-held", "profile": profile})
        raise DiagnosticError(
            "native launch held: current registered launch/lifecycle contract is unverified"
        )


def supervised_fixture(
    command: list[str],
    binding: dict,
    *,
    cwd: Path,
    environment: dict[str, str],
    timeout: float,
) -> subprocess.CompletedProcess:
    """Shared binder/supervisor seam, qualified only with fake native executables.

    Not a CLI launch route. Production native admission remains held above.
    """
    return test_runner.run_command(
        [
            sys.executable,
            str(Path(workflow.__file__).resolve()),
            "--review-exec",
            json.dumps({"command": command, "binding": binding}),
        ],
        cwd=cwd,
        timeout=min(TOTAL_SECONDS, timeout),
        capture=True,
        environment=environment,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    prepare_parser = sub.add_parser("prepare")
    prepare_parser.add_argument("--run-dir", type=Path, required=True)
    prepare_parser.add_argument("--authority", required=True)
    for action in ("inspect-profile", "launch", "observe"):
        command = sub.add_parser(action)
        command.add_argument("--run-dir", type=Path, required=True)
        command.add_argument("--hook", type=Path, required=True)
        if action != "observe":
            command.add_argument("--settings", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.action == "prepare":
            prepare(args.run_dir, authority=args.authority)
        elif args.action == "inspect-profile":
            validate(args.run_dir)
            print(json.dumps(context_profile(args.settings, args.hook), sort_keys=True))
        elif args.action == "observe":
            observe(args.run_dir, args.hook, json.load(sys.stdin))
        else:
            launch(args.run_dir, settings=args.settings, hook=args.hook)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"review-diagnostic: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
