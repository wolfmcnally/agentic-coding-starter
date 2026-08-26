---
slug: patient-wombat
title: Poll a yielded nested command to a terminal exit
status: candidate
scope: methodology
proposed_surface: skill
filed: 2026-08-25
source: learn
occurrences:
  - date: 2026-08-25
    ref: "Donor A — a gate runner treated a yielded session's absent immediate exit code as failure and lost the complete diagnostics"
  - date: 2026-08-25
    ref: "Donor A — a nested command yielded, its orchestration scope ended without polling, and completion had to be reconstructed"
---

A command primitive that can yield returns a sum type: terminal result or live
session. On the live branch, poll the exact session inside the same durable
orchestration scope until terminal exit, retaining every output chunk. Only the
terminal branch may drive success or failure. An absent immediate exit code is
`in_progress`, never failure and never success.
