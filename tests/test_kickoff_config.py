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
    executable.write_text(f"#!/bin/sh\nset -eu\n{body}\n")
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


# --- The dispatch-open/amend lifecycle and the candidate the watcher observes --

RESULT_EVENT = (
    """printf '%s\\n' '{"type":"result","result":"OK","""
    """"usage":{"input_tokens":1,"output_tokens":2}}'"""
)


def _coder_pinned_config(tmp_path: Path) -> Path:
    """Every harness section pins only the coder, to a Claude model."""
    config = tmp_path / "kickoff.yaml"
    text = SEED_CONFIG.read_text()
    text = text.replace(
        "  claude:\n    reviewer:\n      model: codex\n    critic:\n      model: codex\n",
        "  claude:\n    coder:\n      model: opus\n",
    ).replace(
        "  codex:\n    reviewer:\n      model: opus\n      effort: high\n    critic:\n"
        "      model: opus\n      effort: high\n",
        "  codex:\n    coder:\n      model: opus\n",
    )
    assert "coder:\n      model: opus" in text
    config.write_text(text)
    return config


def test_preflight_still_aborts_on_a_failed_sentinel(tmp_path: Path) -> None:
    for venue in ("claude", "codex"):
        work = tmp_path / venue
        work.mkdir()
        config = _coder_pinned_config(work)
        if venue == "codex":
            config.write_text(config.read_text().replace("model: opus", "model: sol"))
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
