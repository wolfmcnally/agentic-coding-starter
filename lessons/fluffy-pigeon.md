---
slug: fluffy-pigeon
title: Price a removal by what its tests use it for, not by who documents it
status: candidate
scope: methodology
proposed_surface: skill
filed: 2026-10-26
source: user
occurrences:
  - date: 2026-10-26
    ref: "this template, full sweep — two evidence-tool correction routes were presented to the operator for removal as dead because no prose described them; the operator approved; the trial removal failed six test cases in three unrelated proofs, because the test helper used one route as its default precisely to start a run that needs no role evidence. The decision was reverted, re-asked with the measured cost, and the operator chose to document the routes instead"
---

A removal's cost is set by everything that depends on the thing removed, and tests are dependents. "No instruction mentions it" measured the wrong population: the routes had no readers in prose and a heavy reader in the test fixtures, where they served as the cheap way to isolate unrelated behavior from role bookkeeping.

**Before presenting a removal as a decision, search the tests and fixtures for uses of the thing being removed, and price the rewrite of any proof that leans on it.** A trial removal followed by the affected test files is cheap and settles it. The decision then carries its real cost, and the operator is not asked twice.

Second instance this would catch: retiring a configuration key, schema field or CLI flag that no document mentions but that fixtures set to reach an unrelated branch.
