# Policy: Execution Telemetry and Phase Reports

Authority mode follows [four-canonical-agents.md](four-canonical-agents.md). Product primary mode uses independent advice and primary acceptance; delegated product mode retains approval verdicts and bounded revision loops. References below to reviewer assent or mandatory re-review govern delegated work only. Required objective gates and truthful evidence apply in both modes. All methodology work, including teach/learn, follows [review-lanes.md](review-lanes.md): one-shot by the primary, no delegated production or review, and commit/fast-forward-push authority after required checks.

Kickoff execution timing is exact, candidate-bound, privacy-bounded, and machine-owned. It measures elapsed work; it does not replace narrative logs, status events, gate evidence, or human judgment about whether an optimization is worthwhile.

## Exact schemas

Durable records use closed schemas:

- `agentic_starter.execution_span.v1` for one closed span;
- `agentic_starter.execution_trace.v1` for one finalized trace bundle; and
- `agentic_starter.operator_park_event.v1` for a phase-level required-user-input open or close event.

Unknown keys or enum members, malformed identifiers, missing required values, booleans where integers are required, invalid parentage, and intervals outside their parents fail validation. A trace has exactly one `run` root. Child categories are `intelligence`, `gate`, `reconciliation`, and `wait`. Outcomes are `success`, `error`, `timeout`, `cancelled`, or `interrupted`.

Operator-park events carry only event kind, UUID, phase id, stable reason code, UTC timestamp, boot identity, and monotonic reading. Stable reasons are `approval`, `decision`, `manual-check`, `environment-action`, `acceptance`, and `required-input`. Question text, responses, prompts, paths, and arbitrary prose have no schema field.

Review spans may carry nonnegative `findings_reported` and `actionable_findings`, attached only by validated finding ingestion. These values are never estimated. `findings_reported` is the number of validated entries in that pass's Finding Evidence block; `actionable_findings` is the number of findings in the **whole merged ledger** — not the batch alone — whose id carries that review namespace and whose post-reconciliation state is still `open`, `addressed`, or `blocked-owner`. An approved empty block records zero. Final timing validation rejects an accepted review pass without both integers, unless the run carries a recomputed derived-metrics overlay for it (`policies/orchestration-evidence.md § Derived convergence metrics for a refused batch`); the span itself is never written after the fact.

## Clock and accounting contract

Within a trace, UTC timestamps exist for correlation only. Every span duration comes from `time.monotonic_ns()`. Durable offsets are exact nanoseconds relative to the root:

```text
duration_ns = end_offset_ns - start_offset_ns
```

Aggregation uses interval unions and exclusive attribution. Nested or overlapping spans are never summed and presented as elapsed time. Reports keep these concepts separate:

- active root makespan;
- calendar window across same-phase attempts;
- summed measured work;
- exclusive work by activity;
- failed and retry work;
- peak concurrency;
- orchestration/unmeasured remainder and measured gaps.

A delegated `wait` span mirrors the intelligence interval; it is not a second unit of work and never inflates the report.

Phase-level **operator parks** are separate from traces and `wait` spans. Open a park immediately before stopping for required user input; close it only when a response satisfies that wait. A park may span finalized traces. When open and close share a proven boot identity, its duration is exact monotonic time. Across a reboot, its duration is UTC calendar time labeled **non-exact**. If the UTC order is invalid, the duration is unavailable—not zero. Per-phase totals are interval unions; overlapping parks never double-count.

Kickoff traces prospectively cover sequential `orchestration.setup`, `orchestration.planning`, `orchestration.implementation`, `orchestration.acceptance`, and `orchestration.close` stages. Re-entry increments an attempt. Validation rejects missing stages, overlaps, unknown names, noncontiguous attempts, out-of-order close, unregistered roles, bad role/wait joins, stale gate joins, or accepted review passes without convergence counts.

## Runtime state, durability, and recovery

Open traces live outside the repository at:

```text
${AGENTIC_STARTER_EXECUTION_TELEMETRY_DIR:-${XDG_STATE_HOME:-$HOME/.local/state}/agentic-starter/execution-telemetry}/<repo-key>/<trace-id>/
```

The append-only operator-park ledger and its recoverable open-state files live under the same external `<repo-key>/` root. An event is appended and fsynced before the open-state cache is written; a missing cache is reconstructed from the ledger. Duplicate same-identity opens and closes are idempotent. Conflicting, unmatched, or multiply-open state fails closed.

Mutations take an exclusive lock. Files are written through same-directory temporary files, flushed, fsynced, and atomically replaced. The durable repository ledger is `EXECUTION_LOG.jsonl`; it receives only finalized, canonical compact JSON.

Finalization requires a closed root, no open descendants, valid intervals, valid scope ownership, and an exact privacy projection. Appending is idempotent only for a byte-equivalent trace with the same id. Invalid UTF-8, unterminated JSONL, or a conflicting prior trace fails before append.

Recovery may close descendants deepest-first and the root last only when the stored and current boot identities are provably the same. A changed or unknown boot leaves the trace incomplete. Recovery never invents cross-boot duration, turns missing measurement into zero, or changes failure into success.

## Observed commands and failure truth

Observed commands preserve child stdout, stderr, and normalized status:

- exit 0 → success;
- positive exit → error;
- signal → interrupted;
- wrapper SIGINT/SIGTERM → cancelled;
- command/first-event/idle/hard deadline → timeout;
- spawn failure → error 127.

Cancellation and timeout terminate the process group and check for surviving descendants. Telemetry failure is diagnosed independently and never masks the underlying command result. Missing instrumentation may preserve a successful child result, but it blocks a claim of complete execution evidence.

Kickoff gate commands run through `kickoff-evidence run-gate`, which binds exact argv, selection rationale, before/after candidate identity, child result, warning count, diagnostic digest, and the observed gate span.

## Privacy projection

Sanitization is projection, not redaction. Trace and operator-park records have no generic metadata bag and no place for prompts, responses, reasoning, command arguments, environment, stdout/stderr, exception bodies, credentials, absolute paths, home-relative paths, private source material, or arbitrary prose. Runtime state may contain local roots needed to enforce ownership; it never enters the durable projection. Fixtures are synthetic.

## Phase identity

Report selection, archive paths, history filters and operator-input park records use the exact same phase id. A safe phase id is at most 122 characters (the suffix of the bounded `phase.<id>` operation): a dotted numeric id, or a lowercase letter-led name containing lowercase letters, digits, underscores, plus signs and hyphens, optionally separated by nonempty dots. Path separators, whitespace, empty dot segments and traversal names refuse. Uppercase named ids refuse rather than aliasing existing report or park-state files on case-insensitive filesystems. Numeric ids sort by integer components; named ids sort lexically after numeric ids when completion timestamps tie. A different phase never supplies the accepted trace or handoff. Named ids do not alter review budgets, input-wait ownership or accepted records.

## Deterministic phase report

The accepted trace and every earlier finalized same-phase attempt feed a chronological offline archive under `reports/execution/`. The default view answers:

- what landed and how to try it;
- where active elapsed time went;
- which activities and automated checks were longest;
- which checks failed or repeated;
- whether Plan Review and Code Review converged;
- how much retry and failed work occurred;
- where instrumentation is absent;
- every interval and the union total spent awaiting required user input, including an exact/non-exact basis;
- what phase is next and what the operator should do.

Default labels are Planning, Plan Review, Implementation, Code Review, Automated Checks, Awaiting User Input, and Orchestration / Unmeasured. Work the primary does inline carries the same labels as delegated work: when a trace has no planner or coder role span, the exclusive time of its planning or implementation stage is Planning or Implementation, because the stage is the work. Stage time around a delegated role is coordination and is shown as such. The activity breakdown accounts for the whole recorded execution; no measured stage is dropped from it. Operator parks remain separate from both work and unmeasured orchestration. Charts and tables use readable durations; machine payloads retain nanoseconds, which the report never displays. Root wrappers, internal ids, model names, harness names, and wait mirrors stay out of the default presentation.

The archive is fully offline: data and presentation are separate files, network access is denied by CSP, ECharts 6.1.0 and its Apache license are vendored, as are three Font Awesome Free icons with their license, and no fetch/XHR/WebSocket/eval or inline event handler is allowed. The same trace ledger, accepted trace, operator-park summary, and handoff must regenerate byte-identically.

The handoff schema is `agentic_starter.execution_dashboard_handoff.v2`:

```json
{
  "schema": "agentic_starter.execution_dashboard_handoff.v2",
  "project": "Example Project",
  "phase_id": "1.2",
  "what_just_landed": [{"title": "...", "detail": "..."}],
  "see_for_yourself": [{"title": "...", "steps": ["..."], "expected": "..."}],
  "coming_up_next": {"phase_id": "1.3", "title": "...", "summary": "..."},
  "recommended_steps": [{"title": "...", "detail": "...", "kind": "action"}]
}
```

`project` is the project's name as its own README titles it, at most 80 characters; it heads the report so a reader with several projects' reports open can tell them apart. `coming_up_next` may be null. Recommendation kinds are `action`, `blocking`, and `ready`. The handoff contains only accepted outcomes, concrete safe demos, applied next-phase state, and genuine prerequisites. It never discusses commit state or embeds arbitrary HTML.

`bin/check-execution-dashboards` is a read-only gate. It validates static assets, schema, digests, chronology, navigation, privacy, CSP, and byte-identical regeneration. A report-generation failure after trace finalization blocks the handoff gate; repair or regenerate the current uncommitted close and retry idempotently. A browser-open failure after the handoff gate is presentation-only and does not change tracked artifacts.

When dashboard presentation changes, deterministic checks are insufficient. Open a phase page as a local file first, the way a report is normally opened: a browser applies stricter rules to files than to a server, and an asset that loads when served can be refused from a file. Then serve it with `bin/serve-execution-dashboard`, inspect archive and phase pages at desktop and mobile widths in both light and dark color modes, exercise run selection, the timeline slider, disclosure, and navigation, compare charts with tables, and check the browser console. Blank charts, clipped labels, misleading hierarchy, or DOM-only interactions fail.

Four presentation rules are fixed (operator ruling, 2026-10-09). The heading, page title and archive name the project. A control at the top cycles the color mode through System, Light and Dark, and a printed report is always light. The run menu appears only when a phase took more than one run, labels each run for what it is, and says why one would look at a single run. No chart responds to the wheel or a trackpad scroll: the page scrolls, and the timeline zooms only by its slider.

## Phase-close ordering

Kickoff closes in this order:

1. unchanged approved implementation candidate passes its changed-path gate;
2. evidence and exact timing validate;
3. telemetry finalizes;
4. status, ripple, and lessons update;
5. END log and sanitized report land;
6. bare `./bin/check all` passes against the actual handoff tree and writes its ignored receipt;
7. delivery — the ordinary commit and non-force push of gate-proved work, unless the operator restricted it ([`human-in-the-loop.md`](human-in-the-loop.md)) — and the read-only opening of the already-generated report may follow.

No tracked write follows step 6; step 7 changes no tracked content. A step-5 or step-6 failure reopens the current uncommitted close; completion is not reported until the handoff gate passes.

## Cross-boot interruption observation

`execution-telemetry interrupt --trace-id <old> --successor-trace-id <new> --custody-evidence <file>` records a private, append-only observation after independently verified custody. It requires matching open work/scope, a distinct current-boot successor, a provably changed boot and an attributable custody and candidate-lineage statement. It binds the old trace/span byte snapshot, old and observed boot identities, successor identity and retained custody bytes. Identical requests are idempotent; changed originals, lineage or successor conflict. It never writes old span bytes, terminal events or the finalized ledger. Completion, exit and duration of old open work remain unknown, not success or zero. Same-boot recovery and operator-park accounting are unchanged.

The JSON custody file has exactly `source`, `reference` and `candidate_lineage`, all nonempty strings. Each is the caller's stated claim. Verify through authorized evidence that the old run's processes have stopped and its resources are released before invoking; the record authenticates no user and probes no processes. Keep this private runtime record out of public timing projections. Consumers retain the original incomplete run and initialize fresh durable successor evidence through their owning session; observation alone is not acceptance or permission to reuse missing advice. Missing originals remain missing, with consumed review budgets preserved.


## Related policies

- `policies/orchestration-evidence.md`
- `policies/role-timeouts.md`
- `policies/log-discipline.md`
- `policies/mechanistic-vs-intelligence.md`
- `policies/repo-relative-paths.md`
