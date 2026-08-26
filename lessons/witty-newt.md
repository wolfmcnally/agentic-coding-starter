---
slug: witty-newt
title: A field nothing compares is not evidence
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-26
source: learn
occurrences:
  - date: 2026-08-22
    ref: "Donor A — modification time was proposed as an identity discriminator even though no behavior compared it and ordinary file operations changed it"
---

Two records differed in modification time, so that visible field was proposed
as part of their identity. A reader inventory showed that nothing compared the
field: it was stored once and displayed, but no behavior branched on it.

The field also changed for reasons the domain did not care about, including
touches, copies, and restores. Adding it to identity would have minted distinct
records for unchanged content.

The meaningful properties were already represented by path and content hash.
The timestamp described the observation rather than the observed fact.

**The rule candidate:** before a field enters an identity, key, deduplication
rule, or comparison, count its behavioral readers. Search for sites that
compare or branch on it, not merely sites that store or print it. A field with
no comparisons is provenance or decoration until evidence proves otherwise.
