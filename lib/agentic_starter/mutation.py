"""Mutation survey for the Python profile: which planted faults do the tests miss?

The interface is universal and the tool is not. This module is the Python
implementation behind ``bin/mutate``; another language's wrapper drives its own
tool and prints the same document. The survey never gates: survivors are work
items for whoever wrote or reviews the change.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from collections.abc import Sequence
from datetime import date
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agentic_starter import test_governance  # noqa: E402

_HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


TOOL = "cosmic-ray"


class MutationError(RuntimeError):
    """The survey could not be taken; never reported as unmeasured."""


def _git(root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments], cwd=root, text=True, capture_output=True, check=False
    )
    if result.returncode != 0:
        raise MutationError(f"git {' '.join(arguments)} failed: {result.stderr.strip()}")
    return result.stdout


def _in_scope(path: str, patterns: Sequence[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def _targets(
    root: Path, patterns: Sequence[str], changed_from: str | None
) -> dict[str, list[str] | None]:
    """Each file to mutate, with the line ranges to keep or None for the whole file."""
    present = [
        item
        for item in _git(
            root, "ls-files", "-z", "--cached", "--others", "--exclude-standard"
        ).split("\0")
        if item
    ]
    if changed_from is None:
        return {
            path: None for path in present if _in_scope(path, patterns) and (root / path).is_file()
        }
    _git(root, "rev-parse", "--verify", f"{changed_from}^{{commit}}")
    untracked = {
        item
        for item in _git(root, "ls-files", "-z", "--others", "--exclude-standard").split("\0")
        if item
    }
    targets: dict[str, list[str] | None] = {
        path: None for path in sorted(untracked) if _in_scope(path, patterns)
    }
    changed = _git(root, "diff", "--name-only", "--no-renames", "-z", changed_from, "--")
    for path in sorted(item for item in changed.split("\0") if item):
        if not _in_scope(path, patterns) or not (root / path).is_file():
            continue
        ranges = []
        for line in _git(
            root, "diff", "-U0", "--no-renames", changed_from, "--", path
        ).splitlines():
            match = _HUNK.match(line)
            if match and match.group(2) != "0":
                start = int(match.group(1))
                ranges.append(f"{start}-{start + int(match.group(2) or 1) - 1}")
        if ranges:
            targets[path] = ranges
    return targets


def _selectors(families: list[dict[str, Any]], path: str) -> list[str]:
    """The tests that guard a file: its families', or the whole estate when none claims it."""
    owners = [
        family
        for family in families
        if _in_scope(path, [*family.get("covers", []), *family.get("source_paths", [])])
    ]
    return test_governance.pytest_selectors(owners or families)


def _digests(root: Path, paths: Sequence[str]) -> dict[str, str]:
    return {path: hashlib.sha256((root / path).read_bytes()).hexdigest() for path in paths}


def _copy(root: Path, destination: Path) -> None:
    """A disposable copy of the candidate tree, so no fault is ever planted in the live one."""
    listed = _git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    for item in listed.split("\0"):
        source = root / item
        if not item or not (source.is_file() or source.is_symlink()):
            continue
        target = destination / item
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target, follow_symlinks=False)
    # Proofs that ask git about their own repository need one to ask.
    for arguments in (
        ("init", "-q", "-b", "survey"),
        ("add", "-A"),
        (
            "-c",
            "user.name=survey",
            "-c",
            "user.email=survey@example.invalid",
            "commit",
            "-qm",
            "c",
        ),
    ):
        _git(destination, *arguments)


def _bounded(command: Sequence[str], cwd: Path, deadline: float) -> tuple[int | None, str]:
    """Run in its own process group until the deadline; None means the budget ran out."""
    process = subprocess.Popen(
        list(command),
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    try:
        output, _ = process.communicate(timeout=max(deadline - time.monotonic(), 0.0))
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        output, _ = process.communicate()
        return None, output
    return process.returncode, output


def _survey_file(
    work: Path,
    scratch: Path,
    path: str,
    ranges: list[str] | None,
    selectors: Sequence[str],
    deadline: float,
) -> dict[str, Any]:
    tally: dict[str, Any] = {"killed": 0, "survived": 0, "timed_out": 0, "not_run": 0}
    tally["survivors"] = []
    tool = [sys.executable, "-m"]
    test_command = shlex.join(["./bin/test", "-q", "-x", "-p", "no:cacheprovider", *selectors])
    started = time.monotonic()
    status, output = _bounded(shlex.split(test_command), work, deadline)
    if status is None:
        tally["not_run"] = None
        return tally
    if status != 0:
        raise MutationError(f"tests fail before any fault is planted for {path}:\n{output[-2000:]}")
    per_mutant = max(10.0, 3 * (time.monotonic() - started))
    name = hashlib.sha256(path.encode()).hexdigest()[:16]
    config = scratch / f"{name}.toml"
    session = scratch / f"{name}.sqlite"
    lines = [
        "[cosmic-ray]",
        f"module-path = {json.dumps(path)}",
        f"timeout = {per_mutant:.1f}",
        "excluded-modules = []",
        f"test-command = {json.dumps(test_command)}",
        "",
        "[cosmic-ray.distributor]",
        'name = "local"',
    ]
    if ranges is not None:
        lines += [
            "",
            "[cosmic-ray.filters.line-filter.lines]",
            f"{json.dumps(path)} = {json.dumps(ranges)}",
        ]
    config.write_text("\n".join(lines) + "\n")
    steps = [[*tool, "cosmic_ray.cli", "init", str(config), str(session)]]
    if ranges is not None:
        steps.append(
            [
                *tool,
                "cosmic_ray.tools.filters.line_filter",
                "--config",
                str(config),
                str(session),
            ]
        )
    for step in steps:
        status, output = _bounded(step, work, deadline)
        if status is None:
            tally["not_run"] = None
            return tally
        if status != 0:
            raise MutationError(f"mutation tool failed for {path}:\n{output[-2000:]}")
    status, output = _bounded(
        [*tool, "cosmic_ray.cli", "exec", str(config), str(session)], work, deadline
    )
    if status not in (0, None):
        raise MutationError(f"mutation tool failed for {path}:\n{output[-2000:]}")
    dumped = subprocess.run(
        [*tool, "cosmic_ray.cli", "dump", str(session)],
        cwd=work,
        text=True,
        capture_output=True,
        check=False,
    )
    if dumped.returncode != 0:
        raise MutationError(f"mutation results unreadable for {path}:\n{dumped.stderr[-2000:]}")
    for row in dumped.stdout.splitlines():
        if not row.strip():
            continue
        item, result = json.loads(row)
        if result is None:
            tally["not_run"] += 1
            continue
        if result["worker_outcome"] == "skipped":
            continue
        outcome = result.get("test_outcome")
        if result["worker_outcome"] == "normal" and outcome == "survived":
            tally["survived"] += 1
            for mutation in item["mutations"]:
                tally["survivors"].append(
                    {
                        "path": mutation["module_path"],
                        "line": mutation["start_pos"][0],
                        "change": f"{mutation['operator_name']} #{mutation['occurrence']}",
                    }
                )
        elif result["worker_outcome"] == "normal" and outcome in (
            "killed",
            "incompetent",
        ):
            tally["killed"] += 1
        else:
            tally["timed_out"] += 1
    return tally


def survey(
    root: Path,
    *,
    changed_from: str | None,
    budget_seconds: float | None = None,
    only: Sequence[str] = (),
) -> dict[str, Any]:
    manifest = test_governance.load_yaml(root / "tests/proof-estate.yaml")
    errors = test_governance.mutation_errors(manifest)
    if errors:
        raise MutationError("mutation declaration invalid:\n- " + "\n- ".join(errors))
    declared = manifest["mutation"]
    scope = {"changed_from": changed_from} if changed_from else {"all": True}
    if declared["tool"] is None:
        return {
            "state": "unmeasured",
            "tool": None,
            "scope": scope,
            "reason": declared["reason"],
        }
    if declared["tool"] != TOOL:
        raise MutationError(f"this wrapper drives {TOOL}, not {declared['tool']}")
    families = manifest.get("families")
    if not isinstance(families, list) or not families:
        raise MutationError("manifest families must be a nonempty list")
    targets = _targets(root, declared["paths"], changed_from)
    if only:
        targets = {path: lines for path, lines in targets.items() if _in_scope(path, only)}
    before = _digests(root, list(targets))
    totals = {"killed": 0, "survived": 0, "timed_out": 0, "not_run": 0}
    survivors: list[dict[str, Any]] = []
    unfinished: list[str] = []
    budget = float(declared["budget_seconds"] if budget_seconds is None else budget_seconds)
    deadline = time.monotonic() + budget
    with tempfile.TemporaryDirectory(prefix="mutation-survey-") as temporary:
        work = Path(temporary) / "repo"
        scratch = Path(temporary) / "sessions"
        scratch.mkdir()
        if targets:
            _copy(root, work)
        # Changed lines first: they are the cheap, bounded part of a scoped survey.
        for path, ranges in sorted(targets.items(), key=lambda item: item[1] is None):
            if time.monotonic() >= deadline:
                unfinished.append(path)
                continue
            tally = _survey_file(work, scratch, path, ranges, _selectors(families, path), deadline)
            if tally["not_run"] is None:
                unfinished.append(path)
                continue
            if tally["not_run"]:
                unfinished.append(path)
            for key in totals:
                totals[key] += tally[key]
            survivors.extend(tally["survivors"])
    if _digests(root, list(targets)) != before:
        raise MutationError("a surveyed file changed in the live tree during the survey")
    return {
        "state": "partial" if unfinished else "measured",
        "tool": declared["tool"],
        "scope": scope,
        "files": sorted(targets),
        "unfinished": sorted(unfinished),
        "generated": totals["killed"]
        + totals["survived"]
        + totals["timed_out"]
        + totals["not_run"],
        **totals,
        "survivors": sorted(survivors, key=lambda row: (row["path"], row["line"], row["change"])),
        "budget_seconds": budget,
        "measured_on": date.today().isoformat(),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mutate", description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--changed-from", metavar="REV")
    scope.add_argument("--all", action="store_true")
    parser.add_argument(
        "--budget-seconds", type=float, help="override the declared budget for this run"
    )
    parser.add_argument(
        "--path",
        action="append",
        default=[],
        metavar="PATTERN",
        help="survey only declared paths matching this pattern (repeatable)",
    )
    arguments = parser.parse_args(argv)
    if arguments.budget_seconds is not None and arguments.budget_seconds <= 0:
        parser.error("--budget-seconds must be positive")
    try:
        outcome = survey(
            arguments.root.resolve(),
            changed_from=arguments.changed_from,
            budget_seconds=arguments.budget_seconds,
            only=arguments.path,
        )
    except (MutationError, test_governance.GovernanceError) as exc:
        print(f"MUTATE ERROR {exc}", file=sys.stderr)
        return 1
    print(json.dumps(outcome, indent=2, sort_keys=True))
    print(f"MUTATE {outcome['state'].upper()}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
