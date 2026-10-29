"""Retained shared normalization boundary after flat-log tool retirement."""

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_shared_normalization_survives_record_migration(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "plan").mkdir(parents=True)
    (root / "EXECUTION_LOG.jsonl").write_text("{}\n\n")
    context = root / "plan/INDEX.md"
    context.write_bytes(b"Active plan context\n\n")
    # A declaration alone cannot admit a path outside the closed repair set.
    (root / "candidate-partition.yaml").write_text(
        "schema: agentic.candidate-partition.v1\nactive:\n"
        '  - "/candidate-partition.yaml"\n'
        'bookkeeping:\n  - "/EXECUTION_LOG.jsonl"\n  - "/plan/INDEX.md"\n'
    )
    subprocess.run(["git", "init", "-b", "master", str(root)], check=True, capture_output=True)
    normalizer = ROOT / "bin/normalize-final-newline"
    passed = subprocess.run(
        [str(normalizer), "--root", str(root), "--path", "EXECUTION_LOG.jsonl"], capture_output=True
    )
    assert passed.returncode == 0 and (root / "EXECUTION_LOG.jsonl").read_bytes() == b"{}\n", (
        "SHARED NORMALIZER LOST EXECUTION LOG REPAIR"
    )
    denied = subprocess.run(
        [str(normalizer), "--root", str(root), "--path", "plan/INDEX.md"], capture_output=True
    )
    assert denied.returncode == 2 and b"outside the admitted" in denied.stderr, (
        "SHARED NORMALIZER ADMITTED ACTIVE CONTEXT"
    )
    assert context.read_bytes() == b"Active plan context\n\n", (
        "SHARED NORMALIZER MUTATED REFUSED CONTEXT"
    )
