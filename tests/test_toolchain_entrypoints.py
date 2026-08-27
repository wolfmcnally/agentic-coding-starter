from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
ENTRYPOINTS = ("setup", "test", "python")
SYMLINK_INVOCATIONS = (
    ("setup", ()),
    ("test", ("tests/test_check.py", "-q")),
    ("python", ("--version",)),
)
PROBE = (
    "import example.cli, pytest, subprocess; "
    "subprocess.run(['ruff','--version'], check=True, stdout=subprocess.DEVNULL)"
)


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text)
    path.chmod(0o755)


def _write_python_stub(path: Path) -> None:
    _write_executable(
        path,
        """#!/usr/bin/env bash
printf '%s\n' "$0"
""",
    )


@pytest.fixture
def toolchain_repo(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    root = tmp_path / "repo"
    (root / "bin").mkdir(parents=True)
    (root / "project").mkdir()
    shutil.copy2(REPO_ROOT / "bin" / "_python-toolchain", root / "bin" / "_python-toolchain")
    for entrypoint in ENTRYPOINTS:
        shutil.copy2(REPO_ROOT / "bin" / entrypoint, root / "bin" / entrypoint)
    _write_executable(
        root / "bin" / "test-governance",
        """#!/usr/bin/env bash
printf '%s\n' 'FOCUSED' 'fixture selection' 'tests/test_check.py'
""",
    )
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
if [[ "$*" == python\\ find\\ --no-project\\ * ]]; then
  printf '%s\\n' "${@: -1}"
elif [[ "$*" == "python dir" ]]; then
  printf '%s\\n' "$TOOLCHAIN_TEST_MANAGED_ROOT"
fi
""",
    )
    environment = os.environ.copy()
    environment["PATH"] = f"{tool_dir}:{environment['PATH']}"
    environment["TOOLCHAIN_TEST_LOG"] = str(log_path)
    environment["TOOLCHAIN_TEST_MANAGED_ROOT"] = str(tool_dir / "managed-python")
    return root, environment


def _run_path(
    executable: Path,
    environment: dict[str, str],
    *arguments: str,
    cwd: Path,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(executable), *arguments],
        cwd=cwd,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )


def _run(
    root: Path,
    environment: dict[str, str],
    entrypoint: str,
    *arguments: str,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    return _run_path(root / "bin" / entrypoint, environment, *arguments, cwd=cwd or root)


def _calls(environment: dict[str, str]) -> list[str]:
    log_path = Path(environment["TOOLCHAIN_TEST_LOG"])
    return log_path.read_text().splitlines() if log_path.exists() else []


def test_test_defaults_to_every_repository_test_from_any_cwd(
    toolchain_repo: tuple[Path, dict[str, str]], tmp_path: Path
) -> None:
    root, environment = toolchain_repo

    result = _run(root, environment, "test", cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert _calls(environment) == [
        (
            f"uv cwd={root} args=run --project {root / 'project'} --locked "
            f"--managed-python python -c {PROBE}"
        ),
        (
            f"uv cwd={root} args=run --project {root / 'project'} --locked "
            "--managed-python python -m pytest -q project/tests tests"
        ),
    ]


def _assert_selected_repository(
    root: Path,
    environment: dict[str, str],
    result: subprocess.CompletedProcess[str],
) -> None:
    assert result.returncode == 0, result.stderr
    calls = _calls(environment)
    assert calls
    assert all(f"--project {root / 'project'} --locked" in call for call in calls), calls


@pytest.mark.parametrize(("entrypoint", "arguments"), SYMLINK_INVOCATIONS)
def test_installed_symlink_chain_selects_the_owning_repository(
    toolchain_repo: tuple[Path, dict[str, str]],
    tmp_path: Path,
    entrypoint: str,
    arguments: tuple[str, ...],
) -> None:
    root, environment = toolchain_repo
    first_dir = tmp_path / "first-bin"
    second_dir = tmp_path / "second-bin"
    first_dir.mkdir()
    second_dir.mkdir()
    (first_dir / entrypoint).symlink_to(root / "bin" / entrypoint)
    launcher = second_dir / entrypoint
    launcher.symlink_to(Path("..") / "first-bin" / entrypoint)

    result = _run_path(launcher, environment, *arguments, cwd=tmp_path)

    _assert_selected_repository(root, environment, result)


@pytest.mark.parametrize(
    "arguments",
    [("--vital",), ("--changed-from", "HEAD~1")],
)
def test_test_governed_lanes_run_selected_proofs(
    toolchain_repo: tuple[Path, dict[str, str]], arguments: tuple[str, ...]
) -> None:
    root, environment = toolchain_repo

    result = _run(root, environment, "test", *arguments)

    assert result.returncode == 0, result.stderr
    assert "TEST GOVERNED FOCUSED: fixture selection" in result.stdout
    assert _calls(environment) == [
        (
            f"uv cwd={root} args=run --project {root / 'project'} --locked "
            f"--managed-python python -c {PROBE}"
        ),
        (
            f"uv cwd={root} args=run --project {root / 'project'} --locked "
            "--managed-python python -m pytest -q tests/test_check.py"
        ),
    ]


@pytest.mark.parametrize(
    ("entrypoint", "arguments"),
    [
        ("setup", ()),
        ("test", ("tests/test_check.py", "-q")),
        ("python", ("--version",)),
    ],
)
def test_authoritative_runtime_override_is_used_for_probe_and_command(
    toolchain_repo: tuple[Path, dict[str, str]],
    tmp_path: Path,
    entrypoint: str,
    arguments: tuple[str, ...],
) -> None:
    root, environment = toolchain_repo
    runtime = tmp_path / "candidate-python"
    _write_python_stub(runtime)
    environment["TOOLCHAIN_PYTHON"] = str(runtime)

    result = _run(root, environment, entrypoint, *arguments)

    assert result.returncode == 0, result.stderr
    calls = _calls(environment)
    assert len(calls) == 4
    assert calls[0] == f"uv cwd={root} args=python find --no-project {runtime}"
    assert calls[1] == f"uv cwd={root} args=python dir"
    assert all(f"--python {runtime} --no-managed-python" in call for call in calls[2:])
