---
slug: divided-magpie
title: A role brief that grants a denied capability will be obeyed into failure
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-26
source: learn
occurrences:
  - date: 2026-08-22
    ref: "Donor A — a read-only role brief later instructed the role to write its output file; the sandbox refused and the completed revision was lost"
---

A role brief opened by denying write capability and later instructed the role
to write its completed artifact directly. The role followed the more specific,
later imperative, the sandbox refused it, and the completed revision never
reached the orchestrator.

The contradiction had been introduced as a repair for an earlier unexplained
failure. Its author guessed that final-message capture was unreliable without
checking successful traces that already showed the real mechanism. A guessed
cause became a binding instruction and contradicted the brief's own constraint.

**The rule candidate:** before adding an imperative to a delegated role brief,
check every statement the brief already makes about that capability. Treat the
brief as one satisfiability problem, not a sequence of locally plausible
instructions.

When a failure's mechanism is unknown, preserve that uncertainty. An honest
unknown costs the next role less than a confident instruction for a mechanism
that never existed.
