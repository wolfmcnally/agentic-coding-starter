from __future__ import annotations

import datetime as dt
import json
import os
import signal
import stat
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any

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
PARK_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "execution_telemetry" / "phase-parks.jsonl"


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


def test_operator_park_open_close_is_idempotent_exact_and_fail_closed(
    engine: Path,
) -> None:
    clock = FakeClock()
    opened = telemetry.open_operator_park(
        engine_root=engine, phase_id="3.2", reason="decision", clock=clock
    )
    repeated = telemetry.open_operator_park(
        engine_root=engine, phase_id="3.2", reason="decision", clock=clock
    )
    assert repeated == opened
    with pytest.raises(telemetry.ValidationError, match="different reason"):
        telemetry.open_operator_park(
            engine_root=engine, phase_id="3.2", reason="approval", clock=clock
        )
    open_summary = telemetry.phase_park_summary(engine_root=engine, phase_id="3.2")
    assert open_summary["open"] is True
    assert open_summary["total_duration_ns"] is None

    clock.advance(7_000_000_000)
    closed = telemetry.close_operator_park(
        engine_root=engine, phase_id="3.2", park_id=opened.park_id, clock=clock
    )
    assert closed["duration_ns"] == 7_000_000_000
    assert closed["exact"] is True
    assert closed["method"] == "monotonic"
    assert (
        telemetry.close_operator_park(
            engine_root=engine, phase_id="3.2", park_id=opened.park_id, clock=clock
        )
        == closed
    )
    with pytest.raises(telemetry.ValidationError, match="no open"):
        telemetry.close_operator_park(engine_root=engine, phase_id="3.2", clock=clock)


def test_operator_park_recovers_missing_runtime_state_and_marks_cross_boot(
    engine: Path,
) -> None:
    clock = FakeClock()
    opened = telemetry.open_operator_park(
        engine_root=engine, phase_id="4", reason="required-input", clock=clock
    )
    telemetry._park_state_path(engine, "4").unlink()
    assert (
        telemetry.open_operator_park(
            engine_root=engine, phase_id="4", reason="required-input", clock=clock
        )
        == opened
    )

    clock.boot = "next-boot"
    clock.utc += dt.timedelta(seconds=9)
    clock.monotonic = 100
    closed = telemetry.close_operator_park(
        engine_root=engine, phase_id="4", park_id=opened.park_id, clock=clock
    )
    assert closed["duration_ns"] == 9_000_000_000
    assert closed["exact"] is False
    assert closed["method"] == "calendar-cross-boot"


def test_operator_park_exact_intervals_union_overlaps(engine: Path, tmp_path: Path) -> None:
    ledger = tmp_path / "parks.jsonl"
    events = telemetry.validate_park_ledger(PARK_FIXTURE)[:4]
    payload = "".join(
        json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n" for event in events
    )
    ledger.write_text(
        payload,
        encoding="utf-8",
    )
    summary = telemetry.phase_park_summary(engine_root=engine, phase_id="7", ledger=ledger)
    assert summary["total_duration_ns"] == 15_000_000_000
    assert summary["total_exact"] is True
    assert summary["total_method"] == "monotonic-union"


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


def test_cli_malformed_ledger_fails_closed_without_traceback(tmp_path: Path) -> None:
    ledger = tmp_path / "bad.jsonl"
    ledger.write_text('{"schema":"wrong"}\n', encoding="utf-8")
    result = cli("validate", "--ledger", str(ledger))
    assert result.returncode == 2
    assert result.stdout == ""
    assert "invalid ledger row 1" in result.stderr
    assert "Traceback" not in result.stderr
