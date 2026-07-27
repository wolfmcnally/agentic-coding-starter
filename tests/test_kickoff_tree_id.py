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


def test_ignored_runtime_state_does_not_affect_identity(repository: Path) -> None:
    original = candidate_id(repository)

    (repository / "ignored.txt").write_text("ignored\n")
    (repository / ".cache").mkdir()
    (repository / ".cache" / "state").write_text("runtime\n")

    assert candidate_id(repository) == original


def test_deletion_mode_and_symlink_target_affect_identity(repository: Path) -> None:
    original = candidate_id(repository)

    (repository / "tracked.txt").unlink()
    deleted = candidate_id(repository)
    (repository / "tracked.txt").write_text("tracked\n")
    (repository / "script").chmod(0o755)
    executable = candidate_id(repository)
    (repository / "link").symlink_to("tracked.txt")
    linked = candidate_id(repository)
    (repository / "link").unlink()
    (repository / "link").symlink_to("script")
    retargeted = candidate_id(repository)

    assert len({original, deleted, executable, linked, retargeted}) == 5


def test_manifest_never_contains_file_contents(repository: Path) -> None:
    secret = "not-for-manifest"
    (repository / "new.txt").write_text(secret)

    result = run("--root", str(repository), "--json")

    assert result.returncode == 0, result.stderr
    assert secret not in result.stdout


def test_symlink_escape_fails_closed(repository: Path) -> None:
    (repository / "escape").symlink_to("../outside")

    result = run("--root", str(repository))

    assert result.returncode == 2
    assert "escapes repository" in result.stderr


def test_submodule_checkout_affects_identity_and_dirty_submodule_fails_closed(
    repository: Path, tmp_path: Path
) -> None:
    source = tmp_path / "submodule-source"
    source.mkdir()
    subprocess.run(["git", "init", "-b", "master"], cwd=source, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "fixture@example.invalid"],
        cwd=source,
        check=True,
    )
    subprocess.run(["git", "config", "user.name", "Fixture"], cwd=source, check=True)
    (source / "value.txt").write_text("one\n")
    subprocess.run(["git", "add", "."], cwd=source, check=True)
    subprocess.run(["git", "commit", "-m", "one"], cwd=source, check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-c",
            "protocol.file.allow=always",
            "submodule",
            "add",
            str(source),
            "dependency",
        ],
        cwd=repository,
        check=True,
        capture_output=True,
    )
    original = candidate_id(repository)

    (source / "value.txt").write_text("two\n")
    subprocess.run(["git", "add", "."], cwd=source, check=True)
    subprocess.run(["git", "commit", "-m", "two"], cwd=source, check=True, capture_output=True)
    new_head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=source,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    subprocess.run(
        ["git", "-c", "protocol.file.allow=always", "fetch", "origin"],
        cwd=repository / "dependency",
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "checkout", new_head],
        cwd=repository / "dependency",
        check=True,
        capture_output=True,
    )

    assert candidate_id(repository) != original

    (repository / "dependency" / "value.txt").write_text("dirty\n")
    dirty = run("--root", str(repository))
    assert dirty.returncode == 2
    assert "dirty submodule" in dirty.stderr
