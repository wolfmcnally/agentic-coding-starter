---
slug: optimal-echidna
title: A battery that aborts on first failure reports a partial result in the grammar of a complete one
status: candidate
scope: methodology
proposed_surface: test
filed: 2026-08-17
source: learn
occurrences:
  - date: 2026-08-16
    ref: "Donor A acceptance — a mutation battery reported 1 of 512 rows failing with 294 rows unexecuted; a keep-going re-run of the same candidate found 5"
---

A fail-fast acceptance battery printed a one-failure verdict whose summary
line read like a verdict over the whole battery, while 57% of the rows had not
run at all. Re-run with keep-going semantics, the same candidate yielded five
failures. The default under-reported by 5×.

This is the same defect class as a verification that can only say "good": the
output is not *wrong* about what it checked, it is *silent* about what it
skipped, and the two are indistinguishable to a reader. A carrying acceptance
gate must state its coverage, not just its verdict — at minimum, refuse to
render a row-count verdict when rows were not executed.

Fail-fast has a place: on a repair loop, a fast first signal is the point. The
split the donor landed on: acceptance runs the whole battery; repair may
fail-fast; and any abort summary states exactly how many rows were proved and
how many were not executed, so the reader can see the claim's boundary.

Locally relevant: this repository's `bin/check all` is fail-fast sequential —
a lint failure means the test and policy gates never ran, and nothing in the
output says so.
