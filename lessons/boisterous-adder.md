---
slug: boisterous-adder
title: A reset budget is not a continuing zero-growth budget unless later retirements are replayed
status: candidate
scope: methodology
proposed_surface: bin
filed: 2026-08-28
source: learn
occurrences:
  - date: 2026-08-28
    ref: "LEARN from Donor A — the imported manager counted the large one-time reset's retired proofs as permanently available budget, so a later admission could consume an old reset retirement instead of naming a new physical retirement"
---

A proof-estate reset and a continuing zero-net-growth rule use the same words
but need different accounting. The reset creates the retained baseline. After
that boundary, each new proof must follow one append-only `proof_retirement`
event that removes an active proof and creates exactly one budget unit; the
admission consumes that exact unit once.

Counting every proof retired during the initial reset as forever-spendable
budget makes future growth look compensated while the active estate grows. A
validator must replay the post-reset lifecycle in order, refuse absent or
duplicate retirement targets, refuse reuse, and require the replayed active set
to equal the current inventory.
