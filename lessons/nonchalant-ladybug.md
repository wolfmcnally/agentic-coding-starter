---
slug: nonchalant-ladybug
title: Test integrity relationships rather than only field validity
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-10
source: learn
occurrences:
  - date: 2026-08-10
    ref: "Donor A — individually canonical source identifiers named different legal artifacts"
  - date: 2026-08-24
    ref: "Donor A — pathname validation and later descriptor checks left the first writer outside the pinned object identity"
---

An integrity contract is incomplete when each field or observation is valid in
isolation but their relationships are untested. Include adversarial pairings:
individually canonical identifiers that name different artifacts, and payloads
with equivalent metadata but different complete bytes.

Carry the identity established by the ownership-creating operation through the
first consumer and every later consumer and cleanup step. Securing only the
later half of a time-of-check/time-of-use chain does not secure the relationship.
