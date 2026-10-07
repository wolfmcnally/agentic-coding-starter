---
slug: camouflaged-kakapo
title: A completion signal can outrun the child it reports on
status: candidate
scope: methodology
proposed_surface: policy
filed: 2026-08-24
source: learn
occurrences:
  - date: 2026-08-16
    ref: "Donor A — a double-backgrounded dispatch was reaped at 21 seconds while reporting success"
  - date: 2026-08-20
    ref: "Donor A — a delegated coder launched a gate as a background job in ITS harness, wrote 'holding here until it completes' as its final message, and exited. A child's background job does not outlive the child: when the delegated CLI parent terminated, the job died, and the orchestrator found zero gate processes. The report carried a gate status the role never obtained — the same shape one level down, inside a delegated role rather than the orchestrator"
---

A mechanism that silently did nothing, and reported the same way as a mechanism that worked.

## The completion signal that outran its child

A dispatch died 21 seconds in with no report, exit code 0, task marked complete.
Cause: `nohup … &` written *inside* a call that was already backgrounded.
Double-backgrounded — the outer call returned immediately, the harness recorded
completion, and the detached child was reaped still working.

**The tell was specific.** The script's own trailing line never printed. The
dispatch script ends by echoing its exit code, and that string was absent from a
14 KB log full of real work. **A log that ends mid-stream without the script's own
terminal marker means the process was killed, not that it finished** — and an exit
code from a wrapper says nothing about the child.

So: one level of backgrounding, chosen deliberately. And **give every detached
script a terminal marker only it can print**, because that marker is the difference
between "completed" and "reaped," which the harness's own status cannot
distinguish.

## Why these are one lesson

Both are silent no-ops that render as success — the inert patch makes a test
report a guarantee it never checked; the reaped child makes a dispatch report a
completion it never reached. Neither surfaces an error anywhere, and both are
caught the same way: **require a positive, specific witness that the mechanism
actually ran**, rather than accepting the absence of a complaint as evidence.

## Ledger note — 2026-10-07 (split)

Split from `unique-orangutan` by the operator in the 2026-10-07 sweep, because the two failures filed together there have different remedies. Both incidents recorded here were rows or parts of rows in that lesson; the filing date is the original's.
