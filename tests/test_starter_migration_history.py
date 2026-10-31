"""Starter-only historical-corpus proof; never copied to a new project."""

import json
import subprocess
from pathlib import Path

from test_multioperator import ROOT, assert_rehearsal_contract


def test_actual_starter_rehearsal_preserves_source_and_history(tmp_path: Path) -> None:
    """Starter-only regression against its actual retained committed corpus."""
    source = tmp_path / "faithful-starter"
    # Old-format input comes from our Git provenance; it is not a live fallback.
    manifest = ROOT / "collaboration/manifest.json"
    commit = json.loads(manifest.read_text())["source_commit"]
    archive = subprocess.check_output(["git", "archive", commit], cwd=ROOT)
    source.mkdir()
    import io
    import tarfile

    with tarfile.open(fileobj=io.BytesIO(archive)) as files:
        files.extractall(source, filter="data")
    subprocess.run(["git", "init", "-q", "-b", "master", str(source)], check=True)
    subprocess.run(
        ["git", "config", "user.email", "fixture@example.invalid"],
        cwd=source,
        check=True,
    )
    subprocess.run(["git", "config", "user.name", "Fixture"], cwd=source, check=True)
    paths = (
        subprocess.check_output(
            ["git", "ls-files", "--others", "--exclude-standard", "-z"], cwd=source
        )
        .decode()
        .split("\0")
    )
    subprocess.run(["git", "add", "--", *[p for p in paths if p]], cwd=source, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "Faithful pre-transition fixture"],
        cwd=source,
        check=True,
    )
    assert (source / "LOG.md").read_bytes() == subprocess.check_output(
        ["git", "show", commit + ":LOG.md"], cwd=ROOT
    )
    assert_rehearsal_contract(tmp_path, source, {"1": "starter-template-adoption"})
