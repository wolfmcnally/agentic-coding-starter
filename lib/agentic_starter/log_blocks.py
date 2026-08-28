"""Parse, identify, and chronology-check Starter's append-only activity log."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime

HEADER_RE = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})(?:[ T](\d{2}:\d{2}))?\b(.*)$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
CORRECTION_TITLE = "LOG CHRONOLOGY CORRECTION"
CORRECTION_MARKER = "Log chronology correction:"


@dataclass(frozen=True)
class Block:
    header: str
    body: tuple[str, ...]
    anchor: datetime

    def render(self) -> str:
        return "\n".join((self.header, *self.body)).rstrip() + "\n"

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.render().encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ParsedLog:
    preamble: str
    blocks: tuple[Block, ...]

    def render(self) -> str:
        prefix = self.preamble.rstrip("\n")
        rendered = [block.render().rstrip("\n") for block in self.blocks]
        return prefix + ("\n\n" if prefix and rendered else "") + "\n\n".join(rendered) + "\n"


def parse(text: str) -> ParsedLog:
    lines = text.splitlines()
    starts: list[tuple[int, datetime]] = []
    for index, line in enumerate(lines):
        match = HEADER_RE.match(line)
        if match is None:
            continue
        date, clock, _ = match.groups()
        try:
            anchor = datetime.strptime(f"{date} {clock or '00:00'}", "%Y-%m-%d %H:%M")
        except ValueError:
            continue
        starts.append((index, anchor))
    if not starts:
        return ParsedLog(text, ())
    preamble = "\n".join(lines[: starts[0][0]])
    blocks: list[Block] = []
    for position, (start, anchor) in enumerate(starts):
        end = starts[position + 1][0] if position + 1 < len(starts) else len(lines)
        body = list(lines[start + 1 : end])
        while body and not body[-1].strip():
            body.pop()
        blocks.append(Block(lines[start], tuple(body), anchor))
    return ParsedLog(preamble, tuple(blocks))


def effective_anchors(parsed: ParsedLog) -> tuple[list[datetime], list[str]]:
    anchors = [block.anchor for block in parsed.blocks]
    errors: list[str] = []
    identities: dict[str, list[int]] = {}
    for index, block in enumerate(parsed.blocks):
        identities.setdefault(block.sha256, []).append(index)
    corrected: set[str] = set()
    for index, block in enumerate(parsed.blocks):
        if not block.header.endswith(f"— {CORRECTION_TITLE}"):
            continue
        lines = [line.strip() for line in block.body if line.strip()]
        fields: dict[str, str] = {}
        if not lines or lines[0] != CORRECTION_MARKER:
            errors.append(f"block {index + 1}: malformed chronology correction")
            continue
        for line in lines[1:]:
            key, separator, value = line.removeprefix("- ").partition(": ")
            if not separator or key in fields:
                errors.append(f"block {index + 1}: malformed correction field")
                fields = {}
                break
            fields[key] = value
        if set(fields) != {"target-block-sha256", "recorded-anchor", "effective-anchor"}:
            errors.append(f"block {index + 1}: correction fields are incomplete")
            continue
        target = fields["target-block-sha256"]
        matches = [candidate for candidate in identities.get(target, []) if candidate < index]
        if SHA256_RE.fullmatch(target) is None or len(matches) != 1 or target in corrected:
            errors.append(f"block {index + 1}: correction target is absent, ambiguous, or repeated")
            continue
        try:
            recorded = datetime.strptime(fields["recorded-anchor"], "%Y-%m-%d %H:%M")
            effective = datetime.strptime(fields["effective-anchor"], "%Y-%m-%d %H:%M")
        except ValueError:
            errors.append(f"block {index + 1}: correction anchor is invalid")
            continue
        target_index = matches[0]
        if anchors[target_index] != recorded or not recorded < effective <= block.anchor:
            errors.append(f"block {index + 1}: correction does not move its exact target forward")
            continue
        anchors[target_index] = effective
        corrected.add(target)
    return anchors, errors


def chronology_errors(parsed: ParsedLog) -> list[str]:
    anchors, errors = effective_anchors(parsed)
    for index in range(1, len(anchors)):
        if anchors[index] < anchors[index - 1]:
            errors.append(
                f"block {index + 1} regresses {anchors[index]:%Y-%m-%d %H:%M} "
                f"behind {anchors[index - 1]:%Y-%m-%d %H:%M}"
            )
    return errors
