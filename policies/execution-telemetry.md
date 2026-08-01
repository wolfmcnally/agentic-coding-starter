# Policy: Execution Telemetry and Phase Reports

Kickoff execution timing is exact, candidate-bound, privacy-bounded, and
machine-owned. It measures elapsed work; it does not replace narrative logs,
status events, gate evidence, or human judgment about whether an optimization
is worthwhile.

## Exact schemas

Durable records use closed schemas:

- `agentic_starter.execution_span.v1` for one closed span;
- `agentic_starter.execution_trace.v1` for one finalized trace bundle.

Unknown keys or enum members, malformed identifiers, missing required values,
booleans where integers are required, invalid parentage, and intervals outside
their parents fail validation. A trace has exactly one `run` root. Child
categories are `intelligence`, `gate`, `reconciliation`, and `wait`.
Outcomes are `success`, `error`, `timeout`, `cancelled`, or
`interrupted`.

Review spans may carry nonnegative `findings_reported` and
`actionable_findings`, attached only by validated finding ingestion. These
values are never estimated.

## Clock and accounting contract

UTC timestamps exist for correlation only. Every duration comes from
`time.monotonic_ns()`. Durable offsets are exact nanoseconds relative to the
root:

```text
duration_ns = end_offset_ns - start_offset_ns
```

Aggregation uses interval unions and exclusive attribution. Nested or
overlapping spans are never summed and presented as elapsed time. Reports keep
these concepts separate:

- active root makespan;
- calendar window across same-phase attempts;
- summed measured work;
- exclusive work by activity;
- failed and retry work;
- peak concurrency;
- orchestration/unmeasured remainder and measured gaps.

A delegated `wait` span mirrors the intelligence interval; it is not a second
unit of work and never inflates the report.

Kickoff traces prospectively cover sequential
`orchestration.setup`, `orchestration.planning`,
`orchestration.implementation`, `orchestration.acceptance`, and
`orchestration.close` stages. Re-entry increments an attempt. Validation
rejects missing stages, overlaps, unknown names, noncontiguous attempts,
out-of-order close, unregistered roles, bad role/wait joins, stale gate joins,
or accepted review passes without convergence counts.

## Runtime state, durability, and recovery

Open traces live outside the repository at:

```text
${AGENTIC_STARTER_EXECUTION_TELEMETRY_DIR:-${XDG_STATE_HOME:-$HOME/.local/state}/agentic-starter/execution-telemetry}/<repo-key>/<trace-id>/
```

Mutations take an exclusive lock. Files are written through same-directory
temporary files, flushed, fsynced, and atomically replaced. The durable
repository ledger is `EXECUTION_LOG.jsonl`; it receives only finalized,
canonical compact JSON.

Finalization requires a closed root, no open descendants, valid intervals,
valid scope ownership, and an exact privacy projection. Appending is
idempotent only for a byte-equivalent trace with the same id. Invalid UTF-8,
unterminated JSONL, or a conflicting prior trace fails before append.

Recovery may close descendants deepest-first and the root last only when the
stored and current boot identities are provably the same. A changed or unknown
boot leaves the trace incomplete. Recovery never invents cross-boot duration,
turns missing measurement into zero, or changes failure into success.

## Observed commands and failure truth

Observed commands preserve child stdout, stderr, and normalized status:

- exit 0 → success;
- positive exit → error;
- signal → interrupted;
- wrapper SIGINT/SIGTERM → cancelled;
- command/first-event/idle/hard deadline → timeout;
- spawn failure → error 127.

Cancellation and timeout terminate the process group and check for surviving
descendants. Telemetry failure is diagnosed independently and never masks the
underlying command result. Missing instrumentation may preserve a successful
child result, but it blocks a claim of complete execution evidence.

Kickoff gate commands run through `kickoff-evidence run-gate`, which binds
exact argv, selection rationale, before/after candidate identity, child result,
warning count, diagnostic digest, and the observed gate span.

## Privacy projection

Sanitization is projection, not redaction. Durable records have no generic
metadata bag and no place for prompts, responses, reasoning, command
arguments, environment, stdout/stderr, exception bodies, credentials,
absolute paths, home-relative paths, private source material, or arbitrary
prose. Runtime state may contain local roots needed to enforce ownership; it
never enters the durable projection. Fixtures are synthetic.

## Deterministic phase report

The accepted trace and every earlier finalized same-phase attempt feed a
chronological offline archive under `reports/execution/`. The default view
answers:

- what landed and how to try it;
- where active elapsed time went;
- which activities and automated checks were longest;
- which checks failed or repeated;
- whether Plan Review and Code Review converged;
- how much retry and failed work occurred;
- where instrumentation is absent;
- what phase is next and what the operator should do.

Default labels are Planning, Plan Review, Implementation, Code Review,
Automated Checks, and Orchestration / Unmeasured. Charts use readable minutes;
machine payloads and exact tables retain nanoseconds. Root wrappers, internal
ids, model names, harness names, and wait mirrors stay out of the default
presentation.

The archive is fully offline: data and presentation are separate files,
network access is denied by CSP, ECharts 6.1.0 and its Apache license are
vendored, and no fetch/XHR/WebSocket/eval or inline event handler is allowed.
The same ledger, accepted trace, and handoff must regenerate byte-identically.

The handoff schema is
`agentic_starter.execution_dashboard_handoff.v1`:

```json
{
  "schema": "agentic_starter.execution_dashboard_handoff.v1",
  "phase_id": "1.2",
  "what_just_landed": [{"title": "...", "detail": "..."}],
  "see_for_yourself": [{"title": "...", "steps": ["..."], "expected": "..."}],
  "coming_up_next": {"phase_id": "1.3", "title": "...", "summary": "..."},
  "recommended_steps": [{"title": "...", "detail": "...", "kind": "action"}]
}
```

`coming_up_next` may be null. Recommendation kinds are `action`,
`blocking`, and `ready`. The handoff contains only accepted outcomes,
concrete safe demos, applied next-phase state, and genuine prerequisites. It
never discusses commit state or embeds arbitrary HTML.

`bin/check-execution-dashboards` is a read-only gate. It validates static
assets, schema, digests, chronology, navigation, privacy, CSP, and
byte-identical regeneration. A report failure after trace finalization does not
rewrite accepted evidence, status, ripple, or the END block; a report-only
retry is idempotent.

When dashboard presentation changes, deterministic checks are insufficient.
Serve it with `bin/serve-execution-dashboard`, inspect archive and phase pages
at desktop and mobile widths, exercise trace selection, zoom, disclosure, and
navigation, compare charts with tables, and check the browser console. Blank
charts, clipped labels, misleading hierarchy, or DOM-only interactions fail.

## Phase-close ordering

Kickoff closes in this order:

1. unchanged approved candidate passes its complete final gate;
2. evidence and exact timing validate;
3. telemetry finalizes;
4. status and ripple update;
5. END log lands;
6. sanitized report regenerates and opens as the final tool action.

Late report failure never undoes steps 1–5.

## Related policies

- `policies/orchestration-evidence.md`
- `policies/role-timeouts.md`
- `policies/log-discipline.md`
- `policies/mechanistic-vs-intelligence.md`
- `policies/repo-relative-paths.md`

