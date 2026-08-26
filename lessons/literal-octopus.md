---
slug: literal-octopus
title: Interpret instrument exit codes from their contract
status: candidate
scope: methodology
proposed_surface: test
filed: 2026-08-23
source: learn
occurrences:
  - date: 2026-08-23
    ref: "Donor A — a merge helper recognized only exit 1 as conflict even though positive statuses counted conflict regions"
---

An orchestration helper collapsed a count-valued exit protocol into boolean
semantics: zero meant clean, one meant conflict, and larger values were treated
as instrument failure. Multi-conflict output was therefore complete and usable
but misclassified.

Before routing on an external tool's status, qualify the full status domain
from its documented behavior and pin representative nonzero values in a test.
A wrapper may normalize a count into its own enum, but must not invent binary
semantics merely because most Unix commands use them.
