---
slug: fractal-beetle
title: A mode-conditional relaxation must reach every enforcement site of the check it relaxes
status: superseded
scope: methodology
proposed_surface: policy
filed: 2026-08-17
closed: 2026-08-25
source: learn
occurrences:
  - date: 2026-08-17
    ref: "LEARN apply — this repo's review-lanes policy demotes light-lane review metrics to the omission ledger, but both enforcement call sites of the metrics check (timing-summary and the pre-close validation) ran unguarded; a light-lane run with a recorded omission would have been refused at close, in exactly the demoted mode's rare path. Found only because the donor's diff carried the guards and the hunk-by-hunk direction check asked why the destination lacked them"
---

When a policy declares a mode that relaxes an enforcement — a light lane that
demotes a required measurement to an omission ledger, a documented exemption,
a compatibility window — the relaxation is itself a contract member, and it
must be swept across **every** call site that enforces the underlying check.
A relaxation implemented at N−1 of N sites reads as implemented everywhere:
the ordinary mode exercises all sites identically, and the demoted mode's
rare path is the only thing that reaches the unguarded one.

This is the mirror image of the sibling lesson about new required contract
members and fixture inventories (`macho-collie`): there, an *addition* missed
independent embodiments and failed loudly at preflight; here, a *relaxation*
missed enforcement sites and would have failed a legitimately-demoted run at
close. Same remedy shape: enumerate every independent site that embodies the
contract — grep for the check's name, not the policy's — before declaring the
change complete.

## Disposition

Superseded 2026-08-25 by [`macho-collie`](macho-collie.md), which graduated the
same day into
[`policies/verification-discipline.md`](../policies/verification-discipline.md)
§ "Sweep every embodiment of a changed contract". This entry's occurrence was
carried onto that one.

The two describe opposite halves of a single move — macho-collie the *addition* of
a required contract member, this entry the *relaxation* of an enforcement for one
mode — and this body already named the remedy shape as identical. The graduated
rule keeps both directions and the asymmetry between them: an addition fails
loudly at the gate, while a relaxation missing one enforcement site is invisible
until the demoted mode's rare path reaches it.
