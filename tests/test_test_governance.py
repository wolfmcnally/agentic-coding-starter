from __future__ import annotations

import copy
import difflib
import hashlib
import shlex
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "lib"))

import agentic_starter.test_governance as governance  # noqa: E402


def test_parameterized_leaves_collapse_to_one_family() -> None:
    assert governance._pytest_family("tests/test_x.py::test_case[value]") == (
        "tests/test_x.py::test_case"
    )


def test_inventory_counts_executable_families_and_expanded_leaves() -> None:
    observed = governance.inventory(REPO_ROOT)
    assert observed["counts"] == {"families": 110, "leaves": 128}
    assert observed["by_kind"]["pytest"] == {"families": 86, "leaves": 104}


def test_live_reset_validates() -> None:
    summary = governance.validate(REPO_ROOT)
    assert summary["state"] == "valid"
    assert summary["dispositions"]["delete"] > 0
    assert summary["dispositions"]["consolidate"] > 0


def test_size_ceilings_and_lane_budget_survive_timing_noise(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    node = "tests/test_x.py::test_fast"
    slow = "tests/test_x.py::TestGroup::test_slow[case]"
    proofs = [
        {
            "id": f"pytest:{item}",
            "family": f"pytest:{item.split('[', 1)[0]}",
            "kind": "pytest",
            "selector": item,
            "source_path": "tests/test_x.py",
        }
        for item in (node, slow)
    ]
    manifest = {
        "families": [
            {"id": "x", "kind": "pytest", "selectors": ["tests/test_x.py"], "size": "small"}
        ],
        "size_ceilings_seconds": {"small": 2, "medium": 20, "large": 200},
        "time_budget": {
            "test_lane_seconds": 10,
            "tolerance": 0.25,
            "reference_machine": governance.machine_fingerprint(),
        },
    }
    monkeypatch.setattr(governance, "inventory", lambda _root: {"proofs": proofs})
    monkeypatch.setattr(governance, "load_yaml", lambda _path: copy.deepcopy(manifest))
    record = tmp_path / governance.TIMING_RECORD
    record.parent.mkdir(parents=True)

    source = "../tests/test_x.py"

    def recorded(
        total: float, slow_seconds: float, cases: tuple[str, ...] = ("fast", "slow")
    ) -> None:
        rows = {
            "fast": (f'<testcase classname="test_x" name="test_fast" file="{source}" time="0.1"/>'),
            "slow": (
                '<testcase classname="test_x.TestGroup" name="test_slow[case]" '
                f'file="../tests/test_x.py" time="{slow_seconds}"/>'
            ),
            "gone": (f'<testcase classname="test_x" name="test_gone" file="{source}" time="0.1"/>'),
        }
        record.write_text(
            f'<testsuites><testsuite time="{total}">'
            + "".join(rows[case] for case in cases)
            + "</testsuite></testsuites>"
        )

    assert governance.timing(tmp_path)["reason"] == "no full-run timing record"
    recorded(8.0, 1.5)
    observed = governance.timing(tmp_path)
    assert (observed["state"], observed["budget"]) == ("measured", "within")
    assert observed["slowest"][0] == {"proof": f"pytest:{slow}", "seconds": 1.5}

    # One noisy run over budget-plus-tolerance is advisory; three confirming runs fail.
    recorded(12.6, 1.5)
    assert governance.timing(tmp_path)["budget"].startswith("advisory")
    runs = iter([12.6, 12.7, 12.8])

    def full_run(command: list[str], _root: Path, check: bool = True):
        recorded(next(runs), 1.5)
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(governance, "_run", full_run)
    confirmed = governance.timing(tmp_path, samples=3)
    assert (confirmed["state"], confirmed["budget"], confirmed["samples"]) == ("fail", "over", 3)

    # A budget set on one machine is never judged on another, but size ceilings still bind.
    manifest["time_budget"]["reference_machine"] = "0" * 16
    recorded(99.0, 2.5)
    foreign = governance.timing(tmp_path)
    assert foreign["budget"] == "unmeasured: this is not the reference machine"
    assert foreign["state"] == "fail"
    assert "over the small ceiling of 2s for family x" in foreign["size_violations"][0]

    # A record from a different estate is stale, not a measurement.
    recorded(1.0, 0.1, cases=("fast", "slow", "gone"))
    assert (
        governance.timing(tmp_path)["reason"]
        == "the timing record predates the current pytest estate"
    )
    recorded(1.0, 0.1, cases=("fast",))
    assert governance.timing(tmp_path)["state"] == "unmeasured"
    manifest["size_ceilings_seconds"]["medium"] = 1
    with pytest.raises(governance.GovernanceError, match="increase from small to large"):
        governance.timing(tmp_path)


def test_incomplete_disposition_evidence_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = governance.load_ledger
    mode = ["missing"]

    def malformed(path: Path):
        rows = original(path)
        if path.name == "starter-reset.jsonl":
            if mode[0] == "missing":
                rows.pop(0)
            else:
                rows[0] = {key: value for key, value in rows[0].items() if key != "oracle"}
        return rows

    monkeypatch.setattr(governance, "load_ledger", malformed)
    with pytest.raises(governance.GovernanceError, match="misses 1 baseline proofs"):
        governance.validate(REPO_ROOT)
    mode[0] = "evidence"
    with pytest.raises(governance.GovernanceError, match="wrong disposition fields"):
        governance.validate(REPO_ROOT)


def test_shadow_deleted_proof_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    original = governance.load_ledger
    mode = ["delete"]

    def shadowed(path: Path):
        rows = original(path)
        if path.name == "starter-reset.jsonl":
            if mode[0] == "delete":
                retained = next(row for row in rows if row["disposition"] == "retain")
                retained["disposition"] = "delete"
                retained["replacement"] = None
            else:
                consolidated = next(row for row in rows if row["disposition"] == "consolidate")
                consolidated["replacement"] = "pytest:absent"
        return rows

    monkeypatch.setattr(governance, "load_ledger", shadowed)
    with pytest.raises(governance.GovernanceError, match="deleted proof still exists"):
        governance.validate(REPO_ROOT)
    mode[0] = "replacement"
    with pytest.raises(governance.GovernanceError, match="invalid replacement"):
        governance.validate(REPO_ROOT)


def test_frozen_patches_must_still_apply_or_already_be_applied(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = "lib/agentic_starter/test_governance.py"
    current = (REPO_ROOT / source).read_text().splitlines(keepends=True)
    anchor = current.index('SIZES = ("small", "medium", "large")\n')
    earlier = [*current[:anchor], "SIZES = ()\n", *current[anchor + 1 :]]
    applied = tmp_path / "applied.patch"
    applied.write_text(
        "".join(difflib.unified_diff(earlier, current, f"a/{source}", f"b/{source}"))
    )
    # The same seeded change, but anchored on a context line the code no longer has.
    stale = tmp_path / "stale.patch"
    stale.write_text(applied.read_text().replace(" TIERS = ", " TIERS_RENAMED = ", 1))
    assert stale.read_text() != applied.read_text()
    original = governance.load_yaml
    chosen = [stale]

    def pointed(path: Path):
        payload = original(path)
        if path.name == "corpus.yaml":
            case = payload["cases"][0]
            case["patch"] = str(chosen[0])
            case["patch_sha256"] = hashlib.sha256(chosen[0].read_bytes()).hexdigest()
        return payload

    def matching_report(path: Path):
        rows = original_ledger(path)
        if path.name == "starter-effectiveness.jsonl":
            rows[0]["patch_sha256"] = hashlib.sha256(chosen[0].read_bytes()).hexdigest()
        return rows

    original_ledger = governance.load_ledger
    monkeypatch.setattr(governance, "load_yaml", pointed)
    monkeypatch.setattr(governance, "load_ledger", matching_report)
    with pytest.raises(
        governance.GovernanceError, match="patch no longer applies: check-mode-arity"
    ):
        governance.validate(REPO_ROOT)
    # Inside an assay copy the mutation is already applied; that must not read as a detection.
    chosen[0] = applied
    assert governance.validate(REPO_ROOT)["state"] == "valid"


def test_critical_risk_requires_a_retained_direct_proof(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = governance.load_yaml

    def missing(path: Path):
        payload = original(path)
        if path.name == "proof-estate.yaml":
            payload["critical_risks"]["custody"]["direct_proof"] = "pytest:absent"
        return payload

    monkeypatch.setattr(governance, "load_yaml", missing)
    with pytest.raises(governance.GovernanceError, match="direct proof is not retained"):
        governance.validate(REPO_ROOT)


def test_recall_below_eighty_percent_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    original = governance.load_ledger

    def weakened(path: Path):
        rows = original(path)
        if path.name == "starter-effectiveness.jsonl":
            for row in rows[:3]:
                row["observed"] = False
        return rows

    monkeypatch.setattr(governance, "load_ledger", weakened)
    with pytest.raises(governance.GovernanceError, match="recall below floor"):
        governance.validate(REPO_ROOT)

    monkeypatch.setattr(governance, "load_ledger", original)
    _assert_corpus_floor_is_declared_not_constant(monkeypatch)
    _assert_an_empty_declared_corpus_reports_unmeasured(monkeypatch)
    original_yaml = governance.load_yaml

    def drifted(path: Path):
        payload = original_yaml(path)
        if path.name == "corpus.yaml":
            payload["cases"][0]["patch_sha256"] = "0" * 64
        return payload

    monkeypatch.setattr(governance, "load_yaml", drifted)
    with pytest.raises(governance.GovernanceError, match="patch digest drifted"):
        governance.validate(REPO_ROOT)

    # A failure in an unmodified copy cannot count as mutation detection.
    fixture = tmp_path / "assay"
    fixture.mkdir()
    (fixture / "flag").write_text("good\n")
    (fixture / "alias").symlink_to("flag")
    patch = fixture / "defect.patch"
    patch.write_text("--- a/flag\n+++ b/flag\n@@ -1 +1 @@\n-good\n+bad\n")
    command = shlex.join(
        [
            sys.executable,
            "-c",
            "from pathlib import Path; assert Path('alias').is_symlink(); "
            "assert Path('alias').read_text() == 'good\\n'",
        ]
    )
    corpus = {
        "selection_frozen": True,
        "cases": [
            {
                "id": "copied-link",
                "class": "historical_defect",
                "patch": "defect.patch",
                "patch_sha256": hashlib.sha256(patch.read_bytes()).hexdigest(),
                "command": command,
                "owner": "fixture",
            }
        ],
    }
    monkeypatch.setattr(
        governance,
        "load_yaml",
        lambda path: (
            {"effectiveness_corpus": "corpus.yaml"}
            if path.name == "proof-estate.yaml"
            else copy.deepcopy(corpus)
        ),
    )
    rows = governance.assay(fixture)
    assert len(rows) == 1 and rows[0]["observed"] is True
    assert (fixture / "flag").read_text() == "good\n"
    (fixture / "alias").unlink()
    (fixture / "alias").write_text("good\n")
    with pytest.raises(governance.GovernanceError, match="assay baseline failed for copied-link"):
        governance.assay(fixture)


def test_lifecycle_replay_repairs_and_frozen_selection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = governance.load_yaml

    def unfrozen(path: Path):
        payload = original(path)
        if path.name == "corpus.yaml":
            payload["selection_frozen"] = False
        return payload

    monkeypatch.setattr(governance, "load_yaml", unfrozen)
    with pytest.raises(governance.GovernanceError, match="selection must be frozen"):
        governance.validate(REPO_ROOT)

    monkeypatch.setattr(governance, "load_yaml", original)
    original_ledger = governance.load_ledger
    lifecycle_mode = ["twice"]

    def broken_lifecycle(path: Path):
        rows = original_ledger(path)
        if path.name != "starter-reset.jsonl":
            return rows
        retirements = [row for row in rows if row.get("record_type") == "proof_retirement"]
        if lifecycle_mode[0] == "twice":
            return [*rows, copy.deepcopy(retirements[-1])]
        return [row for row in rows if row is not retirements[-1]]

    monkeypatch.setattr(governance, "load_ledger", broken_lifecycle)
    with pytest.raises(governance.GovernanceError, match="retired more than once"):
        governance.validate(REPO_ROOT)
    lifecycle_mode[0] = "missing"
    with pytest.raises(governance.GovernanceError, match="does not match inventory"):
        governance.validate(REPO_ROOT)

    repair_mode = ["active"]

    def repaired_lifecycle(path: Path):
        rows = original_ledger(path)
        if path.name != "starter-reset.jsonl":
            return rows
        retained = next(row for row in rows if row.get("disposition") == "retain")
        if repair_mode[0] == "reset":
            retained["disposition"] = "repair"
            return rows
        retired = next(row for row in rows if row.get("record_type") == "proof_retirement")
        target = retained if repair_mode[0] == "active" else retired
        repair = {**target, "record_type": "proof_repair", "disposition": "repair"}
        repair["replacement"] = target["proof_id"]
        return [*rows, repair]

    monkeypatch.setattr(governance, "load_ledger", repaired_lifecycle)
    summary = governance.validate(REPO_ROOT)
    assert summary["post_reset_repairs"] == 1
    repair_mode[0] = "reset"
    summary = governance.validate(REPO_ROOT)
    assert summary["dispositions"]["repair"] == 1
    repair_mode[0] = "retired"
    with pytest.raises(governance.GovernanceError, match="repair target is not active"):
        governance.validate(REPO_ROOT)


def test_changed_selection_maps_documents_to_readers_and_widens_on_unmapped_code(
    tmp_path: Path,
) -> None:
    def family(name: str, covers: str, tier: str = "changed") -> str:
        return (
            f"- id: {name}\n  tier: {tier}\n  kind: pytest\n"
            f"  selectors: [tests/test_{name}.py]\n  covers: [{covers}]\n"
            f"  source_paths: [tests/test_{name}.py]\n"
        )

    files = {
        "tests/proof-estate.yaml": "families:\n"
        + family("vital", "known/**", tier="vital")
        + family("mapped", "lib/example.py")
        + family("twin", "lib/twin.py")
        + family("twin2", "lib/twin.py")
        + family("tool", "bin/tool")
        + family("plans", "plan/**")
        + family("phases", "plan/*.md"),
        "known/file": "base\n",
        "lib/example.py": 'RULES = ROOT / "policies" / "read-by-code.md"\n',
        "lib/twin.py": "base\n",
        "tests/test_reader.py": 'assert "policies/read-by-test.md"\n',
        "bin/tool": "cat CLAUDE.md\n",
        "policies/read-by-code.md": "one\n",
        "policies/read-by-test.md": "one\n",
        "policies/read-by-nothing.md": "one\n",
        "CLAUDE.md": "one\n",
        "plan/phase-1.md": "one\n",
    }
    files["tests/proof-estate.yaml"] += family("reader", "lib/reader_only.py")
    for name, text in files.items():
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text(text)

    def git(*arguments: str) -> None:
        subprocess.run(["git", *arguments], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-q")
    git("config", "user.email", "test@example.invalid")
    git("config", "user.name", "Test")
    git("add", "-A")
    git("commit", "-qm", "base")

    def selection(*changed: str) -> tuple[set[str], str | None]:
        for path in changed:
            target = tmp_path / path
            target.write_text((target.read_text() if target.exists() else "") + "two\n")
        chosen, widened = governance.selected_families(tmp_path, "changed", "HEAD")
        git("reset", "-q", "--hard", "HEAD")
        git("clean", "-qfd")
        return {item["id"] for item in chosen}, widened

    # A document no family covers selects the families of the files that name it.
    assert selection("policies/read-by-code.md") == ({"vital", "mapped"}, None)
    assert selection("policies/read-by-test.md") == ({"vital", "reader"}, None)
    assert selection("CLAUDE.md") == ({"vital", "tool"}, None)
    assert selection("policies/read-by-nothing.md") == ({"vital"}, None)
    # A document several families cover selects all of them; ambiguously covered code widens.
    assert selection("plan/phase-1.md") == ({"vital", "plans", "phases"}, None)
    everything = {"vital", "mapped", "twin", "twin2", "tool", "plans", "phases", "reader"}
    assert selection("lib/twin.py") == (everything, "ambiguous-change-map:lib/twin.py")
    assert selection("policies/read-by-nothing.md", "unknown") == (
        everything,
        "unmapped-changes:unknown",
    )


def test_report_counts_the_frozen_baseline_and_current_estate() -> None:
    payload = governance.report(REPO_ROOT)
    assert payload["baseline"] == {"families": 541, "leaves": 690}
    assert payload["current"] == governance.inventory(REPO_ROOT)["counts"]


def _manifest_with(limits: dict[str, object]) -> dict[str, object]:
    manifest = copy.deepcopy(governance.load_yaml(REPO_ROOT / "tests/proof-estate.yaml"))
    manifest["effectiveness_floors"].update(limits)
    return manifest


def _patched_yaml(monkeypatch: pytest.MonkeyPatch, manifest, corpus=None) -> None:
    original_yaml = governance.load_yaml

    def patched(path: Path):
        if path.name == "proof-estate.yaml":
            return copy.deepcopy(manifest)
        if corpus is not None and path.name == "corpus.yaml":
            return copy.deepcopy(corpus)
        return original_yaml(path)

    monkeypatch.setattr(governance, "load_yaml", patched)


def _assert_corpus_floor_is_declared_not_constant(monkeypatch: pytest.MonkeyPatch) -> None:
    """A recipient declares its corpus floor; the estate must meet the number it declared."""
    with monkeypatch.context() as patch:
        _patched_yaml(patch, _manifest_with({"min_mutant_cases": 13}))
        with pytest.raises(governance.GovernanceError, match="below the declared floor of 13"):
            governance.validate(REPO_ROOT)
    with monkeypatch.context() as patch:
        _patched_yaml(patch, _manifest_with({"min_historical_cases": "twelve"}))
        with pytest.raises(governance.GovernanceError, match="min_historical_cases must be"):
            governance.validate(REPO_ROOT)


def _assert_an_empty_declared_corpus_reports_unmeasured(monkeypatch: pytest.MonkeyPatch) -> None:
    """A freshly stamped recipient has no defect history; that reads as unmeasured, not as zero."""
    original_ledger = governance.load_ledger
    with monkeypatch.context() as patch:
        _patched_yaml(
            patch,
            _manifest_with({"min_historical_cases": 0, "min_mutant_cases": 0}),
            corpus={"selection_frozen": True, "cases": []},
        )

        def empty_effectiveness(path: Path):
            if path.name.endswith("effectiveness.jsonl"):
                return []
            return original_ledger(path)

        patch.setattr(governance, "load_ledger", empty_effectiveness)
        summary = governance.validate(REPO_ROOT)
    assert summary["state"] == "valid"
    assert summary["recall"] == {}
    assert summary["recall_unmeasured"] == ["historical_defect", "holdout_mutant"]
