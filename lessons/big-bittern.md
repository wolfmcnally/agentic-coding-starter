---
slug: big-bittern
title: Before a plan removes a repeated step, check that the repetition is accidental and measure what it costs
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-11-10
source: user
occurrences:
  - date: 2026-11-10
    ref: "this template — an operator-approved plan for the build gate listed 'run the log check once' because the full gate runs it before the tests and again inside the policy lane; at implementation the second run turned out to be a deliberate final revalidation with its own admitted proof, and the lane timing added in the same change measured the check at under one second"
---

The plan was written from reading the gate script, where the same check appears twice, and from a tally of gate runs that could not show per-lane time. Both made the repetition look like waste. Neither showed why it was there.

Two cheap checks would have settled it before the plan was approved. Searching the tests for the step showed an existing proof whose failure message names the loss of final log validation, which is a statement that the repetition is intended. Timing the step showed there was nothing to save. The item was dropped at implementation and recorded as a scope departure, so the cost was small, but the operator approved a plan line that should not have been in it.

**A plan line that removes or merges a repeated step states the evidence that the repetition is accidental (no test or comment protects it) and the measured time it takes.** When either is unknown, the plan says so and makes the removal conditional on the measurement instead of listing it as decided.
