from __future__ import annotations

import os
import shutil
import subprocess
import sys
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
    (root / "project" / "tests").mkdir()
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
if [[ "${VIRTUAL_ENV+x}" == x ]]; then
  echo 'Inherited environment reached project selection' >&2
  exit 87
fi
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

    environment["VIRTUAL_ENV"] = str(tmp_path / "standalone-script-environment")

    result = _run(root, environment, "test", cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert _calls(environment) == [
        (
            f"uv cwd={root} args=run --project {root / 'project'} --locked "
            f"--managed-python python -c {PROBE}"
        ),
        (
            f"uv cwd={root} args=run --project {root / 'project'} --locked "
            f"--managed-python python {root}/lib/agentic_starter/test_runner.py "
            f"-m pytest -q --junitxml {root}/.kickoff/test-timing/full.xml "
            "-o junit_family=xunit1 project/tests tests"
        ),
    ]


@pytest.mark.skipif(sys.platform != "darwin", reason="Dropbox ignore attributes are macOS-only")
def test_wrapper_run_excludes_runtime_state_from_dropbox_sync(
    toolchain_repo: tuple[Path, dict[str, str]],
) -> None:
    root, environment = toolchain_repo

    result = _run(root, environment, "setup")

    assert result.returncode == 0, result.stderr
    for attribute in ("com.dropbox.ignored", "com.apple.fileprovider.ignore#P"):
        stored = subprocess.run(
            ["/usr/bin/xattr", "-p", attribute, str(root / ".kickoff")],
            capture_output=True,
            text=True,
            check=False,
        )
        assert stored.stdout.strip() == "1", (
            f"RUNTIME STATE NOT SYNC-EXCLUDED {attribute}: {stored.stderr}"
        )


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
            f"--managed-python python {root}/lib/agentic_starter/test_runner.py "
            "-m pytest -q tests/test_check.py"
        ),
    ]


def test_reuse_lane_runs_native_runner_families_and_nothing_when_nothing_changed(
    toolchain_repo: tuple[Path, dict[str, str]],
) -> None:
    root, environment = toolchain_repo
    stub = root / "bin" / "test-governance"
    runner = f"{root}/lib/agentic_starter/test_runner.py -m pytest"

    _write_executable(
        stub,
        "#!/usr/bin/env bash\n"
        '[[ "$1" == select ]] || exit 0\n'
        "printf '%s\\n' FOCUSED 'fixture selection' tests/test_check.py "
        "'command project/tests/smoke.rs --quiet'\n",
    )
    selected = _run(root, environment, "test", "--reuse")
    selected_calls = [call for call in _calls(environment) if runner in call]
    Path(environment["TOOLCHAIN_TEST_LOG"]).unlink()
    _write_executable(
        stub,
        "#!/usr/bin/env bash\n"
        '[[ "$1" == select ]] || exit 0\n'
        "printf '%s\\n' NONE 'nothing changed'\n",
    )
    unchanged = _run(root, environment, "test", "--reuse")

    assert (
        selected.returncode == 0
        and [call.split(runner, 1)[1] for call in selected_calls]
        == [" -q tests/test_check.py", " project/tests/smoke.rs --quiet"]
        and unchanged.returncode == 0
        and not any(runner in call for call in _calls(environment))
    ), (
        "REUSE LANE SKIPPED A NATIVE-RUNNER FAMILY OR RAN TESTS WHEN NOTHING CHANGED: "
        + selected.stderr
        + unchanged.stderr
    )


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


def test_a_declared_native_suite_is_a_second_lane_and_only_both_lanes_prove_the_tree(
    toolchain_repo: tuple[Path, dict[str, str]], tmp_path: Path
) -> None:
    """Native lane: three projects whose product is not Python each wrote their own way to
    run its suite beside pytest, and each first met the gap as a failed parallel run.

    A project declares the suite with one executable. Against a fixture whose product has
    no pytest tests, the oracle is the exact commands the entry point issues for a full
    run, a native-only selection and an undeclared suite, and the status it hands the
    proven-tree record when the native lane fails after pytest passed.
    """
    root, environment = toolchain_repo
    (root / "project" / "tests").rmdir()
    recorded = tmp_path / "governance.log"
    _write_executable(
        root / "bin" / "test-governance",
        f"#!/usr/bin/env bash\nprintf '%s\\n' \"$*\" >> {recorded}\n",
    )
    runner = f"{root}/lib/agentic_starter/test_runner.py -m pytest"
    native = f"{root}/lib/agentic_starter/native_suite.py"

    undeclared = _run(root, environment, "test", "native")
    Path(environment["TOOLCHAIN_TEST_LOG"]).unlink()
    _write_executable(root / "bin" / "test-native", "#!/bin/sh\nexit 0\n")
    full = _run(root, environment, "test")
    full_calls = [call.split(" python ", 1)[1] for call in _calls(environment)[1:]]
    Path(environment["TOOLCHAIN_TEST_LOG"]).unlink()
    selected = _run(root, environment, "test", "native", "--filter", "one")
    selected_calls = [call.split(" python ", 1)[1] for call in _calls(environment)[1:]]
    Path(environment["TOOLCHAIN_TEST_LOG"]).unlink()
    recorded.unlink()
    environment["TOOLCHAIN_TEST_FAIL_MATCH"] = "native_suite.py"
    failed = _run(root, environment, "test")
    failed_calls = [call for call in _calls(environment) if runner in call or native in call]

    assert (
        undeclared.returncode == 2
        and "no native suite is declared" in undeclared.stderr
        and full.returncode == 0
        and full_calls
        == [
            f"{runner} -q --junitxml {root}/.kickoff/test-timing/full.xml "
            "-o junit_family=xunit1 tests",
            native,
        ]
        and selected.returncode == 0
        and selected_calls == [f"{native} --filter one"]
        and failed.returncode == 23
        and len(failed_calls) == 2
        and recorded.read_text().splitlines()[-1] == "reuse finish --exit 23"
    ), (
        "NATIVE SUITE WAS NOT A SECOND LANE, OR A TREE WAS PROVEN WITHOUT IT: "
        + full.stderr
        + failed.stderr
    )


def test_the_native_suite_runs_supervised_with_its_arguments_and_never_signs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Native lane: the declared runner gets the caller's selection, the supervisor's
    status and the same no-signing override the pytest fixtures get.

    A stand-in runner records what it was given and exits with a chosen status; the oracle
    is that record, the returned status, and the refusal when no runner is declared.
    """
    sys.path.insert(0, str(REPO_ROOT / "lib"))
    from agentic_starter import native_suite

    # This run's own setup already switched signing off; the lane must do it for itself.
    for name in [key for key in os.environ if key.startswith("GIT_CONFIG_")]:
        monkeypatch.delenv(name)
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(tmp_path / "gitconfig"))
    (tmp_path / "gitconfig").write_text("[commit]\n\tgpgsign = true\n")
    root = tmp_path / "repo"
    (root / "bin").mkdir(parents=True)
    (root / "tests").mkdir()
    (root / "tests" / "proof-estate.yaml").write_text("hang_timeout_seconds: 30\n")
    absent = native_suite.main(["--filter", "one"], root)
    seen = tmp_path / "seen.txt"
    _write_executable(
        root / "bin" / "test-native",
        "#!/bin/sh\n"
        f'printf \'%s\\n\' "$*" "$(git config --get commit.gpgsign)" "$PWD" > {seen}\n'
        "exit 7\n",
    )
    status = native_suite.main(["--filter", "one"], root)

    assert (
        absent == 2
        and status == 7
        and seen.read_text().splitlines() == ["--filter one", "false", str(root)]
    ), "NATIVE SUITE RAN UNSUPERVISED, LOST ITS SELECTION OR SIGNED FIXTURE COMMITS"
