"""Behavioral tests for the release worktree check: one clean checkout or a refusal."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "bin" / "check-release-worktrees"
IDENTITY = {
    "GIT_AUTHOR_NAME": "Fixture",
    "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
    "GIT_COMMITTER_NAME": "Fixture",
    "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
}


def _git(directory: Path, *arguments: str) -> None:
    subprocess.run(
        ["git", "-C", str(directory), *arguments],
        check=True,
        capture_output=True,
        env={**os.environ, **IDENTITY},
    )


@pytest.fixture
def release_repo(tmp_path: Path) -> Path:
    root = tmp_path / "release"
    root.mkdir()
    _git(root, "init", "-q", "-b", "master")
    (root / "tracked.txt").write_text("delivered\n", encoding="utf-8")
    _git(root, "add", "tracked.txt")
    _git(root, "commit", "-q", "-m", "Initial")
    return root.resolve()


def _run(root: Path, **environment: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(SCRIPT), "--root", str(root)],
        env={**os.environ, **IDENTITY, **environment},
        text=True,
        capture_output=True,
        check=False,
    )


def _snapshot(root: Path) -> tuple[str, str]:
    """The repository state the check must leave exactly as it found it."""
    listing = subprocess.run(
        ["git", "-C", str(root), "worktree", "list", "--porcelain"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    status = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return listing, status


def test_one_clean_release_checkout_passes(release_repo: Path) -> None:
    result = _run(release_repo)

    assert result.returncode == 0 and "PASS one registered worktree, clean" in result.stdout, (
        "SOLE CLEAN RELEASE CHECKOUT REFUSED: " + result.stdout + result.stderr
    )


@pytest.mark.parametrize("kind", ["tracked", "staged", "untracked"])
def test_any_change_in_the_release_checkout_refuses(release_repo: Path, kind: str) -> None:
    if kind == "tracked":
        (release_repo / "tracked.txt").write_text("edited\n", encoding="utf-8")
    elif kind == "staged":
        (release_repo / "staged.txt").write_text("staged\n", encoding="utf-8")
        _git(release_repo, "add", "staged.txt")
    else:
        (release_repo / "nested").mkdir()
        (release_repo / "nested" / "untracked.txt").write_text("stray\n", encoding="utf-8")
    before = _snapshot(release_repo)

    result = _run(release_repo)

    assert result.returncode == 1 and "the release checkout has 1 changed" in result.stderr, (
        "DIRTY RELEASE CHECKOUT PASSED: " + result.stdout + result.stderr
    )
    assert _snapshot(release_repo) == before, "RELEASE CHECK CHANGED THE CHECKOUT"


@pytest.mark.parametrize("state", ["clean", "dirty"])
def test_an_extra_registered_worktree_refuses_clean_or_dirty(
    release_repo: Path, tmp_path: Path, state: str
) -> None:
    extra = tmp_path / "extra lane"
    _git(release_repo, "worktree", "add", "-q", "-b", "lane", str(extra))
    if state == "dirty":
        (extra / "unfinished.txt").write_text("unique work\n", encoding="utf-8")
    before = _snapshot(release_repo)

    result = _run(release_repo)

    expected = "clean" if state == "clean" else "dirty, 1 changed or untracked path(s)"
    assert result.returncode == 1 and f"{str(extra.resolve())!r}: {expected}" in result.stderr, (
        "EXTRA WORKTREE PASSED OR ITS STATE WAS MISREPORTED: " + result.stdout + result.stderr
    )
    assert _snapshot(release_repo) == before and extra.is_dir(), (
        "RELEASE CHECK CHANGED OR REMOVED A WORKTREE"
    )


def test_a_worktree_path_with_a_space_and_a_newline_is_read_exactly(
    release_repo: Path, tmp_path: Path
) -> None:
    extra = tmp_path / "odd name\nworktree /elsewhere"
    _git(release_repo, "worktree", "add", "-q", "-b", "lane", str(extra))

    result = _run(release_repo)

    assert result.returncode == 1 and repr(str(extra.resolve())) in result.stderr, (
        "WORKTREE PATH WAS NOT PARSED EXACTLY: " + result.stdout + result.stderr
    )
    assert result.stderr.count("extra registered worktree") == 1, (
        "WORKTREE PATH WAS NOT PARSED EXACTLY: " + result.stderr
    )


@pytest.mark.parametrize("state", ["missing", "locked"])
def test_an_unusable_extra_registration_refuses(
    release_repo: Path, tmp_path: Path, state: str
) -> None:
    extra = tmp_path / "extra"
    _git(release_repo, "worktree", "add", "-q", "-b", "lane", str(extra))
    if state == "missing":
        shutil.rmtree(extra)
        expected = "prunable"
    else:
        _git(release_repo, "worktree", "lock", "--reason", "held by its owner", str(extra))
        expected = "locked (held by its owner)"

    result = _run(release_repo)

    assert result.returncode == 1 and f": {expected}" in result.stderr, (
        "UNUSABLE REGISTRATION PASSED OR WAS MISREPORTED: " + result.stdout + result.stderr
    )
    registered = subprocess.run(
        ["git", "-C", str(release_repo), "worktree", "list", "--porcelain"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert f"worktree {extra.resolve()}\n" in registered, "RELEASE CHECK PRUNED A REGISTRATION"


def test_a_linked_worktree_is_not_a_release_checkout(release_repo: Path, tmp_path: Path) -> None:
    linked = tmp_path / "linked"
    _git(release_repo, "worktree", "add", "-q", "-b", "lane", str(linked))

    result = _run(linked.resolve())

    assert result.returncode == 1 and f"{str(release_repo)!r}: clean" in result.stderr, (
        "RELEASE FROM A LINKED WORKTREE PASSED: " + result.stdout + result.stderr
    )


@pytest.mark.parametrize("failing", ["worktree", "status"])
def test_a_failed_git_command_is_an_error_and_never_a_pass(
    release_repo: Path, tmp_path: Path, failing: str
) -> None:
    real = shutil.which("git")
    assert real is not None
    stand_in = tmp_path / "stand-in"
    stand_in.mkdir()
    (stand_in / "git").write_text(
        "#!/usr/bin/env bash\n"
        f'for argument in "$@"; do [[ "$argument" == "{failing}" ]] && exit 9; done\n'
        f'exec "{real}" "$@"\n',
        encoding="utf-8",
    )
    (stand_in / "git").chmod(0o755)

    result = _run(release_repo, PATH=f"{stand_in}{os.pathsep}{os.environ['PATH']}")

    assert result.returncode == 2 and "CHECK-RELEASE-WORKTREES ERROR" in result.stderr, (
        "FAILED GIT COMMAND READ AS A CLEAN RESULT: " + result.stdout + result.stderr
    )


@pytest.mark.parametrize("fields", ["none", "no-branch-or-detached", "both"])
def test_a_record_without_its_identity_fields_is_refused(
    release_repo: Path, tmp_path: Path, fields: str
) -> None:
    real = shutil.which("git")
    assert real is not None
    record = {
        "none": "",
        "no-branch-or-detached": "HEAD " + "a" * 40 + "\\0",
        "both": "HEAD " + "a" * 40 + "\\0branch refs/heads/master\\0detached\\0",
    }[fields]
    stand_in = tmp_path / "stand-in"
    stand_in.mkdir()
    (stand_in / "git").write_text(
        "#!/usr/bin/env bash\n"
        'for argument in "$@"; do\n'
        '  if [[ "$argument" == "worktree" ]]; then\n'
        f"    printf 'worktree %s\\0{record}\\0' '{release_repo}'\n"
        "    exit 0\n"
        "  fi\n"
        "done\n"
        f'exec "{real}" "$@"\n',
        encoding="utf-8",
    )
    (stand_in / "git").chmod(0o755)

    result = _run(release_repo, PATH=f"{stand_in}{os.pathsep}{os.environ['PATH']}")

    assert result.returncode == 1 and "could not be parsed" in result.stderr, (
        "RECORD WITHOUT IDENTITY FIELDS PASSED: " + result.stdout + result.stderr
    )


def test_a_directory_below_the_checkout_top_is_not_a_release_checkout(release_repo: Path) -> None:
    (release_repo / "below").mkdir()

    result = _run(release_repo / "below")

    assert result.returncode == 1 and "is not the top of a checkout" in result.stderr, (
        "DIRECTORY BELOW THE CHECKOUT TOP PASSED: " + result.stdout + result.stderr
    )
