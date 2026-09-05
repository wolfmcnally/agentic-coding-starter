from __future__ import annotations

import re
import shutil
from pathlib import Path

import pytest
from test_check_catalogs import RESOURCES

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
ASK = _normalized(REPO_ROOT / ".claude" / "skills" / "ask" / "SKILL.md")
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


def test_every_universal_skill_propagates_with_its_codex_mirror(tmp_path: Path) -> None:
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
    assert "ask" in universal, "the operator-invoked decision inventory is a universal skill"
    for skill in universal:
        canonical = f".claude/skills/{skill}/SKILL.md"
        mirror = f".agents/skills/{skill}"
        for document in (STAMP, BOOTSTRAP_BRIEF):
            if skill == "kickoff":
                assert ".claude/skills/kickoff/`" in document
                for resource in ("SKILL.md", *RESOURCES):
                    assert f"`{resource}`" in document
            else:
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

    ask_path = ".claude/skills/ask/SKILL.md"
    assert "name: ask" in ASK
    assert "disable-model-invocation: true" in ASK, "ask is operator-invoked only"
    assert "$ARGUMENTS" in ASK
    assert "unavailable in the current mode" in ASK, "ask needs the mode fallback"
    planning = _normalized(REPO_ROOT / ".claude/skills/kickoff/planning.md")
    for surface in (CLAUDE, planning, PLAN_REVIEWER, STAMP, TEACH, BOOTSTRAP_BRIEF):
        assert ask_path in surface or "ask/SKILL.md" in surface, "ask missing from a citing surface"
    assert "AFK" not in KICKOFF, "kickoff must not cite a machine-global unattended protocol"
    ask_mirror = REPO_ROOT / ".agents" / "skills" / "ask"
    assert ask_mirror.is_symlink()
    assert ask_mirror.readlink().as_posix() == "../../.claude/skills/ask"
    assert (ask_mirror / "SKILL.md").is_file()

    mirror = REPO_ROOT / ".agents" / "skills" / "rule-one"
    assert mirror.is_symlink()
    assert mirror.readlink().as_posix() == "../../.claude/skills/rule-one"
    assert (mirror / "SKILL.md").is_file()
    _exercise_transfer_recipes(tmp_path)
    _exercise_owned_contract(
        tmp_path / "phase-entry",
        "preflight.md",
        (
            "If none exists while a row is `🚧`, require an explicit phase id "
            "to resume that active work.",
            "A coherent change stays intact.",
            "An unresolved consequential decision goes to the operator before implementation; "
            "it is not a private choice delegated to the coder.",
        ),
    )
    _exercise_owned_contract(
        tmp_path / "decisions",
        "planning.md",
        (
            "**If `REVISE` and any finding is `blocked-owner`**: "
            "do not re-run the planner on that finding",
        ),
    )
    _exercise_owned_contract(
        tmp_path / "recovery",
        "recovery.md",
        (
            "$TELEMETRY_TOOL park-open --phase",
            "Read [acceptance.md](acceptance.md) before validation and [close.md](close.md) "
            "before terminal bookkeeping, the handoff gate or delivery.",
        ),
    )


def _assert_owned_contract(root: Path, resource: str, clauses: tuple[str, ...]) -> None:
    entry = root / ".claude/skills/kickoff/SKILL.md"
    rows = [line.split("|") for line in entry.read_text().splitlines() if line.startswith("|")]
    assert any(
        len(row) == 5
        and row[2].strip() == f"[{resource}]({resource})"
        and row[3].strip().startswith("Read before ")
        for row in rows
    ), f"{resource}: no operative entry row"
    owner = " ".join((entry.parent / resource).read_text().split())
    for clause in clauses:
        assert clause in owner, f"{resource}: missing owned obligation: {clause}"


def _exercise_owned_contract(tmp_path: Path, resource: str, clauses: tuple[str, ...]) -> None:
    """Exact obligation witnesses; contextual meaning still belongs to review."""
    skill = tmp_path / ".claude/skills/kickoff"
    shutil.copytree(REPO_ROOT / ".claude/skills/kickoff", skill)
    _assert_owned_contract(tmp_path, resource, clauses)
    owner = skill / resource
    original = owner.read_text()
    entry = skill / "SKILL.md"
    entry.write_text(entry.read_text() + "\nUnrelated quotation: " + " ".join(clauses) + "\n")
    for clause in clauses:
        owner.write_text(" ".join(original.split()).replace(clause, "Obligation withdrawn."))
        with pytest.raises(AssertionError, match=f"{resource}: missing owned obligation"):
            _assert_owned_contract(tmp_path, resource, clauses)
    owner.write_text(original)
    _assert_owned_contract(tmp_path, resource, clauses)


def _exercise_transfer_recipes(tmp_path: Path) -> None:
    stamp = (REPO_ROOT / ".claude/skills/stamp/SKILL.md").read_text()
    bootstrap = (REPO_ROOT / "briefs/agentic-bootstrap.md").read_text()
    # Keep these inventories independent: agreement elsewhere cannot fill a gap.
    recipes = (
        (
            "stamp",
            stamp.split("**Load-bearing members", 1)[1].split("The candidate-identity", 1)[0],
            stamp.split("**Starter-only — leave behind:**", 1)[1].split("Everything else", 1)[0],
            stamp.split("**Universal surfaces — copy the whole directory:**", 1)[1].split(
                "**Starter-only", 1
            )[0],
        ),
        (
            "bootstrap",
            bootstrap.split("### 2a.", 1)[1].split("### 2b.", 1)[0],
            bootstrap.split("### 2c.", 1)[1].split("If in doubt", 1)[0],
            bootstrap.split("### 2a.", 1)[1].split("### 2b.", 1)[0],
        ),
    )
    for name, inventory, exclusions, surfaces in recipes:
        resource_row = next(
            line for line in inventory.splitlines() if "`.claude/skills/kickoff/`" in line
        )
        assert "SKILL.md" in inventory, f"{name}: entry missing from inventory"
        for resource in RESOURCES:
            assert f"`{resource}`" in resource_row, f"{name}: resource inventory lacks {resource}"
        assert "docs/README.md" in surfaces
        assert "every row removed" in surfaces or "every row dropped" in surfaces
        assert "briefs/astra-era-development.md" in exclusions
        assert "pinned document" in surfaces or "pinned document" in exclusions
        excluded_briefs = set(re.findall(r"briefs/([\w.-]+\.md)", exclusions))
        destination = tmp_path / name
        for skill in sorted((REPO_ROOT / ".claude/skills").iterdir()):
            if not skill.is_dir() or skill.name == "stamp":
                continue
            shutil.copytree(skill, destination / ".claude/skills" / skill.name)
            link = destination / ".agents/skills" / skill.name
            link.parent.mkdir(parents=True, exist_ok=True)
            link.symlink_to(f"../../.claude/skills/{skill.name}", target_is_directory=True)
        shutil.copytree(
            REPO_ROOT / "briefs",
            destination / "briefs",
            ignore=shutil.ignore_patterns(*excluded_briefs),
        )
        (destination / "docs").mkdir()
        catalog = (REPO_ROOT / "docs/README.md").read_text().splitlines(keepends=True)
        table_rows = [line for line in catalog if line.startswith("|")]
        header = "".join(line for line in catalog if not line.startswith("|"))
        header += "".join(table_rows[:2])
        (destination / "docs/README.md").write_text(header)
        _assert_transferred_resources(destination)
        _assert_transfer_exclusions(destination)
        for resource in RESOURCES:
            target = destination / ".claude/skills/kickoff" / resource
            body = target.read_bytes()
            target.unlink()
            with pytest.raises(AssertionError, match=f"missing resource {resource}"):
                _assert_transferred_resources(destination)
            target.write_bytes(body)
        leaked = destination / "briefs/astra-era-development.md"
        shutil.copy2(REPO_ROOT / "briefs/astra-era-development.md", leaked)
        with pytest.raises(AssertionError, match="local Astra authority"):
            _assert_transfer_exclusions(destination)
        leaked.unlink()
        pin = destination / "docs/template-pin.md"
        pin.write_text("# Template-only pin\n")
        with pytest.raises(AssertionError, match="template pins"):
            _assert_transfer_exclusions(destination)
        pin.unlink()
        _assert_transferred_resources(destination)
        _assert_transfer_exclusions(destination)


def _assert_transferred_resources(destination: Path) -> None:
    canonical = destination / ".claude/skills/kickoff"
    mirror = destination / ".agents/skills/kickoff"
    assert mirror.is_symlink()
    assert mirror.readlink().as_posix() == "../../.claude/skills/kickoff"
    for resource in ("SKILL.md", *RESOURCES):
        assert (canonical / resource).is_file(), f"missing resource {resource}"
        expected = (REPO_ROOT / ".claude/skills/kickoff" / resource).read_bytes()
        assert (canonical / resource).read_bytes() == expected
        assert (mirror / resource).read_bytes() == expected
    for resource in RESOURCES:
        _assert_owned_contract(destination, resource, ())


def _assert_transfer_exclusions(destination: Path) -> None:
    assert not (destination / "briefs/astra-era-development.md").exists(), "local Astra authority"
    assert not (destination / ".claude/skills/stamp").exists(), "local stamp skill"
    entries = {item.name for item in (destination / "docs").iterdir()}
    assert entries == {"README.md"}, "template pins"
    rows = [
        line
        for line in (destination / "docs/README.md").read_text().splitlines()
        if line.startswith("|")
    ]
    assert len(rows) == 2, "template catalog rows"


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
        "candidate-partition.yaml",
        "bin/check-candidate-partition",
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


def test_research_authority_contract_propagates_and_stays_allow_by_default(tmp_path: Path) -> None:
    assert "allow-by-default" in RESEARCH_POLICY
    assert "same-host structural neighbors" in RESEARCH_POLICY
    assert "GET" in RESEARCH_POLICY
    for document in (STAMP, TEACH, BOOTSTRAP_BRIEF):
        assert "research" in document
    for role in (PLANNER, PLAN_REVIEWER):
        assert "originate" in role and "retriev" in role
    for role in (CODER, CODE_CRITIC):
        assert "Do not originate" in role
    _exercise_owned_contract(
        tmp_path / "preflight",
        "preflight.md",
        (
            "Run `./bin/kickoff-config show research`",
            "coder and critic may retrieve plan/brief-identified resources and same-host "
            "structural neighbors but may not originate searches.",
            "Installed MCP servers and plugins remain available by default unless the project "
            "or phase explicitly narrows them.",
        ),
    )
    _exercise_owned_contract(
        tmp_path / "dispatch",
        "dispatch.md",
        (
            "the watcher supplies research/access directives, schemas, credential handling, "
            "routing and budgets; never reconstruct weaker substitutes from memory.",
            "Native dispatches use the generated `span-recipe` commands and the same resolved "
            "research directive and output contract.",
        ),
    )


def test_material_review_counts_are_reproducible(tmp_path: Path) -> None:
    assert "Material counts are reproducible" in VERIFICATION_POLICY
    for document in (PLAN_REVIEWER, CODE_CRITIC):
        assert "material count" in document
        assert "exact command or deterministic procedure" in document
    _exercise_owned_contract(
        tmp_path,
        "close.md",
        (
            "Every material count carries the exact command or deterministic procedure that "
            "produced it; a relayed number is remeasured or attributed plainly as unverified",
        ),
    )
