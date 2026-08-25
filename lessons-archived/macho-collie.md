---
slug: macho-collie
title: A change to a shared contract must be swept across every independent inventory that embodies it
status: codified
scope: methodology
proposed_surface: policy
filed: 2026-08-11
closed: 2026-08-25
graduated_to: policies/verification-discipline.md
source: learn
occurrences:
  - date: 2026-08-11
    ref: "LEARN from Donor A — adding a required --evidence-lane flag to the evidence tool"
  - date: 2026-08-17
    ref: "LEARN from Donor A — adding check-hooks-installed to bin/check's required-executable preflight and policy lane broke ten test_check.py cases across three independent inventories in that one file (the fixture stub loop, the exact expected-call lists for two modes, and the missing-executable parametrize); caught by the authoritative gate, exactly the costly backstop path this lesson names"
  - date: 2026-08-17
    ref: "LEARN apply — the relaxation direction of the same shape (absorbed from `fractal-beetle`). This repo's review-lanes policy demotes light-lane review metrics to the omission ledger, but both enforcement call sites of the metrics check (timing-summary and the pre-close validation) ran unguarded; a light-lane run with a recorded omission would have been refused at close, in exactly the demoted mode's rare path. Found only because the donor's diff carried the guards and the hunk-by-hunk direction check asked why the destination lacked them"
  - date: 2026-08-25
    ref: "Adding bin/treatise to the same preflight and policy lane broke fourteen test_check.py cases across the same four inventories, in a session where this very lesson had been re-filed hours earlier. Two further traps surfaced on the repair: the eight-space expected-call string is a substring of the twelve-space one, so a naive text replacement double-applied, and four nearby integers that look like lane counts are sentinel exit codes the fixture propagates — changing them broke four passing tests. Both were caught by running the suite, neither by reading the file"
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

## Disposition

Graduated 2026-08-25 into
[`policies/verification-discipline.md`](../policies/verification-discipline.md)
§ "Sweep every embodiment of a changed contract", on four occurrences.

`fractal-beetle` was absorbed into this entry in the same sweep and archived
`superseded`: it recorded the *relaxation* direction of the identical move — a
mode-conditional exemption that must reach every enforcement site of the check it
relaxes — and its own body named the remedy shape as the same one. The graduated
rule states both directions and how they differ: an addition fails loudly at the
gate, while a relaxation implemented at N-1 of N sites reads as implemented
everywhere, because only the demoted mode's rare path reaches the unguarded site.

The recorded `proposed_surface` was `skill` (the learn/teach apply stages), written
after the first two occurrences. The third and fourth happened in ordinary phase
work with no cross-repo transfer involved, so the surface was widened to the policy
that governs establishing a change is complete.
