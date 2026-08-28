"""Validated immutable executable command manifests for kickoff runs."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
OPERATION_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


class RunbookError(ValueError):
    """A command manifest is malformed, ambiguous, or does not admit a row."""


def _argv(value: Any, label: str) -> list[str]:
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(item, str) and item and "\x00" not in item for item in value)
    ):
        raise RunbookError(f"{label} must be a nonempty NUL-free string array")
    return value


def validate(document: Any) -> dict[str, Any]:
    if not isinstance(document, dict) or set(document) != {
        "schema_version",
        "commands",
        "preflight_commands",
    }:
        raise RunbookError("command manifest has unknown or missing fields")
    if document.get("schema_version") != SCHEMA_VERSION:
        raise RunbookError("unsupported command manifest schema")
    commands = document.get("commands")
    preflights = document.get("preflight_commands")
    if not isinstance(commands, list) or not commands:
        raise RunbookError("command manifest must declare at least one gate command")
    if not isinstance(preflights, list):
        raise RunbookError("preflight_commands must be an array")
    seen: set[tuple[str, int, bool, tuple[str, ...]]] = set()
    for index, row in enumerate(commands, 1):
        if not isinstance(row, dict) or set(row) != {
            "operation",
            "attempt",
            "final",
            "argv",
        }:
            raise RunbookError(f"command row {index} has unknown or missing fields")
        operation = row.get("operation")
        attempt = row.get("attempt")
        final = row.get("final")
        if not isinstance(operation, str) or OPERATION_RE.fullmatch(operation) is None:
            raise RunbookError(f"command row {index} has invalid operation")
        if not isinstance(attempt, int) or isinstance(attempt, bool) or attempt < 1:
            raise RunbookError(f"command row {index} has invalid attempt")
        if not isinstance(final, bool):
            raise RunbookError(f"command row {index} final must be boolean")
        identity = (
            operation,
            attempt,
            final,
            tuple(_argv(row.get("argv"), f"command row {index} argv")),
        )
        if identity in seen:
            raise RunbookError(f"command row {index} duplicates an earlier row")
        seen.add(identity)
    if not any(identity[2] for identity in seen):
        raise RunbookError("command manifest must declare at least one final gate")
    for index, row in enumerate(preflights, 1):
        if not isinstance(row, dict) or set(row) != {"argv", "reason"}:
            raise RunbookError(f"preflight row {index} must contain exactly argv and reason")
        _argv(row.get("argv"), f"preflight row {index} argv")
        if not isinstance(row.get("reason"), str) or not row["reason"].strip():
            raise RunbookError(f"preflight row {index} reason must be nonempty")
    return document


def load(path: Path) -> tuple[dict[str, Any], bytes, str]:
    raw = path.read_bytes()
    try:
        document = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RunbookError(f"command manifest is not valid UTF-8 JSON: {exc}") from exc
    validate(document)
    return document, raw, hashlib.sha256(raw).hexdigest()


def admitted(
    document: dict[str, Any],
    *,
    operation: str,
    attempt: int,
    final: bool,
    argv: list[str],
) -> bool:
    wanted = (operation, attempt, final, tuple(argv))
    return any(
        (row["operation"], row["attempt"], row["final"], tuple(row["argv"])) == wanted
        for row in document["commands"]
    )


def validate_digest(value: Any, label: str = "manifest digest") -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise RunbookError(f"{label} must be lowercase SHA-256")
    return value
