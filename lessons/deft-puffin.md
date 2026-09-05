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

## Ledger note — 2026-09-05 (graduation considered and held)

**Assessed against the second-instance test and held.** The operator reviewed this entry on 2026-09-05 and declined to graduate it, on the test made binding in [`policies/lessons.md`](../policies/lessons.md) earlier the same day: a rule graduated from an incident must name one other instance it also catches, differing in tool, surface, or subject matter. The three occurrences differ only in which stage was being opened — same tool, same surface, same subject — and all three fall inside a two-day window in one donor project. Under the test that means the class is not yet identified, and the honest move is to file and wait rather than graduate a stretch.

This is a recorded judgment, not an oversight. Do not re-litigate whether the defect is real: it is, and the entry stands at three occurrences. The open question is narrower — whether a fourth sighting arrives that differs in tool or surface, which would identify the class and make the rule statable. A recurrence outside the original two-day window, or in a different repository, is the evidence to watch for.

The operator also considered graduating only the second half — validate each stage record at the transition where recovery is still local, independent of the naming question — and declined, keeping the entry whole.
