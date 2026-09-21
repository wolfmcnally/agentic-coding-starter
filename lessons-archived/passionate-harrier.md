---
slug: passionate-harrier
title: The proof-estate reset contract is unsatisfiable for a freshly stamped recipient
status: codified
scope: methodology
proposed_surface: policy
filed: 2026-09-10
closed: 2026-09-21
graduated_to: policies/test-suite-governance.md
source: user
occurrences:
  - date: 2026-09-10
    ref: "stamp of a Python target — validate demands at most 20% of a baseline that is already the reset estate, plus 12+12 local corpus cases a fresh repo cannot have; parked for the owner"
---

`stamp` tells the recipient to freeze its whole-estate baseline with `test-governance inventory`, retain at most 20% of it, and prove at least 80% recall on exactly twelve historical defects and twelve held-out mutants of its own. A recipient stamped today inherits the template's *post-reset* suite as its baseline, so a compliant reset would discard four fifths of the universal machinery's direct proofs. It has no defect history, and the bootstrap contract forbids copying the template's corpus. The three requirements cannot coexist, and the contract's own escape clause ("a conflict parks for the owner") fires on every fresh stamp.

The proxy mismatch: the 20% ceiling and the 12-case corpus were calibrated against a repository with 541 baseline families and months of recorded defects. They measure whether an *overgrown* estate was pruned, not whether a *new* one is governed.

Candidate corrections, for the owner to choose among: let a fresh recipient inherit the template's pre-reset baseline and reset ledger as its frozen history (the universal proofs then already carry their dispositions); make the ceilings and corpus size recipient-configurable with a stamp-time default of 1.0 and an empty-but-frozen corpus that `reassess` widens as Phase history accrues; or drop the twelve-case constant from `validate` in favor of a recipient-declared corpus size with the recall floor unchanged.

Ratified 2026-09-21: the second correction. The family and leaf ratios and the per-class corpus floors became recipient-declared in `reset_limits`, with a stamp-time default of 1.0 for both ratios and an empty-but-frozen corpus that `reassess` widens as phase history accrues. The recall minimums, direct-risk witnesses, zero-net-growth budget, frozen selection and digest binding are unchanged. An empty class reports as unmeasured rather than as zero or as passing. This template keeps 0.2 and twelve cases per class; the constants became declarations rather than moving.
