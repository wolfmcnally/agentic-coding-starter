"""Precise, privacy-bounded execution telemetry.

Runtime state lives outside the repository.  Durable trace bundles are a
strict projection of that state into the ledger owned by the selected scope.
"""

from __future__ import annotations

import contextlib
import dataclasses
import datetime as dt
import decimal
import fcntl
import hashlib
import json
import os
import re
import signal
import subprocess
import tempfile
import threading
import time
import uuid
from collections.abc import Iterator, Mapping, Sequence
from pathlib import Path
from typing import Any, Protocol

SPAN_SCHEMA = "agentic_starter.execution_span.v1"
TRACE_SCHEMA = "agentic_starter.execution_trace.v1"
RUNTIME_TRACE_SCHEMA = "agentic_starter.execution_trace.runtime.v1"
RUNTIME_SPAN_SCHEMA = "agentic_starter.execution_span.runtime.v1"
MANAGED_RUN_SCHEMA = "agentic_starter.managed_run.runtime.v1"

CATEGORIES = frozenset({"run", "intelligence", "gate", "reconciliation", "wait"})
OUTCOMES = frozenset({"success", "error", "timeout", "cancelled", "interrupted"})
SCOPES = frozenset({"engine", "project", "catalog"})
TIMEOUT_KINDS = frozenset({"command", "first-event", "idle", "hard"})

_ID_RE = re.compile(r"^[0-9a-f]{32}$")
_CYCLE_RE = re.compile(r"^[0-9a-f]{8}$")
_PHASE_RE = re.compile(r"^\d+(?:\.\d+)*$")
_TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/+-]{0,127}$")
_WINDOWS_ABS_RE = re.compile(r"^[A-Za-z]:[\\/]")
_SPAN_REQUIRED = frozenset(
    {
        "schema",
        "trace_id",
        "span_id",
        "parent_span_id",
        "run_type",
        "scope",
        "scope_id",
        "category",
        "operation",
        "attempt",
        "started_at",
        "ended_at",
        "start_offset_ns",
        "end_offset_ns",
        "duration_ns",
        "outcome",
    }
)
_SPAN_OPTIONAL = frozenset(
    {
        "exit_code",
        "timeout_kind",
        "timeout_ns",
        "findings_reported",
        "actionable_findings",
        "harness",
        "role",
        "model",
        "effort",
        "batch_id",
        "concurrency_group",
        "token_reference",
    }
)
_TRACE_KEYS = frozenset(
    {"schema", "trace_id", "finalized_at", "scope", "scope_id", "root_span_id", "spans"}
)
_METADATA_KEYS = (
    "harness",
    "role",
    "model",
    "effort",
    "batch_id",
    "concurrency_group",
)


class TelemetryError(RuntimeError):
    """Base class for execution-telemetry failures."""


class ValidationError(TelemetryError):
    """A runtime or durable record violates its exact schema."""


class ScopeError(TelemetryError):
    """A requested scope does not own the supplied path."""


class IncompleteTraceError(TelemetryError):
    """A trace cannot be finalized because one or more spans are open."""


class ClockDomainError(TelemetryError):
    """Elapsed time cannot be proven within the current monotonic clock domain."""


class Clock(Protocol):
    def utc_now(self) -> dt.datetime: ...

    def monotonic_ns(self) -> int: ...

    def boot_id(self) -> str: ...


class SystemClock:
    def utc_now(self) -> dt.datetime:
        return dt.datetime.now(dt.UTC)

    def monotonic_ns(self) -> int:
        return time.monotonic_ns()

    def boot_id(self) -> str:
        linux_id = Path("/proc/sys/kernel/random/boot_id")
        if linux_id.is_file():
            value = linux_id.read_text(encoding="utf-8").strip()
            if value:
                return value
        if os.uname().sysname == "Darwin":
            result = subprocess.run(
                ["/usr/sbin/sysctl", "-n", "kern.boottime"],
                check=True,
                capture_output=True,
                text=True,
            )
            value = result.stdout.strip()
            if value:
                return value
        raise ClockDomainError("cannot establish the current boot identity")


# macOS derives `kern.boottime` as (now - uptime) rather than storing it, so the
# value is re-computed on every read and drifts as the clock is disciplined: the
# `usec` field moved 393666 -> 309306 across two days of one uninterrupted boot,
# which made `recover` and `finish` raise ClockDomainError on a machine that had
# never rebooted. Comparing raw strings compares a moving reference, so the
# check could only ever say "different boot" for a long-lived trace.
#
# The stable component is `sec`. A reboot moves it by minutes or hours; clock
# discipline moves it by well under a second. Compare on `sec` with a small
# tolerance, and fall back to exact equality for identity formats that are not
# Darwin's (Linux's /proc boot_id is a stable UUID and compares exactly).
BOOT_ID_DRIFT_TOLERANCE_SECONDS = 5

_DARWIN_BOOT_SECONDS = re.compile(r"sec\s*=\s*(\d+)")


def boot_seconds(value: str) -> int | None:
    """Return the stable second-resolution boot epoch, or None if not Darwin-shaped."""
    match = _DARWIN_BOOT_SECONDS.search(value or "")
    return int(match.group(1)) if match else None


def same_boot(left: str, right: str) -> bool:
    """True when two boot identities denote the same boot."""
    if left == right:
        return True
    left_seconds, right_seconds = boot_seconds(left), boot_seconds(right)
    if left_seconds is None or right_seconds is None:
        return False
    return abs(left_seconds - right_seconds) <= BOOT_ID_DRIFT_TOLERANCE_SECONDS


@dataclasses.dataclass(frozen=True)
class SpanHandle:
    trace_id: str
    span_id: str


@dataclasses.dataclass(frozen=True)
class ObservedResult:
    trace_id: str
    span_id: str | None
    exit_code: int
    outcome: str
    telemetry_complete: bool
    error_code: str | None = None


def _utc_text(value: dt.datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValidationError("UTC timestamps must be timezone-aware")
    return value.astimezone(dt.UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _parse_utc(value: object, field: str) -> dt.datetime:
    if not isinstance(value, str) or "\n" in value:
        raise ValidationError(f"{field} must be a UTC timestamp")
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValidationError(f"{field} must be a UTC timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != dt.timedelta(0):
        raise ValidationError(f"{field} must use UTC")
    return parsed


def _require_exact_keys(
    value: Mapping[str, Any], required: frozenset[str], optional: frozenset[str], label: str
) -> None:
    keys = frozenset(value)
    missing = required - keys
    extra = keys - required - optional
    if missing:
        raise ValidationError(f"{label} missing keys: {', '.join(sorted(missing))}")
    if extra:
        raise ValidationError(f"{label} has unknown keys: {', '.join(sorted(extra))}")


def _require_id(value: object, field: str) -> str:
    if not isinstance(value, str) or not _ID_RE.fullmatch(value):
        raise ValidationError(
            f"{field} must be a canonical UUID4 id of 32 lowercase hexadecimal characters"
        )
    parsed = uuid.UUID(hex=value)
    if parsed.version != 4 or parsed.variant != uuid.RFC_4122:
        raise ValidationError(
            f"{field} must be a canonical UUID4 id of 32 lowercase hexadecimal characters"
        )
    return value


def _require_token(value: object, field: str) -> str:
    if isinstance(value, str) and (value.startswith(("/", "~")) or _WINDOWS_ABS_RE.match(value)):
        raise ValidationError(f"{field} must not be an absolute or home-relative path")
    if not isinstance(value, str) or not _TOKEN_RE.fullmatch(value):
        raise ValidationError(f"{field} must be a bounded stable token")
    return value


def _validate_token_reference(value: object) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise ValidationError("token_reference must be an object")
    _require_exact_keys(
        value, frozenset({"ledger", "cycle_id", "role"}), frozenset(), "token_reference"
    )
    if value["ledger"] != "USAGE_LOG.md":
        raise ValidationError("token_reference ledger must be USAGE_LOG.md")
    return {
        "ledger": "USAGE_LOG.md",
        "cycle_id": _require_token(value["cycle_id"], "token_reference.cycle_id"),
        "role": _require_token(value["role"], "token_reference.role"),
    }


def _require_int(value: object, field: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError(f"{field} must be an integer")
    if minimum is not None and value < minimum:
        raise ValidationError(f"{field} must be at least {minimum}")
    return value


def _timeout_nanoseconds(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError("timeout_seconds must be a finite positive number")
    seconds = decimal.Decimal(str(value))
    if not seconds.is_finite() or seconds <= 0:
        raise ValidationError("timeout_seconds must be finite and strictly positive")
    nanoseconds = seconds * decimal.Decimal(1_000_000_000)
    if nanoseconds != nanoseconds.to_integral_value():
        raise ValidationError("timeout_seconds must resolve to an exact integral nanosecond value")
    result = int(nanoseconds)
    if result > (1 << 63) - 1:
        raise ValidationError("timeout_seconds exceeds the signed 64-bit nanosecond range")
    return result


def validate_span(span: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(span, Mapping):
        raise ValidationError("span must be an object")
    _require_exact_keys(span, _SPAN_REQUIRED, _SPAN_OPTIONAL, "span")
    if span["schema"] != SPAN_SCHEMA:
        raise ValidationError(f"span schema must be {SPAN_SCHEMA}")
    trace_id = _require_id(span["trace_id"], "trace_id")
    _require_id(span["span_id"], "span_id")
    parent = span["parent_span_id"]
    if parent is not None:
        _require_id(parent, "parent_span_id")
    _require_token(span["run_type"], "run_type")
    if span["scope"] not in SCOPES:
        raise ValidationError("unknown scope")
    _require_token(span["scope_id"], "scope_id")
    if span["scope"] == "engine" and span["scope_id"] != "engine":
        raise ValidationError("engine scope requires scope_id engine")
    if span["scope"] == "catalog" and span["scope_id"] != "portfolio":
        raise ValidationError("catalog scope requires scope_id portfolio")
    if span["category"] not in CATEGORIES:
        raise ValidationError("unknown category")
    _require_token(span["operation"], "operation")
    _require_int(span["attempt"], "attempt", minimum=1)
    _parse_utc(span["started_at"], "started_at")
    _parse_utc(span["ended_at"], "ended_at")
    start = _require_int(span["start_offset_ns"], "start_offset_ns", minimum=0)
    end = _require_int(span["end_offset_ns"], "end_offset_ns", minimum=0)
    duration = _require_int(span["duration_ns"], "duration_ns", minimum=0)
    if end < start or duration != end - start:
        raise ValidationError("duration_ns must equal end_offset_ns - start_offset_ns")
    outcome = span["outcome"]
    if outcome not in OUTCOMES:
        raise ValidationError("unknown outcome")
    if "exit_code" in span:
        exit_code = _require_int(span["exit_code"], "exit_code", minimum=0)
        if outcome == "success" and exit_code != 0:
            raise ValidationError("success requires exit_code 0")
        if outcome == "error" and exit_code == 0:
            raise ValidationError("process-backed error requires a nonzero exit_code")
        if outcome == "timeout" and exit_code != 124:
            raise ValidationError("command timeout requires exit_code 124")
        if outcome in {"cancelled", "interrupted"} and exit_code == 0:
            raise ValidationError(f"{outcome} requires a nonzero exit_code")
    if outcome == "timeout":
        if span.get("timeout_kind") not in TIMEOUT_KINDS:
            raise ValidationError("timeout requires a valid timeout_kind")
        _require_int(span.get("timeout_ns"), "timeout_ns", minimum=1)
    elif "timeout_kind" in span or "timeout_ns" in span:
        raise ValidationError("timeout fields are valid only for timeout outcomes")
    for key in _METADATA_KEYS:
        if key in span:
            _require_token(span[key], key)
    for key in ("findings_reported", "actionable_findings"):
        if key in span:
            _require_int(span[key], key, minimum=0)
    if "token_reference" in span:
        _validate_token_reference(span["token_reference"])
    return dict(span) | {"trace_id": trace_id}


def validate_bundle(bundle: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(bundle, Mapping):
        raise ValidationError("trace bundle must be an object")
    _require_exact_keys(bundle, _TRACE_KEYS, frozenset(), "trace bundle")
    if bundle["schema"] != TRACE_SCHEMA:
        raise ValidationError(f"trace schema must be {TRACE_SCHEMA}")
    trace_id = _require_id(bundle["trace_id"], "trace_id")
    root_id = _require_id(bundle["root_span_id"], "root_span_id")
    if bundle["scope"] not in SCOPES:
        raise ValidationError("unknown trace scope")
    _require_token(bundle["scope_id"], "scope_id")
    if bundle["scope"] == "engine" and bundle["scope_id"] != "engine":
        raise ValidationError("engine scope requires scope_id engine")
    if bundle["scope"] == "catalog" and bundle["scope_id"] != "portfolio":
        raise ValidationError("catalog scope requires scope_id portfolio")
    _parse_utc(bundle["finalized_at"], "finalized_at")
    if not isinstance(bundle["spans"], list) or not bundle["spans"]:
        raise ValidationError("spans must be a nonempty array")
    spans = [validate_span(item) for item in bundle["spans"]]
    by_id = {span["span_id"]: span for span in spans}
    if len(by_id) != len(spans):
        raise ValidationError("span ids must be unique")
    if root_id not in by_id:
        raise ValidationError("root_span_id does not identify a span")
    roots = [span for span in spans if span["parent_span_id"] is None]
    if len(roots) != 1 or roots[0]["span_id"] != root_id or roots[0]["category"] != "run":
        raise ValidationError("trace must contain exactly one run-category root")
    root = roots[0]
    if root["start_offset_ns"] != 0:
        raise ValidationError("trace root must start at offset zero")
    for span in spans:
        if span["trace_id"] != trace_id:
            raise ValidationError("every span must belong to the bundle trace")
        if span["scope"] != bundle["scope"] or span["scope_id"] != bundle["scope_id"]:
            raise ValidationError("span scope must match trace scope")
        if span["run_type"] != root["run_type"]:
            raise ValidationError("every span must use the root run_type")
        parent_id = span["parent_span_id"]
        if parent_id is not None:
            if span["category"] == "run":
                raise ValidationError("category run is reserved for the trace root")
            parent = by_id.get(parent_id)
            if parent is None:
                raise ValidationError("parent_span_id does not identify a span")
            if (
                span["start_offset_ns"] < parent["start_offset_ns"]
                or span["end_offset_ns"] > parent["end_offset_ns"]
            ):
                raise ValidationError("child interval must be contained by its parent")
            seen = {span["span_id"]}
            cursor = parent
            while True:
                if cursor["span_id"] in seen:
                    raise ValidationError("span ancestry contains a cycle")
                seen.add(cursor["span_id"])
                if cursor["parent_span_id"] is None:
                    if cursor["span_id"] != root_id:
                        raise ValidationError("span ancestry does not reach the trace root")
                    break
                cursor = by_id.get(cursor["parent_span_id"])
                if cursor is None:
                    raise ValidationError("span ancestry is incomplete")
    expected = sorted(spans, key=lambda item: (item["start_offset_ns"], item["span_id"]))
    if bundle["spans"] != expected:
        raise ValidationError("spans must be sorted by start_offset_ns then span_id")
    return dict(bundle)


def telemetry_state_root() -> Path:
    explicit = os.environ.get("AGENTIC_STARTER_EXECUTION_TELEMETRY_DIR")
    if explicit:
        return Path(explicit).expanduser().resolve()
    xdg = os.environ.get("XDG_STATE_HOME")
    base = Path(xdg).expanduser() if xdg else Path.home() / ".local" / "state"
    return (base / "agentic-starter" / "execution-telemetry").resolve()


def discover_engine_root(start: Path | str | None = None) -> Path:
    cursor = Path(start or Path.cwd()).expanduser().resolve()
    if cursor.is_file():
        cursor = cursor.parent
    for candidate in (cursor, *cursor.parents):
        if (
            (candidate / "CLAUDE.md").exists()
            and ((candidate / "plan").is_dir() or (candidate / "projects").is_dir())
            and (candidate / "policies").is_dir()
        ):
            return candidate
    raise ScopeError("could not discover an engine root")


def repo_key(engine_root: Path | str) -> str:
    value = str(Path(engine_root).resolve()).encode()
    return hashlib.sha1(value).hexdigest()[:12]


def scope_ledger_path(
    engine_root: Path | str, scope_root: Path | str, scope: str, scope_id: str
) -> Path:
    engine = Path(engine_root).resolve()
    supplied = Path(scope_root).resolve()
    if scope == "engine" and scope_id == "engine" and supplied == engine:
        return engine / "EXECUTION_LOG.jsonl"
    if scope == "project":
        _require_token(scope_id, "scope_id")
        expected = (engine / "projects" / scope_id).resolve()
        if supplied == expected and expected.parent == (engine / "projects").resolve():
            return expected / "EXECUTION_LOG.jsonl"
    if scope == "catalog" and scope_id == "portfolio":
        expected = (engine / "portfolio").resolve()
        if supplied == expected:
            return expected / "EXECUTION_LOG.jsonl"
    raise ScopeError("scope, scope_id, and scope_root do not identify an owned ledger")


def _trace_dir(engine_root: Path | str, trace_id: str) -> Path:
    _require_id(trace_id, "trace_id")
    return telemetry_state_root() / repo_key(engine_root) / trace_id


def _fsync_directory(directory: Path) -> None:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    descriptor = os.open(directory, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _atomic_json(file_path: Path, value: Mapping[str, Any]) -> None:
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary_name = tempfile.mkstemp(prefix=f".{file_path.name}.", dir=file_path.parent)
        temporary = Path(temporary_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(value, stream, sort_keys=True, separators=(",", ":"))
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, file_path)
            _fsync_directory(file_path.parent)
        finally:
            with contextlib.suppress(FileNotFoundError):
                temporary.unlink()
    except OSError as exc:
        raise TelemetryError(f"cannot write telemetry state: {file_path.name}") from exc


def _read_json(file_path: Path) -> dict[str, Any]:
    try:
        value = json.loads(file_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TelemetryError(f"cannot read telemetry state: {file_path.name}") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"{file_path.name} must contain an object")
    return value


@contextlib.contextmanager
def _trace_lock(trace_dir: Path) -> Iterator[None]:
    try:
        trace_dir.mkdir(parents=True, exist_ok=True)
        lock_path = trace_dir / ".write.lock"
        with lock_path.open("a+", encoding="utf-8") as stream:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
    except OSError as exc:
        raise TelemetryError("cannot lock telemetry trace") from exc


def _load_runtime(engine_root: Path | str, trace_id: str) -> tuple[Path, dict[str, Any]]:
    trace_dir = _trace_dir(engine_root, trace_id)
    trace = _read_json(trace_dir / "trace.json")
    if trace.get("schema") != RUNTIME_TRACE_SCHEMA or trace.get("trace_id") != trace_id:
        raise ValidationError("runtime trace metadata is invalid")
    return trace_dir, trace


def _metadata(
    *,
    harness: str | None = None,
    role: str | None = None,
    model: str | None = None,
    effort: str | None = None,
    batch_id: str | None = None,
    concurrency_group: str | None = None,
    token_cycle_id: str | None = None,
    token_role: str | None = None,
) -> dict[str, Any]:
    values = {
        "harness": harness,
        "role": role,
        "model": model,
        "effort": effort,
        "batch_id": batch_id,
        "concurrency_group": concurrency_group,
    }
    result = {key: _require_token(value, key) for key, value in values.items() if value is not None}
    if (token_cycle_id is None) != (token_role is None):
        raise ValidationError("token_cycle_id and token_role must be supplied together")
    if token_cycle_id is not None and token_role is not None:
        result["token_reference"] = {
            "ledger": "USAGE_LOG.md",
            "cycle_id": _require_token(token_cycle_id, "token_cycle_id"),
            "role": _require_token(token_role, "token_role"),
        }
    return result


def start_trace(
    *,
    engine_root: Path | str,
    scope_root: Path | str,
    scope: str,
    scope_id: str,
    run_type: str,
    operation: str,
    clock: Clock | None = None,
    **metadata: Any,
) -> SpanHandle:
    current_clock = clock or SystemClock()
    engine = Path(engine_root).resolve()
    scope_path = Path(scope_root).resolve()
    scope_ledger_path(engine, scope_path, scope, scope_id)
    trace_id = uuid.uuid4().hex
    root_id = uuid.uuid4().hex
    _require_token(run_type, "run_type")
    _require_token(operation, "operation")
    projected_metadata = _metadata(**metadata)
    monotonic = current_clock.monotonic_ns()
    started = _utc_text(current_clock.utc_now())
    trace_dir = _trace_dir(engine, trace_id)
    trace = {
        "schema": RUNTIME_TRACE_SCHEMA,
        "trace_id": trace_id,
        "root_span_id": root_id,
        "engine_root": str(engine),
        "scope_root": str(scope_path),
        "scope": scope,
        "scope_id": scope_id,
        "run_type": run_type,
        "origin_monotonic_ns": monotonic,
        "boot_id": current_clock.boot_id(),
        "created_at": started,
    }
    root = {
        "schema": RUNTIME_SPAN_SCHEMA,
        "trace_id": trace_id,
        "span_id": root_id,
        "parent_span_id": None,
        "category": "run",
        "operation": operation,
        "attempt": 1,
        "started_at": started,
        "start_monotonic_ns": monotonic,
        "state": "open",
        **projected_metadata,
    }
    with _trace_lock(trace_dir):
        if (trace_dir / "trace.json").exists():
            raise TelemetryError("generated trace id already exists")
        _atomic_json(trace_dir / "trace.json", trace)
        _atomic_json(trace_dir / "spans" / f"{root_id}.json", root)
    return SpanHandle(trace_id, root_id)


def start_span(
    *,
    engine_root: Path | str,
    trace_id: str,
    parent_span_id: str,
    category: str,
    operation: str,
    attempt: int = 1,
    clock: Clock | None = None,
    **metadata: Any,
) -> SpanHandle:
    if category not in CATEGORIES or category == "run":
        raise ValidationError("child category must be intelligence, gate, reconciliation, or wait")
    _require_token(operation, "operation")
    _require_int(attempt, "attempt", minimum=1)
    current_clock = clock or SystemClock()
    trace_dir, _ = _load_runtime(engine_root, trace_id)
    span_id = uuid.uuid4().hex
    with _trace_lock(trace_dir):
        parent_path = trace_dir / "spans" / f"{_require_id(parent_span_id, 'parent_span_id')}.json"
        parent = _read_json(parent_path)
        if parent.get("state") != "open":
            raise IncompleteTraceError("new children require an open parent")
        record = {
            "schema": RUNTIME_SPAN_SCHEMA,
            "trace_id": trace_id,
            "span_id": span_id,
            "parent_span_id": parent_span_id,
            "category": category,
            "operation": operation,
            "attempt": attempt,
            "started_at": _utc_text(current_clock.utc_now()),
            "start_monotonic_ns": current_clock.monotonic_ns(),
            "state": "open",
            **_metadata(**metadata),
        }
        _atomic_json(trace_dir / "spans" / f"{span_id}.json", record)
    return SpanHandle(trace_id, span_id)


def attach_token_reference(
    *,
    engine_root: Path | str,
    trace_id: str,
    span_id: str,
    token_cycle_id: str,
    token_role: str,
) -> dict[str, Any]:
    """Attach an existing token-ledger identity without copying token data."""
    trace_dir, _ = _load_runtime(engine_root, trace_id)
    reference = _metadata(token_cycle_id=token_cycle_id, token_role=token_role)["token_reference"]
    with _trace_lock(trace_dir):
        if (trace_dir / "finalized.json").exists():
            raise ValidationError("cannot attach tokens to a finalized trace")
        span_path = trace_dir / "spans" / f"{_require_id(span_id, 'span_id')}.json"
        span = _read_json(span_path)
        if span.get("trace_id") != trace_id:
            raise ValidationError("span does not belong to trace")
        prior = span.get("token_reference")
        if prior is not None:
            if prior == reference:
                return span
            raise ValidationError("conflicting token reference")
        updated = dict(span)
        updated["token_reference"] = reference
        _atomic_json(span_path, updated)
        return updated


def attach_review_metrics(
    *,
    engine_root: Path | str,
    trace_id: str,
    span_id: str,
    findings_reported: int,
    actionable_findings: int,
) -> dict[str, Any]:
    """Attach validated review-convergence counts to one review intelligence span."""
    metrics = {
        "findings_reported": _require_int(findings_reported, "findings_reported", minimum=0),
        "actionable_findings": _require_int(actionable_findings, "actionable_findings", minimum=0),
    }
    trace_dir, _ = _load_runtime(engine_root, trace_id)
    with _trace_lock(trace_dir):
        if (trace_dir / "finalized.json").exists():
            raise ValidationError("cannot attach review metrics to a finalized trace")
        span_path = trace_dir / "spans" / f"{_require_id(span_id, 'span_id')}.json"
        span = _read_json(span_path)
        if span.get("trace_id") != trace_id:
            raise ValidationError("span does not belong to trace")
        expected_roles = {
            "role.plan-review": "reviewer",
            "role.code-review": "critic",
        }
        if (
            span.get("category") != "intelligence"
            or span.get("operation") not in expected_roles
            or span.get("role") != expected_roles[span["operation"]]
        ):
            raise ValidationError(
                "review metrics require a plan-review or code-review intelligence span"
            )
        prior = {
            key: span.get(key)
            for key in ("findings_reported", "actionable_findings")
            if key in span
        }
        if prior:
            if prior == metrics:
                return span
            raise ValidationError("conflicting review metrics")
        updated = dict(span) | metrics
        _atomic_json(span_path, updated)
        return updated


def _runtime_spans(trace_dir: Path) -> list[dict[str, Any]]:
    span_dir = trace_dir / "spans"
    try:
        paths = sorted(span_dir.glob("*.json"))
    except OSError as exc:
        raise TelemetryError("cannot enumerate runtime spans") from exc
    return [_read_json(item) for item in paths]


def finish_span(
    *,
    engine_root: Path | str,
    trace_id: str,
    span_id: str,
    outcome: str,
    exit_code: int | None = None,
    timeout_kind: str | None = None,
    timeout_ns: int | None = None,
    clock: Clock | None = None,
) -> dict[str, Any]:
    if outcome not in OUTCOMES:
        raise ValidationError("unknown outcome")
    current_clock = clock or SystemClock()
    trace_dir, trace = _load_runtime(engine_root, trace_id)
    if not same_boot(current_clock.boot_id(), trace["boot_id"]):
        raise ClockDomainError("trace belongs to a different monotonic clock domain")
    result = {"outcome": outcome}
    if exit_code is not None:
        result["exit_code"] = _require_int(exit_code, "exit_code", minimum=0)
    if timeout_kind is not None:
        result["timeout_kind"] = timeout_kind
    if timeout_ns is not None:
        result["timeout_ns"] = _require_int(timeout_ns, "timeout_ns", minimum=1)
    with _trace_lock(trace_dir):
        span_path = trace_dir / "spans" / f"{_require_id(span_id, 'span_id')}.json"
        span = _read_json(span_path)
        if span.get("state") == "closed":
            prior = {key: span[key] for key in result if key in span}
            prior_keys = {
                key for key in ("outcome", "exit_code", "timeout_kind", "timeout_ns") if key in span
            }
            if prior == result and prior_keys == set(result):
                return span
            raise ValidationError("conflicting repeated span finish")
        descendants = [
            item
            for item in _runtime_spans(trace_dir)
            if item.get("parent_span_id") == span_id and item.get("state") == "open"
        ]
        if descendants:
            raise IncompleteTraceError("cannot close a span with open descendants")
        end_monotonic = current_clock.monotonic_ns()
        if end_monotonic < span["start_monotonic_ns"]:
            raise ClockDomainError("monotonic clock moved backward")
        closed = dict(span)
        closed.update(result)
        closed.update(
            {
                "state": "closed",
                "ended_at": _utc_text(current_clock.utc_now()),
                "end_monotonic_ns": end_monotonic,
            }
        )
        projected = _project_span(closed, trace)
        validate_span(projected)
        _atomic_json(span_path, closed)
        return closed


def _project_span(span: Mapping[str, Any], trace: Mapping[str, Any]) -> dict[str, Any]:
    if span.get("state") != "closed":
        raise IncompleteTraceError("cannot project an open span")
    origin = _require_int(trace["origin_monotonic_ns"], "origin_monotonic_ns", minimum=0)
    start = _require_int(span["start_monotonic_ns"], "start_monotonic_ns", minimum=0)
    end = _require_int(span["end_monotonic_ns"], "end_monotonic_ns", minimum=0)
    projected: dict[str, Any] = {
        "schema": SPAN_SCHEMA,
        "trace_id": trace["trace_id"],
        "span_id": span["span_id"],
        "parent_span_id": span["parent_span_id"],
        "run_type": trace["run_type"],
        "scope": trace["scope"],
        "scope_id": trace["scope_id"],
        "category": span["category"],
        "operation": span["operation"],
        "attempt": span["attempt"],
        "started_at": span["started_at"],
        "ended_at": span["ended_at"],
        "start_offset_ns": start - origin,
        "end_offset_ns": end - origin,
        "duration_ns": end - start,
        "outcome": span["outcome"],
    }
    for key in (
        *_METADATA_KEYS,
        "findings_reported",
        "actionable_findings",
        "token_reference",
        "exit_code",
        "timeout_kind",
        "timeout_ns",
    ):
        if key in span:
            projected[key] = span[key]
    return projected


def _canonical(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def validate_ledger(ledger: Path | str) -> list[dict[str, Any]]:
    ledger_path = Path(ledger)
    try:
        raw = ledger_path.read_bytes()
    except OSError as exc:
        raise TelemetryError(f"cannot read ledger: {ledger_path}") from exc
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValidationError("execution ledger is not valid utf-8") from exc
    if raw and not raw.endswith(b"\n"):
        raise ValidationError("execution ledger has an unterminated final JSONL row")
    lines = text.splitlines()
    bundles: list[dict[str, Any]] = []
    seen: set[str] = set()
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
            bundle = validate_bundle(value)
        except (json.JSONDecodeError, ValidationError) as exc:
            raise ValidationError(f"invalid ledger row {number}: {exc}") from exc
        if bundle["trace_id"] in seen:
            raise ValidationError(f"duplicate trace_id in ledger row {number}")
        seen.add(bundle["trace_id"])
        bundles.append(bundle)
    return bundles


def validate_runtime_trace(*, engine_root: Path | str, trace_id: str) -> dict[str, Any]:
    """Validate runtime structure without closing or finalizing the trace."""
    try:
        trace_dir, trace = _load_runtime(engine_root, trace_id)
        required_trace = {
            "schema",
            "trace_id",
            "root_span_id",
            "engine_root",
            "scope_root",
            "scope",
            "scope_id",
            "run_type",
            "origin_monotonic_ns",
            "boot_id",
            "created_at",
        }
        if set(trace) != required_trace:
            raise ValidationError("runtime trace metadata has unknown or missing keys")
        root_span_id = _require_id(trace["root_span_id"], "root_span_id")
        _require_token(trace["run_type"], "run_type")
        _parse_utc(trace["created_at"], "created_at")
        origin = _require_int(trace["origin_monotonic_ns"], "origin_monotonic_ns", minimum=0)
        if not isinstance(trace["boot_id"], str) or not trace["boot_id"]:
            raise ValidationError("runtime boot_id must be a nonempty string")
        scope_ledger_path(
            trace["engine_root"], trace["scope_root"], trace["scope"], trace["scope_id"]
        )
        spans = _runtime_spans(trace_dir)
        if not spans:
            raise ValidationError("runtime trace has no spans")
        required_span = {
            "schema",
            "trace_id",
            "span_id",
            "parent_span_id",
            "category",
            "operation",
            "attempt",
            "started_at",
            "start_monotonic_ns",
            "state",
        }
        optional_span = set(_METADATA_KEYS) | {
            "findings_reported",
            "actionable_findings",
            "token_reference",
            "ended_at",
            "end_monotonic_ns",
            "outcome",
            "exit_code",
            "timeout_kind",
            "timeout_ns",
        }
        result_keys = {
            "ended_at",
            "end_monotonic_ns",
            "outcome",
            "exit_code",
            "timeout_kind",
            "timeout_ns",
        }
        by_id: dict[str, dict[str, Any]] = {}
        closed = 0
        for span in spans:
            if not required_span <= set(span) or set(span) - required_span - optional_span:
                raise ValidationError("runtime span has unknown or missing keys")
            if span["schema"] != RUNTIME_SPAN_SCHEMA or span["trace_id"] != trace_id:
                raise ValidationError("runtime span identity is invalid")
            span_id = _require_id(span["span_id"], "span_id")
            parent_id = span["parent_span_id"]
            if parent_id is not None:
                _require_id(parent_id, "parent_span_id")
            if span_id in by_id:
                raise ValidationError("runtime span ids must be unique")
            by_id[span_id] = span
            if span["category"] not in CATEGORIES:
                raise ValidationError("runtime span category is invalid")
            if parent_id is not None and span["category"] == "run":
                raise ValidationError("runtime ancestry reserves category run for the root")
            _require_token(span["operation"], "operation")
            _require_int(span["attempt"], "attempt", minimum=1)
            _parse_utc(span["started_at"], "started_at")
            started = _require_int(span["start_monotonic_ns"], "start_monotonic_ns", minimum=0)
            if started < origin:
                raise ValidationError("runtime span starts before the trace origin")
            for key in _METADATA_KEYS:
                if key in span:
                    _require_token(span[key], key)
            for key in ("findings_reported", "actionable_findings"):
                if key in span:
                    _require_int(span[key], key, minimum=0)
            if "token_reference" in span:
                _validate_token_reference(span["token_reference"])
            if span["state"] not in {"open", "closed"}:
                raise ValidationError("runtime span state is invalid")
            present_results = set(span) & result_keys
            if span["state"] == "closed":
                if not {"ended_at", "end_monotonic_ns", "outcome"} <= present_results:
                    raise ValidationError("closed runtime span is missing result fields")
                validate_span(_project_span(span, trace))
                closed += 1
            elif present_results:
                raise ValidationError("open runtime span carries result fields")
        roots = [span for span in spans if span["parent_span_id"] is None]
        if len(roots) != 1 or roots[0]["span_id"] != root_span_id or roots[0]["category"] != "run":
            raise ValidationError("runtime trace ancestry must contain exactly one run root")
        if roots[0]["start_monotonic_ns"] != origin:
            raise ValidationError("runtime root must start at the trace origin")
        for span in spans:
            parent_id = span["parent_span_id"]
            if parent_id is None:
                continue
            parent = by_id.get(parent_id)
            if parent is None:
                raise ValidationError("runtime span parent is missing")
            seen = {span["span_id"]}
            cursor = parent
            while True:
                if cursor["span_id"] in seen:
                    raise ValidationError("runtime span ancestry contains a cycle")
                seen.add(cursor["span_id"])
                if cursor["parent_span_id"] is None:
                    if cursor["span_id"] != root_span_id:
                        raise ValidationError("runtime ancestry does not reach the root")
                    break
                next_parent = by_id.get(cursor["parent_span_id"])
                if next_parent is None:
                    raise ValidationError("runtime span ancestry is incomplete")
                cursor = next_parent
            if parent["state"] == "closed" and span["state"] == "open":
                raise ValidationError("closed runtime parent has an open child")
            if parent["state"] == "closed" and span["state"] == "closed":
                if (
                    span["start_monotonic_ns"] < parent["start_monotonic_ns"]
                    or span["end_monotonic_ns"] > parent["end_monotonic_ns"]
                ):
                    raise ValidationError("closed runtime child interval is outside its parent")
        return {
            "trace_id": trace_id,
            "valid": True,
            "span_count": len(spans),
            "open_span_count": len(spans) - closed,
        }
    except (KeyError, TypeError, ValueError) as exc:
        raise ValidationError("runtime trace contains malformed values") from exc


def trace_context(*, engine_root: Path | str, trace_id: str) -> dict[str, Any]:
    """Return the validated, non-sensitive identity of one runtime trace."""
    validate_runtime_trace(engine_root=engine_root, trace_id=trace_id)
    _, trace = _load_runtime(engine_root, trace_id)
    root = next(
        item
        for item in _runtime_spans(_trace_dir(engine_root, trace_id))
        if item["span_id"] == trace["root_span_id"]
    )
    return {
        "trace_id": trace["trace_id"],
        "root_span_id": trace["root_span_id"],
        "scope": trace["scope"],
        "scope_id": trace["scope_id"],
        "run_type": trace["run_type"],
        "operation": root["operation"],
        "state": root["state"],
    }


def runtime_span_context(*, engine_root: Path | str, trace_id: str, span_id: str) -> dict[str, Any]:
    """Return one runtime span's allowlisted identity, including open state."""
    validate_runtime_trace(engine_root=engine_root, trace_id=trace_id)
    _, trace = _load_runtime(engine_root, trace_id)
    span = next(
        (
            item
            for item in _runtime_spans(_trace_dir(engine_root, trace_id))
            if item["span_id"] == _require_id(span_id, "span_id")
        ),
        None,
    )
    if span is None:
        raise ValidationError("span_id does not identify a runtime span")
    return {
        "trace_id": trace_id,
        "span_id": span_id,
        "parent_span_id": span["parent_span_id"],
        "scope": trace["scope"],
        "scope_id": trace["scope_id"],
        "run_type": trace["run_type"],
        "category": span["category"],
        "operation": span["operation"],
        "attempt": span["attempt"],
        "state": span["state"],
        **{key: span[key] for key in _METADATA_KEYS if key in span},
    }


def closed_span(*, engine_root: Path | str, trace_id: str, span_id: str) -> dict[str, Any]:
    """Return the durable projection of one validated closed runtime span."""
    validate_runtime_trace(engine_root=engine_root, trace_id=trace_id)
    trace_dir, trace = _load_runtime(engine_root, trace_id)
    for span in _runtime_spans(trace_dir):
        if span["span_id"] == _require_id(span_id, "span_id"):
            if span.get("state") != "closed":
                raise IncompleteTraceError("selected span is still open")
            return validate_span(_project_span(span, trace))
    raise ValidationError("span_id does not identify a runtime span")


def closed_spans(*, engine_root: Path | str, trace_id: str) -> list[dict[str, Any]]:
    """Return durable projections for every currently closed runtime span."""
    validate_runtime_trace(engine_root=engine_root, trace_id=trace_id)
    trace_dir, trace = _load_runtime(engine_root, trace_id)
    return sorted(
        (
            validate_span(_project_span(span, trace))
            for span in _runtime_spans(trace_dir)
            if span["state"] == "closed"
        ),
        key=lambda item: (item["start_offset_ns"], item["span_id"]),
    )


def finalized_trace(*, engine_root: Path | str, trace_id: str) -> dict[str, Any]:
    """Read one finalized trace after reconciling its marker and owned ledger."""
    trace_dir, trace = _load_runtime(engine_root, trace_id)
    marker = _read_json(trace_dir / "finalized.json")
    _require_exact_keys(marker, frozenset({"schema", "bundle"}), frozenset(), "finalized marker")
    if marker["schema"] != "agentic_starter.execution_finalized.runtime.v1":
        raise ValidationError("finalized marker schema is invalid")
    bundle = validate_bundle(marker["bundle"])
    ledger = scope_ledger_path(
        trace["engine_root"], trace["scope_root"], trace["scope"], trace["scope_id"]
    )
    matches = [item for item in validate_ledger(ledger) if item["trace_id"] == trace_id]
    if len(matches) != 1 or matches[0] != bundle:
        raise ValidationError("finalized marker and execution ledger do not agree")
    return bundle


def finalize_trace(
    *, engine_root: Path | str, trace_id: str, clock: Clock | None = None
) -> dict[str, Any]:
    current_clock = clock or SystemClock()
    trace_dir, trace = _load_runtime(engine_root, trace_id)
    with _trace_lock(trace_dir):
        spans = _runtime_spans(trace_dir)
        if any(item.get("state") != "closed" for item in spans):
            raise IncompleteTraceError("all spans must be closed before finalization")
        projected = sorted(
            (_project_span(item, trace) for item in spans),
            key=lambda item: (item["start_offset_ns"], item["span_id"]),
        )
        bundle = {
            "schema": TRACE_SCHEMA,
            "trace_id": trace_id,
            "finalized_at": _utc_text(current_clock.utc_now()),
            "scope": trace["scope"],
            "scope_id": trace["scope_id"],
            "root_span_id": trace["root_span_id"],
            "spans": projected,
        }
        marker_path = trace_dir / "finalized.json"
        if marker_path.exists():
            marker = _read_json(marker_path)
            _require_exact_keys(
                marker,
                frozenset({"schema", "bundle"}),
                frozenset(),
                "finalized marker",
            )
            if marker["schema"] != "agentic_starter.execution_finalized.runtime.v1":
                raise ValidationError("finalized marker schema is invalid")
            marker_bundle = validate_bundle(marker["bundle"])
            candidate = dict(bundle)
            candidate["finalized_at"] = marker_bundle["finalized_at"]
            if candidate != marker_bundle:
                raise ValidationError("finalized marker conflicts with runtime trace")
            bundle = marker_bundle
        validate_bundle(bundle)
        ledger = scope_ledger_path(
            trace["engine_root"], trace["scope_root"], trace["scope"], trace["scope_id"]
        )
        try:
            ledger.parent.mkdir(parents=True, exist_ok=True)
            with ledger.open("a+b") as stream:
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
                try:
                    stream.seek(0)
                    raw_ledger = stream.read()
                    try:
                        ledger_text = raw_ledger.decode("utf-8")
                    except UnicodeDecodeError as exc:
                        raise ValidationError("execution ledger is not valid utf-8") from exc
                    if raw_ledger and not raw_ledger.endswith(b"\n"):
                        raise ValidationError(
                            "execution ledger has an unterminated final JSONL row"
                        )
                    existing_lines = ledger_text.splitlines()
                    existing: dict[str, Any] | None = None
                    seen_trace_ids: set[str] = set()
                    for number, line in enumerate(existing_lines, 1):
                        if not line.strip():
                            continue
                        try:
                            row = validate_bundle(json.loads(line))
                        except (json.JSONDecodeError, ValidationError) as exc:
                            raise ValidationError(f"invalid ledger row {number}: {exc}") from exc
                        if row["trace_id"] in seen_trace_ids:
                            raise ValidationError("ledger contains duplicate trace ids")
                        seen_trace_ids.add(row["trace_id"])
                        if row["trace_id"] == trace_id:
                            existing = row
                    if existing is not None:
                        candidate = dict(bundle)
                        candidate["finalized_at"] = existing["finalized_at"]
                        if candidate != existing:
                            raise ValidationError("ledger contains a conflicting trace id")
                        bundle = existing
                    else:
                        stream.seek(0, os.SEEK_END)
                        stream.write((_canonical(bundle) + "\n").encode("utf-8"))
                        stream.flush()
                        os.fsync(stream.fileno())
                    _fsync_directory(ledger.parent)
                finally:
                    fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
        except OSError as exc:
            raise TelemetryError("cannot append execution ledger") from exc
        _atomic_json(
            marker_path,
            {"schema": "agentic_starter.execution_finalized.runtime.v1", "bundle": bundle},
        )
        return bundle


def recover_trace(
    *, engine_root: Path | str, trace_id: str, clock: Clock | None = None
) -> dict[str, Any]:
    current_clock = clock or SystemClock()
    trace_dir, trace = _load_runtime(engine_root, trace_id)
    validate_runtime_trace(engine_root=engine_root, trace_id=trace_id)
    sampled_boot_id = current_clock.boot_id()
    if not same_boot(sampled_boot_id, trace["boot_id"]):
        raise ClockDomainError("cannot recover a trace from a different boot")

    @dataclasses.dataclass(frozen=True)
    class RecoveryClock:
        sampled_utc: dt.datetime
        sampled_monotonic_ns: int
        sampled_boot_id: str

        def utc_now(self) -> dt.datetime:
            return self.sampled_utc

        def monotonic_ns(self) -> int:
            return self.sampled_monotonic_ns

        def boot_id(self) -> str:
            return self.sampled_boot_id

    recovery_clock: Clock = RecoveryClock(
        current_clock.utc_now(), current_clock.monotonic_ns(), sampled_boot_id
    )
    while True:
        spans = _runtime_spans(trace_dir)
        open_spans = [item for item in spans if item.get("state") == "open"]
        if not open_spans:
            break
        parents = {item.get("parent_span_id") for item in open_spans}
        leaves = [item for item in open_spans if item["span_id"] not in parents]
        if not leaves:
            raise IncompleteTraceError(
                "runtime span graph made no recovery progress; spool retained"
            )
        for span in sorted(leaves, key=lambda item: item["span_id"]):
            finish_span(
                engine_root=engine_root,
                trace_id=trace_id,
                span_id=span["span_id"],
                outcome="interrupted",
                clock=recovery_clock,
            )
    return finalize_trace(engine_root=engine_root, trace_id=trace_id, clock=recovery_clock)


def _process_group_exists(group_id: int) -> bool:
    try:
        os.killpg(group_id, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _wait_for_group_exit(group_id: int, timeout_seconds: float) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while _process_group_exists(group_id):
        if time.monotonic() >= deadline:
            return False
        time.sleep(0.02)
    return True


def _signal_process_group(process: subprocess.Popen[Any], group_id: int, signum: int) -> None:
    try:
        os.killpg(group_id, signum)
    except ProcessLookupError:
        return
    except PermissionError:
        if process.poll() is None:
            if signum == signal.SIGTERM:
                process.terminate()
            else:
                process.kill()


def _terminate_group(process: subprocess.Popen[Any]) -> None:
    group_id = process.pid
    _signal_process_group(process, group_id, signal.SIGTERM)
    if process.poll() is None:
        with contextlib.suppress(subprocess.TimeoutExpired):
            process.wait(timeout=0.1)
    if not _wait_for_group_exit(group_id, 2):
        _signal_process_group(process, group_id, signal.SIGKILL)
        _wait_for_group_exit(group_id, 2)
    if process.poll() is None:
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def run_observed(
    *,
    engine_root: Path | str,
    trace_id: str,
    parent_span_id: str,
    category: str,
    operation: str,
    argv: Sequence[str],
    attempt: int = 1,
    timeout_seconds: float | None = None,
    clock: Clock | None = None,
    **metadata: Any,
) -> ObservedResult:
    if not argv:
        raise ValidationError("observed command must not be empty")
    if threading.current_thread() is not threading.main_thread():
        raise ValidationError("run_observed must be called from the main thread")
    timeout_ns: int | None = None
    if timeout_seconds is not None:
        timeout_ns = _timeout_nanoseconds(timeout_seconds)
    current_clock = clock or SystemClock()
    handle: SpanHandle | None = None
    telemetry_complete = True
    error_code: str | None = None
    try:
        handle = start_span(
            engine_root=engine_root,
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            category=category,
            operation=operation,
            attempt=attempt,
            clock=current_clock,
            **metadata,
        )
    except TelemetryError:
        telemetry_complete = False
        error_code = "span-start-failed"
    process: subprocess.Popen[Any] | None = None
    normalized_exit = 127
    outcome = "error"
    cancelled_signal: int | None = None
    old_handlers: dict[int, Any] = {}

    def cancel_handler(signum: int, _frame: Any) -> None:
        nonlocal cancelled_signal
        cancelled_signal = signum

    try:
        for signum in (signal.SIGINT, signal.SIGTERM):
            old_handlers[signum] = signal.getsignal(signum)
            signal.signal(signum, cancel_handler)
        child_environment = os.environ.copy()
        context_keys = (
            "AGENTIC_STARTER_EXECUTION_ENGINE_ROOT",
            "AGENTIC_STARTER_EXECUTION_TRACE_ID",
            "AGENTIC_STARTER_EXECUTION_PARENT_SPAN_ID",
        )
        for key in context_keys:
            child_environment.pop(key, None)
        if handle is not None:
            child_environment.update(
                {
                    "AGENTIC_STARTER_EXECUTION_ENGINE_ROOT": str(Path(engine_root).resolve()),
                    "AGENTIC_STARTER_EXECUTION_TRACE_ID": trace_id,
                    "AGENTIC_STARTER_EXECUTION_PARENT_SPAN_ID": handle.span_id,
                }
            )
        try:
            process = subprocess.Popen(list(argv), start_new_session=True, env=child_environment)
        except OSError:
            process = None
        if process is not None:
            deadline = (
                time.monotonic() + (timeout_ns / 1_000_000_000) if timeout_ns is not None else None
            )
            while True:
                if cancelled_signal is not None:
                    _terminate_group(process)
                    normalized_exit = 128 + cancelled_signal
                    outcome = "cancelled"
                    break
                remaining = None if deadline is None else deadline - time.monotonic()
                if remaining is not None and remaining <= 0:
                    _terminate_group(process)
                    normalized_exit = 124
                    outcome = "timeout"
                    break
                if cancelled_signal is not None:
                    continue
                wait_slice = 0.1 if remaining is None else min(0.1, remaining)
                try:
                    child_exit = process.wait(timeout=wait_slice)
                except subprocess.TimeoutExpired:
                    continue
                if child_exit < 0:
                    normalized_exit = 128 + abs(child_exit)
                    outcome = "interrupted"
                else:
                    normalized_exit = child_exit
                    outcome = "success" if child_exit == 0 else "error"
                break
    finally:
        for signum, handler in old_handlers.items():
            signal.signal(signum, handler)
    if handle is not None:
        finish_kwargs: dict[str, Any] = {
            "engine_root": engine_root,
            "trace_id": trace_id,
            "span_id": handle.span_id,
            "outcome": outcome,
            "exit_code": normalized_exit,
            "clock": current_clock,
        }
        if outcome == "timeout":
            finish_kwargs["timeout_kind"] = "command"
            finish_kwargs["timeout_ns"] = timeout_ns
        try:
            finish_span(**finish_kwargs)
        except TelemetryError:
            telemetry_complete = False
            error_code = "span-finish-failed"
    return ObservedResult(
        trace_id=trace_id,
        span_id=handle.span_id if handle else None,
        exit_code=normalized_exit,
        outcome=outcome,
        telemetry_complete=telemetry_complete,
        error_code=error_code,
    )


def _interval_union(intervals: Sequence[tuple[int, int]]) -> int:
    if not intervals:
        return 0
    total = 0
    start, end = sorted(intervals)[0]
    for next_start, next_end in sorted(intervals)[1:]:
        if next_start <= end:
            end = max(end, next_end)
        else:
            total += end - start
            start, end = next_start, next_end
    return total + end - start


def _peak_concurrency(intervals: Sequence[tuple[int, int]]) -> int:
    events: list[tuple[int, int]] = []
    for start, end in intervals:
        events.extend(((start, 1), (end, -1)))
    active = 0
    peak = 0
    for _, delta in sorted(events, key=lambda item: (item[0], item[1])):
        active += delta
        peak = max(peak, active)
    return peak


def format_elapsed(duration_ns: int) -> str:
    """Render an exact monotonic duration in a compact deterministic form."""
    value = _require_int(duration_ns, "duration_ns", minimum=0)
    milliseconds = value // 1_000_000
    if milliseconds < 60_000:
        return f"{milliseconds // 1000}.{milliseconds % 1000:03d}s"
    seconds = milliseconds // 1000
    minutes, second = divmod(seconds, 60)
    hours, minute = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minute}m {second}s"
    return f"{minute}m {second}s"


def _batch_metrics(root: Mapping[str, Any], children: list[dict[str, Any]]) -> dict[str, Any]:
    member_re = re.compile(r"^role\.cycle\.([0-9a-f]{8})$")
    members = [
        item
        for item in children
        if item["category"] == "intelligence" and member_re.fullmatch(item["operation"])
    ]
    member_by_cycle: dict[str, list[dict[str, Any]]] = {}
    for item in members:
        cycle_id = member_re.fullmatch(item["operation"]).group(1)  # type: ignore[union-attr]
        member_by_cycle.setdefault(cycle_id, []).append(item)
    committed = {
        item["operation"].removeprefix("batch.commit.")
        for item in children
        if item["operation"].startswith("batch.commit.") and item["outcome"] == "success"
    }
    quarantined = {
        item["operation"].removeprefix("batch.quarantine.")
        for item in children
        if item["operation"].startswith("batch.quarantine.")
    }
    incomplete = {
        item["operation"].removeprefix("batch.telemetry-incomplete.")
        for item in children
        if item["operation"].startswith("batch.telemetry-incomplete.")
    }
    member_intervals = [(item["start_offset_ns"], item["end_offset_ns"]) for item in members]
    summed = sum(item["duration_ns"] for item in members)
    committed_work = sum(
        item["duration_ns"]
        for cycle_id, attempts in member_by_cycle.items()
        if cycle_id in committed
        for item in attempts
    )
    active_union = _interval_union(member_intervals)
    member_window = (
        max(end for _, end in member_intervals) - min(start for start, _ in member_intervals)
        if member_intervals
        else 0
    )
    committed_count = len(committed)
    makespan = root["duration_ns"]
    return {
        "batch_makespan_ns": makespan,
        "launched_members": len(member_by_cycle),
        "committed_members": committed_count,
        "quarantined_members": len(quarantined),
        "failed_members": sum(
            1
            for attempts in member_by_cycle.values()
            if all(item["outcome"] != "success" for item in attempts)
        ),
        "retried_members": sum(
            1
            for attempts in member_by_cycle.values()
            if len(attempts) > 1 or any(item["attempt"] > 1 for item in attempts)
        ),
        "telemetry_incomplete_members": len(incomplete),
        "summed_member_work_ns": summed,
        "committed_member_work_ns": committed_work,
        "wall_clock_per_committed_work_unit_ns": (
            makespan // committed_count if committed_count else None
        ),
        "wall_clock_per_committed_work_unit_reason": (
            None if committed_count else "no committed members"
        ),
        "member_active_union_ns": active_union,
        "member_window_ns": member_window,
        "overlap_ns": summed - active_union,
        "peak_concurrency": _peak_concurrency(member_intervals),
        "member_work_to_window_ratio": (summed / member_window if member_window else None),
        "observed_parallel_speedup": (committed_work / makespan if makespan else None),
        "observed_parallel_speedup_reason": (None if makespan else "zero batch makespan"),
    }


def aggregate_trace(bundle: Mapping[str, Any]) -> dict[str, Any]:
    valid = validate_bundle(bundle)
    spans = valid["spans"]
    root = next(item for item in spans if item["span_id"] == valid["root_span_id"])
    children = [item for item in spans if item["span_id"] != valid["root_span_id"]]

    def intervals(items: Sequence[Mapping[str, Any]]) -> list[tuple[int, int]]:
        return [(item["start_offset_ns"], item["end_offset_ns"]) for item in items]

    makespan = root["duration_ns"]
    covered = _interval_union(intervals(children))
    # Attribute each covered instant to exactly one deepest material span.
    # This makes category totals exclusive even when a gate is nested below an
    # intelligence attempt or independent siblings overlap.
    by_id = {item["span_id"]: item for item in spans}

    def depth(item: Mapping[str, Any]) -> int:
        value = 0
        parent = item.get("parent_span_id")
        while parent is not None:
            value += 1
            parent = by_id[parent].get("parent_span_id")
        return value

    category_totals = {category: 0 for category in sorted(CATEGORIES - {"run"})}
    boundaries = sorted(
        {point for item in children for point in (item["start_offset_ns"], item["end_offset_ns"])}
    )
    for start, end in zip(boundaries, boundaries[1:]):
        active = [
            item
            for item in children
            if item["start_offset_ns"] <= start and item["end_offset_ns"] >= end
        ]
        if not active or end <= start:
            continue
        winner = max(
            active,
            key=lambda item: (
                depth(item),
                -item["duration_ns"],
                item["span_id"],
            ),
        )
        category_totals[winner["category"]] += end - start
    categories = category_totals
    failures = [item for item in children if item["outcome"] != "success"]
    retries = [item for item in children if item["attempt"] > 1]
    groups: dict[str, Any] = {}
    group_names = sorted(
        {item["concurrency_group"] for item in children if "concurrency_group" in item}
    )
    for name in group_names:
        members = [item for item in children if item.get("concurrency_group") == name]
        group_intervals = intervals(members)
        summed = sum(item["duration_ns"] for item in members)
        window = max(end for _, end in group_intervals) - min(start for start, _ in group_intervals)
        active = _interval_union(group_intervals)
        groups[name] = {
            "member_count": len(members),
            "summed_work_ns": summed,
            "enclosing_window_ns": window,
            "active_union_ns": active,
            "overlap_ns": summed - active,
            "peak_concurrency": _peak_concurrency(group_intervals),
            "work_to_window_ratio": summed / window if window else 0.0,
        }
    token_groups: dict[tuple[str, str, str], list[str]] = {}
    for item in spans:
        if "token_reference" not in item:
            continue
        reference = item["token_reference"]
        key = (reference["ledger"], reference["cycle_id"], reference["role"])
        token_groups.setdefault(key, []).append(item["span_id"])
    token_refs = [
        {
            "ledger": key[0],
            "cycle_id": key[1],
            "role": key[2],
            "span_ids": sorted(span_ids),
        }
        for key, span_ids in sorted(token_groups.items())
    ]
    result = {
        "trace_id": valid["trace_id"],
        "finalized_at": valid["finalized_at"],
        "scope": valid["scope"],
        "scope_id": valid["scope_id"],
        "run_type": root["run_type"],
        "root_operation": root["operation"],
        "batch_id": root.get("batch_id"),
        "root_makespan_ns": makespan,
        "category_coverage_ns": categories,
        "non_root_coverage_ns": covered,
        "unattributed_ns": max(0, makespan - covered),
        "failed_coverage_ns": _interval_union(intervals(failures)),
        "retry_coverage_ns": _interval_union(intervals(retries)),
        "slowest_spans": [
            {
                "span_id": item["span_id"],
                "operation": item["operation"],
                "category": item["category"],
                "duration_ns": item["duration_ns"],
                "outcome": item["outcome"],
            }
            for item in sorted(children, key=lambda row: (-row["duration_ns"], row["span_id"]))[:10]
        ],
        "token_references": token_refs,
        "concurrency_groups": groups,
    }
    if root["run_type"] == "improve-batch":
        result["batch_metrics"] = _batch_metrics(root, children)
    if root["run_type"] == "checkpoint":
        result["checkpoint_child_cycles"] = sorted(
            {
                item["operation"].removeprefix("checkpoint.cycle.")
                for item in children
                if item["operation"].startswith("checkpoint.cycle.")
            }
        )
    return result


def report_history(
    ledger: Path | str,
    *,
    trace_id: str | None = None,
    run_type: str | None = None,
    batch_id: str | None = None,
    phase_id: str | None = None,
    since: str | None = None,
    recent: int | None = None,
) -> list[dict[str, Any]]:
    if trace_id is not None:
        _require_id(trace_id, "trace_id")
    if run_type is not None:
        _require_token(run_type, "run_type")
    if batch_id is not None:
        _require_token(batch_id, "batch_id")
    if phase_id is not None:
        if not _PHASE_RE.fullmatch(phase_id):
            raise ValidationError("phase_id must be a dotted numeric phase id")
        if run_type not in {None, "kickoff"}:
            raise ValidationError("phase_id requires kickoff run_type")
        if batch_id is not None:
            raise ValidationError("phase_id cannot be combined with batch_id")
    since_value = _parse_utc(since, "since") if since is not None else None
    if recent is not None:
        _require_int(recent, "recent", minimum=1)
    bundles = validate_ledger(ledger)
    selected = []
    for bundle in bundles:
        root = next(item for item in bundle["spans"] if item["span_id"] == bundle["root_span_id"])
        if trace_id is not None and bundle["trace_id"] != trace_id:
            continue
        if run_type is not None and root["run_type"] != run_type:
            continue
        if phase_id is not None and (
            root["run_type"] != "kickoff" or root["operation"] != f"phase.{phase_id}"
        ):
            continue
        if (
            since_value is not None
            and _parse_utc(bundle["finalized_at"], "finalized_at") < since_value
        ):
            continue
        if batch_id is not None and not any(
            item.get("batch_id") == batch_id for item in bundle["spans"]
        ):
            continue
        selected.append(bundle)
    selected.sort(key=lambda item: (item["finalized_at"], item["trace_id"]))
    if recent is not None:
        selected = selected[-recent:]
    return [aggregate_trace(item) for item in selected]


def format_text_report(reports: Sequence[Mapping[str, Any]] | Mapping[str, Any]) -> str:
    if isinstance(reports, Mapping):
        lines = []
        diagnostics = reports.get("ledger_diagnostics", [])
        for item in diagnostics:
            lines.append(f"Ledger {item['scope']}:{item['scope_id']}: {item['state']}")
        incomplete = reports.get("incomplete_runs", [])
        for item in incomplete:
            lines.append(
                f"Incomplete {item['run_type']} {item['scope']}:{item['scope_id']}: "
                f"{item['lifecycle_state']} ({item.get('error_code') or 'unknown'})"
            )
        for link in reports.get("checkpoint_links", []):
            lines.append(
                f"Checkpoint {link['checkpoint_id']}: outer "
                f"{link['outer_makespan_ns']} ns; child work "
                f"{link['summed_child_work_ns']} ns; "
                f"missing children={','.join(link['missing_child_cycles']) or 'none'}"
            )
        rendered = format_text_report(reports.get("reports", []))
        return ("\n".join(lines) + ("\n" if lines else "")) + rendered
    if not reports:
        return "No matching execution traces.\n"
    lines: list[str] = []
    for report in reports:
        lines.extend(
            [
                f"Trace {report['trace_id']} ({report['run_type']}, "
                f"{report['scope']}:{report['scope_id']})",
                f"  Root makespan: {report['root_makespan_ns']} ns",
                f"  Non-root covered time: {report['non_root_coverage_ns']} ns",
                f"  Unattributed time: {report['unattributed_ns']} ns",
                f"  Failed/retried time: {report['failed_coverage_ns']} / "
                f"{report['retry_coverage_ns']} ns",
                "  Category coverage:",
            ]
        )
        for category, duration in report["category_coverage_ns"].items():
            lines.append(f"    {category}: {duration} ns")
        if "managed_run" in report:
            managed = report["managed_run"]
            lines.append(
                f"  Managed lifecycle: {managed['lifecycle_state']} "
                f"({managed.get('error_code') or 'recoverable'})"
            )
        if report["concurrency_groups"]:
            lines.append("  Concurrency groups:")
            for name, group in report["concurrency_groups"].items():
                lines.append(
                    f"    {name}: {group['member_count']} members, "
                    f"{group['summed_work_ns']} ns summed work, "
                    f"{group['enclosing_window_ns']} ns window, "
                    f"{group['overlap_ns']} ns overlap, "
                    f"peak {group['peak_concurrency']}"
                )
        if "batch_metrics" in report:
            metrics = report["batch_metrics"]
            lines.append("  Batch metrics:")
            for key, value in metrics.items():
                lines.append(f"    {key}: {value}")
        if report["token_references"]:
            lines.append("  Token references:")
            for reference in report["token_references"]:
                lines.append(
                    f"    {','.join(reference['span_ids'])}: {reference['ledger']} "
                    f"cycle={reference['cycle_id']} role={reference['role']}"
                )
        if report["slowest_spans"]:
            lines.append("  Slowest spans:")
            for span in report["slowest_spans"]:
                lines.append(
                    f"    {span['operation']} [{span['category']}]: "
                    f"{span['duration_ns']} ns ({span['outcome']})"
                )
    return "\n".join(lines) + "\n"


def _managed_runs_dir(engine_root: Path | str) -> Path:
    return telemetry_state_root() / repo_key(engine_root) / "managed-runs"


def _validate_managed_run(value: Mapping[str, Any]) -> dict[str, Any]:
    required = frozenset(
        {
            "schema",
            "run_id",
            "cycle_id",
            "scope",
            "scope_id",
            "run_type",
            "operation",
            "batch_id",
            "created_at",
            "updated_at",
            "trace_id",
            "root_span_id",
            "lifecycle_state",
            "error_code",
            "persistence_state",
        }
    )
    _require_exact_keys(value, required, frozenset(), "managed run")
    if value["schema"] != MANAGED_RUN_SCHEMA:
        raise ValidationError("managed run schema is invalid")
    _require_id(value["run_id"], "run_id")
    if value["cycle_id"] is not None and not _CYCLE_RE.fullmatch(value["cycle_id"]):
        raise ValidationError("managed run cycle_id must be 8 lowercase hex characters")
    if value["scope"] not in SCOPES:
        raise ValidationError("managed run scope is invalid")
    _require_token(value["scope_id"], "scope_id")
    _require_token(value["run_type"], "run_type")
    _require_token(value["operation"], "operation")
    if value["batch_id"] is not None:
        _require_token(value["batch_id"], "batch_id")
    _parse_utc(value["created_at"], "created_at")
    _parse_utc(value["updated_at"], "updated_at")
    for field in ("trace_id", "root_span_id"):
        if value[field] is not None:
            _require_id(value[field], field)
    if value["lifecycle_state"] not in {
        "expected",
        "trace-bound",
        "finalized",
        "persisted",
        "incomplete",
    }:
        raise ValidationError("managed run lifecycle_state is invalid")
    if value["error_code"] is not None:
        _require_token(value["error_code"], "error_code")
    if value["persistence_state"] not in {
        "pending",
        "finalized",
        "persisted",
        "incomplete",
    }:
        raise ValidationError("managed run persistence_state is invalid")
    return dict(value)


def _managed_run_path(engine_root: Path | str, run_id: str) -> Path:
    return _managed_runs_dir(engine_root) / f"{_require_id(run_id, 'run_id')}.json"


def _update_managed_run(
    engine_root: Path | str, run_id: str, changes: Mapping[str, Any]
) -> dict[str, Any]:
    directory = _managed_runs_dir(engine_root)
    with _trace_lock(directory):
        file_path = _managed_run_path(engine_root, run_id)
        record = _validate_managed_run(_read_json(file_path))
        updated = record | dict(changes) | {"updated_at": _utc_text(SystemClock().utc_now())}
        _validate_managed_run(updated)
        _atomic_json(file_path, updated)
        return updated


def expect_managed_run(
    *,
    engine_root: Path | str,
    scope: str,
    scope_id: str,
    run_type: str,
    operation: str,
    cycle_id: str | None = None,
    batch_id: str | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Create the bounded pre-trace expectation for one managed run."""
    identity = run_id or uuid.uuid4().hex
    now = _utc_text(SystemClock().utc_now())
    record = {
        "schema": MANAGED_RUN_SCHEMA,
        "run_id": identity,
        "cycle_id": cycle_id,
        "scope": scope,
        "scope_id": scope_id,
        "run_type": run_type,
        "operation": operation,
        "batch_id": batch_id,
        "created_at": now,
        "updated_at": now,
        "trace_id": None,
        "root_span_id": None,
        "lifecycle_state": "expected",
        "error_code": None,
        "persistence_state": "pending",
    }
    _validate_managed_run(record)
    directory = _managed_runs_dir(engine_root)
    with _trace_lock(directory):
        file_path = _managed_run_path(engine_root, identity)
        if file_path.exists():
            prior = _validate_managed_run(_read_json(file_path))
            candidate = dict(record)
            candidate["created_at"] = prior["created_at"]
            candidate["updated_at"] = prior["updated_at"]
            if candidate != prior:
                raise ValidationError("managed run id already has different identity")
            return prior
        _atomic_json(file_path, record)
    return record


def bind_expected_trace(
    *, engine_root: Path | str, run_id: str, trace_id: str, root_span_id: str
) -> dict[str, Any]:
    return _update_managed_run(
        engine_root,
        run_id,
        {
            "trace_id": _require_id(trace_id, "trace_id"),
            "root_span_id": _require_id(root_span_id, "root_span_id"),
            "lifecycle_state": "trace-bound",
            "error_code": None,
        },
    )


def mark_expected_finalized(*, engine_root: Path | str, run_id: str) -> dict[str, Any]:
    prior = _validate_managed_run(
        _read_json(_managed_run_path(engine_root, _require_id(run_id, "run_id")))
    )
    if prior["lifecycle_state"] == "incomplete":
        return _update_managed_run(
            engine_root,
            run_id,
            {"persistence_state": "finalized"},
        )
    return _update_managed_run(
        engine_root,
        run_id,
        {"lifecycle_state": "finalized", "persistence_state": "finalized", "error_code": None},
    )


def mark_expected_persisted(*, engine_root: Path | str, run_id: str) -> dict[str, Any]:
    prior = _validate_managed_run(
        _read_json(_managed_run_path(engine_root, _require_id(run_id, "run_id")))
    )
    if prior["lifecycle_state"] == "incomplete":
        return _update_managed_run(
            engine_root,
            run_id,
            {"persistence_state": "persisted"},
        )
    return _update_managed_run(
        engine_root,
        run_id,
        {"lifecycle_state": "persisted", "persistence_state": "persisted", "error_code": None},
    )


def mark_expected_incomplete(
    *, engine_root: Path | str, run_id: str, error_code: str
) -> dict[str, Any]:
    _require_token(error_code, "error_code")
    return _update_managed_run(
        engine_root,
        run_id,
        {
            "lifecycle_state": "incomplete",
            "persistence_state": "incomplete",
            "error_code": error_code,
        },
    )


def managed_run_expectations(engine_root: Path | str) -> list[dict[str, Any]]:
    directory = _managed_runs_dir(engine_root)
    if not directory.exists():
        return []
    return [
        _validate_managed_run(_read_json(file_path))
        for file_path in sorted(directory.glob("*.json"))
    ]


def gc_managed_runs(*, engine_root: Path | str, now: dt.datetime | None = None) -> dict[str, int]:
    current = now or SystemClock().utc_now()
    removed = 0
    kept = 0
    directory = _managed_runs_dir(engine_root)
    if not directory.exists():
        return {"removed": 0, "kept": 0}
    with _trace_lock(directory):
        for file_path in sorted(directory.glob("*.json")):
            record = _validate_managed_run(_read_json(file_path))
            age = current - _parse_utc(record["updated_at"], "updated_at")
            retention = dt.timedelta(days=14 if record["lifecycle_state"] == "persisted" else 90)
            if age > retention:
                file_path.unlink()
                removed += 1
            else:
                kept += 1
    return {"removed": removed, "kept": kept}


def reconcile_managed_runs(engine_root: Path | str) -> list[dict[str, Any]]:
    results = []
    for record in managed_run_expectations(engine_root):
        trace_id = record["trace_id"]
        if trace_id and record["lifecycle_state"] in {"trace-bound", "incomplete"}:
            try:
                context = trace_context(engine_root=engine_root, trace_id=trace_id)
                if context["state"] == "closed":
                    finalize_trace(engine_root=engine_root, trace_id=trace_id)
                    if record["lifecycle_state"] != "incomplete":
                        record = mark_expected_finalized(
                            engine_root=engine_root, run_id=record["run_id"]
                        )
            except TelemetryError:
                pass
        results.append(record)
    gc_managed_runs(engine_root=engine_root)
    return results


def discover_scope_ledgers(engine_root: Path | str) -> list[dict[str, Any]]:
    engine = Path(engine_root).resolve()
    scopes = [
        {
            "scope": "engine",
            "scope_id": "engine",
            "ledger": engine / "EXECUTION_LOG.jsonl",
        },
        {
            "scope": "catalog",
            "scope_id": "portfolio",
            "ledger": engine / "portfolio" / "EXECUTION_LOG.jsonl",
        },
    ]
    registry = engine / "projects" / "port-assignments.yaml"
    if registry.is_file():
        for line in registry.read_text(encoding="utf-8").splitlines():
            match = re.fullmatch(r"([a-z0-9][a-z0-9-]*):", line)
            if match:
                slug = match.group(1)
                scopes.append(
                    {
                        "scope": "project",
                        "scope_id": slug,
                        "ledger": engine / "projects" / slug / "EXECUTION_LOG.jsonl",
                    }
                )
    return scopes


def report_across_scopes(
    engine_root: Path | str,
    *,
    trace_id: str | None = None,
    run_type: str | None = None,
    scope: str | None = None,
    scope_id: str | None = None,
    phase_id: str | None = None,
    batch_id: str | None = None,
    since: str | None = None,
    recent: int | None = None,
) -> dict[str, Any]:
    if phase_id is not None and (
        scope not in {None, "engine"}
        or scope_id not in {None, "engine"}
        or run_type not in {None, "kickoff"}
        or batch_id is not None
    ):
        raise ValidationError("phase selection is valid only for engine kickoff reports")
    reports: list[dict[str, Any]] = []
    diagnostics: list[dict[str, str]] = []
    present_traces: set[str] = set()
    for item in discover_scope_ledgers(engine_root):
        if scope is not None and item["scope"] != scope:
            continue
        if scope_id is not None and item["scope_id"] != scope_id:
            continue
        ledger = item["ledger"]
        if not ledger.exists():
            diagnostics.append(
                {**{key: item[key] for key in ("scope", "scope_id")}, "state": "missing"}
            )
            continue
        try:
            selected = report_history(
                ledger,
                trace_id=trace_id,
                run_type=run_type,
                batch_id=batch_id,
                phase_id=phase_id,
                since=since,
            )
            reports.extend(selected)
            present_traces.update(report["trace_id"] for report in selected)
        except PermissionError:
            diagnostics.append(
                {**{key: item[key] for key in ("scope", "scope_id")}, "state": "unreadable"}
            )
        except TelemetryError:
            diagnostics.append(
                {**{key: item[key] for key in ("scope", "scope_id")}, "state": "invalid"}
            )
    incomplete = []
    for record in managed_run_expectations(engine_root):
        if record["lifecycle_state"] == "persisted":
            continue
        if scope is not None and record["scope"] != scope:
            continue
        if scope_id is not None and record["scope_id"] != scope_id:
            continue
        if run_type is not None and record["run_type"] != run_type:
            continue
        if trace_id is not None and record["trace_id"] != trace_id:
            continue
        if batch_id is not None and record["batch_id"] != batch_id:
            continue
        if phase_id is not None and (
            record["run_type"] != "kickoff" or record["operation"] != f"phase.{phase_id}"
        ):
            continue
        if since is not None and _parse_utc(record["updated_at"], "updated_at") < _parse_utc(
            since, "since"
        ):
            continue
        state = (
            "telemetry-init-incomplete"
            if record["trace_id"] is None
            else "telemetry-finalization-incomplete"
            if record["lifecycle_state"] in {"trace-bound", "incomplete"}
            else "persistence-incomplete"
        )
        matching_report = next(
            (
                report
                for report in reports
                if record["trace_id"] is not None and report["trace_id"] == record["trace_id"]
            ),
            None,
        )
        managed_view = {
            "run_id": record["run_id"],
            "lifecycle_state": state,
            "error_code": record["error_code"],
            "recoverable": True,
        }
        if matching_report is not None:
            matching_report["managed_run"] = managed_view
            continue
        incomplete.append(
            {
                **managed_view,
                "trace_id": record["trace_id"],
                "scope": record["scope"],
                "scope_id": record["scope_id"],
                "run_type": record["run_type"],
                "operation": record["operation"],
                "cycle_id": record["cycle_id"],
                "batch_id": record["batch_id"],
            }
        )
    # Apply one deterministic recent window across finalized and incomplete
    # managed runs. Finalized rows sort by finalized_at; expectation-only rows
    # sort by their registry update timestamp.
    reports.sort(key=lambda item: (item["finalized_at"], item["trace_id"]))
    if recent is not None:
        _require_int(recent, "recent", minimum=1)
        expectation_by_run = {row["run_id"]: row for row in managed_run_expectations(engine_root)}
        combined: list[tuple[str, str, str, dict[str, Any]]] = []
        for report in reports:
            managed = report.get("managed_run")
            stamp = report["finalized_at"]
            if managed and managed["run_id"] in expectation_by_run:
                stamp = expectation_by_run[managed["run_id"]]["updated_at"]
            combined.append((stamp, report["trace_id"], "report", report))
        for row in incomplete:
            source = expectation_by_run[row["run_id"]]
            combined.append((source["updated_at"], row["run_id"], "incomplete", row))
        combined.sort(key=lambda item: (item[0], item[1], item[2]))
        chosen = combined[-recent:] if len(combined) > recent else combined
        reports = [row for _, _, kind, row in chosen if kind == "report"]
        incomplete = [row for _, _, kind, row in chosen if kind == "incomplete"]
        present_traces = {report["trace_id"] for report in reports}

    expectations = managed_run_expectations(engine_root)
    expectation_by_trace = {
        row["trace_id"]: row for row in expectations if row["trace_id"] is not None
    }
    checkpoint_links = []
    for outer in reports:
        if outer["run_type"] != "checkpoint" or not outer.get("batch_id"):
            continue
        children = [
            row
            for row in reports
            if row is not outer
            and row.get("batch_id") == outer["batch_id"]
            and row["scope"] == "project"
        ]
        expected_cycles = set(outer.get("checkpoint_child_cycles", []))
        linked_cycles = {
            expectation_by_trace[row["trace_id"]]["cycle_id"]
            for row in children
            if row["trace_id"] in expectation_by_trace
            and expectation_by_trace[row["trace_id"]]["cycle_id"] is not None
        }
        checkpoint_links.append(
            {
                "checkpoint_id": outer["batch_id"],
                "outer_trace_id": outer["trace_id"],
                "outer_makespan_ns": outer["root_makespan_ns"],
                "child_traces": [
                    {
                        "trace_id": row["trace_id"],
                        "scope_id": row["scope_id"],
                        "root_makespan_ns": row["root_makespan_ns"],
                    }
                    for row in children
                ],
                "summed_child_work_ns": sum(row["root_makespan_ns"] for row in children),
                "missing_child_cycles": sorted(expected_cycles - linked_cycles),
            }
        )
    return {
        "reports": reports,
        "incomplete_runs": incomplete,
        "ledger_diagnostics": diagnostics,
        "checkpoint_links": checkpoint_links,
    }
