---
slug: fortunate-penguin
title: Make exhaustive contract fixtures semantically complete
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-10
source: learn
occurrences:
  - date: 2026-08-10
    ref: "Donor A — an exact public-inventory fixture omitted human-readable descriptions"
  - date: 2026-08-10
    ref: "Donor A — the exhaustive fixture collapsed unknown sizes into zero"
  - date: 2026-08-10
    ref: "Donor A — the same exhaustive fixture duplicated a hierarchy concept"
---

An exact-output fixture for a finite public contract must represent every
public variant and every field required to understand the result, not merely
prove serialization mechanics. Byte-for-byte exactness can still leave a
semantic hole when representative members omit meaning-bearing fields.

Where the public variant set is bounded, enumerate it completely and assert
both structural and semantic fields. Distinguish absent knowledge from a real
zero and constrain hierarchy at the public boundary.

## Ledger note — 2026-09-29 (graduation considered and held)

The operator held this lesson in the lessons sweep after a recount brought it to three or more occurrences: all three incidents are one fixture on one day. Reopen on the same incompleteness in a different fixture or contract.
