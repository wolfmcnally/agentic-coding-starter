---
slug: sincere-jerboa
title: A timing-sensitive test needs a positive assertion that the dangerous window was entered
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-17
source: learn
occurrences:
  - date: 2026-08-17
    ref: "Donor A — a kill-mid-write atomicity test triggered its SIGKILL on a write count, which lands in the gap between writes, where a non-atomic writer is indistinguishable from an atomic one; the coder's own mutation probe caught it because the test PASSED against a deliberately non-atomic build. Repaired with a forced large operation plus an in-flight witness file"
---

A test that must catch a failure occurring only inside a narrow window
(mid-write, mid-flush, mid-transaction) silently degrades into a no-op if its
trigger can fire outside that window: the assertion then checks the survivor
of a *safe* interval and passes for correct and broken implementations alike.
The test keeps its name, its green check, and none of its meaning.

The rule: a timing-sensitive test must carry a **positive assertion that the
dangerous window was actually entered** — a witness artifact created inside
the window, a forced large operation that cannot complete before the trigger,
an instrumented fault point — and must fail when that witness is absent. The
verifying control is running the test against a deliberately broken
implementation and watching it fail; a kill-timing test that has never been
shown to catch the broken version is the verification-that-cannot-fail defect
on a timer.
