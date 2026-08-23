from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _normalized(path: Path) -> str:
    return " ".join(path.read_text().split())


POLICY = _normalized(REPO_ROOT / "policies" / "build-gates.md")
MECHANISTIC_POLICY = _normalized(REPO_ROOT / "policies" / "mechanistic-vs-intelligence.md")
ORCHESTRATION_POLICY = _normalized(REPO_ROOT / "policies" / "orchestration-evidence.md")
ANONYMIZATION_POLICY = _normalized(REPO_ROOT / "policies" / "anonymize-log-references.md")
INCREMENTAL_BRIEF = _normalized(REPO_ROOT / "briefs" / "incremental-orchestration.md")
METHODOLOGY_BRIEF = _normalized(REPO_ROOT / "briefs" / "methodology.md")
BOOTSTRAP_BRIEF = _normalized(REPO_ROOT / "briefs" / "agentic-bootstrap.md")
CLAUDE = _normalized(REPO_ROOT / "CLAUDE.md")
KICKOFF = _normalized(REPO_ROOT / ".claude" / "skills" / "kickoff" / "SKILL.md")
METHODOLOGY = _normalized(REPO_ROOT / ".claude" / "skills" / "methodology" / "SKILL.md")
PLANNER = _normalized(REPO_ROOT / ".claude" / "agents" / "phase-planner.md")
PLAN_REVIEWER = _normalized(REPO_ROOT / ".claude" / "agents" / "plan-reviewer.md")
CODER = _normalized(REPO_ROOT / ".claude" / "agents" / "phase-coder.md")
CODE_CRITIC = _normalized(REPO_ROOT / ".claude" / "agents" / "code-critic.md")
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


def test_full_gate_receipt_contract_propagates_atomically() -> None:
    for document in (POLICY, LEARN, TEACH, STAMP, BOOTSTRAP_BRIEF):
        assert "full-gate receipt" in document
        assert "environment fingerprint" in document
        assert "complete log" in document
        assert "fail" in document and "closed" in document
    for document in (TEACH, STAMP, BOOTSTRAP_BRIEF):
        assert "bin/check-receipt" in document
        assert "tests/test_check_receipt.py" in document


def test_anonymization_boundary_follows_write_destination() -> None:
    assert "boundary follows the destination of the write" in ANONYMIZATION_POLICY
    assert "Starter's starter-only anonymization policy" in TEACH
    assert "target's approved provenance/count template" in TEACH


def test_orchestration_contract_is_candidate_bound_and_incremental() -> None:
    for document in (ORCHESTRATION_POLICY, KICKOFF):
        assert "kickoff-tree-id" in document
        assert "authority" in document
        assert "drift" in document
        assert "revision packet" in document
        assert "focused" in document
        assert "./bin/check all" in document
        assert "unchanged approved candidate" in document


def test_orchestration_contract_keeps_one_complete_final_gate() -> None:
    assert "the complete phase-prescribed sequence" in ORCHESTRATION_POLICY
    assert "once after code-critic approval" in ORCHESTRATION_POLICY
    assert "--require-final" in ORCHESTRATION_POLICY
    assert "authoritative full gate last" in KICKOFF


def test_protocol_recovery_never_becomes_ordinary_success() -> None:
    for document in (ORCHESTRATION_POLICY, KICKOFF):
        assert "Exit 66" in document
        assert "terminal stream" in document
        assert "not success" in document or "Ordinary success requires" in document


def test_candidate_evidence_bundle_propagates_atomically() -> None:
    required = (
        "briefs/incremental-orchestration.md",
        "policies/orchestration-evidence.md",
        "bin/kickoff-tree-id",
        "bin/kickoff-evidence",
        "tests/test_kickoff_tree_id.py",
        "tests/test_kickoff_evidence.py",
    )
    for phrase in required:
        assert phrase in STAMP
        assert phrase in TEACH
    assert "Orchestration-evidence learning is atomic" in LEARN


def test_self_improvement_bundle_propagates_atomically() -> None:
    required = (
        ".claude/skills/sweep/SKILL.md",
        "briefs/harness-self-improvement.md",
        "policies/lessons.md",
        "bin/lessons",
        "bin/check-catalogs",
        "tests/test_lessons.py",
        "tests/test_check_catalogs.py",
        "lessons-archived",
    )
    for phrase in required:
        assert phrase in STAMP
        assert phrase in TEACH
        assert phrase in BOOTSTRAP_BRIEF


def test_methodology_narrative_carries_lessons_and_failure_analysis() -> None:
    for document in (METHODOLOGY, METHODOLOGY_BRIEF):
        assert "lessons harvest" in document
        assert "Process Observations" in document
    assert "root-cause failure analysis" in INCREMENTAL_BRIEF
    assert "root-cause Failure Analysis" in _normalized(
        REPO_ROOT / "policies" / "four-canonical-agents.md"
    )


def test_learn_harvests_the_post_application_return_path() -> None:
    assert "Harvest the application return path" in LEARN
    assert "Application-found return candidates" in LEARN
    assert "source: learn" in LEARN
    assert "scope: methodology" in LEARN
    assert "after all rule, lesson, stale-migration, and LOG writes" in LEARN


def test_human_wall_clock_efficiency_is_ambient_and_effectiveness_preserving() -> None:
    for document in (
        CLAUDE,
        POLICY,
        MECHANISTIC_POLICY,
        INCREMENTAL_BRIEF,
        KICKOFF,
    ):
        assert "wall-clock" in document
        assert "substantial" in document

    for document in (POLICY, MECHANISTIC_POLICY, INCREMENTAL_BRIEF, KICKOFF, CODER):
        assert "fixed" in document or "numeric" in document
        assert "marginal" in document

    for document in (CLAUDE, KICKOFF, PLANNER, CODER, CODE_CRITIC):
        assert "complete final gate" in document


def test_canonical_roles_apply_wall_clock_judgment_proportionally() -> None:
    for role in (PLANNER, PLAN_REVIEWER, CODER, CODE_CRITIC):
        assert "wall-clock" in role
        assert "substantial" in role
        assert "low-risk" in role
        assert "micro-optimization" in role or "marginal" in role
