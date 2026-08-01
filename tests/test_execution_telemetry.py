from __future__ import annotations

import copy
import datetime as dt
import json
import os
import re
import signal
import stat
import subprocess
import sys
import threading
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

import pytest

# Import the tree-local library, not whatever `agentic_starter` the environment
# resolves. Gate 9 proves a mutation by editing this repo's lib/ inside an
# isolated clone; without this insert the clone's tests would import the
# installed package instead and every mutation here would read as
# `guard-not-load-bearing`.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from agentic_starter import execution_telemetry as telemetry  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
CLI = REPO_ROOT / "bin" / "execution-telemetry"
PARALLEL_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "execution_telemetry" / "parallel.jsonl"
KICKOFF_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "execution_telemetry" / "kickoff-trace.jsonl"


class FakeClock:
    def __init__(
        self,
        *,
        utc: dt.datetime | None = None,
        monotonic: int = 1_000_000,
        boot: str = "synthetic-boot",
    ) -> None:
        self.utc = utc or dt.datetime(2026, 7, 27, 12, tzinfo=dt.UTC)
        self.monotonic = monotonic
        self.boot = boot

    def utc_now(self) -> dt.datetime:
        return self.utc

    def monotonic_ns(self) -> int:
        return self.monotonic

    def boot_id(self) -> str:
        return self.boot

    def advance(self, nanoseconds: int, *, utc_delta: dt.timedelta | None = None) -> None:
        self.monotonic += nanoseconds
        self.utc += (
            utc_delta if utc_delta is not None else dt.timedelta(microseconds=nanoseconds / 1000)
        )


@pytest.fixture
def engine(tmp_path: Path) -> Path:
    root = tmp_path / "engine"
    (root / "projects").mkdir(parents=True)
    (root / "policies").mkdir()
    (root / "portfolio").mkdir()
    (root / "CLAUDE.md").write_text("# synthetic engine\n", encoding="utf-8")
    return root


@pytest.fixture(autouse=True)
def isolated_spool(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    spool = tmp_path / "telemetry-state"
    monkeypatch.setenv("AGENTIC_STARTER_EXECUTION_TELEMETRY_DIR", str(spool))
    return spool


def fixture_bundle() -> dict[str, Any]:
    [bundle] = telemetry.validate_ledger(PARALLEL_FIXTURE)
    return bundle


def span_by_operation(bundle: dict[str, Any], operation: str) -> dict[str, Any]:
    spans = cast(list[dict[str, Any]], bundle["spans"])
    return next(span for span in spans if span["operation"] == operation)


def trace_dir(engine: Path, trace_id: str) -> Path:
    return (
        Path(os.environ["AGENTIC_STARTER_EXECUTION_TELEMETRY_DIR"])
        / telemetry.repo_key(engine)
        / trace_id
    )


def finish_trace(
    engine: Path,
    handle: telemetry.SpanHandle,
    *,
    clock: telemetry.Clock | None = None,
) -> dict[str, Any]:
    telemetry.finish_span(
        engine_root=engine,
        trace_id=handle.trace_id,
        span_id=handle.span_id,
        outcome="success",
        clock=clock,
    )
    return telemetry.finalize_trace(
        engine_root=engine,
        trace_id=handle.trace_id,
        clock=clock,
    )


def cli(
    *args: str,
    env: dict[str, str] | None = None,
    timeout: float = 10,
) -> subprocess.CompletedProcess[str]:
    command_env = os.environ.copy()
    if env:
        command_env.update(env)
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        capture_output=True,
        text=True,
        env=command_env,
        timeout=timeout,
    )


@pytest.mark.parametrize("fixture_path", [PARALLEL_FIXTURE, KICKOFF_FIXTURE])
def test_committed_fixture_is_exact_private_and_canonical(fixture_path: Path) -> None:
    raw = fixture_path.read_text(encoding="utf-8")
    [bundle] = telemetry.validate_ledger(fixture_path)

    assert raw == json.dumps(bundle, sort_keys=True, separators=(",", ":")) + "\n"
    assert set(bundle) == {
        "schema",
        "trace_id",
        "finalized_at",
        "scope",
        "scope_id",
        "root_span_id",
        "spans",
    }
    forbidden = {
        "prompt",
        "response",
        "command",
        "stdout",
        "stderr",
        "environment",
        "secret",
        "source_text",
        "repo_root",
        "scope_root",
    }
    assert forbidden.isdisjoint(raw.lower())
    assert "/Users/" not in raw
    assert "C:\\" not in raw


@pytest.mark.parametrize(
    ("mutation", "match"),
    [
        (lambda value: value.update(extra="no"), "unknown keys"),
        (lambda value: value.update(category="unknown"), "unknown category"),
        (lambda value: value.update(outcome="unknown"), "unknown outcome"),
        (lambda value: value.update(trace_id="ABC"), "UUID4"),
        (lambda value: value.update(attempt=True), "integer"),
        (lambda value: value.update(duration_ns=61), "duration_ns"),
        (lambda value: value.update(operation="/private/source"), "absolute|home-relative"),
        (lambda value: value.update(operation=r"C:\private"), "absolute|home-relative"),
        (lambda value: value.update(operation="~/.secret"), "absolute|home-relative"),
        (lambda value: value.update(operation="line\nprose"), "stable token"),
    ],
)
def test_span_schema_rejects_unknown_malformed_or_private_values(
    mutation: Callable[[dict[str, Any]], None], match: str
) -> None:
    span = copy.deepcopy(cast(list[dict[str, Any]], fixture_bundle()["spans"])[1])
    mutation(span)
    with pytest.raises(telemetry.ValidationError, match=match):
        telemetry.validate_span(span)


@pytest.mark.parametrize(
    "field",
    ["prompt", "response", "command", "stdout", "stderr", "environment", "secret", "source_text"],
)
def test_schema_has_no_arbitrary_or_sensitive_metadata_channel(field: str) -> None:
    span = copy.deepcopy(fixture_bundle()["spans"][1])
    span[field] = "sensitive"
    with pytest.raises(telemetry.ValidationError, match="unknown keys"):
        telemetry.validate_span(span)


def test_timeout_and_token_reference_relations_are_exact() -> None:
    span = copy.deepcopy(fixture_bundle()["spans"][1])
    span["outcome"] = "timeout"
    span["exit_code"] = 124
    span["timeout_kind"] = "command"
    span["timeout_ns"] = 10
    telemetry.validate_span(span)

    for field, value in (
        ("timeout_kind", "other"),
        ("timeout_ns", True),
    ):
        invalid = copy.deepcopy(span)
        invalid[field] = value
        with pytest.raises(telemetry.ValidationError):
            telemetry.validate_span(invalid)

    invalid_ref = copy.deepcopy(fixture_bundle()["spans"][1])
    invalid_ref["token_reference"]["input_tokens"] = 20
    with pytest.raises(telemetry.ValidationError, match="unknown keys"):
        telemetry.validate_span(invalid_ref)


def test_exact_elapsed_format_has_no_utc_or_minute_estimate() -> None:
    assert telemetry.format_elapsed(0) == "0.000s"
    assert telemetry.format_elapsed(1_234_567_890) == "1.234s"
    assert telemetry.format_elapsed(61_999_999_999) == "1m 1s"
    assert telemetry.format_elapsed(3_661_000_000_000) == "1h 1m 1s"


def test_batch_metrics_distinguish_makespan_summed_and_committed_work() -> None:
    bundle = copy.deepcopy(fixture_bundle())
    root, first, second = bundle["spans"]
    for span in bundle["spans"]:
        span["run_type"] = "improve-batch"
    root["operation"] = "batch.improve"
    first["operation"] = "role.cycle.ab12cd34"
    second["operation"] = "role.cycle.cd34ef56"
    commit = copy.deepcopy(first)
    commit.update(
        {
            "span_id": "00000000000040008000000000000004",
            "category": "reconciliation",
            "operation": "batch.commit.ab12cd34",
            "start_offset_ns": 92,
            "end_offset_ns": 94,
            "duration_ns": 2,
        }
    )
    commit.pop("token_reference", None)
    bundle["spans"].append(commit)
    bundle["spans"].sort(key=lambda item: (item["start_offset_ns"], item["span_id"]))

    metrics = telemetry.aggregate_trace(bundle)["batch_metrics"]
    assert metrics["batch_makespan_ns"] == 100
    assert metrics["summed_member_work_ns"] == 110
    assert metrics["committed_member_work_ns"] == 60
    assert metrics["member_active_union_ns"] == 80
    assert metrics["overlap_ns"] == 30
    assert metrics["peak_concurrency"] == 2
    assert metrics["committed_members"] == 1
    assert metrics["wall_clock_per_committed_work_unit_ns"] == 100
    assert metrics["observed_parallel_speedup"] == 0.6


def test_bundle_rejects_scope_mismatch_invalid_nesting_and_unsorted_spans() -> None:
    bundle = fixture_bundle()

    mismatch = copy.deepcopy(bundle)
    mismatch["spans"][1]["scope_id"] = "other"
    with pytest.raises(telemetry.ValidationError, match="scope"):
        telemetry.validate_bundle(mismatch)

    outside = copy.deepcopy(bundle)
    outside["spans"][1]["end_offset_ns"] = 101
    outside["spans"][1]["duration_ns"] = 91
    with pytest.raises(telemetry.ValidationError, match="contained"):
        telemetry.validate_bundle(outside)

    unsorted = copy.deepcopy(bundle)
    unsorted["spans"][1], unsorted["spans"][2] = unsorted["spans"][2], unsorted["spans"][1]
    with pytest.raises(telemetry.ValidationError, match="sorted"):
        telemetry.validate_bundle(unsorted)


@pytest.mark.parametrize(
    ("mutation", "match"),
    [
        (
            lambda bundle: bundle["spans"][1].update(category="run"),
            "run.*root|root.*run",
        ),
        (
            lambda bundle: bundle["spans"][1].update(run_type="improve"),
            "run_type",
        ),
        (
            lambda bundle: bundle["spans"][0].update(start_offset_ns=1, duration_ns=99),
            "offset zero|start_offset_ns",
        ),
        (
            lambda bundle: (
                bundle.update(scope_id="other"),
                [span.update(scope_id="other") for span in bundle["spans"]],
            ),
            "engine",
        ),
        (
            lambda bundle: (
                bundle.update(scope="catalog", scope_id="other"),
                [span.update(scope="catalog", scope_id="other") for span in bundle["spans"]],
            ),
            "portfolio|catalog",
        ),
    ],
)
def test_bundle_rejects_every_durable_lifecycle_relation(
    mutation: Callable[[dict[str, Any]], object], match: str
) -> None:
    bundle = copy.deepcopy(fixture_bundle())
    mutation(bundle)
    with pytest.raises(telemetry.ValidationError, match=match):
        telemetry.validate_bundle(bundle)


def test_process_backed_error_rejects_zero_exit_code() -> None:
    span = copy.deepcopy(cast(list[dict[str, Any]], fixture_bundle()["spans"])[1])
    span.update(outcome="error", exit_code=0)
    with pytest.raises(telemetry.ValidationError, match="error|nonzero"):
        telemetry.validate_span(span)


def test_monotonic_duration_survives_backward_utc_jump(engine: Path) -> None:
    clock = FakeClock()
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="improve",
        operation="cycle",
        clock=clock,
    )
    clock.advance(10, utc_delta=dt.timedelta(hours=-3))
    child = telemetry.start_span(
        engine_root=engine,
        trace_id=root.trace_id,
        parent_span_id=root.span_id,
        category="intelligence",
        operation="writer",
        clock=clock,
    )
    clock.advance(25, utc_delta=dt.timedelta(hours=-2))
    telemetry.finish_span(
        engine_root=engine,
        trace_id=root.trace_id,
        span_id=child.span_id,
        outcome="success",
        clock=clock,
    )
    clock.advance(5, utc_delta=dt.timedelta(hours=-1))
    bundle = finish_trace(engine, root, clock=clock)

    child_span = span_by_operation(bundle, "writer")
    assert child_span["duration_ns"] == 25
    assert child_span["start_offset_ns"] == 10
    assert child_span["end_offset_ns"] == 35
    assert telemetry.aggregate_trace(bundle)["root_makespan_ns"] == 40


def test_review_metrics_are_exact_idempotent_and_role_bound(engine: Path) -> None:
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="kickoff",
        operation="phase.32",
    )
    review = telemetry.start_span(
        engine_root=engine,
        trace_id=root.trace_id,
        parent_span_id=root.span_id,
        category="intelligence",
        operation="role.plan-review",
        role="reviewer",
    )
    implementation = telemetry.start_span(
        engine_root=engine,
        trace_id=root.trace_id,
        parent_span_id=root.span_id,
        category="intelligence",
        operation="role.implement",
        role="coder",
    )
    telemetry.finish_span(
        engine_root=engine,
        trace_id=root.trace_id,
        span_id=review.span_id,
        outcome="success",
    )
    first = telemetry.attach_review_metrics(
        engine_root=engine,
        trace_id=root.trace_id,
        span_id=review.span_id,
        findings_reported=4,
        actionable_findings=2,
    )
    repeated = telemetry.attach_review_metrics(
        engine_root=engine,
        trace_id=root.trace_id,
        span_id=review.span_id,
        findings_reported=4,
        actionable_findings=2,
    )
    assert repeated == first
    with pytest.raises(telemetry.ValidationError, match="conflicting"):
        telemetry.attach_review_metrics(
            engine_root=engine,
            trace_id=root.trace_id,
            span_id=review.span_id,
            findings_reported=4,
            actionable_findings=1,
        )
    with pytest.raises(telemetry.ValidationError, match="review intelligence"):
        telemetry.attach_review_metrics(
            engine_root=engine,
            trace_id=root.trace_id,
            span_id=implementation.span_id,
            findings_reported=0,
            actionable_findings=0,
        )
    telemetry.finish_span(
        engine_root=engine,
        trace_id=root.trace_id,
        span_id=implementation.span_id,
        outcome="success",
    )
    bundle = finish_trace(engine, root)
    durable = span_by_operation(bundle, "role.plan-review")
    assert durable["findings_reported"] == 4
    assert durable["actionable_findings"] == 2


def test_scope_resolution_is_fail_closed(engine: Path) -> None:
    book = engine / "projects" / "synthetic"
    book.mkdir()
    portfolio = engine / "portfolio"

    assert telemetry.scope_ledger_path(engine, engine, "engine", "engine") == (
        engine / "EXECUTION_LOG.jsonl"
    )
    assert telemetry.scope_ledger_path(engine, book, "project", "synthetic") == (
        book / "EXECUTION_LOG.jsonl"
    )
    assert (
        telemetry.scope_ledger_path(engine, portfolio, "catalog", "portfolio")
        == portfolio / "EXECUTION_LOG.jsonl"
    )

    bad = (
        (engine, "project", "synthetic"),
        (book, "engine", "engine"),
        (portfolio, "catalog", "other"),
        (engine / "projects" / ".." / "synthetic", "project", "synthetic"),
    )
    for scope_root, scope, scope_id in bad:
        with pytest.raises(telemetry.ScopeError):
            telemetry.scope_ledger_path(engine, scope_root, scope, scope_id)


def test_lifecycle_idempotency_finalization_and_crash_recovery(engine: Path) -> None:
    clock = FakeClock()
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="kickoff",
        operation="phase",
        clock=clock,
    )
    clock.advance(10)
    child = telemetry.start_span(
        engine_root=engine,
        trace_id=root.trace_id,
        parent_span_id=root.span_id,
        category="gate",
        operation="test",
        clock=clock,
    )
    with pytest.raises(telemetry.IncompleteTraceError):
        telemetry.finish_span(
            engine_root=engine,
            trace_id=root.trace_id,
            span_id=root.span_id,
            outcome="success",
            clock=clock,
        )
    with pytest.raises(telemetry.IncompleteTraceError):
        telemetry.finalize_trace(engine_root=engine, trace_id=root.trace_id, clock=clock)

    clock.advance(10)
    first = telemetry.finish_span(
        engine_root=engine,
        trace_id=root.trace_id,
        span_id=child.span_id,
        outcome="success",
        exit_code=0,
        clock=clock,
    )
    repeated = telemetry.finish_span(
        engine_root=engine,
        trace_id=root.trace_id,
        span_id=child.span_id,
        outcome="success",
        exit_code=0,
        clock=clock,
    )
    assert repeated == first
    with pytest.raises(telemetry.ValidationError, match="conflicting"):
        telemetry.finish_span(
            engine_root=engine,
            trace_id=root.trace_id,
            span_id=child.span_id,
            outcome="error",
            exit_code=1,
            clock=clock,
        )

    clock.advance(10)
    bundle = finish_trace(engine, root, clock=clock)
    ledger = engine / "EXECUTION_LOG.jsonl"
    assert len(ledger.read_text(encoding="utf-8").splitlines()) == 1
    assert (
        telemetry.finalize_trace(engine_root=engine, trace_id=root.trace_id, clock=clock) == bundle
    )
    assert len(ledger.read_text(encoding="utf-8").splitlines()) == 1

    marker = trace_dir(engine, root.trace_id) / "finalized.json"
    marker.unlink()
    assert (
        telemetry.finalize_trace(engine_root=engine, trace_id=root.trace_id, clock=clock) == bundle
    )
    assert marker.is_file()
    assert len(ledger.read_text(encoding="utf-8").splitlines()) == 1


def test_conflicting_existing_trace_id_is_rejected(engine: Path) -> None:
    clock = FakeClock()
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="kickoff",
        operation="phase",
        clock=clock,
    )
    clock.advance(10)
    bundle = finish_trace(engine, root, clock=clock)
    marker = trace_dir(engine, root.trace_id) / "finalized.json"
    marker.unlink()
    conflicting = copy.deepcopy(bundle)
    conflicting["spans"][0]["operation"] = "different"
    (engine / "EXECUTION_LOG.jsonl").write_text(
        json.dumps(conflicting, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(telemetry.ValidationError, match="conflicting"):
        telemetry.finalize_trace(engine_root=engine, trace_id=root.trace_id, clock=clock)


def test_finalized_marker_restores_missing_ledger_row(engine: Path) -> None:
    clock = FakeClock()
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="kickoff",
        operation="phase",
        clock=clock,
    )
    clock.advance(10)
    bundle = finish_trace(engine, root, clock=clock)
    (engine / "EXECUTION_LOG.jsonl").unlink()

    assert (
        telemetry.finalize_trace(engine_root=engine, trace_id=root.trace_id, clock=clock) == bundle
    )
    assert telemetry.validate_ledger(engine / "EXECUTION_LOG.jsonl") == [bundle]


def test_finalized_marker_rejects_conflicting_ledger_row(engine: Path) -> None:
    clock = FakeClock()
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="kickoff",
        operation="phase",
        clock=clock,
    )
    clock.advance(10)
    bundle = finish_trace(engine, root, clock=clock)
    conflicting = copy.deepcopy(bundle)
    conflicting["spans"][0]["operation"] = "different"
    (engine / "EXECUTION_LOG.jsonl").write_text(
        json.dumps(conflicting, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(telemetry.ValidationError, match="conflicting"):
        telemetry.finalize_trace(engine_root=engine, trace_id=root.trace_id, clock=clock)


def test_finalized_marker_rejects_malformed_unrelated_ledger_row(engine: Path) -> None:
    clock = FakeClock()
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="kickoff",
        operation="phase",
        clock=clock,
    )
    clock.advance(10)
    finish_trace(engine, root, clock=clock)
    ledger = engine / "EXECUTION_LOG.jsonl"
    ledger.write_text(
        '{"schema":"malformed-unrelated-row"}\n' + ledger.read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    with pytest.raises(telemetry.ValidationError, match="row 1"):
        telemetry.finalize_trace(engine_root=engine, trace_id=root.trace_id, clock=clock)


def test_atomic_state_and_first_ledger_creation_fsync_directories(
    engine: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    directory_syncs = 0
    real_fsync = os.fsync

    def observe_fsync(file_descriptor: int) -> None:
        nonlocal directory_syncs
        if stat.S_ISDIR(os.fstat(file_descriptor).st_mode):
            directory_syncs += 1
        real_fsync(file_descriptor)

    monkeypatch.setattr(telemetry.os, "fsync", observe_fsync)
    clock = FakeClock()
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="kickoff",
        operation="phase",
        clock=clock,
    )
    clock.advance(10)
    finish_trace(engine, root, clock=clock)

    # trace.json, the root span, its closed replacement, first ledger creation,
    # and finalized.json must each make their containing directory durable.
    assert directory_syncs >= 5


def test_first_ledger_directory_sync_failure_is_recoverable_and_fail_closed(
    engine: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = FakeClock()
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="kickoff",
        operation="phase",
        clock=clock,
    )
    clock.advance(10)
    telemetry.finish_span(
        engine_root=engine,
        trace_id=root.trace_id,
        span_id=root.span_id,
        outcome="success",
        clock=clock,
    )
    real_sync = telemetry._fsync_directory

    def fail_ledger_directory(directory: Path) -> None:
        if directory == engine:
            raise OSError("injected directory sync failure")
        real_sync(directory)

    monkeypatch.setattr(telemetry, "_fsync_directory", fail_ledger_directory)
    with pytest.raises(telemetry.TelemetryError, match="ledger"):
        telemetry.finalize_trace(engine_root=engine, trace_id=root.trace_id, clock=clock)
    assert telemetry.validate_ledger(engine / "EXECUTION_LOG.jsonl")
    assert not (trace_dir(engine, root.trace_id) / "finalized.json").exists()

    monkeypatch.setattr(telemetry, "_fsync_directory", real_sync)
    bundle = telemetry.finalize_trace(engine_root=engine, trace_id=root.trace_id, clock=clock)
    assert bundle["trace_id"] == root.trace_id
    assert (trace_dir(engine, root.trace_id) / "finalized.json").is_file()


def test_failed_first_ledger_directory_sync_is_observed_again_on_finalize_retry(
    engine: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = FakeClock()
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="kickoff",
        operation="phase",
        clock=clock,
    )
    clock.advance(10)
    telemetry.finish_span(
        engine_root=engine,
        trace_id=root.trace_id,
        span_id=root.span_id,
        outcome="success",
        clock=clock,
    )
    real_sync = telemetry._fsync_directory
    ledger_directory_syncs = 0

    def fail_once_then_observe(directory: Path) -> None:
        nonlocal ledger_directory_syncs
        if directory == engine:
            ledger_directory_syncs += 1
            if ledger_directory_syncs == 1:
                raise OSError("injected first ledger directory sync failure")
        real_sync(directory)

    monkeypatch.setattr(telemetry, "_fsync_directory", fail_once_then_observe)
    with pytest.raises(telemetry.TelemetryError, match="ledger"):
        telemetry.finalize_trace(engine_root=engine, trace_id=root.trace_id, clock=clock)
    assert ledger_directory_syncs == 1
    assert telemetry.validate_ledger(engine / "EXECUTION_LOG.jsonl")
    assert not (trace_dir(engine, root.trace_id) / "finalized.json").exists()

    bundle = telemetry.finalize_trace(engine_root=engine, trace_id=root.trace_id, clock=clock)
    assert bundle["trace_id"] == root.trace_id
    assert ledger_directory_syncs == 2
    assert (trace_dir(engine, root.trace_id) / "finalized.json").is_file()


def test_same_boot_recovery_closes_deepest_first(engine: Path) -> None:
    clock = FakeClock()
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="improve",
        operation="cycle",
        clock=clock,
    )
    clock.advance(10)
    child = telemetry.start_span(
        engine_root=engine,
        trace_id=root.trace_id,
        parent_span_id=root.span_id,
        category="intelligence",
        operation="writer",
        clock=clock,
    )
    clock.advance(10)
    telemetry.start_span(
        engine_root=engine,
        trace_id=root.trace_id,
        parent_span_id=child.span_id,
        category="wait",
        operation="provider",
        clock=clock,
    )
    clock.advance(10)
    bundle = telemetry.recover_trace(engine_root=engine, trace_id=root.trace_id, clock=clock)
    assert {span["outcome"] for span in bundle["spans"]} == {"interrupted"}
    assert len(telemetry.validate_ledger(engine / "EXECUTION_LOG.jsonl")) == 1


def test_cross_boot_recovery_retains_incomplete_spool(engine: Path) -> None:
    clock = FakeClock(boot="boot-a")
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="improve",
        operation="cycle",
        clock=clock,
    )
    with pytest.raises(telemetry.ClockDomainError):
        telemetry.recover_trace(
            engine_root=engine,
            trace_id=root.trace_id,
            clock=FakeClock(boot="boot-b"),
        )
    runtime_dir = trace_dir(engine, root.trace_id)
    assert (runtime_dir / "trace.json").is_file()
    assert not (engine / "EXECUTION_LOG.jsonl").exists()


def test_runtime_validation_rejects_cyclic_ancestry_without_traceback(
    engine: Path,
) -> None:
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="improve",
        operation="cycle",
    )
    child = telemetry.start_span(
        engine_root=engine,
        trace_id=root.trace_id,
        parent_span_id=root.span_id,
        category="intelligence",
        operation="writer",
    )
    root_path = trace_dir(engine, root.trace_id) / "spans" / f"{root.span_id}.json"
    root_record = json.loads(root_path.read_text(encoding="utf-8"))
    root_record["parent_span_id"] = child.span_id
    root_path.write_text(json.dumps(root_record), encoding="utf-8")

    with pytest.raises(telemetry.ValidationError, match="cycle|root|ancestry"):
        telemetry.validate_runtime_trace(engine_root=engine, trace_id=root.trace_id)


def test_recovery_detects_no_progress_and_retains_corrupt_spool(engine: Path) -> None:
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="improve",
        operation="cycle",
    )
    child = telemetry.start_span(
        engine_root=engine,
        trace_id=root.trace_id,
        parent_span_id=root.span_id,
        category="intelligence",
        operation="writer",
    )
    runtime_dir = trace_dir(engine, root.trace_id)
    root_path = runtime_dir / "spans" / f"{root.span_id}.json"
    child_path = runtime_dir / "spans" / f"{child.span_id}.json"
    root_record = json.loads(root_path.read_text(encoding="utf-8"))
    child_record = json.loads(child_path.read_text(encoding="utf-8"))
    root_record["parent_span_id"] = child.span_id
    child_record["parent_span_id"] = root.span_id
    root_path.write_text(json.dumps(root_record), encoding="utf-8")
    child_path.write_text(json.dumps(child_record), encoding="utf-8")

    with pytest.raises(telemetry.ValidationError, match="progress|cycle|ancestry"):
        telemetry.recover_trace(engine_root=engine, trace_id=root.trace_id)
    assert (runtime_dir / "trace.json").is_file()
    assert not (engine / "EXECUTION_LOG.jsonl").exists()


def test_runtime_validation_rejects_malformed_token_reference(engine: Path) -> None:
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="improve",
        operation="cycle",
    )
    root_path = trace_dir(engine, root.trace_id) / "spans" / f"{root.span_id}.json"
    record = json.loads(root_path.read_text(encoding="utf-8"))
    record["token_reference"] = {"ledger": "USAGE_LOG.md", "cycle_id": "cycle"}
    root_path.write_text(json.dumps(record), encoding="utf-8")

    with pytest.raises(telemetry.ValidationError, match="token_reference"):
        telemetry.validate_runtime_trace(engine_root=engine, trace_id=root.trace_id)


def test_runtime_validation_normalizes_malformed_closed_results(
    engine: Path,
) -> None:
    clock = FakeClock()
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="improve",
        operation="cycle",
        clock=clock,
    )
    clock.advance(10)
    telemetry.finish_span(
        engine_root=engine,
        trace_id=root.trace_id,
        span_id=root.span_id,
        outcome="success",
        clock=clock,
    )
    root_path = trace_dir(engine, root.trace_id) / "spans" / f"{root.span_id}.json"
    record = json.loads(root_path.read_text(encoding="utf-8"))
    del record["end_monotonic_ns"]
    root_path.write_text(json.dumps(record), encoding="utf-8")

    with pytest.raises(telemetry.ValidationError, match="end_monotonic_ns|result"):
        telemetry.validate_runtime_trace(engine_root=engine, trace_id=root.trace_id)


def test_parallel_aggregation_uses_interval_unions() -> None:
    bundle = fixture_bundle()
    report = telemetry.aggregate_trace(bundle)
    group = report["concurrency_groups"]["parallel-review"]

    assert report["root_makespan_ns"] == 100
    assert report["non_root_coverage_ns"] == 80
    assert report["unattributed_ns"] == 20
    assert report["category_coverage_ns"]["intelligence"] == 80
    assert report["failed_coverage_ns"] == 50
    assert report["retry_coverage_ns"] == 50
    assert group == {
        "member_count": 2,
        "summed_work_ns": 110,
        "enclosing_window_ns": 80,
        "active_union_ns": 80,
        "overlap_ns": 30,
        "peak_concurrency": 2,
        "work_to_window_ratio": 1.375,
    }
    assert report["root_makespan_ns"] < group["summed_work_ns"]
    text = telemetry.format_text_report([report])
    assert "Root makespan: 100 ns" in text
    assert "110 ns summed work" in text
    assert "30 ns overlap, peak 2" in text
    assert report["token_references"] == [
        {
            "ledger": "USAGE_LOG.md",
            "cycle_id": "cycle-31.1",
            "role": "planner",
            "span_ids": ["00000000000040008000000000000002"],
        }
    ]
    assert "Token references:" in text
    assert "USAGE_LOG.md" in text
    assert "cycle-31.1" in text
    assert "planner" in text


def test_root_token_reference_is_visible_in_json_and_text_reports(
    engine: Path,
) -> None:
    clock = FakeClock()
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="kickoff",
        operation="phase",
        token_cycle_id="phase-31.1",
        token_role="orchestrator",
        clock=clock,
    )
    clock.advance(10)
    bundle = finish_trace(engine, root, clock=clock)
    report = telemetry.aggregate_trace(bundle)

    assert report["token_references"] == [
        {
            "ledger": "USAGE_LOG.md",
            "cycle_id": "phase-31.1",
            "role": "orchestrator",
            "span_ids": [root.span_id],
        }
    ]
    text = telemetry.format_text_report([report])
    assert root.span_id in text
    assert "USAGE_LOG.md" in text
    assert "phase-31.1" in text
    assert "orchestrator" in text


def test_nested_span_does_not_inflate_non_root_coverage() -> None:
    bundle = fixture_bundle()
    nested = copy.deepcopy(bundle["spans"][1])
    nested.update(
        {
            "span_id": "00000000000040008000000000000004",
            "parent_span_id": "00000000000040008000000000000002",
            "category": "gate",
            "operation": "nested-gate",
            "start_offset_ns": 20,
            "end_offset_ns": 30,
            "duration_ns": 10,
            "started_at": "2026-07-27T12:00:00.000020Z",
            "ended_at": "2026-07-27T12:00:00.000030Z",
        }
    )
    for key in ("batch_id", "concurrency_group", "role", "token_reference"):
        nested.pop(key, None)
    bundle["spans"].insert(2, nested)
    report = telemetry.aggregate_trace(bundle)
    assert report["non_root_coverage_ns"] == 80
    assert report["category_coverage_ns"]["gate"] == 10


def test_history_filters_after_deterministic_sort_and_rejects_malformed(
    tmp_path: Path,
) -> None:
    first = fixture_bundle()
    second = copy.deepcopy(first)
    second_trace = "11111111111141118111111111111111"
    second["trace_id"] = second_trace
    second["finalized_at"] = "2026-07-27T13:00:00.000000Z"
    second["root_span_id"] = "11111111111141118111111111111112"
    id_map = {
        "00000000000040008000000000000001": "11111111111141118111111111111112",
        "00000000000040008000000000000002": "11111111111141118111111111111113",
        "00000000000040008000000000000003": "11111111111141118111111111111114",
    }
    for span in second["spans"]:
        span["trace_id"] = second_trace
        span["span_id"] = id_map[span["span_id"]]
        if span["parent_span_id"] is not None:
            span["parent_span_id"] = id_map[span["parent_span_id"]]
        span["run_type"] = "improve"
        span.pop("batch_id", None)
    ledger = tmp_path / "history.jsonl"
    ledger.write_text(
        "\n".join(
            json.dumps(item, sort_keys=True, separators=(",", ":")) for item in (second, first)
        )
        + "\n",
        encoding="utf-8",
    )

    assert [row["trace_id"] for row in telemetry.report_history(ledger)] == [
        first["trace_id"],
        second_trace,
    ]
    assert telemetry.report_history(ledger, recent=1)[0]["trace_id"] == second_trace
    assert telemetry.report_history(ledger, run_type="kickoff")[0]["trace_id"] == first["trace_id"]
    assert (
        telemetry.report_history(ledger, batch_id="batch-31.1")[0]["trace_id"] == first["trace_id"]
    )

    ledger.write_text(ledger.read_text(encoding="utf-8") + "{bad json\n", encoding="utf-8")
    with pytest.raises(telemetry.ValidationError, match="row 3"):
        telemetry.report_history(ledger)


def test_concurrent_process_mutations_do_not_lose_spans(engine: Path) -> None:
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="kickoff",
        operation="phase",
    )
    start_commands = [
        [
            sys.executable,
            str(CLI),
            "start",
            "--repo-root",
            str(engine),
            "--trace-id",
            root.trace_id,
            "--parent-span-id",
            root.span_id,
            "--category",
            "intelligence",
            "--operation",
            f"worker-{index}",
        ]
        for index in range(6)
    ]
    processes = [
        subprocess.Popen(command, stdout=subprocess.PIPE, text=True) for command in start_commands
    ]
    handles = []
    for process in processes:
        output, _ = process.communicate(timeout=10)
        assert process.returncode == 0
        handles.append(json.loads(output))

    finish_commands = [
        [
            sys.executable,
            str(CLI),
            "finish",
            "--repo-root",
            str(engine),
            "--trace-id",
            root.trace_id,
            "--span-id",
            handle["span_id"],
            "--outcome",
            "success",
        ]
        for handle in handles
    ]
    processes = [
        subprocess.Popen(command, stdout=subprocess.PIPE, text=True) for command in finish_commands
    ]
    for process in processes:
        process.communicate(timeout=10)
        assert process.returncode == 0

    bundle = finish_trace(engine, root)
    assert len(bundle["spans"]) == 7
    assert len({span["span_id"] for span in bundle["spans"]}) == 7


@pytest.mark.parametrize(
    ("argv", "expected_exit", "expected_outcome"),
    [
        ([sys.executable, "-c", "raise SystemExit(0)"], 0, "success"),
        ([sys.executable, "-c", "raise SystemExit(7)"], 7, "error"),
        (["/definitely/not/a/program"], 127, "error"),
        (
            [sys.executable, "-c", "import os,signal; os.kill(os.getpid(), signal.SIGTERM)"],
            143,
            "interrupted",
        ),
    ],
)
def test_observed_command_preserves_exit_semantics(
    engine: Path, argv: list[str], expected_exit: int, expected_outcome: str
) -> None:
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="kickoff",
        operation="phase",
    )
    result = telemetry.run_observed(
        engine_root=engine,
        trace_id=root.trace_id,
        parent_span_id=root.span_id,
        category="gate",
        operation="command",
        argv=argv,
    )
    assert (result.exit_code, result.outcome, result.telemetry_complete) == (
        expected_exit,
        expected_outcome,
        True,
    )
    bundle = finish_trace(engine, root)
    observed = span_by_operation(bundle, "command")
    assert observed["exit_code"] == expected_exit
    assert observed["outcome"] == expected_outcome


def test_observed_command_propagates_nested_telemetry_context(engine: Path, tmp_path: Path) -> None:
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="kickoff",
        operation="phase",
    )
    capture = tmp_path / "context.json"
    code = (
        "import json,os,pathlib;"
        "keys={'engine':'AGENTIC_STARTER_EXECUTION_ENGINE_ROOT',"
        "'trace':'AGENTIC_STARTER_EXECUTION_TRACE_ID',"
        "'parent':'AGENTIC_STARTER_EXECUTION_PARENT_SPAN_ID'};"
        f"pathlib.Path({str(capture)!r}).write_text("
        "json.dumps({name:os.environ.get(key) for name,key in keys.items()}))"
    )

    result = telemetry.run_observed(
        engine_root=engine,
        trace_id=root.trace_id,
        parent_span_id=root.span_id,
        category="gate",
        operation="outer-gate",
        argv=[sys.executable, "-c", code],
    )

    context = json.loads(capture.read_text(encoding="utf-8"))
    assert context == {
        "engine": str(engine.resolve()),
        "trace": root.trace_id,
        "parent": result.span_id,
    }
    finish_trace(engine, root)


def test_observed_command_clears_stale_context_when_span_start_fails(
    engine: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for key in (
        "AGENTIC_STARTER_EXECUTION_ENGINE_ROOT",
        "AGENTIC_STARTER_EXECUTION_TRACE_ID",
        "AGENTIC_STARTER_EXECUTION_PARENT_SPAN_ID",
    ):
        monkeypatch.setenv(key, "stale")
    capture = tmp_path / "context.json"
    code = (
        "import json,os,pathlib;"
        "keys={'engine':'AGENTIC_STARTER_EXECUTION_ENGINE_ROOT',"
        "'trace':'AGENTIC_STARTER_EXECUTION_TRACE_ID',"
        "'parent':'AGENTIC_STARTER_EXECUTION_PARENT_SPAN_ID'};"
        f"pathlib.Path({str(capture)!r}).write_text("
        "json.dumps({name:os.environ.get(key) for name,key in keys.items()}))"
    )

    result = telemetry.run_observed(
        engine_root=engine,
        trace_id="ffffffffffffffffffffffffffffffff",
        parent_span_id="eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
        category="gate",
        operation="unrecorded",
        argv=[sys.executable, "-c", code],
    )

    assert result.telemetry_complete is False
    assert json.loads(capture.read_text(encoding="utf-8")) == {
        "engine": None,
        "trace": None,
        "parent": None,
    }


def test_observed_timeout_terminates_process_group(engine: Path, tmp_path: Path) -> None:
    marker = tmp_path / "descendant-finished"
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="kickoff",
        operation="phase",
    )
    code = (
        "import subprocess,sys,time;"
        f"subprocess.Popen([sys.executable,'-c',\"import time,pathlib;"
        f"time.sleep(1);pathlib.Path({str(marker)!r}).write_text('bad')\"]);"
        "time.sleep(10)"
    )
    result = telemetry.run_observed(
        engine_root=engine,
        trace_id=root.trace_id,
        parent_span_id=root.span_id,
        category="gate",
        operation="timeout-command",
        argv=[sys.executable, "-c", code],
        timeout_seconds=0.05,
    )
    assert (result.exit_code, result.outcome) == (124, "timeout")
    threading.Event().wait(1.2)
    assert not marker.exists()
    bundle = finish_trace(engine, root)
    observed = span_by_operation(bundle, "timeout-command")
    assert observed["timeout_kind"] == "command"
    assert observed["timeout_ns"] == 50_000_000


def test_cli_sigint_cancels_observed_process_group(engine: Path, tmp_path: Path) -> None:
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="kickoff",
        operation="phase",
    )
    started = tmp_path / "child-started"
    result_path = tmp_path / "cancel-result.json"
    command = [
        sys.executable,
        str(CLI),
        "run",
        "--repo-root",
        str(engine),
        "--trace-id",
        root.trace_id,
        "--parent-span-id",
        root.span_id,
        "--category",
        "gate",
        "--operation",
        "cancel-command",
        "--result-json",
        str(result_path),
        "--",
        sys.executable,
        "-c",
        f"import pathlib,time;pathlib.Path({str(started)!r}).write_text('ready');time.sleep(30)",
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for _ in range(100):
        if started.exists():
            break
        threading.Event().wait(0.02)
    assert started.exists()
    process.send_signal(signal.SIGINT)
    stdout, stderr = process.communicate(timeout=10)

    assert process.returncode == 130, (stdout, stderr)
    assert stdout == ""
    assert stderr == ""
    envelope = json.loads(result_path.read_text(encoding="utf-8"))
    assert envelope["exit_code"] == 130
    assert envelope["outcome"] == "cancelled"
    bundle = finish_trace(engine, root)
    observed = span_by_operation(bundle, "cancel-command")
    assert observed["outcome"] == "cancelled"
    assert observed["exit_code"] == 130


def test_foreground_group_leader_sigint_cancels_observed_process_group(
    engine: Path, tmp_path: Path
) -> None:
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="kickoff",
        operation="phase",
    )
    started = tmp_path / "leader-child-started"
    descendant_finished = tmp_path / "leader-descendant-finished"
    result_path = tmp_path / "leader-result.json"
    child_code = (
        "import pathlib,subprocess,sys,time;"
        f"pathlib.Path({str(started)!r}).write_text('ready');"
        "subprocess.Popen([sys.executable,'-c',"
        f'"import pathlib,time;time.sleep(1);'
        f"pathlib.Path({str(descendant_finished)!r}).write_text('bad')\"]);"
        "time.sleep(30)"
    )
    command = [
        sys.executable,
        str(CLI),
        "run",
        "--repo-root",
        str(engine),
        "--trace-id",
        root.trace_id,
        "--parent-span-id",
        root.span_id,
        "--category",
        "gate",
        "--operation",
        "leader-cancel-command",
        "--result-json",
        str(result_path),
        "--",
        sys.executable,
        "-c",
        child_code,
    ]
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    for _ in range(100):
        if started.exists():
            break
        threading.Event().wait(0.02)
    assert started.exists()
    process.send_signal(signal.SIGINT)
    stdout, stderr = process.communicate(timeout=10)

    assert process.returncode == 130, (stdout, stderr)
    envelope = json.loads(result_path.read_text(encoding="utf-8"))
    assert envelope["outcome"] == "cancelled"
    threading.Event().wait(1.2)
    assert not descendant_finished.exists()
    bundle = finish_trace(engine, root)
    observed = span_by_operation(bundle, "leader-cancel-command")
    assert (observed["outcome"], observed["exit_code"]) == ("cancelled", 130)


def test_group_termination_reaches_descendant_after_leader_has_exited(
    tmp_path: Path,
) -> None:
    descendant_started = tmp_path / "exited-leader-descendant-started"
    descendant_finished = tmp_path / "exited-leader-descendant-finished"
    descendant_code = (
        "import pathlib,time;"
        f"pathlib.Path({str(descendant_started)!r}).touch();"
        "time.sleep(1);"
        f"pathlib.Path({str(descendant_finished)!r}).touch()"
    )
    leader_code = (
        f"import subprocess,sys;subprocess.Popen([sys.executable,'-c',{descendant_code!r}])"
    )
    process = subprocess.Popen(
        [sys.executable, "-c", leader_code],
        start_new_session=True,
    )
    try:
        process.wait(timeout=10)
        for _ in range(100):
            if descendant_started.exists():
                break
            threading.Event().wait(0.02)
        assert descendant_started.exists()

        telemetry._terminate_group(process)
        threading.Event().wait(1.2)
        assert not descendant_finished.exists()
    finally:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def test_group_termination_escalates_when_descendant_ignores_sigterm(
    tmp_path: Path,
) -> None:
    descendant_started = tmp_path / "sigterm-ignoring-descendant-started"
    descendant_finished = tmp_path / "sigterm-ignoring-descendant-finished"
    descendant_code = (
        "import pathlib,signal,time;"
        "signal.signal(signal.SIGTERM,signal.SIG_IGN);"
        f"pathlib.Path({str(descendant_started)!r}).touch();"
        "time.sleep(3);"
        f"pathlib.Path({str(descendant_finished)!r}).touch()"
    )
    leader_code = (
        "import subprocess,sys,time;"
        f"subprocess.Popen([sys.executable,'-c',{descendant_code!r}]);"
        "time.sleep(30)"
    )
    process = subprocess.Popen(
        [sys.executable, "-c", leader_code],
        start_new_session=True,
    )
    try:
        for _ in range(100):
            if descendant_started.exists():
                break
            threading.Event().wait(0.02)
        assert descendant_started.exists()

        telemetry._terminate_group(process)
        threading.Event().wait(3.2)
        assert not descendant_finished.exists()
    finally:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)


def test_non_main_thread_observed_command_is_explicit_and_non_leaking(
    engine: Path, tmp_path: Path
) -> None:
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="kickoff",
        operation="phase",
    )
    command_ran = tmp_path / "thread-command-ran"
    failures: list[BaseException] = []

    def invoke() -> None:
        try:
            telemetry.run_observed(
                engine_root=engine,
                trace_id=root.trace_id,
                parent_span_id=root.span_id,
                category="gate",
                operation="thread-command",
                argv=[
                    sys.executable,
                    "-c",
                    f"from pathlib import Path;Path({str(command_ran)!r}).touch()",
                ],
            )
        except BaseException as exc:
            failures.append(exc)

    worker = threading.Thread(target=invoke)
    worker.start()
    worker.join(timeout=10)

    assert not worker.is_alive()
    assert len(failures) == 1
    assert isinstance(failures[0], telemetry.ValidationError)
    assert "main thread" in str(failures[0]).lower()
    assert not command_ran.exists()
    runtime = telemetry.validate_runtime_trace(engine_root=engine, trace_id=root.trace_id)
    assert runtime["span_count"] == 1
    finish_trace(engine, root)


@pytest.mark.parametrize("timeout_seconds", [0.0, -0.1, float("nan"), float("inf")])
def test_library_rejects_invalid_timeout_before_span_or_process(
    engine: Path, tmp_path: Path, timeout_seconds: float
) -> None:
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope_id="engine",
        scope="engine",
        run_type="kickoff",
        operation="phase",
    )
    command_ran = tmp_path / "invalid-library-timeout-ran"
    with pytest.raises(telemetry.ValidationError, match="finite|positive|timeout"):
        telemetry.run_observed(
            engine_root=engine,
            trace_id=root.trace_id,
            parent_span_id=root.span_id,
            category="gate",
            operation="invalid-timeout",
            argv=[
                sys.executable,
                "-c",
                f"from pathlib import Path;Path({str(command_ran)!r}).touch()",
            ],
            timeout_seconds=timeout_seconds,
        )
    assert not command_ran.exists()
    runtime = telemetry.validate_runtime_trace(engine_root=engine, trace_id=root.trace_id)
    assert runtime["span_count"] == 1
    finish_trace(engine, root)


@pytest.mark.parametrize("timeout_text", ["0", "-0.1", "nan", "inf"])
def test_cli_rejects_invalid_timeout_before_span_or_process(
    engine: Path, tmp_path: Path, timeout_text: str
) -> None:
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope_id="engine",
        scope="engine",
        run_type="kickoff",
        operation="phase",
    )
    command_ran = tmp_path / f"invalid-cli-timeout-{timeout_text}"
    result = cli(
        "run",
        "--repo-root",
        str(engine),
        "--trace-id",
        root.trace_id,
        "--parent-span-id",
        root.span_id,
        "--category",
        "gate",
        "--operation",
        "invalid-timeout",
        "--timeout-seconds",
        timeout_text,
        "--",
        sys.executable,
        "-c",
        f"from pathlib import Path;Path({str(command_ran)!r}).touch()",
    )
    assert result.returncode == 2
    assert result.stdout == ""
    assert "timeout" in result.stderr.lower()
    assert "Traceback" not in result.stderr
    assert not command_ran.exists()
    runtime = telemetry.validate_runtime_trace(engine_root=engine, trace_id=root.trace_id)
    assert runtime["span_count"] == 1
    finish_trace(engine, root)


@pytest.mark.parametrize("timeout_seconds", [1e308, 1.5e-9])
def test_library_rejects_inexact_or_overflowing_timeout_before_effects(
    engine: Path, tmp_path: Path, timeout_seconds: float
) -> None:
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope_id="engine",
        scope="engine",
        run_type="kickoff",
        operation="phase",
    )
    command_ran = tmp_path / "invalid-precise-library-timeout-ran"
    with pytest.raises(telemetry.ValidationError, match="timeout|nanosecond|finite"):
        telemetry.run_observed(
            engine_root=engine,
            trace_id=root.trace_id,
            parent_span_id=root.span_id,
            category="gate",
            operation="invalid-precise-timeout",
            argv=[
                sys.executable,
                "-c",
                f"from pathlib import Path;Path({str(command_ran)!r}).touch()",
            ],
            timeout_seconds=timeout_seconds,
        )
    assert not command_ran.exists()
    runtime = telemetry.validate_runtime_trace(engine_root=engine, trace_id=root.trace_id)
    assert runtime["span_count"] == 1
    finish_trace(engine, root)


@pytest.mark.parametrize("timeout_text", ["1e308", "0.0000000015"])
def test_cli_rejects_inexact_or_overflowing_timeout_before_effects(
    engine: Path, tmp_path: Path, timeout_text: str
) -> None:
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope_id="engine",
        scope="engine",
        run_type="kickoff",
        operation="phase",
    )
    command_ran = tmp_path / f"invalid-precise-cli-timeout-{timeout_text}"
    result = cli(
        "run",
        "--repo-root",
        str(engine),
        "--trace-id",
        root.trace_id,
        "--parent-span-id",
        root.span_id,
        "--category",
        "gate",
        "--operation",
        "invalid-precise-timeout",
        "--timeout-seconds",
        timeout_text,
        "--",
        sys.executable,
        "-c",
        f"from pathlib import Path;Path({str(command_ran)!r}).touch()",
    )
    assert result.returncode == 2
    assert result.stdout == ""
    assert "timeout" in result.stderr.lower()
    assert "Traceback" not in result.stderr
    assert not command_ran.exists()
    runtime = telemetry.validate_runtime_trace(engine_root=engine, trace_id=root.trace_id)
    assert runtime["span_count"] == 1
    finish_trace(engine, root)


def test_library_preserves_exact_integral_nanosecond_timeout(engine: Path) -> None:
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope_id="engine",
        scope="engine",
        run_type="kickoff",
        operation="phase",
    )
    result = telemetry.run_observed(
        engine_root=engine,
        trace_id=root.trace_id,
        parent_span_id=root.span_id,
        category="gate",
        operation="exact-timeout",
        argv=[sys.executable, "-c", "import time;time.sleep(1)"],
        timeout_seconds=2e-9,
    )
    assert (result.exit_code, result.outcome) == (124, "timeout")
    bundle = finish_trace(engine, root)
    observed = span_by_operation(bundle, "exact-timeout")
    assert observed["timeout_ns"] == 2


def test_cli_preserves_exact_integral_nanosecond_timeout(engine: Path, tmp_path: Path) -> None:
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope_id="engine",
        scope="engine",
        run_type="kickoff",
        operation="phase",
    )
    result_path = tmp_path / "exact-timeout-result.json"
    result = cli(
        "run",
        "--repo-root",
        str(engine),
        "--trace-id",
        root.trace_id,
        "--parent-span-id",
        root.span_id,
        "--category",
        "gate",
        "--operation",
        "exact-timeout",
        "--timeout-seconds",
        "0.000000002",
        "--result-json",
        str(result_path),
        "--",
        sys.executable,
        "-c",
        "import time;time.sleep(1)",
    )
    assert result.returncode == 124
    assert result.stdout == ""
    assert result.stderr == ""
    envelope = json.loads(result_path.read_text(encoding="utf-8"))
    assert (envelope["exit_code"], envelope["outcome"]) == (124, "timeout")
    bundle = finish_trace(engine, root)
    observed = span_by_operation(bundle, "exact-timeout")
    assert observed["timeout_ns"] == 2


def test_telemetry_failure_never_replaces_child_exit(engine: Path) -> None:
    result = telemetry.run_observed(
        engine_root=engine,
        trace_id="ffffffffffffffffffffffffffffffff",
        parent_span_id="eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
        category="gate",
        operation="unrecorded",
        argv=[sys.executable, "-c", "raise SystemExit(9)"],
    )
    assert result.exit_code == 9
    assert result.outcome == "error"
    assert result.telemetry_complete is False
    assert result.error_code == "span-start-failed"


def test_finish_telemetry_failure_does_not_replace_success(
    engine: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="kickoff",
        operation="phase",
    )

    def fail_finish(**_kwargs: object) -> None:
        raise telemetry.TelemetryError("injected")

    monkeypatch.setattr(telemetry, "finish_span", fail_finish)
    result = telemetry.run_observed(
        engine_root=engine,
        trace_id=root.trace_id,
        parent_span_id=root.span_id,
        category="gate",
        operation="command",
        argv=[sys.executable, "-c", "raise SystemExit(0)"],
    )
    assert result.exit_code == 0
    assert result.outcome == "success"
    assert result.telemetry_complete is False
    assert result.error_code == "span-finish-failed"


def test_cli_validate_and_text_json_reports_agree() -> None:
    validated = cli("validate", "--ledger", str(PARALLEL_FIXTURE))
    assert validated.returncode == 0
    assert json.loads(validated.stdout)["valid_traces"] == 1
    assert validated.stderr == ""

    json_report = cli("report", "--ledger", str(PARALLEL_FIXTURE), "--format", "json")
    text_report = cli("report", "--ledger", str(PARALLEL_FIXTURE), "--format", "text")
    assert json_report.returncode == text_report.returncode == 0
    [report] = json.loads(json_report.stdout)
    assert report["root_makespan_ns"] == 100
    assert report["concurrency_groups"]["parallel-review"]["summed_work_ns"] == 110
    assert "Root makespan: 100 ns" in text_report.stdout
    assert "110 ns summed work" in text_report.stdout
    assert "USAGE_LOG.md" in text_report.stdout
    assert "cycle-31.1" in text_report.stdout
    assert "planner" in text_report.stdout
    assert json_report.stderr == text_report.stderr == ""


def test_cli_validate_runtime_trace_is_read_only(engine: Path) -> None:
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="kickoff",
        operation="phase",
    )
    result = cli(
        "validate",
        "--repo-root",
        str(engine),
        "--trace-id",
        root.trace_id,
    )
    assert result.returncode == 0
    assert json.loads(result.stdout) == {
        "trace_id": root.trace_id,
        "valid": True,
        "span_count": 1,
        "open_span_count": 1,
    }
    assert not (engine / "EXECUTION_LOG.jsonl").exists()
    finish_trace(engine, root)


def test_cli_run_preserves_streams_and_writes_only_result_envelope(
    engine: Path, tmp_path: Path
) -> None:
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="kickoff",
        operation="phase",
    )
    result_path = tmp_path / "result.json"
    result = cli(
        "run",
        "--repo-root",
        str(engine),
        "--trace-id",
        root.trace_id,
        "--parent-span-id",
        root.span_id,
        "--category",
        "gate",
        "--operation",
        "stream-test",
        "--result-json",
        str(result_path),
        "--",
        sys.executable,
        "-c",
        "import sys;print('child-out');print('child-err', file=sys.stderr)",
    )
    assert result.returncode == 0
    assert result.stdout == "child-out\n"
    assert result.stderr == "child-err\n"
    envelope = json.loads(result_path.read_text(encoding="utf-8"))
    assert set(envelope) == {
        "trace_id",
        "span_id",
        "exit_code",
        "outcome",
        "telemetry_complete",
        "error_code",
    }
    assert envelope["exit_code"] == 0
    assert envelope["telemetry_complete"] is True
    finish_trace(engine, root)


def test_cli_malformed_ledger_fails_closed_without_traceback(tmp_path: Path) -> None:
    ledger = tmp_path / "bad.jsonl"
    ledger.write_text('{"schema":"wrong"}\n', encoding="utf-8")
    result = cli("validate", "--ledger", str(ledger))
    assert result.returncode == 2
    assert result.stdout == ""
    assert "invalid ledger row 1" in result.stderr
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize(
    ("ledger_bytes", "match"),
    [
        (
            PARALLEL_FIXTURE.read_bytes().removesuffix(b"\n"),
            "unterminated|newline|framing",
        ),
        (b"\xff\n", "utf-8|encoding|decode"),
    ],
)
def test_finalize_rejects_invalid_jsonl_framing_or_encoding_without_append(
    engine: Path, ledger_bytes: bytes, match: str
) -> None:
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="kickoff",
        operation="phase",
    )
    telemetry.finish_span(
        engine_root=engine,
        trace_id=root.trace_id,
        span_id=root.span_id,
        outcome="success",
    )
    ledger = engine / "EXECUTION_LOG.jsonl"
    ledger.write_bytes(ledger_bytes)

    with pytest.raises(telemetry.ValidationError, match=match):
        telemetry.finalize_trace(engine_root=engine, trace_id=root.trace_id)
    assert ledger.read_bytes() == ledger_bytes
    assert not (trace_dir(engine, root.trace_id) / "finalized.json").exists()


@pytest.mark.parametrize(
    ("ledger_bytes", "match"),
    [
        (
            PARALLEL_FIXTURE.read_bytes().removesuffix(b"\n"),
            "unterminated|newline|framing",
        ),
        (b"\xff\n", "utf-8|encoding|decode"),
    ],
)
def test_cli_finalize_rejects_invalid_jsonl_without_traceback_or_append(
    engine: Path, ledger_bytes: bytes, match: str
) -> None:
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="kickoff",
        operation="phase",
    )
    telemetry.finish_span(
        engine_root=engine,
        trace_id=root.trace_id,
        span_id=root.span_id,
        outcome="success",
    )
    ledger = engine / "EXECUTION_LOG.jsonl"
    ledger.write_bytes(ledger_bytes)

    result = cli(
        "finalize",
        "--repo-root",
        str(engine),
        "--trace-id",
        root.trace_id,
    )
    assert result.returncode == 2
    assert result.stdout == ""
    assert re.search(match, result.stderr, re.IGNORECASE)
    assert "Traceback" not in result.stderr
    assert ledger.read_bytes() == ledger_bytes
    assert not (trace_dir(engine, root.trace_id) / "finalized.json").exists()


@pytest.mark.parametrize("command", ["validate", "report"])
@pytest.mark.parametrize(
    ("ledger_bytes", "match"),
    [
        (
            PARALLEL_FIXTURE.read_bytes().removesuffix(b"\n"),
            "unterminated|newline|framing",
        ),
        (b"\xff\n", "utf-8|encoding|decode"),
    ],
)
def test_cli_ledger_readers_reject_invalid_jsonl_without_traceback(
    tmp_path: Path, command: str, ledger_bytes: bytes, match: str
) -> None:
    ledger = tmp_path / f"{command}-bad.jsonl"
    ledger.write_bytes(ledger_bytes)
    result = cli(command, "--ledger", str(ledger))

    assert result.returncode == 2
    assert result.stdout == ""
    assert re.search(match, result.stderr, re.IGNORECASE)
    assert "Traceback" not in result.stderr


def test_kickoff_read_helpers_reconcile_runtime_and_durable_bundle(engine: Path) -> None:
    clock = FakeClock()
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="kickoff",
        operation="phase.31.2",
        clock=clock,
    )
    child = telemetry.start_span(
        engine_root=engine,
        trace_id=root.trace_id,
        parent_span_id=root.span_id,
        category="gate",
        operation="gate.focused",
        clock=clock,
    )
    clock.advance(7)
    telemetry.finish_span(
        engine_root=engine,
        trace_id=root.trace_id,
        span_id=child.span_id,
        outcome="success",
        exit_code=0,
        clock=clock,
    )
    assert telemetry.trace_context(engine_root=engine, trace_id=root.trace_id) == {
        "trace_id": root.trace_id,
        "root_span_id": root.span_id,
        "scope": "engine",
        "scope_id": "engine",
        "run_type": "kickoff",
        "operation": "phase.31.2",
        "state": "open",
    }
    assert (
        telemetry.closed_span(engine_root=engine, trace_id=root.trace_id, span_id=child.span_id)[
            "duration_ns"
        ]
        == 7
    )
    assert [
        item["span_id"]
        for item in telemetry.closed_spans(engine_root=engine, trace_id=root.trace_id)
    ] == [child.span_id]
    clock.advance(3)
    telemetry.finish_span(
        engine_root=engine,
        trace_id=root.trace_id,
        span_id=root.span_id,
        outcome="success",
        clock=clock,
    )
    expected = telemetry.finalize_trace(engine_root=engine, trace_id=root.trace_id, clock=clock)
    assert telemetry.finalized_trace(engine_root=engine, trace_id=root.trace_id) == expected


def test_closed_span_rejects_open_root_and_child_without_cli_traceback(
    engine: Path,
) -> None:
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="kickoff",
        operation="phase.31.2",
    )
    child = telemetry.start_span(
        engine_root=engine,
        trace_id=root.trace_id,
        parent_span_id=root.span_id,
        category="gate",
        operation="gate.focused",
    )
    for span_id in (root.span_id, child.span_id):
        with pytest.raises(telemetry.IncompleteTraceError, match="still open"):
            telemetry.closed_span(engine_root=engine, trace_id=root.trace_id, span_id=span_id)
        result = cli(
            "span",
            "--repo-root",
            str(engine),
            "--trace-id",
            root.trace_id,
            "--span-id",
            span_id,
        )
        assert result.returncode == 2
        assert "still open" in result.stderr
        assert "Traceback" not in result.stderr


def test_category_totals_are_exclusive_for_nested_spans(engine: Path) -> None:
    clock = FakeClock(monotonic=0)
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="improve-engine",
        operation="cycle.improve-engine",
        clock=clock,
    )
    intelligence = telemetry.start_span(
        engine_root=engine,
        trace_id=root.trace_id,
        parent_span_id=root.span_id,
        category="intelligence",
        operation="role.maintainer",
        clock=clock,
    )
    clock.advance(10)
    gate = telemetry.start_span(
        engine_root=engine,
        trace_id=root.trace_id,
        parent_span_id=intelligence.span_id,
        category="gate",
        operation="gate.focused",
        clock=clock,
    )
    clock.advance(20)
    telemetry.finish_span(
        engine_root=engine,
        trace_id=root.trace_id,
        span_id=gate.span_id,
        outcome="success",
        exit_code=0,
        clock=clock,
    )
    clock.advance(20)
    telemetry.finish_span(
        engine_root=engine,
        trace_id=root.trace_id,
        span_id=intelligence.span_id,
        outcome="success",
        exit_code=0,
        clock=clock,
    )
    clock.advance(10)
    bundle = finish_trace(engine, root, clock=clock)
    report = telemetry.aggregate_trace(bundle)
    assert report["category_coverage_ns"]["intelligence"] == 30
    assert report["category_coverage_ns"]["gate"] == 20
    assert (
        sum(report["category_coverage_ns"].values()) + report["unattributed_ns"]
        == report["root_makespan_ns"]
    )
    assert report["root_operation"] == "cycle.improve-engine"


def test_cross_scope_checkpoint_links_keep_outer_and_child_work_separate(
    engine: Path,
) -> None:
    (engine / "projects/demo").mkdir(parents=True)
    (engine / "projects/port-assignments.yaml").write_text("demo:\n")
    clock = FakeClock(monotonic=0)
    checkpoint = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="checkpoint",
        operation="checkpoint.catalog",
        batch_id="feedbeef",
        clock=clock,
    )
    outer_child = telemetry.start_span(
        engine_root=engine,
        trace_id=checkpoint.trace_id,
        parent_span_id=checkpoint.span_id,
        category="intelligence",
        operation="checkpoint.cycle.ab12cd34",
        batch_id="feedbeef",
        clock=clock,
    )
    clock.advance(40)
    telemetry.finish_span(
        engine_root=engine,
        trace_id=checkpoint.trace_id,
        span_id=outer_child.span_id,
        outcome="success",
        exit_code=0,
        clock=clock,
    )
    clock.advance(10)
    finish_trace(engine, checkpoint, clock=clock)

    expected = telemetry.expect_managed_run(
        engine_root=engine,
        scope="project",
        scope_id="demo",
        run_type="improve",
        operation="cycle.improve",
        cycle_id="ab12cd34",
        batch_id="feedbeef",
    )
    child_clock = FakeClock(monotonic=0)
    child = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine / "projects/demo",
        scope="project",
        scope_id="demo",
        run_type="improve",
        operation="cycle.improve",
        batch_id="feedbeef",
        clock=child_clock,
    )
    telemetry.bind_expected_trace(
        engine_root=engine,
        run_id=expected["run_id"],
        trace_id=child.trace_id,
        root_span_id=child.span_id,
    )
    child_clock.advance(30)
    finish_trace(engine, child, clock=child_clock)
    telemetry.mark_expected_finalized(engine_root=engine, run_id=expected["run_id"])
    telemetry.mark_expected_persisted(engine_root=engine, run_id=expected["run_id"])

    report_set = telemetry.report_across_scopes(engine, batch_id="feedbeef")
    [link] = report_set["checkpoint_links"]
    assert link["outer_makespan_ns"] == 50
    assert link["summed_child_work_ns"] == 30
    assert link["missing_child_cycles"] == []
    assert link["child_traces"][0]["trace_id"] == child.trace_id


def test_recent_applies_once_across_finalized_and_incomplete_runs(
    engine: Path,
) -> None:
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="improve-engine",
        operation="cycle.improve-engine",
    )
    finish_trace(engine, root)
    telemetry.expect_managed_run(
        engine_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="improve-engine",
        operation="cycle.improve-engine",
        cycle_id="ab12cd34",
    )
    report_set = telemetry.report_across_scopes(engine, recent=1)
    assert (len(report_set["reports"]) + len(report_set["incomplete_runs"])) == 1
    assert report_set["incomplete_runs"][0]["cycle_id"] == "ab12cd34"


class TestBootIdentityDrift:
    """Boot identity must survive clock discipline but not a real reboot.

    macOS derives `kern.boottime` as (now - uptime) rather than storing it, so
    every read recomputes it and the value drifts as the clock is disciplined.
    Across two days of one uninterrupted boot the `usec` field moved
    393666 -> 309306, and raw string comparison then rejected the trace:
    `recover` and `finish` both raised ClockDomainError on a machine that had
    never rebooted, which made a long-lived trace impossible to finalize.

    That is a check comparing a moving reference -- it could only ever say
    "different boot" once a trace outlived a clock adjustment.
    """

    REAL_RECORDED = "{ sec = 1785000109, usec = 393666 } Sat Jul 25 11:21:49 2026"
    REAL_SAMPLED = "{ sec = 1785000109, usec = 309306 } Sat Jul 25 11:21:49 2026"

    def test_the_observed_drift_is_the_same_boot(self) -> None:
        from agentic_starter.execution_telemetry import same_boot

        assert same_boot(self.REAL_RECORDED, self.REAL_SAMPLED)

    def test_a_real_reboot_is_still_a_different_boot(self) -> None:
        """Tolerance must not swallow an actual restart."""
        from agentic_starter.execution_telemetry import same_boot

        later = "{ sec = 1785200000, usec = 1 } Mon Jul 27 18:53:20 2026"
        assert not same_boot(self.REAL_RECORDED, later)

    def test_tolerance_is_seconds_not_minutes(self) -> None:
        """A reboot within the tolerance window would be indistinguishable.

        Keep the window small enough that only clock discipline fits inside it.
        """
        from agentic_starter.execution_telemetry import (
            BOOT_ID_DRIFT_TOLERANCE_SECONDS,
            same_boot,
        )

        assert 0 < BOOT_ID_DRIFT_TOLERANCE_SECONDS <= 10
        base = 1785000109
        inside = f"{{ sec = {base + BOOT_ID_DRIFT_TOLERANCE_SECONDS}, usec = 1 }}"
        outside = f"{{ sec = {base + BOOT_ID_DRIFT_TOLERANCE_SECONDS + 1}, usec = 1 }}"
        anchor = f"{{ sec = {base}, usec = 1 }}"
        assert same_boot(anchor, inside)
        assert not same_boot(anchor, outside)

    def test_non_darwin_identities_compare_exactly(self) -> None:
        """Linux's /proc boot_id is a stable UUID; it must not gain a tolerance."""
        from agentic_starter.execution_telemetry import boot_seconds, same_boot

        uuid = "6f1a1c1e-1f2b-4c3d-8e4f-5a6b7c8d9e0f"
        assert boot_seconds(uuid) is None
        assert same_boot(uuid, uuid)
        assert not same_boot(uuid, "6f1a1c1e-1f2b-4c3d-8e4f-5a6b7c8d9e00")

    def test_unparseable_identity_never_silently_matches(self) -> None:
        from agentic_starter.execution_telemetry import same_boot

        assert not same_boot("", self.REAL_RECORDED)
        assert not same_boot("garbage", self.REAL_RECORDED)


def test_recovery_survives_darwin_boottime_drift(engine: Path) -> None:
    """The real defect, at the real call site.

    A trace started when `kern.boottime` read `usec = 393666` must still recover
    after the clock is disciplined and the same boot reads `usec = 309306`.
    Before the fix this raised ClockDomainError and the trace could never be
    finalized, so `timing-summary` was permanently unavailable for any run that
    outlived a clock adjustment.

    This exercises `recover_trace` rather than `same_boot` directly: the unit
    tests still pass with the call site reverted to raw string comparison, so
    they cannot detect the defect that actually bit.
    """
    started = FakeClock(boot="{ sec = 1785000109, usec = 393666 } Sat Jul 25 11:21:49 2026")
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="kickoff",
        operation="phase.test",
        clock=started,
    )
    started.advance(10)
    telemetry.start_span(
        engine_root=engine,
        trace_id=root.trace_id,
        parent_span_id=root.span_id,
        category="gate",
        operation="gate.acceptance.check-all",
        clock=started,
    )

    drifted = FakeClock(
        boot="{ sec = 1785000109, usec = 309306 } Sat Jul 25 11:21:49 2026",
        monotonic=started.monotonic + 10,
    )
    bundle = telemetry.recover_trace(engine_root=engine, trace_id=root.trace_id, clock=drifted)
    assert bundle["root_span_id"] == root.span_id
    assert bundle["finalized_at"]


def test_recovery_still_refuses_a_genuine_reboot(engine: Path) -> None:
    """The tolerance must not turn a real restart into a recoverable trace."""
    started = FakeClock(boot="{ sec = 1785000109, usec = 1 } Sat Jul 25 11:21:49 2026")
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="kickoff",
        operation="phase.test",
        clock=started,
    )
    rebooted = FakeClock(boot="{ sec = 1785200000, usec = 1 } Mon Jul 27 18:53:20 2026")
    with pytest.raises(telemetry.ClockDomainError):
        telemetry.recover_trace(engine_root=engine, trace_id=root.trace_id, clock=rebooted)


def test_finish_keeps_stdout_clear_for_the_next_span_id(
    engine: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """CH-5: `close A, open B, capture B's span id` must capture one blob.

    `start` prints the handle a caller has to keep; `finish` prints only a
    confirmation. With both on stdout the ordinary helper that closes one
    orchestration stage and opens the next captures two JSON documents and binds
    the wrong span — it cost exactly one bad span-id capture in a real run.
    """
    monkeypatch.setenv("AGENTIC_STARTER_EXECUTION_TELEMETRY_DIR", str(tmp_path / "spool"))
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="kickoff",
        operation="phase.1.1",
    )
    span = telemetry.start_span(
        engine_root=engine,
        trace_id=root.trace_id,
        parent_span_id=root.span_id,
        category="reconciliation",
        operation="orchestration.setup",
    )

    finished = subprocess.run(
        [
            sys.executable,
            str(CLI),
            "finish",
            "--repo-root",
            str(engine),
            "--trace-id",
            root.trace_id,
            "--span-id",
            span.span_id,
            "--outcome",
            "success",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert finished.returncode == 0, finished.stderr
    assert finished.stdout == "", "finish must leave stdout for the caller's capture"
    assert span.span_id in finished.stderr
    assert "closed" in finished.stderr


def test_finish_still_offers_the_machine_readable_confirmation(
    engine: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Routed away by default, not removed: `--json` restores it on stdout."""
    monkeypatch.setenv("AGENTIC_STARTER_EXECUTION_TELEMETRY_DIR", str(tmp_path / "spool"))
    root = telemetry.start_trace(
        engine_root=engine,
        scope_root=engine,
        scope="engine",
        scope_id="engine",
        run_type="kickoff",
        operation="phase.1.1",
    )
    span = telemetry.start_span(
        engine_root=engine,
        trace_id=root.trace_id,
        parent_span_id=root.span_id,
        category="reconciliation",
        operation="orchestration.setup",
    )

    finished = subprocess.run(
        [
            sys.executable,
            str(CLI),
            "finish",
            "--repo-root",
            str(engine),
            "--trace-id",
            root.trace_id,
            "--span-id",
            span.span_id,
            "--outcome",
            "success",
            "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert finished.returncode == 0, finished.stderr
    payload = json.loads(finished.stdout)
    assert payload["span_id"] == span.span_id
    assert payload["state"] == "closed"
