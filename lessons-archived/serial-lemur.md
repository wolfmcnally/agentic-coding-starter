---
slug: serial-lemur
title: Serialize commands that can recreate the shared project environment
status: rejected
scope: methodology
proposed_surface: skill
filed: 2026-08-25
closed: 2026-10-26
source: learn
occurrences:
  - date: 2026-08-25
    ref: "Donor A — a dependency probe recreated the shared environment while the runtime wrapper was qualifying it, producing a removal race"
---

Commands that can create, replace, or remove a shared project environment must
run serially. Parallelize read-only checks and independent tests, but first
qualify whether an environment-management command mutates the environment. A
shared environment is one write surface even when commands have different
names.

**Closed 2026-10-26 by sweep:** no new occurrence in sixty days. A new occurrence appended here reopens it.
