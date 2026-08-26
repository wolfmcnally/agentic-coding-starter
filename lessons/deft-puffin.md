---
slug: deft-puffin
title: Treat telemetry operation names as schema keys
status: candidate
scope: methodology
proposed_surface: skill
filed: 2026-08-24
source: learn
occurrences:
  - date: 2026-08-24
    ref: "Donor A — implementation work used a descriptive near-synonym, so the required telemetry join was absent until explicit reconciliation"
  - date: 2026-08-24
    ref: "Donor A — acceptance used the wrong operation/category pair, forcing a truthful failed trace and corrective reseal"
  - date: 2026-08-25
    ref: "Donor A — another implementation stage used a near-synonym and required a genuine close-time reconciliation"
---

Telemetry operation names are validated contract keys, not descriptive labels.
Two labels can mean the same thing to a reader while remaining different schema
members, leaving a required join unsatisfied.

Before opening a stage, obtain its operation from the run's required-operation
inventory or canonical literal. Validate each just-closed span at the transition
where recovery is still local instead of waiting for the final evidence gate.
