from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK_SOURCE = REPO_ROOT / "bin" / "check"


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text)
    path.chmod(0o755)


@pytest.fixture
def check_repo(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    root = tmp_path / "repo"
    (root / "bin").mkdir(parents=True)
    (root / "project").mkdir()
    (root / "tests").mkdir()
    shutil.copy2(CHECK_SOURCE, root / "bin" / "check")
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
            f"uv cwd={root / 'project'} args=run --locked --managed-python "
            "ruff check example tests ../bin/kickoff-config ../tests"
        ),
        (
            f"uv cwd={root / 'project'} args=run --locked --managed-python ruff format --check "
            "example tests ../bin/kickoff-config ../tests"
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
            f"config cwd={root} args=show",
            f"policy cwd={root}",
        ]
    else:
        assert len(calls) == 1
        assert expected in calls[0]
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


@pytest.mark.parametrize("missing", [".python-version", "pyproject.toml", "uv.lock"])
def test_missing_project_contract_fails_clearly(
    check_repo: tuple[Path, dict[str, str]], missing: str
) -> None:
    root, environment = check_repo
    (root / "project" / missing).unlink()

    result = _run(root, environment)

    assert result.returncode == 1
    assert f"CHECK ERROR missing required file: project/{missing}" in result.stderr


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
