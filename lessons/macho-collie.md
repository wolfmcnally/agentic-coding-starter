---
slug: macho-collie
title: A new required contract member must be swept across every independent fixture inventory of that contract
status: candidate
scope: methodology
proposed_surface: skill
filed: 2026-08-11
source: learn
occurrences:
  - date: 2026-08-11
    ref: "LEARN from Donor A — adding a required --evidence-lane flag to the evidence tool"
---

Adding a required member to a shared repository contract — a mandatory CLI
flag, a required schema field, a new required executable in a gate's preflight
list — breaks every call site that exercises the contract, and those call
sites live in **independent inventories** that no single search obviously
unifies. Observed while absorbing an evidence-lane flag: the tool's own
behavioral test file was swept and updated, but a *second* test file (a
different tool's suite that initializes evidence runs as a fixture) and a
*third* inventory (a gate test's stub-executable list plus its expected
call-log assertions) each carried their own copies. Both were missed by the
first sweep and surfaced only as authoritative-gate failures.

The generalizable discipline: when a change makes a contract member
*required*, grep for the contract's distinctive tokens (the command name, a
neighboring flag, the executable list) across the whole tree — not just the
contract's own test file — and treat each hit file as an independent
inventory to update in the same change. The gate catching the miss is the
backstop working as designed, but each such round-trip costs a full gate run;
the sweep is cheap by comparison. Proposed surface: the learn/teach skills'
apply stages, which are where cross-repo absorption makes this class of edit
routinely.
