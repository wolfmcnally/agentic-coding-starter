---
slug: fictional-junglefowl
title: Verify append-only writes landed at the true end of the ledger
status: candidate
scope: methodology
proposed_surface: bin
filed: 2026-08-26
source: learn
occurrences:
  - date: 2026-08-23
    ref: "Donor A — an append patch matched an older repeated Markdown block and inserted a new close record before later history"
---

An edit intended to append a close record used a repeated Markdown block as
its context anchor. The patch succeeded but selected an older copy, placing
the new record before existing history and violating the ledger's ordering
contract.

Success from an editing primitive proves that bytes changed, not that an
append landed at the true end.

**The rule candidate:** independently verify that every append-only write is
the final record after editing. Prefer a deterministic append helper or an
explicit end-of-file postcondition, because repeated document structures make
context anchors inherently ambiguous.
