"""Deterministic, offline dashboards for finalized kickoff telemetry."""

from __future__ import annotations

import contextlib
import fcntl
import hashlib
import json
import os
import re
import shutil
import tempfile
from collections.abc import Iterator, Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from agentic_starter.execution_telemetry import ValidationError, aggregate_trace, validate_ledger

DASHBOARD_SCHEMA = "agentic_starter.execution_dashboard.v1"
INDEX_SCHEMA = "agentic_starter.execution_dashboard_index.v1"
HANDOFF_SCHEMA = "agentic_starter.execution_dashboard_handoff.v1"
RENDERER_VERSION = "dashboard-v3"
DATA_PREFIX = "window.AGENTIC_STARTER_EXECUTION_DASHBOARD_DATA="
INDEX_PREFIX = "window.AGENTIC_STARTER_EXECUTION_DASHBOARD_INDEX="
PHASE_RE = re.compile(r"^\d+(?:\.\d+)*$")
TRACE_ID_RE = re.compile(r"^[0-9a-f]{32}$")
UTC_RE = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})T(?P<time>\d{2}:\d{2}:\d{2})"
    r"(?:\.(?P<fraction>\d{1,9}))?Z$"
)
ROLE_ORDER = ("planner", "reviewer", "coder", "critic")
ROLE_LABELS = {
    "planner": "Planning",
    "reviewer": "Plan Review",
    "coder": "Implementation",
    "critic": "Code Review",
}
SAFE_SPAN_FIELDS = (
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
)
HANDOFF_ITEM_KEYS = frozenset({"title", "detail"})
DEMO_ITEM_KEYS = frozenset({"title", "steps", "expected"})
NEXT_KEYS = frozenset({"phase_id", "title", "summary"})
RECOMMENDATION_KEYS = frozenset({"title", "detail", "kind"})
RECOMMENDATION_KINDS = frozenset({"action", "blocking", "ready"})
HANDOFF_KEYS = frozenset(
    {
        "schema",
        "phase_id",
        "what_just_landed",
        "see_for_yourself",
        "coming_up_next",
        "recommended_steps",
    }
)
HANDOFF_FORBIDDEN = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"/Users/",
        r"[A-Za-z]:\\",
        r"\bprompt\b",
        r"\bresponse\b",
        r"\bsecret\b",
        r"\btoken(?:s)?\b",
        r"\buncommitted\b",
    )
)


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _safe_script_json(value: Any) -> str:
    text = _canonical(value).decode()
    return (
        text.replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def _script(prefix: str, value: Any) -> str:
    return f"{prefix}Object.freeze({_safe_script_json(value)});\n"


def parse_data_script(text: str, *, index: bool = False) -> dict[str, Any]:
    prefix = INDEX_PREFIX if index else DATA_PREFIX
    suffix = ");\n"
    if not text.startswith(prefix + "Object.freeze(") or not text.endswith(suffix):
        raise ValidationError("dashboard data file is not a data-only frozen assignment")
    raw = text[len(prefix + "Object.freeze(") : -len(suffix)]
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValidationError("dashboard data payload must be an object")
    expected = INDEX_SCHEMA if index else DASHBOARD_SCHEMA
    if value.get("schema") != expected:
        raise ValidationError(f"dashboard data schema must be {expected}")
    return value


def semantic_phase_key(phase_id: str) -> tuple[int, ...]:
    if not PHASE_RE.fullmatch(phase_id):
        raise ValidationError("phase must be a dotted numeric phase id")
    return tuple(int(part) for part in phase_id.split("."))


def _handoff_text(value: Any, field: str, *, maximum: int = 500) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValidationError(f"{field} must be a nonempty trimmed string")
    if len(value) > maximum or any(character in value for character in "\r\n<>"):
        raise ValidationError(f"{field} contains unsafe or oversized text")
    for pattern in HANDOFF_FORBIDDEN:
        if pattern.search(value):
            raise ValidationError(f"{field} contains private or out-of-scope text")
    return value


def validate_handoff(value: Mapping[str, Any], *, phase_id: str) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != HANDOFF_KEYS:
        raise ValidationError("dashboard handoff has unknown or missing fields")
    if value["schema"] != HANDOFF_SCHEMA or value["phase_id"] != phase_id:
        raise ValidationError("dashboard handoff schema or phase does not match")
    semantic_phase_key(phase_id)

    landed = value["what_just_landed"]
    demos = value["see_for_yourself"]
    recommendations = value["recommended_steps"]
    if not isinstance(landed, list) or not 1 <= len(landed) <= 8:
        raise ValidationError("what_just_landed must contain 1-8 items")
    if not isinstance(demos, list) or len(demos) > 6:
        raise ValidationError("see_for_yourself must contain at most 6 items")
    if not isinstance(recommendations, list) or len(recommendations) > 8:
        raise ValidationError("recommended_steps must contain at most 8 items")

    valid_landed = []
    for index, item in enumerate(landed):
        if not isinstance(item, Mapping) or set(item) != HANDOFF_ITEM_KEYS:
            raise ValidationError("what_just_landed items have an invalid shape")
        valid_landed.append(
            {
                "title": _handoff_text(item["title"], f"landed[{index}].title", maximum=120),
                "detail": _handoff_text(item["detail"], f"landed[{index}].detail"),
            }
        )
    valid_demos = []
    for index, item in enumerate(demos):
        if not isinstance(item, Mapping) or set(item) != DEMO_ITEM_KEYS:
            raise ValidationError("see_for_yourself items have an invalid shape")
        steps = item["steps"]
        if not isinstance(steps, list) or not 1 <= len(steps) <= 8:
            raise ValidationError("demo steps must contain 1-8 strings")
        valid_demos.append(
            {
                "title": _handoff_text(item["title"], f"demo[{index}].title", maximum=120),
                "steps": [
                    _handoff_text(step, f"demo[{index}].steps[{step_index}]")
                    for step_index, step in enumerate(steps)
                ],
                "expected": _handoff_text(item["expected"], f"demo[{index}].expected"),
            }
        )
    next_phase = value["coming_up_next"]
    valid_next = None
    if next_phase is not None:
        if not isinstance(next_phase, Mapping) or set(next_phase) != NEXT_KEYS:
            raise ValidationError("coming_up_next has an invalid shape")
        next_id = _handoff_text(next_phase["phase_id"], "coming_up_next.phase_id", maximum=32)
        semantic_phase_key(next_id)
        valid_next = {
            "phase_id": next_id,
            "title": _handoff_text(next_phase["title"], "coming_up_next.title", maximum=160),
            "summary": _handoff_text(next_phase["summary"], "coming_up_next.summary"),
        }
    valid_recommendations = []
    for index, item in enumerate(recommendations):
        if not isinstance(item, Mapping) or set(item) != RECOMMENDATION_KEYS:
            raise ValidationError("recommended_steps items have an invalid shape")
        if item["kind"] not in RECOMMENDATION_KINDS:
            raise ValidationError("recommended step kind is invalid")
        valid_recommendations.append(
            {
                "title": _handoff_text(item["title"], f"recommended[{index}].title", maximum=120),
                "detail": _handoff_text(item["detail"], f"recommended[{index}].detail"),
                "kind": item["kind"],
            }
        )
    return {
        "schema": HANDOFF_SCHEMA,
        "phase_id": phase_id,
        "what_just_landed": valid_landed,
        "see_for_yourself": valid_demos,
        "coming_up_next": valid_next,
        "recommended_steps": valid_recommendations,
    }


def _phase_for(bundle: Mapping[str, Any]) -> str | None:
    root_id = bundle["root_span_id"]
    root = next(span for span in bundle["spans"] if span["span_id"] == root_id)
    operation = root["operation"]
    if root["run_type"] != "kickoff" or not operation.startswith("phase."):
        return None
    phase_id = operation.removeprefix("phase.")
    return phase_id if PHASE_RE.fullmatch(phase_id) else None


def _root(bundle: Mapping[str, Any]) -> Mapping[str, Any]:
    return next(span for span in bundle["spans"] if span["span_id"] == bundle["root_span_id"])


def _utc_ns(value: str) -> int:
    match = UTC_RE.fullmatch(value)
    if not match:
        raise ValidationError("dashboard timestamp must be canonical UTC")
    second = datetime.strptime(
        f"{match.group('date')}T{match.group('time')}", "%Y-%m-%dT%H:%M:%S"
    ).replace(tzinfo=UTC)
    fraction = (match.group("fraction") or "").ljust(9, "0")
    return int(second.timestamp()) * 1_000_000_000 + int(fraction or "0")


def _interval_union(intervals: Sequence[tuple[int, int]]) -> int:
    valid = sorted((start, end) for start, end in intervals if end > start)
    if not valid:
        return 0
    total = 0
    start, end = valid[0]
    for next_start, next_end in valid[1:]:
        if next_start <= end:
            end = max(end, next_end)
        else:
            total += end - start
            start, end = next_start, next_end
    return total + end - start


def _dashboard_view(
    bundles: Sequence[Mapping[str, Any]],
    *,
    view_id: str,
    view_type: str,
    outcome: str,
    trace_status: str,
    accepted: bool,
    unsuccessful: bool,
) -> dict[str, Any]:
    roots: list[tuple[int, int]] = []
    spans: list[dict[str, Any]] = []
    interval_by_id: dict[str, tuple[int, int]] = {}
    source_by_id: dict[str, str] = {}
    raw_by_id: dict[str, Mapping[str, Any]] = {}
    root_ids: set[str] = set()
    for bundle in bundles:
        root = _root(bundle)
        origin = _utc_ns(root["started_at"])
        root_interval = (origin, origin + root["duration_ns"])
        roots.append(root_interval)
        root_ids.add(root["span_id"])
        for raw in bundle["spans"]:
            safe = {key: raw[key] for key in SAFE_SPAN_FIELDS if key in raw}
            start = origin + raw["start_offset_ns"]
            end = origin + raw["end_offset_ns"]
            interval_by_id[raw["span_id"]] = (start, end)
            source_by_id[raw["span_id"]] = bundle["trace_id"]
            raw_by_id[raw["span_id"]] = raw
            safe["source_trace_id"] = bundle["trace_id"]
            spans.append(safe)

    phase_origin = min(start for start, _ in roots)
    for span in spans:
        start, end = interval_by_id[span["span_id"]]
        span["start_offset_ns"] = start - phase_origin
        span["end_offset_ns"] = end - phase_origin

    children = [span for span in spans if span["span_id"] not in root_ids]

    def depth(span: Mapping[str, Any]) -> int:
        value = 0
        parent = span.get("parent_span_id")
        while parent is not None:
            value += 1
            parent = raw_by_id[parent].get("parent_span_id")
        return value

    def effective_category(span: Mapping[str, Any]) -> str:
        if span["category"] != "wait":
            return span["category"]
        parent = span.get("parent_span_id")
        while parent is not None:
            ancestor = raw_by_id[parent]
            if ancestor["category"] == "intelligence":
                return "intelligence"
            parent = ancestor.get("parent_span_id")
        return "wait"

    def is_nested_intelligence_wait(span: Mapping[str, Any]) -> bool:
        return span["category"] == "wait" and effective_category(span) == "intelligence"

    category_totals = {
        category: 0 for category in ("gate", "intelligence", "reconciliation", "wait")
    }
    root_boundaries = {point for interval in roots for point in interval}
    child_boundaries = {point for span in children for point in interval_by_id[span["span_id"]]}
    boundaries = sorted(root_boundaries | child_boundaries)
    gate_exclusive: dict[str, int] = {}
    for start, end in zip(boundaries, boundaries[1:]):
        if end <= start or not any(
            root_start <= start and root_end >= end for root_start, root_end in roots
        ):
            continue
        active = [
            span
            for span in children
            if interval_by_id[span["span_id"]][0] <= start
            and interval_by_id[span["span_id"]][1] >= end
        ]
        if active:
            winner = max(
                active,
                key=lambda span: (
                    depth(span),
                    -span["duration_ns"],
                    span["span_id"],
                ),
            )
            category_totals[effective_category(winner)] += end - start
        active_gates = [span for span in active if span["category"] == "gate"]
        if active_gates:
            gate_winner = max(
                active_gates,
                key=lambda span: (
                    depth(span),
                    -span["duration_ns"],
                    span["span_id"],
                ),
            )
            gate_exclusive[gate_winner["operation"]] = (
                gate_exclusive.get(gate_winner["operation"], 0) + end - start
            )

    active_ns = _interval_union(roots)
    covered_ns = _interval_union([interval_by_id[span["span_id"]] for span in children])
    material_children = [span for span in children if not is_nested_intelligence_wait(span)]
    failed = [span for span in material_children if span["outcome"] != "success"]
    retried = [span for span in material_children if span["attempt"] > 1]

    role_rows = []
    for role in ROLE_ORDER:
        intelligence = [
            span
            for span in children
            if span["category"] == "intelligence" and span.get("role") == role
        ]
        if not intelligence:
            continue
        intelligence_ids = {span["span_id"] for span in intelligence}
        waits = [
            span
            for span in children
            if span["category"] == "wait"
            and span.get("role") == role
            and span.get("parent_span_id") in intelligence_ids
        ]
        role_rows.append(
            {
                "role": role,
                "label": ROLE_LABELS[role],
                "attempt_count": len(intelligence),
                "failed_attempts": sum(span["outcome"] != "success" for span in intelligence),
                "total_duration_ns": sum(span["duration_ns"] for span in intelligence),
                "active_union_ns": _interval_union(
                    [interval_by_id[span["span_id"]] for span in intelligence]
                ),
                "orchestrator_wait_ns": _interval_union(
                    [interval_by_id[span["span_id"]] for span in waits]
                ),
                "harnesses": sorted(
                    {span["harness"] for span in intelligence if "harness" in span}
                ),
                "models": sorted({span["model"] for span in intelligence if "model" in span}),
            }
        )

    gate_rows = []
    gate_spans = [span for span in children if span["category"] == "gate"]
    for operation, duration_ns in sorted(
        gate_exclusive.items(), key=lambda item: (-item[1], item[0])
    ):
        matching = [span for span in gate_spans if span["operation"] == operation]
        gate_rows.append(
            {
                "operation": operation,
                "attempt_count": len(matching),
                "failed_attempts": sum(span["outcome"] != "success" for span in matching),
                "exclusive_duration_ns": duration_ns,
            }
        )

    convergence_rows = []
    review_passes = [
        span
        for span in children
        if span["category"] == "intelligence"
        and span.get("role") in {"reviewer", "critic"}
        and "findings_reported" in span
        and "actionable_findings" in span
    ]
    pass_by_role: dict[str, int] = {}
    for span in sorted(
        review_passes,
        key=lambda item: (
            interval_by_id[item["span_id"]][0],
            item["span_id"],
        ),
    ):
        role = span["role"]
        pass_by_role[role] = pass_by_role.get(role, 0) + 1
        convergence_rows.append(
            {
                "role": role,
                "label": ROLE_LABELS[role],
                "pass": pass_by_role[role],
                "findings_reported": span["findings_reported"],
                "actionable_findings": span["actionable_findings"],
                "duration_ns": span["duration_ns"],
                "outcome": span["outcome"],
            }
        )

    slowest = sorted(material_children, key=lambda span: (-span["duration_ns"], span["operation"]))[
        :20
    ]
    calendar_elapsed_ns = max(end for _, end in roots) - phase_origin
    return {
        "view_id": view_id,
        "view_type": view_type,
        "accepted": accepted,
        "unsuccessful": unsuccessful,
        "trace_status": trace_status,
        "outcome": outcome,
        "makespan_ns": active_ns,
        "calendar_elapsed_ns": calendar_elapsed_ns,
        "coverage_ns": covered_ns,
        "coverage_ratio": covered_ns / active_ns if active_ns else 1.0,
        "unattributed_ns": active_ns - covered_ns,
        "failed_coverage_ns": _interval_union([interval_by_id[span["span_id"]] for span in failed]),
        "retry_coverage_ns": _interval_union([interval_by_id[span["span_id"]] for span in retried]),
        "failed_span_count": len(failed),
        "retry_span_count": len(retried),
        "role_attempt_count": sum(row["attempt_count"] for row in role_rows),
        "role_followup_count": sum(max(0, row["attempt_count"] - 1) for row in role_rows),
        "gate_run_count": len(gate_spans),
        "failed_gate_count": sum(span["outcome"] != "success" for span in gate_spans),
        "category_coverage_ns": category_totals,
        "slowest_spans": slowest,
        "concurrency_groups": {},
        "attempts": _attempt_summary(material_children),
        "role_breakdown": role_rows,
        "gate_breakdown": gate_rows,
        "trace_count": len(bundles),
        "spans": spans,
        **({"review_convergence": convergence_rows} if convergence_rows else {}),
    }


def _attempt_summary(spans: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
    for span in spans:
        if span["category"] == "run":
            continue
        grouped.setdefault((span["operation"], span.get("role", "")), []).append(span)
    return [
        {
            "operation": key[0],
            "role": key[1] or None,
            "attempt_count": len(items),
            "highest_attempt": max(item["attempt"] for item in items),
            "failed_attempts": sum(item["outcome"] != "success" for item in items),
            "total_duration_ns": sum(item["duration_ns"] for item in items),
        }
        for key, items in sorted(grouped.items())
        if len(items) > 1 or any(item["attempt"] > 1 for item in items)
    ]


def build_phase_payload(
    bundles: Sequence[Mapping[str, Any]],
    *,
    phase_id: str,
    accepted_trace_id: str,
    handoff: Mapping[str, Any],
) -> dict[str, Any]:
    semantic_phase_key(phase_id)
    if not TRACE_ID_RE.fullmatch(accepted_trace_id):
        raise ValidationError("accepted trace id must be a lowercase UUID4 hex id")
    selected = [bundle for bundle in bundles if _phase_for(bundle) == phase_id]
    if not selected:
        raise ValidationError(f"no finalized kickoff traces exist for phase {phase_id}")
    accepted = next(
        (bundle for bundle in selected if bundle["trace_id"] == accepted_trace_id), None
    )
    if accepted is None:
        raise ValidationError("accepted trace is absent or belongs to another phase")
    accepted_root = _root(accepted)
    if accepted_root["outcome"] != "success":
        raise ValidationError("accepted trace must have a successful finalized root")

    selected = sorted(selected, key=lambda item: (item["finalized_at"], item["trace_id"]))
    lineage = [bundle for bundle in selected if bundle["finalized_at"] <= accepted["finalized_at"]]
    traces = []
    for bundle in selected:
        root = _root(bundle)
        is_accepted = bundle["trace_id"] == accepted_trace_id
        telemetry_report = aggregate_trace(bundle)
        unsuccessful = not is_accepted and (
            root["outcome"] != "success" or telemetry_report["failed_coverage_ns"] > 0
        )
        trace = _dashboard_view(
            [bundle],
            view_id=bundle["trace_id"],
            view_type="trace",
            outcome=root["outcome"],
            trace_status=(
                "accepted" if is_accepted else "unsuccessful" if unsuccessful else "superseded"
            ),
            accepted=is_accepted,
            unsuccessful=unsuccessful,
        )
        trace["trace_id"] = bundle["trace_id"]
        trace["finalized_at"] = bundle["finalized_at"]
        trace["concurrency_groups"] = telemetry_report["concurrency_groups"]
        traces.append(trace)
    accepted_trace = next(item for item in traces if item["accepted"])
    phase_view = _dashboard_view(
        lineage,
        view_id="phase",
        view_type="phase",
        outcome=accepted_trace["outcome"],
        trace_status="accepted phase",
        accepted=True,
        unsuccessful=False,
    )
    finalized_date = str(accepted["finalized_at"])[:10]
    valid_handoff = validate_handoff(handoff, phase_id=phase_id)
    return {
        "schema": DASHBOARD_SCHEMA,
        "renderer_version": RENDERER_VERSION,
        "phase_id": phase_id,
        "utc_date": finalized_date,
        "accepted_trace_id": accepted_trace_id,
        "accepted_finalized_at": accepted["finalized_at"],
        "outcome": accepted_trace["outcome"],
        "source_bundle_digest": _digest(selected),
        "handoff_digest": _digest(valid_handoff),
        "handoff": valid_handoff,
        "trace_count": len(traces),
        "lineage_trace_count": len(lineage),
        "failed_trace_count": sum(item["unsuccessful"] for item in traces),
        "phase_view": phase_view,
        "traces": traces,
    }


PHASE_HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy"
 content="default-src 'none'; script-src 'self'; style-src 'self';
 img-src 'self' data:; font-src 'none'; connect-src 'none'; object-src 'none';
 base-uri 'none'; form-action 'none'">
<title>Execution dashboard</title>
<link rel="stylesheet" href="../../assets/dashboard-v3.css"></head>
<body data-view="phase"><header class="sticky"><nav aria-label="Breadcrumb">
<a href="../../index.html">Execution archive</a><span aria-hidden="true">›</span>
<span id="crumb-date"></span><span aria-hidden="true">›</span>
<strong id="crumb-phase"></strong></nav><div class="phase-nav">
<a id="previous-phase" hidden>← Previous</a>
<a id="next-phase" hidden>Next →</a></div></header>
<main id="app"><p class="loading">Loading local telemetry…</p></main>
<script src="../../assets/echarts-6.1.0.min.js"></script>
<script src="data.js"></script><script src="../../index-data.js"></script>
<script src="../../assets/dashboard-v3.js"></script></body></html>
"""

INDEX_HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy"
 content="default-src 'none'; script-src 'self'; style-src 'self';
 img-src 'self' data:; font-src 'none'; connect-src 'none'; object-src 'none';
 base-uri 'none'; form-action 'none'">
<title>Execution dashboard archive</title>
<link rel="stylesheet" href="assets/dashboard-v3.css"></head>
<body data-view="index"><header class="sticky"><nav aria-label="Breadcrumb">
<strong>Execution archive</strong></nav></header>
<main id="app"><p class="loading">Loading local telemetry…</p></main>
<script src="assets/echarts-6.1.0.min.js"></script>
<script src="index-data.js"></script>
<script src="assets/dashboard-v3.js"></script></body></html>
"""


def _atomic_text(file_path: Path, text: str) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{file_path.name}.", dir=file_path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, file_path)
    finally:
        with contextlib.suppress(FileNotFoundError):
            temporary.unlink()


@contextlib.contextmanager
def _archive_lock(engine_root: Path) -> Iterator[None]:
    lock_name = hashlib.sha256(str(engine_root.resolve()).encode()).hexdigest()[:24]
    lock_path = Path(tempfile.gettempdir()) / f"agentic_starter-dashboard-{lock_name}.lock"
    with lock_path.open("a", encoding="utf-8") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def _summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    phase_view = payload["phase_view"]
    return {
        "phase_id": payload["phase_id"],
        "utc_date": payload["utc_date"],
        "accepted_trace_id": payload["accepted_trace_id"],
        "accepted_finalized_at": payload["accepted_finalized_at"],
        "outcome": payload["outcome"],
        "trace_count": payload["trace_count"],
        "failed_trace_count": payload["failed_trace_count"],
        "makespan_ns": phase_view["makespan_ns"],
        "calendar_elapsed_ns": phase_view["calendar_elapsed_ns"],
        "role_followup_count": phase_view["role_followup_count"],
        "gate_run_count": phase_view["gate_run_count"],
        "failed_gate_count": phase_view["failed_gate_count"],
        "href": f"{payload['utc_date']}/phase-{payload['phase_id']}/index.html",
        "source_bundle_digest": payload["source_bundle_digest"],
    }


def _existing_payloads(output_root: Path) -> list[dict[str, Any]]:
    payloads = []
    for file_path in sorted(output_root.glob("????-??-??/phase-*/data.js")):
        payloads.append(parse_data_script(file_path.read_text(encoding="utf-8")))
    return payloads


def _write_index(output_root: Path, payloads: Sequence[Mapping[str, Any]]) -> None:
    summaries = [_summary(payload) for payload in payloads]
    summaries.sort(
        key=lambda item: (
            item["accepted_finalized_at"],
            semantic_phase_key(item["phase_id"]),
        )
    )
    for position, item in enumerate(summaries):
        item["previous_href"] = summaries[position - 1]["href"] if position else None
        item["next_href"] = (
            summaries[position + 1]["href"] if position + 1 < len(summaries) else None
        )
    grouped: dict[str, list[str]] = {}
    for item in summaries:
        grouped.setdefault(item["utc_date"], []).append(item["phase_id"])
    index = {
        "schema": INDEX_SCHEMA,
        "renderer_version": RENDERER_VERSION,
        "phases": summaries,
        "dates": [{"utc_date": key, "phases": grouped[key]} for key in sorted(grouped)],
    }
    _atomic_text(output_root / "index.html", INDEX_HTML)
    _atomic_text(output_root / "index-data.js", _script(INDEX_PREFIX, index))


def render_phase_dashboard(
    *,
    engine_root: Path,
    output_root: Path,
    phase_id: str,
    accepted_trace_id: str,
    handoff: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    bundles = validate_ledger(engine_root / "EXECUTION_LOG.jsonl")
    output_root = output_root.resolve()
    selected = [bundle for bundle in bundles if _phase_for(bundle) == phase_id]
    accepted = next(
        (bundle for bundle in selected if bundle["trace_id"] == accepted_trace_id), None
    )
    if accepted is None:
        raise ValidationError("accepted trace is absent or belongs to another phase")
    finalized_date = str(accepted["finalized_at"])[:10]
    destination = output_root / finalized_date / f"phase-{phase_id}"
    if handoff is None:
        handoff_path = destination / "handoff.json"
        if not handoff_path.is_file():
            raise ValidationError("dashboard handoff is required for first generation")
        handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
    payload = build_phase_payload(
        bundles,
        phase_id=phase_id,
        accepted_trace_id=accepted_trace_id,
        handoff=handoff,
    )
    with _archive_lock(engine_root):
        destination.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=".dashboard-", dir=destination.parent))
        try:
            (staging / "index.html").write_text(PHASE_HTML, encoding="utf-8", newline="\n")
            (staging / "data.js").write_text(
                _script(DATA_PREFIX, payload), encoding="utf-8", newline="\n"
            )
            (staging / "handoff.json").write_bytes(_canonical(payload["handoff"]) + b"\n")
            backup = destination.with_name(f".{destination.name}.previous")
            if backup.exists():
                shutil.rmtree(backup)
            if destination.exists():
                os.replace(destination, backup)
            os.replace(staging, destination)
            if backup.exists():
                shutil.rmtree(backup)
            payloads = [
                item for item in _existing_payloads(output_root) if item["phase_id"] != phase_id
            ]
            payloads.append(payload)
            _write_index(output_root, payloads)
        finally:
            if staging.exists():
                shutil.rmtree(staging)
    return {
        "phase_id": phase_id,
        "accepted_trace_id": accepted_trace_id,
        "archive_directory": str(destination.relative_to(output_root)),
        "source_bundle_digest": payload["source_bundle_digest"],
    }
