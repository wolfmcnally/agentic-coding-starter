---
title: A proof admission that refuses partway leaves witness receipts for the proofs
  before it
scope: methodology
proposed_surface: bin
source: teach
slug: funny-moth
status: candidate
filed: '2026-11-14'
occurrences:
- date: '2026-11-14'
  ref: a recipient's 1.7.0 transfer, rehearsed in a private copy; the worker reported
    that one admission input of thirteen proofs refused at the tenth on a wrong expected
    failure, with nine receipts already appended to the witness ledger and no admission
    rows written
---

Reported by a transfer worker and not reproduced by the hub. The admission's precheck refuses an input before any witnessing when a record cannot be valid, and says nothing was witnessed. A failure that only witnessing can reveal, such as an expected failure that does not match what the planted defect produces, arrives after earlier proofs in the same input have already written their receipts. The ledger then holds receipts with no admission, and the refusal does not say so.

The rehearsal in a private copy kept this out of the recipient's real checkout. A worker that admits directly in the checkout would be left with a ledger it may not hand-edit and an input it must correct and rerun.

Candidate correction: witness every proof of one input first and append receipts and admission rows together only when all pass; or have the refusal name the receipts already written and state whether a corrected rerun is safe. Until then the transfer skill's advice to rehearse the admission in a private copy carries the protection.
