"""Behavioral tests for the universal kickoff configuration manager."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MANAGER = ROOT / "bin" / "kickoff-config"
SEED_CONFIG = ROOT / "kickoff.yaml"


def seeded_config(tmp_path: Path) -> Path:
    config = tmp_path / "kickoff.yaml"
    config.write_text(SEED_CONFIG.read_text())
    return config


def run_manager(
    config: Path,
    *arguments: str,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["KICKOFF_CONFIG_FILE"] = str(config)
    if extra_env:
        environment.update(extra_env)
    return subprocess.run(
        [str(MANAGER), *arguments],
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


def watch_arguments(
    tmp_path: Path,
    cli: Path,
    *,
    venue: str = "claude",
    model: str = "opus",
    effort: str = "high",
    extra_watch: tuple[str, ...] = (),
    cli_arguments: tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    if cli_arguments is None:
        cli_arguments = ("--model", "opus", "--effort", "high")
    return (
        "watch",
        "--role",
        "reviewer",
        "--venue",
        venue,
        "--model",
        model,
        "--effort",
        effort,
        "--phase",
        "test",
        "--first-event-timeout",
        "1",
        "--idle-timeout",
        "1",
        "--hard-timeout",
        "2",
        *extra_watch,
        "--",
        str(cli),
        *cli_arguments,
    )


def read_record(path: Path) -> dict[str, object]:
    return json.loads(path.read_text().splitlines()[-1])


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
        cli,
        extra_watch=("--result-file", str(result_path)),
    )

    result = run_manager(
        config,
        *arguments,
        extra_env={"KICKOFF_TIMING_LOG": str(telemetry)},
    )

    assert result.returncode == 0, result.stderr
    assert result_path.read_text() == "FRESH"
    record = read_record(telemetry)
    assert record["outcome"] == "success"
    assert record["program"] == "claude"
    assert record["input_tokens"] == 3
    assert record["output_tokens"] == 2


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
        cli,
        extra_watch=("--result-file", str(result_path)),
    )

    result = run_manager(
        config,
        *arguments,
        extra_env={"KICKOFF_TIMING_LOG": str(telemetry)},
    )

    assert result.returncode == 65
    assert result_path.read_text() == ""
    assert "no structured stdout event" in result.stderr
    assert "stream result event missing or empty" in result.stderr
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
        cli,
        venue="codex",
        model="codex",
        effort="default",
        extra_watch=("--required-output-file", str(output_path)),
        cli_arguments=(),
    )

    result = run_manager(
        config,
        *arguments,
        extra_env={"KICKOFF_TIMING_LOG": str(telemetry)},
    )

    assert result.returncode == 65
    assert output_path.read_text() == ""
    assert "required output artifact missing or empty" in result.stderr


def test_watch_accepts_matching_explicit_codex_routing(tmp_path: Path) -> None:
    config = seeded_config(tmp_path)
    output_path = tmp_path / "last-message.txt"
    telemetry = tmp_path / "timings.jsonl"
    cli = fake_cli(
        tmp_path,
        "codex",
        f"printf '%s\\n' '{{\"type\":\"thread.started\"}}'\n"
        f"printf '%s' 'CODEX FRESH' > {output_path}",
    )
    arguments = watch_arguments(
        tmp_path,
        cli,
        venue="codex",
        model="sol",
        effort="medium",
        extra_watch=("--required-output-file", str(output_path)),
        cli_arguments=(
            "--model",
            "gpt-5.6-sol",
            "-c",
            'model_reasoning_effort="medium"',
        ),
    )

    result = run_manager(
        config,
        *arguments,
        extra_env={"KICKOFF_TIMING_LOG": str(telemetry)},
    )

    assert result.returncode == 0, result.stderr
    assert output_path.read_text() == "CODEX FRESH"
    assert read_record(telemetry)["program"] == "codex"


def test_watch_rejects_routing_metadata_that_child_flags_do_not_apply(tmp_path: Path) -> None:
    config = seeded_config(tmp_path)
    cli = fake_cli(tmp_path, "claude", "printf '%s\\n' '{\"type\":\"assistant\"}'")
    arguments = watch_arguments(tmp_path, cli, cli_arguments=())

    result = run_manager(config, *arguments)

    assert result.returncode == 2
    assert "command must include --model opus" in result.stderr


def test_watch_rejects_zero_timeout_override_before_launch(tmp_path: Path) -> None:
    config = seeded_config(tmp_path)
    marker = tmp_path / "launched"
    cli = fake_cli(tmp_path, "claude", f"touch {marker}")
    arguments = list(watch_arguments(tmp_path, cli))
    index = arguments.index("--first-event-timeout") + 1
    arguments[index] = "0"

    result = run_manager(config, *arguments)

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
    arguments = list(watch_arguments(tmp_path, cli))
    arguments[arguments.index("--first-event-timeout") + 1] = "0.1"

    result = run_manager(
        config,
        *arguments,
        extra_env={"KICKOFF_TIMING_LOG": str(telemetry)},
    )

    assert result.returncode == 124
    record = read_record(telemetry)
    assert record["timeout_kind"] == "first-event"


def test_watch_enforces_idle_timeout_after_first_event(tmp_path: Path) -> None:
    config = seeded_config(tmp_path)
    telemetry = tmp_path / "timings.jsonl"
    cli = fake_cli(
        tmp_path,
        "claude",
        "printf '%s\\n' '{\"type\":\"assistant\"}'\nsleep 0.4",
    )
    arguments = list(watch_arguments(tmp_path, cli))
    arguments[arguments.index("--idle-timeout") + 1] = "0.1"

    result = run_manager(
        config,
        *arguments,
        extra_env={"KICKOFF_TIMING_LOG": str(telemetry)},
    )

    assert result.returncode == 124
    record = read_record(telemetry)
    assert record["timeout_kind"] == "idle"


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
                "role": "reviewer",
                "venue": "claude",
                "model": "opus",
                "effort": "high",
                "outcome": "success",
                "duration_seconds": 10,
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
