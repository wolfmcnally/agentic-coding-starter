from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "lib"))

from agentic_starter.test_governance import (  # noqa: E402
    GovernanceError,
    load_estate,
    select_estate,
    validate_estate,
)


def _family(
    family_id: str,
    selector: str,
    *,
    vital: bool,
    source_paths: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "id": family_id,
        "kind": "pytest",
        "selectors": [selector],
        "source_paths": source_paths or ["src/shared.py"],
        "covers": f"Fixture proofs owned by {family_id}.",
        "contract": "The fixture behavior remains observable.",
        "risk_class": "fixture-contract",
        "oracle": "Pytest exits zero only when the fixture expectation holds.",
        "tiers": ["full", "vital"] if vital else ["full"],
        "runner": {"kind": "pytest", "selectors": [selector]},
        "admission": (
            {
                "red_witness": "The fixture test fails when its expected value is inverted.",
                "nearest_overlap": "The neighboring family owns a different test file.",
                "distinct_value": "This family guards the manager's own fail-closed behavior.",
            }
            if vital
            else {
                "state": "full-only",
                "reason": "Not admitted to the fixture fast lane.",
            }
        ),
        "historical_evidence": ["fixture-historical"] if vital else [],
        "mutation_evidence": ["fixture-holdout"] if vital else [],
    }


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(f"{json.dumps(record, sort_keys=True)}\n" for record in records))


def _fixture_estate(tmp_path: Path, *, two_families: bool = False):
    root = tmp_path / "repo"
    (root / "tests").mkdir(parents=True)
    (root / "bin").mkdir()
    (root / ".githooks").mkdir()
    (root / "reports").mkdir()
    (root / "src").mkdir()
    (root / "src" / "shared.py").write_text("VALUE = 1\n")
    (root / "tests" / "test_alpha.py").write_text(
        "def test_first():\n    assert True\n\ndef test_second():\n    assert True\n"
    )
    families = [_family("alpha", "tests/test_alpha.py", vital=True)]
    definitions = 2
    if two_families:
        (root / "tests" / "test_beta.py").write_text("def test_third():\n    assert True\n")
        families.append(_family("beta", "tests/test_beta.py", vital=False))
        definitions += 1
    (root / "bin" / "check").write_text("#!/usr/bin/env bash\nrun_gate test ./bin/test\n")
    (root / ".githooks" / "pre-commit").write_text(
        "#!/usr/bin/env bash\n./bin/test-governance validate\n"
    )
    (root / "reports" / "audit.jsonl").write_text("")

    manifest = {
        "schema_version": 1,
        "inventory": {
            "test_roots": ["tests"],
            "gate_files": ["bin/check"],
            "hook_files": [".githooks/pre-commit"],
            "candidate_paths": ["bin/check", "src/shared.py"],
        },
        "baseline": {
            "test_files": 2 if two_families else 1,
            "test_definitions": definitions,
            "check_gates": 1,
            "hook_commands": 1,
        },
        "surfaces": {
            "check_gates": ["test"],
            "hook_commands": ["./bin/test-governance validate"],
        },
        "families": families,
        "audit": {"ledger_file": "reports/audit.jsonl"},
        "reports": {
            "baseline_file": "reports/baseline.json",
            "selection_file": "reports/selection.json",
            "timing_file": "reports/timing.json",
        },
        "effectiveness": {
            "evidence_file": "reports/effectiveness.jsonl",
            "required_classes": ["historical_defect", "holdout_mutant"],
        },
    }
    manifest_path = root / "tests" / "proof-estate.yaml"
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False))
    estate = load_estate(root, manifest_path)
    (root / "reports" / "baseline.json").write_text(
        json.dumps(
            {
                "record_type": "proof-estate-baseline",
                "schema_version": 1,
                "candidate_sha256": estate.candidate_sha256,
                "manifest_sha256": estate.manifest_sha256,
                "inventory_sha256": estate.inventory_sha256,
                "counts": estate.inventory["counts"],
            }
        )
    )
    vital_families = sorted(family["id"] for family in families if "vital" in family["tiers"])
    vital_selectors = sorted(
        {
            selector
            for family in families
            if "vital" in family["tiers"]
            for selector in family["runner"]["selectors"]
        }
    )
    (root / "reports" / "selection.json").write_text(
        json.dumps(
            {
                "record_type": "selection",
                "lane": "vital" if vital_families else "full-only",
                "reason": "fixture selection state",
                "candidate_sha256": estate.candidate_sha256,
                "manifest_sha256": estate.manifest_sha256,
                "inventory_sha256": estate.inventory_sha256,
                "families": vital_families,
                "selectors": vital_selectors,
            }
        )
    )
    (root / "reports" / "timing.json").write_text(
        json.dumps(
            {
                "record_type": "local-timing-observations",
                "candidate_sha256": estate.candidate_sha256,
                "manifest_sha256": estate.manifest_sha256,
                "inventory_sha256": estate.inventory_sha256,
                "measurements": [],
                "universal_budget": None,
            }
        )
    )
    records = []
    for evidence_class, evidence_id in (
        ("historical_defect", "fixture-historical"),
        ("holdout_mutant", "fixture-holdout"),
    ):
        records.append(
            {
                "record_type": "effectiveness",
                "evidence_class": evidence_class,
                "evidence_id": evidence_id,
                "candidate_sha256": estate.candidate_sha256,
                "manifest_sha256": estate.manifest_sha256,
                "inventory_sha256": estate.inventory_sha256,
                "command": f"fixture assay {evidence_id}",
                "expected": "the malformed estate is rejected",
                "observed": "the malformed estate was rejected",
                "detected": True,
                "detected_by": ["alpha"],
                "output_sha256": "0" * 64,
                "denominator": 1,
            }
        )
    _write_jsonl(root / "reports" / "effectiveness.jsonl", records)
    return load_estate(root, manifest_path)


def _rewrite_manifest(estate, mutation) -> Any:
    manifest = yaml.safe_load(estate.manifest_path.read_text())
    mutation(manifest)
    estate.manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False))
    return load_estate(estate.root, estate.manifest_path)


def test_valid_estate_accounts_for_every_proof_and_surface(tmp_path: Path) -> None:
    estate = _fixture_estate(tmp_path)

    summary = validate_estate(estate)

    assert summary["counts"] == {
        "test_files": 1,
        "test_definitions": 2,
        "check_gates": 1,
        "hook_commands": 1,
    }
    assert summary["families"] == 1
    assert summary["vital_families"] == 1


def test_missing_proof_claim_fails_closed(tmp_path: Path) -> None:
    estate = _fixture_estate(tmp_path)
    estate = _rewrite_manifest(
        estate,
        lambda manifest: manifest["families"][0].update(
            {
                "selectors": ["tests/test_alpha.py::test_first"],
                "runner": {
                    "kind": "pytest",
                    "selectors": ["tests/test_alpha.py::test_first"],
                },
            }
        ),
    )

    with pytest.raises(GovernanceError, match="proof ownership invalid"):
        validate_estate(estate)


def test_unsupported_fast_lane_runner_fails_closed(tmp_path: Path) -> None:
    estate = _fixture_estate(tmp_path)
    estate = _rewrite_manifest(
        estate,
        lambda manifest: manifest["families"][0]["runner"].update({"kind": "shell"}),
    )

    with pytest.raises(GovernanceError, match="unsupported runner"):
        validate_estate(estate)


def test_stale_baseline_fails_closed(tmp_path: Path) -> None:
    estate = _fixture_estate(tmp_path)
    (estate.root / "tests" / "test_late.py").write_text("def test_late():\n    assert True\n")
    estate = load_estate(estate.root, estate.manifest_path)

    with pytest.raises(GovernanceError, match="baseline is stale"):
        validate_estate(estate)


def test_stale_effectiveness_binding_fails_closed(tmp_path: Path) -> None:
    estate = _fixture_estate(tmp_path)
    evidence_path = estate.root / "reports" / "effectiveness.jsonl"
    records = [json.loads(line) for line in evidence_path.read_text().splitlines()]
    records[0]["inventory_sha256"] = "f" * 64
    _write_jsonl(evidence_path, records)

    with pytest.raises(GovernanceError, match="stale inventory_sha256"):
        validate_estate(estate)


def test_stale_audit_binding_fails_closed(tmp_path: Path) -> None:
    estate = _fixture_estate(tmp_path)
    _write_jsonl(
        estate.root / "reports" / "audit.jsonl",
        [
            {
                "record_type": "estate_disposition",
                "evidence_id": "fixture-retention",
                "candidate_sha256": estate.candidate_sha256,
                "manifest_sha256": estate.manifest_sha256,
                "inventory_sha256": "f" * 64,
                "disposition": "retain",
                "denominator_type": "test_definitions",
                "denominator": 2,
                "rationale": "The fixture retains both proofs.",
            }
        ],
    )

    with pytest.raises(GovernanceError, match="audit fixture-retention has stale"):
        validate_estate(estate)


def test_full_only_estate_requires_no_borrowed_effectiveness_corpus(
    tmp_path: Path,
) -> None:
    estate = _fixture_estate(tmp_path)

    def make_full_only(manifest: dict[str, Any]) -> None:
        family = manifest["families"][0]
        family["tiers"] = ["full"]
        family["admission"] = {
            "state": "full-only",
            "reason": "The recipient has not run its local assay.",
        }
        family["historical_evidence"] = []
        family["mutation_evidence"] = []

    estate = _rewrite_manifest(estate, make_full_only)
    (estate.root / "reports" / "effectiveness.jsonl").write_text("")
    for report_name in ("baseline.json", "timing.json"):
        report_path = estate.root / "reports" / report_name
        report = json.loads(report_path.read_text())
        report["candidate_sha256"] = estate.candidate_sha256
        report["manifest_sha256"] = estate.manifest_sha256
        report["inventory_sha256"] = estate.inventory_sha256
        report_path.write_text(json.dumps(report))
    selection_path = estate.root / "reports" / "selection.json"
    selection = json.loads(selection_path.read_text())
    selection.update(
        {
            "lane": "full-only",
            "candidate_sha256": estate.candidate_sha256,
            "manifest_sha256": estate.manifest_sha256,
            "inventory_sha256": estate.inventory_sha256,
            "families": [],
            "selectors": [],
        }
    )
    selection_path.write_text(json.dumps(selection))

    summary = validate_estate(estate)

    assert summary["vital_families"] == 0


def test_changed_selection_unions_every_legitimate_mapping(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    estate = _fixture_estate(tmp_path, two_families=True)
    monkeypatch.setattr(
        "agentic_starter.test_governance._changed_paths",
        lambda _root, _reference: ["src/shared.py"],
    )

    selection = select_estate(estate, tier=None, changed_from="HEAD")

    assert selection["mode"] == "focused"
    assert selection["families"] == ["alpha", "beta"]
    assert selection["selectors"] == ["tests/test_alpha.py", "tests/test_beta.py"]


def test_unmapped_changed_path_widens_to_full(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    estate = _fixture_estate(tmp_path)
    monkeypatch.setattr(
        "agentic_starter.test_governance._changed_paths",
        lambda _root, _reference: ["src/unmapped.py"],
    )

    selection = select_estate(estate, tier=None, changed_from="HEAD")

    assert selection["mode"] == "full"
    assert "unmapped" in selection["reason"]


def test_live_repository_estate_validates() -> None:
    result = subprocess.run(
        [str(REPO_ROOT / "bin" / "test-governance"), "validate"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "TEST GOVERNANCE PASS" in result.stdout


@pytest.mark.skipif(
    "TEST_GOVERNANCE_ASSAY_CASE" not in os.environ,
    reason="effectiveness holdouts run only in the explicit assay",
)
def test_external_effectiveness_assay_case(tmp_path: Path) -> None:
    case_name = os.environ["TEST_GOVERNANCE_ASSAY_CASE"]
    fixture_path = REPO_ROOT / "tests" / "fixtures" / "test_governance" / f"{case_name}.json"
    case = json.loads(fixture_path.read_text())
    estate = _fixture_estate(tmp_path)

    if case["mutation"] == "omit-proof-claim":
        estate = _rewrite_manifest(
            estate,
            lambda manifest: manifest["families"][0].update(
                {
                    "selectors": ["tests/test_alpha.py::test_first"],
                    "runner": {
                        "kind": "pytest",
                        "selectors": ["tests/test_alpha.py::test_first"],
                    },
                }
            ),
        )
    elif case["mutation"] == "unsupported-runner":
        estate = _rewrite_manifest(
            estate,
            lambda manifest: manifest["families"][0]["runner"].update({"kind": "shell"}),
        )
    else:
        pytest.fail(f"unknown assay mutation: {case['mutation']}")

    with pytest.raises(GovernanceError, match=case["expected_error"]):
        validate_estate(estate)
    print(f"ASSAY DETECTED {case_name}")
