---
name: kickoff
description: >-
  Orchestrate a single phase of plan/ end-to-end: pick up the next phase,
  plan, review plan, implement, review code, build/test, update status
  markers in plan/INDEX.md, and log. Language- and surface-agnostic; the
  project's CLAUDE.md and phase file declare which build gates to run.
  Invoke as /kickoff (picks up the ⬅️ phase) or /kickoff phase N (targets
  a specific phase).
---

# Kickoff: Single-Phase Session

Orchestrate a full implementation of one phase under `plan/`, from plan through working code, following the plan → plan-review → code → code-review → build pipeline.

This skill is language- and surface-agnostic. The project's `CLAUDE.md` declares the conventions; the phase file declares the deliverables; the planner picks the build gates; the orchestrator runs them.

## Current context

- Branch: `git branch --show-current`
- Phase markers: `grep -E '^\| \[Phase ' plan/INDEX.md 2>/dev/null || echo "(plan/INDEX.md missing)"`
- Recent log: `tail -20 LOG.md 2>/dev/null || echo "(no log)"`

## Parse arguments

Raw arguments: `!{ARGUMENTS}`

- If empty, Step 1 picks up the `⬅️` phase.
- If `phase N` or `phase N.M` (e.g., `phase 1`, `phase 1.3`), target that specific phase file `plan/phase-<id>.md`.
- If free text, treat it as a phase description and try to match it against a phase row in `plan/INDEX.md`. If nothing matches, ask the user which phase they mean rather than guess.

## Workflow

### Step 0a: Resolve per-role model/venue

Resolve once per session, before phase work begins, per [`policies/role-models.md`](../../../policies/role-models.md). This resolves a `(venue, model, effort)` for **each of the four roles** from `kickoff.yaml`'s harness-aware `role_models` section.

1. **Recursion guard.** If the env var `KICKOFF_DELEGATION_DEPTH` is set, this session is *itself* a delegated role invoked by an outer `/kickoff`; **every role runs native** and no further delegation happens. Skip the rest of Step 0a.
2. **Detect the orchestrating harness `H`:** `CLAUDECODE=1` in the environment → `claude`; otherwise → `codex`.
3. **Read + resolve.** Run `./bin/kickoff-config show models` — it validates the complete human-editable `kickoff.yaml` and prints the resolved `model` plus optional separate `effort` field per role for the current harness. (The resolution rule is: `role_models[H][role]` if set, else `role_models['default'][role]` if set, else `{model: default}`.) Models are `default | claude | codex | opus | fable | sol | terra | luna`; effort is absent/default or `low | medium | high | xhigh`, plus Claude-only `max`.
4. **Map each resolved value to a venue:**
   - `default` → **native** (in-harness subagent on the session model). No CLI.
   - `claude` → the `claude` CLI, its configured default model (no `--model`).
   - `codex` → the `codex` CLI, its configured default model (no `-m`).
   - `opus` / `fable` → the `claude` CLI, `--model opus|fable`.
   - `sol` / `terra` / `luna` → the `codex` CLI,
     `--model gpt-5.6-sol|terra|luna` respectively.
   - A separate effort field adds `-c 'model_reasoning_effort="<effort>"'` to Codex
     initial and resume invocations, or `--effort <effort>` to Claude initial
     and resume invocations. An absent effort field preserves the configured/default effort.

Remember each role's resolved `(venue, model, effort)` and the orchestrating harness for Steps 3–6 and the Step 10 END block. Roles do not re-resolve mid-session. A non-`default` model always goes through the CLI recipe — do **not** short-circuit "model == session model" (uniform resolution, no session-model probing).

### Step 0b: Preflight every non-native role venue

Before identifying a phase, changing a status marker, writing `LOG.md`, or invoking any role, run:

```
./bin/kickoff-config preflight
```

This deterministic preflight resolves the same role pins as Step 0a and makes one live sentinel call for every unique non-native `(CLI, model, effort, access mode)` target. It uses the production credential scrubs, model/effort overrides, headless flags, stdin closure, and read-only versus write-enabled posture, but runs in an empty temporary working directory so it neither loads repository context nor touches the tree (the Codex probe adds `--skip-git-repo-check` solely because that directory is intentionally not a checkout). The active orchestrator needs no probe because the current session already proves it is authenticated; every role that will run through a subprocess is probed, including a deliberately configured same-vendor pin. Duplicate targets are probed once.

The preflight validates the full upstream path needed by the phase: CLI presence, usable authentication, model entitlement, network reachability, current flag compatibility, sandbox/access posture, a response within the 120-second hang guard, and an exact `KICKOFF_PREFLIGHT_OK` sentinel. A status command or credential-file check is insufficient because it does not prove a live model call under the production environment.

**Any failure aborts `/kickoff` immediately.** Report the failed target and the script's diagnostic, then stop. Do not fall back to native, identify or decompose the phase, change `plan/INDEX.md`, append a START/END block, or invoke an agent. After the user fixes authentication or the other upstream error, they rerun `/kickoff` from a clean pre-phase state. If every role is native, or the recursion guard makes every role native, the script reports `N/A` / `skipped` and succeeds.

### Step 0c: Load per-role execution budgets

Run `./bin/kickoff-config show timeouts` and retain the first-event timeout, each role's hard deadline and idle watchdog, plus its Claude-only `claude_max_turns` circuit breaker from `kickoff.yaml`'s `role_timeouts` section, per [`policies/role-timeouts.md`](../../../policies/role-timeouts.md). The three clocks apply to **every invocation or resumed revision round**; the turn value applies only when the delegated venue is Claude, because Codex and native subagents expose no equivalent flag. The shipped seed values are below; when a project has deliberately recalibrated its config, the validated config output governs:

- planner — 1,800 s hard / 600 s idle / 50 turns;
- reviewer — 1,800 s hard / 600 s idle / 50 turns;
- coder — 7,200 s hard / 1,200 s idle / 200 turns;
- critic — 2,700 s hard / 600 s idle / 50 turns;
- every role — first structured event within 120 s.

For every external CLI call, including resumes and the one permitted max-turn rescue, invoke the production command through `./bin/kickoff-config watch` with `--role`, resolved `--venue`, `--model`, `--effort`, phase id, and named stdout/stderr/result artifacts. Pass Claude's extracted result path as `--result-file`; pass Codex's `--output-last-message` path as `--required-output-file`. The wrapper closes stdin, verifies that the actual CLI/model/effort flags match its metadata, truncates result paths before launch, requires a structured event and fresh result, streams progress, terminates the whole process group on first-event/idle/hard timeout, returns 124 on timeout or 65 on a protocol failure, and appends local telemetry to `.kickoff/role-timings.jsonl`. Codex must emit JSONL with `--json`; Claude must emit JSONL with `--output-format stream-json --verbose`. Preserve each role's timing record for Step 10.

For native subagents, use the same role-specific hard and idle budgets through the harness's wait/status mechanism. Progress means a real agent event, status transition, or tool result; the orchestrator's own polling is not progress. If the harness cannot expose idle timing, enforce the hard deadline and record first-event/idle as `unavailable`. Keep the user informed at least every 60 seconds while waiting.

### Step 1: Identify the phase

Read `plan/INDEX.md` (the authoritative phase ledger) and locate the phase to work on. Status markers live in the `INDEX.md` phase table, not in the per-phase files (see [`policies/phase-status.md`](../../../policies/phase-status.md)).

- **No arguments**: find the row whose status is `⬅️` in the phase table. If multiple rows are marked `⬅️` (should never happen), pick the earliest in the dependency graph and warn the user.
- **`phase N` / `phase N.M`**: find the row whose link is `[Phase <id>](phase-<id>.md)`.
- **Free text**: resolve to a phase row or ask the user.

Then resolve the **review lane** per [`policies/review-lanes.md`](../../../policies/review-lanes.md): read `review_lane:` from the target phase file's frontmatter. Absent or `full` → **full** lane. `light` → **light** lane: Step 4 (plan review) will be skipped; the code critic still runs and guards the lane. You may upgrade a declared `light` to `full` when the phase's actual deliverables look non-mechanical — note the upgrade and why. Never downgrade `full` to `light` on your own.

Tell the user which phase you are picking up, the path to its file (`plan/phase-<id>.md`), and the resolved review lane.

### Step 1a: Sub-phase decomposition (parent phases only — just-in-time, one at a time)

The parent `phase-N.md` was drafted at bootstrap (or by an earlier major-phase-close ripple — see Step 9b). Step 1a decides whether to decompose its sub-phases, not whether to draft the parent itself.

If the target is a **parent phase** (`phase-N.md`, not `phase-N.M.md`) and no `plan/phase-N.*.md` sub-phase files exist for it yet:

- If the phase's Deliverables list is small (≤ 3 distinct surfaces) and fits one focused session, proceed monolithically — skip to Step 2.
- If the phase is large or multi-surface, **decompose just-in-time, one sub-phase at a time**. Size the bite to the executing coder model's demonstrated coherence, not to a fixed calendar (see [`briefs/methodology.md`](../../../briefs/methodology.md) §6): when recent phases of the current size have been closing with first-cycle approvals and green gates, prefer fewer, larger sub-phases; split finer only when revision loops or build-gate fix cycles have been saying so.
  1. Invoke `phase-planner` for a one-shot decomposition of `phase-N.1` *only* (full Goal / Deliverables / Acceptance / brief refs, plus a `review_lane:` frontmatter assignment per [`policies/review-lanes.md`](../../../policies/review-lanes.md) eligibility — default `full`).
  2. Write `phase-N.1.md`. Update `plan/INDEX.md`'s phase table to add the new row and adjust the dependency graph.
  3. Mark the parent `🚧` and `phase-N.1` `⬅️`. Restart `/kickoff` against `phase-N.1`.
  4. **Do not draft `phase-N.2`, `phase-N.3`, etc. yet.** Their shape benefits from `phase-N.1`'s outcomes. Subsequent sub-phases land at sub-phase close (see Step 9a). See [`briefs/methodology.md`](../../../briefs/methodology.md) §6.

Surface the decomposition decision (or the choice to stay monolithic) to the user in the opening report.

(Major-phase JIT does *not* happen here — every major phase the brief surfaces was sketched at bootstrap per [`briefs/agentic-bootstrap.md`](../../../briefs/agentic-bootstrap.md) §8. If a sketched `phase-N.md` is missing when `/kickoff` reaches Phase N, that is a bootstrap-completeness failure to surface to the user, not a Step 1a responsibility.)

### Step 2: Flip marker and open the log

Update `plan/INDEX.md` so the target row's status cell is `🚧`. **Do not edit the target `plan/phase-<id>.md` file's frontmatter or body** — status is stored only in `INDEX.md` (see [`policies/phase-status.md`](../../../policies/phase-status.md)).

Append a START entry to `LOG.md`. Create `LOG.md` if it does not exist (with the header described in [`policies/log-discipline.md`](../../../policies/log-discipline.md)). Format:

```
## <YYYY-MM-DD HH:MM> — START
<Phase heading>

Planned work:
- <deliverable 1>
- <deliverable 2>
- ...
```

Use the phase's "Deliverables" list from `plan/phase-<id>.md` verbatim (trimmed to the bullet text). If the phase has no Deliverables section, fall back to the phase's Goal paragraph rephrased as bullets.

### Step 3: Plan

**Native venue** (planner unpinned, per Step 0a): delegate the planning stage to the `phase-planner` subagent (Claude Code) / the `phase-planner` agent (Codex), enforcing the planner budget from Step 0c. Pass it:

- The phase identifier (e.g., `Phase 1.3`) and heading.
- The full phase text from `plan/phase-<id>.md` (copy/paste, do not summarize).
- Nothing about the agent's own procedure — the role definition already covers the reading protocol and output format.

**Delegated venue** (`claude`/`codex`/`opus`/`fable`/`sol`/`terra`/`luna`, with optional effort, per Step 0a): run the planner in that CLI per [`policies/role-models.md`](../../../policies/role-models.md), reusing the read-only recipe in [`briefs/cross-agent-invocation.md`](../../../briefs/cross-agent-invocation.md) with the resolved model/effort flags and `KICKOFF_DELEGATION_DEPTH=1` in the child environment, wrapped by `bin/kickoff-config watch` with the planner budget. The planner is read-only but needs its full tool stance — `--allowedTools "Read,Grep,Glob,WebSearch,WebFetch"` for claude; codex read-only sandbox. Instruct the external agent to read `.claude/agents/phase-planner.md` and adopt that role; pass the phase reference and full phase text via a temp file. Capture the session id for revision rounds (codex `--json` `thread_id`; claude stream event `session_id`) — the planner resumes across plan-revision rounds with the same resolved model and effort. If a later runtime call fails despite the successful preflight, fall back to the native `phase-planner` and record it for Step 10; that is a 🚨 disconnect.

Wait for the plan.

### Step 4: Review the plan

**Light lane** (per Step 1's lane resolution): skip this step entirely. Record `Plan review: skipped (light lane)` for the END block and proceed to Step 5. Everything below applies to the full lane only.

**Native venue** (per Step 0a): delegate the review stage to the `plan-reviewer` agent. Pass it:

- The phase reference and heading.
- The full phase text from `plan/phase-<id>.md`.
- The full plan text from Step 3.

**Delegated venue** (the non-`default` model `reviewer` resolved to in Step 0a): run the role in that CLI per [`policies/role-models.md`](../../../policies/role-models.md). The shipped `kickoff.yaml` resolves reviewer to the *other* harness (cross-vendor review); a project may resolve it anywhere. Add the resolved model and effort flags to the recipe below and preserve them on resume; everything else is identical. A later runtime failure despite the successful preflight falls back to native with a 🚨 in Step 10.

1. Write the full phase text and the full plan text to temp files (e.g., `/tmp/kickoff-phase-<id>.md`, `/tmp/kickoff-plan-<id>.md`). Do not include the planner's own confidence statements or open-questions commentary beyond the plan text itself.
2. Write a prompt file instructing the external agent to: read `.claude/agents/plan-reviewer.md` and adopt that role for this review; review the plan in `<plan temp file>` against the phase text in `<phase temp file>`; assume the planner was careful but missed something; end with the exact verdict header (`## Verdict: APPROVED` or `## Verdict: REVISE`). Note that `AskUserQuestion` is unavailable in this venue — an unresolved product decision becomes `REVISE` with the question stated. **Scope the reading mandate** — the reviewer has a read-only checkout and its own Read/Grep, so name the handful of load-bearing files to read (the sources the plan actually reshapes), not "read all the sources the plan touches." An unbounded "read everything" instruction on a large multi-file phase can exhaust the external reviewer's own context (and trip its internal compaction, which can fail on a network stall) before it reaches a verdict — see [`briefs/cross-agent-invocation.md`](../../../briefs/cross-agent-invocation.md) §4.
3. Invoke the recipe for the venue from [`briefs/cross-agent-invocation.md`](../../../briefs/cross-agent-invocation.md) through `bin/kickoff-config watch` with the reviewer budget and named event/diagnostic/result artifacts (codex emits `--json` and supplies `--required-output-file`; claude emits `--output-format stream-json --verbose` and supplies `--result-file`). Put the resolved model and effort flags on the actual child CLI command as well as the watchdog metadata; the watchdog rejects any mismatch before launch. The API-key scrubs are unconditional because a set key silently outranks subscription auth; the wrapper closes stdin. **Capture the session id for revision rounds**: for codex it is the first stdout event, `{"type":"thread.started","thread_id":"<uuid>"}`; for claude, read `session_id` from the stream. A flag-parse error from a churned CLI version counts as an invocation failure (next item).
4. Gate on the three-signal check: output artifact non-empty, exactly one `## Verdict:` header, and execution inside all three clocks. Exception before falling back: a claude stream result with `subtype: "error_max_turns"` means the investigation finished but went unreported — **resume the session once** (`claude --resume <sid> -p "Conclude your review now: emit the exact verdict header and your essential findings only. Do not investigate further."`) and re-gate. On failure (including a failed rescue): perform this stage with the native `plan-reviewer` instead, record `[fallback: <reason>]` for the END block, and keep all remaining rounds of this stage native.

**If `APPROVED`**: proceed to Step 5. Show the user a brief summary plus any Minor Corrections (do not wait for explicit approval unless the user asked to review plans themselves).

**If `REVISE`**: re-run `phase-planner` with the reviewer's feedback appended to the prompt, then re-review in the same venue — native re-runs `plan-reviewer`; external prefers session resume (`codex exec resume <sid>` / `claude --resume <sid> -p`), falling back to a fresh external call with the full updated plan re-passed. Use the policy's resume recipe, not the initial-call recipe with the prompt swapped: `codex exec resume` rejects `-s/--sandbox` and `-C/--cd` (set sandbox via `-c 'sandbox_mode="read-only"'`, `cd` into the repo instead of `-C`); see [`briefs/cross-agent-invocation.md`](../../../briefs/cross-agent-invocation.md) §2. Keep iterating only while the reviewer's objections are **converging on approval** (shrinking in count and severity, no finding re-raised, no equal-or-worse new findings); the moment the loop stalls or diverges — same objection recurring, whack-a-mole, or an unresolvable product/architecture disagreement — present the plans and the sticking point to the user for a manual decision. A 5-cycle runaway backstop applies per [`policies/four-canonical-agents.md`](../../../policies/four-canonical-agents.md): never iterate past it without surfacing to the user.

### Step 5: Implement

**Native venue** (coder unpinned, per Step 0a): delegate implementation to the `phase-coder` agent. Pass it:

- The approved plan (full text, including any Minor Corrections from the plan-reviewer appended as a note).

**Pinned venue** (any non-`default` model, per Step 0a): run the coder in that model's implied CLI per [`policies/role-models.md`](../../../policies/role-models.md), using the **write-enabled** recipe (the coder writes — unlike every read-only reviewer role):

1. Instruct the external agent to read `.claude/agents/phase-coder.md` and adopt that role; pass the approved plan (full text) via a temp file.
2. Invoke the write-enabled recipe with `KICKOFF_DELEGATION_DEPTH=1` in the child environment:
   - **claude coder:** run `claude -p "$(cat "$PROMPTFILE")" --model <m> [--effort <effort>] --permission-mode dontAsk --allowedTools "Read,Grep,Glob,Write,Edit,Bash" --output-format stream-json --verbose --max-turns <coder claude_max_turns>` through `bin/kickoff-config watch`, with the credential scrubs and recursion guard from the invocation brief. The implementation loop uses the coder's larger budget; `.git`/`.claude` stay non-auto-approved under `dontAsk`, and the coder writes under the deliverable dir.
   - **codex coder:** the Step 4 codex recipe but `-s workspace-write` (initial) / `-c 'sandbox_mode="workspace-write"'` (resume), plus the resolved `--model gpt-5.6-<name>` and `model_reasoning_effort` overrides when present. **Never** `--yolo`/`danger-full-access`.
3. **Single-writer guarantee:** `/kickoff` is sequential, so during this stage no native writer touches the tree — the pinned coder owns it exclusively (build gates run afterward, Step 7). This satisfies "serialize or isolate — never two writers on one tree" without a worktree.
4. Capture the session id (codex `--json` `thread_id`; claude stream `session_id`) — the coder resumes across code-revision and build-fix rounds. Read the report (file list, Build Status, Manual Checks) from the watcher result artifact / codex `--output-last-message`; the file writes have already landed in the tree.
5. **Fallback:** a later three-signal gate failure or timeout despite the successful preflight → fall back to the native `phase-coder`, record `[fallback: <reason>]`, and raise the 🚨 disconnect for Step 10. Do not attempt to repair the sandbox mid-run.

Wait for the coder. Collect the list of files created or modified, the Build Status block, and the Manual Checks list.

### Step 6: Review code

**Native venue** (per Step 0a): delegate code review to the `code-critic` agent. Pass it:

- The approved plan (full text).
- Any Minor Corrections the plan-reviewer issued.
- The list of files the coder created or modified.
- **Light lane only:** the lane declaration, with the instruction to additionally judge lane fit per [`policies/review-lanes.md`](../../../policies/review-lanes.md) — did the diff stay within mechanical scope?

**Delegated venue** (the non-`default` model `critic` resolved to in Step 0a): run the role in that model's implied CLI per [`policies/role-models.md`](../../../policies/role-models.md). The shipped `kickoff.yaml` resolves critic to the *other* harness (cross-vendor review). Add the resolved model and effort flags and preserve them on resume; a later runtime failure despite the successful preflight falls back with a 🚨 in Step 10.

1. Write the approved plan and the **changed-file list** to temp files, and capture `git diff --stat` (what changed and where). The external reviewer runs against a **read-only checkout** with its own Read/Grep, so hand it a map, not a payload: it pulls the specific files it wants. Inline a full diff into a temp file only when the change is small enough to read whole; for a large change the file list + `git diff --stat` *is* the handoff. **Never pre-materialize a monolithic diff and reject the venue because `git diff | wc -c` is large** — an on-disk artifact is not tokens-in-the-window; a reviewer with Read/Grep reads surgically, and delegation is discarded only on the three-signal gate below, never on a pre-computed size estimate. **Flag machine-regenerated blobs** in the file list (fixtures, snapshot JSON, lockfiles, golden files) as "spot-check structure, don't read line-by-line" — they dominate byte count but carry almost no review surface. **Redact the coder's self-assessment** — no Build Status block, no Manual Checks narrative, no "tests pass" framing. Cold artifacts review 3–4× deeper (see [`briefs/cross-agent-invocation.md`](../../../briefs/cross-agent-invocation.md) §§1, 4).
2. Write a prompt file instructing the external agent to: read `.claude/agents/code-critic.md` and adopt that role for this review; review the changed files (listed in the file-list temp file; explore them via the read-only checkout) against the plan in the temp file; assume the implementer was careful but missed something; end with the exact verdict header.
3. Invoke the policy's recipe for the venue through `bin/kickoff-config watch`, with `KICKOFF_DELEGATION_DEPTH=1` in the child environment and the critic budget from Step 0c. Capture the session id for revision rounds the same way as Step 4 (codex: `--json` first event `thread_id`; claude: stream `session_id`).
4. Gate on the three-signal check (artifact non-empty; exactly one `## Verdict:` header; execution inside all three clocks). Exception before falling back: on `subtype: "error_max_turns"`, resume the session once with the "conclude now" instruction (as in Step 4) and re-gate. On failure (including a failed rescue): perform this stage with the native `code-critic` instead, record `[fallback: <reason>]` for the END block, and keep all remaining rounds of this stage native.

**If `APPROVED`**: proceed to Step 7.

**If `REVISE`**: re-run `phase-coder` with the critic's feedback, then re-review in the same venue (resume preferred externally, as in Step 4). Keep iterating only while the critic's findings are **converging on approval** (shrinking in count and severity, no finding re-raised, no equal-or-worse new findings); the moment the loop stalls or diverges — same finding recurring, whack-a-mole, or an unresolvable disagreement — present the issues to the user. A 5-cycle runaway backstop applies per [`policies/four-canonical-agents.md`](../../../policies/four-canonical-agents.md): never iterate past it without surfacing to the user.

**If `REVISE` opens with `Escalate: full lane — <reason>`** (light lane only): the work exceeded mechanical scope. Run the skipped Step 4 plan review now, against the plan as-built (same venue rules), route its outcome through the normal revision loops, and finish the phase in the full lane. Record `light → full (escalated: <reason>)` for the END block. The lane escalation itself is not a stall signal and does not count toward the runaway backstop; the critic's other Required Changes do feed the convergence judgment.

### Step 7: Final build gate

Even though the coder ran the build commands, re-run them in the orchestrator context to guarantee the merged state is green. Build commands depend on the surfaces the phase touched.

Identify "touched surfaces" by looking at the files the coder reported plus `git status`. Then run the gates declared in the plan's **Build Gate Sequence** section, in order.

The project's primary build gates come from the project's actual tooling. For the **Agentic Coding Starter Template itself**, the example Python project lives under `project/` per [`policies/project-isolation.md`](../../../policies/project-isolation.md), so the gates are:

```
cd project && uv run ruff check example tests ../bin/kickoff-config ../tests && uv run ruff format --check example tests ../bin/kickoff-config ../tests && uv run pytest -q tests ../tests
```

The `cd project && ...` pattern is the canonical shape (single executable line; uniform across language ecosystems). Projects that opt out of the `project/` convention put the metadata at the root and drop the `cd project &&` prefix. A project derived from this template via `/stamp` may have different gates — Node, Rust, Go, polyglot. The planner is responsible for listing them; the orchestrator runs whatever the planner listed.

If any build gate fails:

1. Classify the failure:
   - **Coder error** (syntax, type mismatch, missing import, wrong signature, failing test assertion) → re-run `phase-coder` with the error output and the plan.
   - **Plan error** (wrong file path, missing module, architectural mismatch) → re-run `phase-planner` with the error, then `phase-coder` with the updated plan. Counts as one cycle.
   - **Environment error** (missing toolchain, missing system dependency, missing credential) → report to the user immediately; do not retry.
2. Re-run the failing gate after the fix.
3. On success, re-run `code-critic` on the files the coder touched during the fix (same venue rules as Step 6). If `REVISE`, back to coder (feeds the code-review convergence judgment).
4. Keep iterating only while the build gate is **converging** — each fix knocks down failures and the error surface shrinks. Escalate the moment it stalls: the same failure recurs, or each fix trades one break for another (oscillation). A 5-cycle runaway backstop applies per [`policies/four-canonical-agents.md`](../../../policies/four-canonical-agents.md); environment errors escalate immediately (step 1) regardless.

### Step 8: Phase-specific acceptance gates

Each phase declares its own empirical acceptance checks under `Acceptance` in `plan/phase-<id>.md`. The orchestrator runs whichever of those checks are mechanically executable (shell commands, smoke scripts, curl probes, deterministic comparisons) and reports the rest as **manual checks** for the user.

A failed acceptance gate routes back through Step 7's fix loop.

Per [`policies/acceptance-empirical.md`](../../../policies/acceptance-empirical.md), every acceptance criterion is either executable or named manual. Treat ambiguous criteria as manual and flag them in the END block.

### Step 9: Update status markers

In `plan/INDEX.md`'s phase table (and only there):

1. Flip the completed phase's status cell from `🚧` to `✅`.
2. **If the closed phase was a sub-phase** (`phase-N.M.md`), go to Step 9a. Step 9a owns next-sub-phase drafting, the ripple sub-step, and (if the parent rolled up) handing off to Step 9b.
3. **Otherwise** (closed phase was a monolithic major phase with no sub-phases), go to Step 9b. Step 9b owns the major-phase ripple pass and advancing `⬅️`.

If the phase is only partially complete (the user paused mid-way), leave it `🚧` and do not advance `⬅️`.

**Never edit the per-phase file's frontmatter or body to record status.** Per-phase frontmatter is `id` / `title` / `depends_on` / `informs` plus optional `review_lane` ([`policies/review-lanes.md`](../../../policies/review-lanes.md)) only.

### Step 9a: Draft the next sub-phase (sub-phase close only)

If the just-closed phase was a sub-phase `phase-N.M.md` and the parent `phase-N.md`'s Deliverables are **not yet fully addressed** by the closed sub-phases:

1. Invoke `phase-planner` to draft `phase-N.(M+1).md` with the benefit of the closed sub-phases' outcomes. Pass it: the parent's full text, the list of closed sub-phases with their END summaries, and the parent's remaining un-addressed deliverables. The draft includes a `review_lane:` frontmatter assignment per [`policies/review-lanes.md`](../../../policies/review-lanes.md) eligibility (default `full`), and is sized per the capability-indexed guidance in Step 1a.
2. Write `phase-N.(M+1).md`. Update `plan/INDEX.md` (new row, dependency graph if needed).
3. Mark `phase-N.(M+1)` `⬅️`. Parent stays `🚧`.

If the parent's Deliverables **are** fully addressed by the closed sub-phases:

1. Mark the parent `✅`.
2. Run Step 9b (below) to ripple into the next major phase and advance `⬅️`. (Step 9.2's normal "advance to next `⏳`" is subsumed by Step 9b.)

If the closed sub-phase reveals that the parent's Deliverables list needs revision (new deliverable surfaced, an existing one no longer applies), surface this to the user explicitly in Step 10's report rather than silently rewriting the parent. The parent edit is a Wolf decision.

This step implements just-in-time, one-at-a-time sub-phase decomposition per [`briefs/methodology.md`](../../../briefs/methodology.md) §6 — `phase-N.(M+1)` is drafted *with* `phase-N.M`'s outcomes in hand, not in advance.

**Then run the ripple sub-step** before proceeding to Step 10. This applies whether the parent is still `🚧` (a new sub-phase was drafted in 1–3 above) or just rolled up to `✅` (Step 9b took over). The ripple sub-step exists per [`policies/phase-ripple.md`](../../../policies/phase-ripple.md):

1. Read the closing sub-phase's `LOG.md` END block, the plan-reviewer's Observations, and the code-critic's verdict body.
2. Identify candidate ripples: pinned values, renamed paths, added brief refs, tightened Acceptance criteria, surfaced concerns addressed to a later phase by name.
3. For each candidate, walk the downstream drafted phase files — siblings (`phase-N.(M+1)`, `phase-N.(M+2)`, …, just-drafted or already drafted) plus downstream major phases (`phase-(N+1).md`, `phase-(N+2).md`, …, sketched at bootstrap). Classify each potential edit:
   - **AUTO** (mechanical, one correct shape): apply the edit now. If the edit is more than one line (e.g., reshaping an Acceptance section to incorporate a now-pinned value), invoke `phase-planner` with the downstream file and the ripple description; otherwise edit directly.
   - **DECIDE** (judgment-bearing): do *not* edit. Capture the item for the END block.
4. AUTO edits land before Step 10 writes the END block; the END block lists every AUTO ripple applied and every DECIDE ripple surfaced.

If no downstream drafted phase files exist (e.g., this is the project's only phase, or all later phases are already ✅), the ripple sub-step is a no-op — note `none — no downstream sketches` in the END block.

### Step 9b: Major-phase close — ripple and advance ⬅️ (major-phase close only)

Runs when a major phase's row was just flipped to `✅` — either by Step 9.3 directly (the closed phase was a monolithic major phase) or by Step 9a's parent-rollup branch (the closed phase was the last sub-phase under its parent).

1. **Ripple pass** against the next drafted major phase (`phase-(N+1).md`) and any subsequent sketched phases. Procedure mirrors Step 9a's ripple sub-step (read END block + verdict bodies; classify each candidate AUTO/DECIDE; apply AUTO; capture DECIDE for the END block). The major-phase ripple is more likely to touch Goal and Deliverables (lower-fidelity sketches have more headroom) and Acceptance (sketched criteria need tightening once the upstream phase pins them).
2. **Advance `⬅️`.** Find the next `⏳` row in the dependency graph order (honoring parallel opportunities). Change it to `⬅️`. Only one `⬅️` at a time.
3. **Sketched-phase completeness check.** If the new `⬅️` row points at a `phase-N.md` that doesn't exist as a file (only a row in INDEX.md), this is a bootstrap-completeness failure — flag in the END block. Do not auto-draft it; per [`briefs/agentic-bootstrap.md`](../../../briefs/agentic-bootstrap.md) §8, every major phase the brief surfaces should have been sketched at bootstrap.

If no downstream major phase exists (project complete), Step 9b's ripple is a no-op and `⬅️` advances to nothing — the project is done. Surface this to the user in the report.

### Step 10: Close the log and report

Append an END entry to `LOG.md`:

```
## <YYYY-MM-DD HH:MM> — END
<Phase heading>

Files changed:
- <path> — <brief>
- ...

Build status:
- <gate 1>: OK | N/A | failed (<short reason>)
- <gate 2>: OK | N/A | failed (<short reason>)
- ...

Review lane (per `policies/review-lanes.md`):
- full | light | light → full (escalated: <reason>) | light → full (orchestrator upgrade: <reason>)

Role model/venue (per `policies/role-models.md`) — orchestrated by <claude|codex>:
- Preflight: OK (<validated targets>) | N/A (every role native)
- Planner: model=<model> effort=<effort|default> venue=<native|claude|codex> <annotate "[fallback: <reason>]" only for a post-preflight runtime failure>
- Reviewer (plan review): model=<model> effort=<effort|default> venue=<native|claude|codex> | skipped (light lane) <same annotations>
- Coder: model=<model> effort=<effort|default> venue=<native|claude|codex> <same annotations>
- Critic (code review): model=<model> effort=<effort|default> venue=<native|claude|codex> <same annotations>

Role timing (per `policies/role-timeouts.md`):
- Planner: <duration>; first event <duration|unavailable>; longest idle <duration|unavailable>; <success|error|timeout(type)>
- Reviewer (plan review): <same> | skipped (light lane)
- Coder: <same>
- Critic (code review): <same>

Manual checks for user:
- <named check> | None

Ripple (per `policies/phase-ripple.md`):
- AUTO: <downstream phase file> — <one-line: what was pinned and how the file was updated> | None
- DECIDE: <downstream phase file> — <one-line: candidate ripple, why it needs human judgment> | None
<If no downstream drafted phase files exist, state "none — no downstream sketches".>

User demo (per `policies/user-demo-protocols.md`):
<If the approved plan carried a `User Demo:` block, paste it verbatim here, with the entry-point command on its own line so the user can copy it directly. If the plan declared `User Demo: N/A — <reason>`, restate that line.>

Remaining:
- <anything significant left incomplete, or "None">
```

Then report to the user:

- **🚨 Role disconnects (per [`policies/role-models.md`](../../../policies/role-models.md)):** for every role whose runtime call failed after a successful preflight (three-signal gate or timeout) so it ran native instead, add a 🚨 line stating what was configured, what actually ran, and why — e.g. `🚨 coder configured for opus but ran native (call timed out) — output was NOT produced by opus`. If every role ran on its resolved venue, omit this entirely. Preflight failures never reach Step 10 because they abort before phase state exists.
- Which phase was completed and which is next (`⬅️`).
- Files created/modified, grouped by surface.
- Build and gate status.
- Any Minor Corrections or Observations the reviewers noted that the user may want to track.
- Manual checks the user needs to perform that the orchestrator couldn't.

**Do not auto-commit.** The user drives commits, per [`policies/human-in-the-loop.md`](../../../policies/human-in-the-loop.md).

---

## Operating notes

- The four canonical role names (`phase-planner`, `plan-reviewer`, `phase-coder`, `code-critic`) are load-bearing. See [`policies/four-canonical-agents.md`](../../../policies/four-canonical-agents.md).
- The verdict header (`## Verdict: APPROVED` or `## Verdict: REVISE`) is parsed by string match. Mis-cased or rephrased verdicts break orchestration.
- Per-role model/venue ([`policies/role-models.md`](../../../policies/role-models.md)): `kickoff.yaml`'s human-editable `role_models` section (set directly or via `/roles`) resolves each of the four roles to separate model and effort fields plus an implied venue at Step 0a, scoped by which harness is orchestrating. Step 0b live-validates every non-native CLI/model/access target and aborts before phase mutation on any upstream failure. The shipped default routes reviewer + critic to the *other* harness (cross-vendor review — there is no separate on/off token) and leaves planner + coder native; a project may resolve any role anywhere. A role resolving to a CLI is invoked there with the resolved model/effort overrides (write-enabled for the coder), resuming the same session across the role's rounds. Orchestration and build gates always run on the session model — never pinnable. A later runtime failure after successful preflight may still fall back per-stage and surfaces a 🚨 in the Step 10 report. The recursion guard env var is `KICKOFF_DELEGATION_DEPTH` (a delegated role never re-delegates). Recipes and handoff hygiene: [`briefs/cross-agent-invocation.md`](../../../briefs/cross-agent-invocation.md).
- Per-role execution budgets ([`policies/role-timeouts.md`](../../../policies/role-timeouts.md)): Step 0c loads portable defaults from `kickoff.yaml`'s `role_timeouts` section. Every external initial/resume/rescue call runs through `bin/kickoff-config watch`; native calls use the same budgets through the harness wait mechanism. Raw telemetry is local under `.kickoff/`, and Step 10 records the human-readable timing summary.
- Review lanes ([`policies/review-lanes.md`](../../../policies/review-lanes.md)): a phase's `review_lane: light` frontmatter skips Step 4 for mechanical work. The code critic always runs in every lane, guards the lane, and can escalate a light phase back to full; the END block records the lane. Lane and venue are orthogonal.
- The ripple pass in Step 9a (sub-phase close) and Step 9b (major-phase close) is governed by [`policies/phase-ripple.md`](../../../policies/phase-ripple.md). AUTO ripples land in the same session; DECIDE ripples appear in the END block as named follow-ups.
- Cross-harness: this same skill drives both Claude Code and Codex. The Codex slash-command entry point lives at `.codex/prompts/kickoff.md` (file symlink to this file); Codex's native skill-discovery surface reaches it through `.agents/skills/kickoff` (directory symlink to the parent `.claude/skills/kickoff/`). Edit this canonical skill, not the wrappers.
- If your harness does not expose named subagents, perform the same role sequence locally by reading each `.claude/agents/<role>.md` directly and adopting that role's reading protocol and output format for the duration of the step.

## Local fallback

If the current platform does not expose named subagents, perform the same role sequence locally and follow the canonical role procedures in `.claude/agents/phase-planner.md`, `.claude/agents/plan-reviewer.md`, `.claude/agents/phase-coder.md`, and `.claude/agents/code-critic.md` directly. The agents' tool-stance and verdict format apply just the same.
