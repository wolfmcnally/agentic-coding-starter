from __future__ import annotations

import copy
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
    assert observed["counts"] == {"families": 108, "leaves": 126}
    assert observed["by_kind"]["pytest"] == {"families": 87, "leaves": 105}


def test_live_reset_validates() -> None:
    summary = governance.validate(REPO_ROOT)
    assert summary["state"] == "valid"
    assert summary["dispositions"]["delete"] > 0
    assert summary["dispositions"]["consolidate"] > 0


def test_family_or_leaf_cap_overrun_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = governance.inventory(REPO_ROOT)
    over = copy.deepcopy(original)
    over["counts"]["families"] = 109
    monkeypatch.setattr(governance, "inventory", lambda _root: over)
    with pytest.raises(governance.GovernanceError, match="families cap exceeded"):
        governance.validate(REPO_ROOT)
    over["counts"]["families"] = 108
    over["counts"]["leaves"] = 139
    with pytest.raises(governance.GovernanceError, match="leaves cap exceeded"):
        governance.validate(REPO_ROOT)


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
    original_yaml = governance.load_yaml

    def drifted(path: Path):
        payload = original_yaml(path)
        if path.name == "corpus.yaml":
            payload["cases"][0]["patch_sha256"] = "0" * 64
        return payload

    monkeypatch.setattr(governance, "load_yaml", drifted)
    with pytest.raises(governance.GovernanceError, match="patch digest drifted"):
        governance.validate(REPO_ROOT)


def test_positive_growth_requires_named_approval(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = governance.load_yaml
    mode = ["budget"]

    def unapproved(path: Path):
        payload = original(path)
        if path.name == "proof-estate.yaml":
            payload["test_budget_delta"]["families"] = 1
            payload.pop("budget_approval", None)
        elif path.name == "corpus.yaml" and mode[0] == "selection":
            payload["selection_frozen"] = False
        return payload

    monkeypatch.setattr(governance, "load_yaml", unapproved)
    with pytest.raises(governance.GovernanceError, match="positive families budget"):
        governance.validate(REPO_ROOT)
    mode[0] = "selection"
    with pytest.raises(governance.GovernanceError, match="selection must be frozen"):
        governance.validate(REPO_ROOT)

    monkeypatch.setattr(governance, "load_yaml", original)
    original_ledger = governance.load_ledger
    lifecycle_mode = ["missing"]

    def broken_lifecycle(path: Path):
        rows = original_ledger(path)
        if path.name != "starter-reset.jsonl":
            return rows
        retirements = [row for row in rows if row.get("record_type") == "proof_retirement"]
        admissions = [row for row in rows if row.get("record_type") == "proof_admission"]
        if lifecycle_mode[0] == "missing":
            target = retirements[-1]["proof_id"]
            return [
                row
                for row in rows
                if not (
                    row.get("record_type") == "proof_retirement" and row.get("proof_id") == target
                )
            ]
        admissions[-1]["compensating_retirement"] = retirements[0]["proof_id"]
        return rows

    monkeypatch.setattr(governance, "load_ledger", broken_lifecycle)
    with pytest.raises(governance.GovernanceError, match="lacks an available retirement"):
        governance.validate(REPO_ROOT)
    lifecycle_mode[0] = "reuse"
    with pytest.raises(governance.GovernanceError, match="retirement budget is reused"):
        governance.validate(REPO_ROOT)


def test_changed_selection_widens_on_an_unmapped_path(tmp_path: Path) -> None:
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests/proof-estate.yaml").write_text(
        "families:\n"
        "- id: retained\n"
        "  tier: vital\n"
        "  kind: pytest\n"
        "  selectors: [tests/test_x.py]\n"
        "  covers: [known/**]\n"
        "  source_paths: [tests/test_x.py]\n"
    )
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.invalid"],
        cwd=tmp_path,
        check=True,
    )
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    (tmp_path / "known").mkdir()
    (tmp_path / "known/file").write_text("base")
    subprocess.run(
        ["git", "add", "known/file", "tests/proof-estate.yaml"],
        cwd=tmp_path,
        check=True,
    )
    subprocess.run(["git", "commit", "-qm", "base"], cwd=tmp_path, check=True)
    (tmp_path / "unknown").write_text("change")
    families, reason = governance.selected_families(tmp_path, "changed", "HEAD")
    assert reason == "unmapped-changes:unknown"
    assert [family["id"] for family in families] == ["retained"]


def test_report_reproduces_reset_ratios() -> None:
    payload = governance.report(REPO_ROOT)
    assert payload["baseline"] == {"families": 541, "leaves": 690}
    assert payload["current"] == {"families": 108, "leaves": 126}
    assert payload["family_ratio"] < 0.2
    assert payload["leaf_ratio"] < 0.2
