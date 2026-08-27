"""Behavioral tests for bin/review-verdicts."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HARVESTER = ROOT / "bin" / "review-verdicts"


def finding(identifier: str, evidence: str, state: str = "open") -> dict[str, object]:
    return {
        "id": identifier,
        "severity": "blocking",
        "authority": "plan/phase-1.md",
        "evidence": evidence,
        "affected_paths": ["lib/x.py"],
        "required_outcome": "Fix it",
        "introduced_in": "a" * 64,
        "resolved_in": None,
        "state": state,
        "classification": "initial",
        "disposition": None,
    }


def verdict_text(findings: list[dict[str, object]], verdict: str = "REVISE") -> str:
    return (
        "## Finding Evidence\n```json\n"
        + json.dumps({"findings": findings})
        + f"\n```\n\n## Verdict: {verdict}\n\n### Required Changes\n- Name the seam.\n"
    )


def claude_record(cwd: str, text: str, timestamp: str = "2026-08-20T10:00:00Z") -> str:
    return json.dumps(
        {
            "type": "assistant",
            "cwd": cwd,
            "timestamp": timestamp,
            "message": {"content": [{"type": "text", "text": text}]},
        }
    )


def codex_records(cwd: str, text: str) -> list[str]:
    return [
        json.dumps({"type": "session_meta", "payload": {"cwd": cwd}}),
        json.dumps(
            {
                "timestamp": "2026-08-21T10:00:00Z",
                "type": "response_item",
                "payload": {"content": [{"text": text}]},
            }
        ),
    ]


TEMPLATE_ECHO = (
    "```markdown\n## Verdict: REVISE\n\n### Required Changes\n"
    "- [Specific issue]: [What needs to change and why]\n```\n\n## Rules\n"
)


def corpus(tmp_path: Path) -> tuple[Path, Path]:
    claude_root = tmp_path / "claude" / "projects"
    codex_root = tmp_path / "codex" / "sessions" / "2026" / "08" / "21"
    (claude_root / "-Users-x-proj-a").mkdir(parents=True)
    codex_root.mkdir(parents=True)
    first = verdict_text([finding("PLAN-F001", "The seam is not named")])
    re_aimed = verdict_text(
        [finding("PLAN-F001", "The seam exists but its failure contract is wrong")]
    )
    approved = verdict_text(
        [finding("PLAN-F001", "The seam is named", state="verified")], "APPROVED"
    )
    code = verdict_text([finding("CODE-F001", "Guard runs after the mutation")])
    session = claude_root / "-Users-x-proj-a" / "s1.jsonl"
    session.write_text(
        "\n".join(
            [
                claude_record("/srv/x/proj-a", first),
                claude_record("/srv/x/proj-a", TEMPLATE_ECHO),
                claude_record("/srv/x/proj-a", re_aimed, "2026-08-21T10:00:00Z"),
                claude_record("/srv/x/proj-a", approved, "2026-08-21T11:00:00Z"),
                claude_record("/srv/x/proj-b", code),
                # The same cross-harness review echoed in the dispatching session.
                claude_record("/srv/x/proj-a", "Result:\n" + first),
            ]
        )
        + "\n"
    )
    (codex_root / "rollout.jsonl").write_text(
        "\n".join(codex_records("/srv/x/proj-a", first)) + "\n"
    )
    return claude_root, tmp_path / "codex" / "sessions"


def run(claude_root: Path, codex_root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            str(HARVESTER),
            "--claude-root",
            str(claude_root),
            "--codex-root",
            str(codex_root),
            "--since-days",
            "3650",
            *extra,
        ],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def test_dedupes_across_harnesses_and_drops_template_echoes(tmp_path: Path) -> None:
    claude_root, codex_root = corpus(tmp_path)
    output = tmp_path / "verdicts.json"
    result = run(claude_root, codex_root, "--kind", "all", "--json", str(output))
    assert result.returncode == 0, result.stderr
    payload = json.loads(output.read_text())
    verdicts = payload["verdicts"]
    # first (deduped across the Codex copy and the Claude echo), re-aimed, approved, code.
    assert len(verdicts) == 4, [item["block"][:40] for item in verdicts]
    assert payload["unclassified"] == []
    kinds = sorted((item["project"], item["kind"], item["verdict"]) for item in verdicts)
    assert kinds == [
        ("proj-a", "plan", "APPROVED"),
        ("proj-a", "plan", "REVISE"),
        ("proj-a", "plan", "REVISE"),
        ("proj-b", "code", "REVISE"),
    ]
    assert "REVIEW VERDICTS 4 genuine" in result.stdout


def test_running_session_and_explicit_exclusions_are_skipped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    claude_root, codex_root = corpus(tmp_path)
    own = claude_root / "-Users-x-proj-a" / "11111111-2222-3333-4444-555555555555.jsonl"
    own.write_text(
        claude_record("/srv/x/proj-a", verdict_text([finding("PLAN-F009", "own noise")])) + "\n"
    )
    monkeypatch.delenv("CODEX_SESSION_ID", raising=False)
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "11111111-2222-3333-4444-555555555555")
    result = run(claude_root, codex_root, "--kind", "all", "--exclude-session", "rollout")
    assert result.returncode == 0, result.stderr
    assert "REVIEW VERDICTS 4 genuine" in result.stdout
    assert "Excluded sessions: 11111111-2222-3333-4444-555555555555, rollout" in result.stdout
    assert "PLAN-F009" not in result.stdout
