from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
COMMAND_ZERO = ROOT / "bin" / "kickoff-command-zero"
sys.path.insert(0, str(ROOT / "lib"))

from agentic_starter import kickoff_runbook  # noqa: E402


def executable(path: Path, body: str) -> None:
    path.write_text("#!/bin/sh\nset -eu\n" + body)
    path.chmod(0o755)


def test_manifest_preflight_and_runner_admission_fail_closed(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    run_dir = tmp_path / "run"
    (root / "bin").mkdir(parents=True)
    (run_dir / "tools").mkdir(parents=True)
    (run_dir / "gate-manifests").mkdir()
    subprocess.run(["git", "init", "-q", "-b", "master", str(root)], check=True)
    calls = tmp_path / "calls"
    executable(run_dir / "tools" / "kickoff-evidence", f"printf '%s\\n' evidence >> {calls}\n")
    executable(root / "probe", f"printf '%s\\n' probe >> {calls}\n")
    executable(
        root / "bin" / "check",
        f"test \"$1\" = format\nprintf '%s\\n' format >> {calls}\n",
    )
    executable(root / "bin" / "check-log", f"printf '%s\\n' log >> {calls}\n")
    document = {
        "schema_version": 1,
        "commands": [
            {
                "operation": "gate.final",
                "attempt": 1,
                "final": True,
                "argv": ["./bin/check", "all"],
            }
        ],
        "preflight_commands": [{"argv": ["./probe"], "reason": "selector dry-run"}],
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(document, sort_keys=True) + "\n")
    loaded, raw, digest = kickoff_runbook.load(manifest_path)
    assert loaded == document
    assert digest == hashlib.sha256(raw).hexdigest()
    assert kickoff_runbook.admitted(
        loaded,
        operation="gate.final",
        attempt=1,
        final=True,
        argv=["./bin/check", "all"],
    )
    assert not kickoff_runbook.admitted(
        loaded,
        operation="gate.final",
        attempt=1,
        final=True,
        argv=["./bin/check", "policy"],
    )
    (run_dir / "gate-manifests" / f"{digest}.json").write_bytes(raw)
    (run_dir / "gate-manifests.jsonl").write_text(json.dumps({"manifest_sha256": digest}) + "\n")
    (run_dir / "run.json").write_text(json.dumps({"repository_root": str(root)}) + "\n")

    result = subprocess.run(
        [str(COMMAND_ZERO), "--run-dir", str(run_dir)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert calls.read_text().splitlines() == ["evidence", "probe", "format", "log"]

    calls.write_text("")
    stored_manifest = run_dir / "gate-manifests" / f"{digest}.json"
    stored_manifest.write_bytes(raw + b" ")
    result = subprocess.run(
        [str(COMMAND_ZERO), "--run-dir", str(run_dir)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert "digest does not match bytes" in result.stderr
    assert calls.read_text().splitlines() == ["evidence"]
    stored_manifest.write_bytes(raw)

    calls.write_text("")
    executable(root / "probe", f"printf '%s\\n' probe >> {calls}\nexit 19\n")
    result = subprocess.run(
        [str(COMMAND_ZERO), "--run-dir", str(run_dir)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert calls.read_text().splitlines() == ["evidence", "probe"]

    malformed = dict(document)
    malformed["commands"] = []
    with pytest.raises(kickoff_runbook.RunbookError):
        kickoff_runbook.validate(malformed)
