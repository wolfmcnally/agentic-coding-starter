# Policy: Cross-Harness Review

When enabled, `/kickoff` delegates its two **review** stages — plan review (Step 4) and code critique (Step 6) — to the *other* harness's CLI: `codex` when `/kickoff` runs in Claude Code, `claude` when it runs in Codex. Orchestration, planning, and coding always stay in the invoking harness. A model reviewing another vendor's model catches failure classes same-model review misses; the research and flag-level rationale live in [`briefs/cross-agent-invocation.md`](../briefs/cross-agent-invocation.md).

## Review diversity scales with coder capability

A reviewer from the *same* model family shares the coder's blind spots, and its marginal catches shrink as the coder's baseline quality rises. Cross-model review's value is decorrelation, and decorrelation does not shrink: whatever class of error a frontier coder still makes is precisely the class it is least able to see in its own family's review. Two consequences:

- **The stronger the coding model, the stronger the case for this policy.** Same-family subagent review depreciates with coder capability; cross-harness review is the review mechanism whose value survives it. Do not read a strong coder's streak of clean first-cycle reviews as a reason to disable delegation — read it as same-family review running out of things only a different family would catch.
- **Projects that pin models per role should route the reviewer roles to a different model family from the coder.** A per-role model-routing table (a policy file mapping role → model) is an established pattern in derived projects; where one exists, `plan-reviewer` and `code-critic` belong on the other family. Where the harness offers only one frontier family natively, this policy's CLI delegation *is* the mechanism that supplies the second family.

Interaction with review lanes ([`review-lanes.md`](review-lanes.md)): in a `light` lane the code critique is the only review that runs, which makes its venue diversity matter more, not less. Light-lane phases use the resolved venue like any other phase.

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

Default for this template and for projects stamped by `/stamp`: **enabled**. The token is per-project: it lives in Project Context, which `/stamp` rewrites per project and `/teach` never touches.

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
env -u OPENAI_API_KEY -u CODEX_API_KEY codex exec -s read-only -c 'approval_policy="never"' -C "$(pwd)" --output-last-message "$MSGFILE" "$(cat "$PROMPTFILE")" 2>/dev/null
```

Non-negotiable: approvals pinned off via the `-c 'approval_policy="never"'` config override (an approval prompt with no TTY can hang the call and has held git index locks; the override is used because `codex exec` flag surfaces churn — e.g., codex-cli 0.136.0 rejects the older `-a/--ask-for-approval` flag on `exec` — while `-c` overrides parse across versions); `-s read-only` (reviewer tool stance; no tree contention); capture from the `--output-last-message` artifact, not stdout (stderr is progress noise); no hardcoded `-m` model (names churn); scrub `OPENAI_API_KEY` / `CODEX_API_KEY` from the child environment (a set `OPENAI_API_KEY` silently flips codex from ChatGPT-plan auth to API-key billing — or 401s on a stale key — while `codex /status` still reports the plan login; brief §2); run with `KICKOFF_REVIEW_DEPTH=1` in the child environment. If the invocation fails with a flag-parse error, consult `codex exec --help` and adapt — or treat it as a fallback trigger like any other. Revision rounds prefer `codex exec resume <session-id>`.

Codex → claude:

```
env -u CLAUDECODE -u CLAUDE_CODE_ENTRYPOINT -u ANTHROPIC_API_KEY KICKOFF_REVIEW_DEPTH=1 claude -p "$(cat "$PROMPTFILE")" --permission-mode dontAsk --allowedTools "Read,Grep,Glob" --output-format json --max-turns 50
```

Non-negotiable: `--permission-mode dontAsk`, never `--dangerously-skip-permissions` (its one-time interactive consent dialog hangs without a TTY); `--allowedTools` mirrors the reviewer tool stance (`AskUserQuestion` omitted — a nested CLI cannot reach the human; an unresolved product question becomes a `REVISE` verdict stating the question); scrub `CLAUDECODE` / `CLAUDE_CODE_ENTRYPOINT` / `ANTHROPIC_API_KEY` from the child environment (an inherited `CLAUDECODE=1` makes the inner `claude` refuse to launch; an inherited `ANTHROPIC_API_KEY` silently outranks subscription auth — next paragraph); parse `.result` and `.session_id` from the JSON envelope, and treat an envelope with `is_error: true` as a failed call regardless of content. Revision rounds prefer `claude --resume <session-id> -p`.

`ANTHROPIC_API_KEY` is scrubbed **unconditionally** because the methodology's assumed auth model is OAuth subscription login for both CLIs (`claude` via its interactive login, `codex` via `~/.codex/auth.json`). Under that model an environment API key is never the intended auth — it is contamination: Claude Code injects a session-scoped key into every child process, and a stale key can ride into even a genuine Codex parent through its inherited environment with no key in any shell rc. A set key silently outranks subscription auth — by *documented, intentional* credential precedence, not by bug — and a stale one fails with `is_error: true`, `api_error_status: 401`, `"Invalid API key · Fix external API key"`; verified empirically, including in a derived project's first live Codex → claude plan review. The scrub costs nothing when no key is present, and every login-based auth path (keychain OAuth, `CLAUDE_CODE_OAUTH_TOKEN`, `apiKeyHelper`) survives it by construction — none depend on the env var. A project that genuinely authenticates `claude` with an API key (e.g., API-key CI) amends this recipe to re-export the key explicitly into the child environment rather than relying on ambient inheritance. Precedence chains, the symmetric codex-side trap, and hard backstops: [`briefs/cross-agent-invocation.md`](../briefs/cross-agent-invocation.md) §§2–4.

Full flag-by-flag rationale, auth notes, and the macOS sandbox-network caveat: [`briefs/cross-agent-invocation.md`](../briefs/cross-agent-invocation.md) §§2–3.

## Fallback state machine

Success of an external review call is gated on **three signals together**:

1. The output artifact (codex `--output-last-message` file / claude JSON `.result`) exists and is non-empty.
2. It contains exactly one `## Verdict: APPROVED` or `## Verdict: REVISE` header.
3. The call returned within a wall-clock timeout — 600 s for plan review, 900 s for code critique. The timeout is a **hang guard, not a performance target**: its only job is to keep a stalled subprocess (approval prompt, consent dialog, network stall) from hanging the orchestrator. It is generous by design — a working external review takes as long as it takes, and timing one out discards real work and burns quota for nothing. Tune upward freely for large phases; tighten only with evidence.

Any signal failing means the call failed. Triggers and handling:

| Trigger | Detected | Action |
|---|---|---|
| Alternative CLI not on PATH | Step 0a | Venue is `native` for the whole session. Silent; venue report reads `native (<cli> not on PATH)`. |
| Recursion guard (`KICKOFF_REVIEW_DEPTH` set) | Step 0a | Venue is `native`. Silent. |
| Non-zero exit, timeout, or network failure | During an external call | This **stage** finishes natively: read the canonical role file and perform the role in-harness. Record `[fallback: <reason>]` in the END block. |
| Turn cap exhausted (claude envelope `subtype: "error_max_turns"`, `is_error: true`, no verdict) | After an external call | The investigation is done but unreported and the session id is live — **resume once** (`claude --resume <sid> -p "Conclude your review now: emit the exact verdict header and your essential findings only. Do not investigate further."`) before giving up. If the resume also fails the gate, fall back native: `[fallback: max-turns exhausted]`. |
| Artifact missing/empty or verdict header missing/malformed | After an external call | Same as above — `[fallback: malformed verdict]`. |

Rules:

- The `--max-turns` cap is a **runaway-loop guard, not a review-depth budget** — the wall-clock timeout is the binding guard. Calibrate generously (we use 50): a real code critique reads the role file, plan, file list, diff, sources, and tests, and field use showed a 12-turn cap killing two genuine critiques mid-investigation in one evening. Same philosophy as the timeouts above.
- Fallback is **per stage**. A Step 4 fallback does not force Step 6 native; Step 6 retries the external venue unless the failure was clearly sticky (binary gone, auth dead).
- Once a stage falls back mid-way, **all remaining revision rounds of that stage run natively** — no venue thrashing inside a stage.
- Fallback is never an error condition. The phase proceeds; the END block tells the human what happened.

## Revision cycles across harnesses

The convergence-based loop from [`four-canonical-agents.md`](four-canonical-agents.md) governs external rounds unchanged — iterate while the reviewer's objections are narrowing, escalate the moment they stall or diverge, under the same 5-cycle runaway backstop. For external rounds, prefer session resume (`codex exec resume <sid>` / `claude --resume <sid> -p`) so the reviewer retains its prior findings; if no session id was captured or resume fails, issue a fresh external call with the full updated plan/diff re-passed. A failed resume that also fails fresh trips the fallback row above.

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
