"""Opt-in isolated migration and maintenance of proposed collaboration records.

This module is not wired into current kickoff or its live policies. It does not
allocate leases, authenticate writers, or turn a rehearsal into adoption.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import uuid
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import yaml

from agentic_starter import log_blocks
from agentic_starter import multioperator_transition as transition

FORMAT = "starter.multioperator.v1"
SLUG = re.compile(r"[a-z]+(?:-[a-z]+){2}")
STATES = {"⏳": "not-started", "⬅️": "next", "🚧": "in-progress", "✅": "completed"}
PHASE_ROW = re.compile(r"\[Phase (\d+(?:\.\d+)*)\]\(phase-\1\.md\)")
LOG_HEADING = re.compile(r"^## \d{4}-\d{2}-\d{2} \d{2}:\d{2} — ")


class Refusal(ValueError):
    """A concrete refusal; no authority is inferred from caller-supplied text."""


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise Refusal(reason)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encode(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode()


def unique_pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result = dict(items)
    require(len(result) == len(items), "duplicate JSON key")
    return result


class PhaseLoader(yaml.SafeLoader):
    """Reject ambiguous metadata rather than accepting the last duplicate key."""

    def construct_mapping(self, node: Any, deep: bool = False) -> dict[str, Any]:
        pairs = [
            (self.construct_object(k, deep=deep), self.construct_object(v, deep=deep))
            for k, v in node.value
        ]
        return unique_pairs(pairs)


def load(path: Path) -> Any:
    require(not path.is_symlink(), f"symlink record refused: {path.name}")
    return json.loads(path.read_bytes(), object_pairs_hook=unique_pairs)


def safe(root: Path, relative: str) -> Path:
    base = root.resolve()
    path = base / relative
    require(path.resolve().is_relative_to(base), "path escapes target")
    for component in (path, *path.parents):
        if component == base:
            break
        require(not component.is_symlink(), f"symlink destination refused: {relative}")
    return path


def publish(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def frontmatter(data: bytes) -> tuple[dict[str, Any], str]:
    parts = data.decode().split("---\n", 2)
    require(len(parts) == 3 and parts[0] == "", "phase lacks YAML frontmatter")
    metadata = yaml.load(parts[1], Loader=PhaseLoader)
    require(isinstance(metadata, dict), "phase frontmatter is not a mapping")
    return metadata, parts[2]


def phase_bytes(metadata: dict[str, Any], body: str) -> bytes:
    return ("---\n" + yaml.safe_dump(metadata, sort_keys=False) + "---\n" + body).encode()


def log_record(metadata: dict[str, Any], body: bytes) -> bytes:
    # JSON is a YAML mapping too; a single metadata line leaves the Markdown body exact.
    return b"---\n" + json.dumps(metadata, sort_keys=True).encode() + b"\n---\n" + body


def read_log(data: bytes) -> tuple[dict[str, Any], bytes]:
    parts = data.split(b"\n---\n", 1)
    require(len(parts) == 2 and parts[0].startswith(b"---\n"), "invalid log envelope")
    metadata = json.loads(parts[0][4:])
    require(digest(parts[1]) == metadata["body_sha256"], "log body digest mismatch")
    return metadata, parts[1]


def split_log(data: bytes) -> list[bytes]:
    """Split only real entry headings, retaining preamble and every source byte."""
    offsets, position, fence = [0], 0, None
    for line in data.decode().splitlines(keepends=True):
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            token = marker[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
        elif fence is None and LOG_HEADING.match(line) and position:
            offsets.append(position)
        position += len(line.encode())
    return [data[a:b] for a, b in zip(offsets, offsets[1:] + [len(data)], strict=True)]


def records(root: Path) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    require(load(safe(root, "collaboration/manifest.json"))["format"] == FORMAT, "wrong format")
    phases = {}
    for path in sorted(safe(root, "plan/phases").glob("*.md")):
        require(not path.is_symlink(), "symlink phase refused")
        meta, _ = frontmatter(path.read_bytes())
        identifier = meta["id"]
        require(bool(SLUG.fullmatch(identifier)), "invalid permanent phase id")
        require(path.name == identifier + ".md" and identifier not in phases, "duplicate phase id")
        require(
            "status" not in meta and "owner" not in meta, "phase metadata duplicates event state"
        )
        try:
            Fraction(meta["order"])
        except (ValueError, TypeError, ZeroDivisionError) as exc:
            raise Refusal("invalid rational order key") from exc
        phases[identifier] = meta
    require(bool(phases), "empty phase inventory")
    events = []
    for path in sorted(safe(root, "plan/events").glob("*.json")):
        event = load(path)
        require(path.stem == event["id"], "event filename/id mismatch")
        events.append(event)
    return phases, events


def fold(phases: dict[str, dict[str, Any]], events: list[dict[str, Any]]) -> dict[str, Any]:
    heads = {}
    for identifier, phase in phases.items():
        require(isinstance(phase["order"], str), "order key must be a rational string")
        require(
            isinstance(phase.get("informs"), list) and all(i in phases for i in phase["informs"]),
            "unknown informed phase",
        )
        deps = phase["depends_on"]
        require(isinstance(deps, list) and all(d in phases for d in deps), "unknown dependency")
        parent = phase.get("parent")
        require(parent is None or parent in phases, "unknown parent")
        require(parent != identifier and identifier not in deps, "self cycle")
        for dependency in deps:
            require(
                (Fraction(phases[dependency]["order"]), dependency)
                <= (Fraction(phase["order"]), identifier),
                "dependency ordered after dependent",
            )
        relevant = [event for event in events if event["phase"] == identifier]
        require(bool(relevant), "phase has no genesis event")
        by_id = {event["id"]: event for event in relevant}
        require(len(by_id) == len(relevant), "duplicate event id")
        seen_previous = set()
        for event in relevant:
            require(bool(re.fullmatch(r"[0-9a-f]{32}", event["id"])), "invalid event id")
            require(event["state"] in STATES.values(), "unknown phase state")
            require(
                bool(event.get("writer")) and bool(event.get("reason")), "missing event attribution"
            )
            previous = event["previous"]
            require(previous not in seen_previous, "competing phase heads; coordinate ownership")
            seen_previous.add(previous)
            if previous is None:
                require(event["from"] is None, "invalid genesis")
            else:
                require(previous in by_id, "missing event predecessor")
                old = by_id[previous]
                require(event["from"] == old["state"], "stale phase state")
                allowed = {
                    "not-started": {"next", "in-progress"},
                    "next": {"not-started", "in-progress"},
                    "in-progress": {"in-progress", "completed"},
                    "completed": set(),
                }
                require(event["state"] in allowed[old["state"]], "invalid lifecycle transition")
                if event["state"] == "in-progress":
                    require(
                        bool(event.get("owner")) and bool(event.get("claim")),
                        "missing owner/claim evidence",
                    )
                if old.get("owner") and event.get("owner") != old["owner"]:
                    require(
                        bool(event.get("release")) and bool(event.get("claim")),
                        "handoff lacks release/claim",
                    )
        genesis = [e for e in relevant if e["previous"] is None]
        require(len(genesis) == 1, "phase requires one genesis")
        visited, current = set(), genesis[0]
        while True:
            require(current["id"] not in visited, "event cycle")
            visited.add(current["id"])
            children = [e for e in relevant if e["previous"] == current["id"]]
            if not children:
                break
            current = children[0]
        require(len(visited) == len(relevant), "disconnected event history")
        heads[identifier] = current
    require(all(e["phase"] in phases for e in events), "event names absent phase")
    visiting, visited = set(), set()

    def visit(identifier: str) -> None:
        require(identifier not in visiting, "phase graph cycle")
        if identifier in visited:
            return
        visiting.add(identifier)
        phase = phases[identifier]
        for target in phase["depends_on"] + ([phase["parent"]] if phase.get("parent") else []):
            visit(target)
        visiting.remove(identifier)
        visited.add(identifier)

    for identifier in phases:
        visit(identifier)
        if heads[identifier]["state"] in {"in-progress", "completed"}:
            require(
                all(heads[d]["state"] == "completed" for d in phases[identifier]["depends_on"]),
                "work precedes completed dependencies",
            )
        for event in [e for e in events if e["phase"] == identifier]:
            if event["previous"] is not None and event["state"] == "completed":
                require(bool(event.get("acceptance")), "completion lacks acceptance reference")
        if heads[identifier]["state"] == "completed":
            require(
                all(
                    heads[c]["state"] == "completed"
                    for c in phases
                    if phases[c].get("parent") == identifier
                ),
                "parent has incomplete children",
            )
    owners = [h.get("owner") for h in heads.values() if h["state"] == "next"]
    require(len(owners) == len(set(owners)), "multiple next selections for one owner")
    return heads


def terminal_body(body: bytes) -> None:
    errors = log_blocks.terminal_blocks_missing_lessons(log_blocks.parse(body.decode()).blocks)
    require(not errors, "terminal body lacks Lessons witness")


def logs(root: Path) -> list[tuple[dict[str, Any], bytes]]:
    entries = []
    for path in safe(root, "log/entries").glob("*.md"):
        metadata, body = read_log(path.read_bytes())
        require(path.stem == metadata["id"], "log filename/id mismatch")
        require(
            bool(metadata.get("writer")) and type(metadata["sequence"]) is int,
            "invalid log writer/sequence",
        )
        if "source_offset" not in metadata:
            terminal_body(body)
            instant = datetime.fromisoformat(metadata["at"])
            require(
                instant.tzinfo is not None
                and instant.astimezone(UTC).isoformat() == metadata["at"],
                "log timestamp is not canonical UTC",
            )
        entries.append((metadata, body))
    grouped: dict[str, list[dict[str, Any]]] = {}
    for metadata, _ in entries:
        grouped.setdefault(metadata["writer"], []).append(metadata)
    for group in grouped.values():
        group.sort(key=lambda m: m["sequence"])
        for index, item in enumerate(group, 1):
            require(item["sequence"] == index, "log writer sequence gap/duplicate")
            require(
                item["previous"] == (group[index - 2]["id"] if index > 1 else None),
                "log writer predecessor mismatch",
            )
            if index > 1:
                require(item["at"] >= group[index - 2]["at"], "writer clock moved backward")
    return sorted(entries, key=lambda pair: (pair[0]["at"], pair[0]["writer"], pair[0]["sequence"]))


def verify_acceptance_bytes(root: Path, event: dict[str, Any]) -> None:
    """Check retention, not semantic phase approval; live adapters still own that."""
    if event["previous"] is None or event["state"] != "completed":
        return
    reference = event["acceptance"]
    require(
        isinstance(reference, dict) and set(reference) == {"path", "sha256"},
        "completion requires retained acceptance bytes",
    )
    require(not Path(reference["path"]).is_absolute(), "acceptance reference must be repo-relative")
    artifact = safe(root, reference["path"])
    require(
        artifact.is_file() and digest(artifact.read_bytes()) == reference["sha256"],
        "acceptance artifact missing or mutated",
    )


def validate(root: Path) -> dict[str, Any]:
    require(
        (root / "AGENTS.md").is_file() and not (root / "AGENTS.md").is_symlink(),
        "AGENTS must be the regular primary constitution",
    )
    require(
        not (root / "CLAUDE.md").exists() and not (root / "CLAUDE.md").is_symlink(),
        "top-level CLAUDE alias must be absent",
    )
    phases, events = records(root)
    heads = fold(phases, events)
    for event in events:
        verify_acceptance_bytes(root, event)
    entries = logs(root)
    manifest = load(safe(root, "collaboration/manifest.json"))
    imported = sorted(
        (pair for pair in entries if pair[0].get("source_offset") is not None),
        key=lambda pair: pair[0]["source_offset"],
    )
    offset = 0
    for metadata, body in imported:
        require(
            metadata["source_offset"] == offset and metadata["writer"] == "unattributed-import",
            "historical offset/attribution mismatch",
        )
        offset += len(body)
    require(offset == manifest["original_log_bytes"], "historical log byte count mismatch")
    original = b"".join(body for _, body in imported)
    require(
        digest(original) == manifest["original_log_sha256"],
        "historical log reconstruction mismatch",
    )
    return {
        "phases": len(phases),
        "events": len(events),
        "log_entries": len(entries),
        "heads": heads,
        "historical_log_sha256": digest(original),
        "adopted": manifest["adopted"],
    }


def render(root: Path, check: bool = False) -> None:
    state = validate(root)
    phases, _ = records(root)
    ordered = sorted(phases, key=lambda p: (Fraction(phases[p]["order"]), p))
    table = (
        "# Phase projection (generated; never authority)\n\n"
        "| Phase | Title | State | Owner |\n|---|---|---|---|\n"
    )
    for identifier in ordered:
        h = state["heads"][identifier]
        table += (
            f"| {identifier} | {phases[identifier]['title']} | {h['state']} | "
            f"{h.get('owner') or 'unassigned'} |\n"
        )
    entries = logs(root)
    imports = sorted(
        (pair for pair in entries if "source_offset" in pair[0]),
        key=lambda pair: pair[0]["source_offset"],
    )
    bodies = imports + [pair for pair in entries if "source_offset" not in pair[0]]
    for name, data in [("PLAN.md", table.encode()), ("LOG.md", b"".join(b for _, b in bodies))]:
        path = safe(root, ".collaboration-views/" + name)
        if check:
            require(path.is_file() and path.read_bytes() == data, "stale generated projection")
        else:
            path.parent.mkdir(exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
                handle.write(data)
                temporary = Path(handle.name)
            temporary.replace(path)


def rewrite_links(text: str, path: Path, mapping: dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        target = match[1]
        # Only mechanical links, not unqualified prose or quoted historical ids.
        for old, new in mapping.items():
            target = re.sub(
                r"(?<![\w-])phase-" + re.escape(old) + r"\.md(?=#|$)",
                "phases/" + new + ".md",
                target,
            )
        if target.endswith("LOG.md"):
            target = target[:-6] + "log/README.md"
        if path.parent.as_posix() == "plan/phases" and not target.startswith(
            ("http:", "https:", "#")
        ):
            # Source files lived one directory shallower; phase-to-phase targets moved too.
            if target.startswith("phases/"):
                target = target[7:]
            elif target.startswith("../"):
                target = "../" + target
            elif target == "INDEX.md":
                target = "../INDEX.md"
        return "](" + target + ")"

    return re.sub(r"\]\(([^\s)]+)\)", replace, text)


def rehearse(source: Path, output: Path, mapping_path: Path) -> None:
    source, output = source.resolve(), output.absolute()
    require(not output.exists() and not output.is_symlink(), "output must be absent")
    require(output != source and not source.is_relative_to(output), "output overlaps source")
    compatibility = claude_compatibility()
    config = load(mapping_path)
    head = subprocess.check_output(
        ["git", "-C", str(source), "rev-parse", "HEAD"], text=True
    ).strip()
    archive = subprocess.check_output(["git", "-C", str(source), "archive", head])
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent, prefix=".migration-stage-") as temporary:
        root = Path(temporary)
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            for member in tar.getmembers():
                path = safe(root, member.name)
                if member.isdir():
                    path.mkdir(parents=True, exist_ok=True)
                elif member.issym():
                    require(
                        not Path(member.linkname).is_absolute()
                        and (path.parent / member.linkname).resolve().is_relative_to(root),
                        "archive symlink escapes rehearsal",
                    )
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.symlink_to(member.linkname)
                elif member.isfile():
                    body = tar.extractfile(member)
                    require(body is not None, "archive member missing")
                    publish(path, body.read())
                    path.chmod(member.mode)
                else:
                    raise Refusal("unsupported archive entry")
        require(not (root / "collaboration").exists(), "source already has collaboration records")
        plan = root / "plan"
        index = (plan / "INDEX.md").read_text()
        rows = {}
        section = index.split("## Phase Table", 1)
        require(len(section) == 2, "missing phase table")
        for line in section[1].split("\n## ", 1)[0].splitlines():
            match = PHASE_ROW.search(line)
            if match:
                marks = [m for m in STATES if m in line]
                require(len(marks) == 1 and match[1] not in rows, "ambiguous phase status")
                rows[match[1]] = STATES[marks[0]]
        mapping = config["phases"]
        require(
            set(mapping) == set(rows) and len(set(mapping.values())) == len(mapping),
            "mapping must cover every phase exactly once",
        )
        require(
            all(SLUG.fullmatch(value) for value in mapping.values()), "invalid permanent phase id"
        )
        phase_files = sorted(plan.glob("phase-*.md"))
        require({p.stem[6:] for p in phase_files} == set(rows), "phase files/table disagree")
        writer = config["writer"]
        require(
            isinstance(writer, str) and bool(writer.strip()), "explicit migration writer required"
        )
        new_phases, events = {}, []
        order = sorted(rows, key=lambda p: tuple(map(int, p.split("."))))
        for number, old in enumerate(order, 1):
            path = plan / ("phase-" + old + ".md")
            meta, body = frontmatter(path.read_bytes())
            require(str(meta["id"]) == old, "phase filename/id mismatch")
            owner = config.get("owners", {}).get(old)
            if rows[old] == "in-progress":
                checkpoint = config.get("active_checkpoints", {}).get(old, {})
                require(
                    checkpoint.get("terminal") is True
                    and bool(checkpoint.get("evidence"))
                    and bool(owner),
                    "active work lacks owner and terminal checkpoint",
                )
            for key in ("depends_on", "informs"):
                require(
                    isinstance(meta.get(key), list) and all(str(d) in mapping for d in meta[key]),
                    "unknown dependency/reference",
                )
                meta[key] = [mapping[str(d)] for d in meta[key]]
            parent = old.rsplit(".", 1)[0] if "." in old else None
            require(parent is None or parent in mapping, "missing direct parent")
            meta.update(id=mapping[old], order=str(number), parent=mapping.get(parent))
            require("status" not in meta and "owner" not in meta, "duplicate source state")
            name = "plan/phases/" + mapping[old] + ".md"
            new_phases[name] = phase_bytes(meta, rewrite_links(body, Path(name), mapping))
            events.append(
                {
                    "id": uuid.uuid5(uuid.NAMESPACE_URL, head + ":phase:" + old).hex,
                    "phase": mapping[old],
                    "previous": None,
                    "from": None,
                    "state": rows[old],
                    "owner": owner,
                    "writer": writer,
                    "reason": "Imported source state, not a new acceptance or lease",
                    "source_phase": old,
                }
            )
        original_log = (root / "LOG.md").read_bytes()
        for name, data in new_phases.items():
            publish(root / name, data)
        for event in events:
            publish(root / "plan/events" / (event["id"] + ".json"), encode(event))
        offset, previous = 0, None
        for sequence, body in enumerate(split_log(original_log), 1):
            identifier = uuid.uuid5(uuid.NAMESPACE_URL, head + ":log:" + str(offset)).hex
            metadata = {
                "id": identifier,
                "writer": "unattributed-import",
                "sequence": sequence,
                "previous": previous,
                "at": "import",
                "body_sha256": digest(body),
                "source_offset": offset,
            }
            publish(root / "log/entries" / (identifier + ".md"), log_record(metadata, body))
            offset += len(body)
            previous = identifier
        # Historical prose/evidence is deliberately not rewritten.
        excluded = {"LOG.md", "plan/INDEX.md"}
        report = []
        for path in root.rglob("*.md"):
            relative = path.relative_to(root)
            if (
                path.is_symlink()
                or str(relative) in excluded
                or relative.parts[0]
                in {
                    "log",
                    "docs",
                    "lessons",
                    "lessons-archived",
                    "user-actions",
                    "user-actions-archived",
                    "reports",
                    "plan",
                }
            ):
                continue
            text = path.read_text()
            updated = rewrite_links(text, relative, mapping)
            if updated != text:
                path.write_text(updated)
        for path in phase_files:
            path.unlink()
        (root / "LOG.md").unlink()
        # Retain handwritten context in its one home, not a duplicate rollback archive.
        # Old operational prose is flagged for owner adaptation, never silently ratified.
        sections = re.split(r"(?m)(?=^## )", index)
        context = "".join(
            section
            for section in sections
            if not section.startswith(("## Phase Table", "## Phase Dependency Graph"))
        )
        (plan / "INDEX.md").write_text(
            "# Proposed plan discovery — REHEARSAL ONLY\n\n"
            "State lives in phases/ and events/; render produces disposable local views. "
            "The preserved context below still needs owner/caller cutover review.\n\n"
            + rewrite_links(context, Path("plan/INDEX.md"), mapping)
        )
        publish(
            root / "log/README.md",
            b"# Activity records\n\nImmutable entries; run multioperator render "
            b"for the local view.\n",
        )
        manifest = {
            "format": FORMAT,
            "adopted": False,
            "source_commit": head,
            "phase_mapping": mapping,
            "original_log_sha256": digest(original_log),
            "original_log_bytes": len(original_log),
            "writer": writer,
            "migration_tool_sha256": digest(Path(__file__).read_bytes()),
            "source_archive_sha256": digest(archive),
            "active_imports": [p for p in rows if rows[p] == "in-progress"],
        }
        publish(root / "collaboration/manifest.json", encode(manifest))
        # Rescan actual post-conversion files, including extensionless executables.
        report = []
        for path in sorted(root.rglob("*")):
            if (
                path.is_file()
                and not path.is_symlink()
                and path.relative_to(root).parts[0] not in {"docs", "log", "reports"}
                and path.suffix in {"", ".py", ".md", ".yaml", ".yml", ".toml", ".json", ".sh"}
            ):
                try:
                    text = path.read_text()
                except UnicodeError:
                    continue
                if any(token in text for token in ("phase-", "LOG.md", "Phase Table", "PHASE_RE")):
                    report.append(str(path.relative_to(root)))
        publish(
            root / "collaboration/adoption-blockers.json",
            encode(
                {
                    "unadapted_callers_and_prose": report,
                    "remaining": [
                        "Owner-approved atomic policy/caller/hook/evidence cutover",
                        "Per-project custody, active checkpoints, ownership/lease mechanism",
                        "Recipient native/acceptance/full-gate qualification",
                    ],
                }
            ),
        )
        ignore = root / ".gitignore"
        with ignore.open("a") as handle:
            handle.write("\n/.collaboration-views/\n")
        retirement = transition.retire(
            root, config.get("retirements", {}), Path(__file__).resolve().parents[2]
        )
        publish(root / "collaboration/retirement.json", encode(retirement))
        publish(
            root / "collaboration/constitution.json",
            encode(
                {
                    "compatibility": compatibility,
                    "runtime_caveats": constitution_caveats(root),
                    "content": retirement["constitution"],
                    "loading_qualified": False,
                }
            ),
        )
        validate(root)
        render(root)
        require(
            (root / ".collaboration-views/LOG.md").read_bytes() == original_log,
            "conversion changed historical log bytes",
        )
        # Publishing a new rehearsal is one directory rename, not an in-place transaction.
        require(not output.exists(), "output appeared during rehearsal")
        root.rename(output)


def event(root: Path, data: dict[str, Any]) -> None:
    phases, prior = records(root)
    fold(phases, [*prior, data])
    verify_acceptance_bytes(root, data)
    publish(safe(root, "plan/events/" + data["id"] + ".json"), encode(data))


def append(root: Path, writer: str, body: bytes, at: str) -> None:
    validate(root)
    terminal_body(body)
    require(bool(writer.strip()) and writer != "unattributed-import", "invalid current log writer")
    instant = datetime.fromisoformat(at.replace("Z", "+00:00"))
    require(instant.tzinfo is not None, "log timestamp needs timezone")
    at = instant.astimezone(UTC).isoformat()
    group = [m for m, _ in logs(root) if m["writer"] == writer]
    require(not group or at >= group[-1]["at"], "writer clock moved backward")
    identifier = uuid.uuid4().hex
    meta = {
        "id": identifier,
        "writer": writer,
        "sequence": len(group) + 1,
        "previous": group[-1]["id"] if group else None,
        "at": at,
        "body_sha256": digest(body),
    }
    publish(safe(root, "log/entries/" + identifier + ".md"), log_record(meta, body))


def add_phase(root: Path, document: Path, writer: str) -> None:
    validate(root)
    phases, prior = records(root)
    metadata, body = frontmatter(document.read_bytes())
    identifier = metadata["id"]
    require(
        identifier not in phases and bool(SLUG.fullmatch(identifier)), "phase id collision/invalid"
    )
    require("owner" not in metadata and "status" not in metadata, "phase duplicates event state")
    genesis = {
        "id": uuid.uuid4().hex,
        "phase": identifier,
        "previous": None,
        "from": None,
        "state": "not-started",
        "owner": None,
        "writer": writer,
        "reason": "New phase; not a claim or acceptance",
    }
    fold({**phases, identifier: metadata}, [*prior, genesis])
    # Both new paths are committed together. An interrupted partial publication
    # remains invalid and visible; no success or automatic cleanup is inferred.
    publish(safe(root, "plan/phases/" + identifier + ".md"), phase_bytes(metadata, body))
    publish(safe(root, "plan/events/" + genesis["id"] + ".json"), encode(genesis))


def order_phase(root: Path, identifier: str, value: str) -> None:
    validate(root)
    phases, events = records(root)
    require(identifier in phases, "phase absent")
    metadata = {**phases[identifier], "order": str(Fraction(value))}
    fold({**phases, identifier: metadata}, events)
    path = safe(root, "plan/phases/" + identifier + ".md")
    _, body = frontmatter(path.read_bytes())
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        handle.write(phase_bytes(metadata, body))
        temporary = Path(handle.name)
    temporary.replace(path)


CLAUDE_AGENTS_MINIMUM = (2, 1, 290)
CLAUDE_AGENTS_RELEASE = "https://github.com/anthropics/claude-code/releases/tag/v2.1.290"


def claude_compatibility() -> dict[str, Any]:
    """The one software gate: current resolved CLI absent, or stable >= verified floor."""
    executable = shutil.which("claude")
    minimum = ".".join(map(str, CLAUDE_AGENTS_MINIMUM))
    if executable is None:
        return {
            "minimum": minimum,
            "installed": None,
            "gate": "not-applicable",
            "probe_scope": "invoking host PATH",
            "instruction_loading": "not-observed",
        }
    completed = subprocess.run(
        [executable, "--version"], capture_output=True, text=True, timeout=10
    )
    require(completed.returncode == 0, "installed Claude version query failed")
    match = re.fullmatch(
        r"(?:Claude Code\s+)?v?(\d+)\.(\d+)\.(\d+)(?:\s+\(Claude Code\))?", completed.stdout.strip()
    )
    require(match is not None, "installed Claude version is unknown/unparseable")
    version = tuple(map(int, match.groups()))
    require(
        version >= CLAUDE_AGENTS_MINIMUM,
        "installed Claude is below the verified AGENTS minimum " + minimum,
    )
    return {
        "minimum": minimum,
        "installed": ".".join(map(str, version)),
        "gate": "passed",
        "probe_scope": "invoking host PATH",
        "instruction_loading": "not-observed",
    }


def constitution_caveats(root: Path) -> list[str]:
    warnings = [
        "Plugin disablement/first-upgrade loading uninspected; version is not loading proof."
    ]
    if any((root / relative).exists() for relative in (".claude/CLAUDE.md", "CLAUDE.local.md")):
        warnings.append("Project-local instruction precedence may shadow AGENTS; files preserved.")
    for ancestor in root.resolve().parents:
        files = [ancestor / "CLAUDE.md", ancestor / "CLAUDE.local.md"]
        if ancestor != Path.home():
            files.append(ancestor / ".claude/CLAUDE.md")
        if any(path.exists() for path in files):
            warnings.append(
                "Ancestor project instructions may shadow AGENTS; no ancestor was modified."
            )
            break
    return warnings


def git_read(root: Path, *arguments: str) -> bytes:
    result = subprocess.run(["git", "-C", str(root), *arguments], capture_output=True, check=False)
    require(result.returncode == 0, "Git read failed: " + result.stderr.decode(errors="replace"))
    return result.stdout


def validate_staged(root: Path) -> dict[str, Any]:
    """Validate immutable indexed records, not a reassuring working-tree substitute."""
    git_read(root, "rev-parse", "--is-inside-work-tree")
    prefixes = (
        "AGENTS.md",
        "CLAUDE.md",
        "plan/phases",
        "plan/events",
        "log/entries",
        "collaboration/manifest.json",
    )
    raw_index = git_read(root, "ls-files", "--stage", "-z", "--", *prefixes)
    indexed = {}
    for row in raw_index.split(b"\0"):
        if not row:
            continue
        fields, path_bytes = row.split(b"\t", 1)
        mode, object_id, stage = fields.decode().split()
        require(stage == "0" and mode in {"100644", "100755"}, "unmerged/symlink record in index")
        indexed[path_bytes.decode()] = git_read(root, "cat-file", "blob", object_id)
    head_query = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--verify", "HEAD"], capture_output=True
    )
    if head_query.returncode:
        require(
            git_read(root, "rev-list", "--all", "--count").strip() == b"0",
            "cannot resolve nonempty HEAD",
        )
        head = None
    else:
        head = head_query.stdout.decode().strip()
    if head:
        previous = git_read(root, "ls-tree", "-rz", "--name-only", head, "--", *prefixes)
        for raw_path in previous.split(b"\0"):
            if not raw_path:
                continue
            relative = raw_path.decode()
            if relative == "CLAUDE.md":
                continue
            require(relative in indexed, "staged record/phase deletion refused")
            if relative != "AGENTS.md" and not relative.startswith("plan/phases/"):
                require(
                    indexed[relative] == git_read(root, "show", head + ":" + relative),
                    "staged immutable record rewrite refused",
                )
    with tempfile.TemporaryDirectory(prefix="multioperator-index-") as temporary:
        staging = Path(temporary)
        for relative, body in indexed.items():
            publish(safe(staging, relative), body)
        for relative in indexed:
            if relative.startswith("plan/events/"):
                record = load(staging / relative)
                if record.get("previous") is not None and record.get("state") == "completed":
                    reference = record["acceptance"]
                    require(
                        not Path(reference["path"]).is_absolute(),
                        "acceptance must be repo-relative",
                    )
                    artifact = safe(root, reference["path"])
                    require(
                        artifact.is_file() and digest(artifact.read_bytes()) == reference["sha256"],
                        "staged acceptance bytes missing/mutated",
                    )
                    destination = safe(staging, reference["path"])
                    if not destination.exists():
                        publish(destination, artifact.read_bytes())
        state = validate(staging)
    require(
        git_read(root, "ls-files", "--stage", "-z", "--", *prefixes) == raw_index,
        "index changed during record validation",
    )
    final_head = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--verify", "HEAD"], capture_output=True
    )
    require(
        (final_head.returncode != 0 and head is None)
        or (final_head.returncode == 0 and final_head.stdout.decode().strip() == head),
        "HEAD changed during record validation",
    )
    return {**state, "staged": True}


def layout(root: Path) -> str:
    require(root.is_dir(), "transfer directory NOT-FOUND")
    marker = safe(root, "collaboration/manifest.json")
    if marker.exists() or marker.is_symlink():
        data = load(marker)
        require(
            data.get("format") == FORMAT and type(data.get("adopted")) is bool,
            "unknown/malformed collaboration declaration",
        )
        require(
            (root / "plan/phases").is_dir() and (root / "log/entries").is_dir(),
            "partial collaboration structure",
        )
        return "declared-adopted" if data["adopted"] else "rehearsal"
    require(
        not (root / "plan/phases").exists() and not (root / "log/entries").exists(),
        "partial collaboration structure has no declaration",
    )
    require(
        (root / "plan/INDEX.md").is_file() and (root / "LOG.md").is_file(),
        "unsupported pre-migration structure",
    )
    return "pre-migration"


def transfer_preflight(donor: Path, recipient: Path, entry: str) -> dict[str, Any]:
    """Read-only route detection. Declared adoption is not verified authority."""
    require(donor.resolve() != recipient.resolve(), "donor and recipient are the same checkout")
    donor_state, recipient_state = layout(donor), layout(recipient)
    require(donor_state == "declared-adopted", "donor has not migrated; rehearsal is not adoption")
    require(
        recipient_state != "rehearsal", "recipient has an unresolved rehearsal/partial transition"
    )
    return {
        "compatibility": claude_compatibility() if recipient_state == "pre-migration" else None,
        "entry": entry,
        "route": "migration-rehearsal" if recipient_state == "pre-migration" else "maintenance",
        "donor_layout": donor_state,
        "recipient_layout": recipient_state,
        "mutation_authorized": False,
        "adoption_verified": False,
        "required_owner_checks": [
            "Actual qualified Starter-first adoption and exact donor candidate",
            "Recipient custody, clean/settled work and terminal phase/review/native boundaries",
            "Approved concrete teach/learn migration plan and recipient-specific recipe/runtime",
            "Phase/budget/evidence continuity; obsolete-tool retirement and full acceptance",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    inventory_parser = commands.add_parser("inventory")
    inventory_parser.add_argument("--root", type=Path, required=True)
    transfer = commands.add_parser("transfer-preflight")
    transfer.add_argument("--donor", type=Path, required=True)
    transfer.add_argument("--recipient", type=Path, required=True)
    transfer.add_argument("--entry", choices=("teach", "learn"), required=True)
    audit_parser = commands.add_parser("audit-retirement")
    audit_parser.add_argument("--root", type=Path, required=True)
    migration = commands.add_parser("rehearse")
    for name in ("source", "output", "mapping"):
        migration.add_argument("--" + name, type=Path, required=True)
    for name in ("validate", "render", "event", "append", "add", "order"):
        command = commands.add_parser(name)
        command.add_argument("--root", type=Path, required=True)
        if name == "validate":
            command.add_argument("--staged", action="store_true")
        if name == "render":
            command.add_argument("--check", action="store_true")
        if name == "event":
            command.add_argument("--file", type=Path, required=True)
        if name == "add":
            command.add_argument("--document", type=Path, required=True)
            command.add_argument("--writer", required=True)
        if name == "order":
            command.add_argument("--phase", required=True)
            command.add_argument("--value", required=True)
        if name == "append":
            command.add_argument("--writer", required=True)
            command.add_argument("--body", type=Path, required=True)
            command.add_argument("--at", default=datetime.now(UTC).isoformat())
    args = parser.parse_args()
    try:
        if args.command == "transfer-preflight":
            print(
                json.dumps(
                    transfer_preflight(args.donor, args.recipient, args.entry), sort_keys=True
                )
            )
        elif args.command == "audit-retirement":
            print(json.dumps(transition.audit(args.root), sort_keys=True))
        elif args.command == "inventory":
            print(json.dumps(transition.inventory(args.root), sort_keys=True))
        elif args.command == "rehearse":
            rehearse(args.source, args.output, args.mapping)
        elif args.command == "validate":
            print(
                json.dumps(
                    validate_staged(args.root) if args.staged else validate(args.root),
                    sort_keys=True,
                )
            )
        elif args.command == "render":
            render(args.root, args.check)
        elif args.command == "event":
            validate(args.root)
            event(args.root, load(args.file))
        elif args.command == "add":
            add_phase(args.root, args.document, args.writer)
        elif args.command == "order":
            order_phase(args.root, args.phase, args.value)
        elif args.command == "append":
            append(args.root, args.writer, args.body.read_bytes(), args.at)
        return 0
    except (
        Refusal,
        OSError,
        ValueError,
        KeyError,
        TypeError,
        yaml.YAMLError,
        tarfile.TarError,
        subprocess.CalledProcessError,
    ) as exc:
        print("MULTIOPERATOR REFUSED: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
