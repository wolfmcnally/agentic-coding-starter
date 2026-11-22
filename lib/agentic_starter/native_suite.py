"""A deliverable's own test suite, in its own language, as a supervised lane.

A project whose product is not Python declares that suite by supplying one executable,
``bin/test-native``, which runs the suite and forwards any arguments as a selection. The
test entry point then runs it here, after the parallel pytest run and never inside one
of its workers: such a runner usually schedules its own worker pool, and nesting two
pools multiplies workers. It gets what pytest gets from ``test_runner``: no elapsed
limit, process-group cleanup and the incomplete status with its reason.

Fixture repositories the suite creates never sign, exactly as the pytest fixtures do
(``tests/conftest.py``): the operator's signing setup is not under test.
"""

from __future__ import annotations

import os
import sys
from collections.abc import MutableMapping, Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lib"))

from agentic_starter import test_runner  # noqa: E402

RUNNER = "bin/test-native"


def isolate_fixture_git_signing(environment: MutableMapping[str, str]) -> None:
    """Append commit and tag signing overrides after any the caller already supplied."""
    count = int(environment.get("GIT_CONFIG_COUNT", "0") or "0")
    supplied = {environment.get(f"GIT_CONFIG_KEY_{index}") for index in range(count)}
    for key in ("commit.gpgsign", "tag.gpgsign"):
        if key in supplied:
            continue
        environment[f"GIT_CONFIG_KEY_{count}"] = key
        environment[f"GIT_CONFIG_VALUE_{count}"] = "false"
        count += 1
    environment["GIT_CONFIG_COUNT"] = str(count)


def main(arguments: Sequence[str], root: Path = ROOT) -> int:
    runner = root / RUNNER
    if not os.access(runner, os.X_OK):
        print(f"TEST ERROR no native suite is declared: {RUNNER} is absent", file=sys.stderr)
        return 2
    try:
        isolate_fixture_git_signing(os.environ)
        result = test_runner.run_command([str(runner), *arguments], cwd=root)
    except (OSError, ValueError) as exc:
        print(f"TEST INCOMPLETE: native suite supervisor could not run: {exc}", file=sys.stderr)
        return test_runner.INCOMPLETE
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
