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

Every role must produce its first structured event within **120 seconds**. The turn column is deliberately named `claude_max_turns` in configuration: Claude exposes that CLI circuit breaker, while Codex and native subagents do not expose an equivalent per-invocation flag. Their enforceable guards are the three clocks. Authentication preflight has its own 120-second deadline in [`role-models.md`](role-models.md). The 5-cycle convergence backstop remains separate: it limits revision rounds, while this policy limits one round.

These are hang guards, not performance targets or promises. Planning and review get enough room for repository inspection and reasoning; implementation gets a materially larger envelope; critique sits between them. There is deliberately no whole-phase timeout because phase scope and build gates vary too widely.

## Enforcement

External CLI roles run through `bin/kickoff-config watch`. The wrapper:

1. starts the command in its own process group with stdin closed;
2. tees structured stdout and diagnostics to named artifacts;
3. requires a first stdout event even when the child exits quickly, resets the idle clock on subsequent stdout or stderr activity, and enforces the hard deadline regardless of activity;
4. truncates named result artifacts before launch and requires the current call to repopulate them;
5. verifies that the actual CLI/model/effort flags match the recorded routing metadata;
6. terminates the entire process group on timeout, preserving artifacts and any session identifier already emitted; and
7. returns 124 on timeout, 65 on a stream/artifact protocol failure, or the child's status otherwise.

Codex runs with JSONL events and names its `--output-last-message` path as the watchdog's required output. Claude runs with `--output-format stream-json --verbose`; the wrapper extracts and requires the final `result` event. The role-shape gate in [`role-models.md`](role-models.md) still applies after the process exits.

Native roles use the same role-specific hard and idle budgets through the orchestrating harness's sub-agent wait/status mechanism. If the harness cannot expose structured progress or an idle watchdog, enforce the hard deadline and report that idle telemetry was unavailable; do not invent activity. The orchestrator remains responsive and gives the user a progress update at least every 60 seconds while it waits.

One max-turn rescue is allowed only for a review role that completed investigation but failed to emit its verdict. Resume the existing session with the concise “conclude now” instruction. Do not automatically rerun a timed-out role from scratch: a timeout falls through the existing stage fallback state machine and is surfaced with a 🚨.

## Local telemetry and recalibration

Every watched invocation appends one JSON object to `.kickoff/role-timings.jsonl`, which is local runtime state and must not be committed. Records include separate model and effort fields alongside phase, role, venue, timestamps, duration, first-event latency, longest idle gap, best-effort turns/tokens, outcome, timeout kind, and exit code. The END block summarizes timings for the phase; raw records stay local.

`bin/kickoff-config recommend-timeouts` groups successful records by `(role, venue, model, effort)`. It emits a recommendation only after at least 30 successful samples in a group:

```
hard deadline = max(role hard floor, 2 × p95 successful duration)
idle watchdog = max(role idle floor, 2 × p95 longest successful idle gap)
```

Timeouts are right-censored evidence, not successful durations. Review them separately before changing a budget. Recommendations never rewrite configuration and never auto-tighten a deadline; a human evaluates the workload and edits the policy/config together.

## Portability

The two policy sections, unified config schema and shipped defaults, manager, telemetry schema, `kickoff` instructions, `roles`, and invocation recipes are one **atomic universal bundle**. `stamp` copies the bundle. `teach` proposes it atomically but preserves an existing target's values, comments, `extensions` data, local telemetry, model choices, and project-specific overrides. `learn` may adopt improved mechanics, schema, algorithms, or universal defaults, but never imports donor operational state.

## Relationship to other policies

- [`role-models.md`](role-models.md) resolves venue/model/effort, performs fail-closed preflight, gates artifacts, and owns runtime fallback.
- [`four-canonical-agents.md`](four-canonical-agents.md) owns role semantics and the five-cycle convergence limit.
- [`mechanistic-vs-intelligence.md`](mechanistic-vs-intelligence.md) places validation, enforcement, measurement, and percentile calculation in `bin/kickoff-config`; deciding whether evidence warrants a policy change remains human judgment.
- [`human-in-the-loop.md`](human-in-the-loop.md) still governs completion: timing out or finishing within budget says nothing about subjective acceptance.
