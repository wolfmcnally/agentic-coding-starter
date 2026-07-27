from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
ENTRYPOINTS = ("setup", "test", "python")


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text)
    path.chmod(0o755)


@pytest.fixture
def toolchain_repo(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    root = tmp_path / "repo"
    (root / "bin").mkdir(parents=True)
    (root / "project").mkdir()
    for entrypoint in ENTRYPOINTS:
        shutil.copy2(REPO_ROOT / "bin" / entrypoint, root / "bin" / entrypoint)
    (root / "project" / ".python-version").write_text("3.11\n")
    (root / "project" / "pyproject.toml").write_text("[project]\nname='fixture'\n")
    (root / "project" / "uv.lock").write_text("version = 1\n")

    log_path = tmp_path / "calls.log"
    tool_dir = tmp_path / "tools"
    tool_dir.mkdir()
    _write_executable(
        tool_dir / "uv",
        """#!/usr/bin/env bash
set -u
printf 'uv cwd=%s args=%s\\n' "$PWD" "$*" >> "$TOOLCHAIN_TEST_LOG"
if [[ -n "${TOOLCHAIN_TEST_FAIL_MATCH:-}" && "$*" == *"$TOOLCHAIN_TEST_FAIL_MATCH"* ]]; then
  exit "${TOOLCHAIN_TEST_FAIL_CODE:-23}"
fi
""",
    )
    environment = os.environ.copy()
    environment["PATH"] = f"{tool_dir}:{environment['PATH']}"
    environment["TOOLCHAIN_TEST_LOG"] = str(log_path)
    return root, environment


def _run(
    root: Path,
    environment: dict[str, str],
    entrypoint: str,
    *arguments: str,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(root / "bin" / entrypoint), *arguments],
        cwd=cwd or root,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )


def _calls(environment: dict[str, str]) -> list[str]:
    log_path = Path(environment["TOOLCHAIN_TEST_LOG"])
    return log_path.read_text().splitlines() if log_path.exists() else []


def test_setup_syncs_the_pinned_locked_environment_from_any_cwd(
    toolchain_repo: tuple[Path, dict[str, str]], tmp_path: Path
) -> None:
    root, environment = toolchain_repo

    result = _run(root, environment, "setup", cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert _calls(environment) == [
        (f"uv cwd={root} args=sync --project {root / 'project'} --locked --managed-python")
    ]
    assert "SETUP PASS" in result.stdout


def test_test_defaults_to_every_repository_test_from_any_cwd(
    toolchain_repo: tuple[Path, dict[str, str]], tmp_path: Path
) -> None:
    root, environment = toolchain_repo

    result = _run(root, environment, "test", cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert _calls(environment) == [
        (
            f"uv cwd={root} args=run --project {root / 'project'} --locked "
            "--managed-python python -m pytest -q project/tests tests"
        )
    ]


def test_test_forwards_focused_arguments_relative_to_repository_root(
    toolchain_repo: tuple[Path, dict[str, str]],
) -> None:
    root, environment = toolchain_repo

    result = _run(
        root,
        environment,
        "test",
        "tests/test_check.py",
        "-k",
        "failure",
        "-q",
    )

    assert result.returncode == 0, result.stderr
    assert _calls(environment) == [
        (
            f"uv cwd={root} args=run --project {root / 'project'} --locked "
            "--managed-python python -m pytest tests/test_check.py -k failure -q"
        )
    ]


def test_python_forwards_to_the_repository_selected_interpreter(
    toolchain_repo: tuple[Path, dict[str, str]], tmp_path: Path
) -> None:
    root, environment = toolchain_repo

    result = _run(root, environment, "python", "-c", "print('ok')", cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert _calls(environment) == [
        (
            f"uv cwd={root} args=run --project {root / 'project'} --locked "
            "--managed-python python -c print('ok')"
        )
    ]


@pytest.mark.parametrize(
    ("entrypoint", "match", "exit_code"),
    [
        ("setup", "sync", "31"),
        ("test", "pytest", "32"),
        ("python", "python", "33"),
    ],
)
def test_child_failure_status_is_preserved(
    toolchain_repo: tuple[Path, dict[str, str]],
    entrypoint: str,
    match: str,
    exit_code: str,
) -> None:
    root, environment = toolchain_repo
    environment["TOOLCHAIN_TEST_FAIL_MATCH"] = match
    environment["TOOLCHAIN_TEST_FAIL_CODE"] = exit_code

    result = _run(root, environment, entrypoint)

    assert result.returncode == int(exit_code)


@pytest.mark.parametrize("entrypoint", ENTRYPOINTS)
def test_missing_uv_fails_clearly(
    toolchain_repo: tuple[Path, dict[str, str]], entrypoint: str
) -> None:
    root, environment = toolchain_repo
    environment["PATH"] = "/usr/bin:/bin"

    result = _run(root, environment, entrypoint)

    assert result.returncode == 1
    assert f"{entrypoint.upper()} ERROR missing prerequisite: uv" in result.stderr


@pytest.mark.parametrize("entrypoint", ENTRYPOINTS)
@pytest.mark.parametrize("missing", [".python-version", "pyproject.toml", "uv.lock"])
def test_missing_contract_member_fails_clearly(
    toolchain_repo: tuple[Path, dict[str, str]],
    entrypoint: str,
    missing: str,
) -> None:
    root, environment = toolchain_repo
    (root / "project" / missing).unlink()

    result = _run(root, environment, entrypoint)

    assert result.returncode == 1
    assert f"{entrypoint.upper()} ERROR missing required file: project/{missing}" in result.stderr


@pytest.mark.parametrize("entrypoint", ["setup", "test"])
def test_help_does_not_require_toolchain(
    toolchain_repo: tuple[Path, dict[str, str]], entrypoint: str
) -> None:
    root, environment = toolchain_repo
    environment["PATH"] = "/usr/bin:/bin"

    result = _run(root, environment, entrypoint, "--help")

    assert result.returncode == 0
    assert f"Usage: ./bin/{entrypoint}" in result.stdout


def test_setup_rejects_arguments(
    toolchain_repo: tuple[Path, dict[str, str]],
) -> None:
    root, environment = toolchain_repo

    result = _run(root, environment, "setup", "extra")

    assert result.returncode == 2
    assert "Usage: ./bin/setup" in result.stderr
