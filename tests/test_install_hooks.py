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


def test_dry_run_does_not_change_config(hook_repo: Path) -> None:
    result = _run(hook_repo, "--dry-run")

    assert result.returncode == 0
    assert "would set core.hooksPath=.githooks" in result.stdout
    probe = subprocess.run(
        ["git", "-C", str(hook_repo), "config", "--local", "--get", "core.hooksPath"],
        capture_output=True,
        check=False,
    )
    assert probe.returncode == 1


def test_install_is_idempotent(hook_repo: Path) -> None:
    first = _run(hook_repo)
    second = _run(hook_repo)

    assert first.returncode == 0
    assert second.returncode == 0
    assert _configured_path(hook_repo) == ".githooks"


def test_conflicting_configuration_is_preserved_without_force(hook_repo: Path) -> None:
    subprocess.run(
        ["git", "-C", str(hook_repo), "config", "--local", "core.hooksPath", "custom-hooks"],
        check=True,
    )

    result = _run(hook_repo)

    assert result.returncode == 1
    assert "INSTALL-HOOKS REFUSED" in result.stderr
    assert _configured_path(hook_repo) == "custom-hooks"


def test_force_replaces_conflicting_configuration(hook_repo: Path) -> None:
    subprocess.run(
        ["git", "-C", str(hook_repo), "config", "--local", "core.hooksPath", "custom-hooks"],
        check=True,
    )

    result = _run(hook_repo, "--force")

    assert result.returncode == 0
    assert _configured_path(hook_repo) == ".githooks"


def test_missing_hook_fails_without_changing_config(hook_repo: Path) -> None:
    (hook_repo / ".githooks" / "pre-push").unlink()

    result = _run(hook_repo)

    assert result.returncode == 1
    assert "INSTALL-HOOKS ERROR missing executable" in result.stderr


def test_invalid_argument_is_usage_error(hook_repo: Path) -> None:
    result = _run(hook_repo, "--bogus")

    assert result.returncode == 2
    assert "Usage: ./bin/install-hooks" in result.stderr
