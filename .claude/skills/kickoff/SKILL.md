---
name: kickoff
description: >-
  Orchestrate a single phase of plan/ end-to-end: pick up the next phase,
  plan, review plan, implement, review code, build/test, update status
  markers in plan/INDEX.md, and log; route later test- or user-driven
  corrections by risk and size. Language- and surface-agnostic; the project's
  CLAUDE.md and phase file declare which build gates to run.
  Invoke as /kickoff in Claude Code or $kickoff in Codex (picks up the ⬅️
  phase); append "phase N" to target a specific phase.
last-reviewed: 2026-08-23
---

# Kickoff: Single-Phase Session

Orchestrate a full initial implementation of one phase under `plan/`, from
plan through working code, following the plan → plan-review → code →
code-review → build pipeline. Own candidate-bound authority, change, finding,
packet, and gate evidence throughout. Route later test- or user-driven
corrections proportionally instead of replaying that full pipeline by default.

This skill is language- and surface-agnostic. The project's `CLAUDE.md` declares the conventions; the phase file declares the deliverables; the planner picks the build gates; the orchestrator runs them.

## Current context

- Branch: `git branch --show-current`
- Phase markers: `grep -E '^\| \[Phase ' plan/INDEX.md 2>/dev/null || echo "(plan/INDEX.md missing)"`
- Recent log: `tail -20 LOG.md 2>/dev/null || echo "(no log)"`

## Parse arguments

Raw arguments: `!{ARGUMENTS}`

- If empty, Step 1 picks up the `⬅️` phase.
- If `phase N` or `phase N.M` (e.g., `phase 1`, `phase 1.3`), target that specific phase file `plan/phase-<id>.md`.
- If the arguments carry the token `one-shot` (e.g., `phase 2.1 one-shot`), the user is invoking the one-shot review lane for this cycle per [`policies/review-lanes.md`](../../../policies/review-lanes.md); Step 0 checks eligibility.
- If free text describes a concrete build/test failure or user-requested correction to an active or recently completed phase, treat it as a **follow-up revision** under [`policies/review-lanes.md`](../../../policies/review-lanes.md), not as a phase description.
- Otherwise, treat free text as a phase description and try to match it against a phase row in `plan/INDEX.md`. If nothing matches, ask the user which phase they mean rather than guess.

## Follow-up entry

A follow-up revision exists only after the affected implementation has received its initial code-critic pass. Inspect the diagnostic or user instruction and the likely change surface, then classify both risk and size per [`policies/review-lanes.md`](../../../policies/review-lanes.md):

- **Direct fix** (small and low risk): the orchestrator edits the localized code itself. Skip role resolution/preflight and Steps 3–6; validate through Steps 7–8.
- **Coder only** (low risk, but implementation delegation is useful): run Steps 0a–0c, invoke Step 5, skip Step 6, then validate through Steps 7–8.
- **Full cycle** (high risk or large/cross-cutting): run Steps 0a–0c and the normal coder → critic path in Steps 5–8. Re-run planning first only when the correction exposes a plan or architecture error.

For a delegated follow-up, use the concrete diagnostic or user instruction, the phase file, and the prior END block as the correction brief for Steps 5–6; do not depend on an ephemeral plan from an earlier session. If those sources do not determine the correction safely, classify it as high risk and re-run planning.

Do not turn an uncertain correction into a direct fix: uncertainty about behavior, blast radius, or validation makes it high risk. For a follow-up during an active phase, continue through the normal Steps 9–10 after validation. If the prior phase is already `✅`, skip Steps 2 and 9 and do not emit the normal Step 10 END block; preserve its status and historical END block, then append an `END (correction)` block and report the route and evidence per [`policies/log-discipline.md`](../../../policies/log-discipline.md). A concrete correction does not reopen the phase, while genuinely new scope belongs in a new phase.

Every route still initializes Step 1b evidence. For a direct fix, the
orchestrator writes the same exact Change Evidence JSON object the coder would
have reported and passes it to `capture-change --metadata`; direct authorship
does not bypass candidate identity, risk tags, selection rationale, or final
gate records.

## Workflow

### Operator-input parks (applies throughout)

Phase-level time awaiting required user input is not a role `wait` span and may
cross trace finalization or a machine reboot. Immediately before stopping for
an approval, decision, manual check, environment action, acceptance judgment,
or other required input, run:

```
$TELEMETRY_TOOL park-open --phase "$PHASE_ID" --reason <stable-reason-code>
```

Use only the enumerated reason codes shown by the CLI; never record the
question, response, prompt, repository content, or private data. Preserve the
returned park id. On the continuation that receives an answer satisfying the
wait, close it **before resuming phase work**:

```
$TELEMETRY_TOOL park-close --phase "$PHASE_ID" --park-id <park-id>
```

Repeated open/close calls are idempotent for the same identity; a conflicting,
missing, or multiply-open park fails closed. `phase-summary` reports each
interval and its union total. Same-boot intervals use exact monotonic time;
cross-boot intervals use visibly non-exact UTC calendar duration. Never turn an
open, malformed, or unknowable interval into zero.

### Step 0a: Resolve per-role model/venue

For an initial implementation or delegated follow-up, resolve once per session before role work begins, per [`policies/role-models.md`](../../../policies/role-models.md). This resolves a `(venue, model, effort)` for **each of the four roles** from `kickoff.yaml`'s harness-aware `role_models` section. A direct follow-up fix skips this step.

1. **Recursion guard.** If the env var `KICKOFF_DELEGATION_DEPTH` is set, this session is *itself* a delegated role invoked by an outer `kickoff` run; **every role runs native** and no further delegation happens. Skip the rest of Step 0a.
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

Before identifying a phase, changing a status marker, writing `LOG.md`, or invoking any role for an initial implementation or delegated follow-up, run:

```
./bin/kickoff-config preflight
```

This deterministic preflight resolves the same role pins as Step 0a and makes one live sentinel call for every unique non-native `(CLI, model, effort, access mode)` target. It uses the production credential scrubs, model/effort overrides, headless flags, stdin closure, and read-only versus write-enabled posture, but runs in an empty temporary working directory so it neither loads repository context nor touches the tree (the Codex probe adds `--skip-git-repo-check` solely because that directory is intentionally not a checkout). The active orchestrator needs no probe because the current session already proves it is authenticated; every role that will run through a subprocess is probed, including a deliberately configured same-vendor pin. Duplicate targets are probed once.

The preflight validates the full upstream path needed by the phase: CLI presence, usable authentication, model entitlement, network reachability, current flag compatibility, sandbox/access posture, a response within the 120-second hang guard, and an exact `KICKOFF_PREFLIGHT_OK` sentinel. A status command or credential-file check is insufficient because it does not prove a live model call under the production environment.

**Coder toolchain probe.** For every write-enabled target (the coder, when pinned), the preflight additionally asks the venue to run the repository's cheapest toolchain probe (`./bin/test --help`) from the checkout and reply with `KICKOFF_TOOLCHAIN_OK` or the failure text. This one does **not** abort: a venue whose sandbox cannot reach the toolchain (a uv cache outside its allowed paths, a missing system tool) is reported as `Role venue preflight: WARNING — coder venue cannot run the toolchain: <diagnostic>`, and the orchestrator records for Step 5 that the unverified-handoff guard will run the focused sequence natively on every coder return. Without this, the coder discovers the gap mid-phase, hands off unverified, and the critic spends its round on formatting.

**Any failure aborts `kickoff` immediately.** Report the failed target and the script's diagnostic, then stop. Do not fall back to native, identify or decompose the phase, change `plan/INDEX.md`, append a START/END block, or invoke an agent. After the user fixes authentication or the other upstream error, tell them to rerun `/kickoff` in Claude Code or `$kickoff` in Codex from a clean pre-phase state. If every role is native, or the recursion guard makes every role native, the script reports `N/A` / `skipped` and succeeds.

### Step 0c: Load per-role execution budgets

For an initial implementation or delegated follow-up, run `./bin/kickoff-config show timeouts` and retain the first-event timeout, each role's hard deadline and idle watchdog, plus its Claude-only `claude_max_turns` circuit breaker from `kickoff.yaml`'s `role_timeouts` section, per [`policies/role-timeouts.md`](../../../policies/role-timeouts.md). A direct follow-up fix skips this step. The three clocks apply to **every invocation or resumed revision round**; the turn value applies only when the delegated venue is Claude, because Codex and native subagents expose no equivalent flag. The shipped seed values are below; when a project has deliberately recalibrated its config, the validated config output governs:

- planner — 1,800 s hard / 600 s idle / 50 turns;
- reviewer — 1,800 s hard / 600 s idle / 50 turns;
- coder — 7,200 s hard / 1,200 s idle / 200 turns;
- critic — 2,700 s hard / 600 s idle / 50 turns;
- every role — first structured event within 120 s.

For every external CLI call, including resumes and the one permitted max-turn
rescue, invoke the production command through `./bin/kickoff-config watch`
with `--role`, resolved `--venue`, `--model`, `--effort`, phase id, and named
stdout/stderr/result artifacts. Pass Claude's extracted result path as
`--result-file`; pass Codex's `--output-last-message` path as
`--required-output-file`. The wrapper closes stdin, verifies routing flags,
truncates result paths, streams progress, terminates the process group on
first-event/idle/hard timeout, and appends local telemetry. It returns the
child status, 124 on timeout, 65 on unrecoverable protocol failure, or 66
(`completed-unverified-protocol`) when a successful child left a fresh
artifact but no complete terminal stream.

Exit 66 is not success. Preserve the artifact and verify the exact role shape,
the expected candidate id, and its structured change/finding evidence through
`bin/kickoff-evidence`. If all checks pass, continue without rerunning the
intelligence work and record `[protocol recovered: terminal stream
incomplete]` for Step 10. If any check fails, use the stage's normal native
fallback and record a 🚨 disconnect. Codex emits JSONL with `--json`; Claude
emits JSONL with `--output-format stream-json --verbose`. Preserve each role's
timing record for Step 10.

For native subagents, use the same role-specific hard and idle budgets through the harness's wait/status mechanism. Progress means a real agent event, status transition, or tool result; the orchestrator's own polling is not progress. If the harness cannot expose idle timing, enforce the hard deadline and record first-event/idle as `unavailable`. Keep the user informed at least every 60 seconds while waiting.

Run `./bin/kickoff-config show research` and retain the role authority and
originating-query budgets from `kickoff.yaml`. Planner and reviewer may search
and retrieve; coder and critic may retrieve plan/brief-identified resources and
same-host structural neighbors but may not originate searches. Installed MCP
servers and plugins remain available by default unless the project or phase
explicitly narrows them. Every dispatch receives the resolved directive from
`bin/kickoff-config`; do not hand-author a weaker prompt. See
[`policies/research-authority.md`](../../../policies/research-authority.md).

### Step 1: Identify the phase

Read `plan/INDEX.md` (the authoritative phase ledger) and locate the phase to work on. Status markers live in the `INDEX.md` phase table, not in the per-phase files (see [`policies/phase-status.md`](../../../policies/phase-status.md)).

- **No arguments**: find the row whose status is `⬅️` in the phase table. If
  none exists while a row is `🚧`, require an explicit phase id to resume that
  active work. If every row is `✅`, report that the project is complete. If
  incomplete work is idle with no `⬅️`, or more than one row is `⬅️`, stop
  on the invalid ledger rather than choosing through ambiguity.
- **`phase N` / `phase N.M`**: find the row whose link is `[Phase <id>](phase-<id>.md)`.
- **Free text**: resolve to a phase row or ask the user.

The lifecycle invariant is: every phase row has exactly one recognized status;
idle incomplete work has exactly one `⬅️`; active or complete work may have
zero; more than one is always invalid. `./bin/check-catalogs` enforces this
same state machine.

Then resolve the **review lane** per [`policies/review-lanes.md`](../../../policies/review-lanes.md): read `review_lane:` from the target phase file's frontmatter. Absent or `full` → **full** lane. `light` → **light** lane: Step 4 (plan review) will be skipped; the code critic still runs and guards the lane. You may upgrade a declared `light` to `full` when the phase's actual deliverables look non-mechanical — note the upgrade and why. Never downgrade `full` to `light` on your own.

**One-shot is invocation-only.** If the invocation line carries the `one-shot` token, check eligibility (binding-spec bar + isolation, per the policy): eligible → run the one-shot lane (Steps 3–4 skipped; coder → orchestrator vet → code critic → normal acceptance close; the mechanically derived role set drops `role.plan` and the `orchestration.planning` stage); ineligible → refuse with the stated reason and run the phase file's declared lane. A frontmatter `review_lane: one-shot` is invalid — refuse and ask. Escalation (a park, a write-set widening, a second gate failure, or the critic's `Escalate: full lane`) cannot continue in the same evidence run: finalize the one-shot run truthfully as paused, re-init a fresh full-lane run, carry open findings forward in the revision packet, and record `one-shot → full (escalated: <reason>)` in the END block.

Also resolve the **evidence lane**: read optional `evidence_lane:` frontmatter (absent or `full` → full apparatus; `light` → structural tests, the operator gate, and the mandatory seal at close, with role registration/span joins/stage envelopes validated-if-present). Refuse a `light` declaration whose deliverables touch an authority surface, irreversible or external state, or a deploy seam; you may upgrade `light` → `full`, never downgrade. Report both lanes in the opening report and END block.

Tell the user which phase you are picking up, the path to its file (`plan/phase-<id>.md`), the resolved review lane, and that gate-proved work will be committed and fast-forward-pushed at close (delivery is not acceptance) unless they restrict it now (`policies/human-in-the-loop.md`). Stating the delivery posture in the first minute is what makes a restriction cheap to give — it costs one sentence before any commit exists.

### Step 1a: Sub-phase decomposition (parent phases only — just-in-time, one at a time)

The parent `phase-N.md` was drafted at bootstrap (or by an earlier major-phase-close ripple — see Step 9b). Step 1a decides whether to decompose its sub-phases, not whether to draft the parent itself.

If the target is a **parent phase** (`phase-N.md`, not `phase-N.M.md`) and no `plan/phase-N.*.md` sub-phase files exist for it yet:

- If the phase's Deliverables list is small (≤ 3 distinct surfaces) and fits one focused session, proceed monolithically — skip to Step 2.
- If the phase is large or multi-surface, **decompose just-in-time, one sub-phase at a time**. Size the bite to the executing coder model's demonstrated coherence, not to a fixed calendar (see [`briefs/methodology.md`](../../../briefs/methodology.md) §6): when recent phases of the current size have been closing with first-cycle approvals and green gates, prefer fewer, larger sub-phases; split finer only when revision loops or build-gate fix cycles have been saying so.
  1. Invoke `phase-planner` for a one-shot decomposition of `phase-N.1` *only* (full Goal / Deliverables / Acceptance / brief refs, plus a `review_lane:` frontmatter assignment per [`policies/review-lanes.md`](../../../policies/review-lanes.md) eligibility — default `full`).
  2. Write `phase-N.1.md`. Update `plan/INDEX.md`'s phase table to add the new row and adjust the dependency graph.
  3. Mark the parent `🚧` and `phase-N.1` `⬅️`. Restart the `kickoff` skill against `phase-N.1`.
  4. **Do not draft `phase-N.2`, `phase-N.3`, etc. yet.** Their shape benefits from `phase-N.1`'s outcomes. Subsequent sub-phases land at sub-phase close (see Step 9a). See [`briefs/methodology.md`](../../../briefs/methodology.md) §6.

Surface the decomposition decision (or the choice to stay monolithic) to the user in the opening report.

(Major-phase JIT does *not* happen here — every major phase the brief surfaces was sketched at bootstrap per [`briefs/agentic-bootstrap.md`](../../../briefs/agentic-bootstrap.md) §8. If a sketched `phase-N.md` is missing when `kickoff` reaches Phase N, that is a bootstrap-completeness failure to surface to the user, not a Step 1a responsibility.)

### Step 1b: Start telemetry and initialize candidate-bound evidence

After target resolution and any decomposition, start exactly one repository
trace with `./bin/execution-telemetry start --scope-root . --scope engine
--scope-id engine --run-type kickoff --operation phase.<id>`. Retain the
returned trace id and root span id. Immediately open a `reconciliation` child
named `orchestration.setup`, attempt 1, before allocating the evidence
directory.

Allocate a **new** opaque run directory with `mktemp -d`; never reuse a path
from an earlier or interrupted run. Initialize it through
`./bin/kickoff-evidence init` per
[the orchestration-evidence policy](../../../policies/orchestration-evidence.md).
Pass the phase id, authority list, trace id, root span id, open setup span id,
resolved review lane, resolved evidence lane, and follow-up route. Authorities, in governing order, are
`plan/INDEX.md`; target and parent phase files; cited briefs; declared
dependencies; the immediately preceding completed phase; `CLAUDE.md`; and
every applicable policy. Use repo-relative paths with optional `::locator`
suffixes. Initialization failure aborts before Step 2.

Initialization pins `kickoff-evidence`, `kickoff-tree-id`,
`execution-telemetry`, `kickoff-config`, `kickoff.yaml`, and their runtime
libraries beneath `$RUN_DIR/tools/`. From that point use the pinned
`EVIDENCE_TOOL`, `TELEMETRY_TOOL`, and `WATCHER_TOOL` for every evidence,
role, gate, recovery, finalization, summary, and dashboard action.

The root owns sequential, non-overlapping `reconciliation` stages:
`orchestration.setup`, `orchestration.planning`,
`orchestration.implementation`, `orchestration.acceptance`, and
`orchestration.close`. Close one before opening the next and increment a
stage's attempt on re-entry. Role, wait, and gate spans may nest or overlap,
but aggregation assigns specific work first and counts only the stage's
exclusive remainder as orchestration. Never fabricate a missing span.

For a follow-up correction, create a fresh trace and evidence run against the
correction brief and current tree. Runtime state remains outside the repository;
only the finalized privacy projection enters `EXECUTION_LOG.jsonl`.

### Step 2: Flip marker and open the log

Update `plan/INDEX.md` so the target row's status cell is `🚧`. **Do not edit the target `plan/phase-<id>.md` file's frontmatter or body** — status is stored only in `INDEX.md` (see [`policies/phase-status.md`](../../../policies/phase-status.md)).

Append a START entry to `LOG.md`. Create `LOG.md` if it does not exist (with the header described in [`policies/log-discipline.md`](../../../policies/log-discipline.md)). Format:

```
## <YYYY-MM-DD HH:MM> — START
<Phase heading>

Execution trace: <trace-id>
Baseline: <commit id> — <baseline-dependent criteria> <only when such criteria exist>

Planned work:
- <deliverable 1>
- <deliverable 2>
- ...
```

Use the phase's "Deliverables" list from `plan/phase-<id>.md` verbatim (trimmed to the bullet text). If the phase has no Deliverables section, fall back to the phase's Goal paragraph rephrased as bullets. `Execution trace:` is the trace id opened in Step 1. Include the `Baseline:` line only when an acceptance criterion compares against prior state ("unchanged before and after"); record the commit id it compares against per `policies/acceptance-empirical.md` § Baseline-dependent criteria. On re-entering a paused phase, append `START (resumed)` rather than a bare START (`policies/log-discipline.md` § Multi-session phases).

Close `orchestration.setup` successfully and immediately open
`orchestration.planning`. Recompute the candidate through
`$EVIDENCE_TOOL current-candidate`; the status and START writes intentionally
changed it, so no role may receive the candidate printed by `init`.

### Step 3: Plan

Before every role attempt, atomically run
`$EVIDENCE_TOOL register-role-attempt` with its stable operation
(`role.plan`, `role.plan-review`, `role.implement`, or
`role.code-review`), attempt, role, harness, resolved model/effort, reason,
and a per-attempt `--output` file directly under `$RUN_DIR`. Never pass the
append-only `role-attempts.jsonl` ledger as a registration.

For an external venue, write the role prompt to a file and invoke
`$WATCHER_TOOL watch`. The watcher generates the complete Claude or Codex
command from routing metadata, including access stance, structured-output
schema, credential scrubs, recursion guard, artifact wiring, and timeouts.
Never hand-write the child command; use `$WATCHER_TOOL render-command` for
inspection. For a native venue, validate the registration, open the same
intelligence span, open its nested wait span only after dispatch acceptance,
then close both truthfully and record their ids with
`record-role-dispatch`. Rejected dispatches close intelligence as error 127
and create no wait. Every retry, resume, rescue, reexecution, or fallback gets
a new immutable registration and attempt number.

Every dispatch also records the candidate it opened against and the candidate
it returned at, and the pair **brackets the child's run**, so a tree that moved
under an in-flight role is visible at the seam instead of surfacing later as a
wholesale refused batch, and `accept-candidate-drift` — the only sanctioned
recovery for that movement (`policies/orchestration-evidence.md § Candidate
drift under an in-flight dispatch`) — has both sides to classify. **For an
external role you do nothing:** `$WATCHER_TOOL` captures the open candidate
immediately before it spawns the child and records the row only after the
child terminates. **For a native role**, and only then, run
`record-role-dispatch --state opened` (with `--dispatch-candidate` set to the
id `current-candidate` printed immediately before you dispatched) before
launching the role, and append the accepted or rejected terminal amendment
after the role has returned — not while it is running, or both candidates
describe the same instant and a mid-role write becomes invisible.

**Native venue** (planner unpinned, per Step 0a): delegate the planning stage to the `phase-planner` subagent (Claude Code) / the `phase-planner` agent (Codex), enforcing the planner budget from Step 0c. Pass it:

- The phase identifier (e.g., `Phase 1.3`) and heading.
- The full phase text from `plan/phase-<id>.md` (copy/paste, do not summarize).
- The evidence run directory and current candidate id.
- Nothing about the agent's own procedure — the role definition already covers the reading protocol and output format.

**Delegated venue** (per Step 0a): write a prompt that tells the
external agent to read `.claude/agents/phase-planner.md`, then invoke the
registered attempt through `$WATCHER_TOOL watch`. The planner is read-only.
Preserve its session id for revision rounds. A post-preflight runtime failure
may fall back to the native planner only after the failed attempt is closed
and recorded; surface the disconnect in Step 10.

Wait for the plan. Write the exact plan artifact into the run directory and
invoke `./bin/kickoff-evidence capture-plan --run-dir <run> --plan <artifact>`.
The returned plan hash is the identity reviewed in Step 4. A malformed planner
report or failed capture follows the planner stage's fallback rules; do not
send unbound plan text to review.

**Mechanical pre-review.** Before spending a review round, run
`./bin/check-plan-concreteness --plan <artifact>` (its own block; read the
refusal). It refuses a plan that cites an identifier occurring nowhere in the
tree and undeclared in the plan's `## Definitions Read` table, names a path
that does not exist and is not a declared new file, writes a command that
cannot run (missing script, unknown `--flag`, `<placeholder>`, pinned candidate
id), or defers a lookup to the coder. On refusal, re-run the planner with the
exact `ERROR` rows as feedback — a new registered attempt with reason
`revision`, not a review round and not a convergence signal — then re-capture
and re-check. Two consecutive refusals on the same rows park the phase for the
operator. Only a passing plan proceeds to Step 4.

### Step 4: Review the plan

**Light lane** (per Step 1's lane resolution): skip this step entirely. Record `Plan review: skipped (light lane)` for the END block and proceed to Step 5. Everything below applies to the full lane only.

**Native venue** (per Step 0a): delegate the review stage to the `plan-reviewer` agent. Pass it:

- The phase reference and heading.
- The full phase text from `plan/phase-<id>.md`.
- The full plan text from Step 3.
- The plan hash, current candidate id, and evidence run directory.
- On revision rounds, the prior finding ledger and generated plan-revision
  packet.

**Delegated venue** (the non-`default` model `reviewer` resolved to in Step 0a): run the role in that CLI per [`policies/role-models.md`](../../../policies/role-models.md). The shipped `kickoff.yaml` resolves reviewer to the *other* harness (cross-vendor review); a project may resolve it anywhere. Add the resolved model and effort flags to the recipe below and preserve them on resume; everything else is identical. A later runtime failure despite the successful preflight falls back to native with a 🚨 in Step 10.

1. Write the full phase text and the full plan text to temp files (e.g., `/tmp/kickoff-phase-<id>.md`, `/tmp/kickoff-plan-<id>.md`). Do not include the planner's own confidence statements or open-questions commentary beyond the plan text itself.
2. Write a prompt file instructing the external agent to: read `.claude/agents/plan-reviewer.md` and adopt that role for this review; review the plan in `<plan temp file>` against the phase text in `<phase temp file>`; use the supplied plan hash, candidate id, evidence run directory, and revision packet/ledger when present; assume the planner was careful but missed something; emit the exact `## Finding Evidence` JSON block; and end with the exact verdict header (`## Verdict: APPROVED` or `## Verdict: REVISE`). Note that `AskUserQuestion` is unavailable in this venue — an unresolved owner decision is recorded as a `blocked-owner` finding whose `required_outcome` states the exact question and its defensible answers, and the verdict is `REVISE`; the orchestrator relays it (below). **Scope the reading mandate** — the reviewer has a read-only checkout and its own Read/Grep, so name the handful of load-bearing files to read (the sources the plan actually reshapes), not "read all the sources the plan touches." An unbounded "read everything" instruction on a large multi-file phase can exhaust the external reviewer's own context (and trip its internal compaction, which can fail on a network stall) before it reaches a verdict — see [`briefs/cross-agent-invocation.md`](../../../briefs/cross-agent-invocation.md) §4.
3. Invoke the registered attempt through `$WATCHER_TOOL watch`.
   It generates the read-only venue command and schema-constrains the complete
   artifact from the same finding vocabularies the evidence validator uses.
   Preserve the session id. Exit 66 remains recoverable only after exact
   role-shape, artifact, candidate, and finding validation.
4. Gate on ordinary three-signal success, or handle exit 66 through Step 0c's
   explicit recovery. In either case, write the exact reviewer response to a
   fresh artifact, require exactly one `## Verdict:` header, and run
   `./bin/kickoff-evidence ingest-findings --run-dir <run> --kind plan
   --candidate <current-candidate-id> --review-span-id <reviewer-intelligence-span-id>
   --artifact <review-artifact>`. **`--review-span-id` is required** — the
   convergence metrics attach to that span, and a finalized trace cannot be
   repaired retroactively, so `timing-summary` refuses for the whole run until
   the pass is measured. An omission is recoverable rather than terminal:
   `validate` refuses an accepted, successful review dispatch whose span lacks
   metrics **unconditionally** — not only under `--require-final` — so the gap
   surfaces while a re-ingest still costs one command; and where the batch was
   structurally uningestable, `kickoff-evidence attach-derived-metrics` records
   an overlay that `validate` recomputes from the run's artifacts and honors
   either side of finalization. Neither is a reason to omit the flag:
   re-ingesting an earlier artifact to satisfy a validator drives
   `verified → open` and reopens resolved findings, which is why the flag is
   still required here. Failure
   of role shape, finding schema/transition, or candidate identity triggers
   native fallback. Exception before falling back:
   a Claude `error_max_turns` result may resume once with the concise
   “conclude now” instruction and re-gate. After ingesting the response, mark
   the plan just reviewed through `mark-plan-reviewed --plan <plan-artifact>
   --expected-plan <plan-hash>`.

**If `APPROVED`**: proceed to Step 5. Show the user a brief summary plus any Minor Corrections (do not wait for explicit approval unless the user asked to review plans themselves).

**If `REVISE` and any finding is `blocked-owner`**: do not re-run the
planner on that finding — it is a question the planner cannot answer. Open an
operator-input park, put the finding's `required_outcome` to the operator in
the `plain` register (natively via `AskUserQuestion`; while unattended, the
parked artifact per the AFK rules), and on the answer record the ruling in the
phase file or the owning brief, transition the finding `blocked-owner → open`
with the ruling in `disposition`, and re-run the planner with it. Findings that
are not `blocked-owner` proceed in the same round as below.

**If `REVISE`**: re-run `phase-planner` with the stable finding ledger and
reviewer's narrative feedback. Capture the updated plan, then run
`capture-plan` and generate a `--kind plan` revision packet. Re-review in the
same venue with the packet, full updated plan, and ledger — external session
resume is preferred; a fresh call receives all three. Use the venue's resume
recipe, not its initial-call flags. Run the mechanical
pre-review on every recaptured plan. Continue only while at least one blocking
finding advances and no equal-or-worse finding reopens; an
`evidence-substituted` ingest refusal means the reviewer re-aimed a prior
finding — return the refusal to the reviewer for a re-emission with a new id
before judging convergence. Rebase to a complete
review when the packet requires it. Escalate on recurrence, oscillation,
authority disagreement, or two rounds without lower severity or uncertainty.
The 10-cycle runaway backstop still applies.

### Step 5: Implement

**Native venue** (coder unpinned, per Step 0a): delegate implementation to the `phase-coder` agent. Pass it:

- The approved plan (full text, including any Minor Corrections from the plan-reviewer appended as a note).
- The evidence run directory and current candidate id.
- On revision rounds, the stable finding ledger and generated code-revision
  packet.

**Pinned venue** (any non-`default` model, per Step 0a): run the coder in that model's implied CLI per [`policies/role-models.md`](../../../policies/role-models.md), using the **write-enabled** recipe (the coder writes — unlike every read-only reviewer role):

1. Instruct the external agent to read `.claude/agents/phase-coder.md` and
   adopt that role; pass the approved plan, evidence run directory, current
   candidate id, and any revision packet/finding ledger via temp files.
2. Invoke the registered attempt through `$WATCHER_TOOL watch`.
   The generated coder command is the sole external workspace-write recipe;
   serialization preserves the single-writer invariant, and its schema/access
   flags cannot drift from the routing metadata.
3. **Single-writer guarantee:** `kickoff` is sequential, so during this stage no native writer touches the tree — the pinned coder owns it exclusively (build gates run afterward, Step 7). This satisfies "serialize or isolate — never two writers on one tree" without a worktree.
4. Capture the session id (codex `--json` `thread_id`; claude stream `session_id`) — the coder resumes across code-revision and build-fix rounds. Read the report (file list, Build Status, Manual Checks) from the watcher result artifact / codex `--output-last-message`; the file writes have already landed in the tree.
5. **Fallback:** a later three-signal gate failure or timeout despite the successful preflight → fall back to the native `phase-coder`, record `[fallback: <reason>]`, and raise the 🚨 disconnect for Step 10. Do not attempt to repair the sandbox mid-run.

Wait for the coder. Write its exact report to a fresh artifact. Require the
normal report shape plus exactly one `### Change Evidence` JSON block, then
run:

```
./bin/kickoff-evidence capture-change --run-dir <run> --metadata-artifact <coder-artifact>
```

This binds the changed paths, declared risks, selected tests, selection reason,
intentionally unchanged neighbors, rebase reasons, falsifiers, and the coder's
`gate_status` to the resulting candidate. Exit 66 is recoverable only if this
validation and the report-shape gate both pass. Collect the file list, focused
Build Status, Finding Resolution, and Manual Checks. The coder does not run or
claim the acceptance-close sequence.

**Unverified-handoff guard.** Read `gate_status` from `change.json`. When
`focused` is `not-run` (the venue could not reach the toolchain) or `red`, run
the approved plan's Iteration and Revision Close sequence natively, then
`./bin/check format` and `./bin/check lint` — each command in its own block,
its refusal read — and record each as a gate against the candidate. A red
result goes back to the coder as a revision attempt with the diagnostics
(reason `revision`); the critic is never dispatched on code whose focused
gate has not run green somewhere. When a role venue was flagged at Step 0b as
unable to run the toolchain, expect this branch on every coder return.

**Delivery pre-review.** Run
`./bin/check-plan-delivery --plan <approved plan artifact> --root . --deviations <coder artifact>`
in its own block. `ERROR` rows — planned files, introduced identifiers, or
named tests the tree does not hold and the report does not declare as
deviations — go back to the coder as a revision attempt, not to the critic.
`DEVIATION` rows are passed to the critic with the file list.

**Push-back.** A Finding Resolution line of the form
`<id> — rejected-with-evidence: <observation>` is ingested as that transition
(`--no-review-span '<coder refutation>'`) and the refutation is quoted to the
critic on the next round, which accepts it or reopens with counter-evidence.

Before dispatching the coder, close `orchestration.planning` and open
`orchestration.implementation`. On any later return from acceptance to
implementation, close the failed acceptance stage truthfully and increment
both stage attempts.

### Step 6: Review code

**Native venue** (per Step 0a): delegate code review to the `code-critic` agent. Pass it:

- The approved plan (full text).
- Any Minor Corrections the plan-reviewer issued.
- The list of files the coder created or modified.
- The reviewed/current candidate ids, change manifest, and evidence run
  directory.
- On revision rounds, the prior finding ledger and generated code-revision
  packet.
- **Light lane only:** the lane declaration, with the instruction to additionally judge lane fit per [`policies/review-lanes.md`](../../../policies/review-lanes.md) — did the diff stay within mechanical scope?
- Any `DEVIATION` rows from the delivery pre-review, any coder refutations
  (`rejected-with-evidence`) with their evidence, and the native observation
  for any prior finding the critic marked `SUSPECTED` (run the probe it named
  before dispatching; attach the output verbatim).

**Delegated venue** (the non-`default` model `critic` resolved to in Step 0a): run the role in that model's implied CLI per [`policies/role-models.md`](../../../policies/role-models.md). The shipped `kickoff.yaml` resolves critic to the *other* harness (cross-vendor review). Add the resolved model and effort flags and preserve them on resume; a later runtime failure despite the successful preflight falls back with a 🚨 in Step 10.

1. Write the approved plan and the **changed-file list** to temp files, and capture `git diff --stat` (what changed and where). The external reviewer runs against a **read-only checkout** with its own Read/Grep, so hand it a map, not a payload: it pulls the specific files it wants. Inline a full diff into a temp file only when the change is small enough to read whole; for a large change the file list + `git diff --stat` *is* the handoff. **Never pre-materialize a monolithic diff and reject the venue because `git diff | wc -c` is large** — an on-disk artifact is not tokens-in-the-window; a reviewer with Read/Grep reads surgically, and delegation is discarded only on the three-signal gate below, never on a pre-computed size estimate. **Flag machine-regenerated blobs** in the file list (fixtures, snapshot JSON, lockfiles, golden files) as "spot-check structure, don't read line-by-line" — they dominate byte count but carry almost no review surface. **Redact the coder's self-assessment** — no Build Status block, no Manual Checks narrative, no "tests pass" framing. Cold artifacts review 3–4× deeper (see [`briefs/cross-agent-invocation.md`](../../../briefs/cross-agent-invocation.md) §§1, 4).
2. Write a prompt file instructing the external agent to: read
   `.claude/agents/code-critic.md` and adopt that role; review the changed
   files against the plan using the supplied candidate ids, change manifest,
   evidence run directory, and revision packet/ledger when present; assume the
   implementer was careful but missed something; emit exactly one
   `## Finding Evidence` JSON block; and end with the exact verdict header.
3. Invoke the registered attempt through `$WATCHER_TOOL watch`.
   It generates the read-only venue command and schema-constrains the code
   review artifact. Preserve the session id and exact intelligence span id for
   finding ingestion and convergence reporting.
4. Gate on ordinary three-signal success, or handle exit 66 through Step 0c.
   Write the exact response to a fresh artifact, require exactly one verdict,
   and run `./bin/kickoff-evidence ingest-findings --run-dir <run> --kind code
   --candidate <current-candidate-id> --review-span-id <critic-intelligence-span-id>
   --artifact <critic-artifact>` against
   its `## Finding Evidence` block. **`--review-span-id` is required**, for the
   reason given in Step 4. Failure of role shape, evidence
   schema/transition, or candidate identity triggers native fallback. The one
   `error_max_turns` conclude-now rescue remains available. After ingesting
   the response, mark the candidate just reviewed through
   `bin/kickoff-evidence mark-reviewed --expected-candidate <id>`.

**If `APPROVED`**: proceed to Step 7.

**If `REVISE`**: re-run `phase-coder` with the stable finding ledger and
critic narrative, instructing it to include a **Failure Analysis** — why the
previous attempt produced these findings (root cause, not restatement) — in
its report and as the `failure_analysis` key of its Change Evidence. Validate
its new Change Evidence, then generate a `--kind code` revision packet and
re-review in the same venue (resume preferred); the packet carries the failure
analysis forward so the critic reviews the fix against the coder's own theory
of the failure. Continue only while a blocking finding advances and no
equal-or-worse finding reopens. When the change manifest requires rebasing,
run a complete critique rather than a delta-only pass. Escalate on recurrence,
oscillation, authority disagreement, or two rounds without reduced severity or
uncertainty. The 10-cycle runaway backstop still applies.

**If any code finding is `blocked-owner`** — the critic asked an owner
question (an adversary or authorization no authority names): park it to the
operator exactly as Step 4 does for a plan finding, and do not dispatch the
coder on it; the remaining findings proceed in the same round.

**If `REVISE` opens with `Escalate: full lane — <reason>`** (light lane only): the work exceeded mechanical scope. Run the skipped Step 4 plan review now, against the plan as-built (same venue rules), route its outcome through the normal revision loops, and finish the phase in the full lane. Record `light → full (escalated: <reason>)` for the END block. The lane escalation itself is not a stall signal and does not count toward the runaway backstop; the critic's other Required Changes do feed the convergence judgment.

### Step 7: Candidate-bound implementation gate

After code-critic approval (or after an eligible direct/coder-only follow-up),
close `orchestration.implementation` and open `orchestration.acceptance`.
capture the approved candidate id with `./bin/kickoff-tree-id`. Run the plan's
complete **Acceptance Close** sequence in the orchestrator context: first
every mechanically executable phase-specific check identified in Step 8, then
the repository's authoritative full gate last. This is the complete
candidate-bound implementation sequence; it proves the unchanged implementation
candidate before close bookkeeping changes the tree. The coder's focused checks
are not repeated merely as ceremony unless the plan includes them in acceptance.

For every command, invoke `$EVIDENCE_TOOL run-gate` with the approved candidate
id, exact argv, selection reason, attempt, optional diagnostic artifact, and
`--final` for implementation-gate commands. This boundary records before/after
candidate identity, preserves complete diagnostics and child exit status,
counts warnings, and opens the exact observed gate span. It rejects drift.
After the sequence, run the pinned `kickoff-tree-id` again and require the same
id; a gate that mutated the candidate fails.

Treat human wall-clock efficiency as an ambient priority throughout the run,
not as a fixed timeout or telemetry program. Notice when a gate, build, index,
generator, migration, repeated setup step, or other operation materially
dominates the work. When a substantial reduction appears available through a
clear, low-risk mechanism, make one bounded assessment before blindly
repeating the cost: focused selection during iteration, invariant setup paid
once, safe isolation and parallel execution of genuinely independent units,
or reuse backed by complete input identity. Use an existing safe acceleration
when available. If a permanent improvement expands the phase, surface it once
and continue; do not pursue the tangent. Do not chase marginal savings, invent
numeric thresholds, collect purposeless timing data, or weaken correctness,
coverage, determinism, review independence, diagnostics, failure propagation,
candidate binding, or either close gate.

Every methodology-following repository owns the cwd- and symlink-independent atomic
interface defined by
[`policies/build-gates.md`](../../../policies/build-gates.md). For the
**Agentic Coding Starter Template itself**, the authoritative final command is:

```
./bin/check all
```

`bin/setup`, `bin/test`, `bin/check`, and `bin/python` plus the runtime pin,
manifest, and lockfile form this repository's atomic toolchain contract.
`bin/check test` delegates to `bin/test`; the full gate includes root
methodology tests and policy checks and preserves failing child statuses. A
project derived via `stamp` keeps the universal setup/test/check interface
while adapting it to that project's real language and version choices. The
planner may add project-specific focused checks or smokes before the full gate.
When `bin/test-governance` and `tests/proof-estate.yaml` exist and validate,
prefer `./bin/test --vital` for the standing fast set or
`./bin/test --changed-from <ref>` for candidate impact; preserve the manager's
selection reason in evidence. A full fallback is the correct result for
invalid or unmapped selection. These lanes are iteration aids only and never
replace either `./bin/check all` close gate. The planner must not bypass an
existing repository test entry point or replace the full gate with a copied raw
command list.

If any implementation gate fails:

1. Classify the failure source:
   - **Code error** — syntax, type mismatch, missing import, wrong signature, or failing test assertion.
   - **Plan error** — wrong file path, missing module, or architectural mismatch.
   - **Environment error** — missing toolchain, system dependency, or credential. Report this to the user immediately; do not retry.
2. For a code error, classify the correction's risk and size per [`policies/review-lanes.md`](../../../policies/review-lanes.md):
   - **Direct fix** (small and low risk) → the orchestrator applies the localized correction.
   - **Coder only** (low risk, but delegation is useful) → re-run `phase-coder` with the error output and plan.
   - **Full cycle** (high risk or large/cross-cutting) → re-run `phase-coder`, then `code-critic` under the Step 6 venue rules.
   A plan error is automatically a full-cycle correction: re-run `phase-planner`, then `phase-coder`, then `code-critic`.
3. Re-run the failing check first through the iteration/revision-close ladder.
   If a correction changes the candidate, prior final-gate evidence is
   invalid. Route any required critique, then run the complete
   candidate-bound implementation sequence again against the new approved candidate.
4. Do not invoke `code-critic` after a successful direct or coder-only correction merely as ceremony. Do invoke it if the correction grows beyond its classification, exposes a design question, lacks convincing validation, or otherwise crosses the full-cycle threshold.
5. A direct or coder-only attempt gets one pass. If it fails validation or trades one break for another, upgrade to the full cycle. Once in the full cycle, keep iterating only while the gate and review findings are **converging**. Escalate on recurrence or oscillation; the 10-cycle runaway backstop in [`policies/four-canonical-agents.md`](../../../policies/four-canonical-agents.md) applies to that full loop.

### Step 8: Reconcile phase-specific acceptance

Each phase declares its own empirical acceptance checks under `Acceptance` in `plan/phase-<id>.md`. The orchestrator runs whichever of those checks are mechanically executable (shell commands, smoke scripts, curl probes, deterministic comparisons) and reports the rest as **manual checks** for the user.

Step 7 must already have included every mechanical check before its full
gate. Here, reconcile each criterion against the gate ledger and classify the
rest as manual. Do not rerun a recorded check. If this reconciliation discovers
an omitted mechanical check, the implementation gate was incomplete: run the
missing check, then rerun the authoritative full gate against the same
candidate and record both. Reconfirm candidate identity afterward. A failed
acceptance gate or candidate mutation routes through Step 7's proportional
follow-up classification and invalidation loop.

Per [`policies/acceptance-empirical.md`](../../../policies/acceptance-empirical.md), every acceptance criterion is either executable or named manual. Treat ambiguous criteria as manual and flag them in the END block.

**This classification now gates delivery**
([`policies/human-in-the-loop.md`](../../../policies/human-in-the-loop.md)), so
type each criterion deliberately rather than by convenience. A criterion counts
as objective only if it is executable, was independently reviewed, was proved by
the complete gate, and is bound to the exact candidate; a manual, perceptual,
product, custody, or owner-only criterion parks no matter how green the gate is,
and so does an unrun `User Demo:` protocol. Write both halves into the END
block's `Acceptance:` field. A phase delivers on its **gates**, not on its
parked half: an open manual, perceptual, product, or custody criterion does not
hold the commit, and the END block says plainly that it is still the user's.
Misclassifying a subjective criterion as objective is the one error that would
let a phase claim evidence that does not exist; when in doubt, park it.

### Step 8b: Finalize exact execution evidence

Run `$EVIDENCE_TOOL validate --run-dir <run> --require-final
--required-final-command "./bin/check all"` and require success. Prepare the
acceptance reconciliation and downstream ripple decisions while the trace is
still open. Then close `orchestration.acceptance`, open
`orchestration.close`, complete close preparation, close that stage, and close
the root with its truthful outcome.

Run `$TELEMETRY_TOOL finalize`, followed by
`$EVIDENCE_TOOL timing-summary` in both JSON and text formats. Timing validation
rejects missing, overlapping, unknown, out-of-order, or unregistered
stage/role/gate joins, and any accepted review pass without exact finding
convergence counts. Only finalized evidence and successful summaries authorize
the tracked close writes in Steps 9–11. They do not authorize reporting
completion until the post-bookkeeping handoff gate in Step 12 passes. An
interrupted or failed run closes what can be closed truthfully;
unexpected abandonment may use same-boot `recover`, but recovery never
fabricates cross-boot duration or success.

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

If the closed sub-phase reveals that the parent's Deliverables list needs revision (new deliverable surfaced, an existing one no longer applies), surface this to the user explicitly in Step 10's report rather than silently rewriting the parent. The parent edit is the user's decision.

This step implements just-in-time, one-at-a-time sub-phase decomposition per [`briefs/methodology.md`](../../../briefs/methodology.md) §6 — `phase-N.(M+1)` is drafted *with* `phase-N.M`'s outcomes in hand, not in advance.

**Then run the ripple sub-step** before proceeding to Step 9c. This applies whether the parent is still `🚧` (a new sub-phase was drafted in 1–3 above) or just rolled up to `✅` (Step 9b took over). The ripple sub-step exists per [`policies/phase-ripple.md`](../../../policies/phase-ripple.md):

1. Read the closing sub-phase's `LOG.md` END block, the plan-reviewer's Observations, and the code-critic's verdict body.
2. Identify candidate ripples: pinned values, renamed paths, added brief refs, tightened Acceptance criteria, surfaced concerns addressed to a later phase by name.
3. For each candidate, walk the downstream drafted phase files — siblings (`phase-N.(M+1)`, `phase-N.(M+2)`, …, just-drafted or already drafted) plus downstream major phases (`phase-(N+1).md`, `phase-(N+2).md`, …, sketched at bootstrap). Classify each potential edit:
   - **AUTO** (mechanical, one correct shape): apply the edit now. If the edit is more than one line (e.g., reshaping an Acceptance section to incorporate a now-pinned value), invoke `phase-planner` with the downstream file and the ripple description; otherwise edit directly.
   - **DECIDE** (judgment-bearing): do *not* edit. Capture the item for the END block.
4. AUTO edits land before Step 10 writes the END block; the END block lists every AUTO ripple applied and every DECIDE ripple surfaced.
   Note ripple's boundary: it propagates *content* into downstream `plan/` files. Durable *process* learnings are not ripples — they belong to Step 9c's lessons harvest.

If no downstream drafted phase files exist (e.g., this is the project's only phase, or all later phases are already ✅), the ripple sub-step is a no-op — note `none — no downstream sketches` in the END block.

### Step 9b: Major-phase close — ripple and advance ⬅️ (major-phase close only)

Runs when a major phase's row was just flipped to `✅` — either by Step 9.3 directly (the closed phase was a monolithic major phase) or by Step 9a's parent-rollup branch (the closed phase was the last sub-phase under its parent).

1. **Ripple pass** against the next drafted major phase (`phase-(N+1).md`) and any subsequent sketched phases. Procedure mirrors Step 9a's ripple sub-step (read END block + verdict bodies; classify each candidate AUTO/DECIDE; apply AUTO; capture DECIDE for the END block). The major-phase ripple is more likely to touch Goal and Deliverables (lower-fidelity sketches have more headroom) and Acceptance (sketched criteria need tightening once the upstream phase pins them).
2. **Advance `⬅️`.** Find the next `⏳` row in the dependency graph order (honoring parallel opportunities). Change it to `⬅️`. At most one row is `⬅️`; when no downstream phase exists, zero is the valid completed state.
3. **Sketched-phase completeness check.** If the new `⬅️` row points at a `phase-N.md` that doesn't exist as a file (only a row in INDEX.md), this is a bootstrap-completeness failure — flag in the END block. Do not auto-draft it; per [`briefs/agentic-bootstrap.md`](../../../briefs/agentic-bootstrap.md) §8, every major phase the brief surfaces should have been sketched at bootstrap.

If no downstream major phase exists (project complete), Step 9b's ripple is a no-op and `⬅️` advances to nothing — the project is done. Surface this to the user in the report.

### Step 9c: Harvest lessons (every close)

Runs on **every** phase close — sub-phase or major — after the ripple pass and before Step 10, per [`policies/lessons.md`](../../../policies/lessons.md). This is the capture stage of the improvement flywheel: the question is mandatory; "no lessons" is a permitted, recorded answer.

1. **Gather the sensor feed.** Re-read the close-out artifacts the ripple pass already collected (END-adjacent material, the plan-reviewer's and code-critic's verdict bodies) plus: every role's **Process Observations** output (planner, reviewer, coder, critic), the coder's **Failure Analysis** from any revision rounds, wall-clock observations, and any `user-actions` dispositions filed during the phase.
2. **Distill candidate lessons.** A candidate lesson is a specific, generalizable process learning — friction or ambiguity in a brief, policy, plan, skill, or tool that a future phase (or a future repo) should not re-derive. Discard one-off situational notes; keep what would change behavior next time.
3. **File or recur.** For each candidate, check `lessons/` and `lessons-archived/` for an existing entry stating the same lesson. Append an occurrence (`{date, ref}` — use the phase id) to an existing entry, or write a new `lessons/<slug>.md` with `status: candidate` and a scope classification (`local` — binds only this project; `methodology` — generalizes to the template and is an upstream candidate for `learn`). Follow the slug recipe and collision check in the policy.
4. **Validate and tally.** Run `./bin/lessons validate` (must pass — fix any schema error now), then `./bin/lessons candidates`. Carry every graduation-ready lesson (≥3 occurrences) forward to the END block as a graduation DECIDE item.
5. **Surface the telemetry recommendation.** Run `./bin/kickoff-config recommend-timeouts`. Summarize per-target output for the END block: the recommendation when a target has crossed the sample threshold, otherwise `insufficient samples (<n>/<minimum>)`. Never edit `kickoff.yaml` from this output — recalibration is a human decision per [`policies/role-timeouts.md`](../../../policies/role-timeouts.md).

**Hard boundary:** filing and occurrence-appending in `lessons/` are the *only* writes this step performs. Codifying a lesson — editing `CLAUDE.md`, `policies/`, `briefs/`, a skill, or an agent definition because of it — requires the user's explicit ratification of a surfaced DECIDE item. Never apply a graduation autonomously, and never rewrite rule documents wholesale from session memory.

### Step 10: Close the log and report

Read the validated evidence and finalized timing summaries directly to compute
the block below; never substitute remembered counts or reassuring defaults
when a record is absent. Run `$TELEMETRY_TOOL phase-summary --phase
"$PHASE_ID"` and require every operator-input park to be closed before a
completion END block. Every material count carries the exact command or
deterministic procedure that produced it; a relayed number is remeasured or
attributed plainly as unverified, per
[`policies/verification-discipline.md`](../../../policies/verification-discipline.md).

The END block and the report that accompanies it are addressed to the
operator, so both are composed in the [`plain`](../../../.claude/skills/plain/SKILL.md) register: lead with what is
true now and what it means, name every parked criterion the operator still
owns, and keep ids, paths, and stage mechanics available on request rather
than ambient. Identifiers the operator must act on are given exactly.

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
- Handoff gate: runs after this tracked END block; completion is contingent on
  the ignored receipt from the final bare `./bin/check all`
- ...

Review lane (per `policies/review-lanes.md`):
- full | light | one-shot | light → full (escalated: <reason>) | light → full (orchestrator upgrade: <reason>) | one-shot → full (escalated: <reason>) | one-shot refused (<reason>) → <declared lane>

Evidence lane (per `policies/review-lanes.md`):
- full | light | light → full (orchestrator upgrade: <reason>) | light refused (<trigger>) → full

Follow-up route (per `policies/review-lanes.md`):
- N/A (initial implementation) | direct fix — <risk/size reason> | coder only — <risk/size reason> | full cycle — <risk/size reason>

Role model/venue (per `policies/role-models.md`) — orchestrated by <claude|codex>:
- Preflight: OK (<validated targets>) | N/A (every role native)
- Planner: model=<model> effort=<effort|default> venue=<native|claude|codex> <annotate "[fallback: <reason>]" only for a post-preflight runtime failure>
- Reviewer (plan review): model=<model> effort=<effort|default> venue=<native|claude|codex> | skipped (light lane) <same annotations>
- Coder: model=<model> effort=<effort|default> venue=<native|claude|codex> <same annotations>
- Critic (code review): model=<model> effort=<effort|default> venue=<native|claude|codex> <same annotations>
<Annotate any exit-66 artifact accepted after explicit validation as
"[protocol recovered: terminal stream incomplete]"; this is not a fallback.>

Role timing (per `policies/role-timeouts.md`):
- Planner: <duration>; first event <duration|unavailable>; longest idle <duration|unavailable>; <success|error|timeout(type)>
- Reviewer (plan review): <same> | skipped (light lane)
- Coder: <same>
- Critic (code review): <same>

Execution timing (per `policies/execution-telemetry.md`):
- Active makespan: <exact duration>; calendar window: <exact duration>
- Summed measured work: <duration>; peak concurrency: <n>
- Exclusive work: Planning=<duration>; Plan Review=<duration>; Implementation=<duration>; Code Review=<duration>; Automated Checks=<duration>; Reconciliation=<duration>
- Failed work: <duration>; retry work: <duration>
- Orchestration / Unmeasured: <duration>; largest measured gaps: <summary|none>
- Awaiting user input:
  - <opened UTC> → <closed UTC|open>: <duration|unavailable> (<reason>; exact monotonic | non-exact calendar cross-boot | unavailable)
  - Total: <union duration|unavailable> (<exact monotonic union | non-exact calendar union | incomplete>)
- Timing validation: exact monotonic nanoseconds, overlap-safe unions, trace joins <OK|failed>

Candidate-bound evidence (per `policies/orchestration-evidence.md`):
- Candidate: initial=<id> approved=<id> final=<id>
- Revision packets: <count>; <total bytes>; source hashes recorded
- Findings: open=<n> addressed=<n> verified=<n> closed=<n> blocked=<n>; reopened=<n>; missed-in-full-pass=<n>
- Gates: focused=<n> implementation-final=<n>; all recorded against approved implementation candidate=<yes|no>
- Evidence validation: `bin/kickoff-evidence validate --require-final` <OK|failed>

Wall-clock observations:
- <material operation; substantial safe improvement used or surfaced; why guarantees were preserved> | None

Acceptance (per `policies/human-in-the-loop.md`):
- Objective (independently reviewed, gate-proved, candidate-bound): <named criteria> | None
- Parked for the user: <named manual, perceptual, product, or custody criteria, and the `User Demo:` protocol when unrun> | None

Delivery:
- default — commit + fast-forward push after the handoff gate | restricted: <user's words, verbatim> | parked: <reason>

Ripple (per `policies/phase-ripple.md`):
- AUTO: <downstream phase file> — <one-line: what was pinned and how the file was updated> | None
- DECIDE: <downstream phase file> — <one-line: candidate ripple, why it needs human judgment> | None
<If no downstream drafted phase files exist, state "none — no downstream sketches".>

Lessons (per `policies/lessons.md`):
- filed: <slug> — <one-line lesson, scope> | none
- occurrences added: <slug> (<n> total) — <ref> | none
- graduation DECIDE: <slug> → <proposed_surface> — <one-line why it is ready> | none
- recalibration: <role/venue target — recommended hard/idle values> | insufficient samples (<n>/<minimum>)

User demo (per `policies/user-demo-protocols.md`):
<If the approved plan carried a `User Demo:` block, paste it verbatim here, with the entry-point command on its own line so the user can copy it directly. If the plan declared `User Demo: N/A — <reason>`, restate that line.>

Remaining:
- <anything significant left incomplete, or "None">
```

### Step 10a: User testing protocol

Every phase that ships user-observable behavior — a running service, a CLI tool, a new tool surface, a new artifact landing where the user can see it — produces a structured **test protocol** appended to the user-facing report (Step 11). The protocol is the bridge between "the orchestrator says this is done" and "the user has satisfied themselves it works." It is the deeper sibling of the `User Demo:` block from [`policies/user-demo-protocols.md`](../../../policies/user-demo-protocols.md): the policy declares *what* to demo at plan time; this step ships the structured testing layout at close time. It is not optional except for purely internal phases (e.g., a refactor that ships nothing externally observable; flag the exception explicitly in the END block under `Remaining` if so).

Format. The protocol has up to seven sections; omit any that don't apply:

```
# <Phase id> — <Phase title> · Test Protocol

**Surfaces introduced.** One-line inventory the user can paste into their shell or open directly.

## 1. Hot-state checks (run now, no setup)
Two-to-five short shell commands the user can run immediately to confirm the deployed state. Each line: a `bash` block plus the expected output.

## 2. Daemon / service / console checks (manual)
What to inspect via process listings, service status commands, log directories, or a GUI. Anything the orchestrator cannot script.

## 3. End-to-end behaviour (if a new behaviour ships)
The full happy path the user should walk through — invoking the new command, opening the produced artifact, exercising the new surface end to end. Name every observable side-effect.

## 4. Acceptance items not covered by automated smokes
Phase-file Acceptance entries that require manual verification. Quote the entry and provide the verification recipe.

## 5. Destructive / maintenance-window checks (optional)
Anything that requires a temporary-state change to verify (e.g., "stop the service, edit a file, restart, verify catch-up"). Mark clearly as "DO NOT RUN CASUALLY" and document the restore procedure.

## 6. Future-phase deferrals
Acceptance items the phase claims partial credit for but that genuinely belong to a future phase. Name which phase will close them out.

## 7. Summary
A two-to-three-line wrap: which automated checks PASS, which manual checks remain, what the user should do next.
```

Style notes:
- Use real values from the running system (file paths, session ids, service names) rather than `<placeholders>` the user has to fill in.
- Every shell command is copy-pasteable and self-contained.
- When a check is racey or eventually consistent, say so and provide the deterministic alternative.
- When the protocol leans on a brief or policy, name it — e.g., "verifies the append-only invariant from `policies/log-discipline.md`."

Where to put it: inline at the end of the user-facing report. Long protocols (~> 50 lines) may also be appended to `LOG.md` under the END block as a `### Test protocol` subsection so future planners can find it without scrolling the conversation.

When to skip: mandatory unless the phase is a pure internal refactor with no user-observable surface, or introduces only invariants enforced by automated gates. In either case, state explicitly in the END block under `Remaining`: `Test protocol: skipped (reason: …)`.

### Step 11: Generate the tracked phase report

After status, ripple, lessons harvest, next-phase selection, and the END block
are complete, write `$RUN_DIR/dashboard-handoff.json` using the exact schema in
[`policies/execution-telemetry.md`](../../../policies/execution-telemetry.md).
Ground `what_just_landed`, `see_for_yourself`, `coming_up_next`, and
`recommended_steps` in accepted work, the User Demo, applied ripple, and real
operator prerequisites. Never discuss commit state or place arbitrary HTML,
prompts, responses, secrets, absolute paths, or private source material in the
handoff.

Invoke the pinned command without `--open`:

```
$TELEMETRY_TOOL dashboard --phase "$PHASE_ID" --accepted-trace-id "$TRACE_ID" --handoff "$RUN_DIR/dashboard-handoff.json"
```

It validates and archives the sanitized handoff and regenerates the
chronological offline report under `reports/execution/`. This is the final
tracked close write. A render failure keeps the phase unreported and routes to
the close-repair path in Step 12. When report presentation code changed, the localhost desktop/mobile,
interaction, chart/table agreement, and console protocol in the telemetry
policy must already have passed.

### Step 12: Prove the actual handoff tree

Run a **bare** `./bin/check all` after every tracked close write—status,
ripple, lessons, END block, dashboard handoff, report, and index—is present.
This is the handoff gate. It is deliberately outside the candidate-bound
implementation ledger because the close writes changed the tree; its ignored
full-gate receipt binds the actual tree handed to the user.

No tracked write may follow a successful handoff gate. Opening the already
generated local report is read-only and may follow. If the gate fails, do not
report completion. Reopen the current uncommitted close: restore the phase to
`🚧` when necessary, correct or regenerate the failing close artifact, amend
the current run's still-uncommitted END block in place, and rerun the bare gate.
Do not edit a historical committed END block. If the failure exposes an
implementation defect rather than close bookkeeping, return to Step 7's
proportional correction route; the prior implementation gate is invalidated by
any implementation-candidate change.

### Step 13: Deliver the accepted phase

Runs after the handoff gate is green. Parked acceptance criteria do not hold it
up — they stay open for the user and are reported. Governed by
[`policies/human-in-the-loop.md`](../../../policies/human-in-the-loop.md) and
[`policies/commit-staging.md`](../../../policies/commit-staging.md).

1. **Re-read the tree.** Run `git status` and read the complete final diff.
   Every path must be one this phase touched. An unexpected path means a
   concurrent session shares this checkout — park and report it; never sweep it
   in.
2. **Stage explicitly and verify the staging assertions.** `git add <exact
   paths>` or `git commit -- <paths>`. **Never `git add -A` or `git add .`.**
   Re-read `git status --porcelain` immediately before staging. Partition any
   shared-file hunks, stage moved destinations rather than vanished sources,
   and read the staged diff before committing. If ownership cannot be
   established safely, park delivery.
3. **Commit and verify its file set.** Use an ordinary factual message
   describing the change. No agent
   credit, no `--no-verify`. A pre-commit hook refusal parks the commit and is
   reported truthfully — never retried around. Compare `git show --stat
   --oneline HEAD` with the intended file list before pushing.
4. **Push**, only when the current branch has exactly one unambiguous
   configured upstream and the update is a fast-forward. Never force. Never
   create an upstream, select a remote, tag, rebase, or repair history — those
   belong to the user.
5. **Verify.** Fetch, then prove `HEAD`, the tracking ref, and the remote tip
   agree and the tree is clean.

Any of the parks in the policy — unexpected path, hook refusal, missing or
ambiguous upstream, rejected push, divergence, residual dirt — stops delivery,
is reported, and is never worked around. An open parked criterion is not one of
them.
A user restriction recorded in the END block (`Delivery: restricted — …`) makes
the run local-only or uncommitted; a restriction narrows delivery only and never
relaxes a gate.

Commit and push change no tracked content, so they legitimately follow the
handoff gate. **No later tracked write records their outcome** — the outcome is
reported to the user and nowhere else.

### Step 14: Open the report and hand off

Open the already generated phase page without modifying it. A browser-open
failure is presentation-only and may be retried; it changes no artifact. Then
report to the user.

Report to the user, in this order:

- **🚨 Role disconnects (per [`policies/role-models.md`](../../../policies/role-models.md)):** for every role whose runtime call failed after a successful preflight (three-signal gate or timeout) so it ran native instead, add a 🚨 line stating what was configured, what actually ran, and why — e.g. `🚨 coder configured for opus but ran native (call timed out) — output was NOT produced by opus`. If every role ran on its resolved venue, omit this entirely. Preflight failures never reach Step 10 because they abort before phase state exists.
- **What to try: the user testing protocol** for what's new or changed (Step 10a). This leads because it is what the user does next — the phase is already delivered, so the demo, not a commit instruction, is the handoff (`policies/user-demo-protocols.md`).
- **Acceptance:** what closed objectively on gate evidence, and what is parked for the user's judgment. Both halves, even when one is `None`.
- **Delivery:** the commit id and the push result — or the park and its reason, or the user's restriction verbatim.
- Which phase was completed and which is next (`⬅️`).
- Files created/modified, grouped by surface.
- Build and gate status.
- Candidate identity, finding convergence, implementation-gate identity,
  handoff-gate receipt, and any
  verified protocol recoveries.
- Any material wall-clock opportunity used or surfaced, and how the unchanged
  guarantees were preserved. Omit marginal timing noise and no-leverage
  observations.
- Any Minor Corrections or Observations the reviewers noted that the user may want to track.
- Lessons filed or recurred this phase, and any graduation DECIDE items awaiting the user's ratification (with the proposed target surface for each).

**Delivery is not acceptance.** The phase being committed and pushed settles
nothing the user owes judgment on; the parked criteria stay parked, and saying
otherwise in the report is the failure this whole boundary exists to prevent.

---

## Operating notes

- The four canonical role names (`phase-planner`, `plan-reviewer`, `phase-coder`, `code-critic`) are load-bearing. See [`policies/four-canonical-agents.md`](../../../policies/four-canonical-agents.md).
- The verdict header (`## Verdict: APPROVED` or `## Verdict: REVISE`) is parsed by string match. Mis-cased or rephrased verdicts break orchestration.
- Per-role model/venue ([`policies/role-models.md`](../../../policies/role-models.md)): `kickoff.yaml`'s human-editable `role_models` section (set directly or via `roles`) resolves each of the four roles to separate model and effort fields plus an implied venue at Step 0a, scoped by which harness is orchestrating. Step 0b live-validates every non-native CLI/model/access target and aborts before phase mutation on any upstream failure. The shipped default routes reviewer + critic to the *other* harness (cross-vendor review — there is no separate on/off token) and leaves planner + coder native; a project may resolve any role anywhere. A role resolving to a CLI is invoked there with the resolved model/effort overrides (write-enabled for the coder), resuming the same session across the role's rounds. Orchestration and build gates always run on the session model — never pinnable. A later runtime failure after successful preflight may still fall back per-stage and surfaces a 🚨 in the Step 10 report. The recursion guard env var is `KICKOFF_DELEGATION_DEPTH` (a delegated role never re-delegates). Recipes and handoff hygiene: [`briefs/cross-agent-invocation.md`](../../../briefs/cross-agent-invocation.md).
- Per-role execution budgets ([`policies/role-timeouts.md`](../../../policies/role-timeouts.md)): Step 0c loads portable defaults from `kickoff.yaml`'s `role_timeouts` section. Every external initial/resume/rescue call runs through the generated-command watcher; native calls use the same budgets through the harness wait mechanism. The finalized shared trace is authoritative; `.kickoff/role-timings.jsonl` remains local protocol/recalibration diagnostics.
- Exact execution telemetry ([`policies/execution-telemetry.md`](../../../policies/execution-telemetry.md)): monotonic nanoseconds, overlap-safe unions, exclusive attribution, candidate/role/gate joins, truthful recovery, phase-level operator-input parks, and deterministic offline reports are one acceptance-bound contract. UTC is correlation only for trace spans; a cross-boot operator park uses visibly non-exact calendar duration. Wait mirrors are not extra work, operator parks are reported separately, and missing measurement never becomes a reassuring zero.
- Research authority ([`policies/research-authority.md`](../../../policies/research-authority.md)): planner/reviewer may originate search and retrieval within their configured budgets; coder/critic may retrieve approved authorities but not originate search. Ambient MCP servers and plugins are allow-by-default unless explicitly narrowed, and external research receives no repository or candidate content.
- Review lanes and follow-up routing ([`policies/review-lanes.md`](../../../policies/review-lanes.md)): a phase's `review_lane: light` frontmatter skips Step 4 for mechanical initial work; the invocation-only `one-shot` token additionally skips Step 3 for well-specified isolated work. The code critic runs on every initial implementation and guards both lanes. The orthogonal `evidence_lane: light` frontmatter reduces evidence ceremony (never the close seal) for phases off the authority/irreversible/deploy triggers. Later test- or user-driven corrections use direct fix, coder-only, or full-cycle routing according to risk and size; only the full-cycle route repeats independent review.
- Candidate-bound evidence ([`policies/orchestration-evidence.md`](../../../policies/orchestration-evidence.md)): every run uses a fresh isolated evidence directory; revisions use stable findings and deterministic packets; the implementation gate names the unchanged approved candidate, then a bare post-bookkeeping handoff gate proves the actual tree delivered to the user.
- Fail-closed park and diagnosed resume ([`policies/fail-closed-resume.md`](../../../policies/fail-closed-resume.md)): any first-encountered defect finishes the run truthfully — dispatches stopped, spans closed with the failure outcome, artifacts preserved, candidate restoration or lineage proved — and records a five-part failure signature in the phase's append-only `.kickoff/failure-signatures.jsonl` ledger. A **novel**, fully diagnosed signature with a recorded causal correction may open a fresh corrective trace against the phase's self-resume budget (`kickoff.yaml` `run_budgets.self_resume`, shipped default 3, restored by any operator relay; `0` pins every park to the operator). A **recurring** signature always stops for the operator. Prelaunch dispatcher rejections are corrected-and-relaunched at most once without consuming budget. Sealing is a close-time act: never re-run whole-repository sealing per fix inside a convergence loop.
- `ingest-findings` **requires `--review-span-id`** and refuses without it. The convergence integers attach to the review pass's own intelligence span, and a span is immutable once the trace is finalized — so an omitted flag makes `timing-summary` refuse for the entire run and cannot be repaired afterward. Preserve each reviewer's and critic's intelligence span id when you dispatch it. For an ingest that is genuinely **not** a review pass — most commonly the orchestrator recording an `open → addressed` transition after a *plan* revision, since `phase-planner` emits a revised plan rather than a `## Finding Evidence` block — pass `--no-review-span '<reason>'`, which records the omission in `review-metrics-omitted.jsonl` instead of hiding it.
- Human wall-clock efficiency is an ambient judgment, not a timer-driven
  program: act or surface only when a substantial, low-risk gain is reasonably
  apparent, never at the expense of effectiveness or either close gate.
- The ripple pass in Step 9a (sub-phase close) and Step 9b (major-phase close) is governed by [`policies/phase-ripple.md`](../../../policies/phase-ripple.md). AUTO ripples land in the same session; DECIDE ripples appear in the END block as named follow-ups.
- The lessons harvest in Step 9c is governed by [`policies/lessons.md`](../../../policies/lessons.md). Agents file and recur ledger entries; graduation into a rule surface is a human-ratified DECIDE, never an autonomous edit. A follow-up correction that reveals a recurring learning files a lesson too, even though it skips the full Step 9 family.
- Cross-harness: this same canonical skill drives both Claude Code and Codex. Claude Code invokes it as `kickoff`; Codex discovers it through `.agents/skills/kickoff` (a directory symlink to `.claude/skills/kickoff/`) and invokes it as `$kickoff`. Edit this canonical skill, not the mirror.
- If your harness does not expose named subagents, perform the same role sequence locally by reading each `.claude/agents/<role>.md` directly and adopting that role's reading protocol and output format for the duration of the step.

## Local fallback

If the current platform does not expose named subagents, perform the same role sequence locally and follow the canonical role procedures in `.claude/agents/phase-planner.md`, `.claude/agents/plan-reviewer.md`, `.claude/agents/phase-coder.md`, and `.claude/agents/code-critic.md` directly. The agents' tool-stance and verdict format apply just the same.
