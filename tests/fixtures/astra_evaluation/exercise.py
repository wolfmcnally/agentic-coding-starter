"""Prepare and locally qualify fixed evaluation inputs; never invokes a model."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def write_files(destination: Path, files: dict[str, str]) -> None:
    for name, body in files.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body)


def prepare(destination: Path, task: dict) -> None:
    destination = destination.resolve()
    if destination == ROOT or ROOT in destination.parents:
        raise ValueError("workspace must be outside this repository")
    destination.mkdir(parents=True, exist_ok=False)
    write_files(destination, task["files"])
    (destination / "TASK.md").write_text(task["prompt"] + "\n")


def check(destination: Path, task: dict) -> subprocess.CompletedProcess[str]:
    # Checks stay in evaluator memory, never copied into the model's workspace.
    program = "from pathlib import Path\n" + task["checks"]
    return subprocess.run(
        [sys.executable, "-B", "-c", program],
        cwd=destination,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def require_failure(result: subprocess.CompletedProcess[str], expected: str) -> None:
    lines = result.stderr.strip().splitlines()
    if result.returncode == 0 or not lines or lines[-1] != expected:
        raise ValueError(
            f"expected {expected!r}, observed exit={result.returncode}: {result.stderr}"
        )


def qualify(tasks: dict) -> None:
    for name, task in tasks.items():
        with tempfile.TemporaryDirectory(prefix="astra-fixture-") as temporary:
            workspace = Path(temporary) / "work"
            prepare(workspace, task)
            baseline = check(workspace, task)
            require_failure(baseline, task["baseline_failure"])
            write_files(workspace, task["reference"])
            positive = check(workspace, task)
            if positive.returncode:
                raise ValueError(f"{name}: reference failed: {positive.stderr}")
            write_files(workspace, task["negative"])
            negative = check(workspace, task)
            require_failure(negative, task["negative_failure"])
            # An import-time crash is not evidence that the behavioral check fired.
            module = next(name for name in task["reference"] if name.endswith(".py"))
            write_files(workspace, {module: "raise RuntimeError('unrelated startup failure')\n"})
            unrelated = check(workspace, task)
            if "RuntimeError: unrelated startup failure" not in unrelated.stderr:
                raise ValueError(f"{name}: unrelated failure control did not execute")
            try:
                require_failure(unrelated, task["negative_failure"])
            except ValueError:
                pass
            else:
                raise ValueError(f"{name}: unrelated startup failure counted as detection")
            print(
                f"{name}: intended baseline/repair failures proved; reference accepted; "
                "unrelated failure refused"
            )
    print("LOCAL FIXTURE QUALIFICATION ONLY; no model or manual-design result")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("prepare", "check", "qualify", "digest"))
    parser.add_argument("--task")
    parser.add_argument("--workspace", type=Path)
    args = parser.parse_args()
    tasks = json.loads((HERE / "tasks.json").read_text())["tasks"]
    if args.operation == "digest":
        for source in sorted(HERE.iterdir()):
            if source.is_file():
                print(hashlib.sha256(source.read_bytes()).hexdigest(), source.name)
        return 0
    if args.operation == "qualify":
        qualify(tasks)
        return 0
    if args.task not in tasks or args.workspace is None:
        parser.error("prepare/check require a valid --task and --workspace")
    if args.operation == "prepare":
        prepare(args.workspace, tasks[args.task])
        print(f"Prepared public inputs only: {args.workspace.resolve()}")
        return 0
    result = check(args.workspace, tasks[args.task])
    print(result.stdout, end="")
    print(result.stderr, end="", file=sys.stderr)
    print(
        "BEHAVIOR PASS; manual rubric still required" if result.returncode == 0 else "BEHAVIOR FAIL"
    )
    return result.returncode


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f"FIXTURE ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
