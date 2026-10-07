from __future__ import annotations

import copy
import hashlib
import json
import os
import shlex
import stat
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


EVIDENCE = {
    "contract": "The fixture contract holds.",
    "oracle": "A direct call observes the fixture outcome.",
    "red_witness": "Removing the behavior makes the proof fail.",
    "nearest_overlap": "None in this fixture.",
    "replacement_evidence": "The named replacement covers the same contract.",
    "rationale": "Fixture estate.",
}
SAMPLE = "pytest:tests/test_sample.py::"


def _proof(node: str) -> dict[str, str]:
    kind = node.split(":", 1)[0]
    selector = node.removeprefix("pytest:") if kind == "pytest" else node
    if kind == "gate":
        selector = node.removeprefix("gate:")
    family = governance._pytest_family(node) if kind == "pytest" else node
    source = {
        "pytest": selector.split("::", 1)[0],
        "gate": "bin/check:1",
        "hook": ".githooks/pre-commit:1",
    }[kind]
    return {"id": node, "family": family, "kind": kind, "selector": selector, "source_path": source}


def _write_estate(root: Path, *, pruned: bool) -> Path:
    """A whole small repository the manager can inventory, with its own reset history.

    Pruned, it is an estate with a past: a baseline proof deleted, one consolidated,
    one admitted later with its witness receipt, and one retired later. Unpruned, it is
    what a new repository has: every baseline proof retained and nothing yet witnessed.
    """
    files = {
        "tests/test_sample.py": (
            "import pytest\n\n\ndef test_kept():\n    pass\n\n\n"
            '@pytest.mark.parametrize("case", [1, 2])\ndef test_cases(case):\n    pass\n\n\n'
            "def test_admitted():\n    pass\n"
        ),
        "project/tests/test_product.py": "def test_product():\n    pass\n",
        "bin/check": "run_gate policy-sample ./bin/sample\n",
        ".githooks/pre-commit": "./bin/check-sample\n",
        "bin/python": f'#!/bin/sh\nexec {shlex.quote(sys.executable)} "$@"\n',
    }
    for name, text in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text)
    (root / "bin/python").chmod(0o755)

    live = [
        SAMPLE + "test_kept",
        SAMPLE + "test_cases[1]",
        SAMPLE + "test_cases[2]",
        "pytest:project/tests/test_product.py::test_product",
        "gate:policy-sample",
        "hook:.githooks/pre-commit:./bin/check-sample",
    ]
    admitted = SAMPLE + "test_admitted"
    gone = [SAMPLE + name for name in ("test_deleted", "test_folded", "test_retired")]
    proofs = [_proof(node) for node in ([*live, *gone] if pruned else [*live, admitted])]
    baseline: dict[str, object] = {
        "schema": governance.BASELINE_SCHEMA,
        "counts": {
            "families": len({proof["family"] for proof in proofs}),
            "leaves": len(proofs),
        },
        "proofs": proofs,
    }
    digest = hashlib.sha256(
        json.dumps(baseline, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    baseline["inventory_sha256"] = digest

    def row(record_type: str, node: str, disposition: str, replacement: str | None) -> dict:
        return {
            "record_type": record_type,
            "proof_id": node,
            "disposition": disposition,
            "replacement": replacement,
            "baseline_inventory_sha256": digest,
            **EVIDENCE,
        }

    ledger = [row("proof_disposition", node, "retain", node) for node in live]
    receipts: list[dict[str, object]] = []
    if pruned:
        deleted, folded, retired = gone
        ledger += [
            row("proof_disposition", deleted, "delete", None),
            row("proof_disposition", folded, "consolidate", live[0]),
            row("proof_disposition", retired, "retain", retired),
            row("proof_admission", admitted, "retain", admitted),
            row("proof_retirement", retired, "delete", None),
        ]
        receipts.append(
            {
                "record_type": "red_witness",
                "proof_ids": [admitted],
                "defect": "The admitted behavior is removed.",
                "command": "./bin/test tests/test_sample.py -q",
                "expect": "test_admitted",
                "paths": ["tests/test_sample.py"],
                "mutation_sha256": "0" * 64,
                "red_output_sha256": "1" * 64,
                "witnessed_on": "2026-01-01",
            }
        )
    else:
        ledger.append(row("proof_disposition", admitted, "retain", admitted))

    def family(name: str, kind: str, selector: str, source: str) -> dict[str, object]:
        declared: dict[str, object] = {
            "id": name,
            "kind": kind,
            "selectors": [selector],
            "source_paths": [source],
            "covers": [source],
            "contract": "The fixture contract holds.",
            "risk_class": "fixture",
            "oracle": "A direct call observes the fixture outcome.",
            "admission": "Fixture estate.",
            "nearest_overlap": "None in this fixture.",
            "tier": "changed",
            "flake_rate": 0.0,
            "replacement_lineage": [],
        }
        if kind == "pytest":
            declared["size"] = "small"
        return declared

    manifest = {
        "schema": governance.SCHEMA,
        "baseline_report": "reports/baseline.json",
        "audit_ledger": "reports/reset.jsonl",
        "witness_ledger": "reports/witnesses.jsonl",
        "mutation": {"tool": None, "reason": "The fixture declares no mutation tool."},
        "size_ceilings_seconds": {"small": 2, "medium": 20, "large": 200},
        "time_budget": {"test_lane_seconds": 10, "tolerance": 0.25, "reference_machine": None},
        "critical_risks": {
            "custody": {"state": "applicable", "direct_proof": live[0]},
            "deploy": {
                "state": "not-applicable",
                "rationale": "The fixture deploys nothing.",
                "activation_trigger": "A deploy surface is added.",
            },
        },
        "families": [
            family("sample", "pytest", "tests/test_sample.py", "tests/test_sample.py"),
            family(
                "product",
                "pytest",
                "project/tests/test_product.py",
                "project/tests/test_product.py",
            ),
            family("gates", "gate", "policy-sample", "bin/check"),
            family("hooks", "hook", "hook:.githooks/pre-commit:*", ".githooks/pre-commit"),
        ],
    }
    (root / "reports").mkdir()
    (root / "tests/proof-estate.yaml").write_text(json.dumps(manifest))
    (root / "reports/baseline.json").write_text(json.dumps(baseline))
    for name, rows in (("reset.jsonl", ledger), ("witnesses.jsonl", receipts)):
        (root / "reports" / name).write_text("".join(json.dumps(item) + "\n" for item in rows))
    return root


@pytest.fixture(scope="module")
def estate(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return _write_estate(tmp_path_factory.mktemp("estate"), pruned=True)


def test_inventory_counts_executable_families_and_expanded_leaves(estate: Path) -> None:
    observed = governance.inventory(estate)
    assert observed["counts"] == {"families": 6, "leaves": 7}
    assert observed["by_kind"]["pytest"] == {"families": 4, "leaves": 5}


def test_live_reset_validates(estate: Path, tmp_path: Path) -> None:
    summary = governance.validate(estate)
    assert summary["dispositions"] == {"retain": 7, "repair": 0, "consolidate": 1, "delete": 1}
    assert (summary["admissions"], summary["post_reset_retirements"]) == (1, 1)
    assert (summary["witness_receipts"], summary["unwitnessed_baseline"]) == (1, 6)
    # A new repository keeps every proof it was given and has witnessed nothing yet.
    fresh = governance.validate(_write_estate(tmp_path / "fresh", pruned=False))
    assert fresh["state"] == "valid"
    assert fresh["dispositions"] == {"retain": 7, "repair": 0, "consolidate": 0, "delete": 0}
    assert (fresh["witness_receipts"], fresh["unwitnessed_baseline"]) == (0, 7)
    # Last, because the live estate refuses while a red witness is pending in this checkout:
    # a defect planted to challenge this proof has to fail a fixture assertion above.
    assert governance.validate(REPO_ROOT)["state"] == "valid"


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
    estate: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = governance.load_ledger
    mode = ["missing"]

    def malformed(path: Path):
        rows = original(path)
        if path.name == "reset.jsonl":
            if mode[0] == "missing":
                rows.pop(0)
            else:
                rows[0] = {key: value for key, value in rows[0].items() if key != "oracle"}
        return rows

    monkeypatch.setattr(governance, "load_ledger", malformed)
    with pytest.raises(governance.GovernanceError, match="misses 1 baseline proofs"):
        governance.validate(estate)
    mode[0] = "evidence"
    with pytest.raises(governance.GovernanceError, match="wrong disposition fields"):
        governance.validate(estate)


def test_shadow_deleted_proof_fails_closed(estate: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    original = governance.load_ledger
    mode = ["delete"]

    def shadowed(path: Path):
        rows = original(path)
        if path.name == "reset.jsonl":
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
        governance.validate(estate)
    mode[0] = "replacement"
    with pytest.raises(governance.GovernanceError, match="invalid replacement"):
        governance.validate(estate)


def test_critical_risk_requires_a_retained_direct_proof(
    estate: Path,
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
        governance.validate(estate)


def test_lifecycle_replay_and_repairs(
    estate: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_ledger = governance.load_ledger
    lifecycle_mode = ["twice"]

    def broken_lifecycle(path: Path):
        rows = original_ledger(path)
        if path.name != "reset.jsonl":
            return rows
        retirements = [row for row in rows if row.get("record_type") == "proof_retirement"]
        if lifecycle_mode[0] == "twice":
            return [*rows, copy.deepcopy(retirements[-1])]
        return [row for row in rows if row is not retirements[-1]]

    monkeypatch.setattr(governance, "load_ledger", broken_lifecycle)
    with pytest.raises(governance.GovernanceError, match="retired more than once"):
        governance.validate(estate)
    lifecycle_mode[0] = "missing"
    with pytest.raises(governance.GovernanceError, match="does not match inventory"):
        governance.validate(estate)

    repair_mode = ["active"]

    def repaired_lifecycle(path: Path):
        rows = original_ledger(path)
        if path.name == "witnesses.jsonl" and repair_mode[0] != "unwitnessed":
            return [*rows, {**rows[0], "proof_ids": [SAMPLE + "test_kept"]}]
        if path.name != "reset.jsonl":
            return rows
        retained = next(row for row in rows if row.get("disposition") == "retain")
        if repair_mode[0] == "reset":
            retained["disposition"] = "repair"
            return rows
        retired = next(row for row in rows if row.get("record_type") == "proof_retirement")
        target = retired if repair_mode[0] == "retired" else retained
        repair = {**target, "record_type": "proof_repair", "disposition": "repair"}
        repair["replacement"] = target["proof_id"]
        return [*rows, repair]

    monkeypatch.setattr(governance, "load_ledger", repaired_lifecycle)
    summary = governance.validate(estate)
    assert summary["post_reset_repairs"] == 1
    repair_mode[0] = "reset"
    summary = governance.validate(estate)
    assert summary["dispositions"]["repair"] == 1
    repair_mode[0] = "retired"
    with pytest.raises(governance.GovernanceError, match="repair target is not active"):
        governance.validate(estate)
    # A repair is a new claim that the proof can fail, so it needs its own observation.
    repair_mode[0] = "unwitnessed"
    with pytest.raises(governance.GovernanceError, match="test_kept") as refused:
        governance.validate(estate)
    assert "admitted or repaired proof has no witness receipt" in str(refused.value)


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


def test_changed_code_selects_the_families_of_files_that_use_it(tmp_path: Path) -> None:
    def family(name: str, covers: str, tier: str = "changed") -> str:
        return (
            f"- id: {name}\n  tier: {tier}\n  kind: pytest\n"
            f"  selectors: [tests/test_{name}.py]\n  covers: [{covers}]\n"
            f"  source_paths: [tests/test_{name}.py]\n"
        )

    files = {
        "tests/proof-estate.yaml": "families:\n"
        + family("vital", "known/**", tier="vital")
        + family("helper", "lib/pkg/helper.py")
        + family("user", "lib/pkg/user.py")
        + family("bystander", "lib/pkg/bystander.py"),
        "known/file": "base\n",
        "lib/pkg/helper.py": "def shared():\n    return 1\n",
        "lib/pkg/user.py": "from pkg.helper import shared\n",
        "lib/pkg/bystander.py": "VALUE = 2\n",
        "tests/test_caller.py": "import pkg.helper\n",
    }
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
    (tmp_path / "lib/pkg/helper.py").write_text("def shared():\n    return 3\n")
    chosen, widened = governance.selected_families(tmp_path, "changed", "HEAD")
    # The module that imports the helper brings its family; the untouched bystander does not.
    assert ({item["id"] for item in chosen}, widened) == ({"vital", "helper", "user"}, None)


def test_report_counts_the_frozen_baseline_and_current_estate(estate: Path) -> None:
    payload = governance.report(estate)
    assert payload["baseline"] == {"families": 8, "leaves": 9}
    assert payload["current"] == {"families": 6, "leaves": 7}


def test_a_mutation_declaration_names_its_tool_scope_and_budget_or_says_why_not() -> None:
    measured = {"tool": "any-tool", "paths": ["lib/*.py"], "budget_seconds": 300}
    unmeasured = {"tool": None, "reason": "No tool is maintained for this language."}
    assert governance.mutation_errors({"mutation": measured}) == []
    assert governance.mutation_errors({"mutation": unmeasured}) == []
    refused = {
        "mutation must be a mapping": None,
        "carries only tool and reason": {**unmeasured, "paths": ["lib/*.py"]},
        "must say why no mutation tool is declared": {"tool": None, "reason": " "},
        "carries tool, paths and budget_seconds": {**measured, "reason": "extra"},
        "must be null or the name of the tool": {**measured, "tool": " "},
        "mutation.paths must be a nonempty list": {**measured, "paths": []},
        "mutation.budget_seconds must be a positive number": {**measured, "budget_seconds": 0},
    }
    for message, declared in refused.items():
        errors = governance.mutation_errors({"mutation": declared})
        assert len(errors) == 1 and message in errors[0], (message, errors)
    assert governance.mutation_errors({"mutation": {**measured, "budget_seconds": 1}}) == []
    # A missing field is refused as surely as an extra one.
    assert governance.mutation_errors({"mutation": {"tool": None}}) != []
    assert governance.mutation_errors({"mutation": {"tool": "any-tool", "paths": ["a"]}}) != []
    assert governance.mutation_errors({"mutation": {**measured, "budget_seconds": -1}}) != []
    assert governance.mutation_errors({"mutation": {**measured, "paths": [7]}}) != []
    assert governance.mutation_errors({"mutation": {**measured, "budget_seconds": True}}) != []


WITNESS = {
    "proof_ids": ["pytest:tests/test_sample.py::test_admitted"],
    "defect": "The guard allows instead of denying.",
    "expect": "GUARD OPEN",
    "command": "./check.sh",
    "paths": ["guard.txt"],
}


def _witness_repo(root: Path, guard: str = "deny\n", *, validates_itself: bool = False) -> Path:
    """A repository whose only proof is a shell script, so nothing here depends on pytest."""
    (root / "tests").mkdir(parents=True)
    (root / "tests/proof-estate.yaml").write_text(
        json.dumps({"witness_ledger": "reports/witnesses.jsonl"})
    )
    (root / "guard.txt").write_text(guard)
    (root / "guard.txt").chmod(0o640)
    # An old file, as real source usually is: begin has no fresh write to wait out.
    os.utime(root / "guard.txt", (0, 0))
    (root / "check.sh").write_text(
        '#!/bin/sh\ngrep -qx deny guard.txt || { echo "GUARD OPEN"; exit 1; }\n'
        + (
            # Like a proof that validates its own estate: green only with no witness pending.
            f"test ! -e {governance.WITNESS_PENDING}/request.json"
            ' || { echo "PENDING"; exit 1; }\n'
            if validates_itself
            else ""
        )
        + "echo checked\n"
    )
    (root / "check.sh").chmod(0o755)
    return root


def test_witness_observes_red_restores_exactly_and_records_a_receipt(tmp_path: Path) -> None:
    root = _witness_repo(tmp_path, validates_itself=True)
    governance.witness_begin(root, **WITNESS)
    (root / "guard.txt").write_text("allow\n")
    planted_second = int((root / "guard.txt").stat().st_mtime)
    receipt = governance.witness_finish(root)
    assert (root / "guard.txt").read_bytes() == b"deny\n"
    # A cache keyed on size and whole-second time must see the restored file as new.
    assert int((root / "guard.txt").stat().st_mtime) > planted_second
    assert not (root / governance.WITNESS_PENDING).exists()
    assert governance.load_ledger(root / "reports/witnesses.jsonl") == [receipt]
    assert receipt["paths"] == ["guard.txt"] and receipt["defect"] == WITNESS["defect"]
    assert governance._receipt_errors(receipt, 1, set(WITNESS["proof_ids"])) == []


def test_witness_refuses_anything_short_of_the_named_failure(tmp_path: Path) -> None:
    def attempt(name: str, *, guard: str = "deny\n", planted: str | None, **changed: str) -> Path:
        root = _witness_repo(tmp_path / name, guard)
        governance.witness_begin(root, **{**WITNESS, **changed})
        if planted is not None:
            (root / "guard.txt").write_text(planted)
        governance.witness_finish(root)
        return root

    refusals = {
        "the baseline is already red": (
            "baseline is not green",
            {"guard": "allow\n", "planted": None},
        ),
        "the expected text shows while green": (
            "already appears while the command passes",
            {"planted": None, "expect": "checked"},
        ),
        "nothing was planted": ("no journaled path has changed", {"planted": None}),
        "the mutant survives": (
            "NOT WITNESSED: the command still passed",
            {"planted": "deny\nextra\n"},
        ),
        "it fails for another reason": (
            "NOT WITNESSED: the command failed, but not with the expected text",
            {"planted": "allow\n", "expect": "A DIFFERENT GUARD"},
        ),
    }
    for number, (reason, (message, arguments)) in enumerate(refusals.items()):
        root = tmp_path / str(number)
        with pytest.raises(governance.GovernanceError, match=message):
            attempt(str(number), **arguments)
        assert (root / "guard.txt").read_text() == arguments.get("guard", "deny\n"), reason
        assert not (root / "reports/witnesses.jsonl").exists(), reason


def test_a_pending_witness_blocks_validation_until_it_is_aborted(tmp_path: Path) -> None:
    root = _witness_repo(tmp_path)
    governance.witness_begin(root, **WITNESS)
    # The planted defect here is the file's removal, as an interrupted run would leave it.
    (root / "guard.txt").unlink()
    with pytest.raises(governance.GovernanceError, match="a red witness is pending"):
        governance.validate(root)
    with pytest.raises(governance.GovernanceError, match="a red witness is pending"):
        governance.witness_begin(root, **WITNESS)
    assert governance.witness_abort(root) == {"state": "aborted", "restored": ["guard.txt"]}
    assert (root / "guard.txt").read_bytes() == b"deny\n"
    assert stat.S_IMODE((root / "guard.txt").stat().st_mode) == 0o640
    assert not (root / governance.WITNESS_PENDING).exists()
    with pytest.raises(governance.GovernanceError, match="no red witness is pending"):
        governance.witness_abort(root)


def test_receipts_are_validated_and_an_admitted_proof_must_have_one(
    estate: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = governance.load_ledger
    change: list[object] = [None]

    def altered(path: Path):
        rows = original(path)
        if path.name == "witnesses.jsonl":
            return change[0](rows)
        return rows

    monkeypatch.setattr(governance, "load_ledger", altered)
    change[0] = lambda rows: []
    with pytest.raises(governance.GovernanceError, match="test_admitted") as refused:
        governance.validate(estate)
    assert "admitted or repaired proof has no witness receipt" in str(refused.value)
    malformed = {
        "has wrong fields": lambda row: row.pop("expect"),
        "names a proof the audit ledger does not know": lambda row: row.update(
            proof_ids=["pytest:absent"]
        ),
        "has no witness date": lambda row: row.update(witnessed_on="last week"),
        "mutation_sha256 must be a SHA-256 digest": lambda row: row.update(mutation_sha256="0"),
    }
    for message, damage in malformed.items():

        def damaged(rows, damage=damage):
            damage(rows[0])
            return rows

        change[0] = damaged
        with pytest.raises(governance.GovernanceError, match=message):
            governance.validate(estate)
