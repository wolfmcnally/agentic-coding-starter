"""Behavioral tests for deterministic cross-harness parity enforcement."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "bin" / "check-harness-parity"


def run(root: Path) -> subprocess.CompletedProcess[str]:
    checker = root / "bin" / "check-harness-parity"
    return subprocess.run(
        [str(checker)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


def test_repository_is_in_parity() -> None:
    result = run(ROOT)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == "HARNESS PARITY OK\n"
