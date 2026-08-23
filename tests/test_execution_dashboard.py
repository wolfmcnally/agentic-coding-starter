from __future__ import annotations

import contextlib
import copy
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))

from agentic_starter import execution_dashboard as dashboard  # noqa: E402
from agentic_starter import execution_telemetry as telemetry  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "execution_telemetry" / "kickoff-trace.jsonl"
PARK_FIXTURE = ROOT / "tests" / "fixtures" / "execution_telemetry" / "phase-parks.jsonl"
SERVER = ROOT / "bin" / "serve-execution-dashboard"
CLI = ROOT / "bin" / "execution-telemetry"
ECHARTS_SHA256 = "b66b25aeb4df84e33199dc21694014d336d222cbd9deb0e5a7c14bd6aa0d0fd0"


def kickoff_bundle() -> dict[str, Any]:
    [bundle] = telemetry.validate_ledger(FIXTURE)
    return bundle


def test_vendored_echarts_is_the_complete_pinned_release() -> None:
    chart_library = ROOT / "reports" / "execution" / "assets" / "echarts-6.1.0.min.js"

    assert hashlib.sha256(chart_library.read_bytes()).hexdigest() == ECHARTS_SHA256


def sample_handoff(phase_id: str = "31.2") -> dict[str, Any]:
    return {
        "schema": dashboard.HANDOFF_SCHEMA,
        "phase_id": phase_id,
        "what_just_landed": [
            {"title": "Exact timing", "detail": "Managed work now reports measured duration."}
        ],
        "see_for_yourself": [
            {
                "title": "Inspect the report",
                "steps": ["Run ./bin/python bin/execution-telemetry report --recent 1"],
                "expected": "The accepted trace appears with exclusive category coverage.",
            }
        ],
        "coming_up_next": {
            "phase_id": "31.3",
            "title": "Managed-loop integration",
            "summary": "Extend exact telemetry to the remaining managed loops.",
        },
        "recommended_steps": [
            {
                "title": "No prerequisite",
                "detail": "The next kickoff can begin immediately.",
                "kind": "ready",
            }
        ],
    }


def failed_predecessor(bundle: dict[str, Any]) -> dict[str, Any]:
    failed = copy.deepcopy(bundle)
    trace_id = "30000000000040008000000000000000"
    id_map = {
        span["span_id"]: f"300000000000400080000000000000{index:02x}"
        for index, span in enumerate(failed["spans"], start=1)
    }
    failed["trace_id"] = trace_id
    failed["finalized_at"] = "2026-07-28T11:59:59.000000Z"
    failed["root_span_id"] = id_map[failed["root_span_id"]]
    for span in failed["spans"]:
        span["trace_id"] = trace_id
        span["span_id"] = id_map[span["span_id"]]
        if span["parent_span_id"] is not None:
            span["parent_span_id"] = id_map[span["parent_span_id"]]
    root = next(span for span in failed["spans"] if span["parent_span_id"] is None)
    root["outcome"] = "error"
    return telemetry.validate_bundle(failed)


def gate_only_recovery(bundle: dict[str, Any]) -> dict[str, Any]:
    recovery = copy.deepcopy(bundle)
    trace_id = "40000000000040008000000000000000"
    root = next(span for span in recovery["spans"] if span["parent_span_id"] is None)
    gate = next(span for span in recovery["spans"] if span["operation"] == "gate.check-all")
    root_id = "40000000000040008000000000000001"
    gate_id = "40000000000040008000000000000002"
    recovery["trace_id"] = trace_id
    recovery["root_span_id"] = root_id
    recovery["finalized_at"] = "2026-07-28T12:00:02.000000Z"
    root.update(
        {
            "trace_id": trace_id,
            "span_id": root_id,
            "started_at": "2026-07-28T12:00:01.000000Z",
            "ended_at": "2026-07-28T12:00:01.000001Z",
        }
    )
    gate.update(
        {
            "trace_id": trace_id,
            "span_id": gate_id,
            "parent_span_id": root_id,
            "started_at": "2026-07-28T12:00:01.000000Z",
            "ended_at": "2026-07-28T12:00:01.000000Z",
        }
    )
    recovery["spans"] = [root, gate]
    return telemetry.validate_bundle(recovery)


def write_ledger(engine: Path, bundles: list[dict[str, Any]]) -> None:
    engine.mkdir()
    (engine / "projects").mkdir()
    (engine / "policies").mkdir()
    (engine / "CLAUDE.md").write_text("# fixture\n", encoding="utf-8")
    (engine / "EXECUTION_LOG.jsonl").write_text(
        "".join(
            json.dumps(bundle, sort_keys=True, separators=(",", ":")) + "\n" for bundle in bundles
        ),
        encoding="utf-8",
    )


def test_payload_includes_failed_primary_and_exact_exclusive_accounting() -> None:
    primary = kickoff_bundle()
    accepted = gate_only_recovery(primary)
    payload = dashboard.build_phase_payload(
        [failed_predecessor(primary), accepted],
        phase_id="31.2",
        accepted_trace_id=accepted["trace_id"],
        handoff=sample_handoff(),
    )

    assert payload["schema"] == dashboard.DASHBOARD_SCHEMA
    assert payload["trace_count"] == 2
    assert payload["failed_trace_count"] == 1
    assert payload["operator_parks"] == {
        "phase_id": "31.2",
        "intervals": [],
        "total_duration_ns": 0,
        "total_exact": True,
        "total_method": "none",
        "open": False,
    }
    assert [item["trace_status"] for item in payload["traces"]] == [
        "unsuccessful",
        "accepted",
    ]
    trace = next(item for item in payload["traces"] if item["accepted"])
    assert (
        sum(trace["category_coverage_ns"].values()) + trace["unattributed_ns"]
        == trace["makespan_ns"]
    )
    assert all("token_reference" not in span for span in trace["spans"])
    assert "token" not in json.dumps(payload).lower()
    phase = payload["phase_view"]
    assert phase["view_type"] == "phase"
    assert phase["trace_count"] == 2
    assert [item["role"] for item in phase["role_breakdown"]] == [
        "planner",
        "reviewer",
        "coder",
        "critic",
    ]
    assert phase["category_coverage_ns"]["intelligence"] > 0
    assert phase["category_coverage_ns"]["wait"] == 0
    assert {item["operation"] for item in phase["gate_breakdown"]} == {
        "gate.focused",
        "gate.check-all",
    }
    assert phase["role_attempt_count"] == sum(
        item["attempt_count"] for item in phase["role_breakdown"]
    )
    assert phase["role_followup_count"] == sum(
        max(0, item["attempt_count"] - 1) for item in phase["role_breakdown"]
    )
    assert [item["label"] for item in phase["role_breakdown"]] == [
        "Planning",
        "Plan Review",
        "Implementation",
        "Code Review",
    ]
    assert phase["gate_run_count"] == sum(item["attempt_count"] for item in phase["gate_breakdown"])
    assert phase["failed_gate_count"] == sum(
        item["failed_attempts"] for item in phase["gate_breakdown"]
    )
    assert (
        sum(phase["category_coverage_ns"].values()) + phase["unattributed_ns"]
        == phase["makespan_ns"]
    )


def test_payload_reports_each_operator_park_and_nonexact_total() -> None:
    accepted = kickoff_bundle()
    parks = telemetry.phase_park_summary(engine_root=ROOT, phase_id="7", ledger=PARK_FIXTURE)
    parks = parks | {
        "phase_id": "31.2",
        "intervals": [item | {"phase_id": "31.2"} for item in parks["intervals"]],
    }
    payload = dashboard.build_phase_payload(
        [accepted],
        phase_id="31.2",
        accepted_trace_id=accepted["trace_id"],
        handoff=sample_handoff(),
        operator_parks=parks,
    )

    assert payload["operator_parks"] == parks
    assert payload["phase_view"]["operator_parks"] == parks
    assert payload["operator_parks"]["total_duration_ns"] == 75_000_000_000
    assert payload["operator_parks"]["total_exact"] is False
    assert "boot_id" not in json.dumps(payload["operator_parks"])


def test_renderer_disables_decorative_graph_styling_and_uses_semantic_rework() -> None:
    renderer = (ROOT / "reports" / "execution" / "assets" / "dashboard-v4.js").read_text(
        encoding="utf-8"
    )

    assert "decal: {show: false}" in renderer
    assert "borderColor" not in renderer
    assert "borderWidth" not in renderer
    assert "lineWidth" not in renderer
    assert "lineDash" not in renderer
    assert "Failures and retries" not in renderer
    assert "Where the Build Time Went" in renderer
    assert "Build Timeline" in renderer
    assert "Orchestration / Unmeasured" in renderer
    assert "wait mirrors" in renderer
    assert "source_trace_id.slice" not in renderer
    assert "Orchestrator waiting" not in renderer
    assert "Review Convergence" in renderer
    assert "Setup & Coordination" in renderer
    assert "Acceptance Coordination" in renderer
    assert "Awaiting User Input" in renderer
    assert "calendar union · non-exact" in renderer
    assert "specificKeys.size ? specificKeys : stageKeys" in renderer


def test_renderer_uses_minutes_for_every_elapsed_time_axis() -> None:
    renderer = (ROOT / "reports" / "execution" / "assets" / "dashboard-v4.js").read_text(
        encoding="utf-8"
    )

    assert "const nsToMinutes" in renderer
    assert renderer.count("axisLabel: {formatter: axisMinutes}") == 5
    assert 'name: "Minutes"' in renderer
    assert 'name: "Elapsed Minutes"' in renderer
    assert "Elapsed seconds" not in renderer
    assert 'name: "Seconds"' not in renderer
    assert "axisDuration" not in renderer


def test_renderer_accepts_the_generator_schema_names() -> None:
    renderer = (ROOT / "reports" / "execution" / "assets" / "dashboard-v4.js").read_text(
        encoding="utf-8"
    )

    assert f'phaseData.schema !== "{dashboard.DASHBOARD_SCHEMA}"' in renderer
    assert f'indexData.schema !== "{dashboard.INDEX_SCHEMA}"' in renderer


def test_payload_projects_review_convergence_without_historical_backfill() -> None:
    historical = kickoff_bundle()
    historical_payload = dashboard.build_phase_payload(
        [historical],
        phase_id="31.2",
        accepted_trace_id=historical["trace_id"],
        handoff=sample_handoff(),
    )
    assert "review_convergence" not in historical_payload["phase_view"]

    measured = copy.deepcopy(historical)
    reviewer = next(span for span in measured["spans"] if span.get("role") == "reviewer")
    critic = next(span for span in measured["spans"] if span.get("role") == "critic")
    reviewer.update(findings_reported=3, actionable_findings=2)
    critic.update(findings_reported=2, actionable_findings=0)
    measured = telemetry.validate_bundle(measured)
    payload = dashboard.build_phase_payload(
        [measured],
        phase_id="31.2",
        accepted_trace_id=measured["trace_id"],
        handoff=sample_handoff(),
    )

    assert payload["phase_view"]["review_convergence"] == [
        {
            "role": "reviewer",
            "label": "Plan Review",
            "pass": 1,
            "findings_reported": 3,
            "actionable_findings": 2,
            "duration_ns": reviewer["duration_ns"],
            "outcome": "success",
        },
        {
            "role": "critic",
            "label": "Code Review",
            "pass": 1,
            "findings_reported": 2,
            "actionable_findings": 0,
            "duration_ns": critic["duration_ns"],
            "outcome": "success",
        },
    ]


def test_gate_breakdown_assigns_parent_only_its_exclusive_remainder() -> None:
    accepted = copy.deepcopy(kickoff_bundle())
    parent = next(span for span in accepted["spans"] if span["operation"] == "gate.check-all")
    child = copy.deepcopy(parent)
    child.update(
        {
            "span_id": "50000000000040008000000000000001",
            "parent_span_id": parent["span_id"],
            "operation": "gate.check.test",
            "start_offset_ns": 820,
            "end_offset_ns": 860,
            "duration_ns": 40,
        }
    )
    accepted["spans"].append(child)
    accepted = telemetry.validate_bundle(accepted)

    payload = dashboard.build_phase_payload(
        [accepted],
        phase_id="31.2",
        accepted_trace_id=accepted["trace_id"],
        handoff=sample_handoff(),
    )

    breakdown = {
        item["operation"]: item["exclusive_duration_ns"]
        for item in payload["phase_view"]["gate_breakdown"]
    }
    assert breakdown["gate.check-all"] == 60
    assert breakdown["gate.check.test"] == 40


@pytest.mark.parametrize(
    ("phase_id", "accepted_id", "match"),
    [
        ("31.3", "10000000000040008000000000000000", "no finalized"),
        ("31.2", "50000000000040008000000000000000", "absent"),
        ("31.2", "30000000000040008000000000000000", "successful"),
        ("phase-31", "10000000000040008000000000000000", "dotted numeric"),
    ],
)
def test_payload_refuses_invalid_phase_or_accepted_trace(
    phase_id: str, accepted_id: str, match: str
) -> None:
    accepted = kickoff_bundle()
    bundles = [failed_predecessor(accepted), accepted]
    with pytest.raises(telemetry.ValidationError, match=match):
        dashboard.build_phase_payload(
            bundles,
            phase_id=phase_id,
            accepted_trace_id=accepted_id,
            handoff=sample_handoff(phase_id if phase_id != "phase-31" else "31.2"),
        )


def test_render_is_byte_identical_and_recovers_interrupted_replacement(
    tmp_path: Path,
) -> None:
    accepted = kickoff_bundle()
    engine = tmp_path / "engine"
    output = engine / "reports" / "execution"
    write_ledger(engine, [failed_predecessor(accepted), accepted])

    dashboard.render_phase_dashboard(
        engine_root=engine,
        output_root=output,
        phase_id="31.2",
        accepted_trace_id=accepted["trace_id"],
        handoff=sample_handoff(),
    )
    phase_dir = output / "2026-07-28" / "phase-31.2"
    first = {
        file_path.relative_to(output): file_path.read_bytes()
        for file_path in output.rglob("*")
        if file_path.is_file()
    }
    backup = phase_dir.with_name(".phase-31.2.previous")
    backup.mkdir()
    (backup / "incomplete").write_text("partial", encoding="utf-8")
    dashboard.render_phase_dashboard(
        engine_root=engine,
        output_root=output,
        phase_id="31.2",
        accepted_trace_id=accepted["trace_id"],
        handoff=sample_handoff(),
    )
    second = {
        file_path.relative_to(output): file_path.read_bytes()
        for file_path in output.rglob("*")
        if file_path.is_file()
    }
    assert first == second
    assert not backup.exists()
    assert json.loads((phase_dir / "handoff.json").read_text()) == sample_handoff()


def test_data_script_is_data_only_frozen_schema_and_escapes_script_delimiters() -> None:
    value = {"schema": dashboard.DASHBOARD_SCHEMA, "value": "</script>&\u2028"}
    text = dashboard._script(dashboard.DATA_PREFIX, value)
    assert "<" not in text
    assert "&" not in text
    assert "Object.freeze(" in text
    assert dashboard.parse_data_script(text) == value


def test_semantic_phase_ordering() -> None:
    phases = ["31.10", "31.2.1", "31.2", "9"]
    assert sorted(phases, key=dashboard.semantic_phase_key) == [
        "9",
        "31.2",
        "31.2.1",
        "31.10",
    ]


@pytest.mark.parametrize(
    ("mutation", "match"),
    [
        (lambda value: value["what_just_landed"][0].update(detail="/Users/private"), "private"),
        (lambda value: value["recommended_steps"][0].update(kind="maybe"), "kind"),
        (lambda value: value.update(phase_id="31.9"), "phase"),
        (lambda value: value.update(extra="no"), "unknown"),
    ],
)
def test_handoff_schema_rejects_private_or_malformed_content(mutation: Any, match: str) -> None:
    value = copy.deepcopy(sample_handoff())
    mutation(value)
    with pytest.raises(telemetry.ValidationError, match=match):
        dashboard.validate_handoff(value, phase_id="31.2")


@contextlib.contextmanager
def occupied(port: int):
    """Hold `port` open for the duration of the block, if the host allows it.

    Yields True when this test really is holding the port. When something else
    already holds it, the condition under test is satisfied anyway, so the block
    still runs.
    """
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        listener.bind(("127.0.0.1", port))
        listener.listen(1)
    except OSError:
        listener.close()
        yield False
        return
    try:
        yield True
    finally:
        listener.close()


def dashboard_fixture(tmp_path: Path) -> Path:
    fixture = tmp_path / "fixture"
    (fixture / "bin").mkdir(parents=True)
    (fixture / "reports" / "execution").mkdir(parents=True)
    shutil.copy2(SERVER, fixture / "bin" / SERVER.name)
    python = fixture / "bin" / "python"
    python.write_text('#!/bin/sh\nprintf "%s\\n" "$*"\n', encoding="utf-8")
    python.chmod(0o755)
    return fixture


def test_dashboard_server_composition_survives_an_occupied_fixed_port(
    tmp_path: Path,
) -> None:
    """Port 18080 is legitimately shared, so this assertion must not depend on it.

    `CLAUDE.md` reserves 18080 for ad-hoc rendered-book/static HTML serving, and
    `/kickoff` phase plans put fixture servers there. Observed in Phase 26.9.2:
    with the acceptance battery's fixture server running, the whole host suite
    reported exactly one failure -- this test -- and it cleared the moment the
    servers stopped. What the test is about is the argv the script composes, not
    whether the developer happens to be serving something.
    """
    fixture = dashboard_fixture(tmp_path)
    stub = tmp_path / "lsof-free"
    stub.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
    stub.chmod(0o755)

    with occupied(18080):
        result = subprocess.run(
            [str(fixture / "bin" / SERVER.name)],
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, "AGENTIC_STARTER_DASHBOARD_LSOF": str(stub)},
        )

    assert result.returncode == 0, result.stderr
    assert "http://127.0.0.1:18080/" in result.stdout


def test_dashboard_server_refuses_when_the_fixed_port_is_taken(tmp_path: Path) -> None:
    """The occupancy guard itself, which had no coverage before."""
    fixture = dashboard_fixture(tmp_path)
    stub = tmp_path / "lsof-busy"
    stub.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    stub.chmod(0o755)

    result = subprocess.run(
        [str(fixture / "bin" / SERVER.name)],
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "AGENTIC_STARTER_DASHBOARD_LSOF": str(stub)},
    )

    assert result.returncode == 1
    assert result.stderr == "EXECUTION DASHBOARD ERROR port 18080 is already in use\n"


def test_dashboard_server_uses_fixed_localhost_surface(tmp_path: Path) -> None:
    fixture = dashboard_fixture(tmp_path)
    # Deterministic occupancy probe: this asserts the argv the script composes,
    # which must not depend on whether the developer is using the shared 18080.
    stub = tmp_path / "lsof-free"
    stub.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
    stub.chmod(0o755)

    result = subprocess.run(
        [str(fixture / "bin" / SERVER.name)],
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "AGENTIC_STARTER_DASHBOARD_LSOF": str(stub)},
    )

    assert result.returncode == 0, result.stderr
    assert "http://127.0.0.1:18080/" in result.stdout
    assert (
        f"-m http.server 18080 --bind 127.0.0.1 --directory {fixture / 'reports' / 'execution'}"
    ) in result.stdout


def test_dashboard_server_rejects_arguments() -> None:
    result = subprocess.run(
        [str(SERVER), "--port", "9999"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert result.stderr == "Usage: ./bin/serve-execution-dashboard\n"


def test_dashboard_cli_opens_generated_phase_in_default_browser(tmp_path: Path) -> None:
    accepted = kickoff_bundle()
    engine = tmp_path / "engine"
    output = engine / "reports" / "execution"
    write_ledger(engine, [accepted])
    handoff_path = tmp_path / "handoff.json"
    handoff_path.write_text(json.dumps(sample_handoff()), encoding="utf-8")
    browser_log = tmp_path / "browser.log"
    browser = tmp_path / "browser"
    browser.write_text(
        '#!/bin/sh\nprintf "%s\\n" "$1" > "$DASHBOARD_BROWSER_LOG"\n',
        encoding="utf-8",
    )
    browser.chmod(0o755)
    environment = os.environ.copy()
    environment["BROWSER"] = f"{browser} %s"
    environment["DASHBOARD_BROWSER_LOG"] = str(browser_log)

    result = subprocess.run(
        [
            str(CLI),
            "dashboard",
            "--repo-root",
            str(engine),
            "--phase",
            "31.2",
            "--accepted-trace-id",
            accepted["trace_id"],
            "--handoff",
            str(handoff_path),
            "--output-root",
            str(output),
            "--open",
        ],
        capture_output=True,
        text=True,
        env=environment,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    opened = browser_log.read_text(encoding="utf-8").strip()
    assert opened == (output / "2026-07-28" / "phase-31.2" / "index.html").as_uri()
    assert (output / "2026-07-28" / "phase-31.2" / "handoff.json").is_file()
