"""The closed vocabularies of a review finding, and the schema derived from them.

These sets are the validator's. They live here rather than inside
`bin/kickoff-evidence` so that the tool which *checks* a finding and the tool
which *constrains its generation* read the same definition — a second copy is
the defect this module exists to remove.

**Why constrain at generation.** Validation used to run only after the
reviewing agent had exited, so the cheapest possible repair — one more turn
saying "invalid severity, re-emit" — was unavailable, and a single invented
token cost a whole review. It happened three times in one phase: a blank line
after a heading discarded seven plan findings; an `open → verified` transition
discarded nine; the severity token `major` discarded five blocking findings
after a 73-turn, ~13-minute, $8.67 critique. In every case the reviewer did
substantively correct work and the evidence layer threw it away on a format
technicality. An enum-constrained field cannot emit `major`, and a JSON payload
has no markdown envelope to get wrong, so both failure modes stop being
categories rather than being caught later.

**What the schema deliberately does not carry.** The emitted document stays
inside the strict structured-output subset both vendors accept: object types,
closed `enum`s, `items`, an exhaustive `required` list, and
`additionalProperties: false`. It carries no `pattern`, no `minLength`, and no
bare optional properties — an optional field is typed `["string", "null"]` and
still listed as required, which is how strict mode expresses optionality.

That subset cannot express finding-id shape, candidate-hash shape, non-empty
text, or transition legality. Those remain with `kickoff-evidence`'s validator,
which stays in the dispatch path as defense in depth. The division is the point:
the schema owns what a vocabulary can state, the validator owns what only a
run's own history can decide.

**Why there is no `$schema` key.** The two venues disagree about it. Codex's
`--output-schema` accepts the document either way; Claude's `--json-schema`
treats the value as a meta-schema reference it must already hold and rejects
the document outright when it cannot resolve it. Emitting the draft 2020-12
URI therefore made every Claude-venue review die in under a second, before the
model ran — and under a Codex-orchestrated kickoff the shipped routing sends
both review roles there. The key constrains nothing the vendors read, so the
schema simply does not carry it.
"""

from __future__ import annotations

import json
from typing import Any

__all__ = [
    "CLASSIFICATIONS",
    "FINDING_ALIASES",
    "OPTIONAL_FINDING_FIELDS",
    "REQUIRED_FINDING_FIELDS",
    "REVIEW_KINDS",
    "SEVERITIES",
    "STATES",
    "VERDICTS",
    "finding_schema",
    "review_artifact_schema",
    "schema_json",
]

SEVERITIES = {"blocking", "high", "medium", "low", "nit"}
STATES = {
    "open",
    "addressed",
    "verified",
    "closed",
    "rejected-with-evidence",
    "blocked-owner",
    "superseded",
}
CLASSIFICATIONS = {
    "initial",
    "introduced-by-revision",
    "newly-exposed-by-resolution",
    "missed-in-full-pass",
}
VERDICTS = ("APPROVED", "REVISE")
REVIEW_KINDS = {"plan": "PLAN", "code": "CODE"}

# Tokens a reviewer plausibly reaches for that the closed sets do not contain.
# Retained under schema-constrained generation: a native subagent runs without a
# schema, and an alias degrades a slip to a printed normalization rather than a
# discarded batch.
FINDING_ALIASES = {
    "severity": {
        "major": "high",
        "critical": "blocking",
        "minor": "low",
        "info": "nit",
    },
    "state": {
        "resolved": "verified",
        "fixed": "verified",
    },
}

REQUIRED_FINDING_FIELDS = (
    "id",
    "severity",
    "authority",
    "evidence",
    "affected_paths",
    "required_outcome",
    "introduced_in",
    "state",
    "classification",
)
OPTIONAL_FINDING_FIELDS = ("resolved_in", "disposition")


def _enum(values: set[str]) -> list[str]:
    """Sorted so the emitted schema is byte-stable across runs."""
    return sorted(values)


def finding_schema(kind: str) -> dict[str, Any]:
    """The object schema for one finding of a plan or code review."""
    if kind not in REVIEW_KINDS:
        raise ValueError(f"unknown review kind: {kind}")
    prefix = REVIEW_KINDS[kind]
    properties: dict[str, Any] = {
        "id": {
            "type": "string",
            "description": f"{prefix}-Fnnn, unique and stable across revision rounds",
        },
        "severity": {"type": "string", "enum": _enum(SEVERITIES)},
        "authority": {
            "type": "string",
            "description": "the governing file or rule the finding is grounded in",
        },
        "evidence": {
            "type": "string",
            "description": "what was observed, specific enough to re-check",
        },
        "affected_paths": {
            "type": "array",
            "items": {"type": "string"},
            "description": "repo-relative paths",
        },
        "required_outcome": {
            "type": "string",
            "description": "what must be true for this finding to be resolved",
        },
        "introduced_in": {
            "type": "string",
            "description": "candidate id this finding was observed against",
        },
        "state": {"type": "string", "enum": _enum(STATES)},
        "classification": {"type": "string", "enum": _enum(CLASSIFICATIONS)},
        "resolved_in": {
            "type": ["string", "null"],
            "description": "candidate id that resolved it; null while unresolved",
        },
        "disposition": {
            "type": ["string", "null"],
            "description": "optional note; null when absent",
        },
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
        # Strict mode requires every property to be listed; optionality is
        # expressed by the nullable type above, not by omission from this list.
        "required": list(REQUIRED_FINDING_FIELDS) + list(OPTIONAL_FINDING_FIELDS),
    }


def review_artifact_schema(kind: str) -> dict[str, Any]:
    """The whole final message a delegated review role emits.

    The verdict travels inside the document. Under structured output there is no
    markdown left to carry a `## Verdict:` header, so a schema that constrained
    only the findings array would silently drop the orchestration contract that
    header exists to satisfy.
    """
    return {
        # No `$schema` declaration. Claude's `--json-schema` resolves the value
        # as a meta-schema it must already hold, and rejects the whole document
        # with `no schema with key or ref "…"` — in 0.6 s, before the model
        # runs, so a phase's entire code review is lost to a key that adds
        # nothing. Codex's `--output-schema` accepts the document with or
        # without it. Measured under a Codex-orchestrated kickoff the default
        # routing sends *both* review roles to the Claude CLI, so carrying this
        # key meant that harness could not run a review at all.
        "title": f"agentic-starter-{kind}-review",
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "verdict": {"type": "string", "enum": list(VERDICTS)},
            "summary": {
                "type": "string",
                "description": "the critique in prose; the reasoning behind the verdict",
            },
            "findings": {"type": "array", "items": finding_schema(kind)},
        },
        "required": ["verdict", "summary", "findings"],
    }


def schema_json(kind: str) -> str:
    """The schema as compact, byte-stable JSON, for a CLI flag or a file."""
    return json.dumps(review_artifact_schema(kind), separators=(",", ":"))
