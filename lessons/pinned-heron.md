---
slug: pinned-heron
title: Use pinned tools and fail-fast shell composition in active evidence runs
status: candidate
scope: methodology
proposed_surface: skill
filed: 2026-08-25
source: learn
occurrences:
  - date: 2026-08-25
    ref: "Donor A — an unpinned evidence command refused an active run after an earlier projection failure silently left an empty artifact"
---

Once an evidence run pins its tool bundle, every later mutation or validation
for that run must invoke the pinned executable from the run directory. Compound
host-side evidence commands must enable fail-fast and pipe-failure handling,
validate every generated artifact before ingest, and stop before the manager is
called if generation failed. Read-only help may use the repository launcher
before a run; active-run state may not.
