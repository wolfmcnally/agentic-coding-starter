---
slug: divergent-scorpion
title: Preserve a dependency's ownership boundary before extending it
status: candidate
scope: methodology
proposed_surface: brief
filed: 2026-08-25
source: learn
occurrences:
  - date: 2026-08-25
    ref: "Donor A — a proposed immutable-generation protocol displaced an existing consumer-owned publication boundary"
---

Before proposing stronger lifecycle guarantees for a dependency, inspect how
its real consumers divide responsibility. A shared mechanism should guarantee
only what it can know; a consumer may be the only party able to know whether a
corpus is complete or a copied artifact is ready to publish.

Do not turn a consumer-owned snapshot into a substrate-owned immutable
generation protocol merely because reproducibility sounds desirable. Preserve
the dependency's established modes, then add only capabilities that fit its
existing ownership boundary.
