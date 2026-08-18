---
slug: banana-macaw
title: The orchestrating harness's command ceiling is below every role budget, and the death is silent
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-17
source: learn
occurrences:
  - date: 2026-08-16
    ref: "Donor A — a planner attempt killed at 9m59s; evidence row lost, two spans orphaned"
  - date: 2026-08-16
    ref: "Donor A — identical signature in a sibling thread, independently diagnosed the same afternoon"
---

The orchestrating harness's foreground command tool caps execution well below
every per-role hard budget in `kickoff.yaml`, and a requested timeout above
the cap is silently clamped rather than refused. A foreground
`kickoff-config watch` therefore **cannot complete for any role**.

**The silent-death signature**, all four together, none of which says
"timeout":

- exit 143 (SIGTERM to the watcher; the process group takes the child too)
- an artifact file present, zero bytes, well-formed path
- stdout that simply stops mid-stream
- no row in the role-timings ledger, and **no dispatch row recorded at all**

Discriminator that matters: an empty artifact mid-run is *normal*, because the
child writes its final message at the end. Empty is a death signal only
together with a stopped stream and exit 143.

**Fix:** dispatch every role through the harness's own tracked background
mechanism, not a foreground call — and not detached `nohup`, which dodges the
cap but forfeits the completion signal, leaving the orchestrator polling
blind.

**The durable repair shape** — the dispatch row written only at the end loses
every death before that point — is the append-then-amend opened/terminal
lifecycle now shipped in `bin/kickoff-evidence`; this lesson stands for the
signature and the standing mitigation: after ANY interrupted role dispatch,
verify the dispatch row exists and close orphaned spans **unconditionally**. A
swept trace and an unswept one look identical afterward, so the sweep cannot
be conditional on noticing.
