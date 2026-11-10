"""Committed-source transition and current collaboration-record maintenance.

Records do not allocate leases or authenticate writers. Adoption still requires
receiving ownership, actual adapter qualification and session-loading evidence.
"""

from __future__ import annotations

import argparse
import fcntl
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
    require(
        load(safe(root, "collaboration/manifest.json"))["format"] == FORMAT,
        "wrong format",
    )
    phases = {}
    for path in sorted(safe(root, "plan/phases").glob("*.md")):
        require(not path.is_symlink(), "symlink phase refused")
        meta, _ = frontmatter(path.read_bytes())
        identifier = meta["id"]
        require(bool(SLUG.fullmatch(identifier)), "invalid permanent phase id")
        require(
            path.name == identifier + ".md" and identifier not in phases,
            "duplicate phase id",
        )
        require(
            "status" not in meta and "owner" not in meta,
            "phase metadata duplicates event state",
        )
        try:
            Fraction(meta["order"])
        except (ValueError, TypeError, ZeroDivisionError) as exc:
            raise Refusal("invalid rational order key") from exc
        phases[identifier] = meta
    manifest = load(safe(root, "collaboration/manifest.json"))
    require(
        bool(phases) or (manifest.get("mode") == "retrofit" and manifest.get("adopted") is False),
        "empty phase inventory",
    )
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
        require(
            isinstance(deps, list) and all(d in phases for d in deps),
            "unknown dependency",
        )
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
                bool(event.get("writer")) and bool(event.get("reason")),
                "missing event attribution",
            )
            previous = event["previous"]
            require(
                previous not in seen_previous,
                "competing phase heads; coordinate ownership",
            )
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
                require(
                    event["state"] in allowed[old["state"]],
                    "invalid lifecycle transition",
                )
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
                require(
                    bool(event.get("acceptance")),
                    "completion lacks acceptance reference",
                )
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


def compose_terminal(content: dict[str, Any], at: str) -> bytes:
    """Supply structure, never substantive outcomes or an inferred lessons answer."""
    require(
        set(content) == {"title", "body", "lessons"},
        "terminal content requires title, body and explicit lessons",
    )
    title, meaning, lessons = content["title"], content["body"], content["lessons"]
    require(
        isinstance(title, str) and re.fullmatch(r"(?:END|PARK)(?: [^\r\n]+)?", title),
        "terminal title must be one END or PARK line",
    )
    require(isinstance(meaning, str) and bool(meaning.strip()), "terminal body is required")
    require(
        not any(line.strip().startswith("Lessons:") for line in meaning.splitlines()),
        "supply lessons separately, not a handwritten Lessons heading",
    )
    require(
        isinstance(lessons, list)
        and bool(lessons)
        and all(isinstance(item, str) and bool(item.strip()) for item in lessons),
        "explicit nonempty lessons array is required; none is never inferred",
    )
    instant = datetime.fromisoformat(at.replace("Z", "+00:00"))
    require(instant.tzinfo is not None, "log timestamp needs timezone")
    lesson_lines = ["- " + item.replace("\n", "\n  ") for item in lessons]
    body = (
        f"## {instant.astimezone(UTC):%Y-%m-%d %H:%M} — {title}\n\n"
        + meaning.rstrip("\n")
        + "\n\nLessons:\n"
        + "\n".join(lesson_lines)
        + "\n"
    ).encode()
    require(len(log_blocks.parse(body.decode()).blocks) == 1, "nested log entry in content")
    terminal_body(body)
    return body


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
    return sorted(
        entries,
        key=lambda pair: (pair[0]["at"], pair[0]["writer"], pair[0]["sequence"]),
    )


def not_held(path: Path, relative: str, absent: list[str] | None) -> bool:
    """Ignored runtime evidence does not travel with a clone or to another machine.

    Historical validation reports its absence instead of refusing. A file that is
    present must still match, tracked paths are never excused, and publishing a new
    completion passes no list, so it keeps requiring the bytes.
    """
    if absent is None or not relative.startswith(".kickoff/") or path.exists() or path.is_symlink():
        return False
    absent.append(relative)
    return True


def verify_acceptance_bytes(
    root: Path, event: dict[str, Any], absent: list[str] | None = None
) -> None:
    """Check retention, not semantic phase approval; live adapters still own that."""
    if event["previous"] is None or event["state"] != "completed":
        return
    reference = event["acceptance"]
    require(
        isinstance(reference, dict) and set(reference) == {"path", "sha256"},
        "completion requires retained acceptance bytes",
    )
    require(
        not Path(reference["path"]).is_absolute(),
        "acceptance reference must be repo-relative",
    )
    artifact = safe(root, reference["path"])
    if not_held(artifact, reference["path"], absent):
        return
    require(
        artifact.is_file() and digest(artifact.read_bytes()) == reference["sha256"],
        "acceptance artifact missing or mutated",
    )
    inspect_phase_acceptance(root, event, absent=absent)


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
    absent: list[str] = []
    for event in events:
        verify_acceptance_bytes(root, event, absent)
    entries = logs(root)
    manifest = load(safe(root, "collaboration/manifest.json"))
    if manifest.get("mode") == "retrofit":
        for name, expected in manifest["historical_plans"].items():
            path = safe(root, name)
            require(
                path.is_file() and digest(path.read_bytes()) == expected,
                "retained historical plan missing or mutated",
            )
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
        "evidence_not_held": sorted(set(absent)),
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
    for name, data in [
        ("PLAN.md", table.encode()),
        ("LOG.md", b"".join(b for _, b in bodies)),
    ]:
        path = safe(root, ".collaboration-views/" + name)
        if check:
            require(
                path.is_file() and path.read_bytes() == data,
                "stale generated projection",
            )
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


def source_phase_states(index: str) -> dict[str, str]:
    """Decode only the explicitly committed transition source, never current state."""
    rows = {}
    section = index.split("## Phase Table", 1)
    require(len(section) == 2, "missing phase table")
    for line in section[1].split("\n## ", 1)[0].splitlines():
        match = PHASE_ROW.search(line)
        if match:
            marks = [m for m in STATES if m in line]
            require(len(marks) == 1 and match[1] not in rows, "ambiguous phase status")
            rows[match[1]] = STATES[marks[0]]
    return rows


def rehearse(source: Path, output: Path, mapping_path: Path) -> None:
    source, output = source.resolve(), output.absolute()
    require(not output.exists() and not output.is_symlink(), "output must be absent")
    require(
        not output.resolve().is_relative_to(source) and not source.is_relative_to(output.resolve()),
        "output overlaps source",
    )
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
        require(
            not (root / "collaboration").exists(),
            "source already has collaboration records",
        )
        if config.get("mode") == "retrofit":
            retrofit_records(root, config, head, archive, compatibility)
            require(not output.exists(), "output appeared during rehearsal")
            root.rename(output)
            return
        plan = root / "plan"
        index = (plan / "INDEX.md").read_text()
        rows = source_phase_states(index)
        mapping = config["phases"]
        require(
            set(mapping) == set(rows) and len(set(mapping.values())) == len(mapping),
            "mapping must cover every phase exactly once",
        )
        require(
            all(SLUG.fullmatch(value) for value in mapping.values()),
            "invalid permanent phase id",
        )
        phase_files = sorted(plan.glob("phase-*.md"))
        require({p.stem[6:] for p in phase_files} == set(rows), "phase files/table disagree")
        writer = config["writer"]
        require(
            isinstance(writer, str) and bool(writer.strip()),
            "explicit migration writer required",
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
            root,
            config.get("retirements", {}),
            Path(__file__).resolve().parents[2],
            config.get("tool_replacements", {}),
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


def phase_custody(root: Path, phase: str) -> dict[str, Any]:
    phases, events = records(root)
    require(phase in phases, "phase is absent from the canonical definition inventory")
    head = fold(phases, events)[phase]
    require(
        head["state"] == "in-progress" and bool(head.get("owner")) and bool(head.get("claim")),
        "phase work requires an active owner and recorded claim",
    )
    return head


def phase_heads_digest(root: Path, phases: list[str]) -> str:
    definitions, events = records(root)
    heads = fold(definitions, events)
    require(all(p in heads for p in phases), "transition names absent phase")
    return digest(encode({p: heads[p]["id"] for p in sorted(phases)}))


def completion_plan(
    root: Path, phase: str, proposed: dict[str, Any], parents: list[str] | None = None
) -> dict[str, Any]:
    require(
        isinstance(proposed, dict)
        and set(proposed) == {"schema", "events", "parent_continuation"}
        and proposed["schema"] == "agentic.phase-transition.v1",
        "invalid prospective phase transition",
    )
    definitions, prior = records(root)
    heads = fold(definitions, prior)
    require(phase in definitions, "closing phase is absent")
    items = proposed["events"]
    require(isinstance(items, list) and bool(items), "transition has no proposed events")
    allowed = {phase, *(parents or [])}
    expected_fields = {
        "id",
        "phase",
        "previous",
        "from",
        "state",
        "owner",
        "writer",
        "claim",
        "reason",
    }
    require(
        all(isinstance(e, dict) and set(e) == expected_fields for e in items),
        "prospective events must contain exactly the transition fields, not fabricated acceptance",
    )
    require(
        len({e["phase"] for e in items}) == len(items) and {e["phase"] for e in items} == allowed,
        "transition must complete exactly the accepted phase and authorized ancestors",
    )
    for item in items:
        current = heads[item["phase"]]
        require(
            item["previous"] == current["id"]
            and item["from"] == "in-progress"
            and current["state"] == "in-progress"
            and item["state"] == "completed",
            "transition is stale or does not complete active work",
        )
        require(
            item["owner"] == current["owner"]
            and item["claim"] == current.get("claim")
            and bool(item["writer"])
            and bool(item["reason"]),
            "completion changed owner or claim",
        )
    # This copy is only prospective graph analysis; it is never published as evidence.
    planned = [{**e, "acceptance": {"pending_validation": True}} for e in items]
    after = fold(definitions, [*prior, *planned])
    parent = definitions[phase].get("parent")
    reason = proposed["parent_continuation"]
    require(
        reason is None or (isinstance(reason, str) and bool(reason.strip())),
        "invalid parent continuation",
    )
    if parent and after[parent]["state"] != "completed":
        remaining = [
            p
            for p, meta in definitions.items()
            if meta.get("parent") == parent and after[p]["state"] != "completed"
        ]
        require(
            bool(remaining) or bool(reason),
            "last child requires independent parent completion or truthful remaining-work reason",
        )
    keys = sorted(allowed)
    return {
        "before_sha256": digest(encode({p: heads[p]["id"] for p in keys})),
        "after_sha256": digest(encode({p: after[p]["id"] for p in keys})),
        "completed_phases": keys,
        "proposal": proposed,
    }


def snapshot_acceptance(root: Path, run_dir: Path) -> dict[str, Any]:
    require(
        run_dir.resolve().is_relative_to(root.resolve()),
        "phase qualification must be in durable project storage",
    )
    files = {}
    for path in sorted(run_dir.rglob("*")):
        relative = path.relative_to(run_dir)
        if (
            "__pycache__" in relative.parts
            or path.name in {"closure.json", "closure.lock"}
            or path.name.endswith(".lock")
        ):
            continue
        require(not path.is_symlink(), "qualification snapshots refuse symlinks")
        if path.is_file():
            files[path.relative_to(root).as_posix()] = digest(path.read_bytes())
    require(
        all(
            (run_dir / required).relative_to(root).as_posix() in files
            for required in (
                "run.json",
                "authority.json",
                "tools/manifest.json",
                "gates.jsonl",
                "findings.json",
            )
        ),
        "phase acceptance has incomplete run inputs",
    )
    run = load(run_dir / "run.json")
    from agentic_starter import advisory

    budget = advisory.budget_path(root, run["phase"])
    prefix = None
    if budget.exists():
        data = budget.read_bytes()
        prefix = {
            "path": budget.relative_to(root).as_posix(),
            "bytes": len(data),
            "sha256": digest(data),
        }
    ledger = safe(root, "EXECUTION_LOG.jsonl")
    require(ledger.is_file(), "phase acceptance has no retained execution ledger")
    execution_bytes = ledger.read_bytes()
    execution_prefix = {
        "path": "EXECUTION_LOG.jsonl",
        "bytes": len(execution_bytes),
        "sha256": digest(execution_bytes),
    }
    return {
        "schema": "agentic.phase-qualification.v1",
        "files": files,
        "budget_prefix": prefix,
        "execution_prefix": execution_prefix,
    }


def verify_qualification_snapshot(
    root: Path, value: dict[str, Any], absent: list[str] | None = None
) -> None:
    require(
        isinstance(value, dict)
        and set(value) == {"schema", "files", "budget_prefix", "execution_prefix"}
        and value["schema"] == "agentic.phase-qualification.v1"
        and isinstance(value["files"], dict)
        and bool(value["files"]),
        "invalid phase qualification snapshot",
    )
    for relative, expected in value["files"].items():
        path = safe(root, relative)
        if not_held(path, relative, absent):
            continue
        require(
            path.is_file() and not path.is_symlink() and digest(path.read_bytes()) == expected,
            "accepted phase input is missing or mutated: " + relative,
        )

    for key in ("execution_prefix", "budget_prefix"):
        prefix = value[key]
        if prefix is None:
            require(key == "budget_prefix", "missing retained execution prefix")
            continue
        require(
            isinstance(prefix, dict)
            and set(prefix) == {"path", "bytes", "sha256"}
            and type(prefix["bytes"]) is int
            and prefix["bytes"] >= 0,
            "invalid accepted ledger prefix",
        )
        if key == "execution_prefix":
            require(prefix["path"] == "EXECUTION_LOG.jsonl", "wrong execution ledger prefix")
        path = safe(root, prefix["path"])
        if not_held(path, prefix["path"], absent):
            continue
        require(
            path.is_file()
            and len(path.read_bytes()) >= prefix["bytes"]
            and digest(path.read_bytes()[: prefix["bytes"]]) == prefix["sha256"],
            "accepted " + key + " is missing or changed",
        )


def inspect_phase_acceptance(
    root: Path,
    event: dict[str, Any],
    *,
    fresh: bool = False,
    absent: list[str] | None = None,
) -> None:
    reference = event["acceptance"]
    closure_path = safe(root, reference["path"])
    closure = load(closure_path)
    require(
        closure.get("status") == "complete"
        and closure.get("outcome") == "accepted"
        and closure.get("phase") == event["phase"],
        "artifact is not this phase's accepted close",
    )
    bound = {k: v for k, v in closure.items() if k not in {"closure_id", "status", "completed_at"}}
    require(
        closure.get("closure_id")
        == digest(json.dumps(bound, sort_keys=True, separators=(",", ":")).encode()),
        "accepted closure identity mismatch",
    )
    custody = closure.get("phase_custody", {})
    require(
        custody.get("id") == event["previous"]
        and custody.get("owner") == event["owner"]
        and custody.get("claim") == event.get("claim"),
        "completion does not match accepted phase custody",
    )
    verify_qualification_snapshot(root, closure.get("qualification"), absent)
    log_id = uuid.uuid5(
        uuid.NAMESPACE_URL, "log:" + custody["owner"] + ":" + closure["closure_id"]
    ).hex
    log_path = safe(root, "log/entries/" + log_id + ".md")
    require(log_path.is_file(), "accepted closure log entry is missing")
    log_metadata, log_body = read_log(log_path.read_bytes())
    require(
        log_metadata["writer"] == custody["owner"]
        and digest(log_body) == closure.get("log_sha256"),
        "accepted closure log bytes or writer differ",
    )
    if fresh:
        package = Path(__file__).resolve().parents[2]
        executable = package / "bin/kickoff-evidence"
        if not executable.is_file():
            executable = package / "kickoff-evidence"
        require(executable.is_file(), "trusted phase acceptance validator NOT-FOUND")
        checked = subprocess.run(
            [
                sys.executable,
                str(executable),
                "audit-phase-acceptance",
                "--run-dir",
                str(closure_path.parent),
            ],
            cwd=root,
            capture_output=True,
            text=True,
        )
        require(
            checked.returncode == 0,
            "phase acceptance audit refused: " + (checked.stdout + checked.stderr).strip(),
        )


def apply_completion(
    root: Path,
    transition: dict[str, Any],
    run_dir: Path,
    parent_run: Path | None = None,
) -> None:
    closures = {load(run_dir / "run.json")["phase"]: run_dir / "closure.json"}
    if parent_run:
        parent_closure = load(parent_run / "closure.json")
        closures[parent_closure["phase"]] = parent_run / "closure.json"
        for value in parent_closure.get("ancestor_acceptance", {}).values():
            path = safe(root, value["path"])
            require(
                digest(path.read_bytes()) == value["sha256"],
                "ancestor acceptance changed",
            )
            closures[load(path)["phase"]] = path
    # Children are admitted before parents, retaining the actual independent acceptance per phase.
    definitions, _ = records(root)
    pending = list(transition["proposal"]["events"])
    while pending:
        ready = [
            e
            for e in pending
            if not any(definitions[c["phase"]].get("parent") == e["phase"] for c in pending)
        ]
        require(bool(ready), "completion ancestor cycle")
        for proposal in ready:
            path = safe(root, "plan/events/" + proposal["id"] + ".json")
            acceptance = closures.get(proposal["phase"])
            require(acceptance is not None, "missing independently accepted ancestor")
            reference = {
                "path": acceptance.relative_to(root).as_posix(),
                "sha256": digest(acceptance.read_bytes()),
            }
            item = {**proposal, "acceptance": reference}
            if path.exists():
                require(
                    load(path) == item,
                    "replayed completion differs from accepted event",
                )
            else:
                event(root, item)
            pending.remove(proposal)
    render(root)


def event(root: Path, data: dict[str, Any]) -> None:
    lock = safe(root, ".kickoff/multioperator/phase-writes.lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    with lock.open("a+b") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        phases, prior = records(root)
        fold(phases, [*prior, data])
        verify_acceptance_bytes(root, data)
        if data["state"] == "completed" and data["previous"] is not None:
            inspect_phase_acceptance(root, data, fresh=True)
        publish(safe(root, "plan/events/" + data["id"] + ".json"), encode(data))


def append(
    root: Path, writer: str, body: bytes, at: str, *, idempotency_key: str | None = None
) -> str:
    require(
        bool(writer.strip()) and writer != "unattributed-import",
        "invalid current log writer",
    )
    lock = safe(root, ".kickoff/multioperator/log-" + digest(writer.encode()) + ".lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    with lock.open("a+b") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        validate(root)
        terminal_body(body)
        # A methodology close under any other heading would skip the Lessons contract.
        # New entries only: earlier closes keep the headings they were written with.
        require(
            not any(
                re.search(r"— METHODOLOGY(?! SCOPE\b)", block.header)
                and "— END" not in block.header
                and "— PARK" not in block.header
                for block in log_blocks.parse(body.decode()).blocks
            ),
            "methodology close must be an END or PARK record from append-terminal",
        )
        identifier = (
            uuid.uuid5(uuid.NAMESPACE_URL, "log:" + writer + ":" + idempotency_key).hex
            if idempotency_key
            else uuid.uuid4().hex
        )
        path = safe(root, "log/entries/" + identifier + ".md")
        if path.exists():
            metadata, previous_body = read_log(path.read_bytes())
            require(
                idempotency_key is not None
                and metadata["writer"] == writer
                and previous_body == body,
                "idempotent log request differs from the original",
            )
            return identifier
        instant = datetime.fromisoformat(at.replace("Z", "+00:00"))
        require(instant.tzinfo is not None, "log timestamp needs timezone")
        at = instant.astimezone(UTC).isoformat()
        group = [m for m, _ in logs(root) if m["writer"] == writer]
        require(not group or at >= group[-1]["at"], "writer clock moved backward")
        metadata = {
            "id": identifier,
            "writer": writer,
            "sequence": len(group) + 1,
            "previous": group[-1]["id"] if group else None,
            "at": at,
            "body_sha256": digest(body),
        }
        publish(path, log_record(metadata, body))
        return identifier


def add_phase(root: Path, document: Path, writer: str) -> None:
    validate(root)
    phases, prior = records(root)
    metadata, body = frontmatter(document.read_bytes())
    identifier = metadata["id"]
    require(
        identifier not in phases and bool(SLUG.fullmatch(identifier)),
        "phase id collision/invalid",
    )
    require(
        "owner" not in metadata and "status" not in metadata,
        "phase duplicates event state",
    )
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
        r"(?:Claude Code\s+)?v?(\d+)\.(\d+)\.(\d+)(?:\s+\(Claude Code\))?",
        completed.stdout.strip(),
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
    require(
        result.returncode == 0,
        "Git read failed: " + result.stderr.decode(errors="replace"),
    )
    return result.stdout


def validate_staged(root: Path) -> dict[str, Any]:
    """Validate immutable indexed records, not a reassuring working-tree substitute."""
    git_read(root, "rev-parse", "--is-inside-work-tree")
    prefixes = (
        "AGENTS.md",
        "EXECUTION_LOG.jsonl",
        "CLAUDE.md",
        "plan/phases",
        "plan/events",
        "log/entries",
        "collaboration/manifest.json",
    )
    manifest_bytes = git_read(root, "show", ":collaboration/manifest.json")
    manifest = json.loads(manifest_bytes, object_pairs_hook=unique_pairs)
    if manifest.get("mode") == "retrofit":
        retained = manifest["historical_plans"]
        require(
            isinstance(retained, dict)
            and all(name.startswith("plan/") and ".." not in Path(name).parts for name in retained),
            "invalid retained historical plan paths",
        )
        prefixes += tuple(retained)
    raw_index = git_read(root, "ls-files", "--stage", "-z", "--", *prefixes)
    indexed = {}
    for row in raw_index.split(b"\0"):
        if not row:
            continue
        fields, path_bytes = row.split(b"\t", 1)
        mode, object_id, stage = fields.decode().split()
        require(
            stage == "0" and mode in {"100644", "100755"},
            "unmerged/symlink record in index",
        )
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
    prior_paths: set[str] = set()
    if head:
        previous = git_read(root, "ls-tree", "-rz", "--name-only", head, "--", *prefixes)
        for raw_path in previous.split(b"\0"):
            if not raw_path:
                continue
            relative = raw_path.decode()
            prior_paths.add(relative)
            if relative == "CLAUDE.md":
                continue
            require(relative in indexed, "staged record/phase deletion refused")
            if relative == "EXECUTION_LOG.jsonl":
                require(
                    indexed[relative].startswith(git_read(root, "show", head + ":" + relative)),
                    "staged execution history rewrite refused",
                )
            elif relative != "AGENTS.md" and not relative.startswith("plan/phases/"):
                require(
                    indexed[relative] == git_read(root, "show", head + ":" + relative),
                    "staged immutable record rewrite refused",
                )
    with tempfile.TemporaryDirectory(prefix="multioperator-index-") as temporary:
        staging = Path(temporary)
        for relative, body in indexed.items():
            publish(safe(staging, relative), body)
        for relative in indexed:
            if relative.startswith("plan/events/") and relative.endswith(".json"):
                record = load(staging / relative)
                if (
                    relative not in prior_paths
                    and record.get("previous") is None
                    and record.get("state") == "completed"
                ):
                    manifest = load(staging / "collaboration/manifest.json")
                    source = manifest.get("source_commit", "")
                    old = record.get("source_phase")
                    require(
                        bool(re.fullmatch(r"[0-9a-f]{40}", source))
                        and manifest.get("phase_mapping", {}).get(old) == record["phase"]
                        and record["id"]
                        == uuid.uuid5(uuid.NAMESPACE_URL, source + ":phase:" + str(old)).hex,
                        "new completed genesis lacks verified historical import",
                    )
                    ancestry = subprocess.run(
                        [
                            "git",
                            "-C",
                            str(root),
                            "merge-base",
                            "--is-ancestor",
                            source,
                            "HEAD",
                        ],
                        capture_output=True,
                    )
                    require(
                        ancestry.returncode == 0,
                        "import source is not a retained ancestor",
                    )
                    imported = source_phase_states(
                        git_read(root, "show", source + ":plan/INDEX.md").decode()
                    )
                    require(
                        imported.get(old) == "completed",
                        "completed genesis differs from committed historical state",
                    )
                if record.get("previous") is not None and record.get("state") == "completed":
                    reference = record["acceptance"]
                    require(
                        not Path(reference["path"]).is_absolute(),
                        "acceptance must be repo-relative",
                    )
                    artifact = safe(root, reference["path"])
                    unheld: list[str] | None = [] if relative in prior_paths else None
                    if not_held(artifact, reference["path"], unheld):
                        continue
                    require(
                        artifact.is_file() and digest(artifact.read_bytes()) == reference["sha256"],
                        "staged acceptance bytes missing/mutated",
                    )
                    destination = safe(staging, reference["path"])
                    if not destination.exists():
                        publish(destination, artifact.read_bytes())
                    closure = load(artifact)
                    qualification = closure.get("qualification")
                    verify_qualification_snapshot(root, qualification, unheld)
                    retained = list(qualification["files"])
                    for key in ("execution_prefix", "budget_prefix"):
                        if qualification[key] is not None:
                            retained.append(qualification[key]["path"])
                    for retained_relative in retained:
                        retained_source = safe(root, retained_relative)
                        if not_held(retained_source, retained_relative, unheld):
                            continue
                        if retained_relative in indexed:
                            data = indexed[retained_relative]
                        else:
                            require(
                                retained_relative.startswith(".kickoff/"),
                                "tracked qualification input absent from index: "
                                + retained_relative,
                            )
                            data = retained_source.read_bytes()
                        target = safe(staging, retained_relative)
                        if target.exists():
                            require(
                                target.read_bytes() == data,
                                "staged qualification bytes disagree: " + retained_relative,
                            )
                        else:
                            publish(target, data)
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


def retrofit_records(
    root: Path, recipe: dict[str, Any], head: str, archive: bytes, compatibility: Any
) -> None:
    """Seed prospective records in a committed snapshot; never infer old phase state."""
    require(
        layout(root) == "existing-project",
        "retrofit requires an existing non-methodology project",
    )
    require(
        set(recipe) == {"mode", "source_commit", "writer", "constitution", "historical_plans"}
        and recipe["source_commit"] == head,
        "retrofit recipe must bind the exact committed source",
    )
    require(
        isinstance(recipe["writer"], str) and bool(recipe["writer"].strip()),
        "explicit retrofit writer required",
    )
    plans = {
        p.relative_to(root).as_posix(): digest(p.read_bytes())
        for p in safe(root, "plan").rglob("*")
        if p.is_file() and not p.is_symlink()
    }
    require(
        recipe["historical_plans"] == plans,
        "historical plan inventory/preimage mismatch",
    )
    constitution = recipe["constitution"]
    require(
        isinstance(constitution, str) and bool(constitution.strip()),
        "reviewed constitution required",
    )
    require(
        not any(
            (root / name).exists() or (root / name).is_symlink()
            for name in ("AGENTS.md", "CLAUDE.md")
        ),
        "existing constitution requires owner reconciliation before retrofit",
    )
    publish(root / "AGENTS.md", constitution.encode())
    for name in ("plan/phases", "plan/events", "log/entries"):
        publish(root / name / ".gitkeep", b"")
    publish(
        root / "plan/INDEX.md",
        (
            "# Plan discovery\n\nNew work uses phases/ and events/. "
            "Historical narrative plans remain at their original paths; "
            "they are not imported lifecycle or acceptance records.\n\n"
            + "".join(
                f"- [{name}]({Path(name).relative_to('plan').as_posix()})\n"
                for name in sorted(plans)
            )
        ).encode(),
    )
    publish(
        root / "log/README.md",
        b"# Activity records\n\nProspective immutable entries; "
        b"no historical activity log was supplied.\n",
    )
    publish(
        root / "collaboration/manifest.json",
        encode(
            {
                "format": FORMAT,
                "adopted": False,
                "source_commit": head,
                "source_archive_sha256": digest(archive),
                "writer": recipe["writer"],
                "phase_mapping": {},
                "active_imports": [],
                "original_log_bytes": 0,
                "original_log_sha256": digest(b""),
                "historical_plans": plans,
                "mode": "retrofit",
            }
        ),
    )
    publish(
        root / "collaboration/adoption-blockers.json",
        encode(
            {
                "remaining": [
                    "Approved recipient-local atomic methodology/toolchain/caller/proof bundle",
                    "Owner decisions for prospective phases; no historical acceptance inferred",
                    "Settled work, external custody and terminal native/review boundaries",
                    "Recipient validation, retirement audit, full gate and instruction loading",
                ],
                "compatibility": compatibility,
                "loading_qualified": False,
            }
        ),
    )
    validate(root)
    render(root)


def layout(root: Path, *, capability_source: bool = False) -> str:
    require(root.is_dir(), "transfer directory NOT-FOUND")
    marker = safe(root, "collaboration/manifest.json")
    if marker.exists() or marker.is_symlink():
        data = load(marker)
        require(
            data.get("format") == FORMAT and type(data.get("adopted")) is bool,
            "unknown/malformed collaboration declaration",
        )
        require(
            all(
                safe(root, name).is_dir() for name in ("plan/phases", "plan/events", "log/entries")
            ),
            "partial collaboration structure",
        )
        return "declared-adopted" if data["adopted"] else "rehearsal"
    require(
        not any(
            safe(root, name).exists()
            for name in ("collaboration", "plan/phases", "plan/events", "log/entries")
        ),
        "partial collaboration structure has no declaration",
    )
    index, log = safe(root, "plan/INDEX.md"), safe(root, "LOG.md")
    if index.exists() or log.exists() or list(safe(root, "plan").glob("phase-*.md")):
        require(
            index.is_file() and log.is_file(),
            "partial/unsupported pre-migration structure",
        )
        rows = source_phase_states(index.read_text())
        require(
            bool(rows) and {p.stem[6:] for p in (root / "plan").glob("phase-*.md")} == set(rows),
            "phase files/table disagree",
        )
        return "pre-migration"
    require(
        not safe(root, "kickoff.yaml").exists()
        and not safe(root, ".claude/skills/kickoff").exists(),
        "partial methodology structure requires owner reconciliation",
    )
    for name in ("AGENTS.md", "CLAUDE.md"):
        candidate = safe(root, name)
        require(
            not candidate.exists() or candidate.is_file(),
            "unrecognized constitution structure",
        )
    require(
        not ((root / "AGENTS.md").exists() and (root / "CLAUDE.md").exists()),
        "conflicting constitutions require owner reconciliation",
    )
    if capability_source:
        require(
            any(
                p.is_file() and not p.is_symlink() and p.stat().st_size > 0
                for p in root.iterdir()
                if p.name != ".DS_Store"
            ),
            "empty/unsupported capability source",
        )
        return "capability-source"
    require(
        any(
            safe(root, name).is_file()
            for name in (
                "pyproject.toml",
                "package.json",
                "Cargo.toml",
                "go.mod",
                "Package.swift",
                "CMakeLists.txt",
            )
        )
        or any(
            p.is_file()
            and not p.is_symlink()
            and p.suffix in {".py", ".rs", ".js", ".ts", ".go", ".swift", ".c", ".cpp"}
            for p in root.iterdir()
        ),
        "unsupported existing-project structure; explicit owner assessment required",
    )
    return "existing-project"


PROVENANCE = "collaboration/methodology-provenance.json"
RELEASE = r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"


def methodology_provenance(root: Path) -> dict[str, Any] | None:
    """The recipient-carried record of the methodology release it last adopted.

    Absent means no named baseline is recorded, never that one is current. A malformed
    record refuses: a wrong answer here would hide releases the recipient lacks.
    """
    path = root / PROVENANCE
    if not path.exists() and not path.is_symlink():
        return None
    value = load(safe(root, PROVENANCE))
    require(
        isinstance(value, dict)
        and set(value) == {"schema", "source", "release", "revision", "recorded", "capabilities"}
        and value["schema"] == "agentic.methodology-provenance.v1"
        and isinstance(value["source"], str)
        and bool(value["source"].strip())
        and (value["release"] is None or bool(re.fullmatch(RELEASE, str(value["release"]))))
        and isinstance(value["revision"], str)
        and bool(re.fullmatch(r"[0-9a-f]{40}", value["revision"]))
        and isinstance(value["recorded"], str)
        and bool(re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value["recorded"]))
        and isinstance(value["capabilities"], list)
        and all(isinstance(item, str) and bool(item.strip()) for item in value["capabilities"]),
        "invalid methodology provenance record",
    )
    return value


def declared_releases(root: Path) -> list[str]:
    """Release headings a source declares in RELEASES.md, oldest first; none if it has no file."""
    path = root / "RELEASES.md"
    if not path.is_file():
        return []
    found = re.findall(r"(?m)^## (" + RELEASE.replace("(", "(?:") + r")(?= |$)", path.read_text())
    require(len(found) == len(set(found)), "source declares a release twice")
    return sorted(found, key=lambda name: tuple(map(int, name.split("."))))


def transfer_preflight(
    donor: Path, recipient: Path, entry: str, intent: str = "methodology"
) -> dict[str, Any]:
    """Read-only route detection. Declared adoption is not verified authority."""
    require(
        not donor.resolve().is_relative_to(recipient.resolve())
        and not recipient.resolve().is_relative_to(donor.resolve()),
        "donor and recipient are the same checkout or overlap",
    )
    donor_state = layout(donor, capability_source=intent == "capability")
    recipient_state = layout(recipient)
    require(
        intent == "capability" or donor_state == "declared-adopted",
        "donor has not migrated; rehearsal is not adoption",
    )
    require(
        donor_state != "rehearsal",
        "donor rehearsal is not an operational source",
    )
    require(
        recipient_state != "rehearsal",
        "recipient has an unresolved rehearsal/partial transition",
    )
    route = (
        "capability-learning"
        if intent == "capability"
        else {
            "pre-migration": "migration-rehearsal",
            "existing-project": "retrofit-rehearsal",
            "declared-adopted": "maintenance",
        }[recipient_state]
    )
    if route == "retrofit-rehearsal":
        require(
            not any((recipient / name).exists() for name in ("AGENTS.md", "CLAUDE.md")),
            "existing constitution requires owner reconciliation before retrofit",
        )
    recorded = methodology_provenance(recipient)
    return {
        "compatibility": claude_compatibility()
        if route in {"migration-rehearsal", "retrofit-rehearsal"}
        else None,
        "entry": entry,
        "intent": intent,
        "route": route,
        "donor_layout": donor_state,
        "recipient_layout": recipient_state,
        "recipient_provenance": recorded,
        "releases_not_recorded": [
            name
            for name in declared_releases(donor)
            if recorded is None
            or recorded["release"] is None
            or tuple(map(int, name.split("."))) > tuple(map(int, recorded["release"].split(".")))
        ],
        "mutation_authorized": False,
        "adoption_verified": False,
        "required_owner_checks": [
            "Exact source/capability; qualified donor adoption for whole-methodology transfer",
            "Recipient custody, clean/settled work and terminal phase/review/native boundaries",
            "Approved concrete teach/learn migration plan and recipient-specific recipe/runtime",
            "Phase/budget/evidence continuity; obsolete-tool retirement and full acceptance",
        ],
    }


def select_phase(root: Path, owner: str, phase: str | None = None) -> dict[str, Any]:
    """Select current canonical work without acquiring or pretending to acquire custody."""
    require(bool(owner.strip()), "selection requires a named current operator")
    state = validate(root)
    definitions, _ = records(root)
    heads = state["heads"]
    if phase is None:
        choices = [
            name
            for name, head in heads.items()
            if head["state"] == "next" and head.get("owner") == owner
        ]
        if not choices:
            choices = [
                name
                for name, head in heads.items()
                if head["state"] == "next" and head.get("owner") is None
            ]
        require(
            len(choices) == 1,
            "no unique next selection; name the authorized phase explicitly",
        )
        phase = choices[0]
    require(phase in definitions, "selected phase does not exist")
    head = heads[phase]
    require(head["state"] != "completed", "selected phase is already completed")
    require(head.get("owner") in {None, owner}, "selected phase belongs to another operator")
    require(
        all(heads[d]["state"] == "completed" for d in definitions[phase]["depends_on"]),
        "selected phase has incomplete dependencies",
    )
    return {
        "phase": phase,
        "definition": "plan/phases/" + phase + ".md",
        "head": head,
        "parent": definitions[phase].get("parent"),
        "mutation_authorized": False,
        "required": "Verify external claim/custody before appending an in-progress event",
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
    transfer.add_argument("--intent", choices=("methodology", "capability"), default="methodology")
    selection = commands.add_parser("select")
    selection.add_argument("--root", type=Path, required=True)
    selection.add_argument("--owner", required=True)
    selection.add_argument("--phase")
    status = commands.add_parser("status")
    status.add_argument("--root", type=Path, required=True)
    audit_parser = commands.add_parser("audit-retirement")
    audit_parser.add_argument("--root", type=Path, required=True)
    migration = commands.add_parser("rehearse")
    for name in ("source", "output", "mapping"):
        migration.add_argument("--" + name, type=Path, required=True)
    for name in ("compose-terminal", "append-terminal"):
        command = commands.add_parser(name)
        command.add_argument("--content", type=Path, required=True)
        command.add_argument("--at", default=datetime.now(UTC).isoformat())
        if name == "compose-terminal":
            command.add_argument("--output", type=Path, required=True)
        else:
            command.add_argument("--root", type=Path, required=True)
            command.add_argument("--writer", required=True)
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
        if args.command in {"compose-terminal", "append-terminal"}:
            body = compose_terminal(load(args.content), args.at)
            if args.command == "compose-terminal":
                publish(args.output, body)
            else:
                append(args.root, args.writer, body, args.at)
        elif args.command == "transfer-preflight":
            print(
                json.dumps(
                    transfer_preflight(args.donor, args.recipient, args.entry, args.intent),
                    sort_keys=True,
                )
            )
        elif args.command == "select":
            print(json.dumps(select_phase(args.root, args.owner, args.phase), sort_keys=True))
        elif args.command == "status":
            print(json.dumps(validate(args.root), sort_keys=True))
        elif args.command == "audit-retirement":
            print(json.dumps(transition.audit(args.root), sort_keys=True))
        elif args.command == "inventory":
            print(json.dumps(transition.inventory(args.root), sort_keys=True))
        elif args.command == "rehearse":
            rehearse(args.source, args.output, args.mapping)
        elif args.command == "validate":
            state = validate_staged(args.root) if args.staged else validate(args.root)
            print(json.dumps(state, sort_keys=True))
            if state["evidence_not_held"]:
                print(
                    f"EVIDENCE NOT HELD {len(state['evidence_not_held'])}: retained acceptance "
                    "evidence is absent from this checkout; present evidence was verified",
                    file=sys.stderr,
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
