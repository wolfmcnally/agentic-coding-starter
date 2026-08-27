"""Smoke tests for the example CLI.

The point is to give the build gates something real to run from the
first session. Phase 1 of a derived project should add tests that
exercise actual behavior, not just that the CLI parses arguments.
"""

from __future__ import annotations

import pytest

from example.cli import main


def test_main_hello_default(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["hello"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "Hello, world!\n"
