---
slug: space-quokka
title: Enforce export invariants before admitting irreversible work
status: candidate
scope: methodology
proposed_surface: bin
filed: 2026-10-21
source: user
occurrences:
  - date: 2026-10-21
    ref: "Donor A — role registration admitted a fresh local second attempt, the real reviewer ran and consumed its phase allowance, and later export rejected the missing local predecessor"
---

The first divergence was admission, before launch. Registration checked duplicate keys while export independently required contiguous local numbering. A phase-wide pass count was mistaken for local evidence continuity. An earlier real dispatch had returned an artifact that could not be ingested, so report-only carry could not recover its successor.

Prevention belongs at admission: apply the same prospective continuity invariant before publishing a handoff. Recovery must distinguish a proven launch from an accepted report, preserve the original rejected run, and attest original registration/dispatch/span/budget joins in a separate continuation without inventing a report or resetting an allowance. The correction tests both successful admission and refusal before dispatch, plus faithful historical recovery and deliberate evidence faults.
