"""Behavioral coverage for durable, candidate-bound full-gate receipts."""

from __future__ import annotations

import json
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_SOURCE = REPO_ROOT / "bin" / "check-receipt"
TREE_SOURCE = REPO_ROOT / "bin" / "kickoff-tree-id"
HOOK_SOURCE = REPO_ROOT / ".githooks" / "pre-push"
ZERO_SHA = "0" * 40


def write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "bin").mkdir(parents=True)
    (root / ".githooks").mkdir()
    shutil.copy2(SCRIPT_SOURCE, root / "bin" / "check-receipt")
    shutil.copy2(TREE_SOURCE, root / "bin" / "kickoff-tree-id")
    shutil.copy2(HOOK_SOURCE, root / ".githooks" / "pre-push")
    write_executable(
        root / "bin" / "python",
        "\n".join(
            (
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                'if [[ "${CHECK_RECEIPT_TEST_RUNTIME_MODE:-}" == "fail" ]]; then',
                "  echo 'selected runtime probe failed' >&2",
                "  exit 23",
                "fi",
                'if [[ "${CHECK_RECEIPT_TEST_RUNTIME_MODE:-}" == "malformed" ]]; then',
                "  printf '%s\\n' 'not-json'",
                "  exit 0",
                "fi",
                f"selected={shlex.quote(sys.executable)}",
                'if [[ -n "${CHECK_RECEIPT_TEST_MANAGED_PYTHON:-}" ]]; then',
                '  selected="$CHECK_RECEIPT_TEST_MANAGED_PYTHON"',
                "fi",
                'if [[ -n "${TOOLCHAIN_PYTHON:-}" ]]; then',
                '  selected="$TOOLCHAIN_PYTHON"',
                "fi",
                'if [[ -n "${CHECK_RECEIPT_TEST_PYTHON_VERSION:-}" ]]; then',
                '  export PYTHONPATH="$PWD/.kickoff/runtime-site"',
                "fi",
                'exec "$selected" "$@"',
                "",
            )
        ),
    )
    write_executable(
        root / "bin" / "check",
        "#!/usr/bin/env bash\n"
        'mkdir -p "$PWD/.kickoff"\n'
        "printf 'called\\n' >> \"$PWD/.kickoff/hook-called\"\n",
    )
    (root / ".gitignore").write_text(".kickoff/\n", encoding="utf-8")
    (root / "tracked.txt").write_text("fixture\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q", "-b", "master"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "fixture@example.invalid"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Fixture"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "fixture"], cwd=root, check=True)
    site = root / ".kickoff" / "runtime-site"
    site.mkdir(parents=True)
    (site / "sitecustomize.py").write_text(
        "import os\n"
        "import platform\n"
        "import sys\n"
        "if version := os.environ.get('CHECK_RECEIPT_TEST_PYTHON_VERSION'):\n"
        "    platform.python_version = lambda: version\n"
        "if identity := os.environ.get('CHECK_RECEIPT_TEST_RUNTIME_IDENTITY'):\n"
        "    sys.executable = identity\n"
        "    sys._base_executable = identity\n",
        encoding="utf-8",
    )
    return root


def run_receipt(
    root: Path,
    *arguments: str,
    stdin: str | None = None,
    environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "bin" / "check-receipt"), *arguments],
        cwd=root,
        env=environment,
        input=stdin,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )


def candidate(root: Path) -> str:
    result = run_receipt(root, "candidate", "--root", str(root))
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def head(root: Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()


def push_input(root: Path, local_sha: str | None = None) -> str:
    selected = local_sha or head(root)
    return f"refs/heads/master {selected} refs/heads/master {ZERO_SHA}\n"


def record_pass(
    root: Path,
    *,
    output: str = "gate output\n",
    environment: dict[str, str] | None = None,
) -> tuple[Path, Path]:
    identity = candidate(root)
    begun = run_receipt(
        root,
        "begin",
        "--root",
        str(root),
        "--candidate",
        identity,
        environment=environment,
    )
    assert begun.returncode == 0, begun.stderr
    log = Path(begun.stdout.strip())
    log.write_text(output, encoding="utf-8")
    completed = run_receipt(
        root,
        "complete",
        "--root",
        str(root),
        "--log",
        str(log),
        "--candidate-before",
        identity,
        "--candidate-after",
        identity,
        "--exit-code",
        "0",
        "--outcome",
        "passed",
        environment=environment,
    )
    assert completed.returncode == 0, completed.stderr
    assert "CHECK ALL PASS" in completed.stdout
    receipts = list((root / ".kickoff" / "check-all" / "receipts").glob("*.json"))
    assert len(receipts) == 1
    return log, receipts[0]


def test_passed_run_is_durable_and_reusable_for_exact_clean_head(
    repository: Path,
) -> None:
    log, receipt_path = record_pass(repository)

    result = run_receipt(
        repository,
        "pre-push",
        "--root",
        str(repository),
        stdin=push_input(repository),
    )

    assert result.returncode == 0, result.stderr
    assert "CHECK RECEIPT HIT" in result.stdout
    assert log.read_text(encoding="utf-8").endswith("CHECK ALL PASS\n")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    run = json.loads((repository / receipt["run"]).read_text(encoding="utf-8"))
    assert receipt["candidate_id"] == candidate(repository)
    assert run["status"] == "passed"
    assert run["candidate_before"] == run["candidate_after"]


def test_tampered_log_never_reuses_receipt(repository: Path) -> None:
    log, _ = record_pass(repository)
    with log.open("a", encoding="utf-8") as handle:
        handle.write("tampered\n")

    result = run_receipt(
        repository,
        "pre-push",
        "--root",
        str(repository),
        stdin=push_input(repository),
    )

    assert result.returncode == 1
    assert "reason=receipt-log-mismatch" in result.stderr


def test_candidate_drift_is_terminal_and_never_creates_a_receipt(
    repository: Path,
) -> None:
    identity = candidate(repository)
    begun = run_receipt(repository, "begin", "--root", str(repository), "--candidate", identity)
    assert begun.returncode == 0, begun.stderr
    log = Path(begun.stdout.strip())
    log.write_text("gate output\n", encoding="utf-8")

    completed = run_receipt(
        repository,
        "complete",
        "--root",
        str(repository),
        "--log",
        str(log),
        "--candidate-before",
        identity,
        "--candidate-after",
        "1" * 64,
        "--exit-code",
        "1",
        "--outcome",
        "candidate-drift",
    )

    assert completed.returncode == 0, completed.stderr
    metadata = json.loads(log.with_suffix(".json").read_text(encoding="utf-8"))
    assert metadata["status"] == "candidate-drift"
    assert not (repository / ".kickoff" / "check-all" / "receipts").exists()


def test_pre_push_hook_skips_only_a_verified_hit(repository: Path) -> None:
    record_pass(repository)
    marker = repository / ".kickoff" / "hook-called"
    hook = repository / ".githooks" / "pre-push"

    hit = subprocess.run(
        [str(hook), "origin", "fixture"],
        cwd=repository,
        input=push_input(repository),
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )
    assert hit.returncode == 0, hit.stderr
    assert "CHECK RECEIPT HIT" in hit.stdout
    assert not marker.exists()

    (repository / "tracked.txt").write_text("dirty\n", encoding="utf-8")
    miss = subprocess.run(
        [str(hook), "origin", "fixture"],
        cwd=repository,
        input=push_input(repository),
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )
    assert miss.returncode == 0, miss.stderr
    assert "reason=working-tree-not-clean" in miss.stderr
    assert marker.read_text(encoding="utf-8") == "called\n"
