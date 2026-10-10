from __future__ import annotations

import copy
import json
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


def sample_handoff(phase_id: str = "31.2") -> dict[str, Any]:
    return {
        "schema": dashboard.HANDOFF_SCHEMA,
        "project": "Sample Project",
        "phase_id": phase_id,
        "what_just_landed": [
            {
                "title": "Exact timing",
                "detail": "Managed work now reports measured duration.",
            }
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

    assert payload["project"] == "Sample Project"
    assert payload["operator_parks"] == parks
    assert payload["phase_view"]["operator_parks"] == parks
    assert payload["operator_parks"]["total_duration_ns"] == 75_000_000_000
    assert payload["operator_parks"]["total_exact"] is False
    assert "boot_id" not in json.dumps(payload["operator_parks"])


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
    archive = dashboard.parse_data_script((output / "index-data.js").read_text(), index=True)
    assert archive["project"] == "Sample Project"
    assert archive["phases"][0]["project"] == "Sample Project"


@pytest.mark.parametrize(
    ("mutation", "match"),
    [
        (
            lambda value: value["what_just_landed"][0].update(detail="/Users/private"),
            "private",
        ),
        (lambda value: value["recommended_steps"][0].update(kind="maybe"), "kind"),
        (lambda value: value.update(phase_id="31.9"), "phase"),
        (lambda value: value.update(extra="no"), "unknown"),
        (lambda value: value.pop("project"), "missing fields"),
        (lambda value: value.update(project=" "), "nonempty"),
        (lambda value: value.update(project="/Users/me/app"), "out-of-scope"),
    ],
)
def test_handoff_schema_rejects_private_or_malformed_content(mutation: Any, match: str) -> None:
    value = copy.deepcopy(sample_handoff())
    mutation(value)
    with pytest.raises(telemetry.ValidationError, match=match):
        dashboard.validate_handoff(value, phase_id="31.2")


def test_content_scan_blanks_operation_labels_and_nothing_else() -> None:
    data = json.dumps(
        {
            "spans": [{"operation": "gate.no-lock-tokens", "outcome": "success"}],
            "title": "the tokens leaked",
            "note": {"operation": "not a label: tokens"},
        },
        separators=(",", ":"),
    )
    scanned = dashboard.content_scan_text(data)
    assert "gate.no-lock-tokens" not in scanned
    assert '"operation":""' in scanned
    assert "the tokens leaked" in scanned
    assert "not a label: tokens" in scanned
    assert dashboard.content_scan_text('{"operation": "gate.secret"}') == '{"operation":""}'


def with_stages(bundle: dict[str, Any], *, drop_roles: tuple[str, ...]) -> dict[str, Any]:
    """Add planning and implementation stage spans; optionally remove delegated roles."""
    staged = copy.deepcopy(bundle)
    root = next(span for span in staged["spans"] if span["parent_span_id"] is None)
    staged["spans"] = [span for span in staged["spans"] if span.get("role") not in drop_roles]
    for index, (operation, start, end) in enumerate(
        (("orchestration.planning", 0, 400), ("orchestration.implementation", 400, 900)),
        start=0xA0,
    ):
        stage = copy.deepcopy(root)
        stage.update(
            span_id=f"100000000000400080000000000000{index:02x}",
            parent_span_id=root["span_id"],
            category="reconciliation",
            operation=operation,
            start_offset_ns=start,
            end_offset_ns=end,
            duration_ns=end - start,
        )
        staged["spans"].append(stage)
    staged["spans"].sort(key=lambda span: (span["start_offset_ns"], span["span_id"]))
    return telemetry.validate_bundle(staged)


def inline_roles(bundle: dict[str, Any]) -> dict[str, str | None]:
    payload = dashboard.build_phase_payload(
        [bundle],
        phase_id="31.2",
        accepted_trace_id=bundle["trace_id"],
        handoff=sample_handoff(),
    )
    views = [payload["phase_view"], *payload["traces"]]
    found = [
        {
            span["operation"]: span.get("inline_role")
            for span in view["spans"]
            if span["category"] == "reconciliation"
        }
        for view in views
    ]
    assert len(found) == 2 and found[0] == found[1]
    return found[0]


def test_inline_planning_and_coding_are_attributed_to_their_activities() -> None:
    delegated = with_stages(kickoff_bundle(), drop_roles=())
    assert inline_roles(delegated) == {
        "orchestration.planning": None,
        "orchestration.implementation": None,
    }
    primary = with_stages(kickoff_bundle(), drop_roles=("planner", "coder"))
    assert inline_roles(primary) == {
        "orchestration.planning": "planner",
        "orchestration.implementation": "coder",
    }
    coder_only = with_stages(kickoff_bundle(), drop_roles=("planner",))
    assert inline_roles(coder_only) == {
        "orchestration.planning": "planner",
        "orchestration.implementation": None,
    }
