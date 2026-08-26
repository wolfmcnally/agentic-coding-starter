---
slug: blue-crocodile
title: Split a review by surface when the changed material exceeds one reviewer's context
status: candidate
scope: methodology
proposed_surface: skill
filed: 2026-08-26
source: learn
occurrences:
  - date: 2026-08-21
    ref: "Donor A — two complete review attempts died without verdicts; two disjoint surface reviews completed quickly and found six defects"
---

Two review attempts failed even after the second stayed within its stated
repository boundary. The changed surface, its tests, a frozen referent, the
plan, and the revision packet simply exceeded what one reviewer could hold.
Repeatedly reopening material already read was the visible sign that the
reviewer was losing its working context.

Splitting by surface worked immediately: one review owned implementation
behavior against the referent, while another owned tests against behavior.

Mechanics worth preserving:

- Give each reviewer disjoint finding-id ranges.
- State exactly which surface each verdict covers.
- Require every surface verdict before proceeding.
- Tell each reviewer what the other owns and forbid duplicate review.
- Name what the orchestrator already proved mechanically so judgment stays on
  the material that reading must establish.

The trigger is changed-surface volume, not the number of failed attempts.
Partition before repeated context loss turns a complete review into a skim.
