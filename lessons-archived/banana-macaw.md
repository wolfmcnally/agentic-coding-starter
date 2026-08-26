---
slug: banana-macaw
title: A harness command ceiling can undercut a role budget, and the death is silent
status: codified
scope: methodology
proposed_surface: policy
filed: 2026-08-17
closed: 2026-08-25
graduated_to: policies/role-timeouts.md
source: learn
occurrences:
  - date: 2026-08-13
    ref: "Donor A (absorbed from `wisteria-termite`) — a planner attempt with an 1800s budget was killed at 10 minutes by the orchestrating harness's own command ceiling and diagnosed for ~30 minutes as a venue failure; the caller was the last place anyone looked"
  - date: 2026-08-16
    ref: "Donor A — a planner attempt killed at 9m59s; evidence row lost, two spans orphaned"
  - date: 2026-08-16
    ref: "Donor A — identical signature in a sibling thread, independently diagnosed the same afternoon"
---

The observed donor harness's foreground command tool capped execution well
below every per-role hard budget in `kickoff.yaml`, and a requested timeout
above the cap was silently clamped rather than refused. A foreground
`kickoff-config watch` therefore could not complete for any role in that
harness. Other harnesses may return a durable session handle that remains
observable past the initial foreground yield, so the general rule is to prove
the execution surface can carry the full budget before using it.

**The silent-death signature**, all four together, none of which says
"timeout":

- exit 143 (SIGTERM to the watcher; the process group takes the child too)
- an artifact file present, zero bytes, well-formed path
- stdout that simply stops mid-stream
- no row in the role-timings ledger, and **no dispatch row recorded at all**

Discriminator that matters: an empty artifact mid-run is *normal*, because the
child writes its final message at the end. Empty is a death signal only
together with a stopped stream and exit 143.

**Fix:** when the current harness's foreground surface clamps the budget or
loses the session handle, dispatch through the harness's own tracked
background mechanism — not detached `nohup`, which forfeits the completion
signal and leaves the orchestrator polling blind.

**The durable repair shape** — the dispatch row written only at the end loses
every death before that point — is the append-then-amend opened/terminal
lifecycle now shipped in `bin/kickoff-evidence`; this lesson stands for the
signature and the standing mitigation: after ANY interrupted role dispatch,
verify the dispatch row exists and close orphaned spans **unconditionally**. A
swept trace and an unswept one look identical afterward, so the sweep cannot
be conditional on noticing.

## Disposition

Graduated 2026-08-25 into
[`policies/role-timeouts.md`](../policies/role-timeouts.md) § "The harness ceiling
bounds every budget", on three occurrences.

`wisteria-termite` was absorbed into this entry in the same sweep and archived
`superseded`. Both describe one mechanism and end at one instruction — prove
that the chosen execution surface can carry the configured budget, and use
harness-tracked background work when the foreground surface cannot. This entry
carried the signature; that one carried the misdiagnosis cost, and its
contribution is preserved in the graduated rule as a named diagnostic step:
**before blaming a delegated venue for a child's death, check what actually
bounded it** — the tool's limits, the harness ceiling, the parent's timeout,
the process group. The caller is the last place anyone looks, because the
caller is the thing doing the looking.

The graduation matters beyond the signature: the repository's shipped-budget
table declares 1,800 s, 7,200 s, and 2,700 s hard deadlines. The policy now
requires an execution surface that remains observable for the corresponding
budget instead of assuming that every harness has the same foreground
semantics.
