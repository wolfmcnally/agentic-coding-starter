---
slug: blazing-cicada
title: Tightening a widely-read resolver is a fixture migration — schedule the full gate inside implementation, not at acceptance
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-24
source: learn
occurrences:
  - date: 2026-08-19
    ref: "Donor A — the plan's focused-test command named none of the fourteen suites that broke when a context resolver stopped resolving by directory presence and started refusing on absent authority. Both the coder and the code critic independently reached the same observation from the diff; the breakage surfaced only at the coder's first full-gate run"
  - date: 2026-08-19
    ref: "Donor A — same mechanism, 28 failures at the gate, every one a fixture sized to a resolver that tolerated a missing store. Plus an ordering corollary the phase paid for: the write set spanned three repositories, and two of them were pushed on their own green gates BEFORE the third's full gate ran, so the fixture breakage was discovered after irreversible external state had already changed"
---

Making a resolver fail-closed changes the contract every one of its consumers was
written against — including the ones that only ever exercised the happy path
through a fixture that happened to satisfy the old, looser rule. Those consumers
do not fail because their logic is wrong. They fail because their fixtures were
sized to a resolver that tolerated absence, and now it refuses.

That makes the blast radius a property of the **fixture population**, not of the
call graph, and no reading of the diff predicts it. A focused-test list derived
from "what does this change touch" will systematically under-name it, because the
broken suites are the ones that do not touch the change at all.

So a phase whose deliverable is "this authority now refuses" should treat the
full gate as an **implementation step with a scheduled slot**, not as the
acceptance formality at the end. Discovering the fixture migration at acceptance
costs a full extra cycle; discovering it mid-implementation costs one gate run the
phase was going to pay for anyway.

**The ordering corollary matters more here than it did in the donor.** Where a
phase's write set spans repositories, or contains any irreversible step, every
repository's full gate belongs *before the first irreversible step* — not merely
before that repository's own. A red gate found before anything shipped is
discarded in place; the same red gate found afterward becomes a condition to be
corrected forward, bracketed by state that cannot be taken back. Now that
`kickoff` delivers accepted phases itself
([`policies/human-in-the-loop.md`](../policies/human-in-the-loop.md)), the push is
that irreversible step, and this repo's handoff gate is what stands between the
two.

Kin to `macho-collie` (sweep every independent fixture inventory when a contract
gains a required member): same tool, different blindness. There the fixtures were
missing a new member; here they were sized to an old tolerance.
