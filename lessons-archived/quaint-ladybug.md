---
slug: quaint-ladybug
title: A zero-net-growth budget pushes new contracts into existing test functions whose names no longer describe them
status: rejected
scope: methodology
proposed_surface: policy
filed: 2026-09-29
closed: 2026-09-29
source: learn
occurrences:
  - date: 2026-09-29
    ref: "Starter — adding the repair disposition's lifecycle proof inside an existing growth-approval test function to avoid spending a family budget; the function name now promises less than it checks"
---

Adding the `repair` ledger disposition needed a proof of three behaviors: a reset-era repair stays active, a post-reset repair of an active proof validates without touching the budget, and a repair of a retired proof refuses. A new test function would have added a family and required a compensating retirement or an approved positive budget. The cheaper path, taken here, was to extend the existing lifecycle test `test_positive_growth_requires_named_approval`, which already monkeypatches the ledger.

That is legal under the zero-net-growth rule and it is also one of the junk patterns absorbed in the same run: a name that no longer describes what the proof checks. The family's contract line and the function name now under-describe it, and a later layer pass reading names rather than assertions would miss that repair is guarded here at all.

The budget rule counts families and leaves; it has no view of how many distinct contracts a family carries. So a strict budget and a "one contract per proof, named for what it checks" rule pull in opposite directions, and the budget always wins silently because only it is executable.

Candidate remedy for ratification: when a proof is extended to guard an additional contract, the family's `contract` text and the function name must be updated to cover it in the same change, or the addition must go to a new family under a named budget. A reviewer or sweep treats a family whose name covers fewer contracts than its assertions as a repair candidate, not a pass.

Closed 2026-09-29 by the operator as obsolete: the same day's change replaced the count budget with a time budget, which removes the pressure to fold new contracts into existing proofs. The symptom that remains possible, a proof name that no longer describes its assertions, is already a junk pattern in `policies/test-suite-governance.md` § Judging a proof. The proposed remedy was not adopted.
