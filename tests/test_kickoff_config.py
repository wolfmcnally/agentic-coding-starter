"""Behavioral tests for the universal kickoff configuration manager."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))

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
    manager: Path | None = None,
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
        [UV, "run", "--script", str(manager or MANAGER), *arguments],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


def fake_cli(tmp_path: Path, name: str, body: str) -> Path:
    executable = tmp_path / name
    executable.write_text(
        f'#!/bin/sh\nset -eu\nif [ "${{1:-}}" = "--version" ]; then '
        f'echo "test-cli 1.0"; exit 0; fi\n{body}\n'
    )
    executable.chmod(0o755)
    return executable


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
    original = original.replace("model: fable", 'model: "fable" # role comment', 1)
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

    base = yaml.safe_load(updated)["role_models"]["default"]
    # Independent oracle: role order is planner/reviewer/coder/critic.
    matrices = {
        ("quality", "same-harness"): (("astra",) * 4, ("fable",) * 4),
        ("balanced", "same-harness"): (
            ("astra", "astra", "sol", "astra"),
            ("fable", "fable", "opus", "fable"),
        ),
        ("economy", "same-harness"): (("sol",) * 4, ("opus",) * 4),
        ("quality", "cross-vendor"): (
            ("astra", "fable", "astra", "fable"),
            ("fable", "astra", "fable", "astra"),
        ),
        ("balanced", "cross-vendor"): (
            ("astra", "fable", "sol", "fable"),
            ("fable", "astra", "opus", "astra"),
        ),
        ("economy", "cross-vendor"): (
            ("sol", "opus", "sol", "opus"),
            ("opus", "sol", "opus", "sol"),
        ),
    }
    for (preset, review), expected in matrices.items():
        options = () if review == "same-harness" else ("--review", review)
        result = run_manager(config, "apply-preset", preset, *options)
        assert result.returncode == 0, result.stderr
        text = config.read_text()
        document = yaml.safe_load(text)
        assert document["role_models"]["default"] == base
        for harness, models in zip(("codex", "claude"), expected, strict=True):
            assert document["role_models"][harness] == {
                role: {"model": model, "effort": "high"}
                for role, model in zip(
                    ("planner", "reviewer", "coder", "critic"), models, strict=True
                )
            }
        assert 'quoted: "keep me" # preserve this comment' in text
        assert text.split("role_timeouts:", 1)[1] == timeout_block
        assert "# role comment" in text
        assert 'model: "' in text
        assert "Resolved for this harness" in result.stdout
    assert run_manager(config, "reset", "models").returncode == 0
    seed_models = yaml.safe_load(SEED_CONFIG.read_text())["role_models"]
    assert yaml.safe_load(config.read_text())["role_models"] == seed_models
    assert list(yaml.safe_load(config.read_text())["role_models"]) == list(seed_models)
    explicit = run_manager(config, "apply-preset", "quality", "--review", "same-harness")
    assert explicit.returncode == 0, explicit.stderr
    assert yaml.safe_load(config.read_text())["role_models"] == seed_models
    config.unlink()
    assert run_manager(config, "reset", "all").returncode == 0
    assert yaml.safe_load(config.read_text())["role_models"] == seed_models
    assert list(yaml.safe_load(config.read_text())["role_models"]) == list(seed_models)


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

    for arguments in (
        ("apply-preset", "unknown"),
        ("apply-preset", "quality", "--review", "unknown"),
        ("set-models", "codex", "coder.model=codex", "coder.effort=max"),
        ("set-models", "codex", "coder.model=astra", "coder.effort=ultra"),
    ):
        result = run_manager(config, *arguments)
        assert result.returncode == 2
        assert config.read_bytes() == before


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
    assert record["teardown_diagnostics"] == []

    assert record["model"] == "opus" and record["effort"] == "high"
    assert record["harness_version"] == "test-cli 1.0"
    assert record["observed_model"] is None and record["observed_effort"] is None
    assert "primary model unreported" in record["observation_errors"]
    primary = {
        "type": "system",
        "subtype": "init",
        "model": "claude-opus-5",
        "claude_code_version": "2.1.261",
    }
    cases = [
        ([primary], "claude-opus-5", "2.1.261"),
        ([{**primary, "type": "assistant"}], None, "test-cli 1.0"),
        ([{**primary, "subtype": "other"}], None, "test-cli 1.0"),
        (
            [primary, {**primary, "model": "different", "claude_code_version": "different"}],
            None,
            None,
        ),
        ([{**primary, "model": 9, "claude_code_version": 9}], None, None),
        ([{"type": "result", "modelUsage": {"auxiliary": {}}}], None, "test-cli 1.0"),
    ]
    for events, expected_model, expected_version in cases:
        events.append({"type": "result", "result": "FRESH"})
        cli = fake_cli(
            tmp_path,
            "claude",
            "\n".join("printf '%s\\n' '" + json.dumps(event) + "'" for event in events),
        )
        result = run_manager(
            config, *arguments, extra_env={"KICKOFF_TIMING_LOG": str(telemetry)}, cli=cli
        )
        assert result.returncode == 0, result.stderr
        record = read_record(telemetry)
        assert record["observed_model"] == expected_model
        assert record["harness_version"] == expected_version
        assert record["observed_effort"] is None
        assert record["model"] == "opus" and record["effort"] == "high"
        if expected_model is not None:
            assert record["observation_errors"] == []
    cli = fake_cli(tmp_path, "claude", RESULT_EVENT)
    cli.write_text(cli.read_text().replace('echo "test-cli 1.0"; exit 0', "exit 9"))
    result = run_manager(
        config, *arguments, extra_env={"KICKOFF_TIMING_LOG": str(telemetry)}, cli=cli
    )
    assert result.returncode == 0, result.stderr
    record = read_record(telemetry)
    assert record["harness_version"] is None
    assert "version command failed or returned empty output" in record["observation_errors"]
    for complete in (True, False):
        events = [
            {"type": "assistant", "message": {"content": "FRESH"}},
            {"type": "result", "is_error": True, "result": "FRESH" if complete else ""},
        ]
        cli = fake_cli(
            tmp_path,
            "claude",
            "\n".join("printf '%s\\n' '" + json.dumps(event) + "'" for event in events),
        )
        result = run_manager(
            config, *arguments, extra_env={"KICKOFF_TIMING_LOG": str(telemetry)}, cli=cli
        )
        assert result.returncode == 65, result.stderr
        record = read_record(telemetry)
        assert record["outcome"] == "error"
        assert record["artifact_status"] == "fresh"
        assert record["stream_status"] == ("complete" if complete else "incomplete")
        assert "explicit terminal error" in record["protocol_error"]
        assert result_path.read_text() == "FRESH"
        cli.write_text(cli.read_text() + "\nexit 7\n")
        result = run_manager(
            config, *arguments, extra_env={"KICKOFF_TIMING_LOG": str(telemetry)}, cli=cli
        )
        assert result.returncode == 7
        assert read_record(telemetry)["outcome"] == "error"


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


def test_watch_preserves_codex_artifact_when_terminal_stream_is_incomplete(
    tmp_path: Path,
) -> None:
    config = seeded_config(tmp_path)
    output_path = tmp_path / "last-message.txt"
    telemetry = tmp_path / "timings.jsonl"
    for resume in ((), ("--resume-session", "existing-session")):
        arguments = watch_arguments(
            tmp_path,
            venue="codex",
            model="astra",
            effort="max",
            extra_watch=("--required-output-file", str(output_path), *resume),
        )
        argv_path = tmp_path / "argv.txt"
        cli = fake_cli(
            tmp_path,
            "codex",
            f"printf '%s\\n' \"$@\" > {argv_path}\n"
            f"printf '%s\\n' '{{\"type\":\"thread.started\"}}'\n"
            f"printf '%s' 'CODEX RECOVER' > {output_path}",
        )
        result = run_manager(
            config,
            *arguments,
            extra_env={"KICKOFF_TIMING_LOG": str(telemetry)},
            cli=cli,
        )
        assert result.returncode == 66, result.stderr
        argv = argv_path.read_text().splitlines()
        assert argv[argv.index("--model") + 1] == "gpt-6-astra"
        assert 'model_reasoning_effort="max"' in argv
        if resume:
            assert "existing-session" in argv
        assert output_path.read_text() == "CODEX RECOVER"
        record = read_record(telemetry)
        assert record["outcome"] == "completed_unverified_protocol"
        assert record["artifact_status"] == "fresh"
        assert record["stream_status"] == "incomplete"
        assert record["model"] == "astra" and record["effort"] == "max"
        assert record["observed_model"] is None
        assert record["observed_effort"] is None


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

    def test_claude_coder_is_the_only_write_enabled_role(self, tmp_path: Path) -> None:
        coder, _ = rendered(tmp_path, venue="claude", model="opus", role="coder")
        assert coder[coder.index("--allowedTools") + 1] == (
            "Read,Grep,Glob,Write,Edit,Bash,WebFetch"
        )
        assert coder[coder.index("--max-turns") + 1] == "200"

        expected = {
            "planner": "Read,Grep,Glob,WebFetch,WebSearch",
            "reviewer": "Read,Grep,Glob,WebFetch,WebSearch",
            "critic": "Read,Grep,Glob,WebFetch",
        }
        for role, tools in expected.items():
            command, _ = rendered(tmp_path, venue="claude", model="opus", role=role)
            assert command[command.index("--allowedTools") + 1] == tools

        for model, venue, wire in (
            ("astra", "codex", "gpt-6-astra"),
            ("sol", "codex", "gpt-5.6-sol"),
            ("terra", "codex", "gpt-5.6-terra"),
            ("luna", "codex", "gpt-5.6-luna"),
            ("fable", "claude", "fable"),
            ("opus", "claude", "opus"),
        ):
            for resume in ((), ("--resume-session", "existing-session")):
                command, result = rendered(
                    tmp_path, venue=venue, model=model, effort="max", extra=resume
                )
                assert result.returncode == 0, result.stderr
                assert command[command.index("--model") + 1] == wire
                if venue == "claude":
                    assert command[command.index("--effort") + 1] == "max"
                    assert "--json-schema" in command
                else:
                    assert 'model_reasoning_effort="max"' in command
                    assert "--output-schema" in command
                if resume:
                    assert "existing-session" in command
        for venue, model in (("claude", "opus"), ("codex", "astra")):
            for effort in ("low", "medium", "high", "xhigh", "max"):
                command, result = rendered(tmp_path, venue=venue, model=model, effort=effort)
                assert result.returncode == 0, result.stderr
                if venue == "claude":
                    assert command[command.index("--effort") + 1] == effort
                    assert "--json-schema" in command
                else:
                    assert f'model_reasoning_effort="{effort}"' in command
                    assert "--output-schema" in command
        for venue, model, effort in (
            ("claude", "astra", "high"),
            ("codex", "fable", "high"),
            ("codex", "default", "high"),
            ("codex", "codex", "max"),
            ("codex", "astra", "ultra"),
        ):
            _, result = rendered(tmp_path, venue=venue, model=model, effort=effort)
            assert result.returncode != 0


# --- The dispatch-open/amend lifecycle and the candidate the watcher observes --

RESULT_EVENT = (
    """printf '%s\\n' '{"type":"result","result":"OK","""
    """"usage":{"input_tokens":1,"output_tokens":2}}'"""
)


def _coder_pinned_config(tmp_path: Path) -> Path:
    """Every harness section pins only the coder, to a Claude model."""
    config = tmp_path / "kickoff.yaml"
    document = yaml.safe_load(SEED_CONFIG.read_text())
    document["role_models"] = {
        "default": {
            role: {"model": "default"} for role in ("planner", "reviewer", "coder", "critic")
        },
        "claude": {"coder": {"model": "opus"}},
        "codex": {"coder": {"model": "opus"}},
    }
    config.write_text(yaml.safe_dump(document))
    return config


def test_preflight_still_aborts_on_a_failed_sentinel(tmp_path: Path) -> None:
    for venue in ("claude", "codex"):
        work = tmp_path / venue
        work.mkdir()
        config = _coder_pinned_config(work)
        if venue == "codex":
            document = yaml.safe_load(config.read_text())
            for harness in ("claude", "codex"):
                document["role_models"][harness] = {"coder": {"model": "sol"}}
            config.write_text(yaml.safe_dump(document))
        missing_receipt = work / "missing-cli-receipt.json"
        missing_path = work / "empty-bin"
        missing_path.mkdir()
        missing = run_manager(
            config,
            "preflight",
            "--receipt",
            str(missing_receipt),
            extra_env={"PATH": str(missing_path)},
        )
        assert missing.returncode != 0
        assert "CLI not on PATH" in missing.stderr
        assert not missing_receipt.exists()
        observed = work / "observed.txt"
        toolchain = work / "toolchain.txt"
        executable = work / venue
        executable.write_text(
            f"#!{sys.executable}\n"
            + r"""import hashlib
import json
import os
import sys
from pathlib import Path

probe = Path(".kickoff-capability-probe")
if probe.is_file():
    token = probe.read_text(encoding="ascii")
    assert len(token) == 64 and all(c in "0123456789abcdef" for c in token)
    prompt = sys.argv[sys.argv.index("-p") + 1] if "-p" in sys.argv else sys.argv[-1]
    assert token not in prompt
    assert "sha" not in prompt.lower() and "digest" not in prompt.lower()
    Path(os.environ["PROBE_OBSERVED"]).write_text(token)
    mode = os.environ["PROBE_RESPONSE"]
    answer = "KICKOFF_PREFLIGHT_OK " + token
    if mode == "wrong":
        answer = "KICKOFF_PREFLIGHT_OK " + ("0" if token[0] != "0" else "1") + token[1:]
    elif mode == "digest":
        answer = "KICKOFF_PREFLIGHT_OK " + hashlib.sha256(token.encode("ascii")).hexdigest()
    elif mode == "sentinel":
        answer = "KICKOFF_PREFLIGHT_OK"
    elif mode == "extra":
        answer += " extra text"
    elif mode == "malformed":
        answer = "nope"
else:
    Path(os.environ["PROBE_TOOLCHAIN"]).write_text("called")
    answer = "KICKOFF_TOOLCHAIN_OK"
if "--output-last-message" in sys.argv:
    Path(sys.argv[sys.argv.index("--output-last-message") + 1]).write_text(answer)
else:
    print(json.dumps({"result": answer}))
"""
        )
        executable.chmod(0o755)
        for mode in ("malformed", "wrong", "digest", "sentinel", "extra", "readback"):
            receipt = work / f"{mode}.json"
            result = run_manager(
                config,
                "preflight",
                "--receipt",
                str(receipt),
                cli=executable,
                extra_env={
                    "PROBE_OBSERVED": str(observed),
                    "PROBE_TOOLCHAIN": str(toolchain),
                    "PROBE_RESPONSE": mode,
                    "PATH": str(work) + os.pathsep + os.environ["PATH"],
                },
            )
            token = observed.read_text()
            if mode != "readback":
                assert result.returncode != 0
                assert "preflight failed" in result.stderr
                expected = (
                    "local probe challenge"
                    if mode in ("wrong", "digest")
                    else "malformed capability response"
                )
                assert expected in result.stderr
                assert token not in result.stderr
                assert hashlib.sha256(token.encode("ascii")).hexdigest() not in result.stderr
                assert "toolchain" not in result.stdout
                assert not receipt.exists()
                assert not toolchain.exists()
                continue
            assert result.returncode == 0, result.stderr
            assert toolchain.is_file()
            document = json.loads(receipt.read_text())
            assert document["targets"]
            assert all(target["cli"] == venue for target in document["targets"])
            assert all(
                target["model"] == ("opus" if venue == "claude" else "gpt-5.6-sol")
                for target in document["targets"]
            )
            assert all(
                target["probe_sha256"] == hashlib.sha256(token.encode("ascii")).hexdigest()
                for target in document["targets"]
            )
            verified = run_manager(config, "verify-preflight-receipt", "--receipt", str(receipt))
            assert verified.returncode == 0, verified.stderr
            assert "PREFLIGHT RECEIPT VALID" in verified.stdout

            config.write_text(config.read_text() + "\n# routing configuration changed\n")
            stale = run_manager(config, "verify-preflight-receipt", "--receipt", str(receipt))
            assert stale.returncode != 0
            assert "stale routing configuration" in stale.stderr
