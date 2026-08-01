"""Behavioral tests for deterministic cross-harness parity enforcement."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "bin" / "check-harness-parity"


def run(root: Path) -> subprocess.CompletedProcess[str]:
    checker = root / "bin" / "check-harness-parity"
    return subprocess.run(
        [str(checker)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


def fixture(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "bin").mkdir(parents=True)
    shutil.copy2(CHECKER, root / "bin" / "check-harness-parity")
    (root / "CLAUDE.md").write_text("# Instructions\n", encoding="utf-8")
    (root / "AGENTS.md").symlink_to("CLAUDE.md")
    canonical_skill = root / ".claude" / "skills" / "demo"
    canonical_skill.mkdir(parents=True)
    (canonical_skill / "SKILL.md").write_text("# Demo\n", encoding="utf-8")
    mirror_skills = root / ".agents" / "skills"
    mirror_skills.mkdir(parents=True)
    (mirror_skills / "demo").symlink_to("../../.claude/skills/demo")
    canonical_agents = root / ".claude" / "agents"
    canonical_agents.mkdir(parents=True)
    (canonical_agents / "reviewer.md").write_text(
        "---\nname: reviewer\ndescription: >-\n"
        "  Review the candidate.\ntools: Read\n---\n\n# Reviewer\n",
        encoding="utf-8",
    )
    wrappers = root / ".codex" / "agents"
    wrappers.mkdir(parents=True)
    (wrappers / "reviewer.toml").write_text(
        'name = "reviewer"\n'
        'description = "Review the candidate."\n'
        'developer_instructions = """Read .claude/agents/reviewer.md in this '
        'repo and follow it."""\n',
        encoding="utf-8",
    )
    return root


def test_repository_is_in_parity() -> None:
    result = run(ROOT)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == "HARNESS PARITY OK\n"


def test_detects_instruction_skill_and_agent_drift(tmp_path: Path) -> None:
    root = fixture(tmp_path)
    (root / "AGENTS.md").unlink()
    (root / "AGENTS.md").write_text("copy\n", encoding="utf-8")
    (root / ".agents" / "skills" / "demo").unlink()
    (root / ".agents" / "skills" / "demo").mkdir()
    wrapper = root / ".codex" / "agents" / "reviewer.toml"
    wrapper.write_text(
        wrapper.read_text().replace("Review the candidate.", "Drifted."), encoding="utf-8"
    )

    result = run(root)

    assert result.returncode == 1
    assert "instructions\tAGENTS.md\tmust be a symlink" in result.stdout
    assert "skills\t.agents/skills/demo\tmust be a directory symlink" in result.stdout
    assert "agents\t.codex/agents/reviewer.toml\tdescription does not match" in result.stdout


def test_detects_missing_and_orphan_mirrors(tmp_path: Path) -> None:
    root = fixture(tmp_path)
    (root / ".agents" / "skills" / "demo").unlink()
    (root / ".agents" / "skills" / "orphan").symlink_to("../../.claude/skills/missing")
    (root / ".codex" / "agents" / "reviewer.toml").unlink()
    (root / ".codex" / "agents" / "orphan.toml").write_text('name = "orphan"\n', encoding="utf-8")

    result = run(root)

    assert result.returncode == 1
    assert "missing mirror" in result.stdout
    assert "orphan mirror" in result.stdout
    assert "missing wrapper" in result.stdout
    assert "orphan wrapper" in result.stdout
