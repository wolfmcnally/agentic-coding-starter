"""Command-line entry point for the example package.

This is a minimal-but-runnable CLI shell. It exposes one subcommand,
``hello``, that prints a greeting. Phase 1 of any project derived from
this template is meant to flesh this out (or replace it) with real
functionality.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from example import __version__


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level argument parser."""
    parser = argparse.ArgumentParser(
        prog="example",
        description=(
            "Example CLI shipped with the Agentic Coding Starter Template. "
            "Replace with your real CLI as Phase 1 lands."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"example {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", required=False)

    hello = subparsers.add_parser(
        "hello",
        help="Print a friendly greeting.",
    )
    hello.add_argument(
        "name",
        nargs="?",
        default="world",
        help="Who to greet. Defaults to 'world'.",
    )

    return parser


def cmd_hello(name: str) -> int:
    """Execute the ``hello`` subcommand."""
    print(f"Hello, {name}!")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Dispatch the parsed arguments to the matching subcommand."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "hello":
        return cmd_hello(args.name)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
