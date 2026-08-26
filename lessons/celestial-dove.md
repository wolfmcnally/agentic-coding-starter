---
slug: celestial-dove
title: A silence resolved in prose needs its own named test row
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-26
source: learn
occurrences:
  - date: 2026-08-21
    ref: "Donor A — a behavioral ownership decision appeared in Architecture Decisions but nowhere in Testing Strategy, leaving its branch entirely uncovered"
---

A plan resolved a contract silence with an explicit architectural decision.
The decision had behavioral consequences, but the testing section named no
criterion for them. The implementation therefore shipped with the relevant
branch structurally unreachable from the test fixtures.

The plan and the suite both looked complete. The gap sat between two correct
sections: the decision existed in prose, and the tests correctly covered every
row they listed. Nothing required the two inventories to join.

Counts did not expose the gap because neighboring tests mentioned the same
error types for unrelated reasons. Only tracing the resolved silence to a
named behavioral criterion showed that no test exercised it.

**The rule candidate:** every contract silence resolved with behavioral
consequence receives its own named acceptance criterion. Record an explicit
mapping from each resolved silence to the test or manual check that binds it.
