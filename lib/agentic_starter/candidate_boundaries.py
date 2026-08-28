"""Shared parsing and matching for orchestration bookkeeping boundaries."""

from __future__ import annotations

import fnmatch
import re
from pathlib import Path

PARTITION_BLOCK = re.compile(r"```yaml\s*\n# kickoff-evidence drift partitions\n(.*?)```", re.S)


class BoundaryError(ValueError):
    """The policy-owned candidate boundary is absent or malformed."""


def load_inert_paths(root: Path) -> tuple[str, ...]:
    """Read the one inert-path vocabulary from its governing policy."""
    policy = root / "policies" / "orchestration-evidence.md"
    try:
        text = policy.read_text(encoding="utf-8")
    except OSError as exc:
        raise BoundaryError(f"cannot read candidate-boundary policy: {exc}") from exc
    matches = list(PARTITION_BLOCK.finditer(text))
    if len(matches) != 1:
        raise BoundaryError("candidate-boundary policy must contain one drift partition block")
    entries: list[str] = []
    in_inert = False
    for raw in matches[0].group(1).splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line == "inert:":
            in_inert = True
            continue
        if not in_inert or not line.startswith("- "):
            raise BoundaryError(f"invalid drift partition line: {raw}")
        entry = line[2:].strip()
        path = Path(entry.rstrip("/"))
        if not entry or path.is_absolute() or ".." in path.parts:
            raise BoundaryError(f"invalid inert path: {entry!r}")
        entries.append(entry)
    if not entries or len(entries) != len(set(entries)):
        raise BoundaryError("inert paths must be nonempty and unique")
    return tuple(entries)


def path_is_inert(path: str, entries: tuple[str, ...]) -> bool:
    """Match a repo-relative path; wildcards never cross path separators."""
    relative = Path(path)
    if relative.is_absolute() or ".." in relative.parts:
        return False
    parts = relative.parts
    for entry in entries:
        if entry.endswith("/"):
            prefix = Path(entry.rstrip("/")).parts
            if parts[: len(prefix)] == prefix:
                return True
            continue
        pattern = Path(entry).parts
        if len(pattern) == len(parts) and all(
            fnmatch.fnmatchcase(component, expected) for component, expected in zip(parts, pattern)
        ):
            return True
    return False
