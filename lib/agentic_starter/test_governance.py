"""Deterministic inventory, validation, assay, and selection for proof estates."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import platform
import re
import shlex
import shutil
import statistics
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ElementTree
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import yaml

SCHEMA = "agentic.proof_estate.v3"
BASELINE_SCHEMA = "agentic.proof_baseline.v2"
REQUIRED_FAMILY_FIELDS = {
    "id",
    "kind",
    "selectors",
    "source_paths",
    "covers",
    "contract",
    "risk_class",
    "oracle",
    "admission",
    "nearest_overlap",
    "historical_evidence",
    "mutation_evidence",
    "tier",
    "flake_rate",
    "replacement_lineage",
}
TIERS = {"vital", "changed", "full"}
SIZES = ("small", "medium", "large")
TIMING_RECORD = ".kickoff/test-timing/full.xml"
CONFIRMING_SAMPLES = 3
KINDS = {"pytest", "gate", "hook"}
DISPOSITION_FIELDS = {
    "record_type",
    "proof_id",
    "disposition",
    "contract",
    "oracle",
    "red_witness",
    "nearest_overlap",
    "replacement",
    "replacement_evidence",
    "rationale",
    "baseline_inventory_sha256",
}
ADMISSION_FIELDS = DISPOSITION_FIELDS
RETIREMENT_FIELDS = DISPOSITION_FIELDS
REPAIR_FIELDS = DISPOSITION_FIELDS
SELF_BOUND_DISPOSITIONS = {"retain", "repair"}
EFFECTIVENESS_FIELDS = {
    "record_type",
    "evidence_id",
    "evidence_class",
    "observed",
    "detected_by",
    "command",
    "patch_sha256",
    "output_sha256",
    "assayed_on",
}


class GovernanceError(RuntimeError):
    """A fail-closed proof-governance refusal."""


@dataclass(frozen=True)
class Proof:
    proof_id: str
    family_id: str
    kind: str
    selector: str
    source_path: str

    def as_dict(self) -> dict[str, str]:
        return {
            "id": self.proof_id,
            "family": self.family_id,
            "kind": self.kind,
            "selector": self.selector,
            "source_path": self.source_path,
        }


def _run(
    command: Sequence[str], root: Path, *, check: bool = True
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        list(command),
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "no diagnostic"
        raise GovernanceError(
            f"command failed ({result.returncode}): {' '.join(command)}: {detail}"
        )
    return result


def _pytest_family(node_id: str) -> str:
    return re.sub(r"\[[^\n]*\]$", "", node_id)


def collect_pytest(root: Path) -> list[Proof]:
    result = _run(
        [
            str(root / "bin/python"),
            "-m",
            "pytest",
            "--collect-only",
            "-q",
            "--rootdir",
            ".",
            "project/tests",
            "tests",
        ],
        root,
    )
    proofs: list[Proof] = []
    for line in result.stdout.splitlines():
        node_id = line.strip()
        if not node_id.startswith(("project/tests/", "tests/")) or "::" not in node_id:
            continue
        family = _pytest_family(node_id)
        source_path = node_id.split("::", 1)[0]
        proofs.append(
            Proof(
                proof_id=f"pytest:{node_id}",
                family_id=f"pytest:{family}",
                kind="pytest",
                selector=node_id,
                source_path=source_path,
            )
        )
    if not proofs:
        raise GovernanceError("pytest collection produced no proof nodes")
    return proofs


_GATE_CALL = re.compile(r"^\s*run_(?:member_)?gate\s+([A-Za-z0-9_-]+)(?:\s|$)")


def collect_check_gates(root: Path) -> list[Proof]:
    path = root / "bin/check"
    proofs: list[Proof] = []
    try:
        lines = path.read_text().splitlines()
    except OSError as exc:
        raise GovernanceError(f"cannot read bin/check: {exc}") from exc
    for line_number, line in enumerate(lines, 1):
        match = _GATE_CALL.match(line)
        if not match:
            continue
        name = match.group(1)
        if name.startswith("$"):
            continue
        proof_id = f"gate:{name}"
        proofs.append(
            Proof(
                proof_id=proof_id,
                family_id=proof_id,
                kind="gate",
                selector=name,
                source_path=f"bin/check:{line_number}",
            )
        )
    unique = {proof.proof_id: proof for proof in proofs}
    return [unique[key] for key in sorted(unique)]


def collect_hooks(root: Path) -> list[Proof]:
    path = root / ".githooks/pre-commit"
    if not path.is_file():
        return []
    proofs: list[Proof] = []
    for line_number, line in enumerate(path.read_text().splitlines(), 1):
        command = line.strip()
        if command.startswith("./bin/"):
            proof_id = f"hook:.githooks/pre-commit:{command}"
            proofs.append(
                Proof(
                    proof_id=proof_id,
                    family_id=proof_id,
                    kind="hook",
                    selector=proof_id,
                    source_path=f".githooks/pre-commit:{line_number}",
                )
            )
    return proofs


def inventory(root: Path) -> dict[str, Any]:
    proofs = collect_pytest(root) + collect_check_gates(root) + collect_hooks(root)
    proof_ids = [proof.proof_id for proof in proofs]
    if len(proof_ids) != len(set(proof_ids)):
        duplicates = sorted({item for item in proof_ids if proof_ids.count(item) > 1})
        raise GovernanceError(f"duplicate proof ids: {', '.join(duplicates[:10])}")
    families = sorted({proof.family_id for proof in proofs})
    by_kind: dict[str, dict[str, int]] = {}
    for kind in sorted(KINDS):
        members = [proof for proof in proofs if proof.kind == kind]
        by_kind[kind] = {
            "families": len({proof.family_id for proof in members}),
            "leaves": len(members),
        }
    payload: dict[str, Any] = {
        "schema": BASELINE_SCHEMA,
        "counts": {"families": len(families), "leaves": len(proofs)},
        "by_kind": by_kind,
        "families": families,
        "proofs": [proof.as_dict() for proof in proofs],
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["inventory_sha256"] = hashlib.sha256(canonical).hexdigest()
    return payload


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        payload = yaml.safe_load(path.read_text())
    except (OSError, yaml.YAMLError) as exc:
        raise GovernanceError(f"cannot read {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise GovernanceError(f"{path} must contain one YAML mapping")
    return payload


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise GovernanceError(f"cannot read {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise GovernanceError(f"{path} must contain one JSON object")
    return payload


def load_ledger(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text().splitlines()
    except OSError as exc:
        raise GovernanceError(f"cannot read {path}: {exc}") from exc
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise GovernanceError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise GovernanceError(f"{path}:{line_number}: row must be an object")
        rows.append(row)
    return rows


def _matches(selector: str, proof: Proof) -> bool:
    if proof.kind == "pytest":
        family = proof.family_id.removeprefix("pytest:")
        node = proof.proof_id.removeprefix("pytest:")
        if selector.endswith(".py"):
            return node.startswith(f"{selector}::")
        return fnmatch.fnmatchcase(family, selector) or fnmatch.fnmatchcase(node, selector)
    return fnmatch.fnmatchcase(proof.selector, selector) or fnmatch.fnmatchcase(
        proof.proof_id, selector
    )


def _family_claims(family: dict[str, Any], proof: Proof) -> bool:
    if family.get("kind") != proof.kind:
        return False
    selectors = family.get("selectors")
    return isinstance(selectors, list) and any(
        isinstance(selector, str) and _matches(selector, proof) for selector in selectors
    )


def _validate_family_shape(family: Any, index: int) -> list[str]:
    errors: list[str] = []
    if not isinstance(family, dict):
        return [f"families[{index}] must be a mapping"]
    missing = sorted(REQUIRED_FAMILY_FIELDS - set(family))
    if missing:
        errors.append(f"families[{index}] missing: {', '.join(missing)}")
    family_id = family.get("id", f"families[{index}]")
    if family.get("kind") not in KINDS:
        errors.append(f"{family_id}: invalid kind {family.get('kind')!r}")
    if family.get("tier") not in TIERS:
        errors.append(f"{family_id}: invalid tier {family.get('tier')!r}")
    selectors = family.get("selectors")
    if (
        not isinstance(selectors, list)
        or not selectors
        or not all(isinstance(item, str) and item for item in selectors)
    ):
        errors.append(f"{family_id}: selectors must be a nonempty string list")
    for field in (
        "source_paths",
        "covers",
        "historical_evidence",
        "mutation_evidence",
        "replacement_lineage",
    ):
        value = family.get(field)
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            errors.append(f"{family_id}: {field} must be a string list")
    for field in ("contract", "risk_class", "oracle", "admission", "nearest_overlap"):
        if not isinstance(family.get(field), str) or not family.get(field, "").strip():
            errors.append(f"{family_id}: {field} must be nonempty text")
    if family.get("kind") == "pytest":
        if family.get("size") not in SIZES:
            errors.append(f"{family_id}: pytest size must be one of {', '.join(SIZES)}")
    elif "size" in family:
        errors.append(f"{family_id}: only pytest families declare a size")
    flake = family.get("flake_rate")
    if not isinstance(flake, (int, float)) or not 0 <= flake <= 1:
        errors.append(f"{family_id}: flake_rate must be between 0 and 1")
    return errors


def machine_fingerprint() -> str:
    """A stable, non-identifying name for this machine; timings compare only within one."""
    material = "|".join(
        (platform.node(), platform.system(), platform.machine(), str(os.cpu_count()))
    )
    return hashlib.sha256(material.encode()).hexdigest()[:16]


def _time_budget_errors(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    ceilings = manifest.get("size_ceilings_seconds")
    if (
        not isinstance(ceilings, dict)
        or set(ceilings) != set(SIZES)
        or not all(isinstance(value, (int, float)) and value > 0 for value in ceilings.values())
    ):
        errors.append("size_ceilings_seconds must give a positive ceiling for each size")
    elif not ceilings["small"] < ceilings["medium"] < ceilings["large"]:
        errors.append("size_ceilings_seconds must increase from small to large")
    budget = manifest.get("time_budget")
    if not isinstance(budget, dict):
        return [*errors, "time_budget must be a mapping"]
    seconds = budget.get("test_lane_seconds")
    if not isinstance(seconds, (int, float)) or seconds <= 0:
        errors.append("time_budget.test_lane_seconds must be positive")
    tolerance = budget.get("tolerance")
    if not isinstance(tolerance, (int, float)) or not 0 <= tolerance <= 1:
        errors.append("time_budget.tolerance must be between 0 and 1")
    reference = budget.get("reference_machine")
    if reference is not None and not (
        isinstance(reference, str) and re.fullmatch(r"[0-9a-f]{16}", reference)
    ):
        errors.append("time_budget.reference_machine must be null or a machine fingerprint")
    return errors


def _source_file(reported: str, known: set[str]) -> str | None:
    """Resolve a file pytest reported relative to its rootdir to one repository test file."""
    parts = [part for part in reported.split("/") if part not in ("", ".")]
    while parts and parts[0] == "..":
        parts.pop(0)
    relative = "/".join(parts)
    if relative in known:
        return relative
    matches = [path for path in known if path.endswith("/" + relative)]
    return matches[0] if len(matches) == 1 else None


def _junit_sample(path: Path, known: set[str]) -> tuple[float, dict[str, float]] | None:
    """The suite's wall time and each executed leaf's time, or None when the record is unusable."""
    try:
        document = ElementTree.parse(path).getroot()
    except (OSError, ElementTree.ParseError):
        return None
    suites = [document] if document.tag == "testsuite" else list(document.iter("testsuite"))
    try:
        total = sum(float(suite.get("time", "")) for suite in suites)
    except ValueError:
        return None
    leaves: dict[str, float] = {}
    for case in document.iter("testcase"):
        file_name, classname, name = case.get("file"), case.get("classname", ""), case.get("name")
        source = _source_file(file_name, known) if file_name and name else None
        module = Path(source).stem if source else None
        components = classname.split(".")
        if source is None or module not in components:
            return None
        inner = "::".join(components[len(components) - components[::-1].index(module) :])
        node = f"{source}::{inner}::{name}" if inner else f"{source}::{name}"
        try:
            leaves[f"pytest:{node}"] = float(case.get("time", ""))
        except ValueError:
            return None
    return (total, leaves) if suites and leaves else None


def timing(root: Path, samples: int = 0) -> dict[str, Any]:
    """Judge per-test size ceilings and the test-lane budget from recorded full runs.

    Wall-clock time is noisy, so each check is shaped to survive it: size ceilings are
    order-of-magnitude bands, the lane budget carries a tolerance, a single run can only
    raise an advisory, and a budget set on one machine is never judged on another.
    """
    manifest = load_yaml(root / "tests/proof-estate.yaml")
    shape_errors = _time_budget_errors(manifest)
    if shape_errors:
        raise GovernanceError("timing configuration invalid:\n- " + "\n- ".join(shape_errors))
    record = root / TIMING_RECORD
    current = {
        proof["id"]: proof for proof in inventory(root)["proofs"] if proof["kind"] == "pytest"
    }
    known = {str(proof["source_path"]) for proof in current.values()}
    runs: list[tuple[float, dict[str, float]]] = []
    if samples:
        for index in range(samples):
            completed = _run([str(root / "bin/test")], root, check=False)
            sample = _junit_sample(record, known) if completed.returncode == 0 else None
            if sample is None:
                raise GovernanceError(f"timing sample {index + 1} did not complete a full run")
            runs.append(sample)
    else:
        sample = _junit_sample(record, known)
        if sample is not None:
            runs.append(sample)
    fingerprint = machine_fingerprint()
    if not runs:
        return {
            "state": "unmeasured",
            "reason": "no full-run timing record",
            "machine": fingerprint,
        }
    if any(set(leaves) != set(current) for _, leaves in runs):
        if samples:
            raise GovernanceError("timing samples do not cover exactly the current pytest estate")
        return {
            "state": "unmeasured",
            "reason": "the timing record predates the current pytest estate",
            "machine": fingerprint,
        }
    families = manifest["families"]
    ceilings = manifest["size_ceilings_seconds"]
    violations = []
    medians: dict[str, float] = {}
    for proof_id, row in current.items():
        median = statistics.median(leaves[proof_id] for _, leaves in runs)
        medians[proof_id] = median
        proof = Proof(
            proof_id=row["id"],
            family_id=row["family"],
            kind=row["kind"],
            selector=row["selector"],
            source_path=row["source_path"],
        )
        owners = [family for family in families if _family_claims(family, proof)]
        if len(owners) != 1:
            raise GovernanceError(f"timing cannot resolve one family for {proof_id}")
        size = owners[0]["size"]
        if median > ceilings[size]:
            violations.append(
                f"{proof_id} took {median:.2f}s, over the {size} ceiling of {ceilings[size]}s"
                f" for family {owners[0]['id']}"
            )
    budget = manifest["time_budget"]
    total = statistics.median(total for total, _ in runs)
    limit = budget["test_lane_seconds"] * (1 + budget["tolerance"])
    if budget.get("reference_machine") is None:
        budget_state = "unmeasured: no reference machine is declared"
    elif budget["reference_machine"] != fingerprint:
        budget_state = "unmeasured: this is not the reference machine"
    elif total <= limit:
        budget_state = "within"
    elif len(runs) >= CONFIRMING_SAMPLES:
        budget_state = "over"
    else:
        budget_state = "advisory: over on too few runs to confirm"
    return {
        "state": "fail" if violations or budget_state == "over" else "measured",
        "machine": fingerprint,
        "samples": len(runs),
        "test_lane_seconds": round(total, 2),
        "budget_seconds": budget["test_lane_seconds"],
        "limit_seconds": round(limit, 2),
        "budget": budget_state,
        "size_violations": violations,
        "slowest": [
            {"proof": proof_id, "seconds": round(seconds, 2)}
            for proof_id, seconds in sorted(medians.items(), key=lambda item: -item[1])[:5]
        ],
    }


def _is_iso_date(value: Any) -> bool:
    try:
        return isinstance(value, str) and date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def _ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        raise GovernanceError("recall denominator must be positive")
    return numerator / denominator


def validate(root: Path) -> dict[str, Any]:
    manifest_path = root / "tests/proof-estate.yaml"
    manifest = load_yaml(manifest_path)
    errors: list[str] = []
    if manifest.get("schema") != SCHEMA:
        errors.append(f"manifest schema must be {SCHEMA}")
    families = manifest.get("families")
    if not isinstance(families, list) or not families:
        raise GovernanceError("manifest families must be a nonempty list")
    for index, family in enumerate(families):
        errors.extend(_validate_family_shape(family, index))
    family_ids = [family.get("id") for family in families if isinstance(family, dict)]
    duplicates = sorted({item for item in family_ids if family_ids.count(item) > 1})
    if duplicates:
        errors.append(f"duplicate family ids: {', '.join(str(item) for item in duplicates)}")

    current = inventory(root)
    proofs = [
        Proof(
            proof_id=row["id"],
            family_id=row["family"],
            kind=row["kind"],
            selector=row["selector"],
            source_path=row["source_path"],
        )
        for row in current["proofs"]
    ]
    claimed_by: dict[str, list[str]] = {}
    for proof in proofs:
        claims = [family["id"] for family in families if _family_claims(family, proof)]
        claimed_by[proof.proof_id] = claims
        if not claims:
            errors.append(f"undeclared executable proof: {proof.proof_id}")
        elif len(claims) > 1:
            errors.append(
                f"multiply declared executable proof: {proof.proof_id}: {', '.join(claims)}"
            )
    for family in families:
        if not any(family["id"] in claims for claims in claimed_by.values()):
            errors.append(f"declared family selects no executable proof: {family['id']}")
        for source_path in family.get("source_paths", []):
            if (
                not any(character in source_path for character in "*?[")
                and not (root / source_path).exists()
            ):
                errors.append(f"{family['id']}: missing source path: {source_path}")

    baseline_rel = manifest.get("baseline_report")
    if not isinstance(baseline_rel, str) or not baseline_rel:
        errors.append("baseline_report must be a repo-relative path")
        baseline: dict[str, Any] = {}
    else:
        baseline = load_json(root / baseline_rel)
        if baseline.get("schema") != BASELINE_SCHEMA:
            errors.append(f"baseline schema must be {BASELINE_SCHEMA}")
        canonical_baseline = dict(baseline)
        declared_baseline_digest = canonical_baseline.pop("inventory_sha256", None)
        observed_baseline_digest = hashlib.sha256(
            json.dumps(canonical_baseline, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        if declared_baseline_digest != observed_baseline_digest:
            errors.append("baseline inventory digest is stale")
    limits = manifest.get("effectiveness_floors")
    if not isinstance(limits, dict):
        errors.append("effectiveness_floors must be a mapping")
        limits = {}
    errors.extend(_time_budget_errors(manifest))

    current_ids = {proof.proof_id for proof in proofs}
    critical = manifest.get("critical_risks")
    if not isinstance(critical, dict) or not critical:
        errors.append("critical_risks must be a nonempty mapping")
        critical = {}
    for risk_class, declaration in critical.items():
        if not isinstance(declaration, dict):
            errors.append(f"critical risk {risk_class} must be a mapping")
            continue
        state = declaration.get("state")
        if state == "applicable":
            direct_proof = declaration.get("direct_proof")
            if direct_proof not in current_ids:
                errors.append(
                    f"critical risk {risk_class} direct proof is not retained: {direct_proof}"
                )
        elif state == "not-applicable":
            if risk_class != "deploy":
                errors.append(f"only deploy may be not-applicable: {risk_class}")
            for field in ("rationale", "activation_trigger"):
                if not isinstance(declaration.get(field), str) or not declaration[field]:
                    errors.append(f"critical risk {risk_class} lacks {field}")
        else:
            errors.append(f"critical risk {risk_class} has invalid state")

    ledger_rel = manifest.get("audit_ledger")
    if not isinstance(ledger_rel, str) or not ledger_rel:
        errors.append("audit_ledger must be a repo-relative path")
        ledger: list[dict[str, Any]] = []
    else:
        ledger = load_ledger(root / ledger_rel)
    baseline_ids = {row.get("id") for row in baseline.get("proofs", [])}
    disposition_rows = [row for row in ledger if row.get("record_type") == "proof_disposition"]
    admission_rows = [row for row in ledger if row.get("record_type") == "proof_admission"]
    retirement_rows = [row for row in ledger if row.get("record_type") == "proof_retirement"]
    repair_rows = [row for row in ledger if row.get("record_type") == "proof_repair"]
    known_record_types = {
        "proof_disposition",
        "proof_admission",
        "proof_retirement",
        "proof_repair",
    }
    unknown_record_types = sorted(
        {
            str(row.get("record_type"))
            for row in ledger
            if row.get("record_type") not in known_record_types
        }
    )
    if unknown_record_types:
        errors.append(
            "audit ledger contains unknown record types: " + ", ".join(unknown_record_types)
        )
    disposition_ids = [row.get("proof_id") for row in disposition_rows]
    if len(disposition_ids) != len(set(disposition_ids)):
        errors.append("audit ledger contains duplicate proof dispositions")
    missing_dispositions = sorted(baseline_ids - set(disposition_ids))
    extra_dispositions = sorted(set(disposition_ids) - baseline_ids)
    if missing_dispositions:
        errors.append(f"audit ledger misses {len(missing_dispositions)} baseline proofs")
    if extra_dispositions:
        errors.append(f"audit ledger names {len(extra_dispositions)} non-baseline proofs")
    admission_ids = [row.get("proof_id") for row in admission_rows]
    if len(admission_ids) != len(set(admission_ids)):
        errors.append("audit ledger contains duplicate proof admissions")
    if not current_ids - baseline_ids <= set(admission_ids):
        errors.append("audit ledger does not admit every active post-baseline proof")
    dispositions_seen: set[str] = set()
    for row in disposition_rows:
        if set(row) != DISPOSITION_FIELDS:
            errors.append(f"wrong disposition fields for {row.get('proof_id')}")
            continue
        if row.get("disposition") not in SELF_BOUND_DISPOSITIONS | {"delete", "consolidate"}:
            errors.append(f"invalid disposition for {row.get('proof_id')}")
            continue
        dispositions_seen.add(str(row["disposition"]))
        for field in (
            "contract",
            "oracle",
            "red_witness",
            "nearest_overlap",
            "replacement_evidence",
            "rationale",
        ):
            if not isinstance(row.get(field), str) or not row[field]:
                errors.append(f"missing disposition {field} for {row.get('proof_id')}")
        if row.get("baseline_inventory_sha256") != baseline.get("inventory_sha256"):
            errors.append(f"stale disposition baseline for {row.get('proof_id')}")
        proof_id = row.get("proof_id")
        replacement = row.get("replacement")
        if row.get("disposition") in SELF_BOUND_DISPOSITIONS:
            if replacement != proof_id:
                errors.append(f"retained proof self-binding is wrong: {proof_id}")
        elif row.get("disposition") == "consolidate":
            if proof_id in current_ids or replacement not in baseline_ids | set(admission_ids):
                errors.append(f"consolidated proof has invalid replacement: {proof_id}")
        elif proof_id in current_ids or replacement is not None:
            errors.append(f"deleted proof still exists or names a replacement: {proof_id}")
    if not {"delete", "consolidate"} <= dispositions_seen:
        errors.append("reset must contain both delete and consolidate dispositions")
    initial_active = {
        str(row.get("proof_id"))
        for row in disposition_rows
        if row.get("disposition") in SELF_BOUND_DISPOSITIONS
    }
    active = set(initial_active)
    seen_retirement_targets: set[str] = set()
    disposition_phase_open = True
    for row in ledger:
        record_type = row.get("record_type")
        if record_type == "proof_disposition":
            if not disposition_phase_open:
                errors.append("baseline dispositions must precede lifecycle events")
            continue
        disposition_phase_open = False
        if record_type == "proof_retirement":
            proof_id = row.get("proof_id")
            if set(row) != RETIREMENT_FIELDS:
                errors.append(f"wrong retirement fields for {proof_id}")
                continue
            if proof_id in seen_retirement_targets:
                errors.append(f"proof is retired more than once: {proof_id}")
            seen_retirement_targets.add(str(proof_id))
            if proof_id not in active:
                errors.append(f"retirement target is not active: {proof_id}")
                continue
            disposition = row.get("disposition")
            replacement = row.get("replacement")
            if disposition == "consolidate":
                if replacement == proof_id or replacement not in active:
                    errors.append(f"retirement has invalid consolidation replacement: {proof_id}")
            elif disposition == "delete":
                if replacement is not None:
                    errors.append(f"deleted retirement names a replacement: {proof_id}")
            else:
                errors.append(f"retirement must consolidate or delete: {proof_id}")
            if row.get("baseline_inventory_sha256") != baseline.get("inventory_sha256"):
                errors.append(f"stale retirement baseline for {proof_id}")
            for field in (
                "contract",
                "oracle",
                "red_witness",
                "nearest_overlap",
                "replacement_evidence",
                "rationale",
            ):
                if not isinstance(row.get(field), str) or not row[field]:
                    errors.append(f"missing retirement {field} for {proof_id}")
            active.discard(str(proof_id))
            continue
        if record_type == "proof_repair":
            proof_id = row.get("proof_id")
            if set(row) != REPAIR_FIELDS:
                errors.append(f"wrong repair fields for {proof_id}")
                continue
            if proof_id not in active:
                errors.append(f"repair target is not active: {proof_id}")
            if row.get("disposition") != "repair" or row.get("replacement") != proof_id:
                errors.append(f"repair must self-bind with disposition repair: {proof_id}")
            if row.get("baseline_inventory_sha256") != baseline.get("inventory_sha256"):
                errors.append(f"stale repair baseline for {proof_id}")
            for field in (
                "contract",
                "oracle",
                "red_witness",
                "nearest_overlap",
                "replacement_evidence",
                "rationale",
            ):
                if not isinstance(row.get(field), str) or not row[field]:
                    errors.append(f"missing repair {field} for {proof_id}")
            continue
        if record_type != "proof_admission":
            continue
        if set(row) != ADMISSION_FIELDS:
            errors.append(f"wrong admission fields for {row.get('proof_id')}")
            continue
        proof_id = row.get("proof_id")
        if row.get("disposition") != "retain" or row.get("replacement") != proof_id:
            errors.append(f"post-baseline admission must retain and self-bind: {proof_id}")
        if proof_id in active:
            errors.append(f"admission proof is already active: {proof_id}")
        active.add(str(proof_id))
        for field in (
            "contract",
            "oracle",
            "red_witness",
            "nearest_overlap",
            "replacement_evidence",
            "rationale",
        ):
            if not isinstance(row.get(field), str) or not row[field]:
                errors.append(f"missing admission {field} for {proof_id}")
    if active != current_ids:
        missing = sorted(current_ids - active)
        shadow = sorted(active - current_ids)
        errors.append(
            "replayed proof estate does not match inventory"
            f" (unadmitted={missing[:3]}, shadow={shadow[:3]})"
        )

    corpus_rel = manifest.get("effectiveness_corpus")
    report_rel = manifest.get("effectiveness_report")
    corpus = load_yaml(root / corpus_rel) if isinstance(corpus_rel, str) else {}
    effectiveness = load_ledger(root / report_rel) if isinstance(report_rel, str) else []
    cases = corpus.get("cases") if isinstance(corpus, dict) else None
    if corpus.get("selection_frozen") is not True:
        errors.append("effectiveness selection must be frozen before holdout execution")
    if not isinstance(cases, list):
        errors.append("effectiveness corpus cases must be a list")
        cases = []
    case_ids = [case.get("id") for case in cases if isinstance(case, dict)]
    if len(case_ids) != len(set(case_ids)):
        errors.append("effectiveness corpus contains duplicate case ids")
    evidence_ids = [row.get("evidence_id") for row in effectiveness]
    if len(evidence_ids) != len(set(evidence_ids)):
        errors.append("effectiveness report contains duplicate case ids")
    if set(evidence_ids) != set(case_ids):
        errors.append("effectiveness report does not cover the frozen corpus exactly")
    for case in cases:
        if not isinstance(case, dict) or set(case) != {
            "id",
            "class",
            "patch",
            "patch_sha256",
            "command",
            "cwd",
            "expected",
            "owner",
        }:
            errors.append(f"effectiveness case has wrong fields: {case!r}")
            continue
        patch = root / str(case["patch"])
        if not patch.is_file() or not patch.read_text().strip():
            errors.append(f"effectiveness patch is absent or empty: {case['patch']}")
            continue
        patch_sha256 = hashlib.sha256(patch.read_bytes()).hexdigest()
        if case["patch_sha256"] != patch_sha256:
            errors.append(f"effectiveness patch digest drifted: {case['id']}")
    cases_by_id = {
        case["id"]: case
        for case in cases
        if isinstance(case, dict) and isinstance(case.get("id"), str)
    }
    recall: dict[str, float] = {}
    unmeasured: list[str] = []
    assay_dates: list[str] = []
    for evidence_class, limit_key, floor_key in (
        ("historical_defect", "min_historical_recall", "min_historical_cases"),
        ("holdout_mutant", "min_mutant_recall", "min_mutant_cases"),
    ):
        expected = [
            case for case in cases if isinstance(case, dict) and case.get("class") == evidence_class
        ]
        declared_floor = limits.get(floor_key, 0)
        if not isinstance(declared_floor, int) or isinstance(declared_floor, bool):
            errors.append(f"{floor_key} must be an integer")
            declared_floor = 0
        elif declared_floor < 0:
            errors.append(f"{floor_key} must not be negative")
            declared_floor = 0
        if len(expected) < declared_floor:
            errors.append(
                f"{evidence_class} corpus holds {len(expected)} cases, "
                f"below the declared floor of {declared_floor}"
            )
        evidence = [row for row in effectiveness if row.get("evidence_class") == evidence_class]
        observed = [row for row in evidence if row.get("observed") is True]
        for row in evidence:
            if set(row) != EFFECTIVENESS_FIELDS:
                errors.append(f"{evidence_class} {row.get('evidence_id')} has wrong fields")
                continue
            case = cases_by_id.get(row["evidence_id"])
            if case is None:
                continue
            if row["observed"] not in (True, False):
                errors.append(f"{evidence_class} {row['evidence_id']} has invalid observation")
            if row["command"] != case["command"]:
                errors.append(f"{evidence_class} {row['evidence_id']} command drifted")
            if row["patch_sha256"] != case["patch_sha256"]:
                errors.append(f"{evidence_class} {row['evidence_id']} patch digest drifted")
            if not _is_iso_date(row["assayed_on"]):
                errors.append(f"{evidence_class} {row['evidence_id']} has no assay date")
            else:
                assay_dates.append(str(row["assayed_on"]))
        detected = [
            row
            for row in observed
            if isinstance(row.get("detected_by"), list)
            and any(item in family_ids for item in row["detected_by"])
        ]
        minimum = limits.get(limit_key)
        if not evidence:
            if declared_floor == 0 and not expected:
                # An empty declared corpus is unmeasured, never zero and never passing.
                unmeasured.append(evidence_class)
                continue
            errors.append(f"audit ledger has no {evidence_class} evidence")
            continue
        if not isinstance(minimum, (int, float)) or not 0 <= minimum <= 1:
            errors.append(f"{limit_key} must be between 0 and 1")
            continue
        score = _ratio(len(detected), len(evidence))
        recall[evidence_class] = score
        if score < minimum:
            errors.append(
                f"{evidence_class} recall below floor: "
                f"{len(detected)}/{len(evidence)}={score:.3f} < {minimum:.3f}"
            )

    if errors:
        raise GovernanceError("validation failed:\n- " + "\n- ".join(errors))
    return {
        "schema": SCHEMA,
        "state": "valid",
        "families": current["counts"]["families"],
        "leaves": current["counts"]["leaves"],
        "recall": recall,
        "recall_unmeasured": sorted(unmeasured),
        # Recall is a measurement from the last assay, taken at a sweep, not a live property.
        "recall_as_of": min(assay_dates) if assay_dates else None,
        "dispositions": {
            state: sum(row.get("disposition") == state for row in disposition_rows)
            for state in ("retain", "repair", "consolidate", "delete")
        },
        "admissions": len(admission_rows),
        "post_reset_retirements": len(retirement_rows),
        "post_reset_repairs": len(repair_rows),
    }


DOCUMENT_READER_ROOTS = ("tests", "lib", "bin")
MAX_READER_BYTES = 4 * 1024 * 1024


def _is_document(path: str) -> bool:
    return path.endswith(".md")


def _mentions(text: str, path: str) -> bool:
    """Whether a file names a path: its repository path, or its file name beside its
    parent directory's name (code that joins ``"policies" / "surfaces.md"``; a Python
    module imported as ``package.module``). The stand-in over-selects on a shared name,
    which costs only time; it misses a path reached through a computed name, which the
    full gate before a push still catches."""
    if path in text:
        return True
    name = path.rsplit("/", 1)[-1]
    parent = path.rsplit("/", 2)[-2] if "/" in path else None
    names = (name, name.removesuffix(".py")) if name.endswith(".py") else (name,)
    return any(item in text for item in names) and (parent is None or parent in text)


def _readers(root: Path, documents: list[str]) -> dict[str, list[str]] | None:
    """Tracked test, library and executable files naming each path; None if unlistable."""
    listed = _run(["git", "ls-files", "--", *DOCUMENT_READER_ROOTS], root, check=False)
    if listed.returncode != 0:
        return None
    readers: dict[str, list[str]] = {document: [] for document in documents}
    for candidate in listed.stdout.splitlines():
        target = root / candidate
        try:
            if not target.is_file() or target.stat().st_size > MAX_READER_BYTES:
                continue
            text = target.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for document in documents:
            if _mentions(text, document):
                readers[document].append(candidate)
    return readers


def _families_for_reader(families: list[dict[str, Any]], reader: str) -> list[dict[str, Any]]:
    """A reader's families: a test file by selectors or source paths, code by its covers."""
    found = []
    for family in families:
        selector_files = {str(item).split("::", 1)[0] for item in family.get("selectors", [])}
        patterns = [*family.get("covers", []), *family.get("source_paths", [])]
        if reader in selector_files or any(
            fnmatch.fnmatchcase(reader, pattern) for pattern in patterns
        ):
            found.append(family)
    return found


def selected_families(
    root: Path, mode: str, base: str | None = None
) -> tuple[list[dict[str, Any]], str | None]:
    manifest = load_yaml(root / "tests/proof-estate.yaml")
    families = manifest.get("families")
    if not isinstance(families, list) or not families:
        raise GovernanceError("manifest families must be a nonempty list")
    vital = [family for family in families if family.get("tier") == "vital"]
    if mode == "vital":
        return vital, None
    if mode != "changed" or not base:
        raise GovernanceError("changed selection requires --base <git-ref>")
    resolved = _run(["git", "rev-parse", "--verify", f"{base}^{{commit}}"], root, check=False)
    if resolved.returncode != 0:
        return families, f"invalid-or-unavailable-base:{base}"
    result = _run(
        ["git", "diff", "--name-only", "--no-renames", base, "--"],
        root,
        check=False,
    )
    untracked = _run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        root,
        check=False,
    )
    if result.returncode != 0 or untracked.returncode != 0:
        return families, f"changed-path-enumeration-failed:{base}"
    changed = sorted(
        {line for line in (*result.stdout.splitlines(), *untracked.stdout.splitlines()) if line}
    )
    if not changed:
        return vital, None
    selected = {family["id"]: family for family in vital}
    unmapped: list[str] = []
    mapped_code: list[str] = []
    for path in changed:
        matches = [
            family
            for family in families
            if any(fnmatch.fnmatchcase(path, pattern) for pattern in family.get("covers", []))
            or any(fnmatch.fnmatchcase(path, pattern) for pattern in family.get("source_paths", []))
        ]
        if not matches:
            unmapped.append(path)
            continue
        if len(matches) > 1 and not _is_document(path):
            return families, f"ambiguous-change-map:{path}"
        if not _is_document(path):
            mapped_code.append(path)
        # A document several families cover selects all of them: its readers, not one owner,
        # are what it can break.
        for family in matches:
            selected[family["id"]] = family
    # A document no family covers selects the families of the files that read it
    # (none: the vital families
    # alone); anything else unmapped still widens to the full suite.
    documents = [path for path in unmapped if _is_document(path)]
    unmapped = [path for path in unmapped if not _is_document(path)]
    if unmapped:
        return families, "unmapped-changes:" + ",".join(sorted(unmapped))
    if documents:
        readers = _readers(root, documents)
        if readers is None:
            return families, "document-readers-unlisted"
        for document in documents:
            for reader in readers[document]:
                for family in _families_for_reader(families, reader):
                    selected[family["id"]] = family
    # Changed code also selects the families of the files that name it: a helper covered by
    # one family is still exercised by the tests of every module and test that uses it.
    if mapped_code:
        readers = _readers(root, mapped_code)
        if readers is None:
            return families, "code-readers-unlisted"
        for path in mapped_code:
            for reader in readers[path]:
                for family in _families_for_reader(families, reader):
                    selected[family["id"]] = family
    return list(selected.values()), None


def pytest_selectors(families: Iterable[dict[str, Any]]) -> list[str]:
    selectors: list[str] = []
    for family in families:
        if family.get("kind") != "pytest":
            continue
        selectors.extend(str(item) for item in family.get("selectors", []))
    return sorted(set(selectors))


def report(root: Path) -> dict[str, Any]:
    manifest = load_yaml(root / "tests/proof-estate.yaml")
    baseline = load_json(root / str(manifest["baseline_report"]))
    current = inventory(root)
    return {
        "baseline": baseline["counts"],
        "current": current["counts"],
        "by_kind": current["by_kind"],
    }


def assay(root: Path, *, evidence_class: str | None = None) -> list[dict[str, Any]]:
    manifest = load_yaml(root / "tests/proof-estate.yaml")
    corpus = load_yaml(root / str(manifest["effectiveness_corpus"]))
    cases = corpus.get("cases")
    if corpus.get("selection_frozen") is not True or not isinstance(cases, list):
        raise GovernanceError("effectiveness corpus is not frozen and complete")
    rows: list[dict[str, Any]] = []
    for case in cases:
        if evidence_class and case.get("class") != evidence_class:
            continue
        with tempfile.TemporaryDirectory(prefix="proof-assay-") as temporary:
            work = Path(temporary) / "repo"
            shutil.copytree(
                root,
                work,
                symlinks=True,
                ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__", ".pytest_cache"),
            )
            patch = root / str(case["patch"])
            patch_sha256 = hashlib.sha256(patch.read_bytes()).hexdigest()
            if case.get("patch_sha256") != patch_sha256:
                raise GovernanceError(f"assay patch digest drifted for {case['id']}")
            command = shlex.split(str(case["command"]))
            case_root = work / str(case.get("cwd", "."))
            baseline = _run(command, case_root, check=False)
            if baseline.returncode != 0:
                raise GovernanceError(
                    f"assay baseline failed for {case['id']}: "
                    + (baseline.stdout + "\n" + baseline.stderr).strip()
                )
            applied = _run(["git", "apply", str(patch)], work, check=False)
            if applied.returncode != 0:
                raise GovernanceError(
                    f"assay patch does not apply for {case['id']}: {applied.stderr.strip()}"
                )
            result = _run(command, case_root, check=False)
            output = (result.stdout + "\n" + result.stderr).encode()
            rows.append(
                {
                    "record_type": "effectiveness",
                    "evidence_id": case["id"],
                    "evidence_class": case["class"],
                    "observed": result.returncode != 0,
                    "detected_by": [case["owner"]] if result.returncode != 0 else [],
                    "command": case["command"],
                    "patch_sha256": patch_sha256,
                    "output_sha256": hashlib.sha256(output).hexdigest(),
                    "assayed_on": date.today().isoformat(),
                }
            )
    return rows


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="test-governance")
    parser.add_argument(
        "--root",
        "--repo-root",
        dest="repo_root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    inventory_parser = subparsers.add_parser("inventory")
    inventory_parser.add_argument("--output", type=Path)
    subparsers.add_parser("validate")
    select_parser = subparsers.add_parser("select")
    selection = select_parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--tier", choices=("vital",))
    selection.add_argument("--changed-from")
    select_parser.add_argument("--format", choices=("json", "lines"), default="json")
    subparsers.add_parser("report")
    assay_parser = subparsers.add_parser("assay")
    assay_parser.add_argument(
        "--class",
        dest="evidence_class",
        choices=("historical_defect", "holdout_mutant"),
    )
    assay_parser.add_argument("--output", type=Path)
    subparsers.add_parser("reassess")
    timing_parser = subparsers.add_parser("timing")
    timing_parser.add_argument(
        "--samples",
        type=int,
        default=0,
        help=(f"run the full suite this many times first; {CONFIRMING_SAMPLES} confirm an overrun"),
    )
    args = parser.parse_args(argv)
    root = args.repo_root.resolve()
    try:
        if args.command == "inventory":
            payload = inventory(root)
            if args.output:
                output = args.output if args.output.is_absolute() else root / args.output
                _write_json(output, payload)
            print(json.dumps(payload, indent=2, sort_keys=True))
        elif args.command == "validate":
            print(json.dumps(validate(root), indent=2, sort_keys=True))
        elif args.command == "select":
            mode = "vital" if args.tier else "changed"
            families, widened = selected_families(root, mode, args.changed_from)
            if widened:
                print(f"TEST GOVERNANCE WIDENED TO FULL: {widened}", file=sys.stderr)
            if args.format == "lines":
                print("FULL" if widened else "FOCUSED")
                print(widened or f"locally admitted {mode} families")
                for selector in pytest_selectors(families):
                    print(selector)
            else:
                print(
                    json.dumps(
                        {"mode": mode, "widened": widened, "families": families},
                        indent=2,
                        sort_keys=True,
                    )
                )
        elif args.command == "report":
            print(json.dumps(report(root), indent=2, sort_keys=True))
        elif args.command == "assay":
            rows = assay(root, evidence_class=args.evidence_class)
            rendered = "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
            if args.output:
                output = args.output if args.output.is_absolute() else root / args.output
                output.write_text(rendered)
            print(rendered, end="")
        elif args.command == "reassess":
            summary = validate(root)
            print(json.dumps({**summary, **report(root)}, indent=2, sort_keys=True))
        elif args.command == "timing":
            if args.samples < 0:
                raise GovernanceError("--samples must not be negative")
            observed = timing(root, args.samples)
            print(json.dumps(observed, indent=2, sort_keys=True))
            print(f"TEST TIME {observed['state'].upper()} budget={observed.get('budget', 'n/a')}")
            if observed["state"] == "fail":
                return 1
        return 0
    except GovernanceError as exc:
        print(f"TEST GOVERNANCE ERROR {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
