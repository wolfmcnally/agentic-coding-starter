---
slug: piecemeal-heron
title: Subset findings plus subset fixes create an unbounded review loop
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-26
source: learn
occurrences:
  - date: 2026-08-22
    ref: "Donor A — a resolved policy decision remained inconsistently stated; successive reviews named two sites, then eight more, before a complete enumeration was requested"
---

A reviewer reports the defects it found, and a fixer addresses the sites it
was given. Both behaviors are reasonable. Together they create a loop whose
length depends on how many sites the reviewer happens to enumerate per round.

The signal is a finding whose substance is already settled while its
consistency tail keeps reopening at new textual sites.

**The rule candidate:** when a correction spans an unknown number of sites,
first ask how many exist. Require the reviewer to return every remaining site
in one list, with an explicit inclusion criterion and enough quoted context to
distinguish relevant uses. An empty list must be stated explicitly.

Use mechanical searches as leads, not as substitutes for semantic judgment.
The complete-enumeration request converts a potentially unbounded review loop
into one bounded correction pass.
