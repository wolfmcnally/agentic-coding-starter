---
slug: greedy-ammonite
title: A role that writes its report into its own artifact path has it clobbered by the venue's last-message write
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-17
source: learn
occurrences:
  - date: 2026-08-11
    ref: "Donor A — a coder attempt's 10.7 KB handoff report destroyed at turn completion by the venue's last-message write; recovered by a resume dispatch to a distinct output path"
---

The watcher passes the role's artifact path to the external venue as its
last-message sink (`--output-last-message` or equivalent). A coder wrote its
full handoff report *into that same file* during the turn, then ended the turn
with a short summary that linked to the file. The venue wrote that summary to
the sink, overwriting the report with a four-line note pointing at itself. The
orchestrator had read the full report moments earlier, so the loss was
visible; had it read the artifact only after completion, the loss would have
been silent and the change evidence unrecoverable.

The failure is structural, not a role mistake: nothing in the prompt or the
persona tells a role that its artifact path is also the venue's last-message
sink, and a role that helpfully "saves its work" to the path it was told about
destroys it. Recovery cost one resume dispatch with a distinct output path,
which worked because the provider session was still resumable.

The candidate rule, if this recurs: either the watcher should refuse a role
write to its own required-output file before the terminal message, or role
prompts should state explicitly that the artifact path is written by the
harness at turn end and must not be written by the role.
