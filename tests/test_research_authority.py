from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANAGER = ROOT / "bin" / "kickoff-config"
SEED = ROOT / "kickoff.yaml"
ROLES = ("planner", "reviewer", "coder", "critic")


def render(tmp_path: Path, *, role: str, venue: str) -> list[str]:
    prompt = tmp_path / f"{venue}-{role}.md"
    prompt.write_text("Perform the assigned role.\n", encoding="utf-8")
    artifact = tmp_path / f"{venue}-{role}.out"
    command = [
        str(MANAGER),
        "render-command",
        "--role",
        role,
        "--venue",
        venue,
        "--model",
        "opus" if venue == "claude" else "sol",
        "--effort",
        "high" if venue == "claude" else "medium",
        "--prompt-file",
        str(prompt),
        "--result-file" if venue == "claude" else "--required-output-file",
        str(artifact),
        "--json",
    ]
    environment = os.environ.copy()
    environment["KICKOFF_CONFIG_FILE"] = str(SEED)
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_generated_commands_enforce_the_role_authority_matrix(tmp_path: Path) -> None:
    expected_claude_tools = {
        "planner": "Read,Grep,Glob,WebFetch,WebSearch",
        "reviewer": "Read,Grep,Glob,WebFetch,WebSearch",
        "coder": "Read,Grep,Glob,Write,Edit,Bash,WebFetch",
        "critic": "Read,Grep,Glob,WebFetch",
    }
    for role in ROLES:
        claude = render(tmp_path, role=role, venue="claude")
        assert claude[claude.index("--allowedTools") + 1] == expected_claude_tools[role]

        codex = render(tmp_path, role=role, venue="codex")
        assert 'web_search="live"' in codex
        assert not any(
            value.startswith("mcp_servers.") or value.startswith("plugins.") for value in codex
        )

        prompt = claude[2]
        assert "External research is GET-only" in prompt
        assert "never place repository or candidate content in outbound" in prompt
        assert "Installed MCP servers and plugins are available by default" in prompt
        if role in {"planner", "reviewer"}:
            assert "may originate web or installed-resource searches" in prompt
        else:
            assert "Do not originate searches" in prompt
            assert "same-host structural neighbors" in prompt


def test_research_budgets_accept_a_phase_project_zero_pin(tmp_path: Path) -> None:
    config = tmp_path / "kickoff.yaml"
    config.write_text(
        SEED.read_text(encoding="utf-8").replace("  planner: 12", "  planner: 0"),
        encoding="utf-8",
    )
    environment = os.environ.copy()
    environment["KICKOFF_CONFIG_FILE"] = str(config)
    result = subprocess.run(
        [str(MANAGER), "show", "research"],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    assert "planner" in result.stdout and "0" in result.stdout


def test_retrieval_only_roles_reject_originating_search_budget(tmp_path: Path) -> None:
    config = tmp_path / "kickoff.yaml"
    config.write_text(
        SEED.read_text(encoding="utf-8").replace("  coder: 0", "  coder: 1"),
        encoding="utf-8",
    )
    environment = os.environ.copy()
    environment["KICKOFF_CONFIG_FILE"] = str(config)
    result = subprocess.run(
        [str(MANAGER), "show", "research"],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert result.returncode == 2
    assert "coder is retrieval-only" in result.stderr


def test_scoped_research_reset_preserves_other_configuration(tmp_path: Path) -> None:
    config = tmp_path / "kickoff.yaml"
    original = (
        SEED.read_text(encoding="utf-8")
        .replace("extensions: {}", 'extensions:\n  marker: "preserve"')
        .replace("  planner: 12", "  planner: 0")
    )
    config.write_text(original, encoding="utf-8")
    environment = os.environ.copy()
    environment["KICKOFF_CONFIG_FILE"] = str(config)
    result = subprocess.run(
        [str(MANAGER), "reset", "research"],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    updated = config.read_text(encoding="utf-8")
    assert 'marker: "preserve"' in updated
    assert "  planner: 12" in updated
    assert (
        original.split("role_models:", 1)[1].split("research_budgets:", 1)[0]
        == (updated.split("role_models:", 1)[1].split("research_budgets:", 1)[0])
    )


def test_policy_is_allow_by_default_without_assuming_any_named_server() -> None:
    policy = (ROOT / "policies" / "research-authority.md").read_text(encoding="utf-8")
    assert "allow-by-default" in policy
    assert "never assumed to exist" in policy
    assert "GET-only" in policy
    assert "same-host structural neighbors" in policy
