from __future__ import annotations

import copy
import hashlib
import json
import os
import shlex
import stat
import subprocess
import sys
import tempfile
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
        return declared

    manifest = {
        "schema": governance.SCHEMA,
        "baseline_report": "reports/baseline.json",
        "audit_ledger": "reports/reset.jsonl",
        "witness_ledger": "reports/witnesses.jsonl",
        "mutation": {"tool": None, "reason": "The fixture declares no mutation tool."},
        "adoption": {"mode": "complete"},
        "hang_timeout_seconds": 1800,
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
def estate():
    storage = REPO_ROOT / ".kickoff/proof-runtime"
    storage.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="estate-", dir=storage) as directory:
        yield _write_estate(Path(directory), pruned=True)


def test_inventory_counts_executable_families_and_expanded_leaves(estate: Path) -> None:
    observed = governance.inventory(estate)
    assert observed["counts"] == {"families": 6, "leaves": 7}
    assert observed["by_kind"]["pytest"] == {"families": 4, "leaves": 5}


def test_live_reset_validates(estate: Path, tmp_path: Path) -> None:
    summary = governance.validate(estate)
    assert summary["dispositions"] == {"retain": 7, "repair": 0, "consolidate": 1, "delete": 1}
    assert (summary["admissions"], summary["post_reset_retirements"]) == (1, 1)
    assert (summary["witness_receipts"], summary["unwitnessed_baseline"]) == (1, 6)
    status, _ = governance._witness_run("/usr/bin/true", estate)
    assert status == 0
    capture_root = estate / ".kickoff/witness/captures"
    digest = governance.load_ledger(capture_root / "index.jsonl")[0]["sha256"]
    stored = capture_root / "retained-artifacts" / digest
    original = stored.read_bytes()
    assert governance.validate(estate)["state"] == "valid"
    for changed in (b"altered observation", None):
        if changed is None:
            stored.unlink()
        else:
            stored.write_bytes(changed)
        refused = False
        try:
            governance.validate(estate)
        except governance.GovernanceError as exc:
            refused = "witness capture invalid" in str(exc)
        assert refused, "DURABILITY WITNESS CORRUPTION ACCEPTED"
    stored.write_bytes(original)
    assert governance.validate(estate)["state"] == "valid"
    # A new repository keeps every proof it was given and has witnessed nothing yet.
    fresh = governance.validate(_write_estate(tmp_path / "fresh", pruned=False))
    assert fresh["state"] == "valid"
    assert fresh["dispositions"] == {"retain": 7, "repair": 0, "consolidate": 0, "delete": 0}
    assert (fresh["witness_receipts"], fresh["unwitnessed_baseline"]) == (0, 7)
    # Last, because the live estate refuses while a red witness is pending in this checkout:
    # a defect planted to challenge this proof has to fail a fixture assertion above.
    assert governance.validate(REPO_ROOT)["state"] == "valid"


def test_runtime_is_diagnostic_and_stale_records_are_unmeasured(
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
        "families": [{"id": "x", "kind": "pytest", "selectors": ["tests/test_x.py"]}],
        "adoption": {"mode": "complete"},
        "hang_timeout_seconds": 1800,
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

    # Large elapsed times remain diagnostic, with no hidden confirming reruns.
    def no_automatic_run(*args, **kwargs):
        pytest.fail("timing must read existing data without running tests")

    monkeypatch.setattr(governance, "_run", no_automatic_run)

    assert governance.timing(tmp_path)["state"] == "unmeasured", "missing timing must be unmeasured"
    assert governance.timing(tmp_path)["reason"] == "no full-run timing record", (
        "missing timing must explain the missing record"
    )
    recorded(8.0, 1.5)
    observed = governance.timing(tmp_path)
    assert observed["state"] == "measured", "ordinary runtime is diagnostic"
    assert observed["slowest"][0] == {"proof": f"pytest:{slow}", "seconds": 1.5}, (
        "report the observed leaf duration"
    )

    recorded(9999.0, 2500.0)
    slow_report = governance.timing(tmp_path)
    assert slow_report["state"] == "measured", "slow runtime must remain diagnostic"
    assert slow_report["test_lane_seconds"] == 9999.0, "report the observed suite duration"

    # A record from a different estate is stale, not a measurement.
    recorded(1.0, 0.1, cases=("fast", "slow", "gone"))
    assert governance.timing(tmp_path)["state"] == "unmeasured", "stale timing must be unmeasured"
    assert governance.timing(tmp_path)["reason"] == (
        "the timing record predates the current pytest estate"
    ), "stale timing must explain the inventory mismatch"
    recorded(1.0, 0.1, cases=("fast",))
    assert governance.timing(tmp_path)["state"] == "unmeasured", "partial timing must be unmeasured"
    manifest["hang_timeout_seconds"] = float("nan")
    with pytest.raises(governance.GovernanceError, match="finite and positive"):
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


def test_witness_observes_red_restores_exactly_and_records_a_receipt(
    tmp_path: Path,
) -> None:
    root = _witness_repo(tmp_path, validates_itself=True)
    check = root / "check.sh"
    check.write_text(check.read_text().replace("exit 1", "exit 101"))
    governance.witness_begin(root, failure_exit=101, **WITNESS)
    (root / "guard.txt").write_text("allow\n")
    planted_second = int((root / "guard.txt").stat().st_mtime)
    receipt = governance.witness_finish(root)
    assert (root / "guard.txt").read_bytes() == b"deny\n"
    # A cache keyed on size and whole-second time must see the restored file as new.
    assert int((root / "guard.txt").stat().st_mtime) > planted_second
    assert not (root / governance.WITNESS_PENDING).exists()
    assert governance.load_ledger(root / "reports/witnesses.jsonl") == [receipt]
    capture_root = root / ".kickoff/witness/captures"
    captures = [
        json.loads((capture_root / "retained-artifacts" / row["sha256"]).read_text())
        for row in governance.load_ledger(capture_root / "index.jsonl")
    ]
    assert [item["exit_code"] for item in captures].count(0) == 2, (
        "DURABILITY WITNESS CAPTURE LOST RED STATUS"
    )
    red = [item for item in captures if item["exit_code"] == 101]
    assert (
        len(red) == 1
        and hashlib.sha256(red[0]["output"].encode()).hexdigest() == receipt["red_output_sha256"]
    ), "DURABILITY WITNESS CAPTURE LOST RED STATUS"
    assert (
        receipt["paths"] == ["guard.txt"]
        and receipt["defect"] == "Completed failure exit 101: " + WITNESS["defect"]
    )
    assert governance._receipt_errors(receipt, 1, set(WITNESS["proof_ids"])) == []

    with pytest.raises(governance.GovernanceError, match="failure-exit must identify"):
        governance.witness_begin(root, failure_exit=124, **WITNESS)
    with tempfile.TemporaryDirectory() as temporary:
        with pytest.raises(governance.GovernanceError, match="temporary storage"):
            governance._witness_run("/usr/bin/true", Path(temporary))


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


def test_witness_expect_must_appear_in_a_declared_failure_line(tmp_path: Path) -> None:
    """An echoed assertion message cannot witness a run that failed for another reason."""

    def attempt(name: str, failure: str) -> Path:
        root = _witness_repo(tmp_path / name)
        (root / "tests/proof-estate.yaml").write_text(
            json.dumps(
                {"witness_ledger": "reports/witnesses.jsonl", "witness_failure_lines": "^E "}
            )
        )
        (root / "check.sh").write_text(
            "#!/bin/sh\n"
            "grep -qx deny guard.txt || {\n"
            "  echo '>       assert guard, \"GUARD OPEN\"'\n"
            f"  echo '{failure}'\n"
            "  exit 1\n"
            "}\n"
            "echo checked\n"
        )
        governance.witness_begin(root, **WITNESS)
        (root / "guard.txt").write_text("allow\n")
        governance.witness_finish(root)
        return root

    refused = False
    try:
        attempt("echoed", "E       ValueError: guard is not in list")
    except governance.GovernanceError as exc:
        refused = "outside the declared failure lines" in str(exc)
    assert refused, "WITNESS ACCEPTED AN ECHOED MESSAGE"

    root = attempt("failed", "E       AssertionError: GUARD OPEN")
    assert len(governance.load_ledger(root / "reports/witnesses.jsonl")) == 1

    bad = _witness_repo(tmp_path / "bad")
    (bad / "tests/proof-estate.yaml").write_text(
        json.dumps({"witness_ledger": "reports/witnesses.jsonl", "witness_failure_lines": "("})
    )
    governance.witness_begin(bad, **WITNESS)
    (bad / "guard.txt").write_text("allow\n")
    with pytest.raises(governance.GovernanceError, match="not a valid regular expression"):
        governance.witness_finish(bad)


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


def test_bounded_adoption_reports_pending_without_discarding_proofs(
    estate: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original_yaml, original_ledger, original_inventory = (
        governance.load_yaml,
        governance.load_ledger,
        governance.inventory,
    )
    step = [0]
    kept, case = SAMPLE + "test_kept", SAMPLE + "test_cases[1]"
    keeper = SAMPLE + "test_cases[2]"

    def bounded(path):
        result = original_yaml(path)
        result["adoption"] = {
            "mode": "complete" if step[0] == 4 else "bounded",
            "reason": "One named fixture contract per batch.",
        }
        if step[0] >= 2:
            result["critical_risks"]["custody"]["direct_proof"] = keeper
        return result

    def progression(path):
        rows = original_ledger(path)
        if path.name == "witnesses.jsonl":
            return rows + [{**rows[0], "proof_ids": [kept]}]
        if path.name != "reset.jsonl":
            return rows
        retained = [
            r
            for r in rows
            if r["record_type"] == "proof_disposition" and r["disposition"] == "retain"
        ]
        result = [r for r in rows if r not in retained]
        source = next(r for r in retained if r["proof_id"] == kept)
        if step[0] >= 1:
            result.append(
                {
                    **source,
                    "record_type": "proof_modification",
                    "disposition": "repair",
                    "witness_receipts": [2],
                }
            )
        if step[0] >= 2:
            result.append({**source, "disposition": "consolidate", "replacement": keeper})
        if step[0] >= 3:
            result.append(
                {
                    **source,
                    "record_type": "proof_retirement",
                    "proof_id": case,
                    "disposition": "consolidate",
                    "replacement": keeper,
                }
            )
        if step[0] == 4:
            retired = {r["proof_id"] for r in result if r["record_type"] == "proof_retirement"}
            result.extend(r for r in retained if r["proof_id"] not in retired | {kept})
        return result

    def live(root):
        result = original_inventory(root)
        removed = ({kept} if step[0] >= 2 else set()) | ({case} if step[0] >= 3 else set())
        result["proofs"] = [r for r in result["proofs"] if r["id"] not in removed]
        return result

    monkeypatch.setattr(governance, "load_yaml", bounded)
    monkeypatch.setattr(governance, "load_ledger", progression)
    monkeypatch.setattr(governance, "inventory", live)
    for stage, pending in enumerate((6, 6, 5, 4, 0)):
        step[0] = stage
        assert governance.validate(estate)["pending_baseline_review"] == pending, (
            f"pending review count at batch {stage}"
        )


def test_modification_must_reference_its_own_unreused_observation(
    estate: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = governance.load_ledger
    mode = ["valid"]

    def modified(path):
        rows = original(path)
        if path.name == "reset.jsonl":
            admission = next(row for row in rows if row["record_type"] == "proof_admission")
            event = {
                **admission,
                "record_type": "proof_modification",
                "disposition": "repair",
                "witness_receipts": [1],
            }
            rows.append(event)
            if mode[0] == "reused":
                rows.append(dict(event))
            elif mode[0] == "absent":
                event["witness_receipts"] = []
            elif mode[0] == "wrong":
                event["witness_receipts"] = [999]
            elif mode[0] == "other-proof":
                event["witness_receipts"] = [2]
        elif path.name == "witnesses.jsonl":
            rows.append({**rows[0], "proof_ids": [SAMPLE + "test_kept"]})
        return rows

    monkeypatch.setattr(governance, "load_ledger", modified)
    # Successful status shape is already proved by test_live_reset_validates.
    governance.validate(estate)

    def refuses(value: str, message: str) -> None:
        mode[0] = value
        try:
            governance.validate(estate)
        except governance.GovernanceError as exc:
            assert message in str(exc), f"wrong refusal for {value}"
        else:
            pytest.fail(f"modification incorrectly accepted {value}")

    refuses("reused", "reuses an earlier")
    refuses("absent", "needs witness")
    refuses("wrong", "invalid witness")
    refuses("other-proof", "does not witness its proof")


def test_hang_supervision_preserves_failures_and_stops_chattering_children(tmp_path: Path) -> None:
    import os
    import sys
    import time

    from agentic_starter.test_runner import run_command

    failed = run_command(
        [sys.executable, "-c", "print('expected assertion'); raise SystemExit(1)"],
        cwd=tmp_path,
        capture=True,
    )
    assert failed.returncode == 1, "completed failure status must survive"
    assert "expected assertion" in failed.stdout, "completed failure output must survive"
    child_pid = tmp_path / "child.pid"
    child = "import signal,time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(30)"
    code = (
        "import subprocess,sys,time,pathlib; "
        f"p=subprocess.Popen([sys.executable,'-c',{child!r}]); "
        f"pathlib.Path({str(child_pid)!r}).write_text(str(p.pid)); "
        "exec('while True: print(\"alive\",flush=True); time.sleep(.02)')"
    )
    result = run_command([sys.executable, "-c", code], cwd=tmp_path, timeout=5, capture=True)
    assert child_pid.exists(), "SETUP INCOMPLETE: child never reached readiness"
    pid = int(child_pid.read_text())
    try:
        assert result.returncode == 124, "hang must be incomplete"
        assert "INCOMPLETE" in result.stderr, "hang must have an incomplete diagnostic"
        assert "alive" in result.stdout, "partial chatter output must survive cleanup"
        for _ in range(50):
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                break
            time.sleep(0.02)
        else:
            pytest.fail("inherited child survived timeout cleanup")
    finally:
        # The fixture owns exactly this non-forking child, even during red challenges.
        import signal

        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def test_incomplete_exit_cannot_supply_a_red_witness(tmp_path: Path) -> None:
    root = _witness_repo(tmp_path)
    governance.witness_begin(root, **WITNESS)
    (root / "guard.txt").write_text("allow\n")
    original = governance._witness_run
    try:
        governance._witness_run = lambda command, root: (
            (124, WITNESS["expect"])
            if (root / "guard.txt").read_text() == "allow\n"
            else original(command, root)
        )
        with pytest.raises(governance.GovernanceError, match="incomplete, interrupted"):
            governance.witness_finish(root)
    finally:
        governance._witness_run = original
    assert (root / "guard.txt").read_text() == "deny\n"
    assert not (root / "reports/witnesses.jsonl").exists()


def test_governance_child_incomplete_remains_incomplete(
    estate: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def interrupted_collection(root):
        return governance._run([sys.executable, "-c", "raise SystemExit(124)"], root)

    monkeypatch.setattr(governance, "collect_pytest", interrupted_collection)
    result = governance.main(["--root", str(estate), "inventory"])
    error = capsys.readouterr().err
    assert result == 124, "governance must preserve the incomplete exit"
    assert "TEST GOVERNANCE INCOMPLETE" in error, "governance must label incomplete collection"
    assert "TEST GOVERNANCE ERROR" not in error, "incomplete collection is not a refusal"


@pytest.mark.parametrize("leader_exit", [0, 1])
def test_outstanding_child_makes_completed_leader_incomplete(
    tmp_path: Path, leader_exit: int
) -> None:
    import signal
    import time

    from agentic_starter.test_runner import run_command

    ready = tmp_path / "ready"
    child = (
        "import os,signal,time,pathlib; signal.signal(signal.SIGTERM,signal.SIG_IGN); "
        f"pathlib.Path({str(ready)!r}).write_text(str(os.getpid())); time.sleep(30)"
    )
    leader = (
        "import subprocess,sys,pathlib,time; "
        f"subprocess.Popen([sys.executable,'-c',{child!r}],"
        "stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); "
        f"ready=pathlib.Path({str(ready)!r}); "
        "deadline=time.monotonic()+10; "
        "exec('while not ready.exists() and time.monotonic()<deadline: time.sleep(.02)'); "
        f"raise SystemExit({leader_exit})"
    )
    pid = None
    try:
        result = run_command([sys.executable, "-c", leader], cwd=tmp_path, capture=True)
        assert ready.exists(), "SETUP INCOMPLETE: leftover child never became ready"
        pid = int(ready.read_text())
        assert result.returncode == 124, f"outstanding group after exit {leader_exit} is incomplete"
        assert "INCOMPLETE" in result.stderr, (
            f"outstanding group after exit {leader_exit} needs a diagnostic"
        )
        for _ in range(50):
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                break
            time.sleep(0.02)
        else:
            pytest.fail(f"outstanding child after exit {leader_exit} survived cleanup")
    finally:
        if pid is None and ready.exists():
            pid = int(ready.read_text())
        if pid is not None:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass


def test_governance_allows_nested_supervisor_cleanup(tmp_path: Path, monkeypatch) -> None:
    import functools
    import signal
    import time

    ready = tmp_path / "ready"
    child = (
        "import os,signal,time,pathlib; signal.signal(signal.SIGTERM,signal.SIG_IGN); "
        f"pathlib.Path({str(ready)!r}).write_text(str(os.getpid())); time.sleep(30)"
    )
    inner = (
        "import sys; from pathlib import Path; "
        f"sys.path.insert(0,{str(REPO_ROOT / 'lib')!r}); "
        "from agentic_starter.test_runner import run_command; "
        f"r=run_command([sys.executable,'-c',{child!r}],cwd=Path.cwd(),timeout=30); "
        "raise SystemExit(r.returncode)"
    )
    monkeypatch.setattr(
        governance, "run_command", functools.partial(governance.run_command, timeout=5)
    )
    pid = None
    try:
        result = governance._run([sys.executable, "-c", inner], tmp_path, check=False)
        assert ready.exists(), "SETUP INCOMPLETE: nested child never became ready"
        pid = int(ready.read_text())
        assert result.returncode == 124, "nested incomplete status must survive governance"
        for _ in range(50):
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                break
            time.sleep(0.02)
        else:
            pytest.fail("outer supervisor killed inner cleanup before its resistant child")
    finally:
        if pid is None and ready.exists():
            pid = int(ready.read_text())
        if pid is not None:
            try:
                os.killpg(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass


@pytest.mark.parametrize("mode", ["timeout", "term", "double-term", "hup", "completed-error"])
def test_real_supervisor_entrypoint_handles_deadlines_and_signals(
    tmp_path: Path, mode: str
) -> None:
    import os
    import signal
    import time

    root = tmp_path / "runner"
    script = root / "lib/agentic_starter/test_runner.py"
    script.parent.mkdir(parents=True)
    script.write_bytes((REPO_ROOT / "lib/agentic_starter/test_runner.py").read_bytes())
    (root / "tests").mkdir()
    (root / "tests/proof-estate.yaml").write_text(
        "hang_timeout_seconds: " + ("5" if mode == "timeout" else "30")
    )
    ready = root / "ready"
    code = (
        "import os,signal,time,pathlib; signal.signal(signal.SIGTERM,signal.SIG_IGN); "
        f"pathlib.Path({str(ready)!r}).write_text(str(os.getpid())); "
        "print('ready',flush=True); time.sleep(30)"
    )
    if mode == "completed-error":
        code = "raise SystemExit(2)"
    process = subprocess.Popen(
        [sys.executable, str(script), "-c", code],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    child_pid = None
    try:
        if mode != "completed-error":
            deadline = time.monotonic() + 10
            while not ready.exists() and process.poll() is None and time.monotonic() < deadline:
                time.sleep(0.02)
            assert ready.exists(), "SETUP INCOMPLETE: supervised child never became ready"
            child_pid = int(ready.read_text())
        if mode in ("term", "double-term", "hup"):
            process.send_signal(signal.SIGHUP if mode == "hup" else signal.SIGTERM)
            if mode == "double-term":
                time.sleep(0.05)
                process.send_signal(signal.SIGTERM)
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            pytest.fail("supervisor did not terminate its invocation")
        if mode == "completed-error":
            assert process.returncode == 2, "completed non-assertion error status must survive"
        else:
            assert process.returncode == 124, "entrypoint interruption must remain incomplete"
            for _ in range(50):
                try:
                    os.kill(child_pid, 0)
                except ProcessLookupError:
                    break
                time.sleep(0.02)
            else:
                pytest.fail("supervisor left its inherited child alive")
        output, error = process.communicate(timeout=2)
        if mode != "completed-error":
            assert "INCOMPLETE" in error, "entrypoint must label incomplete outcomes"
    finally:
        # Only these two fixture-owned, non-forking groups are in the cleanup set.
        for group in (child_pid, process.pid):
            if group is not None:
                try:
                    os.killpg(group, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        process.communicate(timeout=2)
