---
title: "Incremental Orchestration With Candidate-Bound Assurance"
date: 2026-08-23
status: implemented
scope: Universal design for reducing repeated review and verification work while preserving independent criticism and separate implementation-candidate and handoff assurance gates.
---

# Incremental Orchestration With Candidate-Bound Assurance

The planner, plan reviewer, coder, code critic, orchestrator, and human remain
distinct functions. Efficiency comes from making their evidence incremental,
not from removing independent judgment: first reviews are complete, revision
reviews are bound to the causal delta, local verification is focused, and one
complete prescribed gate sequence proves the unchanged approved candidate.
Where a repository has adopted proof-estate governance, the deterministic
`vital` and `changed` lanes operate only over its validated retained estate and
make that focus attributable: each selected family names its contract and
oracle, overlapping mappings form a union, and uncertain impact widens to the
full retained suite. The initial whole-estate reset and periodic reassessment
are prerequisites, not work those fast lanes perform. The complete gate still
closes the candidate.

This design complements
[`deterministic-orchestration.md`](deterministic-orchestration.md). The current
prose orchestrator can use the evidence plane described here immediately. A
future deterministic workflow program can consume the same artifacts without
changing their meaning.

## 1. The optimization target

Repeated whole-context passes spend model time reconstructing facts that the
prior round already established. Repeated full test suites spend machine time
re-proving unaffected behavior while a change is still converging. A missing
terminal stream event can cause a valid role artifact to be discarded even
though the intelligence work finished.

The optimization target is therefore the marginal work after the first pass:

- retain independent first-pass planning and criticism;
- give findings stable identity and explicit state;
- describe revisions relative to the snapshot actually reviewed;
- bind every gate result to the exact candidate it exercised;
- distinguish execution, artifact, and transport outcomes;
- treat conspicuous, avoidable human wait as an optimization signal without
  weakening assurance;
- measure direct evidence rather than infer reassuring telemetry.

## 2. Candidate identity

A candidate is the complete reviewable Git working-tree state: tracked files
whether staged or unstaged, deletions, executable modes, symlink targets, and
nonignored untracked files. Staging a content-identical file does not create a
new candidate; changing any reviewable content does. A clean submodule
contributes its checked-out commit; a dirty submodule fails closed because the
superproject cannot safely summarize its unresolved inner candidate.

The candidate identifier hashes an ordered manifest of repository-relative
path, normalized mode, and content digest. It contains no file contents and
does not include ignored runtime state. Every review snapshot, finding
transition, context packet, and gate record names a candidate identifier.

## 3. Thin evidence plane

Each phase run owns four run-scoped records:

1. **Authority manifest.** The exact governing paths, content hashes, optional
   locators, and priority order. Original files remain authoritative.
2. **Change manifest.** Reviewed and current candidate identifiers, changed
   paths and content hashes, declared risk tags, selected tests and rationale,
   intentionally unchanged neighbors, authority drift, rebase reasons, and —
   on revision rounds — the coder's root-cause failure analysis.
3. **Finding ledger.** Stable finding id, severity, governing authority,
   evidence, affected paths, required outcome, introduction and resolution
   candidates, state, classification, and disposition.
4. **Gate ledger.** Command, candidate identifier, selection rationale, exit
   status, warning count, final-gate flag, and optional artifact digest.

These are deliberately thinner than a general event-sourcing platform. Their
job is to support exact revision handoffs and gate invalidation. Narrative
reports remain useful for judgment, but they are projections of the same facts
rather than the only copy.

## 4. Review protocol

The first plan review and first code critique run at the phase's declared
review intensity and batch all blockers. Each blocker receives a stable id.

A revision review begins with:

- unresolved findings and their prior evidence;
- the reviewed and current candidate identifiers;
- the causal path/hash delta;
- authority drift and explicit rebase reasons;
- selected verification mapped to the change;
- the coder's explanation of why the previous attempt produced the findings;
- prior gate records for the affected candidate.

The failure analysis travels with the packet so the reviewer can test the fix
against the coder's theory of the root cause rather than only its surface diff.

The reviewer decides prior findings first, then examines the changed dependency
surface for regression. New findings remain allowed and are classified as:

- `introduced-by-revision`;
- `newly-exposed-by-resolution`; or
- `missed-in-full-pass`.

Finding states are:

```text
open → addressed → verified → closed
  ↘ blocked-owner
  ↘ rejected-with-evidence
  ↘ superseded
```

A closed, verified, or rejected finding may reopen only explicitly, and every
reopening is counted. The loop continues while blocking findings materially
advance and no equal-or-greater regression replaces them. Recurrence,
oscillation, an unresolved authority question, or two rounds without reduced
severity or uncertainty escalates. The ten-cycle cap remains a deterministic
runaway backstop.

## 5. Fail-closed review rebasing

Revision review widens back to a complete pass when:

- scope or governing authority changed;
- a revision introduces a new risk class;
- a public API, persisted format, security boundary, concurrency boundary, or
  irreversible transition changed;
- the change disperses beyond the surface reviewed previously;
- a finding invalidates a phase acceptance claim outside the prior delta; or
- compaction, venue failure, or missing evidence destroys trustworthy
  continuity.

Thresholds are not guessed in the universal template. A project may calibrate
size or dispersion thresholds from local evidence, but uncertainty always
rebases rather than silently narrowing review.

## 6. Verification ladder

Verification has four levels, the first three candidate-bound and the fourth
bound to the actual handoff tree:

1. **Edit loop.** Run the smallest behavioral test or proof capable of
   falsifying the current edit.
2. **Revision close.** Run affected suites and structural or static checks
   selected from the change surface. Record why the selection is sufficient;
   indeterminate impact fails closed to broader verification.
3. **Implementation-candidate close.** After code-critic approval, run the phase's complete
   prescribed sequence and the repository's authoritative full gate once
   against the unchanged candidate.
4. **Handoff close.** Finalize evidence, apply only the tracked close writes
   declared by the protocol, then run the authoritative full gate again as a
   bare command against the actual tree handed to the user. No tracked write
   follows a successful handoff gate.

Any relevant candidate change invalidates the implementation-candidate gate.
Either gate mutating the candidate is itself a failure. A failed handoff gate
reopens the uncommitted close: correct the tree, re-establish candidate-bound
review/evidence as required, and repeat both gates. Optional, paid, stochastic,
or human-only diagnostics remain governed by phase acceptance.

## 7. Execution protocol

Delegated execution has three independent signals:

- child-process terminal status;
- fresh artifact presence and role-shape validity;
- terminal event-stream completeness.

Ordinary success requires all three. A successful child with a fresh artifact
but an incomplete stream becomes `completed-unverified-protocol`. The artifact
is preserved and may be accepted only after explicit role-shape, evidence, and
candidate verification. Missing or stale artifacts, invalid role shape,
nonzero children, and timeouts remain failures.

This classification prevents transport bookkeeping from automatically buying
another model pass without weakening the success contract.

## 8. Direct measurement

The evidence plane records facts it directly observes:

- revision-packet bytes and source hashes;
- findings by state and severity;
- reopened and missed-in-full-pass findings;
- candidate identities and changed-path counts;
- gate selections, results, warnings, and artifact digests;
- child, artifact, and stream protocol states.

It does not infer model reasoning time, repository-reading time, idle causes,
or critical-path attribution when the venue does not emit those facts.

## 9. Exact execution truth and phase report

One append-only trace now records the complete kickoff execution: root, stage,
role, wait, tool, and gate spans share stable identifiers and monotonic clocks.
Evidence records join to those identifiers rather than estimating elapsed time
from artifacts or messages. Phase close fails closed when a required role,
wait, or gate cannot be joined to the trace.

Time parked awaiting operator input is deliberately not another trace span. A
separate phase ledger records every open/close interval and the overlap-safe
union total. Same-boot duration uses the monotonic clock and is exact;
cross-boot duration uses UTC and is visibly labeled non-exact. An open or
malformed interval fails close rather than becoming zero.

The timing projection distinguishes active makespan, calendar duration, summed
work, exclusive work, peak concurrency, failed/retry time, and uncovered gaps.
Active makespan is the union of active intervals, so parallel work is not
double-counted; wait spans remain explicit and do not silently become work.
Interrupted writers spool locally and reconcile idempotently before final
validation.

After acceptance, a privacy projection removes prompts, raw output, absolute
paths, and environment data. A deterministic generator commits a fully offline
HTML phase report plus aggregate index under `reports/execution/`. The report
uses vendored assets, a restrictive content-security policy, responsive
layouts, and build-gate freshness checks. Opening the validated report is the
final kickoff handoff; a late presentation failure is reported but does not
rewrite already-valid acceptance evidence or phase status.

## 10. Deliberate exclusions

The universal template does not yet add:

- a compiler for every initial role context;
- automatic language-agnostic dependency selection;
- incremental mutation caching;
- nested span or critical-path inference;
- conditional removal of independent roles beyond the existing mechanical
  review lane;
- fixed wall-clock thresholds, automatic hotspot classification, or a
  general ROI-learning loop;
- numeric thresholds without local calibration; or
- named assurance profiles before a project needs more than one.

Those additions remain eligible when direct evidence shows that their
functional return exceeds their complexity and assurance risk.

Human wall-clock efficiency does not require those systems. It is an ambient
judgment rule: agents notice when an operation materially dominates the work
and briefly assess only reasonably apparent, substantial, high-leverage,
low-risk improvements. Common seams are independent units running serially,
invariant setup repeated per unit, complete suites repeated during iteration,
and unchanged work recomputed without an input-identity reason. Existing safe
acceleration may be used; a nontrivial out-of-scope improvement is surfaced
once and deferred. Marginal optimization, open-ended profiling, and any
reduction in correctness, coverage, determinism, review independence, or final
assurance are explicitly out of scope.

## 11. Acceptance properties

The design is realized when:

- candidate identity changes for every reviewable content change and remains
  stable across staging-only changes;
- evidence schemas and finding transitions fail closed under malformed or
  stale input;
- revision packets are deterministic projections with disclosed omissions;
- authority drift and named risk boundaries force a review rebase;
- gate records reject stale candidates;
- the authoritative full gate still closes every completed phase; and
- exact timing summaries derive from trace joins and interval unions, and every
  completed phase produces a deterministic, sanitized, offline HTML report;
- obvious high-leverage wall-clock improvements are considered
  proportionally without numeric tripwires or assurance loss; and
- incomplete streams never become ordinary success, while independently valid
  artifacts are not discarded automatically.
