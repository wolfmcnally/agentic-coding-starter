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
    shutil.copy2(REPO_ROOT / "bin" / "kickoff-evidence", root / "bin" / "kickoff-evidence")
    shutil.copy2(REPO_ROOT / "bin" / "kickoff-tree-id", root / "bin" / "kickoff-tree-id")
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
if [[ -n "${CHECK_POLICY_FAIL_CODE:-}" ]]; then
  exit "$CHECK_POLICY_FAIL_CODE"
fi
""",
    )
    _write_executable(
        root / "bin" / "kickoff-config",
        """#!/usr/bin/env bash
printf 'config cwd=%s args=%s\\n' "$PWD" "$*" >> "$CHECK_TEST_LOG"
""",
    )
    _write_executable(
        root / "bin" / "lessons",
        """#!/usr/bin/env bash
printf 'lessons cwd=%s args=%s\\n' "$PWD" "$*" >> "$CHECK_TEST_LOG"
""",
    )
    _write_executable(
        root / "bin" / "treatise",
        """#!/usr/bin/env bash
printf 'treatise cwd=%s args=%s\\n' "$PWD" "$*" >> "$CHECK_TEST_LOG"
""",
    )
    _write_executable(
        root / "bin" / "test-governance",
        """#!/usr/bin/env bash
printf 'governance cwd=%s args=%s\n' "$PWD" "$*" >> "$CHECK_TEST_LOG"
if [[ "${1:-}" == "select" ]]; then
  printf '%s\n' 'FOCUSED' 'fixture selection' 'tests/test_check.py'
fi
""",
    )
    _write_executable(
        root / "bin" / "check-receipt",
        """#!/usr/bin/env bash
set -euo pipefail
case "$1" in
  candidate)
    printf '%064d\n' 0
    ;;
  begin)
    mkdir -p "$PWD/.kickoff/check-all/logs"
    log="$PWD/.kickoff/check-all/logs/fixture.log"
    : > "$log"
    printf '%s\n' "$log"
    ;;
  complete)
    if [[ " $* " == *" --outcome passed "* ]]; then
      printf '%s\n' \
        'CHECK RECEIPT STORED candidate=fixture log=.kickoff/check-all/logs/fixture.log' \
        'CHECK ALL PASS'
    fi
    ;;
  fingerprint)
    printf '%064d\n' 1
    ;;
  pre-push)
    exit 1
    ;;
esac
""",
    )
    for executable, label in (
        ("execution-telemetry", "telemetry"),
        ("check-harness-parity", "parity"),
        ("check-toolchain-callers", "callers"),
        ("check-execution-dashboards", "dashboards"),
        ("check-catalogs", "catalogs"),
        ("check-hooks-installed", "hooksinstalled"),
        ("check-shell-syntax", "shellsyntax"),
        ("new-name", "newname"),
        ("check-log", "log"),
        ("check-candidate-partition", "partition"),
        ("check-log-prefix", "logprefix"),
        ("check-log-monotonic", "logmonotonic"),
        ("kickoff-command-zero", "commandzero"),
        ("log-append", "logappend"),
        ("log-relocate", "logrelocate"),
        ("normalize-final-newline", "finalnewline"),
    ):
        _write_executable(
            root / "bin" / executable,
            f'#!/usr/bin/env bash\nprintf \'{label} cwd=%s\\n\' "$PWD" >> "$CHECK_TEST_LOG"\n',
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
            "ruff check example tests ../lib ../bin/kickoff-config ../bin/kickoff-evidence "
            "../bin/kickoff-tree-id ../bin/check-receipt ../bin/execution-telemetry "
            "../bin/check-execution-dashboards ../bin/check-harness-parity "
            "../bin/check-toolchain-callers ../bin/lessons ../bin/treatise "
            "../bin/check-catalogs "
            "../bin/check-hooks-installed ../bin/check-shell-syntax ../bin/new-name "
            "../bin/check-plan-concreteness ../bin/check-plan-delivery ../bin/review-verdicts "
            "../bin/check-log-prefix ../bin/check-log-monotonic ../bin/kickoff-command-zero "
            "../bin/log-append ../bin/log-relocate ../bin/normalize-final-newline "
            "../bin/check-candidate-partition "
            "../tests"
        ),
        (
            f"uv cwd={root / 'project'} args=run --locked --managed-python ruff format --check "
            "example tests ../lib ../bin/kickoff-config ../bin/kickoff-evidence "
            "../bin/kickoff-tree-id ../bin/check-receipt ../bin/execution-telemetry "
            "../bin/check-execution-dashboards ../bin/check-harness-parity "
            "../bin/check-toolchain-callers ../bin/lessons ../bin/treatise "
            "../bin/check-catalogs "
            "../bin/check-hooks-installed ../bin/check-shell-syntax ../bin/new-name "
            "../bin/check-plan-concreteness ../bin/check-plan-delivery ../bin/review-verdicts "
            "../bin/check-log-prefix ../bin/check-log-monotonic ../bin/kickoff-command-zero "
            "../bin/log-append ../bin/log-relocate ../bin/normalize-final-newline "
            "../bin/check-candidate-partition "
            "../tests"
        ),
        (
            f"uv cwd={root} args=run --project {root / 'project'} --locked "
            f"--managed-python python -c {PROBE}"
        ),
        (
            f"uv cwd={root} args=run --project {root / 'project'} --locked "
            "--managed-python python -m pytest -q project/tests tests"
        ),
        f"parity cwd={root}",
        f"callers cwd={root}",
        f"dashboards cwd={root}",
        f"config cwd={root} args=show",
        f"catalogs cwd={root}",
        f"lessons cwd={root} args=validate",
        f"treatise cwd={root} args=validate",
        f"hooksinstalled cwd={root}",
        f"shellsyntax cwd={root}",
        f"log cwd={root}",
        f"partition cwd={root}",
        f"governance cwd={root} args=validate",
        f"policy cwd={root}",
    ]
    assert "CHECK ALL PASS" in result.stdout


def test_all_policy_failure_cannot_be_masked_by_later_policy_output(
    check_repo: tuple[Path, dict[str, str]],
) -> None:
    root, environment = check_repo
    environment["CHECK_POLICY_FAIL_CODE"] = "41"

    result = _run(root, environment, "all")

    assert result.returncode == 41
    assert "CHECK policy-anonymization FAIL (exit 41)" in result.stdout
    assert "CHECK policy PASS" not in result.stdout
    assert "CHECK ALL PASS" not in result.stdout


@pytest.mark.parametrize(
    "arguments",
    [("bogus",), ("all", "extra"), ("changed",), ("changed", "HEAD", "extra")],
)
def test_invalid_invocation_is_usage_error(
    check_repo: tuple[Path, dict[str, str]], arguments: tuple[str, ...]
) -> None:
    root, environment = check_repo

    result = _run(root, environment, *arguments)

    assert result.returncode == 2
    assert "Usage: ./bin/check" in result.stderr


@pytest.mark.parametrize(
    ("arguments", "selection_arguments"),
    [
        (("vital",), "--tier vital --format lines"),
        (("changed", "HEAD~1"), "--changed-from HEAD~1 --format lines"),
    ],
)
def test_governed_iteration_lanes_dispatch_selected_tests_without_receipt(
    check_repo: tuple[Path, dict[str, str]],
    arguments: tuple[str, ...],
    selection_arguments: str,
) -> None:
    root, environment = check_repo

    result = _run(root, environment, *arguments)

    assert result.returncode == 0, result.stderr
    calls = Path(environment["CHECK_TEST_LOG"]).read_text().splitlines()
    assert f"governance cwd={root} args=select {selection_arguments}" in calls
    assert any("python -m pytest -q tests/test_check.py" in call for call in calls)
    assert not any("check-receipt" in call for call in calls)


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
