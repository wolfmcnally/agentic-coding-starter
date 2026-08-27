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


def test_syntax_error_fails_with_named_file(tmp_path: Path) -> None:
    write_script(tmp_path / "bin" / "broken", "#!/usr/bin/env bash\nif [ -f x ]; then\n")
    result = run(tmp_path)
    assert result.returncode == 1
    assert "ERROR: bin/broken" in result.stdout
