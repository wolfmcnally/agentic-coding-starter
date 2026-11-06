"""Small checked-file publication primitive for existing record authoring tools."""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any


def read_object(path: Path) -> dict[str, Any]:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        value = dict(items)
        if len(value) != len(items):
            raise ValueError("duplicate JSON input key")
        return value

    if path.is_symlink():
        raise ValueError("symlink input refused")
    value = json.loads(path.read_bytes(), object_pairs_hook=pairs)
    if not isinstance(value, dict):
        raise ValueError("input must be a JSON object")
    return value


def destination(root: Path, relative: str) -> Path:
    root = root.resolve()
    if not relative or any(part in {"", ".", "..", ".git"} for part in relative.split("/")):
        raise ValueError("destination requires canonical repository-relative path segments")
    path = root / relative
    if (
        Path(relative).is_absolute()
        or not path.resolve().is_relative_to(root)
        or ".git" in Path(relative).parts
    ):
        raise ValueError("input destination escapes repository")
    if any(p.is_symlink() for p in (path, *path.parents) if p != root):
        raise ValueError("symlink destination refused")
    return path


def checked_write(
    root: Path,
    relative: str,
    data: bytes,
    check: Callable[[Path], object],
    expected: str | None = None,
) -> None:
    """Validate proposed bytes before create or digest-bound replacement; never force."""
    path = destination(root, relative)
    lock = destination(
        root, ".kickoff/input-writes/" + hashlib.sha256(relative.encode()).hexdigest()
    )
    lock.parent.mkdir(parents=True, exist_ok=True)
    with lock.open("a+b") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)

        def preimage() -> None:
            destination(root, relative)
            if expected is None:
                if path.exists():
                    raise ValueError("destination exists; supply its exact --expect-sha256 to edit")
            elif not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                raise ValueError("destination preimage mismatch")

        preimage()
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".input-", dir=path.parent) as temporary:
            staged = Path(temporary) / path.name
            with staged.open("xb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            check(staged)
            preimage()
            if expected is None:
                os.link(staged, path)
            else:
                staged.chmod(path.stat().st_mode & 0o777)
                os.replace(staged, path)
            descriptor = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
