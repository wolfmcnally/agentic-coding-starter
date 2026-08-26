---
slug: tourmaline-piculet
title: Cleanup paths must not abort before the record is written
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-16
source: learn
occurrences:
  - date: 2026-08-16
    ref: "Donor A — a permission error during process-group termination skipped dispatch recording and span closure"
---

When a caller writes the audit record after a cleanup function returns, any
exception from cleanup can destroy the record. Teardown runs precisely when
something has already failed and is often the least exercised path.

Failing to clean up is recoverable; failing to record is not. Cleanup should
capture its errors so bookkeeping can report them. When a failure leaves no
evidence of itself, detection-based repair is invalid: make the state
unreachable or make reconciliation unconditional. Prefer append-then-amend
records so interruption leaves a partial row rather than none.
