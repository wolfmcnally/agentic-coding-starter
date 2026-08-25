---
slug: russet-mole
title: Something reported success while proving less than its name claimed — the family, not the instance
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-24
source: learn
occurrences:
  - date: 2026-08-16
    ref: "Donor A — a truncated field read as whole: output cut by the reader's own `sed`, with the cut falling exactly where two candidates diverge"
  - date: 2026-08-16
    ref: "Donor A — the same shape a second time in that phase: a gate battery piped through `tail -6`, removing the gate's own verdict from what the reader then reasoned over"
  - date: 2026-08-16
    ref: "Donor A — a measurement whose scope was narrower than its claim: '9 distinct authorities, measured rather than estimated' was a real count over one subset, used to support a catalog-wide claim. The word *measured* carried confidence the enumeration domain had not earned"
  - date: 2026-08-16
    ref: "Donor A — a control covering one surface while named for the phase: a baseline emitted a single digest and was consumed as the phase's control. It would have compared green forever"
  - date: 2026-08-16
    ref: "Donor A — a requirement satisfiable by any route producing its verdict: a policy demanded a cross-paired fixture; the implementation asserted the *finding* without ever forming the *pair*. Letter satisfied, point missed"
  - date: 2026-08-16
    ref: "Donor A — a proof bound to rendering rather than meaning: a mutation's failure signature matched the test runner's summary text, so enlarging a fixture changed the rendering and broke the binding while the guard still fired"
  - date: 2026-08-16
    ref: "Donor A — a review seeing the binding without the bound: the rebind lived in a tracked file and the assertion it bound to in an untracked one, so a tracked-diff review sees the suspicious half and not the half that justifies it"
  - date: 2026-08-20
    ref: "Donor A — a process listing truncated by the reader's own `head -5`; the orchestrator declared all five results to be the operator's own editor processes and concluded no cleanup was needed. Two of its own probe processes had been running the whole time. Identical to this family's first member (output cut by the reader's own `sed`), committed by a reader who had cited that member earlier the same day"
---

Most defects in one donor phase were **one species in different clothes**: a thing
that reported success while proving less than its name claimed. The entry exists
as a *family* because each instance taught a rule too narrow to catch the next
one.

Members worth keeping (each verified in place):

- **A truncated field read as whole.** Output cut by the reader's own `sed`/`head`,
  with the cut falling exactly where two candidates diverge; a gate battery piped
  through `tail -6`, removing the gate's own verdict.
- **A measurement whose scope was narrower than its claim.** "9 distinct
  authorities, *measured* rather than estimated" — a real count over one subset,
  used to support a catalog-wide claim. The word *measured* carried confidence the
  enumeration domain had not earned.
- **A control covering one surface while named for the phase.** A baseline emitted
  a single digest and was consumed as the phase's control. It would have compared
  green forever.
- **A requirement satisfiable by any route producing its verdict.** A policy
  demanded a cross-paired fixture; the implementation asserted the *finding*
  without ever forming the *pair*. Letter satisfied, point missed.
- **A proof bound to rendering rather than meaning.** A mutation's failure
  signature matched the test runner's summary text; enlarging a fixture changed
  the rendering and broke the binding while the guard still fired.
- **A review seeing the binding without the bound.** The rebind lived in a tracked
  file, the assertion it bound to in an untracked one — a tracked-diff review sees
  the suspicious half and not the half that justifies it.

**The rule.** A check, a count, a control, a proof, or a report must be able to
come out **negative** — and **state the binding in the same breath as the value**:
the enumeration domain, not the method; the surfaces covered, not "the control";
the instance required, not the verdict expected. Where a predicate stands in for a
fact, ask whether the predicate can be true when the fact is false.

**Why file the family rather than the members.** Each instance suggested a narrow
rule, and each narrow rule failed to catch the next — including one written down
mid-phase ("never truncate the field you reason from"), stated at its example
rather than its class, which its own author violated hours later on different
output. This repo already holds several members as graduated rules — the
one-reachable-answer rule and vacuous green/uniformity in
[`policies/acceptance-empirical.md`](../policies/acceptance-empirical.md), and the
material-count reproduction rule in
[`policies/verification-discipline.md`](../policies/verification-discipline.md).
What is *not* yet here is the family-level move: **state a rule at its class, not
at the example that produced it**, and treat "my instrument's own reading truncated
the evidence" as a first-class member alongside "my instrument cannot fail."

## Ledger note — 2026-08-25

The `2026-08-16` occurrence was filed as a single row reading "nine distinct
instances in one phase," while the body below named six of them individually. That
is the batched filing [`policies/lessons.md`](../policies/lessons.md) § "One row per
instance" forbids, and it had kept this entry invisible to `bin/lessons candidates`
since the day it was filed. A `sweep lessons` pass split the row against the body;
the six named members plus the `2026-08-20` recurrence are now seven rows.

**Graduation was considered on 2026-08-25 and deliberately held.** The count is now
honest, but the rule is a separate question and only the count was ripe. The only
rule broad enough to cover the whole family — *state a rule at its class, not at
the example that produced it* — is the kind this repository warns does not fire,
and several individual members are already graduated here as narrower rules (the
one-reachable-answer and vacuous-green rules in `acceptance-empirical.md`, the
material-count reproduction rule in `verification-discipline.md`). This entry will
sit on the candidates list until that call is made; its presence there is not an
oversight.
