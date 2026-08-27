from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def hook_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "bin").mkdir(parents=True)
    (root / ".githooks").mkdir()
    shutil.copy2(REPO_ROOT / "bin" / "install-hooks", root / "bin" / "install-hooks")
    shutil.copy2(REPO_ROOT / ".githooks" / "pre-push", root / ".githooks" / "pre-push")
    shutil.copy2(REPO_ROOT / ".githooks" / "pre-commit", root / ".githooks" / "pre-commit")
    subprocess.run(["git", "init", "-q", "-b", "master", str(root)], check=True)
    return root


def _run(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(root / "bin" / "install-hooks"), *arguments],
        cwd=root.parent,
        text=True,
        capture_output=True,
        check=False,
    )


def _configured_path(root: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(root), "config", "--local", "--get", "core.hooksPath"],
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()


def test_install_is_idempotent(hook_repo: Path) -> None:
    first = _run(hook_repo)
    second = _run(hook_repo)

    assert first.returncode == 0
    assert second.returncode == 0
    assert _configured_path(hook_repo) == ".githooks"
