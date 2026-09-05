---
slug: effective-asp
title: A ratified correction does not retire the artifacts the old rule produced
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-09-05
source: user
occurrences:
  - date: 2026-09-05
    ref: "Methodology-routing correction — the direct-implementation rule landed in policy on 2026-09-05, but the three phase rows drafted under the old route survived it, one still marked 🚧, until the operator noticed the mismatch a day later"
---

Ratifying a rule mid-flight fixes what happens next. It does nothing to what the previous rule already produced, and the leftovers are dangerous in a specific way: they still look authoritative. A retired route's artifacts keep whatever markers made them live — a status arrow, an open ledger row, a pending queue entry — so the very machinery the new rule was meant to redirect keeps picking them up.

The correction that prompted this was written *because* a route was wrong, which makes the surviving artifacts of that route the first thing to re-examine, not the last. Nobody did, because the rule felt like the deliverable.

**When a rule is adopted or corrected mid-task, immediately enumerate what was produced under the old rule and dispose of each item explicitly.** Retire, re-route, or keep with a stated reason. The enumeration is the work; the rule text is only half of it. A correction that leaves live artifacts behind has not taken effect, however well it reads.

Watch especially for artifacts that carry an *active* marker rather than a historical one. A completed record under a retired rule is history and stays put. An in-progress one is a live instruction to do the wrong thing again.
