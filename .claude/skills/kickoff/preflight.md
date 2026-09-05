# Kickoff — Preflight and phase entry

Read this resource before executing its branch. Enter through [SKILL.md](SKILL.md); its resource table defines the order. Before any failure, resume or operator-input branch, read [recovery.md](recovery.md).

### Step 0a: Resolve per-role model/venue

For an initial implementation or delegated follow-up, resolve once per session before role work begins, per [`policies/role-models.md`](../../../policies/role-models.md). This resolves a `(venue, model, effort)` for **each of the four roles** from `kickoff.yaml`'s harness-aware `role_models` section. A direct follow-up fix skips this step.

1. **Recursion guard.** If the env var `KICKOFF_DELEGATION_DEPTH` is set, this session is *itself* a delegated role invoked by an outer `kickoff` run; **every role runs native** and no further delegation happens. Skip the rest of Step 0a.
2. **Detect the orchestrating harness `H`:** `CLAUDECODE=1` in the environment → `claude`; otherwise → `codex`.
3. **Read + resolve.** Run `./bin/kickoff-config show models` — it validates the complete human-editable `kickoff.yaml` and prints the resolved `model` plus optional separate `effort` field per role for the current harness. (The resolution rule is: `role_models[H][role]` if set, else `role_models['default'][role]` if set, else `{model: default}`.) Models and their supported effort subsets are defined in [`policies/role-models.md`](../../../policies/role-models.md#human-editable-configuration), including `astra`. Quality/same-harness is the shipped preset; balanced, economy and explicit cross-vendor review expand into ordinary pins through `apply-preset`.
4. **Map each resolved value to a venue:**
   - `default` → **native** (in-harness subagent on the session model). No CLI.
   - `claude` → the `claude` CLI, its configured default model (no `--model`).
   - `codex` → the `codex` CLI, its configured default model (no `-m`).
   - `opus` / `fable` → the `claude` CLI, `--model opus|fable`.
   - `astra` → the `codex` CLI, `--model gpt-6-astra`.
   - `sol` / `terra` / `luna` → the `codex` CLI, `--model gpt-5.6-sol|terra|luna` respectively.
   - A separate effort field adds `-c 'model_reasoning_effort="<effort>"'` to Codex initial and resume invocations, or `--effort <effort>` to Claude initial and resume invocations. An absent effort field preserves the configured/default effort.

Remember each role's resolved `(venue, model, effort)` and the orchestrating harness for Steps 3–6 and the Step 10 END block. Freeze this resolution with the run’s tool/config bundle. Roles do not re-resolve during the run, even when implementation edits live pins; new settings begin the next run. A non-`default` model always goes through the CLI recipe — do **not** short-circuit "model == session model" (uniform resolution, no session-model probing).

### Step 0b: Preflight and retain the role-topology receipt

Before identifying a phase, changing a status marker, writing `LOG.md`, or invoking any role for an initial implementation or delegated follow-up, allocate an opaque temporary preflight directory and run:

```
PREFLIGHT_DIR="$(mktemp -d)"
./bin/kickoff-config preflight --receipt "$PREFLIGHT_DIR/role-preflight.json"
```

This deterministic preflight resolves the same role pins as Step 0a and makes one live real-read call for every unique non-native `(CLI, model, effort, access mode)` target. It creates unpredictable ASCII text in an isolated temporary working directory and requires the venue to read and return that exact text; the manager validates the response and computes the file SHA-256 for the receipt, using the production credential scrubs, model/effort overrides, headless flags, stdin closure, and read-only versus write-enabled posture. The Codex probe adds `--skip-git-repo-check` solely because that directory is intentionally not a checkout. The active orchestrator needs no probe because the current session already proves it is authenticated; every role that will run through a subprocess is probed, including a deliberately configured same-vendor pin. Duplicate targets are probed once.

The preflight validates the full upstream path needed by the phase: CLI presence, usable authentication, model entitlement, network reachability, current flag compatibility, sandbox/access posture, a response within the 120-second hang guard, and access to the unpredictable local bytes. A known echoed sentinel, status command, or credential-file check is insufficient. The receipt binds the routing-config digest, orchestrating harness, exact target descriptors, and shared probe digest; an all-native topology receives the same receipt shape with an empty target set.

**Coder toolchain probe.** For every write-enabled target (the coder, when pinned), the preflight additionally asks the venue to run the repository's cheapest toolchain probe (`./bin/test --help`) from the checkout and reply with `KICKOFF_TOOLCHAIN_OK` or the failure text. This one does **not** abort: a venue whose sandbox cannot reach the toolchain (a uv cache outside its allowed paths, a missing system tool) is reported as `Role venue preflight: WARNING — coder venue cannot run the toolchain: <diagnostic>`, and the orchestrator records for Step 5 that the unverified-handoff guard will run the focused sequence natively on every coder return. Without this, the coder discovers the gap mid-phase, hands off unverified, and the critic spends its round on formatting.

**Any failure aborts `kickoff` immediately.** Report the failed target and the script's diagnostic, then stop. Do not fall back to native, identify or decompose the phase, change `plan/INDEX.md`, append a START/END block, or invoke an agent. After the user fixes authentication or the other upstream error, tell them to rerun `/kickoff` in Claude Code or `$kickoff` in Codex from a clean pre-phase state. If every role is native, or the recursion guard makes every role native, preflight still writes and verifies the empty-target receipt.

### Step 0c: Load per-role execution budgets

For an initial implementation or delegated follow-up, run `./bin/kickoff-config show timeouts` and retain the first-event timeout, each role's hard deadline and idle watchdog, plus its Claude-only `claude_max_turns` circuit breaker from `kickoff.yaml`'s `role_timeouts` section, per [`policies/role-timeouts.md`](../../../policies/role-timeouts.md). A direct follow-up fix skips this step. The three clocks apply to **every invocation or resumed revision round**; the turn value applies only when the delegated venue is Claude, because Codex and native subagents expose no equivalent flag. The shipped seed values are below; when a project has deliberately recalibrated its config, the validated config output governs:

- planner — 1,800 s hard / 600 s idle / 50 turns;
- reviewer — 1,800 s hard / 600 s idle / 50 turns;
- coder — 7,200 s hard / 1,200 s idle / 200 turns;
- critic — 2,700 s hard / 600 s idle / 50 turns;
- every role — first structured event within 120 s.

For every external CLI call, including resumes and the one permitted max-turn rescue, invoke the production command through `./bin/kickoff-config watch` with `--role`, resolved `--venue`, `--model`, `--effort`, phase id, and named stdout/stderr/result artifacts. Pass Claude's extracted result path as `--result-file`; pass Codex's `--output-last-message` path as `--required-output-file`. The wrapper closes stdin, verifies routing flags, truncates result paths, streams progress, terminates the process group on first-event/idle/hard timeout, and appends local telemetry. It returns the child status, 124 on timeout, 65 on unrecoverable protocol failure, or 66 (`completed-unverified-protocol`) when a successful child left a fresh artifact but no complete terminal stream.

Exit 66 is not success. Preserve the artifact and verify the exact role shape, the expected candidate id, and its structured change/finding evidence through `bin/kickoff-evidence`. If all checks pass, continue without rerunning the intelligence work and record `[protocol recovered: terminal stream incomplete]` for Step 10. If any check fails, follow [governed recovery](../../../policies/role-models.md#governed-recovery), retaining the failed evidence and selected model/effort. Codex emits JSONL with `--json`; Claude emits JSONL with `--output-format stream-json --verbose`. Preserve each role's timing record for Step 10.

For native subagents, use the same role-specific hard and idle budgets through the harness's wait/status mechanism. Progress means a real agent event, status transition, or tool result; the orchestrator's own polling is not progress. If the harness cannot expose idle timing, enforce the hard deadline and record first-event/idle as `unavailable`. Keep the user informed at least every 60 seconds while waiting.

Run `./bin/kickoff-config show research` and retain the role authority and originating-query budgets from `kickoff.yaml`. Planner and reviewer may search and retrieve; coder and critic may retrieve plan/brief-identified resources and same-host structural neighbors but may not originate searches. Installed MCP servers and plugins remain available by default unless the project or phase explicitly narrows them. Every dispatch receives the resolved directive from `bin/kickoff-config`; do not hand-author a weaker prompt. See [`policies/research-authority.md`](../../../policies/research-authority.md).

### Step 1: Identify the phase

Read `plan/INDEX.md` (the authoritative phase ledger) and locate the phase to work on. Status markers live in the `INDEX.md` phase table, not in the per-phase files (see [`policies/phase-status.md`](../../../policies/phase-status.md)).

- **No arguments**: find the row whose status is `⬅️` in the phase table. If none exists while a row is `🚧`, require an explicit phase id to resume that active work. If every row is `✅`, report that the project is complete. If incomplete work is idle with no `⬅️`, or more than one row is `⬅️`, stop on the invalid ledger rather than choosing through ambiguity.
- **`phase N` / `phase N.M`**: find the row whose link is `[Phase <id>](phase-<id>.md)`.
- **Free text**: resolve to a phase row or ask the user.

The lifecycle invariant is: every phase row has exactly one recognized status; idle incomplete work has exactly one `⬅️`; active or complete work may have zero; more than one is always invalid. `./bin/check-catalogs` enforces this same state machine.

Then resolve the **review lane** per [`policies/review-lanes.md`](../../../policies/review-lanes.md): read `review_lane:` from the target phase file's frontmatter. Absent or `full` → **full** lane. `light` → **light** lane: Step 4 (plan review) will be skipped; the code critic still runs and guards the lane. You may upgrade a declared `light` to `full` when the phase's actual deliverables look non-mechanical — note the upgrade and why. Never downgrade `full` to `light` on your own.

**One-shot is invocation-only.** If the invocation line carries the `one-shot` token, check eligibility (binding-spec bar + isolation, per the policy): eligible → run the one-shot lane (Steps 3–4 skipped; coder → orchestrator vet → code critic → normal acceptance close; the mechanically derived role set drops `role.plan` and the `orchestration.planning` stage); ineligible → refuse with the stated reason and run the phase file's declared lane. A frontmatter `review_lane: one-shot` is invalid — refuse and ask. Escalation (a park, a write-set widening, a second gate failure, or the critic's `Escalate: full lane`) cannot continue in the same evidence run: finalize the one-shot run truthfully as paused, re-init a fresh full-lane run, carry open findings forward in the revision packet, and record `one-shot → full (escalated: <reason>)` in the END block.

Also resolve the **evidence lane**: read optional `evidence_lane:` frontmatter (absent or `full` → full apparatus; `light` → structural tests, the operator gate, and the mandatory seal at close, with role registration/span joins/stage envelopes validated-if-present). Refuse a `light` declaration whose deliverables touch an authority surface, irreversible or external state, or a deploy seam; you may upgrade `light` → `full`, never downgrade. Report both lanes in the opening report and END block.

Tell the user which phase you are picking up, the path to its file (`plan/phase-<id>.md`), the resolved review lane, and that gate-proved work will be committed and fast-forward-pushed at close (delivery is not acceptance) unless they restrict it now (`policies/human-in-the-loop.md`). Stating the delivery posture in the first minute is what makes a restriction cheap to give — it costs one sentence before any commit exists.

### Step 1a: Assess outcome boundaries (major phases only)

A phase is one independently acceptable outcome. Assess decomposition at entry; absent child files, multiple modules/tests/docs, surface count, session length, and a model's reputation are not reasons to split. A coherent change stays intact.

Split only at an unresolved consequential decision, an independently accepted prerequisite, a distinct deployment/migration/human seam, or a demonstrated model-coherence limit. Name the boundary and its evidence in the opening report. An unresolved consequential decision goes to the operator before implementation; it is not a private choice delegated to the coder. Ordinary implementation steps remain inside the approved phase. Completed phases remain completed.

When an authorized boundary requires children and none exist, invoke `phase-planner` for `phase-N.1` only, with Goal / Deliverables / Acceptance / Brief refs and the appropriate review lane. Read [dispatch.md](dispatch.md) before that pre-run dispatch. Add the child file, row and dependency edge; mark the parent `🚧` and the child `⬅️`, then restart kickoff against the child. Do not draft subsequent children yet: [close.md](close.md) Step 9a drafts one continuation using the predecessor's outcomes. Splitting or changing consequential scope remains the operator's decision; reaching a plan-size limit does not itself authorize decomposition.

All major phases should already have bootstrap sketches. A missing selected major-phase file is a bootstrap-completeness failure to surface, not permission to invent one here. The outcome test and roadmap rationale live in [the methodology brief](../../../briefs/methodology.md#the-eleven-steps).

### Startup authority boundary

After successful preflight and phase/lane selection, set the selected major phase's INDEX row to `🚧` **before Step 1b captures whole-file authorities**. Explicit selection is required to resume an already-in-progress phase; preserve its marker. Do not change any per-phase status. For a completed-phase correction, retain `✅` and follow [recovery.md](recovery.md). This ordering does not relax ledger validation or permit substantive INDEX edits after capture.

When the approved work changes governing prose, perform the approved preparation first, retain its exact reports and candidate lineage, and close that run truthfully parked. Capture the final authorities and already-in-progress marker in a fresh run, with fresh plan/review binding, before genuine remaining executable work. Do not rewrite stored hashes, waive authority checks, manufacture edits, or claim preparation closes the phase. Later governing changes require another truthful park/rebind.

### Step 1b: Start telemetry and initialize candidate-bound evidence

After target resolution and any decomposition, start exactly one repository trace with `./bin/execution-telemetry start --scope-root . --scope engine --scope-id engine --run-type kickoff --operation phase.<id>`. Retain the returned trace id and root span id. Immediately open a `reconciliation` child named `orchestration.setup`, attempt 1, before allocating the evidence directory.

Allocate a **new** opaque run directory with `mktemp -d`; never reuse a path from an earlier or interrupted run. Initialize it through `./bin/kickoff-evidence init` per [the orchestration-evidence policy](../../../policies/orchestration-evidence.md). Pass the phase id, authority list, trace id, root span id, open setup span id, resolved review lane, resolved evidence lane, and follow-up route. Authorities, in governing order, are `plan/INDEX.md`; target and parent phase files; cited briefs; declared dependencies; the immediately preceding completed phase; `CLAUDE.md`; and every applicable policy. Also pass `--preflight-receipt "$PREFLIGHT_DIR/role-preflight.json"`; initialization copies and revalidates the receipt against the current routing configuration. Use repo-relative paths with optional `::locator` suffixes. Initialization failure stops the run; preserve the already-in-progress marker and report the failed initialization without claiming role work began.

Initialization pins `kickoff-evidence`, `kickoff-tree-id`, `kickoff-command-zero`, `execution-telemetry`, `kickoff-config`, `kickoff.yaml`, the candidate-boundary policy, and their runtime libraries beneath `$RUN_DIR/tools/`. From that point use the pinned `EVIDENCE_TOOL`, `TELEMETRY_TOOL`, `WATCHER_TOOL`, and command-zero tool for every evidence, role, gate, recovery, finalization, summary, and dashboard action.

The root owns sequential, non-overlapping `reconciliation` stages: `orchestration.setup`, `orchestration.planning`, `orchestration.implementation`, `orchestration.acceptance`, and `orchestration.close`. Close one before opening the next and increment a stage's attempt on re-entry. Role, wait, and gate spans may nest or overlap, but aggregation assigns specific work first and counts only the stage's exclusive remainder as orchestration. Never fabricate a missing span.

For a follow-up correction, create a fresh trace and evidence run against the correction brief and current tree. Runtime state remains outside the repository; only the finalized privacy projection enters `EXECUTION_LOG.jsonl`.

### Step 2: Open the log after authority capture

Verify that the selected row still has the marker captured by Step 1b. Do not flip it here: startup already set `🚧` before capture. The phase file never carries status. See [phase-status.md](../../../policies/phase-status.md).

Construct the complete START block in a temporary file, then append it at true EOF with `./bin/log-append < <block-file>`. Create `LOG.md` if it does not exist (with the header described in [`policies/log-discipline.md`](../../../policies/log-discipline.md)). Never use a contextual patch or direct editor write for log construction. Format:

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

Close `orchestration.setup` successfully and immediately open `orchestration.planning`. Recompute the candidate through `$EVIDENCE_TOOL current-candidate`; never dispatch from a remembered initialization id. START is bookkeeping, but authority integrity is checked independently. For one-shot, open `orchestration.implementation` instead of the omitted planning stage.
