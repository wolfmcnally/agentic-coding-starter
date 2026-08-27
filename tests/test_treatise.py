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


def test_an_external_fact_without_a_retrieval_date_fails(briefs: Path) -> None:
    path = write_treatise(briefs)
    path.write_text(path.read_text().replace("      retrieved: 2026-08-01\n", ""))
    result = run("validate", root=briefs)
    assert result.returncode == 1
    assert "retrieved" in result.stderr


def declared_treatise_briefs() -> list[str]:
    """Return every brief in this repository whose frontmatter declares a treatise.

    Derived from the tree rather than hard-coded. This test is carried into every
    project stamped from the template, and those projects do not carry the
    template's own treatise brief — a hard-coded filename would fail there for a
    reason that is not a defect.
    """
    briefs = ROOT / "briefs"
    if not briefs.is_dir():
        return []
    declared: list[str] = []
    for path in sorted(briefs.glob("*.md")):
        lines = path.read_text(encoding="utf-8").splitlines()
        if not lines or lines[0].strip() != "---":
            continue
        for line in lines[1:]:
            if line.strip() in ("---", "..."):
                break
            if line.startswith("treatise:"):
                declared.append(f"briefs/{path.name}")
                break
    return declared


def test_the_repository_own_treatises_validate() -> None:
    result = subprocess.run(
        [str(TREATISE), "validate"],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    declared = declared_treatise_briefs()
    if declared:
        for relative in declared:
            assert relative in result.stdout
    else:
        assert "no treatises declared" in result.stdout
