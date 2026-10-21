"""No-model causal checks for the explicitly held diagnostic admission boundary."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
from agentic_starter import review_diagnostic as diagnostic  # noqa: E402
from agentic_starter import workflow  # noqa: E402


def test_diagnostic_seal_and_held_admission(tmp_path, monkeypatch):
    run = tmp_path / "diagnostic"
    diagnostic.prepare(run, authority="operator-approved synthetic diagnostic")
    document = diagnostic.validate(run)
    assert document["purpose"] == "native-binding-diagnostic"
    registration = json.loads((run / "code-registration.json").read_text())
    assert registration["candidate_id"] == document["fixture_sha256"]
    other = tmp_path / "fresh-diagnostic"
    diagnostic.prepare(other, authority="same bounded synthetic assignment")
    assert diagnostic.validate(other)["session_id"] != document["session_id"]
    assert 0 < document["remaining"] <= 600
    assert not (tmp_path / ".kickoff").exists()
    assert not (run / "run.json").exists()  # Never impersonate a kickoff phase.
    with pytest.raises(diagnostic.DiagnosticError, match="new and canonical"):
        diagnostic.prepare(run, authority="another admission")
    hook = tmp_path / "synthetic-hook.py"
    hook.write_text("raise RuntimeError('NATIVE MUST NOT LAUNCH')\n")
    monkeypatch.setattr(diagnostic, "HOOK_SHA256", diagnostic.digest(hook.read_bytes()))
    settings = tmp_path / "settings.json"
    settings.write_text(
        json.dumps(
            {
                "enabledPlugins": {"generic-tool-catalog": True},
                "mcpServers": {"generic-bus": {"command": "synthetic-config-only"}},
                "hooks": {
                    "SessionStart": [
                        {"hooks": [{"type": "command", "command": "unqualified-startup"}]}
                    ]
                },
            }
        )
    )
    profile = diagnostic.context_profile(settings, hook)
    assert profile["state"] == "INSPECTION-ONLY"
    assert "blockers" not in profile
    assert profile["configured_availability"]["enabled_plugin_entries"] == 1
    assert profile["configured_availability"]["mcp_entries_in_this_document"] == 1
    assert all(
        row == {"state": "NOT-OBSERVED", "evidence": []}
        for row in profile["runtime_evidence"].values()
    ), "AVAILABILITY IS NOT RUNTIME EVIDENCE"
    empty_settings = tmp_path / "empty-settings.json"
    empty_settings.write_text("{}")
    empty_profile = diagnostic.context_profile(empty_settings, hook)
    assert empty_profile["state"] == profile["state"]
    assert empty_profile["runtime_evidence"] == profile["runtime_evidence"]
    observer_settings = diagnostic.local_settings(run, hook)
    assert set(observer_settings) == {"hooks"}
    assert set(observer_settings["hooks"]) == {"SessionStart"}
    assert "generic-tool-catalog" not in json.dumps(profile)
    before = (run / "role-attempts.jsonl").read_bytes()
    with pytest.raises(diagnostic.DiagnosticError, match="native launch held"):
        diagnostic.launch(run, settings=settings, hook=hook)
    assert (run / "role-attempts.jsonl").read_bytes() == before
    assert not (run / "launch-claimed.json").exists()
    assert (
        json.loads((run / "events.jsonl").read_text().splitlines()[-1])["event"] == "prelaunch-held"
    )
    (run / "fixture.txt").write_text("arbitrary private project prompt")
    with pytest.raises(diagnostic.DiagnosticError, match="seal mismatch"):
        diagnostic.validate(run)
    (run / "fixture.txt").write_text(diagnostic.FIXTURE)
    # Even internally consistent metadata cannot relabel the fixed candidate.
    registration["candidate_id"] = "foreign-candidate"
    raw = json.dumps(registration)
    (run / "code-registration.json").write_text(raw)
    (run / "role-attempts.jsonl").write_text(raw + "\n")
    sealed = json.loads((run / "diagnostic.json").read_text())
    sealed["registration_sha256"] = diagnostic.digest(raw.encode())
    (run / "diagnostic.json").write_text(json.dumps(sealed))
    with pytest.raises(diagnostic.DiagnosticError, match="seal mismatch"):
        diagnostic.validate(run)
    registration["candidate_id"] = document["fixture_sha256"]
    raw = json.dumps(registration)
    (run / "code-registration.json").write_text(raw)
    (run / "role-attempts.jsonl").write_text(raw + "\n")
    sealed["registration_sha256"] = diagnostic.digest(raw.encode())
    (run / "diagnostic.json").write_text(json.dumps(sealed))
    monkeypatch.setattr(diagnostic.time, "monotonic", lambda: document["boot_monotonic"] + 601)
    with pytest.raises(diagnostic.DiagnosticError, match="deadline expired"):
        diagnostic.validate(run)


def test_diagnostic_uses_real_exec_binding_and_supervisor(tmp_path):
    run = tmp_path / "diagnostic"
    diagnostic.prepare(run, authority="operator-approved synthetic diagnostic")
    document = diagnostic.validate(run)
    _, sha = workflow.review_registration(run / "code-registration.json")
    environment = os.environ.copy()
    environment["DIAGNOSTIC_FORWARD_TEST"] = "present"
    binding = {
        "schema_version": 1,
        "session_id": document["session_id"],
        "cwd": str(run / "workspace"),
        "issued_at": time.time(),
        "expires_at": time.time() + 30,
        "registration_path": str(run / "code-registration.json"),
        "registration_sha256": sha,
    }
    fake = tmp_path / "fake_cli.py"
    fake.write_text(
        "import json,os\n"
        "assert os.environ.get('DIAGNOSTIC_FORWARD_TEST') == 'present', 'BINDING FORWARD'\n"
        "b=json.loads(os.environ['CONTINUATION_REVIEW_BINDING'])\n"
        "assert b['process_session_id']==os.getsid(0)==os.getpid(), 'ACTUAL SID'\n"
        "assert b['cwd']==os.getcwd(), 'ACTUAL CWD'\n"
        "print(json.dumps(b))\n"
    )
    result = diagnostic.supervised_fixture(
        [sys.executable, str(fake)],
        binding,
        cwd=run / "workspace",
        environment=environment,
        timeout=10,
    )
    assert result.returncode == 0, "BINDING FORWARD: " + result.stderr
    assert json.loads(result.stdout)["session_id"] == document["session_id"]
    # Same actual supervisor must kill a hung group and report incomplete evidence.
    result = diagnostic.supervised_fixture(
        [sys.executable, "-c", "import time;time.sleep(30)"],
        binding,
        cwd=run / "workspace",
        environment=environment,
        timeout=0.1,
    )
    assert result.returncode == 124
    assert "INCOMPLETE" in result.stderr
    assert not (run / "observations.jsonl").exists()


def test_diagnostic_observer_requires_exact_native_event(tmp_path, monkeypatch):
    run = tmp_path / "diagnostic"
    diagnostic.prepare(run, authority="operator-approved synthetic diagnostic")
    document = diagnostic.validate(run)
    hook = tmp_path / "synthetic_guard.py"
    marker = tmp_path / "executed"
    hook.write_text(f"from pathlib import Path\nPath({str(marker)!r}).write_text('called')\n")
    monkeypatch.setattr(diagnostic, "HOOK_SHA256", diagnostic.digest(hook.read_bytes()))
    binding = {
        "session_id": document["session_id"],
        "cwd": str(run / "workspace"),
        "process_session_id": os.getsid(0),
        "registration_sha256": document["registration_sha256"],
        "registration_path": str(run / "code-registration.json"),
        "issued_at": time.time(),
        "expires_at": time.time() + 60,
    }
    monkeypatch.setenv("CONTINUATION_REVIEW_BINDING", json.dumps(binding))
    event = {
        "hook_event_name": "SessionStart",
        "source": "compact",
        "cwd": binding["cwd"],
        "session_id": "foreign-session",
    }
    with pytest.raises(diagnostic.DiagnosticError, match="does not match"):
        diagnostic.observe(run, hook, event)
    assert not marker.exists(), "WRONG NATIVE EVENT REACHED GUARD"
    event["session_id"] = document["session_id"]
    diagnostic.observe(run, hook, event)
    row = json.loads((run / "observations.jsonl").read_text())
    assert marker.read_text() == "called"
    assert row["source"] == "compact" and row["empty_stdout"] and row["empty_stderr"]
    assert row["process_session_id"] == os.getsid(0)
    # A hash change cannot quietly substitute another installed guard.
    hook.write_text("print('unqualified context')\n")
    with pytest.raises(diagnostic.DiagnosticError, match="hook changed"):
        diagnostic.observe(run, hook, event)
