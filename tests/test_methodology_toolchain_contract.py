from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _normalized(path: Path) -> str:
    return " ".join(path.read_text().split())


POLICY = _normalized(REPO_ROOT / "policies" / "build-gates.md")
ANONYMIZATION_POLICY = _normalized(REPO_ROOT / "policies" / "anonymize-log-references.md")
LEARN = _normalized(REPO_ROOT / ".claude" / "skills" / "learn" / "SKILL.md")
TEACH = _normalized(REPO_ROOT / ".claude" / "skills" / "teach" / "SKILL.md")
STAMP = _normalized(REPO_ROOT / ".claude" / "skills" / "stamp" / "SKILL.md")


def test_atomic_contract_pins_behavioral_coverage_floor() -> None:
    assert "Behavioral execution is the minimum test floor" in POLICY
    assert "source-text assertions may supplement it, but do not replace" in POLICY
    for skill in (LEARN, TEACH, STAMP):
        assert "source-text" in skill
        assert "controlled" in skill


def test_atomic_contract_covers_all_operational_callers() -> None:
    required = (
        "dependency-bearing operational caller",
        "generated command",
        "tracked hook",
        "active instruction",
    )
    for phrase in required:
        assert phrase in POLICY
        assert phrase in LEARN
        assert phrase in TEACH
        assert phrase in STAMP


def test_atomic_contract_covers_complete_candidate_format_state() -> None:
    for document in (POLICY, LEARN, TEACH, STAMP):
        assert "staged" in document
        assert "unstaged" in document
        assert "nonignored untracked" in document


def test_atomic_contract_resolves_repeated_runtime_once() -> None:
    for document in (POLICY, LEARN, TEACH, STAMP):
        assert "hot loop" in document
        assert "mutation gate" in document
        assert "detached process" in document
        assert "once" in document


def test_anonymization_boundary_follows_write_destination() -> None:
    assert "boundary follows the destination of the write" in ANONYMIZATION_POLICY
    assert "Starter's starter-only anonymization policy" in TEACH
    assert "target's approved provenance/count template" in TEACH
