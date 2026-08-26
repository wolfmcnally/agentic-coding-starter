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
    ref: "Donor A — the exhaustive fixture collapsed unknown sizes into zero and duplicated a hierarchy concept"
---

An exact-output fixture for a finite public contract must represent every
public variant and every field required to understand the result, not merely
prove serialization mechanics. Byte-for-byte exactness can still leave a
semantic hole when representative members omit meaning-bearing fields.

Where the public variant set is bounded, enumerate it completely and assert
both structural and semantic fields. Distinguish absent knowledge from a real
zero and constrain hierarchy at the public boundary.
