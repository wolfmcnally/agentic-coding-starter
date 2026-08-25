---
slug: swinging-hoatzin
title: A guard invented from foresight is a candidate, not a rule, even when the agent inventing it wrote the rule saying so
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-25
source: user
occurrences:
  - date: 2026-08-25
    ref: "Building the treatise editorial record, the orchestrator made the `directives` log append-only and enforced it in `bin/treatise` with four tests and a mutation proof. No incident motivated it; the shape was copied from LOG.md and the lessons ledger. The operator asked one question — is append-only really necessary — and the guard did not survive its own repository's growth rule. Removed the same day it shipped"
---

The doctrine in [`briefs/methodology.md`](../briefs/methodology.md) says a new
binding rule enters only with its motivating incident cited inline, and that
foresight proposals stay candidates in the ledger rather than becoming rules.
That rule had been in the repository for weeks and was re-read, re-summarized,
and quoted into a public-facing treatise **in the same session** in which this
guard was built without an incident.

**Knowing a rule and applying it to your own output are different acts.** The
generator here is specific and worth naming: a guard invented while building
adjacent machinery arrives feeling *derived* rather than *invented*. The
append-only shape was genuinely correct for `LOG.md` (an audit trail nobody may
revise) and for lesson occurrences (evidence of recurrence). Reaching for it a
third time read as consistency with an established pattern, not as a new binding
rule needing its own justification. Consistency is a real virtue, and it is also
how ceremony spreads from the place that earned it to places that did not.

Three tells this had, visible before the operator asked:

- **No incident could be cited**, and the policy text written for it said so by
  omission: it argued from what *could* go wrong, in the conditional.
- **The threat model, once stated, was narrower than the guard.** The real risk
  was the agent quietly dropping a ruling while revising prose. The check could
  not tell an agent from the operator, so it also blocked the operator from
  correcting their own record.
- **A cheaper mechanism already covered most of it.** The brief is committed;
  version control already holds every earlier state of the log.

The costly part was not the guard. It was that removing it also cost four tests,
a mutation proof, three rule surfaces, and the operator's attention to ask.

Candidate rule, if this recurs: before adding any binding check, state the
incident that motivated it in the same edit, and if the honest answer is "none
yet," file the idea here and ship the validator without it. Kin to
`electric-goshawk` (a one-off arrives pre-trusted): there the imported thing is a
fact that was never a convention; here it is a pattern that was a convention
somewhere else.
