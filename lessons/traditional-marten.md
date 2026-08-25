---
slug: traditional-marten
title: A performance fixture that omits accumulated state green-lights the path the real workload fails
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-24
source: learn
occurrences:
  - date: 2026-08-11
    ref: "Donor A — a synthetic fixture reported a 7.2x speedup while the live workload achieved 2.9x; the dominant cost was a per-item rescan of accumulated state that a fixture with no accumulated state cannot exhibit at all. Five review rounds and 784 passing tests missed it; the live run found it in under fifteen minutes"
  - date: 2026-08-15
    ref: "Donor A — the correctness variant of the same shape: six live-data defects passed full review and synthetic gates, then each refused only against the real workload's accumulated history"
---

A phase's acceptance carried both a fixture-scale throughput criterion and a
live-execution criterion. The synthetic fixture — a handful of tiny inputs, no
accumulated ledger, no prior state, synthetic delays dominating runtime —
comfortably passed. The same code on the real corpus fell by more than half,
because the dominant cost was work proportional to **accumulated state**, which
the fixture held at zero.

**The generalizable shape: a performance fixture measures whatever dimension it
varies.** If the quantity that grows in production — corpus size, ledger length,
index cardinality, queue depth, file count — is held at zero, the fixture is
*structurally incapable* of failing for the reason production will. It then does
worse than nothing, because it converts an untested assumption into a green gate.

**The correctness variant is the same defect without the stopwatch.** Behavior
that is correct against a fresh fixture can refuse against real accumulated
history — duplicate members, partially-failed prior work, cross-writer
idempotency, bookkeeping from earlier runs. A synthetic gate cannot see any of it.

Candidate rule: **a phase whose acceptance claims a throughput or scaling factor
must state which quantity its benchmark holds fixed and which it varies**, and the
reviewer checks that the varied dimension is the one that grows in production.
Related but distinct from the false-green comparators in
[`policies/acceptance-empirical.md`](../policies/acceptance-empirical.md) — this is
a benchmark that is *correctly* measuring the wrong dimension.

Kin to `rustling-frog` (name the cost class at the seam): that entry is about the
code shape that produces the cost; this is about the fixture that cannot detect it.
