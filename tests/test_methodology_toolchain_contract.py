from __future__ import annotations

import json
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
DEMO = _normalized(REPO_ROOT / ".claude" / "skills" / "demo" / "SKILL.md")
TREATISE = _normalized(REPO_ROOT / ".claude" / "skills" / "treatise" / "SKILL.md")
RESEARCH_POLICY = _normalized(REPO_ROOT / "policies" / "research-authority.md")
VERIFICATION_POLICY = _normalized(REPO_ROOT / "policies" / "verification-discipline.md")
TREATISE_POLICY = _normalized(REPO_ROOT / "policies" / "treatise.md")
USER_DEMO_POLICY = _normalized(REPO_ROOT / "policies" / "user-demo-protocols.md")


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
        assert "repository-selected runtime" in document
        assert "base-executable" in document
        assert "version-file proxy" in document or "version declaration" in document
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


def test_orchestration_contract_keeps_both_close_gates() -> None:
    assert "the complete phase-prescribed sequence" in ORCHESTRATION_POLICY
    assert "--require-final" in ORCHESTRATION_POLICY
    assert "authoritative full gate last" in KICKOFF
    for document in (ORCHESTRATION_POLICY, KICKOFF):
        assert "implementation" in document and "handoff gate" in document
        assert "No tracked write" in document or "no tracked write" in document


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


def test_shared_library_and_report_archive_propagate_with_their_callers() -> None:
    """`bin/execution-telemetry` imports `lib/`; neither travels alone."""
    for phrase in ("lib/agentic_starter/", "reports/execution/"):
        for document in (STAMP, BOOTSTRAP_BRIEF, TEACH):
            assert phrase in document, f"{phrase} missing from a transfer document"


def test_starter_only_surfaces_are_named_as_staying_behind() -> None:
    """Each starter-only surface exists here and is named as not propagating."""
    starter_only = (
        "policies/anonymize-log-references.md",
        "bin/check-anonymization.sh",
        "bin/anonymization-denylist.local.example",
        "tests/test_methodology_toolchain_contract.py",
        "briefs/eacp-pattern-map.md",
        "briefs/methodology-treatise.md",
    )
    for relative in starter_only:
        assert (REPO_ROOT / relative).exists(), f"{relative} named but absent"
        assert relative in STAMP, f"{relative} not named as starter-only in stamp"
        assert relative in BOOTSTRAP_BRIEF, f"{relative} not named as starter-only in the brief"


def test_universal_demo_and_treatise_bundle_propagates_atomically() -> None:
    for skill in ("demo", "treatise"):
        canonical = f".claude/skills/{skill}/SKILL.md"
        mirror = f".agents/skills/{skill}"
        for document in (STAMP, BOOTSTRAP_BRIEF):
            assert canonical in document
            assert mirror in document
        assert skill in TEACH
    assert "policies/user-demo-protocols.md" in DEMO
    assert "policies/treatise.md" in TREATISE
    assert "canonical" in TREATISE_POLICY and "publication" in TREATISE_POLICY
    assert "universal `demo` skill" in USER_DEMO_POLICY


def test_portable_background_isolation_disables_only_implicit_worktrees() -> None:
    settings = json.loads((REPO_ROOT / ".claude" / "settings.json").read_text())
    assert settings == {"worktree": {"bgIsolation": "none"}}
    for document in (STAMP, TEACH, BOOTSTRAP_BRIEF):
        assert ".claude/settings.json" in document
        assert "explicit" in document and "worktree" in document


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
        assert "handoff" in document


def test_canonical_roles_apply_wall_clock_judgment_proportionally() -> None:
    for role in (PLANNER, PLAN_REVIEWER, CODER, CODE_CRITIC):
        assert "wall-clock" in role
        assert "substantial" in role
        assert "low-risk" in role
        assert "micro-optimization" in role or "marginal" in role
