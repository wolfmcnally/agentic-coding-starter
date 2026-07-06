# Policy: Cross-Harness Review

When enabled, `/kickoff` delegates its two **review** stages — plan review (Step 4) and code critique (Step 6) — to the *other* harness's CLI: `codex` when `/kickoff` runs in Claude Code, `claude` when it runs in Codex. This feature moves only the two review roles: orchestration always stays in the invoking harness, and the planner and coder stay too unless a project separately pins them ([`role-models.md`](role-models.md)). A model reviewing another vendor's model catches failure classes same-model review misses; the research and flag-level rationale live in [`briefs/cross-agent-invocation.md`](../briefs/cross-agent-invocation.md).

## Review diversity scales with coder capability

A reviewer from the *same* model family shares the coder's blind spots, and its marginal catches shrink as the coder's baseline quality rises. Cross-model review's value is decorrelation, and decorrelation does not shrink: whatever class of error a frontier coder still makes is precisely the class it is least able to see in its own family's review. Two consequences:

- **The stronger the coding model, the stronger the case for this policy.** Same-family subagent review depreciates with coder capability; cross-harness review is the review mechanism whose value survives it. Do not read a strong coder's streak of clean first-cycle reviews as a reason to disable delegation — read it as same-family review running out of things only a different family would catch.
- **Projects that pin models per role should route the reviewer roles to a different model family from the coder.** Per-role model pinning is provided by [`role-models.md`](role-models.md) (the `role-models.yaml` config, set via `/roles`); where a project pins the coder, `plan-reviewer` and `code-critic` belong on the other family. A `reviewer`/`critic` pin overrides this policy's venue token for that role (and adds a model flag to the same recipes). Where the harness offers only one frontier family natively, this policy's CLI delegation *is* the mechanism that supplies the second family.

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

1. If the env var `KICKOFF_DELEGATION_DEPTH` is set, the venue is `native` regardless of config — this session *is* a delegated role invoked by an outer `/kickoff`; it must not delegate further (recursion guard). The guard is shared with per-role model pinning ([`role-models.md`](role-models.md)); it is named for delegation generally, not review specifically.
2. Read the `cross-harness-review:` token from `CLAUDE.md` Project Context. `disabled` or absent → `native`.
3. Detect the invoking harness: `CLAUDECODE=1` in the environment means Claude Code (alternative CLI: `codex`); otherwise Codex (alternative CLI: `claude`).
4. `command -v <alternative-cli>` — absent → `native` (silent). Present → the alternative CLI is the review venue.

Both review stages use the same resolved venue; the orchestrator does not re-resolve between Step 4 and Step 6 (but a mid-stage failure can demote a single stage — see the fallback state machine).

## Role sourcing

The external CLI is instructed to **read the same canonical role file** the native subagent uses — `.claude/agents/plan-reviewer.md` for Step 4, `.claude/agents/code-critic.md` for Step 6 — and adopt it for the duration of the call. One role definition, two execution venues. Because Codex auto-ingests `AGENTS.md` (→ `CLAUDE.md`) and `claude` auto-loads `CLAUDE.md`, the external reviewer is bound by the same policies, invariants, and verdict contract with no extra plumbing.

The orchestrator passes the **phase-specific inputs** the role file declares (phase reference and heading; full phase text; the plan text for Step 4; the plan and the changed-file list for Step 6) by writing the large pieces to temp files (e.g., under `/tmp`) and referencing their paths in the prompt — never inline. Because the external reviewer runs against a **read-only checkout** and has its own Read/Grep, the Step 6 handoff is a map, not a payload: the file list plus `git diff --stat`, from which the reviewer pulls what it needs. Inline a full diff only when it is small enough to read whole; never pre-materialize a monolithic diff and reject the venue on its size (see Handoff hygiene).

## The two invocation recipes

Claude Code → codex:

```
env -u OPENAI_API_KEY -u CODEX_API_KEY codex exec --json -s read-only -c 'approval_policy="never"' -C "$(pwd)" --output-last-message "$MSGFILE" "$(cat "$PROMPTFILE")" >"$EVENTS" 2>/dev/null </dev/null
```

Non-negotiable: approvals pinned off via the `-c 'approval_policy="never"'` config override (an approval prompt with no TTY can hang the call and has held git index locks; the override is used because `codex exec` flag surfaces churn — e.g., codex-cli 0.136.0 rejects the older `-a/--ask-for-approval` flag on `exec` — while `-c` overrides parse across versions); `-s read-only` (reviewer tool stance; no tree contention); **redirect stdin from `/dev/null` (`</dev/null`)** — `codex exec` reads stdin even with the prompt passed as an argument, and an open non-TTY stdin that never sees EOF (any backgrounded/detached parent — e.g. a harness that runs a long review as a background command) makes it block on `Reading additional input from stdin...` until the wall-clock timeout discards the call; a foreground shell closes stdin and hides the bug, so the redirect is unconditional (empirically: a backgrounded code-review hung on that exact line, killed at 900 s, while the identical foreground call succeeded); capture the **verdict** from the `--output-last-message` artifact (it populates normally under `--json`); `--json` so stdout carries the JSONL event stream and the **session id** can be captured for revision rounds (`TID=$(grep -m1 '"thread.started"' "$EVENTS" | grep -ioE '[0-9a-f-]{36}')`) — without `--json` the session id reaches *only* stderr, which the recipe discards, making it unrecoverable and forcing a fresh cold context every revision round (brief §2); no hardcoded `-m` model (names churn); scrub `OPENAI_API_KEY` / `CODEX_API_KEY` from the child environment (a set `OPENAI_API_KEY` silently flips codex from ChatGPT-plan auth to API-key billing — or 401s on a stale key — while `codex /status` still reports the plan login; brief §2); run with `KICKOFF_DELEGATION_DEPTH=1` in the child environment. If the invocation fails with a flag-parse error, consult `codex exec --help` and adapt — or treat it as a fallback trigger like any other. Revision rounds prefer `codex exec resume <session-id>` — but note the `resume` subcommand rejects `-s/--sandbox` and `-C/--cd`; see "Revision cycles across harnesses" below for the corrected resume recipe.

Codex → claude:

```
env -u CLAUDECODE -u CLAUDE_CODE_ENTRYPOINT -u ANTHROPIC_API_KEY KICKOFF_DELEGATION_DEPTH=1 claude -p "$(cat "$PROMPTFILE")" --permission-mode dontAsk --allowedTools "Read,Grep,Glob" --output-format json --max-turns 50 </dev/null
```

Non-negotiable: **redirect stdin from `/dev/null` (`</dev/null`)** (same trap as codex — a headless `claude -p` can treat a piped stdin from a backgrounded parent as extra input or hang on it; close it unconditionally); `--permission-mode dontAsk`, never `--dangerously-skip-permissions` (its one-time interactive consent dialog hangs without a TTY); `--allowedTools` mirrors the reviewer tool stance (`AskUserQuestion` omitted — a nested CLI cannot reach the human; an unresolved product question becomes a `REVISE` verdict stating the question); scrub `CLAUDECODE` / `CLAUDE_CODE_ENTRYPOINT` / `ANTHROPIC_API_KEY` from the child environment (an inherited `CLAUDECODE=1` makes the inner `claude` refuse to launch; an inherited `ANTHROPIC_API_KEY` silently outranks subscription auth — next paragraph); parse `.result` and `.session_id` from the JSON envelope, and treat an envelope with `is_error: true` as a failed call regardless of content. Revision rounds prefer `claude --resume <session-id> -p`.

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
| Recursion guard (`KICKOFF_DELEGATION_DEPTH` set) | Step 0a | Venue is `native`. Silent. |
| Non-zero exit, timeout, or network failure | During an external call | This **stage** finishes natively: read the canonical role file and perform the role in-harness. Record `[fallback: <reason>]` in the END block. |
| Turn cap exhausted (claude envelope `subtype: "error_max_turns"`, `is_error: true`, no verdict) | After an external call | The investigation is done but unreported and the session id is live — **resume once** (`claude --resume <sid> -p "Conclude your review now: emit the exact verdict header and your essential findings only. Do not investigate further."`) before giving up. If the resume also fails the gate, fall back native: `[fallback: max-turns exhausted]`. |
| Artifact missing/empty or verdict header missing/malformed | After an external call | Same as above — `[fallback: malformed verdict]`. |

Rules:

- The `--max-turns` cap is a **runaway-loop guard, not a review-depth budget** — the wall-clock timeout is the binding guard. Calibrate generously (we use 50): a real code critique reads the role file, plan, file list, diff, sources, and tests, and field use showed a 12-turn cap killing two genuine critiques mid-investigation in one evening. Same philosophy as the timeouts above.
- Fallback is **per stage**. A Step 4 fallback does not force Step 6 native; Step 6 retries the external venue unless the failure was clearly sticky (binary gone, auth dead).
- Once a stage falls back mid-way, **all remaining revision rounds of that stage run natively** — no venue thrashing inside a stage.
- Fallback is never an error condition. The phase proceeds; the END block tells the human what happened.

## Revision cycles across harnesses

The convergence-based loop from [`four-canonical-agents.md`](four-canonical-agents.md) governs external rounds unchanged — iterate while the reviewer's objections are narrowing, escalate the moment they stall or diverge, under the same 5-cycle runaway backstop. For external rounds, prefer session resume so the reviewer retains its prior findings; if no session id was captured or resume fails, issue a fresh external call with the full updated plan/diff re-passed. A failed resume that also fails fresh trips the fallback row above.

The resume recipes are **not** the initial-call recipes with the prompt swapped — each `resume` subcommand has its own flag surface:

- **codex:** `codex exec resume` rejects `-s/--sandbox` and `-C/--cd` (they exist only on the parent `exec`; codex-cli 0.136.0 errors `unexpected argument '-s'`, exit 2 — verified). Set the sandbox via a `-c` override and `cd` into the repo instead of `-C`:

  ```
  ( cd "$REPO" && env -u OPENAI_API_KEY -u CODEX_API_KEY codex exec resume "$TID" --json -c 'approval_policy="never"' -c 'sandbox_mode="read-only"' --output-last-message "$MSGFILE" "$(cat "$PROMPTFILE")" >"$EVENTS" 2>/dev/null </dev/null )
  ```

  (`resume` reads stdin like `exec`, so it carries the same `</dev/null` redirect.)

- **claude:** `claude --resume <sid> -p "$(cat "$PROMPTFILE")"` keeps the same `--permission-mode` / `--allowedTools` / `--output-format json` flags as the initial call; `.session_id` from the JSON envelope is the `<sid>`.

Capturing the session id is itself part of the contract, not an afterthought: codex requires `--json` on the initial call (the id is on stderr otherwise, which the recipe discards); claude reads `.session_id` from its JSON envelope. A recipe that omits codex's `--json`, or a resume that copies the `exec` flags verbatim, silently defeats resume and forces a fresh cold context every round — both were real defects in the first cut of these recipes.

**Re-capture the id from each round's output and thread the latest one forward** — do not keep reusing the first-round id. Both venues currently return a stable id across a resume chain (verified: a 4-round claude chain held one `session_id` throughout and accumulated context across all rounds; codex resume continued the same `thread_id`), but Claude Code's `--resume` has forked the id on resume in some versions, and a stale id would silently resume a pre-fork state and drop the intermediate rounds. Reading the latest id each round is free and immune to that.

## Handoff hygiene

- **Redact the implementer's self-assessment.** The external critic receives the diff, the file list, the approved plan, and the phase requirements — never the coder's build-status narrative or "all tests pass" framing. Cold artifacts measurably double-to-quadruple review depth (brief §1).
- **Adversarial framing** in the prompt: "assume the implementer was careful but missed something."
- **Large context via temp files**, referenced by path — never inlined into the prompt argument.
- **The reviewer explores; it is not spoon-fed.** The recipe already gives the external reviewer a read-only checkout (`-s read-only -C "$(pwd)"` / `--allowedTools "Read,Grep,Glob"`) — it has the same repo the native subagent reads. So hand it a **map, not a payload**: the changed-file list plus `git diff --stat` (what changed and where), and let it pull the specific files it wants with its own tools. Reserve a full inlined-diff temp file for changes small enough to read whole; for anything larger, the file list *is* the handoff.
- **Never pre-materialize a monolithic diff and reject the venue on window size.** A `git diff | wc -c` in the hundreds of KB is not a reason to fall back — it is a reason *not* to inline. Conflating an on-disk artifact with tokens-in-the-context-window is the trap: a reviewer with Read/Grep never loads the whole diff at once, it reads surgically. Delegation is discarded only on the three-signal gate (missing/empty artifact, malformed verdict, timeout/error), never on a pre-computed size estimate. (Observed: a large, fixture-dominated diff was pre-rejected on its byte count without a single external call ever being made.)
- **Flag machine-regenerated blobs.** In the changed-file list, mark generated/regenerated data (fixtures, snapshot JSON, lockfiles, golden files) as "spot-check structure, don't read line-by-line." These dominate a diff's byte count while carrying almost none of its review surface; unflagged, they make a routine change *read* as too big to review.
- **Scope the reading mandate — for plan review too.** When the prompt names sources to read, name the handful of load-bearing files, not "read all the sources the plan touches." A large multi-file phase with an unbounded "read everything" instruction can exhaust the external reviewer's own context (and trip its internal compaction, which can fail on a network stall) before it reaches a verdict. Point it at the core; let it fan out from there if it needs to.
- **Never** invoke the external CLI with sandbox/approval bypass flags (`--yolo`, `--dangerously-skip-permissions`, `danger-full-access`) on behalf of a review role. Read-only review needs none of them.

## END-block reporting

Every `/kickoff` END block records the resolved venue for each role (format owned by `/kickoff`). Because per-role model pinning ([`role-models.md`](role-models.md)) unified the reporting, the block covers all four roles — the reviewer and critic lines carry this policy's venue (or a pin), and the planner and coder lines carry their pin (or `native`):

```
Role model/venue (per policies/role-models.md + policies/cross-harness-review.md):
- Planner:  native (<session model>) | opus | fable | codex  [fallback: <reason>]
- Reviewer (plan review): native | codex | claude | opus | fable | skipped (light lane)  [fallback: <reason>]
- Coder:    native (<session model>) | opus | fable | codex  [fallback: <reason>]
- Critic (code review):   native | codex | claude | opus | fable  [fallback: <reason>]
```

When the other CLI simply isn't installed, the line reads `native (<cli> not on PATH)` — informative, not a failure. A pinned role that fell back is *also* surfaced with 🚨 in the user-facing summary ([`role-models.md`](role-models.md)), so a pin→native disconnect is never silent.

## Relationship to other policies

- [`four-canonical-agents.md`](four-canonical-agents.md) owns the roles, tool stances, verdict headers, and cycle caps; this policy configures only the execution venue of the two reviewer roles.
- [`role-models.md`](role-models.md) generalizes this policy to all four roles: it pins any role to a specific model/harness and reuses these recipes (plus a model flag; write-enabled for the coder) and this fallback machinery. A `reviewer`/`critic` pin overrides the venue token here for that role; the recursion guard and session-resume mechanics are shared.
- [`cross-harness-parity.md`](cross-harness-parity.md) owns canonical-vs-mirror discipline; the canonical role files this policy points external CLIs at are the same files that policy protects.
- [`human-in-the-loop.md`](human-in-the-loop.md) is unaffected: no venue may commit, advance gates, or claim subjective acceptance. The human decides done, whichever vendor reviewed.
