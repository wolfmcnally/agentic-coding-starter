# Policy: Per-Role Execution Budgets

Every `kickoff` role invocation has three independent guards: **first structured event**, **idle progress**, and **absolute runtime**. A role may legitimately take a long time; it may not disappear silently or run without an upper bound. Budgets apply to each invocation or resumed revision round, not to the phase as a whole.

## Shipped budgets

The human-editable `role_timeouts` section of [`kickoff.yaml`](../kickoff.yaml) is the source of truth. `bin/kickoff-config` validates and consumes it without disturbing `role_models`, comments, or data under `extensions`.

| Role | Hard deadline | Idle watchdog | Claude CLI turn cap |
|---|---:|---:|---:|
| Planner | 1,800 s | 600 s | 50 |
| Plan reviewer | 1,800 s | 600 s | 50 |
| Coder | 7,200 s | 1,200 s | 200 |
| Code critic | 2,700 s | 600 s | 50 |

Every role must produce its first structured event within **120 seconds**. The turn column is deliberately named `claude_max_turns` in configuration: Claude exposes that CLI circuit breaker, while Codex and native subagents do not expose an equivalent per-invocation flag. Their enforceable guards are the three clocks. Authentication preflight has its own 120-second deadline in [`role-models.md`](role-models.md). The 10-cycle convergence backstop remains separate: it limits revision rounds, while this policy limits one round.

These are hang guards, not performance targets or promises. Planning and review get enough room for repository inspection and reasoning; implementation gets a materially larger envelope; critique sits between them. There is deliberately no whole-phase timeout because phase scope and build gates vary too widely. Every dispatch must use an execution surface that can remain observable for the full configured budget — see [The harness ceiling bounds every budget](#the-harness-ceiling-bounds-every-budget) below.

## Enforcement

External CLI roles run through `bin/kickoff-config watch`. The wrapper:

1. starts the command in its own process group with stdin closed;
2. tees structured stdout and diagnostics to named artifacts;
3. requires a first stdout event even when the child exits quickly, resets the idle clock on subsequent stdout or stderr activity, and enforces the hard deadline regardless of activity;
4. truncates named result artifacts before launch and requires the current call to repopulate them;
5. verifies that the actual CLI/model/effort flags match the recorded routing metadata;
6. terminates the entire process group on timeout, preserving artifacts and any session identifier already emitted; and
7. records child status, artifact freshness, and terminal stream completeness
   independently; and
8. returns 124 on timeout, 65 on an unrecoverable protocol failure, 66 when a
   fresh artifact requires explicit verification after an incomplete terminal
   stream, or the child's status otherwise.

Codex runs with JSONL events, requires a terminal `turn.completed`, and names
its `--output-last-message` path as the watchdog's required output. Claude runs
with `--output-format stream-json --verbose`; the wrapper normally extracts
the final `result` event and can preserve the last assistant text for exit 66.
The role-shape and candidate-bound evidence gates in
[`role-models.md`](role-models.md) still apply after the process exits.

Native roles use the same role-specific hard and idle budgets through the orchestrating harness's sub-agent wait/status mechanism. If the harness cannot expose structured progress or an idle watchdog, enforce the hard deadline and report that idle telemetry was unavailable; do not invent activity. The orchestrator remains responsive and gives the user a progress update at least every 60 seconds while it waits.

One max-turn rescue is allowed only for a review role that completed investigation but failed to emit its verdict. Resume the existing session with the concise “conclude now” instruction. Do not automatically rerun a timed-out role from scratch: a timeout follows [governed recovery](role-models.md#governed-recovery), preserving the failed attempt and selected model/effort. No automatic native substitution is authorized.

### The harness ceiling bounds every budget

The effective role budget is the smaller of the configured role budget and the
execution surface's own hard ceiling. Some harness foreground tools accept a
requested timeout above their ceiling and silently clamp it; others return a
durable session handle that the orchestrator can poll past the initial yield.
Before dispatch, prove which behavior the current harness provides. A
foreground `bin/kickoff-config watch` is valid only when its session remains
observable for the full configured budget.

**When a foreground call would be silently clamped or its session handle would
be lost, dispatch through the harness's own tracked background mechanism.** Do
not use detached `nohup`: it dodges the foreground ceiling but forfeits the
completion signal and leaves the orchestrator polling blind.

**The silent-death signature for a clamped foreground dispatch** — all four
together, none of which says "timeout":

- exit 143 (SIGTERM to the watcher; the process group takes the child too);
- an artifact present, zero bytes, well-formed path;
- stdout that simply stops mid-stream;
- no row in the role-timings ledger, and no dispatch row recorded at all.

The discriminator that matters: an empty artifact **mid-run is normal**, because
the child writes its final message at the end. Empty is a death signal only
together with a stopped stream and exit 143.

**Diagnose at the caller before the venue.** The observable symptom is the *child*
dying beside a healthy-looking parent, and every instinct sends the investigation
to the delegated venue — is the model wedged, is the CLI broken, is the sandbox
denying something. Before blaming a venue, check what actually bounded the child:
the tool's own limits, the harness ceiling, the parent's timeout, the process
group. The caller is the last place anyone looks, because the caller is the thing
doing the looking.

**Standing mitigation.** After *any* interrupted role dispatch, verify the dispatch
row exists and close orphaned spans **unconditionally**. The append-then-amend
opened/terminal dispatch lifecycle in `bin/kickoff-evidence`
([`orchestration-evidence.md`](orchestration-evidence.md)) is the durable repair —
a row written only at the end loses every death before that point — but a swept
trace and an unswept one look identical afterward, so the sweep can never be
conditional on having noticed.

## Authoritative and local telemetry

The finalized shared trace governed by
[`execution-telemetry.md`](execution-telemetry.md) is authoritative for phase
timing. It uses monotonic nanoseconds, exact role/wait joins, and truthful
timeout/interruption outcomes. Wait spans mirror delegated work and are never
counted as additional work. Time awaiting required user input is recorded in
the separate phase-level operator-park ledger and never folded into a role's
idle or wait duration.

The watcher also keeps local protocol diagnostics for timeout recalibration.
Those rows are not a second execution ledger and cannot fill a missing shared span. Their `model`/`effort` fields record requests; optional provider observations and null-as-unreported reporting follow [`role-models.md`](role-models.md#end-block-reporting). Observation failures neither establish success nor change routing.

## Local recalibration

Every watched invocation appends one JSON object to
`.kickoff/role-timings.jsonl`, which is local runtime state and must not be
committed. Records include separate model and effort fields alongside phase,
role, venue, timestamps, duration, first-event latency, longest idle gap,
best-effort turns/tokens, outcome, timeout kind, wrapper exit code, child exit
code, artifact status, and stream status. The END block summarizes timings and
verified protocol recoveries for the phase; raw records stay local.

The run-scoped evidence ledgers separately record packet bytes and source
hashes, candidate ids, changed-path counts, finding states/reopenings/
classifications, and gate results. Do not infer nested reasoning, repository
read, test, idle-cause, or critical-path spans when a venue does not emit them;
record unavailable data as `unknown`.

`bin/kickoff-config recommend-timeouts` groups successful records by `(role, venue, model, effort)`. It emits a recommendation only after at least 30 successful samples in a group:

```
hard deadline = max(role hard floor, 2 × p95 successful duration)
idle watchdog = max(role idle floor, 2 × p95 longest successful idle gap)
```

Timeouts are right-censored evidence, not successful durations. Review them separately before changing a budget. Recommendations never rewrite configuration and never auto-tighten a deadline; a human evaluates the workload and edits the policy/config together.

## Portability

The two policy sections, unified config schema and shipped defaults, manager, telemetry schema, `kickoff` instructions, `roles`, and invocation recipes are one **atomic universal bundle**. `stamp` copies the bundle. `teach` proposes it atomically but preserves an existing target's values, comments, `extensions` data, local telemetry, model choices, and project-specific overrides. `learn` may adopt improved mechanics, schema, algorithms, or universal defaults, but never imports donor operational state.

## Relationship to other policies

- [`role-models.md`](role-models.md) resolves venue/model/effort, performs fail-closed preflight, gates artifacts, and owns governed runtime recovery.
- [`execution-telemetry.md`](execution-telemetry.md) owns exact shared spans, aggregation, recovery, and the phase report.
- [`four-canonical-agents.md`](four-canonical-agents.md) owns role semantics and the ten-cycle convergence limit.
- [`mechanistic-vs-intelligence.md`](mechanistic-vs-intelligence.md) places validation, enforcement, measurement, and percentile calculation in `bin/kickoff-config`; deciding whether evidence warrants a policy change remains human judgment.
- [`human-in-the-loop.md`](human-in-the-loop.md) still governs completion: timing out or finishing within budget says nothing about subjective acceptance.
