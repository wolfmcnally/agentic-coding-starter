"""Construct real new-format fixture roots; synthetic claims grant no real authority."""

from __future__ import annotations

import hashlib
import json
import shutil
import uuid
from pathlib import Path

import yaml

SOURCE = Path(__file__).resolve().parents[1]


def install_record_tools(root: Path) -> None:
    library = root / "lib/agentic_starter"
    library.mkdir(parents=True, exist_ok=True)
    for source in (SOURCE / "lib/agentic_starter").glob("*.py"):
        shutil.copy2(source, library / source.name)
    (root / "bin").mkdir(exist_ok=True)
    for name in (
        "kickoff-evidence",
        "kickoff-tree-id",
        "execution-telemetry",
        "kickoff-config",
        "kickoff-command-zero",
    ):
        shutil.copy2(SOURCE / "bin" / name, root / "bin" / name)


def create_records(
    root: Path, phases: dict[str, dict], *, writer: str = "fixture-operator"
) -> dict[str, dict]:
    for directory in ("plan/phases", "plan/events", "log/entries", "collaboration"):
        (root / directory).mkdir(parents=True, exist_ok=True)
    manifest = root / "collaboration/manifest.json"
    if not manifest.exists():
        manifest.write_text(
            json.dumps(
                {
                    "format": "starter.multioperator.v1",
                    "adopted": True,
                    "original_log_bytes": 0,
                    "original_log_sha256": hashlib.sha256(b"").hexdigest(),
                }
            )
            + "\n"
        )
    results = {}
    for index, (name, supplied) in enumerate(phases.items(), 1):
        values = dict(supplied)
        state = values.pop("state", "not-started")
        owner = values.pop("owner", writer if state == "in-progress" else None)
        claim = "fixture-only-coordinated-claim:" + name if state == "in-progress" else None
        body = values.pop("body", "# " + name + "\n")
        metadata = {
            "id": name,
            "title": name,
            "order": str(index),
            "parent": None,
            "depends_on": [],
            "informs": [],
            **values,
        }
        path = root / "plan/phases" / (name + ".md")
        encoded = ("---\n" + yaml.safe_dump(metadata, sort_keys=False) + "---\n\n" + body).encode()
        if path.exists():
            assert path.read_bytes() == encoded, (
                "fixture would rewrite an existing phase definition"
            )
        else:
            path.write_bytes(encoded)
        item = {
            "id": uuid.uuid5(uuid.NAMESPACE_URL, "fixture:" + name).hex,
            "phase": name,
            "previous": None,
            "from": None,
            "state": state,
            "owner": owner,
            "writer": writer,
            "claim": claim,
            "reason": "Explicit synthetic initial conditions; not real acceptance",
        }
        event = root / "plan/events" / (item["id"] + ".json")
        if not event.exists():
            event.write_text(json.dumps(item) + "\n")
        results[name] = item
    return results


def completion(
    root: Path, phase: str, *, ancestors: list[str] = (), remaining: str | None = None
) -> dict:
    heads = {}
    for path in (root / "plan/events").glob("*.json"):
        value = json.loads(path.read_text())
        heads.setdefault(value["phase"], []).append(value)
    proposal = []
    for name in (phase, *ancestors):
        chain = heads[name]
        parent_ids = {item["previous"] for item in chain}
        current = next(item for item in chain if item["id"] not in parent_ids)
        proposal.append(
            {
                "id": uuid.uuid4().hex,
                "phase": name,
                "previous": current["id"],
                "from": current["state"],
                "state": "completed",
                "owner": current["owner"],
                "writer": current["owner"],
                "claim": current["claim"],
                "reason": "Actual qualified fixture close",
            }
        )
    return {
        "schema": "agentic.phase-transition.v1",
        "events": proposal,
        "parent_continuation": remaining,
    }
