---
slug: sincere-manul
title: When a record's verification is relaxed, ask immediately what is still being published on the strength of it
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-24
source: learn
occurrences:
  - date: 2026-08-14
    ref: "Donor A — a derived-metrics attach verb deferred its binding to the reader, so a wrong attempt wrote a record that succeeded and then made every later validation and timing summary refuse permanently, with no verb to withdraw it from an append-only ledger"
  - date: 2026-08-14
    ref: "Donor A — next round: a superseded derived record was verified on its span id alone (correctly — full recomputation fails by definition once the span is measured), but the timing summary kept publishing that entry's refusal class and cause in both formats with nothing on disk checked behind them, and its supporting directory became unreferenced at the moment of supersession, so a cleanup would have deleted it silently"
---

Relaxing a check is often correct. Both instances here were: a reader cannot
re-run a verification whose preconditions the new state contradicts, and insisting
otherwise reinstates the deadlock the relaxation removed. The mistake is not the
relaxation. **The mistake is failing to ask, in the same breath, what the system
still asserts on the strength of the check it just stopped performing.**

Both have the same shape. A record enters a state where part of its verification
no longer applies. The verification is correctly narrowed. And the *display* — the
projection, the summary, the operator-facing report — is not narrowed with it, so
the tool keeps printing claims that nothing on disk still supports. In the second
instance the supporting directory became unreferenced at exactly the moment the
check stopped consulting it, which is what turns "stale" into "deleted by the next
cleanup, silently."

**Note the asymmetry that makes this easy to miss.** Relaxing a check is a
visible, deliberate act with a written justification. Continuing to publish is an
*omission* — nobody edits the projection to keep asserting something; it simply
keeps doing what it already did. So the reasoning that gets recorded is entirely
about why the check may stop, and never about what stops being true.

**The remedy is a fixed pairing rather than vigilance.** A relaxation and a
publication are two halves of one change. When narrowing a verification, list
every field the system still emits about that record and, for each, name the check
that still stands behind it. A field with no surviving check either regains one —
usually a **middle floor**, the subset of the original verification the new state
does not contradict — or stops being published.

In the second instance the middle floor was four lines lifted from code that
already existed: the record's supporting row must still resolve uniquely, and its
artifacts must still be present at their recorded digests. Neither consults the
span or the accepted ingest, which are the only two things supersession
contradicts. That is the general shape — **the floor is what remains checkable,
not all-or-nothing.**

Directly load-bearing here: this repo's derived-metrics overlay and its
unmeasured-review-pass latch
([`policies/orchestration-evidence.md`](../policies/orchestration-evidence.md))
are exactly the kind of narrowed verification whose projections must be audited
alongside them.
