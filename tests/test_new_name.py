"""Behavioral tests for bin/new-name (ledger slug generator)."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NEW_NAME = ROOT / "bin" / "new-name"

FILLERS = {
    "the",
    "a",
    "an",
    "of",
    "and",
    "or",
    "for",
    "in",
    "on",
    "as",
    "to",
    "with",
    "by",
    "at",
    "is",
    "vs",
    "into",
    "from",
    "onto",
    "via",
}


def run(*arguments: str, root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(NEW_NAME), "--root", str(root), *arguments],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def test_avoids_collisions_across_all_ledger_dirs(tmp_path: Path) -> None:
    for dir_name in (
        "lessons",
        "lessons-archived",
        "user-actions",
        "user-actions-archived",
    ):
        (tmp_path / dir_name).mkdir()
    # Seed a collision in each directory, then confirm generated slugs never
    # match any seeded basename over repeated runs.
    seeded = set()
    for index, dir_name in enumerate(
        ("lessons", "lessons-archived", "user-actions", "user-actions-archived")
    ):
        slug = f"seeded-slug{index}"
        (tmp_path / dir_name / f"{slug}.md").write_text("seed")
        seeded.add(slug)
    for _ in range(5):
        result = run(root=tmp_path)
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() not in seeded
