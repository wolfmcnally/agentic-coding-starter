---
slug: quiet-kestrel
title: An optional artifact argument names an existing input, not an output sink
status: candidate
scope: methodology
proposed_surface: skill
filed: 2026-08-24
source: learn
occurrences:
  - date: 2026-08-24
    ref: "Donor A — a gate replay passed nonexistent artifact paths, so diagnostics were never captured there"
  - date: 2026-08-24
    ref: "Donor A — setup repeated the nonexistent-output assumption before the existing-input semantics were rechecked"
---

An optional artifact path may be supporting input for a gate record; that does
not make it a stdout or stderr destination. Before passing one, verify the file
already exists and that a separate explicit mechanism created it from complete
diagnostics. If no artifact exists, omit the argument. Never infer output
capture from an option's name; inspect the command contract.
