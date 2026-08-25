---
slug: fair-cockle
title: A progress artifact that went dark reads exactly like a current one
status: candidate
scope: methodology
proposed_surface: bin
filed: 2026-08-24
source: learn
occurrences:
  - date: 2026-08-20
    ref: "Donor A — a coder's progress checkpoint, last written near the start, still read 'nothing written yet' while the tree held 22 changed files and the role had been running 1h21m. Nothing about the artifact says it is stale; freshness is knowable only by comparison. The orchestrator misread it as the role abandoning the discipline"
  - date: 2026-08-20
    ref: "Donor A — same run, revealed in the final report: every write to the checkpoint path after the first was DENIED by the sandbox. The mechanism was broken, not the practice, and the orchestrator had attributed a discipline failure to a blocked role. A sibling role in the same phase was denied the same way, and both said so plainly in their reports"
---

A progress artifact solves the problem of a role dying with no report. It does
**not** solve a role reporting **once** and then going dark: the resulting
artifact is plausible, well-formed, and false, and it presents exactly as a
current one.

This has a mechanical witness, and it belongs in a watchdog rather than in prose:

    event stream fresh  AND  progress artifact stale beyond N minutes  ==>  alarm

A watch that already reads both mtimes needs one comparison to gain coverage of
**both** dark states — *nothing running* (the stall class) and *running but
unreported* (this class). **A guard that only detects silence cannot see a role
working invisibly.**

The second occurrence carries a separate warning for orchestrators: **before
attributing a missing artifact to a role's discipline, check whether the role
*could* write it.** The information was in the role's own report, unread.

Applicability here is partial and worth stating: this repo has no per-role
progress-checkpoint artifact today — [`policies/role-timeouts.md`](../policies/role-timeouts.md)
enforces first-event, idle-progress, and hard deadlines against the event stream
alone. So the first half is a design note for if one is ever added; **the second
half applies immediately**, because an idle-watchdog trip here is already
ambiguous between "the role stopped working" and "the role cannot report."
