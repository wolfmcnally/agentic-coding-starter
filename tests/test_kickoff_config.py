"""Behavioral tests for the universal kickoff configuration manager."""

from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
from agentic_starter import execution_telemetry as telemetry  # noqa: E402

MANAGER = ROOT / "bin" / "kickoff-config"
# Test-owned seed with the shipped-default pins. Never seed from the live
# repo-root kickoff.yaml: it is operator-editable, so tests coupled to its
# content break on every pin change.
SEED_CONFIG = ROOT / "tests" / "fixtures" / "kickoff_config_seed.yaml"
EVIDENCE = ROOT / "bin" / "kickoff-evidence"
UV = shutil.which("uv")
assert UV is not None


def seeded_config(tmp_path: Path) -> Path:
    config = tmp_path / "kickoff.yaml"
    config.write_text(SEED_CONFIG.read_text())
    return config


def run_manager(
    config: Path,
    *arguments: str,
    extra_env: dict[str, str] | None = None,
    cli: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["KICKOFF_CONFIG_FILE"] = str(config)
    # The manager builds the delegated command itself, so a test can only
    # substitute the *binary* it spawns. Everything around it — flags, order,
    # sandbox, artifact wiring — is the production recipe under test.
    if cli is not None:
        environment[f"KICKOFF_CLI_{cli.name.upper()}"] = str(cli)
    environment.pop("KICKOFF_DELEGATION_DEPTH", None)
    if extra_env:
        environment.update(extra_env)
    return subprocess.run(
        [UV, "run", "--script", str(MANAGER), *arguments],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )


def fake_cli(tmp_path: Path, name: str, body: str) -> Path:
    executable = tmp_path / name
    executable.write_text(f"#!/bin/sh\nset -eu\n{body}\n")
    executable.chmod(0o755)
    return executable


def fake_uv(tmp_path: Path) -> Path:
    cache_dir = tmp_path / "uv-cache"
    data_dir = tmp_path / "uv-data"
    return fake_cli(
        tmp_path,
        "uv",
        f"""case "$1 $2" in
  "cache dir") printf '%s\\n' '{cache_dir}' ;;
  "python dir") printf '%s\\n' '{data_dir / "python"}' ;;
  *) exit 2 ;;
esac""",
    )


def artifact_path(tmp_path: Path, venue: str, role: str = "reviewer") -> Path:
    """Where a dispatch's role artifact lands, for stubs that must populate it."""
    return tmp_path / f"artifact-{venue}-{role}.txt"


def routing_arguments(
    tmp_path: Path,
    *,
    venue: str = "claude",
    model: str = "opus",
    effort: str = "high",
    role: str = "reviewer",
    extra: tuple[str, ...] = (),
) -> tuple[str, ...]:
    """Routing metadata plus a prompt, with the venue's artifact flag defaulted.

    The artifact flag is venue-specific by construction — Claude's verdict is
    extracted from its event stream, Codex writes its own `-o` file — so a test
    that does not care supplies neither and gets the right one.
    """
    prompt = tmp_path / f"prompt-{venue}-{role}.md"
    prompt.write_text("Adopt your canonical persona and report.\n")
    artifact_flag = "--result-file" if venue == "claude" else "--required-output-file"
    artifact: tuple[str, ...] = ()
    if artifact_flag not in extra:
        artifact = (artifact_flag, str(artifact_path(tmp_path, venue, role)))
    return (
        "--role",
        role,
        "--venue",
        venue,
        "--model",
        model,
        "--effort",
        effort,
        "--prompt-file",
        str(prompt),
        *artifact,
        *extra,
    )


def watch_arguments(
    tmp_path: Path,
    *,
    venue: str = "claude",
    model: str = "opus",
    effort: str = "high",
    role: str = "reviewer",
    extra_watch: tuple[str, ...] = (),
) -> tuple[str, ...]:
    return (
        "watch",
        *routing_arguments(
            tmp_path,
            venue=venue,
            model=model,
            effort=effort,
            role=role,
            extra=extra_watch,
        ),
        "--phase",
        "test",
        *(() if "--first-event-timeout" in extra_watch else ("--first-event-timeout", "1")),
        *(() if "--idle-timeout" in extra_watch else ("--idle-timeout", "1")),
        *(() if "--hard-timeout" in extra_watch else ("--hard-timeout", "2")),
    )


def read_record(path: Path) -> dict[str, object]:
    return json.loads(path.read_text().splitlines()[-1])


def managed_watch_context(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[telemetry.SpanHandle, Path, Path]:
    spool = tmp_path / "spool"
    monkeypatch.setenv("AGENTIC_STARTER_EXECUTION_TELEMETRY_DIR", str(spool))
    root = telemetry.start_trace(
        engine_root=ROOT,
        scope_root=ROOT,
        scope="engine",
        scope_id="engine",
        run_type="kickoff",
        operation="phase.test",
    )
    setup = telemetry.start_span(
        engine_root=ROOT,
        trace_id=root.trace_id,
        parent_span_id=root.span_id,
        category="reconciliation",
        operation="orchestration.setup",
    )
    run_dir = tmp_path / "run"
    environment = os.environ.copy()
    initialized = subprocess.run(
        [
            str(EVIDENCE),
            "init",
            "--run-dir",
            str(run_dir),
            "--root",
            str(ROOT),
            "--phase",
            "test",
            "--authority",
            "plan/phase-1.md",
            "--telemetry-trace-id",
            root.trace_id,
            "--telemetry-root-span-id",
            root.span_id,
            "--initial-orchestration-span-id",
            setup.span_id,
            "--review-lane",
            "full",
            "--follow-up-route",
            "direct-fix",
        ],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert initialized.returncode == 0, initialized.stderr
    registration = run_dir / "role.json"
    registered = subprocess.run(
        [
            str(run_dir / "tools" / "kickoff-evidence"),
            "register-role-attempt",
            "--run-dir",
            str(run_dir),
            "--operation",
            "role.plan-review",
            "--attempt",
            "1",
            "--role",
            "reviewer",
            "--harness",
            "claude",
            "--model",
            "opus",
            "--effort",
            "high",
            "--reason",
            "initial",
            "--output",
            str(registration),
        ],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert registered.returncode == 0, registered.stderr
    return root, registration, run_dir


def test_show_validates_seed_config(tmp_path: Path) -> None:
    result = run_manager(seeded_config(tmp_path), "show")

    assert result.returncode == 0, result.stderr
    assert "Resolved for this harness" in result.stdout
    assert "claude turns" in result.stdout


def test_scoped_edit_preserves_extensions_comments_and_timeouts(tmp_path: Path) -> None:
    config = seeded_config(tmp_path)
    original = config.read_text().replace(
        "extensions: {}", 'extensions:\n  quoted: "keep me" # preserve this comment'
    )
    config.write_text(original)
    timeout_block = original.split("role_timeouts:", 1)[1]

    result = run_manager(
        config,
        "set-models",
        "claude",
        "reviewer.model=sol",
        "reviewer.effort=medium",
    )

    assert result.returncode == 0, result.stderr
    updated = config.read_text()
    assert 'quoted: "keep me" # preserve this comment' in updated
    assert updated.split("role_timeouts:", 1)[1] == timeout_block
    assert "model: sol" in updated
    assert "effort: medium" in updated


def test_invalid_edit_is_atomic(tmp_path: Path) -> None:
    config = seeded_config(tmp_path)
    before = config.read_bytes()

    result = run_manager(
        config,
        "set-models",
        "codex",
        "reviewer.model=default",
        "reviewer.effort=high",
    )

    assert result.returncode == 2
    assert config.read_bytes() == before


@pytest.mark.parametrize(
    "old,new,expected",
    [
        ("  claude:\n", "  claud:\n", "unknown harness 'claud'"),
        (
            "    critic:\n      model: opus\n",
            "    critc:\n      model: opus\n",
            "unknown role 'critc'",
        ),
        ("      effort: high\n", "      effrot: high\n", "unknown key(s)"),
    ],
)
def test_direct_edit_typos_fail_validation(
    tmp_path: Path, old: str, new: str, expected: str
) -> None:
    config = seeded_config(tmp_path)
    config.write_text(config.read_text().replace(old, new, 1))

    result = run_manager(config, "show")

    assert result.returncode == 2
    assert expected in result.stderr


def test_watch_extracts_fresh_claude_result_and_telemetry(tmp_path: Path) -> None:
    config = seeded_config(tmp_path)
    result_path = tmp_path / "result.txt"
    result_path.write_text("STALE")
    telemetry = tmp_path / "timings.jsonl"
    cli = fake_cli(
        tmp_path,
        "claude",
        'printf \'%s\\n\' \'{"type":"assistant","usage":{"input_tokens":3}}\'\n'
        'printf \'%s\\n\' \'{"type":"result","result":"FRESH",'
        '"usage":{"output_tokens":2}}\'',
    )
    arguments = watch_arguments(
        tmp_path,
        extra_watch=("--result-file", str(result_path)),
    )

    result = run_manager(
        config,
        *arguments,
        extra_env={"KICKOFF_TIMING_LOG": str(telemetry)},
        cli=cli,
    )

    assert result.returncode == 0, result.stderr
    assert result_path.read_text() == "FRESH"
    record = read_record(telemetry)
    assert record["outcome"] == "success"
    assert record["schema_version"] == 3
    assert record["child_exit_code"] == 0
    assert record["artifact_status"] == "fresh"
    assert record["stream_status"] == "complete"
    assert record["program"] == "claude"
    assert "input_tokens" not in record
    assert record["output_tokens"] == 2
    assert record["usage_scope"] == "invocation"


def test_watch_refuses_the_append_only_ledger_as_a_registration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`role-attempts.jsonl` is never a registration, even when it holds one record.

    The ledger is JSON Lines; a one-record ledger is also a valid JSON object, so
    `json.loads` accepts it and the watcher runs. The same argument then dies with
    `Extra data: line 2 column 1` the moment a second role is registered. That
    order-dependence is the defect: an argument that works early and fails later
    teaches the caller the wrong contract and fails at the worst moment. The
    per-attempt file `register-role-attempt --output` writes is the only
    registration, and passing the ledger must be refused the same way every time.
    """
    root, registration, run_dir = managed_watch_context(tmp_path, monkeypatch)
    ledger = run_dir / "role-attempts.jsonl"
    assert len([line for line in ledger.read_text().splitlines() if line.strip()]) == 1
    assert json.loads(ledger.read_text()) == json.loads(registration.read_text())

    cli = fake_cli(tmp_path, "claude", """printf '%s\\n' '{"type":"result","result":"OK"}'""")
    result = run_manager(
        seeded_config(tmp_path),
        *watch_arguments(
            tmp_path,
            extra_watch=(
                "--telemetry-trace-id",
                root.trace_id,
                "--telemetry-parent-span-id",
                root.span_id,
                "--telemetry-operation",
                "role.plan-review",
                "--telemetry-attempt",
                "1",
                "--telemetry-role-registration",
                str(ledger),
            ),
        ),
        extra_env={"AGENTIC_STARTER_EXECUTION_TELEMETRY_DIR": str(tmp_path / "spool")},
        cli=cli,
    )

    assert result.returncode != 0
    combined = result.stdout + result.stderr
    assert "role-attempts.jsonl" in combined
    assert "register-role-attempt --output" in combined
    assert telemetry.closed_spans(engine_root=ROOT, trace_id=root.trace_id) == []


def test_watch_binds_registered_role_to_intelligence_and_wait_spans(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, registration, run_dir = managed_watch_context(tmp_path, monkeypatch)
    event = {
        "type": "result",
        "result": "OK",
        "usage": {"input_tokens": 1, "output_tokens": 2},
    }
    cli = fake_cli(
        tmp_path,
        "claude",
        f"printf '%s\\n' '{json.dumps(event, separators=(',', ':'))}'",
    )
    result = run_manager(
        seeded_config(tmp_path),
        *watch_arguments(
            tmp_path,
            extra_watch=(
                "--telemetry-trace-id",
                root.trace_id,
                "--telemetry-parent-span-id",
                root.span_id,
                "--telemetry-operation",
                "role.plan-review",
                "--telemetry-attempt",
                "1",
                "--telemetry-role-registration",
                str(registration),
            ),
        ),
        extra_env={
            "AGENTIC_STARTER_EXECUTION_TELEMETRY_DIR": str(tmp_path / "spool"),
            "KICKOFF_TIMING_LOG": str(tmp_path / "timings.jsonl"),
        },
        cli=cli,
    )
    assert result.returncode == 0, result.stderr
    spans = telemetry.closed_spans(engine_root=ROOT, trace_id=root.trace_id)
    intelligence = next(item for item in spans if item["category"] == "intelligence")
    wait = next(item for item in spans if item["category"] == "wait")
    assert intelligence["parent_span_id"] == root.span_id
    assert wait["parent_span_id"] == intelligence["span_id"]
    dispatch = json.loads((run_dir / "role-dispatch.jsonl").read_text())
    assert dispatch["accepted"] is True
    assert dispatch["wait_span_id"] == wait["span_id"]


def test_watch_normalizes_child_signal_as_interrupted(tmp_path: Path) -> None:
    telemetry_path = tmp_path / "timings.jsonl"
    cli = fake_cli(tmp_path, "claude", "kill -TERM $$")
    result = run_manager(
        seeded_config(tmp_path),
        *watch_arguments(tmp_path),
        extra_env={"KICKOFF_TIMING_LOG": str(telemetry_path)},
        cli=cli,
    )
    assert result.returncode == 143
    record = read_record(telemetry_path)
    assert record["outcome"] == "interrupted"
    assert record["child_exit_code"] == 143


@pytest.mark.parametrize(
    ("usage", "expected_scope", "expected_tokens"),
    [
        (None, "unavailable", {}),
        (
            {"input_tokens": 0, "output_tokens": 0},
            "invocation",
            {"input_tokens": 0, "output_tokens": 0},
        ),
        ({"input_tokens": -1, "output_tokens": 2.5}, "unavailable", {}),
        ({"input_tokens": "4", "output_tokens": True}, "unavailable", {}),
        ({"output_tokens": 7}, "invocation", {"output_tokens": 7}),
    ],
)
def test_claude_usage_requires_valid_terminal_invocation_fields(
    tmp_path: Path,
    usage: dict[str, object] | None,
    expected_scope: str,
    expected_tokens: dict[str, int],
) -> None:
    event: dict[str, object] = {"type": "result", "result": "OK"}
    if usage is not None:
        event["usage"] = usage
    cli = fake_cli(
        tmp_path,
        "claude",
        f"printf '%s\\n' '{json.dumps(event, separators=(',', ':'))}'",
    )
    timing = tmp_path / "timings.jsonl"
    result = run_manager(
        seeded_config(tmp_path),
        *watch_arguments(tmp_path),
        extra_env={"KICKOFF_TIMING_LOG": str(timing)},
        cli=cli,
    )
    assert result.returncode == 0, result.stderr
    record = read_record(timing)
    assert record["usage_scope"] == expected_scope
    for field in ("input_tokens", "output_tokens"):
        if field in expected_tokens:
            assert record[field] == expected_tokens[field]
        else:
            assert field not in record


def test_codex_cumulative_usage_is_unavailable(tmp_path: Path) -> None:
    timing = tmp_path / "timings.jsonl"
    event = {
        "type": "turn.completed",
        "usage": {"input_tokens": 99, "output_tokens": 44},
    }
    cli = fake_cli(
        tmp_path,
        "codex",
        f"""printf '%s\\n' '{json.dumps(event, separators=(",", ":"))}'
printf '%s' 'CODEX' > {artifact_path(tmp_path, "codex")}""",
    )
    result = run_manager(
        seeded_config(tmp_path),
        *watch_arguments(tmp_path, venue="codex", model="sol", effort="high"),
        extra_env={"KICKOFF_TIMING_LOG": str(timing)},
        cli=cli,
    )
    assert result.returncode == 0, result.stderr
    record = read_record(timing)
    assert record["usage_scope"] == "unavailable"
    assert "input_tokens" not in record and "output_tokens" not in record


@pytest.mark.parametrize(
    "stage",
    [
        "intelligence-start",
        "wait-start",
        "wait-finish",
        "intelligence-finish",
        "span-read",
    ],
)
def test_shared_telemetry_failures_preserve_successful_child_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, stage: str
) -> None:
    root, registration, _ = managed_watch_context(tmp_path, monkeypatch)
    timing = tmp_path / "timings.jsonl"
    cli = fake_cli(
        tmp_path,
        "claude",
        """printf '%s\\n' '{"type":"result","result":"OK","usage":{"input_tokens":1}}'""",
    )
    result = run_manager(
        seeded_config(tmp_path),
        *watch_arguments(
            tmp_path,
            extra_watch=(
                "--telemetry-trace-id",
                root.trace_id,
                "--telemetry-parent-span-id",
                root.span_id,
                "--telemetry-operation",
                "role.plan-review",
                "--telemetry-attempt",
                "1",
                "--telemetry-role-registration",
                str(registration),
            ),
        ),
        extra_env={
            "AGENTIC_STARTER_EXECUTION_TELEMETRY_DIR": str(tmp_path / "spool"),
            "KICKOFF_TIMING_LOG": str(timing),
            "KICKOFF_TELEMETRY_FAIL": stage,
        },
        cli=cli,
    )
    assert result.returncode == 0, result.stderr
    record = read_record(timing)
    assert record["outcome"] == "success"
    assert record["telemetry_complete"] is False
    assert stage in str(record["telemetry_error"])


def test_launched_child_exit_127_keeps_accepted_wait_topology(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, registration, run_dir = managed_watch_context(tmp_path, monkeypatch)
    cli = fake_cli(
        tmp_path,
        "claude",
        """printf '%s\\n' '{"type":"result","result":"FAILED"}'
exit 127""",
    )
    result = run_manager(
        seeded_config(tmp_path),
        *watch_arguments(
            tmp_path,
            extra_watch=(
                "--telemetry-trace-id",
                root.trace_id,
                "--telemetry-parent-span-id",
                root.span_id,
                "--telemetry-operation",
                "role.plan-review",
                "--telemetry-attempt",
                "1",
                "--telemetry-role-registration",
                str(registration),
            ),
        ),
        extra_env={
            "AGENTIC_STARTER_EXECUTION_TELEMETRY_DIR": str(tmp_path / "spool"),
            "KICKOFF_TIMING_LOG": str(tmp_path / "timings.jsonl"),
        },
        cli=cli,
    )
    assert result.returncode == 127
    dispatch = json.loads((run_dir / "role-dispatch.jsonl").read_text())
    assert dispatch["accepted"] is True and dispatch["wait_span_id"]
    validated = subprocess.run(
        [
            str(run_dir / "tools" / "kickoff-evidence"),
            "validate",
            "--run-dir",
            str(run_dir),
        ],
        cwd=ROOT,
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        check=False,
    )
    assert validated.returncode == 0, validated.stderr


def test_wait_start_failure_with_child_exit_127_blocks_role_join(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, registration, run_dir = managed_watch_context(tmp_path, monkeypatch)
    cli = fake_cli(
        tmp_path,
        "claude",
        """printf '%s\\n' '{"type":"result","result":"FAILED"}'
exit 127""",
    )
    result = run_manager(
        seeded_config(tmp_path),
        *watch_arguments(
            tmp_path,
            extra_watch=(
                "--telemetry-trace-id",
                root.trace_id,
                "--telemetry-parent-span-id",
                root.span_id,
                "--telemetry-operation",
                "role.plan-review",
                "--telemetry-attempt",
                "1",
                "--telemetry-role-registration",
                str(registration),
            ),
        ),
        extra_env={
            "AGENTIC_STARTER_EXECUTION_TELEMETRY_DIR": str(tmp_path / "spool"),
            "KICKOFF_TIMING_LOG": str(tmp_path / "timings.jsonl"),
            "KICKOFF_TELEMETRY_FAIL": "wait-start",
        },
        cli=cli,
    )
    assert result.returncode == 127
    rejected = subprocess.run(
        [
            str(run_dir / "tools" / "kickoff-evidence"),
            "validate",
            "--run-dir",
            str(run_dir),
        ],
        cwd=ROOT,
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        check=False,
    )
    assert rejected.returncode == 2
    assert "nested wait span" in rejected.stderr


def test_local_diagnostic_write_failure_preserves_child_result(tmp_path: Path) -> None:
    target = tmp_path / "timing-directory"
    target.mkdir()
    cli = fake_cli(
        tmp_path,
        "claude",
        """printf '%s\\n' '{"type":"result","result":"OK"}'""",
    )
    result = run_manager(
        seeded_config(tmp_path),
        *watch_arguments(tmp_path),
        extra_env={"KICKOFF_TIMING_LOG": str(target)},
        cli=cli,
    )
    assert result.returncode == 0
    assert "local timing diagnostic write failed" in result.stderr


def process_exists(process_id: int) -> bool:
    try:
        os.kill(process_id, 0)
        return True
    except ProcessLookupError:
        return False


def stubborn_descendant_cli(tmp_path: Path, pid_file: Path) -> Path:
    return fake_cli(
        tmp_path,
        "claude",
        f"""( trap '' TERM; echo $$ > {pid_file}; while :; do sleep 1; done ) &
printf '%s\\n' '{{"type":"assistant","message":{{"content":"working"}}}}'
exit 0""",
    )


def test_timeout_kills_descendant_after_group_leader_exits(tmp_path: Path) -> None:
    pid_file = tmp_path / "descendant.pid"
    cli = stubborn_descendant_cli(tmp_path, pid_file)
    result = run_manager(
        seeded_config(tmp_path),
        *watch_arguments(
            tmp_path,
            extra_watch=(
                "--hard-timeout",
                "0.2",
                "--idle-timeout",
                "0.1",
                "--first-event-timeout",
                "1",
            ),
        ),
        extra_env={"KICKOFF_TIMING_LOG": str(tmp_path / "timings.jsonl")},
        cli=cli,
    )
    assert result.returncode == 124, result.stderr
    descendant = int(pid_file.read_text())
    deadline = time.monotonic() + 2
    while process_exists(descendant) and time.monotonic() < deadline:
        time.sleep(0.02)
    assert not process_exists(descendant)


def test_wrapper_signal_kills_sigterm_resistant_descendant(tmp_path: Path) -> None:
    pid_file = tmp_path / "descendant.pid"
    cli = stubborn_descendant_cli(tmp_path, pid_file)
    config = seeded_config(tmp_path)
    environment = os.environ.copy()
    environment.update(
        {
            "KICKOFF_CONFIG_FILE": str(config),
            "KICKOFF_TIMING_LOG": str(tmp_path / "timings.jsonl"),
            f"KICKOFF_CLI_{cli.name.upper()}": str(cli),
        }
    )
    environment.pop("KICKOFF_DELEGATION_DEPTH", None)
    process = subprocess.Popen(
        [str(MANAGER), *watch_arguments(tmp_path)],
        cwd=ROOT,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    deadline = time.monotonic() + 2
    while not pid_file.exists() and time.monotonic() < deadline:
        time.sleep(0.02)
    assert pid_file.exists()
    process.send_signal(signal.SIGTERM)
    stdout, stderr = process.communicate(timeout=10)
    assert process.returncode == 143, (stdout, stderr)
    descendant = int(pid_file.read_text())
    deadline = time.monotonic() + 2
    while process_exists(descendant) and time.monotonic() < deadline:
        time.sleep(0.02)
    assert not process_exists(descendant)


def test_watch_preserves_claude_artifact_when_terminal_stream_is_incomplete(
    tmp_path: Path,
) -> None:
    config = seeded_config(tmp_path)
    result_path = tmp_path / "result.txt"
    telemetry = tmp_path / "timings.jsonl"
    cli = fake_cli(
        tmp_path,
        "claude",
        "printf '%s\\n' "
        """'{"type":"assistant","message":{"content":[{"type":"text","text":"RECOVER"}]}}'""",
    )
    arguments = watch_arguments(
        tmp_path,
        extra_watch=("--result-file", str(result_path)),
    )

    result = run_manager(
        config,
        *arguments,
        extra_env={"KICKOFF_TIMING_LOG": str(telemetry)},
        cli=cli,
    )

    assert result.returncode == 66
    assert result_path.read_text() == "RECOVER"
    assert "explicit artifact verification required" in result.stderr
    record = read_record(telemetry)
    assert record["outcome"] == "completed_unverified_protocol"
    assert record["child_exit_code"] == 0
    assert record["artifact_status"] == "fresh"
    assert record["stream_status"] == "incomplete"


def test_watch_rejects_fast_exit_without_structured_event_and_clears_result(
    tmp_path: Path,
) -> None:
    config = seeded_config(tmp_path)
    result_path = tmp_path / "result.txt"
    result_path.write_text("STALE VERDICT")
    telemetry = tmp_path / "timings.jsonl"
    cli = fake_cli(tmp_path, "claude", "printf '%s\\n' 'plain output'")
    arguments = watch_arguments(
        tmp_path,
        extra_watch=("--result-file", str(result_path)),
    )

    result = run_manager(
        config,
        *arguments,
        extra_env={"KICKOFF_TIMING_LOG": str(telemetry)},
        cli=cli,
    )

    assert result.returncode == 65
    assert result_path.read_text() == ""
    assert "no structured stdout event" in result.stderr
    assert "required output artifact missing or empty" in result.stderr
    assert "terminal stream event missing or empty" in result.stderr
    record = read_record(telemetry)
    assert record["outcome"] == "error"
    assert record["protocol_error"]


def test_watch_requires_fresh_codex_output_artifact(tmp_path: Path) -> None:
    config = seeded_config(tmp_path)
    output_path = tmp_path / "last-message.txt"
    output_path.write_text("STALE VERDICT")
    telemetry = tmp_path / "timings.jsonl"
    cli = fake_cli(tmp_path, "codex", "printf '%s\\n' '{\"type\":\"thread.started\"}'")
    arguments = watch_arguments(
        tmp_path,
        venue="codex",
        model="codex",
        effort="default",
        extra_watch=("--required-output-file", str(output_path)),
    )

    result = run_manager(
        config,
        *arguments,
        extra_env={"KICKOFF_TIMING_LOG": str(telemetry)},
        cli=cli,
    )

    assert result.returncode == 65
    assert output_path.read_text() == ""
    assert "required output artifact missing or empty" in result.stderr


def test_watch_accepts_its_own_generated_codex_routing(tmp_path: Path) -> None:
    """The generated command must satisfy the routing validator it feeds.

    The validator predates generation: it existed to catch hand-built commands
    whose flags contradicted the telemetry metadata. Keeping it in the path
    turns it into the generator's own proof.
    """
    config = seeded_config(tmp_path)
    output_path = tmp_path / "last-message.txt"
    telemetry = tmp_path / "timings.jsonl"
    cli = fake_cli(
        tmp_path,
        "codex",
        f"printf '%s\\n' '{{\"type\":\"thread.started\"}}'\n"
        f"printf '%s\\n' '{{\"type\":\"turn.completed\"}}'\n"
        f"printf '%s' 'CODEX FRESH' > {output_path}",
    )
    arguments = watch_arguments(
        tmp_path,
        venue="codex",
        model="sol",
        effort="medium",
        extra_watch=("--required-output-file", str(output_path)),
    )

    result = run_manager(
        config,
        *arguments,
        extra_env={"KICKOFF_TIMING_LOG": str(telemetry)},
        cli=cli,
    )

    assert result.returncode == 0, result.stderr
    assert output_path.read_text() == "CODEX FRESH"
    record = read_record(telemetry)
    assert record["program"] == "codex"
    assert record["stream_status"] == "complete"


def test_watch_injects_codex_workspace_write_uv_support(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("UV_NO_SYNC", raising=False)
    fake_uv(tmp_path)
    captured_environment = tmp_path / "environment.txt"
    captured_arguments = tmp_path / "arguments.txt"
    cli = fake_cli(
        tmp_path,
        "codex",
        """printf '%s\\n' "${UV_NO_SYNC-unset}" > "$CAPTURE_ENVIRONMENT"
printf '%s\\n' "$@" > "$CAPTURE_ARGUMENTS"
printf '%s' 'CODEX' > "$CAPTURE_ARTIFACT"
printf '%s\\n' '{"type":"thread.started"}'
printf '%s\\n' '{"type":"turn.completed"}'""",
    )
    result = run_manager(
        seeded_config(tmp_path),
        # Only the coder is write-enabled, and the access mode is derived from
        # the role rather than passed in, so this is the one dispatch that can
        # reach workspace-write at all.
        *watch_arguments(
            tmp_path,
            venue="codex",
            model="sol",
            effort="medium",
            role="coder",
        ),
        extra_env={
            "PATH": f"{tmp_path}:{os.environ['PATH']}",
            "CAPTURE_ENVIRONMENT": str(captured_environment),
            "CAPTURE_ARGUMENTS": str(captured_arguments),
            "CAPTURE_ARTIFACT": str(artifact_path(tmp_path, "codex", "coder")),
        },
        cli=cli,
    )

    assert result.returncode == 0, result.stderr
    assert captured_environment.read_text() == "1\n"
    arguments = captured_arguments.read_text().splitlines()
    writable_roots = [
        item for item in arguments if item.startswith("sandbox_workspace_write.writable_roots=")
    ]
    assert len(writable_roots) == 1
    assert str(tmp_path / "uv-cache") in writable_roots[0]
    assert str(tmp_path / "uv-data") in writable_roots[0]
    assert (
        "injected codex workspace-write support: "
        "UV_NO_SYNC=1, sandbox_workspace_write.writable_roots"
    ) in result.stderr


def test_watch_does_not_inject_uv_support_for_read_only_codex(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("UV_NO_SYNC", raising=False)
    captured_environment = tmp_path / "environment.txt"
    captured_arguments = tmp_path / "arguments.txt"
    cli = fake_cli(
        tmp_path,
        "codex",
        """printf '%s\\n' "${UV_NO_SYNC-unset}" > "$CAPTURE_ENVIRONMENT"
printf '%s\\n' "$@" > "$CAPTURE_ARGUMENTS"
printf '%s' 'CODEX' > "$CAPTURE_ARTIFACT"
printf '%s\\n' '{"type":"thread.started"}'
printf '%s\\n' '{"type":"turn.completed"}'""",
    )
    result = run_manager(
        seeded_config(tmp_path),
        *watch_arguments(tmp_path, venue="codex", model="sol", effort="medium"),
        extra_env={
            "CAPTURE_ENVIRONMENT": str(captured_environment),
            "CAPTURE_ARGUMENTS": str(captured_arguments),
            "CAPTURE_ARTIFACT": str(artifact_path(tmp_path, "codex", "reviewer")),
        },
        cli=cli,
    )

    assert result.returncode == 0, result.stderr
    assert captured_environment.read_text() == "unset\n"
    assert "sandbox_workspace_write.writable_roots=" not in captured_arguments.read_text()
    assert "injected codex workspace-write support" not in result.stderr


def test_resumed_codex_coder_keeps_its_workspace_write_uv_support(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A revision round is as sandbox-bound as the initial call.

    `resume` carries its sandbox as a `sandbox_mode` config override rather than
    `-s`, so a detector reading only the flag spelling would drop the uv support
    on round two — the delegated coder would then run zero gates while reporting
    a clean build, exactly as it did before the injection existed.
    """
    monkeypatch.delenv("UV_NO_SYNC", raising=False)
    fake_uv(tmp_path)
    captured_arguments = tmp_path / "arguments.txt"
    captured_environment = tmp_path / "environment.txt"
    cli = fake_cli(
        tmp_path,
        "codex",
        """printf '%s\\n' "${UV_NO_SYNC-unset}" > "$CAPTURE_ENVIRONMENT"
printf '%s\\n' "$@" > "$CAPTURE_ARGUMENTS"
printf '%s' 'CODEX' > "$CAPTURE_ARTIFACT"
printf '%s\\n' '{"type":"thread.started"}'
printf '%s\\n' '{"type":"turn.completed"}'""",
    )
    result = run_manager(
        seeded_config(tmp_path),
        *watch_arguments(
            tmp_path,
            venue="codex",
            model="sol",
            effort="medium",
            role="coder",
            extra_watch=("--resume-session", "01JABCDEF"),
        ),
        extra_env={
            "PATH": f"{tmp_path}:{os.environ['PATH']}",
            "CAPTURE_ENVIRONMENT": str(captured_environment),
            "CAPTURE_ARGUMENTS": str(captured_arguments),
            "CAPTURE_ARTIFACT": str(artifact_path(tmp_path, "codex", "coder")),
        },
        cli=cli,
    )

    assert result.returncode == 0, result.stderr
    assert captured_environment.read_text() == "1\n"
    arguments = captured_arguments.read_text().splitlines()
    assert arguments[:3] == ["exec", "resume", "01JABCDEF"]
    # The override sits after the session id, not between `exec` and `resume`,
    # where it would not parse.
    roots = next(
        index
        for index, item in enumerate(arguments)
        if item.startswith("sandbox_workspace_write.writable_roots=")
    )
    assert roots > 3
    assert "-s" not in arguments and "-C" not in arguments
    assert 'sandbox_mode="workspace-write"' in arguments


def test_watch_preserves_codex_artifact_when_terminal_stream_is_incomplete(
    tmp_path: Path,
) -> None:
    config = seeded_config(tmp_path)
    output_path = tmp_path / "last-message.txt"
    telemetry = tmp_path / "timings.jsonl"
    cli = fake_cli(
        tmp_path,
        "codex",
        f"printf '%s\\n' '{{\"type\":\"thread.started\"}}'\n"
        f"printf '%s' 'CODEX RECOVER' > {output_path}",
    )
    arguments = watch_arguments(
        tmp_path,
        venue="codex",
        model="sol",
        effort="medium",
        extra_watch=("--required-output-file", str(output_path)),
    )

    result = run_manager(
        config,
        *arguments,
        extra_env={"KICKOFF_TIMING_LOG": str(telemetry)},
        cli=cli,
    )

    assert result.returncode == 66
    assert output_path.read_text() == "CODEX RECOVER"
    record = read_record(telemetry)
    assert record["outcome"] == "completed_unverified_protocol"
    assert record["artifact_status"] == "fresh"
    assert record["stream_status"] == "incomplete"


def test_watch_preserves_nonzero_child_status_even_with_valid_artifact(
    tmp_path: Path,
) -> None:
    config = seeded_config(tmp_path)
    result_path = tmp_path / "result.txt"
    telemetry = tmp_path / "timings.jsonl"
    cli = fake_cli(
        tmp_path,
        "claude",
        """printf '%s\n' '{"type":"result","result":"FAILED RESULT"}'
exit 23""",
    )
    arguments = watch_arguments(
        tmp_path,
        extra_watch=("--result-file", str(result_path)),
    )

    result = run_manager(
        config,
        *arguments,
        extra_env={"KICKOFF_TIMING_LOG": str(telemetry)},
        cli=cli,
    )

    assert result.returncode == 23
    assert result_path.read_text() == "FAILED RESULT"
    record = read_record(telemetry)
    assert record["outcome"] == "error"
    assert record["child_exit_code"] == 23
    assert record["artifact_status"] == "fresh"
    assert record["stream_status"] == "complete"


def test_watch_rejects_a_model_that_does_not_route_to_its_venue(tmp_path: Path) -> None:
    """A venue/model contradiction cannot be papered over by generating anyway."""
    config = seeded_config(tmp_path)
    marker = tmp_path / "launched"
    cli = fake_cli(tmp_path, "claude", f"touch {marker}")
    arguments = watch_arguments(tmp_path, venue="claude", model="sol", effort="high")

    result = run_manager(config, *arguments, cli=cli)

    assert result.returncode == 2
    assert "does not route to the claude CLI" in result.stderr
    assert not marker.exists()


def test_watch_refuses_to_delegate_from_inside_a_delegated_session(
    tmp_path: Path,
) -> None:
    """The recursion guard is a refusal, not a convention.

    `KICKOFF_DELEGATION_DEPTH` set means this process *is* a delegated role.
    A second hop would spend another vendor's quota on a role the parent
    already resolved as native, so the dispatch dies before launch.
    """
    config = seeded_config(tmp_path)
    marker = tmp_path / "launched"
    cli = fake_cli(tmp_path, "claude", f"touch {marker}")

    result = run_manager(
        config,
        *watch_arguments(tmp_path),
        extra_env={"KICKOFF_DELEGATION_DEPTH": "1"},
        cli=cli,
    )

    assert result.returncode == 2
    assert "may not delegate again" in result.stderr
    assert not marker.exists()


def test_watch_rejects_zero_timeout_override_before_launch(tmp_path: Path) -> None:
    config = seeded_config(tmp_path)
    marker = tmp_path / "launched"
    cli = fake_cli(tmp_path, "claude", f"touch {marker}")
    arguments = list(watch_arguments(tmp_path))
    index = arguments.index("--first-event-timeout") + 1
    arguments[index] = "0"

    result = run_manager(config, *arguments, cli=cli)

    assert result.returncode == 2
    assert "first-event timeout must be positive" in result.stderr
    assert not marker.exists()


def test_watch_enforces_first_event_timeout(tmp_path: Path) -> None:
    config = seeded_config(tmp_path)
    telemetry = tmp_path / "timings.jsonl"
    cli = fake_cli(
        tmp_path,
        "claude",
        "sleep 0.4\nprintf '%s\\n' '{\"type\":\"assistant\"}'",
    )
    arguments = list(watch_arguments(tmp_path))
    arguments[arguments.index("--first-event-timeout") + 1] = "0.1"

    result = run_manager(
        config,
        *arguments,
        extra_env={"KICKOFF_TIMING_LOG": str(telemetry)},
        cli=cli,
    )

    assert result.returncode == 124
    record = read_record(telemetry)
    assert record["timeout_kind"] == "first-event"
    assert record["child_exit_code"] is None


def test_watch_enforces_idle_timeout_after_first_event(tmp_path: Path) -> None:
    config = seeded_config(tmp_path)
    telemetry = tmp_path / "timings.jsonl"
    cli = fake_cli(
        tmp_path,
        "claude",
        "printf '%s\\n' '{\"type\":\"assistant\"}'\nsleep 0.4",
    )
    arguments = list(watch_arguments(tmp_path))
    arguments[arguments.index("--idle-timeout") + 1] = "0.1"

    result = run_manager(
        config,
        *arguments,
        extra_env={"KICKOFF_TIMING_LOG": str(telemetry)},
        cli=cli,
    )

    assert result.returncode == 124
    record = read_record(telemetry)
    assert record["timeout_kind"] == "idle"
    assert record["child_exit_code"] is None


def rendered(
    tmp_path: Path, **routing: object
) -> tuple[list[str], subprocess.CompletedProcess[str]]:
    result = run_manager(
        seeded_config(tmp_path),
        "render-command",
        *routing_arguments(tmp_path, **routing),  # type: ignore[arg-type]
        "--json",
    )
    if result.returncode != 0:
        return [], result
    return json.loads(result.stdout), result


class TestGeneratedInvocationRecipes:
    """The recipes themselves, pinned as argv rather than as prose.

    Each of these flags earned its place by failing without it. They lived in a
    brief where every orchestrator retyped them, and each retyping was free to
    drop one silently — the failure mode that makes this class the point of
    CH-13 rather than incidental coverage.
    """

    def test_claude_review_recipe(self, tmp_path: Path) -> None:
        command, result = rendered(tmp_path, venue="claude", model="opus", effort="high")
        assert result.returncode == 0, result.stderr

        assert command[0] == "claude"
        assert command[1] == "-p"
        assert command[2].startswith("Adopt your canonical persona")
        assert command[3:7] == ["--model", "opus", "--effort", "high"]
        # `dontAsk` is the only fully non-interactive mode. The "dangerous"
        # bypass still parks on a one-time consent dialog that never returns
        # without a TTY.
        assert "--permission-mode" in command
        assert command[command.index("--permission-mode") + 1] == "dontAsk"
        assert "--dangerously-skip-permissions" not in command
        assert command[command.index("--allowedTools") + 1] == "Read,Grep,Glob"
        # Progress-aware supervision: the first-event and idle clocks measure
        # real activity only if the child emits structured events.
        assert command[command.index("--output-format") + 1] == "stream-json"
        assert "--verbose" in command
        assert command[command.index("--max-turns") + 1] == "50"

    def test_claude_coder_is_the_only_write_enabled_role(self, tmp_path: Path) -> None:
        coder, _ = rendered(tmp_path, venue="claude", model="opus", role="coder")
        assert coder[coder.index("--allowedTools") + 1] == "Read,Grep,Glob,Write,Edit,Bash"
        assert coder[coder.index("--max-turns") + 1] == "200"

        for role in ("planner", "reviewer", "critic"):
            command, _ = rendered(tmp_path, venue="claude", model="opus", role=role)
            assert command[command.index("--allowedTools") + 1] == "Read,Grep,Glob"

    def test_claude_resume_repeats_model_and_effort(self, tmp_path: Path) -> None:
        command, _ = rendered(
            tmp_path,
            venue="claude",
            model="fable",
            effort="max",
            extra=("--resume-session", "sess-9"),
        )
        assert command[command.index("--resume") + 1] == "sess-9"
        # Repeated, not inherited: a resume that omits them lets the role change
        # model or effort mid-stage.
        assert command[command.index("--model") + 1] == "fable"
        assert command[command.index("--effort") + 1] == "max"

    def test_codex_exec_recipe(self, tmp_path: Path) -> None:
        command, result = rendered(tmp_path, venue="codex", model="sol", effort="medium")
        assert result.returncode == 0, result.stderr

        assert command[:3] == ["codex", "exec", "--json"]
        # `--json` is what makes the session id recoverable at all: the
        # human-readable mode prints it only to stderr, which is redirected.
        assert command[command.index("-s") + 1] == "read-only"
        assert 'approval_policy="never"' in command
        assert command[command.index("-C") + 1] == str(ROOT)
        assert command[command.index("--output-last-message") + 1].endswith(".txt")
        assert command[command.index("--model") + 1] == "gpt-5.6-sol"
        assert 'model_reasoning_effort="medium"' in command
        assert command[-1].startswith("Adopt your canonical persona")
        # The production checkout call must never carry the preflight's probe flag.
        assert "--skip-git-repo-check" not in command

    def test_codex_resume_drops_the_flags_resume_does_not_accept(self, tmp_path: Path) -> None:
        command, _ = rendered(
            tmp_path,
            venue="codex",
            model="sol",
            effort="medium",
            role="coder",
            extra=("--resume-session", "01JXYZ"),
        )
        assert command[:4] == ["codex", "exec", "resume", "01JXYZ"]
        # `resume` rejects `-s` and `-C` outright; reusing the exec flags
        # flag-parse-fails and silently costs the session's whole context.
        assert "-s" not in command and "-C" not in command
        assert 'sandbox_mode="workspace-write"' in command
        assert command[command.index("--model") + 1] == "gpt-5.6-sol"
        assert 'model_reasoning_effort="medium"' in command

    def test_turn_cap_tracks_the_configuration_not_the_generator(self, tmp_path: Path) -> None:
        """CH-2's operator ruling is read from kickoff.yaml, never hardcoded."""
        config = seeded_config(tmp_path)
        config.write_text(
            config.read_text().replace(
                "      claude_max_turns: 50", "      claude_max_turns: 137", 1
            )
        )
        result = run_manager(
            config,
            "render-command",
            *routing_arguments(tmp_path, venue="claude", model="opus", role="planner"),
            "--json",
        )
        assert result.returncode == 0, result.stderr
        command = json.loads(result.stdout)
        assert command[command.index("--max-turns") + 1] == "137"

    @pytest.mark.parametrize(
        ("venue", "model", "wrong_flag", "remedy"),
        [
            ("claude", "opus", "--required-output-file", "--result-file"),
            ("codex", "sol", "--result-file", "--required-output-file"),
        ],
    )
    def test_artifact_wiring_is_venue_specific(
        self, tmp_path: Path, venue: str, model: str, wrong_flag: str, remedy: str
    ) -> None:
        """Claude's verdict comes from its stream; Codex writes its own file.

        Crossing them yields a dispatch that always reports a missing artifact,
        so the mismatch is refused, and the refusal names the right flag.
        """
        _, result = rendered(
            tmp_path,
            venue=venue,
            model=model,
            extra=(wrong_flag, str(tmp_path / "wrong.txt")),
        )
        assert result.returncode == 2
        assert f"use {remedy}" in result.stderr

    @pytest.mark.parametrize("venue,model", [("claude", "opus"), ("codex", "sol")])
    def test_missing_artifact_path_is_refused(self, tmp_path: Path, venue: str, model: str) -> None:
        prompt = tmp_path / "prompt.md"
        prompt.write_text("go\n")
        result = run_manager(
            seeded_config(tmp_path),
            "render-command",
            "--role",
            "reviewer",
            "--venue",
            venue,
            "--model",
            model,
            "--prompt-file",
            str(prompt),
        )
        assert result.returncode == 2
        assert "requires" in result.stderr

    def test_empty_prompt_is_refused(self, tmp_path: Path) -> None:
        prompt = tmp_path / "prompt.md"
        prompt.write_text("   \n")
        result = run_manager(
            seeded_config(tmp_path),
            "render-command",
            "--role",
            "reviewer",
            "--venue",
            "claude",
            "--model",
            "opus",
            "--prompt-file",
            str(prompt),
            "--result-file",
            str(tmp_path / "out.txt"),
        )
        assert result.returncode == 2
        assert "prompt file is empty" in result.stderr


class TestStructuredOutputWiring:
    """The Finding Evidence envelope is constrained where it is produced.

    Validation used to run after the reviewing agent had exited, so the cheapest
    repair — one more turn saying "invalid severity, re-emit" — was unavailable,
    and one invented token cost a whole review three times in a single phase. An
    enum cannot emit `major`; a JSON payload has no markdown envelope.
    """

    def test_codex_review_dispatch_carries_a_schema_file(self, tmp_path: Path) -> None:
        command, result = rendered(
            tmp_path, venue="codex", model="sol", effort="high", role="critic"
        )
        assert result.returncode == 0, result.stderr
        schema_path = Path(command[command.index("--output-schema") + 1])
        assert schema_path.is_file(), "codex takes a schema file, so one must exist"
        document = json.loads(schema_path.read_text())
        assert document["title"] == "agentic-starter-code-review"
        # Beside the artifact rather than in scratch: after a failed dispatch the
        # schema is evidence about what the role was asked for.
        assert schema_path.parent == artifact_path(tmp_path, "codex", "critic").parent

    def test_claude_review_dispatch_carries_the_schema_inline(self, tmp_path: Path) -> None:
        command, result = rendered(
            tmp_path, venue="claude", model="opus", effort="high", role="reviewer"
        )
        assert result.returncode == 0, result.stderr
        document = json.loads(command[command.index("--json-schema") + 1])
        assert document["title"] == "agentic-starter-plan-review"
        assert document["properties"]["verdict"]["enum"] == ["APPROVED", "REVISE"]

    @pytest.mark.parametrize("role,kind", [("reviewer", "plan"), ("critic", "code")])
    def test_each_review_role_gets_its_own_kind(self, tmp_path: Path, role: str, kind: str) -> None:
        command, _ = rendered(tmp_path, venue="claude", model="opus", role=role)
        document = json.loads(command[command.index("--json-schema") + 1])
        assert document["title"] == f"agentic-starter-{kind}-review"
        described = document["properties"]["findings"]["items"]["properties"]["id"]
        assert described["description"].startswith(kind.upper() + "-F")

    @pytest.mark.parametrize("venue,model", [("claude", "opus"), ("codex", "sol")])
    @pytest.mark.parametrize("role", ("planner", "coder"))
    def test_non_review_roles_carry_no_schema(
        self, tmp_path: Path, venue: str, model: str, role: str
    ) -> None:
        """The planner emits a plan and the coder emits Change Evidence.

        Constraining them to a findings document would make the dispatch
        structurally unable to return its own artifact.
        """
        command, result = rendered(tmp_path, venue=venue, model=model, role=role)
        assert result.returncode == 0, result.stderr
        assert "--json-schema" not in command
        assert "--output-schema" not in command

    def test_a_resumed_review_keeps_its_schema(self, tmp_path: Path) -> None:
        """A revision round is as constrained as the first pass.

        Dropping it on resume would reinstate the failure mode for exactly the
        rounds that follow a REVISE — the ones that already cost the most.
        """
        command, _ = rendered(
            tmp_path,
            venue="codex",
            model="sol",
            role="critic",
            extra=("--resume-session", "01JRESUME"),
        )
        assert command[:4] == ["codex", "exec", "resume", "01JRESUME"]
        assert "--output-schema" in command

    def test_the_schema_matches_the_evidence_tools_export(self, tmp_path: Path) -> None:
        """The venue boundary and the validator read one definition.

        If these could differ, a venue could be constrained to emit something the
        validator rejects — the CH-12 failure with an extra step.
        """
        command, _ = rendered(tmp_path, venue="claude", model="opus", role="critic")
        wired = json.loads(command[command.index("--json-schema") + 1])
        exported = subprocess.run(
            [str(ROOT / "bin" / "kickoff-evidence"), "schema", "--kind", "code"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert exported.returncode == 0, exported.stderr
        assert wired == json.loads(exported.stdout)


@pytest.mark.parametrize(
    ("venue", "model", "scrubbed"),
    [
        ("claude", "opus", ("ANTHROPIC_API_KEY", "CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT")),
        ("codex", "sol", ("OPENAI_API_KEY", "CODEX_API_KEY")),
    ],
)
def test_watch_scrubs_credentials_and_marks_delegation_depth(
    tmp_path: Path, venue: str, model: str, scrubbed: tuple[str, ...]
) -> None:
    """The scrub happens at the spawn point, not in the caller's shell.

    Both CLIs rank an environment API key above their subscription OAuth, so an
    inherited stray key silently flips billing or fails 401 while the CLI's own
    status display still reports the subscription login.
    """
    captured = tmp_path / "environment.txt"
    body = 'printf "%s\\n" "${UV_NO_SYNC-x}" >/dev/null\nenv > "$CAPTURE_ENVIRONMENT"\n'
    if venue == "claude":
        body += """printf '%s\\n' '{"type":"result","result":"OK"}'"""
    else:
        body += (
            f"printf '%s' 'CODEX' > {artifact_path(tmp_path, 'codex')}\n"
            """printf '%s\\n' '{"type":"thread.started"}'\n"""
            """printf '%s\\n' '{"type":"turn.completed"}'"""
        )
    cli = fake_cli(tmp_path, venue, body)

    result = run_manager(
        seeded_config(tmp_path),
        *watch_arguments(tmp_path, venue=venue, model=model, effort="high"),
        extra_env={
            "CAPTURE_ENVIRONMENT": str(captured),
            **{key: "leaked-value" for key in scrubbed},
        },
        cli=cli,
    )

    assert result.returncode == 0, result.stderr
    child_environment = dict(
        line.split("=", 1) for line in captured.read_text().splitlines() if "=" in line
    )
    for key in scrubbed:
        assert key not in child_environment, f"{key} reached the delegated child"
    assert child_environment["KICKOFF_DELEGATION_DEPTH"] == "1"


def test_recommend_timeouts_reads_successful_records_without_rewriting_config(
    tmp_path: Path,
) -> None:
    config = seeded_config(tmp_path)
    config.write_text(
        config.read_text().replace(
            "minimum_samples_for_recalibration: 30", "minimum_samples_for_recalibration: 1"
        )
    )
    telemetry = tmp_path / "timings.jsonl"
    telemetry.write_text(
        json.dumps(
            {
                "schema_version": 3,
                "role": "reviewer",
                "venue": "claude",
                "model": "opus",
                "effort": "high",
                "outcome": "success",
                "telemetry_complete": True,
                "duration_ns": 10_000_000_000,
                "longest_idle_seconds": 2,
            },
            separators=(",", ":"),
        )
        + "\n"
    )
    before = config.read_bytes()

    result = run_manager(
        config,
        "recommend-timeouts",
        extra_env={"KICKOFF_TIMING_LOG": str(telemetry)},
    )

    assert result.returncode == 0, result.stderr
    assert "reviewer/claude model=opus effort=high n=1" in result.stdout
    assert config.read_bytes() == before


def test_recommend_timeouts_excludes_incomplete_and_malformed_schema3(
    tmp_path: Path,
) -> None:
    config = seeded_config(tmp_path)
    config.write_text(
        config.read_text().replace(
            "minimum_samples_for_recalibration: 30",
            "minimum_samples_for_recalibration: 1",
        )
    )
    telemetry_path = tmp_path / "timings.jsonl"
    rows = [
        {
            "schema_version": 3,
            "role": "reviewer",
            "venue": "claude",
            "model": "opus",
            "effort": "high",
            "outcome": "success",
            "telemetry_complete": False,
            "duration_ns": None,
            "longest_idle_seconds": 1,
        },
        {
            "schema_version": 3,
            "role": "reviewer",
            "venue": "claude",
            "model": "opus",
            "effort": "high",
            "outcome": "success",
            "telemetry_complete": True,
            "duration_ns": "bad",
            "longest_idle_seconds": "bad",
        },
    ]
    telemetry_path.write_text(
        "".join(json.dumps(row, separators=(",", ":")) + "\n" for row in rows)
    )
    result = run_manager(
        config,
        "recommend-timeouts",
        extra_env={"KICKOFF_TIMING_LOG": str(telemetry_path)},
    )
    assert result.returncode == 0
    assert "No group" in result.stdout
    assert result.stderr.count("incomplete/malformed") == 2


def test_the_manager_runs_where_git_is_absent(tmp_path: Path) -> None:
    """A copy of the engine without `.git` must still be operable.

    `main` asked git for the repository toplevel to reach a root the module had
    already resolved from its own location. Inside a Gate 9 worker copy, which
    carries no `.git` by design, that killed every invocation on a
    CalledProcessError traceback before argument parsing — and because the
    failing rows sat past the battery's first stop, the whole class stayed
    invisible for a full run.
    """
    copy = tmp_path / "engine"
    (copy / "bin").mkdir(parents=True)
    (copy / "lib").symlink_to(ROOT / "lib", target_is_directory=True)
    (copy / "bin" / "kickoff-config").write_bytes(MANAGER.read_bytes())
    (copy / "bin" / "kickoff-config").chmod(0o755)
    (copy / "kickoff.yaml").write_bytes((ROOT / "kickoff.yaml").read_bytes())
    assert not (copy / ".git").exists()

    result = subprocess.run(
        [str(copy / "bin" / "kickoff-config"), "show", "models"],
        cwd=copy,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert str(copy / "kickoff.yaml") in result.stdout
