---
slug: fictional-junglefowl
title: Verify append-only writes landed at the true end of the ledger
status: codified
scope: methodology
proposed_surface: bin
filed: 2026-08-26
closed: 2026-09-29
graduated_to: policies/log-discipline.md
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

Closed 2026-09-29 by the operator in the lessons sweep as already covered: `policies/log-discipline.md` states this lesson's remedy. No new rule was written.
