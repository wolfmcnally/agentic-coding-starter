---
slug: classy-kangaroo
title: Exercise lifecycle mutations against the same authorities used in production
status: candidate
scope: methodology
proposed_surface: test
filed: 2026-09-04
source: kickoff
occurrences:
  - date: 2026-09-04
    ref: "Phase 2 preparation — startup status mutation immediately drifted the required whole-file ledger authority"
---

Check an orchestration lifecycle with its production authority inventory and real status transitions. In Phase 2, kickoff captured `plan/INDEX.md` as a whole-file authority, then changed its status marker as the next required step. Candidate partitioning correctly excluded bookkeeping from product identity, but the independent authority hash still changed. The fixture inventory did not reproduce that combination, so passing component tests did not prove that a complete phase could close.

The approved preparation sequence puts final authority edits and the in-progress marker before a fresh capture, leaving real implementation work afterward. For a major phase, acceptance can finish against that unchanged authority before status bookkeeping and the full handoff gate. Child closure has a separate unresolved ordering conflict: its close checker requires the completed marker before acceptance while the authority hash rejects the same mutation. A prospective correction should prove both legitimate status-only transitions and refusal of substantive ledger changes; excluding all bookkeeping from authority validation would silently discard requirements.

The diagnostic lesson is about lifecycle coverage, not about relaxing authority integrity. No generic ledger normalization or new recovery mechanism is ratified by this entry.
