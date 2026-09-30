---
slug: hashed-ibis
title: Treat pinned byte digests as dependencies of the artifact they authenticate
status: rejected
scope: methodology
proposed_surface: skill
filed: 2026-08-25
closed: 2026-09-29
source: learn
occurrences:
  - date: 2026-08-25
    ref: "Donor A — canonical serialized bytes changed while an independently pinned digest consumer was omitted from the write surface"
---

When canonical serialized bytes change, search for every consumer that pins,
hashes, or byte-compares that artifact and include each affected consumer in
the change surface. Preserve unrelated digests as negative controls. A pinned
digest is a dependency edge even when no import or call graph exposes it.

Rejected 2026-09-29 by the operator as not methodology-specific: its remedy is sound general engineering or source-project practice, but it would change none of this template's rules, roles, skills or tooling, which is what `scope: methodology` requires (`policies/lessons.md`).
