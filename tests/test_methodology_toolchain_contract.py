from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _normalized(path: Path) -> str:
    return " ".join(path.read_text().split())


POLICY = _normalized(REPO_ROOT / "policies" / "build-gates.md")
COMMIT_STAGING_POLICY = _normalized(REPO_ROOT / "policies" / "commit-staging.md")
MECHANISTIC_POLICY = _normalized(REPO_ROOT / "policies" / "mechanistic-vs-intelligence.md")
ORCHESTRATION_POLICY = _normalized(REPO_ROOT / "policies" / "orchestration-evidence.md")
ANONYMIZATION_POLICY = _normalized(REPO_ROOT / "policies" / "anonymize-log-references.md")
INCREMENTAL_BRIEF = _normalized(REPO_ROOT / "briefs" / "incremental-orchestration.md")
METHODOLOGY_BRIEF = _normalized(REPO_ROOT / "briefs" / "methodology.md")
RULE_ONE_BRIEF = _normalized(REPO_ROOT / "briefs" / "rule-one-diagnostic-learning.md")
BOOTSTRAP_BRIEF = _normalized(REPO_ROOT / "briefs" / "agentic-bootstrap.md")
CLAUDE = _normalized(REPO_ROOT / "CLAUDE.md")
KICKOFF = _normalized(REPO_ROOT / ".claude" / "skills" / "kickoff" / "SKILL.md")
METHODOLOGY = _normalized(REPO_ROOT / ".claude" / "skills" / "methodology" / "SKILL.md")
RULE_ONE = _normalized(REPO_ROOT / ".claude" / "skills" / "rule-one" / "SKILL.md")
PLANNER = _normalized(REPO_ROOT / ".claude" / "agents" / "phase-planner.md")
PLAN_REVIEWER = _normalized(REPO_ROOT / ".claude" / "agents" / "plan-reviewer.md")
CODER = _normalized(REPO_ROOT / ".claude" / "agents" / "phase-coder.md")
CODE_CRITIC = _normalized(REPO_ROOT / ".claude" / "agents" / "code-critic.md")
LEARN = _normalized(REPO_ROOT / ".claude" / "skills" / "learn" / "SKILL.md")
TEACH = _normalized(REPO_ROOT / ".claude" / "skills" / "teach" / "SKILL.md")
STAMP = _normalized(REPO_ROOT / ".claude" / "skills" / "stamp" / "SKILL.md")
DEMO = _normalized(REPO_ROOT / ".claude" / "skills" / "demo" / "SKILL.md")
TREATISE = _normalized(REPO_ROOT / ".claude" / "skills" / "treatise" / "SKILL.md")
RESEARCH_POLICY = _normalized(REPO_ROOT / "policies" / "research-authority.md")
VERIFICATION_POLICY = _normalized(REPO_ROOT / "policies" / "verification-discipline.md")
TREATISE_POLICY = _normalized(REPO_ROOT / "policies" / "treatise.md")
USER_DEMO_POLICY = _normalized(REPO_ROOT / "policies" / "user-demo-protocols.md")
TEST_GOVERNANCE_POLICY = _normalized(REPO_ROOT / "policies" / "test-suite-governance.md")
TEST_GOVERNANCE_BRIEF = _normalized(REPO_ROOT / "briefs" / "test-suite-value-governance.md")


def test_proof_estate_governance_propagates_without_local_judgments() -> None:
    required = (
        "briefs/test-suite-value-governance.md",
        "policies/test-suite-governance.md",
        "bin/test-governance",
        "lib/agentic_starter/test_governance.py",
        "tests/test_test_governance.py",
        "tests/test_pre_commit.py",
        "reports/test-governance/README.md",
    )
    for phrase in required:
        for document in (LEARN, TEACH, STAMP, BOOTSTRAP_BRIEF):
            assert phrase in document, f"{phrase} missing from a transfer authority"
    for document in (
        TEST_GOVERNANCE_POLICY,
        TEST_GOVERNANCE_BRIEF,
        LEARN,
        TEACH,
        STAMP,
        BOOTSTRAP_BRIEF,
    ):
        assert "local" in document or "recipient" in document
        assert "full" in document
    assert "Never copy donor family choices" in LEARN
    assert "Never seed the target" in TEACH
    assert "generated from the destination rather than copied" in STAMP


def test_every_universal_skill_propagates_with_its_codex_mirror() -> None:
    """Every canonical skill except starter-only `stamp` reaches a derived project.

    `bin/check-harness-parity` fails closed on a canonical skill with no
    `.agents/skills` mirror, so a skill named in the transfer documents without
    its symlink breaks the destination's gate exactly as a missing skill does.
    """
    canonical_root = REPO_ROOT / ".claude" / "skills"
    universal = sorted(
        item.name for item in canonical_root.iterdir() if item.is_dir() and item.name != "stamp"
    )
    assert "plain" in universal, "the operator register is a universal skill"
    for skill in universal:
        canonical = f".claude/skills/{skill}/SKILL.md"
        mirror = f".agents/skills/{skill}"
        for document in (STAMP, BOOTSTRAP_BRIEF):
            assert canonical in document, f"{skill} missing from a transfer document"
            assert mirror in document, f"{skill} mirror missing from a transfer document"
        assert skill in TEACH

    skill_path = ".claude/skills/rule-one/SKILL.md"
    brief_name = "rule-one-diagnostic-learning.md"
    assert "name: rule-one" in RULE_ONE
    assert "symptom, not a diagnosis" in RULE_ONE
    assert skill_path in RULE_ONE_BRIEF
    for surface in (
        CLAUDE,
        METHODOLOGY_BRIEF,
        METHODOLOGY,
        LEARN,
        TEACH,
        STAMP,
        BOOTSTRAP_BRIEF,
    ):
        assert skill_path in surface
        assert brief_name in surface
    assert "Rule One learning is atomic" in LEARN
    assert "Rule One teaching is atomic" in TEACH
    assert "one member absent" in LEARN
    assert "one member absent" in TEACH

    mirror = REPO_ROOT / ".agents" / "skills" / "rule-one"
    assert mirror.is_symlink()
    assert mirror.readlink().as_posix() == "../../.claude/skills/rule-one"
    assert (mirror / "SKILL.md").is_file()


def test_every_gate_required_executable_propagates() -> None:
    """`bin/check` names the executables it refuses to start without.

    That list is the authority: a transfer document that omits one produces a
    destination whose gate exits before running a single check. Reading the
    requirement out of `bin/check` keeps this test honest when the list grows.
    """
    check = (REPO_ROOT / "bin" / "check").read_text()
    marker = "for evidence_executable in \\\n"
    start = check.index(marker) + len(marker)
    end = check.index("; do", start)
    required = check[start:end].replace("\\\n", " ").split()
    assert len(required) >= 14, required
    starter_only = {"check-anonymization.sh"}
    for name in required:
        if name in starter_only:
            continue
        for document in (STAMP, BOOTSTRAP_BRIEF, TEACH):
            assert f"bin/{name}" in document, f"bin/{name} missing from a transfer document"

    control_plane = (
        "briefs/deterministic-orchestration-control-plane.md",
        "policies/orchestration-control-plane.md",
        "lib/agentic_starter/candidate_boundaries.py",
        "lib/agentic_starter/kickoff_runbook.py",
        "lib/agentic_starter/log_blocks.py",
        "tests/test_kickoff_control_plane.py",
        "tests/test_log_control_plane.py",
    )
    for path in control_plane:
        for document in (LEARN, TEACH, STAMP, BOOTSTRAP_BRIEF):
            assert path in document, f"{path} missing from a transfer authority"


def test_research_authority_contract_propagates_and_stays_allow_by_default() -> None:
    assert "allow-by-default" in RESEARCH_POLICY
    assert "same-host structural neighbors" in RESEARCH_POLICY
    assert "GET" in RESEARCH_POLICY
    for document in (STAMP, TEACH, BOOTSTRAP_BRIEF, KICKOFF):
        assert "research" in document
    for role in (PLANNER, PLAN_REVIEWER):
        assert "originate" in role and "retriev" in role
    for role in (CODER, CODE_CRITIC):
        assert "Do not originate" in role


def test_material_review_counts_are_reproducible() -> None:
    assert "Material counts are reproducible" in VERIFICATION_POLICY
    for document in (PLAN_REVIEWER, CODE_CRITIC, KICKOFF):
        assert "material count" in document
        assert "exact command or deterministic procedure" in document
