"""Behavioral tests for complete kickoff candidate identity."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TREE_ID = ROOT / "bin" / "kickoff-tree-id"


def run(*arguments: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(TREE_ID), *arguments],
        cwd=cwd or ROOT,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-b", "master"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "fixture@example.invalid"],
        cwd=root,
        check=True,
    )
    subprocess.run(["git", "config", "user.name", "Fixture"], cwd=root, check=True)
    (root / ".gitignore").write_text("ignored.txt\n.cache/\n")
    (root / "tracked.txt").write_text("tracked\n")
    (root / "script").write_text("#!/bin/sh\n")
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-m", "fixture"], cwd=root, check=True, capture_output=True)
    return root


def manifest(root: Path, *, cwd: Path | None = None) -> dict[str, object]:
    result = run("--root", str(root), "--json", cwd=cwd)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def candidate_id(root: Path) -> str:
    return str(manifest(root)["candidate_id"])


def test_identity_is_cwd_independent_and_manifest_is_ordered(
    repository: Path, tmp_path: Path
) -> None:
    first = manifest(repository)
    second = manifest(repository, cwd=tmp_path)

    assert first == second
    paths = [entry["path"] for entry in first["entries"]]
    assert paths == sorted(paths, key=os.fsencode)


def test_tracked_staged_unstaged_and_untracked_changes_affect_identity(
    repository: Path,
) -> None:
    original = candidate_id(repository)

    (repository / "tracked.txt").write_text("unstaged\n")
    unstaged = candidate_id(repository)
    subprocess.run(["git", "add", "tracked.txt"], cwd=repository, check=True)
    staged = candidate_id(repository)
    (repository / "new.txt").write_text("untracked\n")
    untracked = candidate_id(repository)

    assert original != unstaged
    assert staged == unstaged
    assert untracked != staged


def test_symlink_escape_fails_closed(repository: Path) -> None:
    (repository / "escape").symlink_to("../outside")

    result = run("--root", str(repository))

    assert result.returncode == 2
    assert "escapes repository" in result.stderr
