"""Behavioral tests for the treatise editorial-record tool (policies/treatise.md)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TREATISE = ROOT / "bin" / "treatise"

PLAIN_BRIEF = """\
---
title: "An ordinary brief"
date: 2026-08-01
status: implemented
scope: A brief that is not a treatise.
---

Body.
"""

TREATISE_BRIEF = """\
---
title: "A treatise"
date: 2026-08-01
status: implemented
scope: A brief that is a treatise.
treatise:
  updated: 2026-08-01
  purpose: Explain the thing to someone who has not seen it.
  audience:
    primary: Anyone evaluating the project.
    range: Engineers through non-coders.
  register:
    form: primer
  coverage:
    includes:
      - What the project is for.
    excludes:
      - A directory tour.
  directives:
{directives}
  renderings:
    - format: artifact
      url: https://example.invalid/artifact
      published: 2026-08-01
  external_facts:
    - claim: The project is public.
      source: https://example.invalid/repo
      retrieved: 2026-08-01
---

Body.
"""


def directive_lines(count: int, *, ruling_suffix: str = "") -> str:
    return "\n".join(
        f"    - date: 2026-08-{index + 1:02d}\n"
        f'      ruling: "Ruling {index + 1}{ruling_suffix}"\n'
        f'      effect: "Effect {index + 1}"'
        for index in range(count)
    )


def write_treatise(root: Path, *, directives: int = 1, name: str = "example") -> Path:
    path = root / "briefs" / f"{name}.md"
    path.write_text(TREATISE_BRIEF.format(directives=directive_lines(directives)))
    return path


def run(*arguments: str, root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(TREATISE), "--root", str(root), *arguments],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


@pytest.fixture
def briefs(tmp_path: Path) -> Path:
    (tmp_path / "briefs").mkdir()
    return tmp_path


def test_a_repository_with_no_treatise_passes(briefs: Path) -> None:
    (briefs / "briefs" / "plain.md").write_text(PLAIN_BRIEF)
    result = run("validate", root=briefs)
    assert result.returncode == 0, result.stderr
    assert "no treatises declared" in result.stdout


def test_a_well_formed_treatise_validates(briefs: Path) -> None:
    write_treatise(briefs)
    result = run("validate", root=briefs)
    assert result.returncode == 0, result.stderr
    assert "1 validated" in result.stdout


def test_an_ordinary_brief_is_not_required_to_carry_the_block(briefs: Path) -> None:
    (briefs / "briefs" / "plain.md").write_text(PLAIN_BRIEF)
    write_treatise(briefs)
    result = run("validate", root=briefs)
    assert result.returncode == 0, result.stderr
    assert "plain.md" not in result.stdout


def drop_block(text: str, key: str) -> str:
    """Remove a top-level `treatise:` child and everything nested under it.

    Dropping only the key line would leave orphaned children and produce a YAML
    parse error, which is a different failure than the one under test.
    """
    lines = text.splitlines()
    kept: list[str] = []
    dropping = False
    for line in lines:
        if line.startswith(f"  {key}:"):
            dropping = True
            continue
        if dropping:
            if line.strip() and not line.startswith("    "):
                dropping = False
            else:
                continue
        kept.append(line)
    return "\n".join(kept) + "\n"


@pytest.mark.parametrize(
    "missing_key",
    ["updated", "purpose", "audience", "register", "coverage", "directives"],
)
def test_a_missing_required_key_fails_as_a_missing_key(briefs: Path, missing_key: str) -> None:
    path = write_treatise(briefs)
    path.write_text(drop_block(path.read_text(), missing_key))
    result = run("validate", root=briefs)
    assert result.returncode == 1
    assert f"missing treatise keys: ['{missing_key}']" in result.stderr


def test_an_unknown_key_fails(briefs: Path) -> None:
    path = write_treatise(briefs)
    path.write_text(path.read_text().replace("  purpose:", "  porpoise:\n    x: 1\n  purpose:"))
    result = run("validate", root=briefs)
    assert result.returncode == 1
    assert "unknown treatise keys" in result.stderr


def test_a_directive_without_a_ruling_fails(briefs: Path) -> None:
    path = write_treatise(briefs)
    path.write_text(path.read_text().replace('      ruling: "Ruling 1"\n', ""))
    result = run("validate", root=briefs)
    assert result.returncode == 1
    assert "ruling" in result.stderr


def test_a_non_iso_directive_date_fails(briefs: Path) -> None:
    path = write_treatise(briefs)
    path.write_text(path.read_text().replace("    - date: 2026-08-01", "    - date: last Tuesday"))
    result = run("validate", root=briefs)
    assert result.returncode == 1
    assert "ISO date" in result.stderr


def test_an_external_fact_without_a_retrieval_date_fails(briefs: Path) -> None:
    path = write_treatise(briefs)
    path.write_text(path.read_text().replace("      retrieved: 2026-08-01\n", ""))
    result = run("validate", root=briefs)
    assert result.returncode == 1
    assert "retrieved" in result.stderr


def test_an_empty_directive_list_fails(briefs: Path) -> None:
    path = briefs / "briefs" / "empty.md"
    path.write_text(TREATISE_BRIEF.format(directives="    []"))
    result = run("validate", root=briefs)
    assert result.returncode == 1
    assert "directives" in result.stderr


def test_an_orphaned_sidecar_fails(briefs: Path) -> None:
    write_treatise(briefs)
    (briefs / "briefs" / "example.yaml").write_text("purpose: stale\n")
    result = run("validate", root=briefs)
    assert result.returncode == 1
    assert "fold this sidecar in" in result.stderr


def test_a_sidecar_without_a_matching_brief_is_ignored(briefs: Path) -> None:
    write_treatise(briefs)
    (briefs / "briefs" / "unrelated-data.yaml").write_text("some: data\n")
    result = run("validate", root=briefs)
    assert result.returncode == 0, result.stderr


def test_show_summarizes_each_treatise(briefs: Path) -> None:
    write_treatise(briefs, directives=2)
    result = run("show", root=briefs)
    assert result.returncode == 0, result.stderr
    assert "A treatise" in result.stdout
    assert "directives 2" in result.stdout


def test_a_missing_briefs_directory_reports_an_error(tmp_path: Path) -> None:
    result = run("validate", root=tmp_path)
    assert result.returncode == 2
    assert "missing briefs/ directory" in result.stderr


def test_validate_is_the_default_command(briefs: Path) -> None:
    write_treatise(briefs)
    result = run(root=briefs)
    assert result.returncode == 0, result.stderr
    assert "validated" in result.stdout


def test_the_repository_own_treatise_validates() -> None:
    result = subprocess.run(
        [str(TREATISE), "validate"],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "briefs/methodology-treatise.md" in result.stdout
