"""Parse the product boundary without third-party dependencies.

The YAML subset accepts a plain schema identifier and block lists of
JSON-quoted strings, blank lines, and full-line comments. Patterns must be
root-anchored; *, ? and whole-segment ** are supported. Bookkeeping wins.
"""

from __future__ import annotations

import fnmatch
import hashlib
import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path

FILENAME = "candidate-partition.yaml"
SCHEMA = "agentic.candidate-partition.v1"


class BoundaryError(ValueError):
    """Missing, malformed, or incomplete candidate declaration."""


def matches(path: str, pattern: str) -> bool:
    """Match a validated anchored pattern without crossing path separators."""
    parts = tuple(path.split("/"))
    if path.startswith("/") or any(p in {"", ".", ".."} for p in parts):
        return False
    segments = tuple(pattern[1:].split("/"))

    @cache
    def visit(i: int, j: int) -> bool:
        if i == len(segments):
            return j == len(parts)
        if segments[i] == "**":
            return visit(i + 1, j) or (j < len(parts) and visit(i, j + 1))
        return j < len(parts) and fnmatch.fnmatchcase(parts[j], segments[i]) and visit(i + 1, j + 1)

    return visit(0, 0)


@dataclass(frozen=True)
class Partition:
    active: tuple[str, ...]
    bookkeeping: tuple[str, ...]
    sha256: str

    def classify(self, path: str) -> str | None:
        """Bookkeeping carves out of active regardless of declaration order."""
        if any(matches(path, p) for p in self.bookkeeping):
            return "bookkeeping"
        if any(matches(path, p) for p in self.active):
            return "active"
        return None

    def require_tracked(self, paths: list[str]) -> None:
        unknown = sorted(path for path in paths if self.classify(path) is None)
        if unknown:
            raise BoundaryError("unclassified tracked paths: " + ", ".join(unknown))


def parse_partition(content: bytes) -> Partition:
    """Parse exact bytes, refusing unsupported syntax and self-exclusion."""
    try:
        text = content.decode("utf-8")
    except UnicodeError as exc:
        raise BoundaryError("partition must be UTF-8") from exc
    seen: set[str] = set()
    patterns: set[str] = set()
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for number, raw in enumerate(text.splitlines(), 1):
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        if "\t" in raw:
            raise BoundaryError(f"partition line {number}: tabs are unsupported")
        if raw == f"schema: {SCHEMA}":
            key = "schema"
            current = None
        elif raw in {"active:", "bookkeeping:"}:
            key = raw[:-1]
            current = key
            sections[key] = []
        elif raw.startswith("  - ") and current is not None:
            try:
                pattern = json.loads(raw[4:])
            except ValueError as exc:
                raise BoundaryError(f"partition line {number}: use JSON-quoted patterns") from exc
            if (
                not isinstance(pattern, str)
                or not pattern.startswith("/")
                or pattern in {"/*", "/**"}
                or any(marker in pattern for marker in "!\\[]")
                or any(p in {"", ".", ".."} for p in pattern[1:].split("/"))
                or any("**" in p and p != "**" for p in pattern[1:].split("/"))
            ):
                raise BoundaryError(f"partition line {number}: unsupported anchored pattern")
            if pattern in patterns:
                raise BoundaryError(f"partition line {number}: duplicate pattern {pattern!r}")
            patterns.add(pattern)
            sections[current].append(pattern)
            continue
        else:
            raise BoundaryError(f"partition line {number}: unsupported declaration syntax")
        if key in seen:
            raise BoundaryError(f"partition line {number}: duplicate field {key}")
        seen.add(key)
    if seen != {"schema", "active", "bookkeeping"} or not sections.get("active"):
        raise BoundaryError("partition requires schema, nonempty active, and bookkeeping lists")
    result = Partition(
        tuple(sections["active"]),
        tuple(sections["bookkeeping"]),
        hashlib.sha256(content).hexdigest(),
    )
    if result.classify(FILENAME) != "active":
        raise BoundaryError("candidate-partition.yaml must classify as active")
    return result


def load_partition(root: Path) -> Partition:
    """Absence never supplies a default boundary."""
    try:
        path = root / FILENAME
        if path.is_symlink() or not path.is_file():
            raise BoundaryError(f"cannot read {FILENAME}: declaration must be a regular file")
        return parse_partition(path.read_bytes())
    except OSError as exc:
        raise BoundaryError(f"cannot read {FILENAME}: {exc}") from exc
