---
slug: cherubic-impala
title: One finding id carrying substituted evidence is several findings wearing one label — the immutable-field refusal is what makes it visible
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-24
source: learn
occurrences:
  - date: 2026-08-18
    ref: "Donor A — a plan-review finding was returned `open` across five rounds with its evidence rewritten to a *different* mechanism each time. Each was a real defect; none was the one the finding was raised on. Caught when the ingest refused on a different finding's immutable field, and chasing that refusal exposed the pattern"
  - date: 2026-08-18
    ref: "Donor A — same phase, code-review delta pass: the critic restamped required_outcome, authority, evidence, severity, and introduced_in on all eight findings at once, and the ingest refused again. Two different roles, same drift — the pressure is structural, not personal"
---

A finding whose stated requirement drifts can **always** be claimed unmet — there
is no fixed target to hit — so the loop cannot converge on its own terms. And the
work that genuinely closed earlier rounds is recorded as closing nothing, because
the label stayed `open`. Convergence metrics computed over such an id measure
nothing.

**What caught it: the ledger, not a human and not the reviewer.** An append-only
ledger with immutable fields earns its cost precisely here. Note also that **the
first refusal it emits is worth investigating past the field it names** — both
times, the named finding was not the interesting one.

**The correct shape**, applied as the repair:

1. Restore every immutable field from the ledger's stored values. The ledger is
   authoritative — not the latest artifact, which is the drifting thing.
2. Close the original finding against its own stated `required_outcome` if that is
   genuinely met.
3. Raise each newly-surfaced mechanism as its **own** finding, classified as
   newly-exposed-by-resolution.

Nothing is lost, the history stops misstating how many distinct problems there
were, and an orchestrator override of a reviewer's state assignment is recorded
rather than silent.

**Candidate rules.**

1. A review round returning a finding `open` must do so against that finding's
   **original** `required_outcome`. Still open for a different mechanism is a new
   finding, not a rewrite.
2. When an ingest refuses on an immutable field, audit **every** finding in the
   artifact against the ledger before re-ingesting. The named field is a symptom,
   not the diagnosis.
3. An orchestrator closing a finding the reviewer left open records the override
   and the replacement finding explicitly. Closing without a replacement is the
   failure this rule exists to prevent.
4. Two independent roles drifted identically, so the durable fix is probably in
   the **role dispatch contract** — state the immutability at the top of every
   review dispatch — rather than in per-role correction.
