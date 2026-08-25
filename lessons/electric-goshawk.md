---
slug: electric-goshawk
title: A one-off artifact you authored yourself is the most dangerous false convention — it arrives pre-trusted
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-24
source: learn
occurrences:
  - date: 2026-08-20
    ref: "Donor A — a plan specified recovering a run directory from an exported environment variable 'the transcript emits'. No such export exists anywhere in the workflow. The variable was in the plan author's context because a sibling session had exported it once, in one handoff document, as a mechanism for exactly one transfer. Neither party grepped a real transcript. Compounded: recovery failure routed to fail-open-loudly, so the gate would have been permanently inert while its acceptance criterion — 'expected caught-stall count is ZERO' — read as success"
  - date: 2026-08-22
    ref: "Donor A — the self-authored artifact was the author's own continuation packet, carrying as a durable rule a gate-tool contract learned the previous night in a SIBLING repository. The two repos' tools share a name, a subcommand, and a flag, and have INVERTED contracts: one requires the command to produce the artifact, the other refuses unless the artifact already exists. The note was accurate about the repository it was written in and arrived in the other pre-trusted as doctrine. The wrapper compounded it: the harness reported the failed call as exit code 0, and only a line inside the captured artifact told the truth"
---

A fact that entered your context by a one-time route is indistinguishable, once
there, from a fact that describes a standing convention. Both are just things you
know. **The provenance is not attached to the content**, and nothing in the reading
experience flags which is which.

**Self-authored artifacts are the worst case**, because they carry your own
authority into someone else's model — or into your own, later. The handoff
document was accurate when written and accurate about what it described; it simply
described *one transfer*, not a workflow. The reader had no reason to doubt a
mechanism the writer had apparently been using, and the writer had no reason to
think a one-off note would be read as doctrine.

This is *quote from the source, never your own earlier summary* promoted one
level: not a summary standing in for a source, but a **local instrument standing in
for a repository convention**. The check is the same and it is cheap: **before
specifying a mechanism as though it exists, find it in the thing that would
contain it.** One `rg` over a real transcript, one read of the tool's `--help`, one
look at the actual file. If it cannot be found where it would have to live, it is
not a convention — it is a memory.

**The second occurrence is this repo's own hazard.** `learn` and `teach` move rules
between sibling repositories that share tool names, flags, and vocabulary while
diverging in contract. That is exactly the shape that arrives pre-trusted, and it
is why the `learn` skill establishes direction of advance **per item** and requires
a donor's defect to reproduce here before its remedy is imported.

**The compounding half deserves separate attention.** This defect selected for
invisibility: a missing mechanism made recovery fail; the guard's fail-open-loudly
posture (correct in itself) turned that into an unconditional exit 0; and the
acceptance criterion measured *absence of caught stalls*, which an inert gate
satisfies perfectly. Every layer behaved as designed and the composition was a
guard that could only ever say "fine."

So when a design depends on a mechanism, ask **two** questions rather than one.
Does it exist? And if it did not, what would the failure look like — loud, or
exactly like success?
