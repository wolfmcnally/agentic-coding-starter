---
slug: staged-heron
title: Archive format upgrades need a mixed-version migration path
status: candidate
scope: methodology
proposed_surface: bin
filed: 2026-08-23
source: learn
occurrences:
  - date: 2026-08-23
    ref: "Donor A — per-member rewrites regenerated an index that assumed every still-archived payload already had the new field"
---

A per-member renderer regenerated an archive-wide index after each rewrite.
The new summarizer required a field old members lacked, so normal sequential
upgrade failed in every intermediate mixed-version state.

Provide either a backward-readable summarizer for the bounded migration window
or a two-phase bulk rewrite that stages every member and atomically swaps only
after the complete index validates. Per-member mutation plus an all-members-new
invariant is not a safe migration path.
