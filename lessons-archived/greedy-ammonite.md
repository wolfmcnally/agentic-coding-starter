---
slug: greedy-ammonite
title: A role that writes its report into its own artifact path has it clobbered by the venue's last-message write
status: codified
scope: methodology
proposed_surface: policy
filed: 2026-08-17
closed: 2026-09-05
graduated_to: policies/four-canonical-agents.md
source: learn
occurrences:
  - date: 2026-08-11
    ref: "Donor A — a coder attempt's 10.7 KB handoff report destroyed at turn completion by the venue's last-message write; recovered by a resume dispatch to a distinct output path"
  - date: 2026-08-24
    ref: "Donor A — a managed coder reexecution wrote its complete report to the required-output path, then the venue overwrote it with the short terminal summary"
  - date: 2026-08-25
    ref: "Donor A — another coder revision's complete report artifact was overwritten by the venue's terminal notification and reconstructed from durable evidence"
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

## Ledger note — 2026-09-05 (graduation)

**Graduated by operator ruling, as the instruction half only.** The rule is a section in [`policies/four-canonical-agents.md`](../policies/four-canonical-agents.md) — a role's report is its terminal message, never a file it writes — with the three sightings and the silent-loss window cited inline. The operative line is repeated in all four role definitions, because a role reads its own definition rather than the policy and the instruction is currently the entire control.

**The machinery half was deliberately not taken.** This entry proposed either an instruction or a watcher refusal; the operator chose to ship the instruction now and scope the code change separately, since it would land in the path every role dispatch runs through. That decision is filed as an open human-only action, `user-actions/mustard-alpaca.md`, which records what the instruction does not cover: an instruction fails exactly when a role does not follow it, which is what happened three times.

## Ledger note — 2026-09-05 (second-instance test not satisfied; graduated on the threshold)

**This entry does not pass the second-instance test** graduated earlier the same day. Its three occurrences are a coder attempt, a coder reexecution and a coder revision, each losing a report to the same last-message sink in the same way: one tool, one surface, one subject. That is the same description used hours later to hold `lessons/deft-puffin.md`, and the two entries must not read as an inconsistency.

**The operator graduated it anyway, on the standing three-occurrence threshold**, which is independent of the test and which this entry meets. The reason given: the loss is silent and unrecoverable. All three sightings were caught only because someone had read the report minutes before it vanished; read after turn completion instead, a complete handoff report is gone with no trace and the change evidence with it. A rule whose absence costs unrecoverable work is worth stating before its class is fully identified, and the instruction costs nothing to follow.

**The record is corrected here because the operator's ruling rested on a wrong statement.** They were told this entry passed the test, in a sentence that described the failure condition and called it a pass. It does not pass. The graduation stands on the threshold and the silent-loss ground stated above, and the independent review that caught the error is the reason this note exists rather than the inconsistency.

What would change the assessment: a sighting on a different role, a different venue, or a different mechanism for destroying a role artifact. Any of those identifies the class and the rule could then be restated at it.
