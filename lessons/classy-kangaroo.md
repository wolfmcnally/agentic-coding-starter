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
  - date: 2026-09-05
    ref: "Readiness review — child-side parent validation used the child's pinned executable, which the parent run correctly refused"
  - date: 2026-09-05
    ref: "Readiness review — final-child completion required a next marker in the same prospective transition, and deeper nesting required separately accepted ancestor completions"
  - date: 2026-09-05
    ref: "Readiness review — a repeated nested close after applying bookkeeping failed the parent pre-state check before reaching idempotency handling"
---

Check an orchestration lifecycle with its production authority inventory and real status transitions. In Phase 2, kickoff captured `plan/INDEX.md` as a whole-file authority, then changed its status marker as the next required step. Candidate partitioning correctly excluded bookkeeping from product identity, but the independent authority hash still changed. The fixture inventory did not reproduce that combination, so passing component tests did not prove that a complete phase could close.

The approved preparation sequence puts final authority edits and the in-progress marker before a fresh capture, leaving real implementation work afterward. For a major phase, acceptance can finish against that unchanged authority before status bookkeeping and the full handoff gate. Child closure has a separate unresolved ordering conflict: its close checker requires the completed marker before acceptance while the authority hash rejects the same mutation. A prospective correction should prove both legitimate status-only transitions and refusal of substantive ledger changes; excluding all bookkeeping from authority validation would silently discard requirements.

The diagnostic lesson is about lifecycle coverage, not about relaxing authority integrity. No generic ledger normalization or new recovery mechanism is ratified by this entry.

The approved readiness repair subsequently exercised distinct pinned parent runs, a three-level final-child rollup, exact next-marker advancement, and retries both before and after applying the ledger. Tampered transition records refuse independently of their claimed status. These observations extend the executable lifecycle proof; they do not graduate this lesson. The earlier unresolved child-close statement records the preparation state, not the repaired implementation.
