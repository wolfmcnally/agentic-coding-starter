---
slug: inventive-swallow
title: Reserve retry headroom inside bounded live-source request budgets
status: rejected
scope: methodology
proposed_surface: skill
filed: 2026-08-26
closed: 2026-09-29
source: learn
occurrences:
  - date: 2026-08-26
    ref: "Donor A — a sub-budget equaled its happy-path denominator, so one transient disconnect exhausted the stage despite unused global headroom"
---

A bounded live-source check needs two numbers: the deterministic happy-path
denominator and a retry-capable sub-budget inside the authorized global cap.
Making them equal turns the first transient network failure into apparent cap
exhaustion even when the global envelope still has room.

Derive stage budgets from the unchanged global cap after reserving every other
stage's maximum. Keep the global cap authoritative while permitting the stage
to use remaining authorized headroom for its bounded retry policy.

Rejected 2026-09-29 by the operator as not methodology-specific: its remedy is sound general engineering or source-project practice, but it would change none of this template's rules, roles, skills or tooling, which is what `scope: methodology` requires (`policies/lessons.md`).
