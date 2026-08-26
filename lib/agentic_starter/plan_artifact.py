"""Parse a `phase-planner` artifact and load the tree it describes.

Shared by `bin/check-plan-concreteness` (before review: does the plan cite
only what exists and defer nothing) and `bin/check-plan-delivery` (after
implementation: did the tree receive everything the plan named). One parser,
two questions, so the two checkers cannot disagree about what a plan says.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

FENCE_PATTERN = re.compile(r"^ {0,3}(`{3,}|~{3,})\s*([\w+-]*)")
COMMAND_LANGUAGES = {"", "bash", "sh", "shell", "zsh", "console", "text"}
CODE_SPAN_PATTERN = re.compile(r"(?<!`)`([^`\n]+)`(?!`)")
IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][\w]*(?:\.[A-Za-z_][\w]*)*$")
FLAG_PATTERN = re.compile(r"^--[a-z][\w-]*$")
PATH_SUFFIXES = (
    ".py",
    ".md",
    ".json",
    ".jsonl",
    ".yaml",
    ".yml",
    ".toml",
    ".sh",
    ".zsh",
    ".txt",
    ".js",
    ".ts",
    ".html",
    ".css",
    ".rs",
    ".swift",
    ".sql",
    ".csv",
    ".cfg",
    ".ini",
    ".lock",
    ".patch",
    ".xml",
    ".svg",
)
DEFINITIONS_HEADING = re.compile(r"^#{2,3}\s+Definitions Read\s*$")
FILE_CHANGES_HEADING = re.compile(r"^## File Changes\s*$")
LINE_SUFFIX_PATTERN = re.compile(r":\d+(?:[-–,]\d+)*$")
NODE_ID_PATTERN = re.compile(r"^(?P<path>[^:]+)::(?P<member>[\w.]+)$")
NEW_FILE_PATH_PATTERN = re.compile(r"^\s*-\s*\*\*Path\*\*:\s*`([^`]+)`")
NEW_MARKERS = ("new", "introduced")
MAX_TEXT_FILE_BYTES = 4 * 1024 * 1024


@dataclass
class Plan:
    lines: list[str]
    prose: list[tuple[int, str]] = field(default_factory=list)
    # Nearest `##`/`###` heading above each line, for section-scoped checks.
    section_of: dict[int, str] = field(default_factory=dict)
    commands: list[tuple[int, str]] = field(default_factory=list)
    definitions: list[tuple[int, str, str]] = field(default_factory=list)
    new_paths: set[str] = field(default_factory=set)
    introduced: set[str] = field(default_factory=set)
    has_definitions_table: bool = False


def parse_plan(text: str) -> Plan:
    plan = Plan(lines=text.splitlines())
    in_fence: str | None = None
    fence_language = ""
    in_definitions = False
    in_file_changes = False
    current_section = ""
    for number, line in enumerate(plan.lines, start=1):
        if line.startswith("#") and not line.startswith("####"):
            current_section = line.lstrip("#").strip()
        plan.section_of[number] = current_section
        fence = FENCE_PATTERN.match(line)
        if fence and in_fence is None:
            in_fence = fence.group(1)
            fence_language = fence.group(2).lower()
            continue
        if in_fence is not None:
            if fence and fence.group(1)[0] == in_fence[0] and len(fence.group(1)) >= len(in_fence):
                in_fence = None
                continue
            if fence_language in COMMAND_LANGUAGES:
                plan.commands.append((number, line))
            continue
        if line.startswith("#"):
            in_definitions = bool(DEFINITIONS_HEADING.match(line))
            if in_definitions:
                plan.has_definitions_table = True
            if FILE_CHANGES_HEADING.match(line):
                in_file_changes = True
            elif line.startswith("## "):
                in_file_changes = False
        elif in_file_changes:
            # Names the plan itself defines are listed under File Changes
            # (`Key types / functions / classes / exports`, `Changes`); they
            # are introduced, not cited.
            plan.introduced.update(span.strip() for span in CODE_SPAN_PATTERN.findall(line))
        elif in_definitions and line.lstrip().startswith("|"):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) >= 2 and not set(cells[0]) <= set("-: "):
                identifier = cells[0].strip("`").strip()
                if identifier and identifier.lower() not in {"identifier", "name"}:
                    plan.definitions.append((number, identifier, cells[1]))
        new_file = NEW_FILE_PATH_PATTERN.match(line)
        if new_file:
            plan.new_paths.add(new_file.group(1).strip())
        plan.prose.append((number, line))
    return plan


def git_tree_files(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-co", "--exclude-standard", "-z"],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(f"check-plan-concreteness: not a git tree: {root}")
    return [root / name for name in result.stdout.decode("utf-8", "replace").split("\0") if name]


class Tree:
    """The repository text a plan may cite, loaded once."""

    def __init__(self, root: Path, exclude: Path | None) -> None:
        self.root = root
        self.files: set[str] = set()
        chunks: list[str] = []
        for path in git_tree_files(root):
            relative = path.relative_to(root).as_posix()
            self.files.add(relative)
            if exclude is not None and path.resolve() == exclude:
                continue
            if not path.is_file() or path.stat().st_size > MAX_TEXT_FILE_BYTES:
                continue
            data = path.read_bytes()
            if b"\0" in data[:4096]:
                continue
            chunks.append(data.decode("utf-8", "replace"))
        self.text = "\n".join(chunks)

    def contains(self, needle: str) -> bool:
        return needle in self.text

    def has_path(self, relative: str) -> bool:
        clean = relative.rstrip("/")
        if clean in self.files:
            return True
        if (self.root / clean).exists():
            return True
        return any(name.startswith(clean + "/") for name in self.files)


def looks_like_path(span: str, tree: Tree) -> bool:
    """A repository-relative path, as opposed to a URL path, `$VAR`, or `A/B`."""
    if "://" in span or " " in span or any(c in span for c in '*<>=()"|?^$[]{}'):
        return False
    if span.startswith(("/", "~", ".", "-")) and not span.startswith(("./", "../")):
        return False
    body = LINE_SUFFIX_PATTERN.sub("", span.split("::", 1)[0])
    body = body[2:] if body.startswith("./") else body
    if "/" not in body:
        # A bare filename is an artifact or an output as often as a tree file.
        return False
    first = body.split("/", 1)[0]
    return tree.has_path(first)


def path_of(span: str) -> str:
    body = LINE_SUFFIX_PATTERN.sub("", span.split("::", 1)[0])
    return body[2:] if body.startswith("./") else body


def identifier_shape(span: str) -> bool:
    if FLAG_PATTERN.match(span):
        return True
    if not IDENTIFIER_PATTERN.match(span) or len(span) < 4:
        return False
    return "_" in span or "." in span or sum(1 for c in span if c.isupper()) >= 2
