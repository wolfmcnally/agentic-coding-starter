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
    (root / "policies").mkdir()
    (root / "policies" / "orchestration-evidence.md").write_text(
        "```yaml\n"
        "# kickoff-evidence drift partitions\n"
        "inert:\n"
        "  - LOG*.md\n"
        "  - EXECUTION_LOG.jsonl\n"
        "  - plan/INDEX.md\n"
        "  - lessons/\n"
        "  - lessons-archived/\n"
        "  - user-actions/\n"
        "  - user-actions-archived/\n"
        "```\n"
    )
    (root / "LOG.md").write_text("# Log\n")
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

    product_before = run("--root", str(repository), "--product", "--json")
    assert product_before.returncode == 0, product_before.stderr
    (repository / "LOG.md").write_text("# Log\n\nappend\n")
    assert candidate_id(repository) != untracked
    product_after = run("--root", str(repository), "--product", "--json")
    assert product_after.returncode == 0, product_after.stderr
    assert (
        json.loads(product_before.stdout)["candidate_id"]
        == json.loads(product_after.stdout)["candidate_id"]
    )

    (repository / "escape").symlink_to("../outside")

    result = run("--root", str(repository))

    assert result.returncode == 2
    assert "escapes repository" in result.stderr
