from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def _write_probe(path: Path, name: str) -> None:
    path.write_text(
        f"""#!/usr/bin/env bash
printf '%s\n' '{name}' >> "$PRE_COMMIT_LOG"
if [[ "${{PRE_COMMIT_FAIL:-}}" == '{name}' ]]; then
  exit 37
fi
"""
    )
    path.chmod(0o755)


@pytest.fixture
def hook_repo(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    root = tmp_path / "repo"
    (root / ".githooks").mkdir(parents=True)
    (root / "bin").mkdir()
    shutil.copy2(REPO_ROOT / ".githooks" / "pre-commit", root / ".githooks" / "pre-commit")
    for executable in (
        "check-harness-parity",
        "check-toolchain-callers",
        "test-governance",
    ):
        _write_probe(root / "bin" / executable, executable)
    subprocess.run(["git", "init", "-q", "-b", "master", str(root)], check=True)
    environment = os.environ.copy()
    environment["PRE_COMMIT_LOG"] = str(tmp_path / "calls.log")
    return root, environment


def _run(root: Path, environment: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(root / ".githooks" / "pre-commit")],
        cwd=root,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )


def test_pre_commit_runs_structural_governance_after_existing_checks(
    hook_repo: tuple[Path, dict[str, str]],
) -> None:
    root, environment = hook_repo

    result = _run(root, environment)

    assert result.returncode == 0, result.stderr
    assert Path(environment["PRE_COMMIT_LOG"]).read_text().splitlines() == [
        "check-harness-parity",
        "check-toolchain-callers",
        "test-governance",
    ]


def test_pre_commit_preserves_governance_failure(
    hook_repo: tuple[Path, dict[str, str]],
) -> None:
    root, environment = hook_repo
    environment["PRE_COMMIT_FAIL"] = "test-governance"

    result = _run(root, environment)

    assert result.returncode == 37
