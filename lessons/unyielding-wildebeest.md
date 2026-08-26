---
slug: unyielding-wildebeest
title: Close an interrupted orchestration stage before opening recovery
status: candidate
scope: methodology
proposed_surface: test
filed: 2026-08-26
source: learn
occurrences:
  - date: 2026-08-26
    ref: "Donor A — recovery planning opened before interrupted implementation closed, invalidating an otherwise complete trace"
---

Recovery is sequential orchestration even when diagnosis starts immediately.
The current stage must reach a truthful terminal outcome before recovery opens;
otherwise stage ownership overlaps and the evidence plane should refuse close.
Make the transition ordering mechanical and test it at the boundary. A failed
trace stays failed; recovery re-proves the candidate in a fresh supported run.
