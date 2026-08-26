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


def test_setup_syncs_the_pinned_locked_environment_from_any_cwd(
    toolchain_repo: tuple[Path, dict[str, str]], tmp_path: Path
) -> None:
    root, environment = toolchain_repo

    result = _run(root, environment, "setup", cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert _calls(environment) == [
        f"uv cwd={root} args=sync --project {root / 'project'} --locked --managed-python",
        (
            f"uv cwd={root} args=run --project {root / 'project'} --locked "
            f"--managed-python python -c {PROBE}"
        ),
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
            f"--managed-python python -c {PROBE}"
        ),
        (
            f"uv cwd={root} args=run --project {root / 'project'} --locked "
            "--managed-python python -m pytest -q project/tests tests"
        ),
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
            f"--managed-python python -c {PROBE}"
        ),
        (
            f"uv cwd={root} args=run --project {root / 'project'} --locked "
            "--managed-python python -m pytest tests/test_check.py -k failure -q"
        ),
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
            f"--managed-python python -c {PROBE}"
        ),
        (
            f"uv cwd={root} args=run --project {root / 'project'} --locked "
            "--managed-python python -c print('ok')"
        ),
    ]


def _assert_selected_repository(
    root: Path, environment: dict[str, str], result: subprocess.CompletedProcess[str]
) -> None:
    assert result.returncode == 0, result.stderr
    calls = _calls(environment)
    assert calls, "the entry point dispatched no command"
    assert all(call.startswith(f"uv cwd={root} args=") for call in calls), calls
    assert all(f"--project {root / 'project'} --locked" in call for call in calls), calls


@pytest.mark.parametrize(("entrypoint", "arguments"), SYMLINK_INVOCATIONS)
def test_installed_symlink_selects_the_owning_repository(
    toolchain_repo: tuple[Path, dict[str, str]],
    tmp_path: Path,
    entrypoint: str,
    arguments: tuple[str, ...],
) -> None:
    root, environment = toolchain_repo
    launcher_dir = tmp_path / "installed-bin"
    launcher_dir.mkdir()
    launcher = launcher_dir / entrypoint
    launcher.symlink_to(Path("..") / "repo" / "bin" / entrypoint)

    result = _run_path(launcher, environment, *arguments, cwd=tmp_path)

    _assert_selected_repository(root, environment, result)


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
    ("entrypoint", "arguments", "match", "exit_code"),
    [
        ("setup", (), "sync", "31"),
        ("test", (), "python -m pytest", "32"),
        ("python", ("-c", "print('ok')"), "print('ok')", "33"),
    ],
)
def test_child_failure_status_is_preserved(
    toolchain_repo: tuple[Path, dict[str, str]],
    entrypoint: str,
    arguments: tuple[str, ...],
    match: str,
    exit_code: str,
) -> None:
    root, environment = toolchain_repo
    environment["TOOLCHAIN_TEST_FAIL_MATCH"] = match
    environment["TOOLCHAIN_TEST_FAIL_CODE"] = exit_code

    result = _run(root, environment, entrypoint, *arguments)

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
@pytest.mark.parametrize(
    "missing", [".python-version", "pyproject.toml", "uv.lock", "_python-toolchain"]
)
def test_missing_contract_member_fails_clearly(
    toolchain_repo: tuple[Path, dict[str, str]],
    entrypoint: str,
    missing: str,
) -> None:
    root, environment = toolchain_repo
    if missing == "_python-toolchain":
        (root / "bin" / missing).unlink()
        expected_path = f"bin/{missing}"
    else:
        (root / "project" / missing).unlink()
        expected_path = f"project/{missing}"

    result = _run(root, environment, entrypoint)

    assert result.returncode == 1
    assert f"{entrypoint.upper()} ERROR missing required file: {expected_path}" in result.stderr


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


@pytest.mark.parametrize("entrypoint", ENTRYPOINTS)
def test_invalid_authoritative_runtime_fails_without_calling_uv_or_falling_back(
    toolchain_repo: tuple[Path, dict[str, str]],
    tmp_path: Path,
    entrypoint: str,
) -> None:
    root, environment = toolchain_repo
    environment["TOOLCHAIN_PYTHON"] = str(tmp_path / "missing-python")

    result = _run(root, environment, entrypoint)

    assert result.returncode == 1
    assert "authoritative TOOLCHAIN_PYTHON must be an executable absolute path" in result.stderr
    assert "no runtime fallback was attempted" in result.stderr
    assert _calls(environment) == []


def test_authoritative_runtime_refuses_self_referential_project_environment(
    toolchain_repo: tuple[Path, dict[str, str]],
) -> None:
    root, environment = toolchain_repo
    runtime = root / "project" / ".venv" / "bin" / "python"
    runtime.parent.mkdir(parents=True)
    _write_python_stub(runtime)
    environment["TOOLCHAIN_PYTHON"] = str(runtime)

    result = _run(root, environment, "python", "--version")

    assert result.returncode == 1
    assert "TOOLCHAIN_PYTHON cannot point inside project/.venv" in result.stderr
    assert "select a base interpreter outside the managed project environment" in result.stderr
    assert "no runtime fallback was attempted" in result.stderr
    assert _calls(environment) == [f"uv cwd={root} args=python find --no-project {runtime}"]


def test_authoritative_runtime_probe_failure_preserves_status_and_never_falls_back(
    toolchain_repo: tuple[Path, dict[str, str]],
    tmp_path: Path,
) -> None:
    root, environment = toolchain_repo
    runtime = tmp_path / "candidate-python"
    _write_python_stub(runtime)
    environment["TOOLCHAIN_PYTHON"] = str(runtime)
    environment["TOOLCHAIN_TEST_FAIL_MATCH"] = PROBE
    environment["TOOLCHAIN_TEST_FAIL_CODE"] = "41"

    result = _run(root, environment, "test")

    assert result.returncode == 41
    assert "dependency-chain probe failed" in result.stderr
    assert "no runtime fallback was attempted" in result.stderr
    assert _calls(environment) == [
        f"uv cwd={root} args=python find --no-project {runtime}",
        f"uv cwd={root} args=python dir",
        (
            f"uv cwd={root} args=run --project {root / 'project'} --locked "
            f"--python {runtime} --no-managed-python python -c {PROBE}"
        ),
    ]


def test_uv_managed_authoritative_runtime_retains_managed_selection(
    toolchain_repo: tuple[Path, dict[str, str]],
) -> None:
    root, environment = toolchain_repo
    runtime = Path(environment["TOOLCHAIN_TEST_MANAGED_ROOT"]) / "cpython-test" / "bin" / "python"
    runtime.parent.mkdir(parents=True)
    _write_python_stub(runtime)
    environment["TOOLCHAIN_PYTHON"] = str(runtime)

    result = _run(root, environment, "python", "--version")

    assert result.returncode == 0, result.stderr
    calls = _calls(environment)
    assert calls[:2] == [
        f"uv cwd={root} args=python find --no-project {runtime}",
        f"uv cwd={root} args=python dir",
    ]
    assert all(f"--python {runtime} --managed-python" in call for call in calls[2:])
    assert all("--no-managed-python" not in call for call in calls[2:])
