"""Deterministic inventory, validation, selection, and reporting for proof estates."""

from __future__ import annotations

import argparse
import ast
import fnmatch
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

SCHEMA_VERSION = 1
TIERS = {"full", "vital"}
EVIDENCE_CLASSES = {"historical_defect", "holdout_mutant"}
FAMILY_KEYS = {
    "id",
    "kind",
    "selectors",
    "source_paths",
    "covers",
    "contract",
    "risk_class",
    "oracle",
    "tiers",
    "runner",
    "admission",
    "historical_evidence",
    "mutation_evidence",
}
EVIDENCE_KEYS = {
    "record_type",
    "evidence_class",
    "evidence_id",
    "candidate_sha256",
    "manifest_sha256",
    "inventory_sha256",
    "command",
    "expected",
    "observed",
    "detected",
    "detected_by",
    "output_sha256",
    "denominator",
}
AUDIT_KEYS = {
    "record_type",
    "evidence_id",
    "candidate_sha256",
    "manifest_sha256",
    "inventory_sha256",
    "disposition",
    "denominator_type",
    "denominator",
    "rationale",
}


class GovernanceError(RuntimeError):
    """A proof-estate contract is malformed or stale."""


@dataclass(frozen=True)
class Estate:
    root: Path
    manifest_path: Path
    manifest: dict[str, Any]
    inventory: dict[str, Any]
    manifest_sha256: str
    inventory_sha256: str
    candidate_sha256: str


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise GovernanceError(f"path escapes repository root: {path}") from exc


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise GovernanceError(f"{label} must be a mapping")
    return value


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise GovernanceError(f"{label} must be a non-empty string")
    return value


def _require_string_list(value: Any, label: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not allow_empty and not value):
        suffix = "" if allow_empty else " non-empty"
        raise GovernanceError(f"{label} must be a{suffix} list")
    result: list[str] = []
    for index, item in enumerate(value):
        result.append(_require_string(item, f"{label}[{index}]"))
    if len(result) != len(set(result)):
        raise GovernanceError(f"{label} contains duplicates")
    return result


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise GovernanceError(f"missing manifest: {_display(path)}")
    try:
        loaded = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        raise GovernanceError(f"invalid YAML in {_display(path)}: {exc}") from exc
    return _require_mapping(loaded, "manifest")


def _display(path: Path) -> str:
    try:
        return path.relative_to(Path.cwd()).as_posix()
    except ValueError:
        return path.as_posix()


def _test_definitions(path: Path, root: Path) -> list[str]:
    relative = _relative(root, path)
    try:
        tree = ast.parse(path.read_text(), filename=relative)
    except (OSError, SyntaxError) as exc:
        raise GovernanceError(f"cannot inventory {relative}: {exc}") from exc

    definitions: list[str] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith(
            "test_"
        ):
            definitions.append(f"{relative}::{node.name}")
        elif isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            for child in node.body:
                if isinstance(
                    child, (ast.FunctionDef, ast.AsyncFunctionDef)
                ) and child.name.startswith("test_"):
                    definitions.append(f"{relative}::{node.name}::{child.name}")
    return definitions


def _inventory(root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    config = _require_mapping(manifest.get("inventory"), "inventory")
    test_roots = _require_string_list(config.get("test_roots"), "inventory.test_roots")
    gate_files = _require_string_list(config.get("gate_files"), "inventory.gate_files")
    hook_files = _require_string_list(config.get("hook_files"), "inventory.hook_files")

    test_files: list[str] = []
    test_definitions: list[str] = []
    for relative_root in test_roots:
        test_root = root / relative_root
        if not test_root.is_dir():
            raise GovernanceError(f"missing test root: {relative_root}")
        for path in sorted(test_root.rglob("test_*.py")):
            if "fixtures" in path.relative_to(test_root).parts or "__pycache__" in path.parts:
                continue
            relative = _relative(root, path)
            definitions = _test_definitions(path, root)
            if definitions:
                test_files.append(relative)
                test_definitions.extend(definitions)

    gates: list[str] = []
    for relative in gate_files:
        path = root / relative
        if not path.is_file():
            raise GovernanceError(f"missing gate file: {relative}")
        gates.extend(re.findall(r"\brun_gate\s+([A-Za-z0-9_-]+)", path.read_text()))

    hook_commands: list[str] = []
    for relative in hook_files:
        path = root / relative
        if not path.is_file():
            raise GovernanceError(f"missing hook file: {relative}")
        for raw_line in path.read_text().splitlines():
            line = raw_line.strip()
            if line.startswith("./bin/"):
                hook_commands.append(line)

    return {
        "test_files": sorted(test_files),
        "test_definitions": sorted(test_definitions),
        "check_gates": sorted(set(gates)),
        "hook_commands": sorted(set(hook_commands)),
        "counts": {
            "test_files": len(test_files),
            "test_definitions": len(test_definitions),
            "check_gates": len(set(gates)),
            "hook_commands": len(set(hook_commands)),
        },
    }


def _candidate_sha256(
    root: Path, manifest_path: Path, manifest: dict[str, Any], inventory: dict[str, Any]
) -> str:
    config = _require_mapping(manifest.get("inventory"), "inventory")
    patterns = _require_string_list(config.get("candidate_paths"), "inventory.candidate_paths")
    paths = {manifest_path.resolve()}
    for relative in inventory["test_files"]:
        paths.add((root / relative).resolve())
    for pattern in patterns:
        matches = sorted(root.glob(pattern))
        if not matches:
            raise GovernanceError(f"candidate path pattern matches nothing: {pattern}")
        paths.update(path.resolve() for path in matches if path.is_file())

    digest = hashlib.sha256()
    for path in sorted(paths):
        relative = _relative(root, path)
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def load_estate(root: Path, manifest_path: Path) -> Estate:
    root = root.resolve()
    manifest_path = manifest_path.resolve()
    manifest = _load_yaml(manifest_path)
    inventory = _inventory(root, manifest)
    return Estate(
        root=root,
        manifest_path=manifest_path,
        manifest=manifest,
        inventory=inventory,
        manifest_sha256=_file_sha256(manifest_path),
        inventory_sha256=_canonical_sha256(inventory),
        candidate_sha256=_candidate_sha256(root, manifest_path, manifest, inventory),
    )


def _selector_claims(selector: str, proof: str) -> bool:
    return proof == selector or proof.startswith(f"{selector}::")


def _validate_family(family: Any, index: int, estate: Estate) -> tuple[str, set[str]]:
    item = _require_mapping(family, f"families[{index}]")
    missing = FAMILY_KEYS - item.keys()
    unknown = item.keys() - FAMILY_KEYS
    if missing or unknown:
        raise GovernanceError(
            f"families[{index}] keys differ: missing={sorted(missing)} unknown={sorted(unknown)}"
        )

    family_id = _require_string(item["id"], f"families[{index}].id")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", family_id):
        raise GovernanceError(f"family id is not a lowercase slug: {family_id}")
    kind = _require_string(item["kind"], f"family {family_id} kind")
    if kind != "pytest":
        raise GovernanceError(f"family {family_id} uses unsupported kind: {kind}")

    selectors = _require_string_list(item["selectors"], f"family {family_id} selectors")
    _require_string_list(item["source_paths"], f"family {family_id} source_paths")
    _require_string(item["covers"], f"family {family_id} covers")
    _require_string(item["contract"], f"family {family_id} contract")
    _require_string(item["risk_class"], f"family {family_id} risk_class")
    _require_string(item["oracle"], f"family {family_id} oracle")

    tiers = set(_require_string_list(item["tiers"], f"family {family_id} tiers"))
    if not tiers <= TIERS or "full" not in tiers:
        raise GovernanceError(
            f"family {family_id} tiers must contain full and only {sorted(TIERS)}"
        )

    runner = _require_mapping(item["runner"], f"family {family_id} runner")
    if set(runner) != {"kind", "selectors"}:
        raise GovernanceError(f"family {family_id} runner requires only kind and selectors")
    if runner["kind"] != "pytest":
        raise GovernanceError(f"family {family_id} has unsupported runner: {runner['kind']}")
    runner_selectors = _require_string_list(
        runner["selectors"], f"family {family_id} runner selectors"
    )
    if runner_selectors != selectors:
        raise GovernanceError(f"family {family_id} runner selectors differ from family selectors")

    admission = _require_mapping(item["admission"], f"family {family_id} admission")
    if "vital" in tiers:
        if set(admission) != {"red_witness", "nearest_overlap", "distinct_value"}:
            raise GovernanceError(f"vital family {family_id} has incomplete admission evidence")
        for key in admission:
            _require_string(admission[key], f"family {family_id} admission.{key}")
    elif set(admission) != {"state", "reason"} or admission.get("state") != "full-only":
        raise GovernanceError(f"full-only family {family_id} needs state and reason")

    _require_string_list(
        item["historical_evidence"],
        f"family {family_id} historical_evidence",
        allow_empty=True,
    )
    _require_string_list(
        item["mutation_evidence"],
        f"family {family_id} mutation_evidence",
        allow_empty=True,
    )

    claimed: set[str] = set()
    for selector in selectors:
        matches = {
            proof
            for proof in estate.inventory["test_definitions"]
            if _selector_claims(selector, proof)
        }
        if not matches:
            raise GovernanceError(f"family {family_id} selector matches no proof: {selector}")
        claimed.update(matches)
    return family_id, claimed


def _load_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    if not path.is_file():
        raise GovernanceError(f"missing {label}: {_display(path)}")
    records: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(path.read_text().splitlines(), 1):
        if not raw_line.strip():
            continue
        try:
            record = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            raise GovernanceError(f"invalid {label} JSON on line {line_number}: {exc}") from exc
        records.append(_require_mapping(record, f"{label} line {line_number}"))
    return records


def _load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise GovernanceError(f"missing {label}: {_display(path)}")
    try:
        loaded = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise GovernanceError(f"invalid {label} JSON: {exc}") from exc
    return _require_mapping(loaded, label)


def _validate_digest_bindings(record: dict[str, Any], label: str, estate: Estate) -> None:
    for key, expected in (
        ("candidate_sha256", estate.candidate_sha256),
        ("manifest_sha256", estate.manifest_sha256),
        ("inventory_sha256", estate.inventory_sha256),
    ):
        if record.get(key) != expected:
            raise GovernanceError(f"{label} has stale {key}")


def _validate_audit(estate: Estate) -> None:
    config = _require_mapping(estate.manifest.get("audit"), "audit")
    if set(config) != {"ledger_file"}:
        raise GovernanceError("audit requires only ledger_file")
    path = estate.root / _require_string(config["ledger_file"], "audit.ledger_file")
    seen: set[str] = set()
    for index, record in enumerate(_load_jsonl(path, "audit ledger")):
        if set(record) != AUDIT_KEYS:
            raise GovernanceError(f"audit record {index} has wrong keys")
        if record["record_type"] != "estate_disposition":
            raise GovernanceError(f"audit record {index} has wrong record_type")
        evidence_id = _require_string(record["evidence_id"], f"audit record {index} id")
        if evidence_id in seen:
            raise GovernanceError(f"duplicate audit evidence_id: {evidence_id}")
        seen.add(evidence_id)
        _validate_digest_bindings(record, f"audit {evidence_id}", estate)
        if record["disposition"] not in {"retain", "replace", "consolidate", "remove"}:
            raise GovernanceError(f"audit {evidence_id} has invalid disposition")
        _require_string(record["denominator_type"], f"audit {evidence_id} denominator_type")
        if not isinstance(record["denominator"], int) or record["denominator"] < 1:
            raise GovernanceError(f"audit {evidence_id} has invalid denominator")
        _require_string(record["rationale"], f"audit {evidence_id} rationale")


def _validate_reports(estate: Estate, families: list[dict[str, Any]]) -> None:
    config = _require_mapping(estate.manifest.get("reports"), "reports")
    expected_config = {"baseline_file", "selection_file", "timing_file"}
    if set(config) != expected_config:
        raise GovernanceError(f"reports requires {sorted(expected_config)}")

    baseline = _load_json(
        estate.root / _require_string(config["baseline_file"], "reports.baseline_file"),
        "baseline report",
    )
    expected_baseline_keys = {
        "record_type",
        "schema_version",
        "candidate_sha256",
        "manifest_sha256",
        "inventory_sha256",
        "counts",
    }
    if set(baseline) != expected_baseline_keys:
        raise GovernanceError("baseline report has wrong keys")
    _validate_digest_bindings(baseline, "baseline report", estate)
    if baseline["record_type"] != "proof-estate-baseline":
        raise GovernanceError("baseline report has wrong record_type")
    if baseline["schema_version"] != SCHEMA_VERSION:
        raise GovernanceError("baseline report has wrong schema_version")
    if baseline["counts"] != estate.inventory["counts"]:
        raise GovernanceError("baseline report counts are stale")

    selection = _load_json(
        estate.root / _require_string(config["selection_file"], "reports.selection_file"),
        "selection report",
    )
    expected_selection_keys = {
        "record_type",
        "lane",
        "reason",
        "candidate_sha256",
        "manifest_sha256",
        "inventory_sha256",
        "families",
        "selectors",
    }
    if set(selection) != expected_selection_keys:
        raise GovernanceError("selection report has wrong keys")
    _validate_digest_bindings(selection, "selection report", estate)
    if selection["record_type"] != "selection":
        raise GovernanceError("selection report has wrong record_type")
    expected_families = sorted(family["id"] for family in families if "vital" in family["tiers"])
    expected_selectors = sorted(
        {
            selector
            for family in families
            if "vital" in family["tiers"]
            for selector in family["runner"]["selectors"]
        }
    )
    if expected_families:
        if selection["lane"] != "vital":
            raise GovernanceError("selection report does not describe the admitted vital lane")
    elif selection["lane"] != "full-only":
        raise GovernanceError("selection report must describe the full-only state")
    if selection["families"] != expected_families or selection["selectors"] != expected_selectors:
        raise GovernanceError("selection report is stale")
    _require_string(selection["reason"], "selection report reason")

    timing = _load_json(
        estate.root / _require_string(config["timing_file"], "reports.timing_file"),
        "timing report",
    )
    expected_timing_keys = {
        "record_type",
        "candidate_sha256",
        "manifest_sha256",
        "inventory_sha256",
        "measurements",
        "universal_budget",
    }
    if set(timing) != expected_timing_keys:
        raise GovernanceError("timing report has wrong keys")
    _validate_digest_bindings(timing, "timing report", estate)
    if timing["record_type"] != "local-timing-observations":
        raise GovernanceError("timing report has wrong record_type")
    if timing["universal_budget"] is not None:
        raise GovernanceError("timing report must not declare a universal budget")
    if not isinstance(timing["measurements"], list):
        raise GovernanceError("timing report measurements must be a list")
    for index, measurement in enumerate(timing["measurements"]):
        item = _require_mapping(measurement, f"timing measurement {index}")
        if set(item) != {"case", "command", "measurement", "seconds"}:
            raise GovernanceError(f"timing measurement {index} has wrong keys")
        for key in ("case", "command", "measurement"):
            _require_string(item[key], f"timing measurement {index} {key}")
        if not isinstance(item["seconds"], (int, float)) or item["seconds"] < 0:
            raise GovernanceError(f"timing measurement {index} has invalid seconds")


def _validate_effectiveness(estate: Estate, families: list[dict[str, Any]]) -> None:
    config = _require_mapping(estate.manifest.get("effectiveness"), "effectiveness")
    evidence_file = estate.root / _require_string(
        config.get("evidence_file"), "effectiveness.evidence_file"
    )
    required_classes = set(
        _require_string_list(config.get("required_classes"), "effectiveness.required_classes")
    )
    if required_classes != EVIDENCE_CLASSES:
        raise GovernanceError(f"effectiveness.required_classes must be {sorted(EVIDENCE_CLASSES)}")
    references: dict[str, str] = {}
    vital_ids = {family["id"] for family in families if "vital" in family["tiers"]}
    for family in families:
        for evidence_id in family["historical_evidence"] + family["mutation_evidence"]:
            if evidence_id in references:
                raise GovernanceError(f"effectiveness id is claimed twice: {evidence_id}")
            references[evidence_id] = family["id"]

    records = _load_jsonl(evidence_file, "effectiveness evidence")
    if not vital_ids:
        if records or references:
            raise GovernanceError("a full-only estate cannot claim effectiveness evidence")
        return
    if not records:
        raise GovernanceError("effectiveness evidence is empty")

    seen: set[str] = set()
    class_counts: dict[str, int] = {value: 0 for value in EVIDENCE_CLASSES}
    for index, record in enumerate(records):
        if set(record) != EVIDENCE_KEYS:
            raise GovernanceError(f"effectiveness record {index} has wrong keys")
        if record["record_type"] != "effectiveness":
            raise GovernanceError(f"effectiveness record {index} has wrong record_type")
        evidence_class = record["evidence_class"]
        if evidence_class not in EVIDENCE_CLASSES:
            raise GovernanceError(f"effectiveness record {index} has unknown class")
        evidence_id = _require_string(record["evidence_id"], f"effectiveness record {index} id")
        if evidence_id in seen:
            raise GovernanceError(f"duplicate effectiveness id: {evidence_id}")
        seen.add(evidence_id)
        class_counts[evidence_class] += 1
        for key, expected in (
            ("candidate_sha256", estate.candidate_sha256),
            ("manifest_sha256", estate.manifest_sha256),
            ("inventory_sha256", estate.inventory_sha256),
        ):
            if record[key] != expected:
                raise GovernanceError(f"effectiveness {evidence_id} has stale {key}")
        if record["detected"] is not True:
            raise GovernanceError(f"effectiveness {evidence_id} was not detected")
        detected_by = _require_string_list(
            record["detected_by"], f"effectiveness {evidence_id} detected_by"
        )
        if not set(detected_by) <= vital_ids:
            raise GovernanceError(f"effectiveness {evidence_id} was not detected by the vital lane")
        if references.get(evidence_id) not in detected_by:
            raise GovernanceError(
                f"effectiveness {evidence_id} is not bound to its claiming family"
            )
        for key in ("command", "expected", "observed", "output_sha256"):
            _require_string(record[key], f"effectiveness {evidence_id} {key}")
        if not isinstance(record["denominator"], int) or record["denominator"] < 1:
            raise GovernanceError(f"effectiveness {evidence_id} has invalid denominator")

    if seen != set(references):
        raise GovernanceError(
            f"effectiveness references differ: manifest_only={sorted(set(references) - seen)} "
            f"evidence_only={sorted(seen - set(references))}"
        )
    for record in records:
        if record["denominator"] != class_counts[record["evidence_class"]]:
            raise GovernanceError(f"effectiveness {record['evidence_id']} denominator is stale")


def validate_estate(estate: Estate) -> dict[str, Any]:
    if estate.manifest.get("schema_version") != SCHEMA_VERSION:
        raise GovernanceError(f"schema_version must be {SCHEMA_VERSION}")

    baseline = _require_mapping(estate.manifest.get("baseline"), "baseline")
    expected_baseline_keys = {
        "test_files",
        "test_definitions",
        "check_gates",
        "hook_commands",
    }
    if set(baseline) != expected_baseline_keys:
        raise GovernanceError("baseline keys differ from the inventory count contract")
    if baseline != estate.inventory["counts"]:
        raise GovernanceError(
            f"baseline is stale: declared={baseline} observed={estate.inventory['counts']}"
        )

    surfaces = _require_mapping(estate.manifest.get("surfaces"), "surfaces")
    if set(surfaces) != {"check_gates", "hook_commands"}:
        raise GovernanceError("surfaces requires check_gates and hook_commands")
    for key in ("check_gates", "hook_commands"):
        declared = sorted(_require_string_list(surfaces[key], f"surfaces.{key}"))
        if declared != estate.inventory[key]:
            raise GovernanceError(
                f"surface inventory drift for {key}: declared={declared} "
                f"observed={estate.inventory[key]}"
            )

    families_raw = estate.manifest.get("families")
    if not isinstance(families_raw, list) or not families_raw:
        raise GovernanceError("families must be a non-empty list")
    families = [
        _require_mapping(item, f"families[{index}]") for index, item in enumerate(families_raw)
    ]
    ids: set[str] = set()
    claims: dict[str, list[str]] = {}
    for index, family in enumerate(families):
        family_id, family_claims = _validate_family(family, index, estate)
        if family_id in ids:
            raise GovernanceError(f"duplicate family id: {family_id}")
        ids.add(family_id)
        for proof in family_claims:
            claims.setdefault(proof, []).append(family_id)

    missing = sorted(set(estate.inventory["test_definitions"]) - claims.keys())
    multiple = sorted(proof for proof, owners in claims.items() if len(owners) != 1)
    if missing or multiple:
        raise GovernanceError(
            f"proof ownership invalid: missing={missing[:5]} multiple={multiple[:5]}"
        )

    _validate_audit(estate)
    _validate_reports(estate, families)
    _validate_effectiveness(estate, families)

    return {
        "schema_version": SCHEMA_VERSION,
        "manifest_sha256": estate.manifest_sha256,
        "inventory_sha256": estate.inventory_sha256,
        "candidate_sha256": estate.candidate_sha256,
        "counts": estate.inventory["counts"],
        "families": len(families),
        "vital_families": sum("vital" in family["tiers"] for family in families),
    }


def _changed_paths(root: Path, reference: str) -> list[str]:
    verified = subprocess.run(
        ["git", "rev-parse", "--verify", f"{reference}^{{commit}}"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if verified.returncode != 0:
        raise GovernanceError(f"cannot resolve changed-from reference: {reference}")
    diff = subprocess.run(
        ["git", "diff", "--name-only", reference, "--"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if diff.returncode != 0:
        raise GovernanceError(f"cannot compute changes from {reference}: {diff.stderr.strip()}")
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if untracked.returncode != 0:
        raise GovernanceError(f"cannot inventory untracked paths: {untracked.stderr.strip()}")
    return sorted(set(diff.stdout.splitlines()) | set(untracked.stdout.splitlines()))


def _matches(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def _full_selection(
    estate: Estate | None, reason: str, changed: list[str] | None = None
) -> dict[str, Any]:
    return {
        "mode": "full",
        "reason": reason,
        "families": [],
        "selectors": [],
        "changed_paths": changed or [],
        "manifest_sha256": estate.manifest_sha256 if estate else None,
        "inventory_sha256": estate.inventory_sha256 if estate else None,
        "candidate_sha256": estate.candidate_sha256 if estate else None,
    }


def select_estate(estate: Estate, *, tier: str | None, changed_from: str | None) -> dict[str, Any]:
    validate_estate(estate)
    families: list[dict[str, Any]] = estate.manifest["families"]
    changed: list[str] = []
    if tier == "vital":
        selected = [family for family in families if "vital" in family["tiers"]]
        reason = "all locally admitted vital families"
    elif changed_from is not None:
        changed = _changed_paths(estate.root, changed_from)
        if not changed:
            return _full_selection(estate, "no changed paths were found", changed)
        selected_ids: set[str] = set()
        unmapped: list[str] = []
        for path in changed:
            matched = [family for family in families if _matches(path, family["source_paths"])]
            if not matched:
                unmapped.append(path)
            selected_ids.update(family["id"] for family in matched)
        if unmapped:
            return _full_selection(
                estate,
                f"changed paths are unmapped: {', '.join(unmapped)}",
                changed,
            )
        selected = [family for family in families if family["id"] in selected_ids]
        reason = f"union of mappings for {len(changed)} changed path(s)"
    else:
        raise GovernanceError("selection requires --tier vital or --changed-from <ref>")

    if not selected:
        return _full_selection(estate, "the requested lane has no admitted families", changed)
    selectors = sorted(
        {selector for family in selected for selector in family["runner"]["selectors"]}
    )
    return {
        "mode": "focused",
        "reason": reason,
        "families": sorted(family["id"] for family in selected),
        "selectors": selectors,
        "changed_paths": changed,
        "manifest_sha256": estate.manifest_sha256,
        "inventory_sha256": estate.inventory_sha256,
        "candidate_sha256": estate.candidate_sha256,
    }


def _render_selection(selection: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(selection, indent=2, sort_keys=True))
        return
    print(selection["mode"].upper())
    print(selection["reason"])
    for selector in selection["selectors"]:
        print(selector)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--manifest", type=Path, default=Path("tests/proof-estate.yaml"))
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("inventory")
    subparsers.add_parser("validate")
    select = subparsers.add_parser("select")
    group = select.add_mutually_exclusive_group(required=True)
    group.add_argument("--tier", choices=("vital",))
    group.add_argument("--changed-from")
    select.add_argument("--format", choices=("json", "lines"), default="json")
    subparsers.add_parser("report")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    root = args.root.resolve()
    manifest_path = args.manifest
    if not manifest_path.is_absolute():
        manifest_path = root / manifest_path
    estate: Estate | None = None
    try:
        estate = load_estate(root, manifest_path)
        if args.command == "inventory":
            payload = {
                **estate.inventory,
                "manifest_sha256": estate.manifest_sha256,
                "inventory_sha256": estate.inventory_sha256,
                "candidate_sha256": estate.candidate_sha256,
            }
            print(json.dumps(payload, indent=2, sort_keys=True))
        elif args.command == "validate":
            summary = validate_estate(estate)
            print(
                "TEST GOVERNANCE PASS "
                f"families={summary['families']} proofs={summary['counts']['test_definitions']} "
                f"vital={summary['vital_families']}"
            )
        elif args.command == "select":
            try:
                selection = select_estate(estate, tier=args.tier, changed_from=args.changed_from)
            except GovernanceError as exc:
                selection = _full_selection(estate, f"governance fallback: {exc}")
            _render_selection(selection, args.format)
        elif args.command == "report":
            summary = validate_estate(estate)
            print(json.dumps(summary, indent=2, sort_keys=True))
    except GovernanceError as exc:
        if args.command == "select":
            _render_selection(_full_selection(estate, f"governance fallback: {exc}"), args.format)
            return 0
        print(f"TEST GOVERNANCE ERROR {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
