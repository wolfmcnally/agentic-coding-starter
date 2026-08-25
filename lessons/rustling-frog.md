---
slug: rustling-frog
title: Name the cost class at the seam — an O(corpus) read inside a per-item loop is invisible to every phase-scoped review
status: candidate
scope: methodology
proposed_surface: agent
filed: 2026-08-24
source: learn
occurrences:
  - date: 2026-08-11
    ref: "Donor A — a pending-work enumerator re-read the whole ledger once per item; the live run went 2.9x slower than the fixture that had validated it"
  - date: 2026-08-14
    ref: "Donor A — same mechanism, four days later and larger: every ledger append re-parsed the full 22.6 MB ledger five to six times. Measured end-to-end on an isolated copy, ~87% of a 129-minute run was this overhead, with throughput decaying 1.14 → 0.57 events/s inside a single wave — the quadratic signature"
---

Twice in four days the same mechanism dominated a production run: work that is
O(accumulated state) executed once per item inside a loop that is itself
O(accumulated state).

**Why it recurs, and this is the part worth keeping.** Each re-read is
individually defensible. Every defensive re-snapshot exists because no contract
says whose snapshot is current — and in a codebase where **correctness is
contractual and witnessed** (locks, validation, gates) while **cost is neither**,
every layer independently trades away the invisible side, and the trades compound
multiplicatively. No single diff ever "added the defect": six sites accreted
across phases, and **phase-scoped review structurally cannot see a composition
cost that no diff introduced.**

It is also a member of the *fix covers the named instance, not the class* family:
the first repair landed at the one enumerator the reviewer named, and the class
survived intact in the machinery next door.

**What to do differently.** At every seam where code runs inside a per-item loop,
name the cost class of each call relative to the quantities that grow in
production — ledger length, corpus size, file count, index cardinality. An
O(corpus) call inside an O(corpus) loop needs an explicit written justification, or
a cache with a stated invalidation contract.

**Candidate rule for graduation:** make *"what does this call cost, times how many
times does this loop run it"* a named review dimension in the code-critic
checklist, so the question is asked while the loop is still a diff. That is the
one place a composition cost can be caught by the process that exists — the
critic reads the merged code, not only the change. It complements this repo's
human-wall-clock-efficiency invariant, which is about the operator's elapsed wait;
this is about the growth curve that produces it.
