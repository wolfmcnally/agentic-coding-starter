---
slug: astonishing-chowchow
title: The repair path is where a chained block is most tempting and least examined
status: candidate
scope: methodology
proposed_surface: invariant
filed: 2026-08-24
source: learn
occurrences:
  - date: 2026-08-20
    ref: "Donor A — an orchestrator opened one stage before closing the previous one, creating a stage overlap. Noticed immediately"
  - date: 2026-08-20
    ref: "Donor A — the REPAIR for that slip ran cancel, close, and reopen in ONE block. The cancel refused, the block continued past the failure, and the reopen executed against a still-open span, creating a second overlap. Both permanent: closed spans are immutable by design, so the run could never certify its final validation"
---

This repo already holds the chaining rule — *a command whose refusal must be read
gets its own block* ([`CLAUDE.md`](../CLAUDE.md), architectural invariants). This
entry names **where** it recurs.

A repair sequence feels atomic. You have just made a mistake, you can see the
whole fix, the commands are obviously related, and writing them as one block is
the natural expression of "undo this properly." That is exactly the composition
the rule forbids — and it is the composition nobody reviews, because cleanup does
not get read the way new work does.

The cost in the donor's case was permanent. The refusing command was the *first*
of three, its refusal was correct and specific, and the two commands after it ran
anyway. Because closed telemetry spans are immutable by design, the resulting
record could never certify, and the phase closed with an amendment stating what
could not be machine-certified and why.

Two corollaries:

- **A repair is new work and gets the same discipline as new work** — one command
  per block wherever any of them can refuse.
- **A declared-defect path matters.** Where a structurally similar failure has an
  explicit "record this as incomplete" verb, the record can say what went wrong in
  its own terms; where it has none, an uncorrectable record is simply wrong with
  no way to say so.
