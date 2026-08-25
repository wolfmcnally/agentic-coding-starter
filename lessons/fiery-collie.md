---
slug: fiery-collie
title: Focused test selection is a performance choice that trades away exactly the coverage cross-file regressions live in
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-24
source: learn
occurrences:
  - date: 2026-08-18
    ref: "Donor A — a venue-scoping repair. Both the coder's focused selection and the orchestrator's named the same single test file (100 green). The regression lived in a different suite, whose synthetic end-to-end test stubs the external CLI with a script that answers every invocation identically, so a newly added capability probe got the wrong answer and the dispatch refused. Only the full gate reached it"
  - date: 2026-08-18
    ref: "Donor A — same change, second mechanism: a default branch was unreachable from any focused *or* full selection, because the shared test helper always injects the flag that suppresses it. Different mechanism, same consequence — the selection that was run could not have failed"
---

Two instances in one change, from two different mechanisms: a regression in a file
the selection did not name, and a branch no selection could reach. The common
shape is that **the passing set was chosen before the failure's location was
known** — which is what a focused selection *is*: a bet that the blast radius
matches the edited file. When the bet is right it saves minutes; when it is wrong,
the green is about a set that excludes the defect.

This is not an argument against focused runs. It is an argument for **naming what
they are.** A focused suite answers "did the tests I chose still pass," which is a
useful question during iteration and a *different* question from "did this change
break anything." Reporting the first as though it answered the second is the
reassuring-instrument shape at the level of test **selection** rather than test
**content**.

What to do differently:

- **State the selection's basis when reporting a focused green.** "100 passed in
  the file I edited" carries its own limit; "100 passed" does not.
- **Treat a signature change, a shared-helper change, or a new cross-module probe
  as automatic full-suite triggers** — all three move the blast radius off the
  edited file by construction.
- **Never let a focused green substitute for the gate.** Both reds here were
  invisible until the complete run, and both were real.

This is the risk side of the focused-to-final ladder this repo already runs
([`policies/orchestration-evidence.md`](../policies/orchestration-evidence.md)):
the ladder is right, and its focused rungs are evidence about a chosen set, never
about the change.
