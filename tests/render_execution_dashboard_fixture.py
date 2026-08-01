"""Render the committed synthetic execution trace for manual dashboard QA."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))

from agentic_starter import execution_dashboard as dashboard  # noqa: E402
from agentic_starter import execution_telemetry as telemetry  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "execution_telemetry" / "kickoff-trace.jsonl"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    arguments = parser.parse_args()

    output = arguments.output.resolve()
    engine = output.parent / "engine"
    engine.mkdir(parents=True, exist_ok=True)
    (engine / "plan").mkdir(exist_ok=True)
    (engine / "policies").mkdir(exist_ok=True)
    (engine / "CLAUDE.md").write_text("# Visual fixture\n", encoding="utf-8")
    bundle = telemetry.validate_ledger(FIXTURE)[0]
    (engine / "EXECUTION_LOG.jsonl").write_text(
        json.dumps(bundle, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    shutil.copytree(ROOT / "reports" / "execution" / "assets", output / "assets")
    handoff = {
        "schema": dashboard.HANDOFF_SCHEMA,
        "phase_id": "31.2",
        "what_just_landed": [
            {
                "title": "Exact execution truth",
                "detail": "Stages, roles, waits, gates, and retries share one measured trace.",
            },
            {
                "title": "Offline phase report",
                "detail": "The accepted trace now renders without network dependencies.",
            },
        ],
        "see_for_yourself": [
            {
                "title": "Compare the views",
                "steps": ["Inspect the timeline, role table, and gate table."],
                "expected": "Durations and attempt counts agree across every view.",
            }
        ],
        "coming_up_next": {
            "phase_id": "31.3",
            "title": "Next phase",
            "summary": "Continue from the accepted candidate.",
        },
        "recommended_steps": [
            {
                "title": "Ready",
                "detail": "No operator prerequisite blocks the next phase.",
                "kind": "ready",
            }
        ],
    }
    dashboard.render_phase_dashboard(
        engine_root=engine,
        output_root=output,
        phase_id="31.2",
        accepted_trace_id=bundle["trace_id"],
        handoff=handoff,
    )
    print(output / "2026-07-28" / "phase-31.2" / "index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
