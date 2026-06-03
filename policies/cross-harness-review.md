# Policy: Cross-Harness Review

When enabled, `/kickoff` delegates its two **review** stages — plan review (Step 4) and code critique (Step 6) — to the *other* harness's CLI: `codex` when `/kickoff` runs in Claude Code, `claude` when it runs in Codex. Orchestration, planning, and coding always stay in the invoking harness. A model reviewing another vendor's model catches failure classes same-model review misses; the research and flag-level rationale live in [`briefs/cross-agent-invocation.md`](../briefs/cross-agent-invocation.md).

## Activation contract

The switch is a single token in `CLAUDE.md`'s **Project Context** zone, in the `## Cross-harness review` subsection:

- `cross-harness-review: enabled`
- `cross-harness-review: disabled`

The orchestrator reads the token by string match. Precedence:

| Token | Other CLI on PATH | Review venue |
|---|---|---|
| `disabled` or absent | (any) | Native subagents. |
| `enabled` | yes | The other harness's CLI. |
| `enabled` | no | Native subagents — **silently**. Not an error, not a fallback; just the venue report `native (<cli> not on PATH)`. |

Default for this template and for projects stamped by `/starter`: **enabled**. The token is per-project: it lives in Project Context, which `/starter` rewrites per project and `/teach` never touches.

## What is delegated — and what is not

- **Delegated when active:** the `plan-reviewer` role (kickoff Step 4) and the `code-critic` role (kickoff Step 6). Both are read-only roles.
- **Never delegated:** orchestration (`/kickoff` itself), planning (`phase-planner`), implementation (`phase-coder`), build gates, status-marker transitions, `LOG.md` writes.

The four canonical roles are unchanged — names, procedures, tool stances, verdict headers all stay as [`four-canonical-agents.md`](four-canonical-agents.md) prescribes. Only the **execution venue** of the two reviewer roles becomes configurable.

## Venue resolution (kickoff Step 0a)

Resolved **once per session**, before phase work begins:

1. If the env var `KICKOFF_REVIEW_DEPTH` is set, the venue is `native` regardless of config — this session *is* a delegated reviewer; it must not delegate further (recursion guard).
2. Read the `cross-harness-review:` token from `CLAUDE.md` Project Context. `disabled` or absent → `native`.
3. Detect the invoking harness: `CLAUDECODE=1` in the environment means Claude Code (alternative CLI: `codex`); otherwise Codex (alternative CLI: `claude`).
4. `command -v <alternative-cli>` — absent → `native` (silent). Present → the alternative CLI is the review venue.

Both review stages use the same resolved venue; the orchestrator does not re-resolve between Step 4 and Step 6 (but a mid-stage failure can demote a single stage — see the fallback state machine).

## Role sourcing

The external CLI is instructed to **read the same canonical role file** the native subagent uses — `.claude/agents/plan-reviewer.md` for Step 4, `.claude/agents/code-critic.md` for Step 6 — and adopt it for the duration of the call. One role definition, two execution venues. Because Codex auto-ingests `AGENTS.md` (→ `CLAUDE.md`) and `claude` auto-loads `CLAUDE.md`, the external reviewer is bound by the same policies, invariants, and verdict contract with no extra plumbing.

The orchestrator passes the **phase-specific inputs** the role file declares (phase reference and heading; full phase text; the plan text for Step 4; the plan, file list, and diff for Step 6) by writing the large pieces to temp files (e.g., under `/tmp`) and referencing their paths in the prompt — never inline.

## The two invocation recipes

Claude Code → codex:

```
codex exec -s read-only -c 'approval_policy="never"' -C "$(pwd)" --output-last-message "$MSGFILE" "$(cat "$PROMPTFILE")" 2>/dev/null
```

Non-negotiable: approvals pinned off via the `-c 'approval_policy="never"'` config override (an approval prompt with no TTY can hang the call and has held git index locks; the override is used because `codex exec` flag surfaces churn — e.g., codex-cli 0.136.0 rejects the older `-a/--ask-for-approval` flag on `exec` — while `-c` overrides parse across versions); `-s read-only` (reviewer tool stance; no tree contention); capture from the `--output-last-message` artifact, not stdout (stderr is progress noise); no hardcoded `-m` model (names churn); run with `KICKOFF_REVIEW_DEPTH=1` in the child environment. If the invocation fails with a flag-parse error, consult `codex exec --help` and adapt — or treat it as a fallback trigger like any other. Revision rounds prefer `codex exec resume <session-id>`.

Codex → claude:

```
env -u CLAUDECODE -u CLAUDE_CODE_ENTRYPOINT KICKOFF_REVIEW_DEPTH=1 claude -p "$(cat "$PROMPTFILE")" --permission-mode dontAsk --allowedTools "Read,Grep,Glob" --output-format json --max-turns 12
```

Non-negotiable: `--permission-mode dontAsk`, never `--dangerously-skip-permissions` (its one-time interactive consent dialog hangs without a TTY); `--allowedTools` mirrors the reviewer tool stance (`AskUserQuestion` omitted — a nested CLI cannot reach the human; an unresolved product question becomes a `REVISE` verdict stating the question); scrub `CLAUDECODE` / `CLAUDE_CODE_ENTRYPOINT` from the child environment (an inherited `CLAUDECODE=1` makes the inner `claude` refuse to launch); parse `.result` and `.session_id` from the JSON envelope, and treat an envelope with `is_error: true` as a failed call regardless of content. Revision rounds prefer `claude --resume <session-id> -p`.

When the chain *began* in a Claude Code session (testing this recipe from inside Claude Code, or any claude → codex → claude chain), also scrub `ANTHROPIC_API_KEY`: Claude Code injects a session-scoped key into child processes that silently outranks subscription auth in the inner `claude` and fails with `api_error_status: 401` ("Invalid API key") — verified empirically. In a genuine Codex parent, leave a deliberately-set `ANTHROPIC_API_KEY` alone; it is the intended auth.

Full flag-by-flag rationale, auth notes, and the macOS sandbox-network caveat: [`briefs/cross-agent-invocation.md`](../briefs/cross-agent-invocation.md) §§2–3.

## Fallback state machine

Success of an external review call is gated on **three signals together**:

1. The output artifact (codex `--output-last-message` file / claude JSON `.result`) exists and is non-empty.
2. It contains exactly one `## Verdict: APPROVED` or `## Verdict: REVISE` header.
3. The call returned within a wall-clock timeout — 300 s for plan review, 420 s for code critique.

Any signal failing means the call failed. Triggers and handling:

| Trigger | Detected | Action |
|---|---|---|
| Alternative CLI not on PATH | Step 0a | Venue is `native` for the whole session. Silent; venue report reads `native (<cli> not on PATH)`. |
| Recursion guard (`KICKOFF_REVIEW_DEPTH` set) | Step 0a | Venue is `native`. Silent. |
| Non-zero exit, timeout, or network failure | During an external call | This **stage** finishes natively: read the canonical role file and perform the role in-harness. Record `[fallback: <reason>]` in the END block. |
| Artifact missing/empty or verdict header missing/malformed | After an external call | Same as above — `[fallback: malformed verdict]`. |

Rules:

- Fallback is **per stage**. A Step 4 fallback does not force Step 6 native; Step 6 retries the external venue unless the failure was clearly sticky (binary gone, auth dead).
- Once a stage falls back mid-way, **all remaining revision rounds of that stage run natively** — no venue thrashing inside a stage.
- Fallback is never an error condition. The phase proceeds; the END block tells the human what happened.

## Revision cycles across harnesses

The 2-cycle cap from [`four-canonical-agents.md`](four-canonical-agents.md) is unchanged. For external rounds, prefer session resume (`codex exec resume <sid>` / `claude --resume <sid> -p`) so the reviewer retains its prior findings; if no session id was captured or resume fails, issue a fresh external call with the full updated plan/diff re-passed. A failed resume that also fails fresh trips the fallback row above.

## Handoff hygiene

- **Redact the implementer's self-assessment.** The external critic receives the diff, the file list, the approved plan, and the phase requirements — never the coder's build-status narrative or "all tests pass" framing. Cold artifacts measurably double-to-quadruple review depth (brief §1).
- **Adversarial framing** in the prompt: "assume the implementer was careful but missed something."
- **Large context via temp files**, referenced by path — never inlined into the prompt argument.
- **Never** invoke the external CLI with sandbox/approval bypass flags (`--yolo`, `--dangerously-skip-permissions`, `danger-full-access`) on behalf of a review role. Read-only review needs none of them.

## END-block reporting

Every `/kickoff` END block records the venue per stage (format owned by `/kickoff`):

```
Review venue (per policies/cross-harness-review.md):
- Plan review: native | codex | claude  [fallback: <reason>]
- Code review: native | codex | claude  [fallback: <reason>]
```

When the other CLI simply isn't installed, the line reads `native (<cli> not on PATH)` — informative, not a failure.

## Relationship to other policies

- [`four-canonical-agents.md`](four-canonical-agents.md) owns the roles, tool stances, verdict headers, and cycle caps; this policy configures only the execution venue of the two reviewer roles.
- [`cross-harness-parity.md`](cross-harness-parity.md) owns canonical-vs-mirror discipline; the canonical role files this policy points external CLIs at are the same files that policy protects.
- [`human-in-the-loop.md`](human-in-the-loop.md) is unaffected: no venue may commit, advance gates, or claim subjective acceptance. The human decides done, whichever vendor reviewed.
