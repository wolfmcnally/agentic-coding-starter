---
title: Test-Suite Value Governance
date: 2026-08-27
status: methodology
scope: Universal design for keeping every proof attributable, selecting fast feedback without weakening the full gate, and requiring local evidence before consolidation.
---

# Test-Suite Value Governance

A test suite is a proof estate, not an accumulating file count. Every proof must
have an owner, a contract, an oracle, and an explanation of the distinct failure
it detects. That attribution makes two otherwise-conflicting goals compatible:
the complete suite remains the authoritative close gate, while smaller lanes can
return fast feedback when the repository has proved that their selection is safe.

The repository owns a machine-readable proof estate. A deterministic manager
inventories executable test definitions and the structural proof surfaces in the
gate and hooks, validates their declared families, selects admitted fast lanes,
and reports the evidence used to govern them. An invalid declaration, an
unsupported runner, an unmapped changed path, or stale evidence widens to the
full suite. Selection failure therefore costs time; it never silently removes
coverage.

## Three lanes, two jobs

- **Vital** is a project-selected, continuously valuable feedback set. A family
  enters it only after the project records its contract, oracle, red witness,
  nearest overlap, and local effectiveness evidence.
- **Changed** maps the live candidate's changed paths to every applicable proof
  family. Legitimate overlaps select the union. Any changed path without a safe
  mapping widens the run to full.
- **Full** runs the complete repository suite and remains authoritative for both
  phase-close gates, pre-push custody, and the durable full-gate receipt.

Fast lanes optimize iteration, not acceptance. They may be used for focused
coder checks and revision loops, but neither one can replace the unchanged
approved-candidate gate or the final handoff-tree gate.

## Admission is local and empirical

The template standardizes the machinery and the evidence shape, not the answer.
Each recipient inventories its own tests, declares its own proof families, and
runs its own assay. It must not inherit another project's selectors, family
choices, timings, risk classes, defect corpus, mutation corpus, thresholds, or
audit judgments.

Before activating a fast lane, the recipient records locally admitted historical
defects and holdout mutants outside ordinary routine execution. Each evidence row
binds the candidate and proof-estate digest to the exact command, expected and
observed outcome, detecting family, output digest, and assay denominator. The
fast lane must detect every admitted case. A repository may choose no fast lane
at all; full-only is a valid governed state.

## Consolidation follows proof flow

Deletion is never inferred from age, duration, line count, or apparent overlap.
An audit traces test-to-test dependencies and every producer-to-consumer proof
flow first. A proof may be consolidated only when another retained proof owns the
same contract and oracle, its red witness still fails, downstream consumers keep
their required artifact, and the local effectiveness assay stays whole. Initial
adoption of this methodology retains the existing estate; reduction is a later,
separately reviewed local decision.

The repository's policy layer carries the operational obligations for this
design; this brief remains the rationale and recipient-neutral model.
