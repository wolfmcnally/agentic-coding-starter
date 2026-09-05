from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))

from agentic_starter import log_blocks  # noqa: E402


def run(
    root: Path, name: str, *arguments: str, stdin: str | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(root / "bin" / name), *arguments],
        cwd=root,
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
    )


def test_append_prefix_chronology_and_bounded_repairs_preserve_bytes(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo"
    (root / "bin").mkdir(parents=True)
    (root / "lib" / "agentic_starter").mkdir(parents=True)
    for name in (
        "check-log",
        "check-log-prefix",
        "check-log-monotonic",
        "log-append",
        "log-relocate",
        "normalize-final-newline",
    ):
        shutil.copy2(ROOT / "bin" / name, root / "bin" / name)
    shutil.copy2(
        ROOT / "lib" / "agentic_starter" / "__init__.py",
        root / "lib" / "agentic_starter",
    )
    shutil.copy2(
        ROOT / "lib" / "agentic_starter" / "log_blocks.py",
        root / "lib" / "agentic_starter",
    )
    shutil.copy2(
        ROOT / "lib/agentic_starter/candidate_boundaries.py",
        root / "lib/agentic_starter",
    )
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
    (root / "LOG.md").write_text(
        "# Activity Log\n\n## 2026-01-01 10:00 — START\n\nLessons:\n\n- None.\n"
    )
    (root / "plan").mkdir()
    (root / "plan" / "INDEX.md").write_text("index\n")
    subprocess.run(["git", "init", "-q", "-b", "master"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "fixture@example.invalid"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Fixture"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True)
    committed = (root / "LOG.md").read_bytes()

    appended = run(
        root,
        "log-append",
        "--root",
        str(root),
        stdin="## 2026-01-01 11:00 — END\n\nLessons:\n\n- One.\n",
    )
    assert appended.returncode == 0, appended.stderr
    assert (root / "LOG.md").read_bytes().startswith(committed)
    assert run(root, "check-log").returncode == 0

    first = log_blocks.parse((root / "LOG.md").read_text()).blocks[-1]
    (root / "LOG.md").write_text(
        (root / "LOG.md").read_text()
        + "\n## 2026-01-01 12:00 — NOTE\n\nLater.\n"
        + "\n## 2026-01-01 11:30 — NOTE\n\nMisplaced.\n"
    )
    parsed = log_blocks.parse((root / "LOG.md").read_text())
    source = parsed.blocks[-1].sha256
    relocated = run(
        root,
        "log-relocate",
        "--root",
        str(root),
        "--block",
        source,
        "--after",
        first.sha256,
    )
    assert relocated.returncode == 0, relocated.stderr
    repaired = (root / "LOG.md").read_bytes()
    assert repaired.startswith(committed)
    repaired_ids = [block.sha256 for block in log_blocks.parse(repaired.decode()).blocks]
    assert source in repaired_ids and first.sha256 in repaired_ids
    assert run(root, "check-log").returncode == 0

    repeated = run(
        root,
        "log-relocate",
        "--root",
        str(root),
        "--block",
        source,
        "--after",
        first.sha256,
    )
    assert repeated.returncode == 1
    assert "no-op" in repeated.stderr

    (root / "LOG.md").write_bytes(repaired + b"\n" + first.render().encode())
    ambiguous = run(
        root,
        "log-relocate",
        "--root",
        str(root),
        "--block",
        first.sha256,
        "--after",
        source,
    )
    assert ambiguous.returncode == 1
    assert "exactly one block" in ambiguous.stderr

    (root / "LOG.md").write_bytes(repaired.replace(b"# Activity Log", b"# Rewritten Log", 1))
    refused = run(root, "check-log-prefix", "--root", str(root))
    assert refused.returncode == 1
    assert "committed bytes are not a prefix" in refused.stderr
    subprocess.run(["git", "add", "LOG.md"], cwd=root, check=True)
    staged_refusal = run(root, "check-log", "--staged")
    assert staged_refusal.returncode == 1
    assert "committed bytes are not a prefix" in staged_refusal.stderr

    (root / "LOG.md").write_bytes(repaired)
    (root / "plan" / "INDEX.md").write_bytes(b"index\n\n")
    normalized = run(
        root,
        "normalize-final-newline",
        "--root",
        str(root),
        "--path",
        "plan/INDEX.md",
    )
    assert normalized.returncode == 0, normalized.stderr
    assert (root / "plan" / "INDEX.md").read_bytes() == b"index\n"

    lesson = root / "lessons" / "one.md"
    lesson.parent.mkdir()
    lesson.write_text("lesson\n\n")
    refused = run(root, "normalize-final-newline", "--root", str(root), "--path", "lessons/one.md")
    assert refused.returncode == 2
    assert "outside the admitted" in refused.stderr
    assert lesson.read_text() == "lesson\n\n"
