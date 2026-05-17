"""Smoke tests for the example CLI.

The point is to give the build gates something real to run from the
first session. Phase 1 of a derived project should add tests that
exercise actual behavior, not just that the CLI parses arguments.
"""

from __future__ import annotations

import pytest

from example import __version__
from example.cli import build_parser, cmd_hello, main


def test_version_is_set() -> None:
    assert __version__ == "0.1.0"


def test_parser_has_hello_subcommand() -> None:
    parser = build_parser()
    args = parser.parse_args(["hello"])
    assert args.command == "hello"
    assert args.name == "world"


def test_parser_hello_with_name() -> None:
    parser = build_parser()
    args = parser.parse_args(["hello", "Ada"])
    assert args.command == "hello"
    assert args.name == "Ada"


def test_cmd_hello_prints_greeting(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = cmd_hello("there")
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "Hello, there!\n"


def test_main_with_no_args_prints_help(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main([])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "usage:" in captured.out.lower()


def test_main_hello_default(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["hello"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "Hello, world!\n"


def test_main_version_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert __version__ in captured.out
