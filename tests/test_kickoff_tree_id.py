"""Behavioral tests for complete kickoff candidate identity."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
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
    (root / "candidate-partition.yaml").write_text(
        "schema: agentic.candidate-partition.v1\n"
        "active:\n"
        '  - "/candidate-partition.yaml"\n'
        '  - "/.gitignore"\n'
        '  - "/CLAUDE.md"\n'
        '  - "/phase.md"\n'
        '  - "/policy.md"\n'
        '  - "/code.py"\n'
        '  - "/tracked.txt"\n'
        '  - "/script"\n'
        '  - "/projects/**"\n'
        '  - "/policies/**"\n'
        '  - "/bin/**"\n'
        '  - "/lib/**"\n'
        '  - "/plan/**"\n'
        "bookkeeping:\n"
        '  - "/LOG*.md"\n'
        '  - "/EXECUTION_LOG.jsonl"\n'
        '  - "/plan/INDEX.md"\n'
        '  - "/lessons/**"\n'
        '  - "/lessons-archived/**"\n'
        '  - "/user-actions/**"\n'
        '  - "/user-actions-archived/**"\n'
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

    (repository / "escape").unlink()
    _assert_partition_boundary(repository)


def _assert_partition_boundary(root: Path) -> None:
    sys.path.insert(0, str(ROOT / "lib"))
    import yaml
    from agentic_starter.candidate_boundaries import BoundaryError, parse_partition

    declaration = root / "candidate-partition.yaml"
    original = declaration.read_bytes()
    parsed = parse_partition(original)
    assert list(parsed.active) == yaml.safe_load(original)["active"]
    assert parsed.classify("plan/phase-1.md") == "active"
    assert parsed.classify("plan/INDEX.md") == "bookkeeping"
    assert parsed.classify("nested/LOG.md") is None
    assert parsed.classify("lessons/deeper/note.md") == "bookkeeping"
    for body in (
        b"",
        original + b"active:\n",
        original.replace(b'"/code.py"', b'"/**"'),
        original.replace(b'"/code.py"', b'"/a**b"'),
        original.replace(b'"/code.py"', b'"/../escape"'),
        original.replace(b'"/code.py"', b"true"),
        original + b'  - "/candidate-*.yaml"\n',
        original.replace(b'"/code.py"', b'"/CLAUDE.md"'),
    ):
        with pytest.raises(BoundaryError):
            parse_partition(body)
    before = run("--root", str(root), "--product", "--json")
    assert before.returncode == 0, before.stderr
    declaration.write_bytes(original + b"# reviewed declaration edit\n")
    changed = run("--root", str(root), "--product", "--json")
    assert changed.returncode == 0, changed.stderr
    assert json.loads(before.stdout)["candidate_id"] != json.loads(changed.stdout)["candidate_id"]
    declaration.write_bytes(original)

    orphan = root / "unclassified.asset"
    orphan.write_text("new active input\n")
    retained = run("--root", str(root), "--product", "--json")
    assert retained.returncode == 0, retained.stderr
    assert "retained as active" in retained.stderr
    assert "unclassified.asset" in {e["path"] for e in json.loads(retained.stdout)["entries"]}
    subprocess.run(["git", "add", "unclassified.asset"], cwd=root, check=True)
    refused = run("--root", str(root), "--product")
    assert refused.returncode == 2
    assert "unclassified tracked paths" in refused.stderr
    # The working declaration cannot launder a different staged declaration.
    declaration.write_bytes(original.replace(b"active:\n", b'active:\n  - "/unclassified.asset"\n'))
    checker = ROOT / "bin/check-candidate-partition"
    working = subprocess.run([str(checker), "--root", str(root)], capture_output=True, text=True)
    assert working.returncode == 0, working.stderr
    staged = subprocess.run(
        [str(checker), "--root", str(root), "--staged"], capture_output=True, text=True
    )
    assert staged.returncode == 1
    assert "unclassified tracked" in staged.stderr
    # Actually exercise the tracked hook, with all unrelated checks stubbed.
    (root / "bin").mkdir(exist_ok=True)
    (root / "lib/agentic_starter").mkdir(parents=True, exist_ok=True)
    shutil.copy2(checker, root / "bin/check-candidate-partition")
    for name in ("__init__.py", "candidate_boundaries.py"):
        shutil.copy2(ROOT / "lib/agentic_starter" / name, root / "lib/agentic_starter" / name)
    for name in (
        "check-harness-parity",
        "check-toolchain-callers",
        "check-log",
        "test-governance",
    ):
        stub = root / "bin" / name
        stub.write_text("#!/bin/sh\nexit 0\n")
        stub.chmod(0o755)
    hook = subprocess.run(
        ["bash", str(ROOT / ".githooks/pre-commit")],
        cwd=root,
        capture_output=True,
        text=True,
    )
    assert hook.returncode != 0
    assert "unclassified tracked" in hook.stderr
    subprocess.run(["git", "add", "candidate-partition.yaml"], cwd=root, check=True)
    admitted = subprocess.run(
        [str(checker), "--root", str(root), "--staged"], capture_output=True, text=True
    )
    assert admitted.returncode == 0, admitted.stderr
    declaration.unlink()
    missing = run("--root", str(root), "--product")
    assert missing.returncode == 2
    assert "cannot read candidate-partition.yaml" in missing.stderr
