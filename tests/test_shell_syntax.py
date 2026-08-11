"""Behavioral tests for bin/check-shell-syntax."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "bin" / "check-shell-syntax"


def run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(CHECKER), "--root", str(root)],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def write_script(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)
    path.chmod(0o755)


def test_clean_tree_passes(tmp_path: Path) -> None:
    write_script(tmp_path / "bin" / "ok", "#!/usr/bin/env bash\necho hello\n")
    write_script(tmp_path / ".githooks" / "pre-commit", "#!/bin/sh\nexit 0\n")
    result = run(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == ""


def test_syntax_error_fails_with_named_file(tmp_path: Path) -> None:
    write_script(tmp_path / "bin" / "broken", "#!/usr/bin/env bash\nif [ -f x ]; then\n")
    result = run(tmp_path)
    assert result.returncode == 1
    assert "ERROR: bin/broken" in result.stdout


def test_hook_scripts_are_scanned(tmp_path: Path) -> None:
    write_script(tmp_path / ".githooks" / "pre-push", "#!/usr/bin/env bash\nwhile true\n")
    result = run(tmp_path)
    assert result.returncode == 1
    assert ".githooks/pre-push" in result.stdout


def test_non_shell_scripts_are_skipped(tmp_path: Path) -> None:
    write_script(
        tmp_path / "bin" / "tool",
        "#!/usr/bin/env python3\nif this were bash it would not parse(\n",
    )
    result = run(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr


def test_real_repo_is_clean() -> None:
    result = run(ROOT)
    assert result.returncode == 0, result.stdout + result.stderr
