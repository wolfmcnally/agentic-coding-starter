---
slug: wisteria-termite
title: A timeout above a tool's documented maximum is silently clamped, and the corpse points at the child
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-17
source: learn
occurrences:
  - date: 2026-08-13
    ref: "Donor A — a planner attempt with an 1800s budget was killed at 10 minutes by the orchestrating harness's own command ceiling and diagnosed for ~30 minutes as a venue failure"
---

A delegated role was given an 1800 s budget and dispatched from a harness tool
call carrying a timeout far above the tool's documented maximum. The value was
**silently clamped** to the ceiling. The role was killed mid-work, with dozens
of completed tool items and its own budgets nowhere near expiry.

Two failures compound, and the second is the expensive one.

**The guard you set is not the guard you have.** An out-of-range timeout does
not error; it is accepted and reduced. Nothing in the call, the result, or the
transcript says "clamped."

**The corpse points at the wrong suspect.** The observable symptom is the
*child* dying — exit 143, no artifact, a healthy-looking parent. Every
instinct sends the investigation to the venue: is the model wedged, is the CLI
broken, is the sandbox denying something? The caller is the last place anyone
looks, because the caller is the thing doing the looking.

**What to do instead.** Before blaming a delegated venue for a child's death,
check what actually bounded it: the tool's own limits, the harness ceiling,
the parent's timeout, the process group. Prefer launching long-running
delegated work as harness-tracked background work, which persists across turns
and re-invokes the session on completion, rather than inside a foreground call
whose ceiling is lower than the work.
