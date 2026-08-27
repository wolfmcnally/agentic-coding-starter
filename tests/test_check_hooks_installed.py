"""Behavioral tests for the opt-in-aware hook-liveness witness."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "bin" / "check-hooks-installed"


@pytest.fixture
def hook_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / ".githooks").mkdir(parents=True)
    for name in ("pre-commit", "pre-push"):
        hook = root / ".githooks" / name
        hook.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
        hook.chmod(0o755)
    subprocess.run(["git", "init", "-q", "-b", "master", str(root)], check=True)
    return root


def _run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(SCRIPT), "--root", str(root)],
        text=True,
        capture_output=True,
        check=False,
    )


def _set_hooks_path(root: Path, value: str) -> None:
    subprocess.run(
        ["git", "-C", str(root), "config", "--local", "core.hooksPath", value],
        check=True,
    )


def test_wrong_hooks_path_fails(hook_repo: Path) -> None:
    # A checkout that opted in and was silently repointed is the silent
    # disablement the witness exists to catch.
    _set_hooks_path(hook_repo, ".git/hooks")

    result = _run(hook_repo)

    assert result.returncode == 1
    assert ".git/hooks" in result.stderr
    assert "install-hooks" in result.stderr


def test_this_repository_passes_its_own_witness() -> None:
    # Whatever this checkout's opt-in state, the witness must be clean here:
    # either cleanly not opted in, or opted in with live executable hooks.
    result = _run(REPO_ROOT)

    assert result.returncode == 0, result.stderr + result.stdout
    assert "CHECK-HOOKS-INSTALLED OK" in result.stdout
