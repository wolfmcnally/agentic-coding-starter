from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK_SOURCE = REPO_ROOT / "bin" / "check"
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
def check_repo(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    root = tmp_path / "repo"
    (root / "bin").mkdir(parents=True)
    (root / "project").mkdir()
    (root / "tests").mkdir()
    shutil.copy2(CHECK_SOURCE, root / "bin" / "check")
    shutil.copy2(REPO_ROOT / "bin" / "_python-toolchain", root / "bin" / "_python-toolchain")
    shutil.copy2(REPO_ROOT / "bin" / "test", root / "bin" / "test")
    (root / "project" / "pyproject.toml").write_text("[project]\nname='fixture'\n")
    (root / "project" / "uv.lock").write_text("version = 1\n")
    (root / "project" / ".python-version").write_text("3.11\n")
    (root / "AGENTS.md").symlink_to("CLAUDE.md")
    (root / "CLAUDE.md").write_text("# Fixture\n")

    log_path = tmp_path / "calls.log"
    tool_dir = tmp_path / "tools"
    tool_dir.mkdir()
    _write_executable(
        tool_dir / "uv",
        """#!/usr/bin/env bash
set -u
printf 'uv cwd=%s args=%s\\n' "$PWD" "$*" >> "$CHECK_TEST_LOG"
if [[ -n "${CHECK_TEST_FAIL_MATCH:-}" && "$*" == *"$CHECK_TEST_FAIL_MATCH"* ]]; then
  exit "${CHECK_TEST_FAIL_CODE:-23}"
fi
if [[ "$*" == python\\ find\\ --no-project\\ * ]]; then
  printf '%s\\n' "${@: -1}"
elif [[ "$*" == "python dir" ]]; then
  printf '%s\\n' "$CHECK_TEST_MANAGED_ROOT"
fi
""",
    )
    _write_executable(
        root / "bin" / "check-anonymization.sh",
        """#!/usr/bin/env bash
printf 'policy cwd=%s\\n' "$PWD" >> "$CHECK_TEST_LOG"
""",
    )
    _write_executable(
        root / "bin" / "kickoff-config",
        """#!/usr/bin/env bash
printf 'config cwd=%s args=%s\\n' "$PWD" "$*" >> "$CHECK_TEST_LOG"
""",
    )
    environment = os.environ.copy()
    environment["PATH"] = f"{tool_dir}:{environment['PATH']}"
    environment["CHECK_TEST_LOG"] = str(log_path)
    environment["CHECK_TEST_MANAGED_ROOT"] = str(tool_dir / "managed-python")
    return root, environment


def _run(
    root: Path,
    environment: dict[str, str],
    *arguments: str,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(root / "bin" / "check"), *arguments],
        cwd=cwd or root,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )


def test_all_is_default_locked_ordered_and_cwd_independent(
    check_repo: tuple[Path, dict[str, str]], tmp_path: Path
) -> None:
    root, environment = check_repo
    result = _run(root, environment, cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    calls = Path(environment["CHECK_TEST_LOG"]).read_text().splitlines()
    assert calls == [
        (
            f"uv cwd={root} args=run --project {root / 'project'} --locked "
            f"--managed-python python -c {PROBE}"
        ),
        (
            f"uv cwd={root / 'project'} args=run --locked --managed-python "
            "ruff check example tests ../bin/kickoff-config ../tests"
        ),
        (
            f"uv cwd={root / 'project'} args=run --locked --managed-python ruff format --check "
            "example tests ../bin/kickoff-config ../tests"
        ),
        (
            f"uv cwd={root} args=run --project {root / 'project'} --locked "
            f"--managed-python python -c {PROBE}"
        ),
        (
            f"uv cwd={root} args=run --project {root / 'project'} --locked "
            "--managed-python python -m pytest -q project/tests tests"
        ),
        f"config cwd={root} args=show",
        f"policy cwd={root}",
    ]
    assert "CHECK ALL PASS" in result.stdout


@pytest.mark.parametrize(
    ("mode", "expected"),
    [
        ("lint", "ruff check"),
        ("format", "ruff format --check"),
        ("test", "pytest -q"),
        ("policy", "policy cwd="),
    ],
)
def test_named_mode_runs_only_selected_gate(
    check_repo: tuple[Path, dict[str, str]], mode: str, expected: str
) -> None:
    root, environment = check_repo
    result = _run(root, environment, mode)

    assert result.returncode == 0, result.stderr
    calls = Path(environment["CHECK_TEST_LOG"]).read_text().splitlines()
    if mode == "policy":
        assert calls == [
            (
                f"uv cwd={root} args=run --project {root / 'project'} --locked "
                f"--managed-python python -c {PROBE}"
            ),
            f"config cwd={root} args=show",
            f"policy cwd={root}",
        ]
    elif mode == "test":
        assert len(calls) == 3
        assert calls[0].endswith(f"python -c {PROBE}")
        assert calls[1].endswith(f"python -c {PROBE}")
        assert expected in calls[2]
    else:
        assert len(calls) == 2
        assert calls[0].endswith(f"python -c {PROBE}")
        assert expected in calls[1]
    assert f"CHECK {mode} PASS" in result.stdout


def test_failure_status_is_preserved(
    check_repo: tuple[Path, dict[str, str]],
) -> None:
    root, environment = check_repo
    environment["CHECK_TEST_FAIL_MATCH"] = "ruff format"
    environment["CHECK_TEST_FAIL_CODE"] = "37"

    result = _run(root, environment, "format")

    assert result.returncode == 37
    assert "CHECK format FAIL (exit 37)" in result.stderr
    assert "CHECK format PASS" not in result.stdout


def test_missing_uv_fails_clearly(
    check_repo: tuple[Path, dict[str, str]],
) -> None:
    root, environment = check_repo
    environment["PATH"] = "/usr/bin:/bin"

    result = _run(root, environment)

    assert result.returncode == 1
    assert "CHECK ERROR missing prerequisite: uv" in result.stderr


@pytest.mark.parametrize(
    "missing", [".python-version", "pyproject.toml", "uv.lock", "_python-toolchain"]
)
def test_missing_project_contract_fails_clearly(
    check_repo: tuple[Path, dict[str, str]], missing: str
) -> None:
    root, environment = check_repo
    if missing == "_python-toolchain":
        (root / "bin" / missing).unlink()
        expected_path = f"bin/{missing}"
    else:
        (root / "project" / missing).unlink()
        expected_path = f"project/{missing}"

    result = _run(root, environment)

    assert result.returncode == 1
    assert f"CHECK ERROR missing required file: {expected_path}" in result.stderr


def test_missing_test_entrypoint_fails_clearly(
    check_repo: tuple[Path, dict[str, str]],
) -> None:
    root, environment = check_repo
    (root / "bin" / "test").unlink()

    result = _run(root, environment)

    assert result.returncode == 1
    assert "CHECK ERROR missing required executable: bin/test" in result.stderr


@pytest.mark.parametrize("arguments", [("bogus",), ("all", "extra")])
def test_invalid_invocation_is_usage_error(
    check_repo: tuple[Path, dict[str, str]], arguments: tuple[str, ...]
) -> None:
    root, environment = check_repo

    result = _run(root, environment, *arguments)

    assert result.returncode == 2
    assert "Usage: ./bin/check" in result.stderr


def test_help_does_not_require_toolchain(
    check_repo: tuple[Path, dict[str, str]],
) -> None:
    root, environment = check_repo
    environment["PATH"] = "/usr/bin:/bin"

    result = _run(root, environment, "--help")

    assert result.returncode == 0
    assert "Usage: ./bin/check" in result.stdout


def test_authoritative_runtime_override_applies_to_probe_and_gate(
    check_repo: tuple[Path, dict[str, str]],
    tmp_path: Path,
) -> None:
    root, environment = check_repo
    runtime = tmp_path / "candidate-python"
    _write_python_stub(runtime)
    environment["TOOLCHAIN_PYTHON"] = str(runtime)

    result = _run(root, environment, "lint")

    assert result.returncode == 0, result.stderr
    calls = Path(environment["CHECK_TEST_LOG"]).read_text().splitlines()
    assert len(calls) == 4
    assert calls[0] == f"uv cwd={root} args=python find --no-project {runtime}"
    assert calls[1] == f"uv cwd={root} args=python dir"
    assert all(f"--python {runtime} --no-managed-python" in call for call in calls[2:])


def test_authoritative_runtime_probe_failure_stops_before_gate_without_fallback(
    check_repo: tuple[Path, dict[str, str]],
    tmp_path: Path,
) -> None:
    root, environment = check_repo
    runtime = tmp_path / "candidate-python"
    _write_python_stub(runtime)
    environment["TOOLCHAIN_PYTHON"] = str(runtime)
    environment["CHECK_TEST_FAIL_MATCH"] = PROBE
    environment["CHECK_TEST_FAIL_CODE"] = "43"

    result = _run(root, environment, "lint")

    assert result.returncode == 43
    assert "dependency-chain probe failed" in result.stderr
    assert "no runtime fallback was attempted" in result.stderr
    calls = Path(environment["CHECK_TEST_LOG"]).read_text().splitlines()
    assert calls == [
        f"uv cwd={root} args=python find --no-project {runtime}",
        f"uv cwd={root} args=python dir",
        (
            f"uv cwd={root} args=run --project {root / 'project'} --locked "
            f"--python {runtime} --no-managed-python python -c {PROBE}"
        ),
    ]
