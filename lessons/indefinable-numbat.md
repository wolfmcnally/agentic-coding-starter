---
slug: indefinable-numbat
title: An artifact no gate regenerates cannot be the only source for a durable claim
status: candidate
scope: methodology
proposed_surface: bin
filed: 2026-09-05
source: user
occurrences:
  - date: 2026-09-05
    ref: "Treatise refresh — reports/test-governance/starter-current.json was the only in-repo artifact from which the published proof counts could be checked without executing the toolchain, and no gate references or regenerates it"
---

A snapshot report is convenient exactly because it answers a question without running anything. That is also what makes it dangerous as a citation: nothing recomputes it, so it drifts silently, and the next reader who trusts it inherits whatever was true on the day it was written.

The concrete case: a published document's proof counts could be checked either by executing the toolchain or by reading a committed report that no gate regenerates and no check references. A read-only reviewer necessarily took the second route. The numbers happened to agree, which is the outcome that makes the pattern hard to notice — a stale snapshot and a fresh one look identical until the day they do not.

**Either give a cited snapshot a freshness check, or record in the document that it is a snapshot and name what regenerates it.** The choice is between mechanizing the currency and disclosing its absence; what fails is citing it as though the currency were mechanized.

The wider form: before relying on a committed artifact as evidence, ask what regenerates it and what would catch it going stale. If the answer to both is nothing, it is a dated observation, not a live measurement, and it should be labeled the way any other dated observation is.
