---
slug: horned-vicugna
title: Fixing an instance without sweeping its siblings leaves the defect next door
status: candidate
scope: methodology
proposed_surface: skill
filed: 2026-08-26
source: learn
occurrences:
  - date: 2026-08-21
    ref: "Donor A — a coder fixed the one test named by review while an adjacent test retained the identical false-coverage pattern"
---

A review finding identified a test whose aggregate coverage assertion could
pass while one required item was never exercised. The coder fixed that test.
An adjacent test, written with the same helper and the same structure, retained
the identical defect and consumed another complete review round.

The line named in a finding is evidence of a pattern, not proof that the
pattern occurs once.

**The rule candidate:** after fixing a finding, sweep every plausible sibling:
the same file, the same helper's callers, adjacent tests, and the same idiom in
the affected module. Report the result whether the sweep finds more instances
or clears them with reasons.

The correction is complete only after everything it implicates has been
examined. A negative sweep is useful evidence because it proves the class, not
only the reported site, was considered.
