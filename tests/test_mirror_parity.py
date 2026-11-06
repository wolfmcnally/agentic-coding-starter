"""Behavioral tests for deterministic cross-harness parity enforcement."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
from pathlib import Path

import pytest
from test_check_catalogs import RESOURCES

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


def test_repository_is_in_parity(tmp_path: Path) -> None:
    result = run(ROOT)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == "HARNESS PARITY OK\n"
    for directory in (".claude/skills", ".claude/agents", ".codex/agents", ".agents/skills"):
        shutil.copytree(ROOT / directory, tmp_path / directory, symlinks=True)
    (tmp_path / "bin").mkdir()
    shutil.copy2(CHECKER, tmp_path / "bin/check-harness-parity")
    shutil.copy2(ROOT / "AGENTS.md", tmp_path / "AGENTS.md")
    copied = run(tmp_path)
    assert copied.returncode == 0, copied.stdout + copied.stderr
    _assert_resource_bytes(tmp_path)
    canonical_role = tmp_path / ".claude/agents/code-critic.md"
    canonical_role.write_text(
        canonical_role.read_text().replace("description: ", "description: Navigation 🧭 ", 1)
    )
    wrapper = tmp_path / ".codex/agents/code-critic.toml"
    original_wrapper = wrapper.read_bytes()
    wrapper.write_bytes(original_wrapper + b'\nmodel = "custom"\n')
    custom = wrapper.read_bytes()
    command = [str(CHECKER), "--root", str(tmp_path), "--sync-role", "code-critic"]
    refused = subprocess.run(
        command + ["--expect-sha256", hashlib.sha256(custom).hexdigest()],
        capture_output=True,
        text=True,
    )
    assert refused.returncode != 0 and wrapper.read_bytes() == custom, (
        "MIRROR SYNC OVERWROTE CUSTOM FIELDS"
    )
    wrapper.write_bytes(original_wrapper)
    written = subprocess.run(
        command + ["--expect-sha256", hashlib.sha256(original_wrapper).hexdigest()],
        capture_output=True,
        text=True,
    )
    assert written.returncode == 0 and run(tmp_path).returncode == 0, (
        "MIRROR ROLE AUTHORING FAILED: " + written.stderr
    )
    skill = tmp_path / ".agents/skills/kickoff"
    skill.unlink()
    linked = subprocess.run(
        [str(CHECKER), "--root", str(tmp_path), "--sync-skill", "kickoff"],
        capture_output=True,
        text=True,
    )
    assert (
        linked.returncode == 0 and skill.readlink().as_posix() == "../../.claude/skills/kickoff"
    ), "MIRROR SKILL AUTHORING FAILED"
    canonical = tmp_path / ".claude/skills/kickoff"
    for name in RESOURCES:
        resource = canonical / name
        body = resource.read_bytes()
        resource.unlink()
        # Directory parity alone is deliberately insufficient for resource delivery.
        skeletal = run(tmp_path)
        assert skeletal.returncode == 0, skeletal.stdout + skeletal.stderr
        with pytest.raises(AssertionError, match=f"missing resource {name}"):
            _assert_resource_bytes(tmp_path)
        resource.write_bytes(body)
    _assert_resource_bytes(tmp_path)


def _assert_resource_bytes(root: Path) -> None:
    mirror = root / ".agents/skills/kickoff"
    assert mirror.is_symlink()
    assert mirror.readlink().as_posix() == "../../.claude/skills/kickoff"
    for name in ("SKILL.md", *RESOURCES):
        assert (mirror / name).is_file(), f"missing resource {name}"
        expected = (ROOT / ".claude/skills/kickoff" / name).read_bytes()
        assert (root / ".claude/skills/kickoff" / name).read_bytes() == expected
        assert (mirror / name).read_bytes() == expected
