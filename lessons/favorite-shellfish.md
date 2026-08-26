---
slug: favorite-shellfish
title: A catch for a child silently misses helpers that raise the root exception
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-26
source: learn
occurrences:
  - date: 2026-08-21
    ref: "Donor A — a shared validator raised the hierarchy root, escaping a child-specific cleanup catch while an outer collector made the result look orderly"
---

A package organized failures under one root exception with sibling child
types. Planning and review classified every refusal by child, but a shared
validator raised the root itself.

A caller promised one child type and instead leaked the root. Worse, a cleanup
guard caught only that child, so the root escaped after staging and left
residue. An outer collector caught the root and produced a tidy per-item
refusal, hiding the missed cleanup.

This generalizes to any rooted taxonomy: switches, handler registries, and
dispatch tables over leaves silently mishandle legitimate root values.

**The rule candidate:** before reasoning over child types, enumerate every site
that raises or returns the root itself. Any root producer is outside a
leaf-specific catch or dispatch rule and must be handled deliberately.
